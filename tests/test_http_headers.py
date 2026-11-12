"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-2026 Pycord Development
Copyright (c) 2026-present The rum team

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Tests for the HTTP client.

The client is built on httpcore, which hands the headers over as plain
strings. The ban guard is tested here too, since it is part of the same
client.
"""

import asyncio

import pytest

from rum import utils
from rum.errors import LoginFailure
from rum.http import BanGuard, HTTPClient, Route, _ResponseProxy, parse_response


class FakeHeaderMap:
    """The headers of a response, the way a client hands them over."""

    def __init__(self, items: dict[str, str]) -> None:
        self._items = {k.lower(): (k, v) for k, v in items.items()}

    def get(self, key: str, default=None):
        entry = self._items.get(key.lower())
        if entry is None:
            return default
        return memoryview(entry[1].encode())

    def __getitem__(self, key: str):
        return self.get(key)

    def __iter__(self):
        for name, value in self._items.values():
            yield memoryview(name.encode()), memoryview(value.encode())


class FakeResponse:
    def __init__(self, body: str, headers: dict[str, str], status: int = 200) -> None:
        self._body = body
        self.headers = FakeHeaderMap(headers)
        self.status = status

    async def text(self) -> str:
        return self._body

    async def bytes(self) -> bytes:
        return self._body.encode()


def test_decode_header_value():
    assert (
        utils._decode_header_value(memoryview(b"application/json"))
        == "application/json"
    )
    assert utils._decode_header_value(b"text/plain") == "text/plain"
    assert utils._decode_header_value("already a str") == "already a str"
    assert utils._decode_header_value(None) is None


def test_decode_headers_is_case_insensitive():
    headers = utils._decode_headers(FakeHeaderMap({"Content-Type": "application/json"}))
    assert headers.get("content-type") == "application/json"
    assert headers.get("CONTENT-TYPE") == "application/json"
    assert headers.get("missing") is None


@pytest.mark.asyncio
async def test_parse_response_json():
    response = FakeResponse(
        '{"id": "1234", "username": "rum"}',
        {"Content-Type": "application/json; charset=utf-8"},
    )
    data = await parse_response(response)
    assert data == {"id": "1234", "username": "rum"}


@pytest.mark.asyncio
async def test_parse_response_plain_text():
    response = FakeResponse("hello", {"Content-Type": "text/plain"})
    assert await parse_response(response) == "hello"


@pytest.mark.asyncio
async def test_parse_response_empty_is_none():
    response = FakeResponse("", {"Content-Type": "application/json"}, status=204)
    assert await parse_response(response) is None


def test_response_proxy_headers_are_decoded():
    response = FakeResponse("{}", {"Content-Type": "application/json"})
    proxy = _ResponseProxy(response)
    assert proxy.headers.get("content-type") == "application/json"
    assert proxy.status == 200


def test_parse_ratelimit_header():
    response = FakeResponse(
        "",
        {
            "X-Ratelimit-Reset-After": "1.5",
            "X-Ratelimit-Remaining": "0",
        },
    )
    proxy = _ResponseProxy(response)
    assert utils._parse_ratelimit_header(proxy) == pytest.approx(1.5)


def test_ban_guard_counts_the_responses_discord_counts():
    guard = BanGuard(limit=10, window=60)
    guard.record(200)
    assert guard.count == 0
    guard.record(401)
    guard.record(403)
    guard.record(429)
    assert guard.count == 3


def test_ban_guard_marks_a_rejected_token():
    guard = BanGuard()
    assert not guard.revoked
    guard.record(401)
    assert guard.revoked


def test_ban_guard_holds_requests_back_at_the_limit():
    guard = BanGuard(limit=2, window=60)
    guard.record(403)
    assert guard.delay() == 0
    guard.record(429)
    assert guard.delay() > 0


def test_ban_guard_forgets_responses_outside_the_window():
    guard = BanGuard(limit=1, window=0)
    guard.record(403)
    assert guard.count == 0


def test_ban_guard_reset_clears_the_counted_responses():
    guard = BanGuard()
    guard.record(401)
    guard.reset()
    assert not guard.revoked
    assert guard.count == 0


@pytest.mark.asyncio
async def test_http_client_stops_after_a_rejected_token():
    client = HTTPClient()
    client.ban_guard.record(401)
    with pytest.raises(LoginFailure):
        await client.request(Route("GET", "/users/@me"))


async def _serve(handler):
    """Starts a local server that answers with what the handler returns."""
    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    return server, server.sockets[0].getsockname()[1]


@pytest.mark.asyncio
async def test_the_client_sends_the_request(monkeypatch):
    """The client sends the query, the headers and the body."""
    seen = {}

    async def handler(reader, writer):
        request_line = await reader.readline()
        headers = {}
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            key, _, value = line.decode().partition(":")
            headers[key.strip().lower()] = value.strip()
        length = int(headers.get("content-length", 0))
        body = await reader.readexactly(length) if length else b""
        seen.update(
            {
                "request": request_line.decode().split(),
                "headers": headers,
                "body": body,
            }
        )
        payload = b'{"ok": true}'
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
            + str(len(payload)).encode()
            + b"\r\n\r\n"
            + payload
        )
        await writer.drain()
        writer.close()

    server, port = await _serve(handler)
    monkeypatch.setattr(Route, "API_BASE_URL", f"http://127.0.0.1:{port}/api/v10")
    client = HTTPClient()
    try:
        result = await client.request(
            Route("POST", "/hello"),
            params={"a": 1},
            json={"hello": "world"},
            headers={"X-Test": "yes"},
        )
    finally:
        await client.close()
        server.close()

    assert result == {"ok": True}
    assert seen["request"][0] == "POST"
    assert seen["request"][1] == "/api/v10/hello?a=1"
    assert seen["headers"]["x-test"] == "yes"
    assert seen["headers"]["content-type"] == "application/json"
    assert seen["body"] == b'{"hello":"world"}'


@pytest.mark.asyncio
async def test_the_client_sends_a_multipart_body(monkeypatch):
    """A multipart body is built by the client."""
    seen = {}

    async def handler(reader, writer):
        await reader.readline()
        headers = {}
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            key, _, value = line.decode().partition(":")
            headers[key.strip().lower()] = value.strip()
        length = int(headers.get("content-length", 0))
        seen["headers"] = headers
        seen["body"] = await reader.readexactly(length) if length else b""
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
        await writer.drain()
        writer.close()

    server, port = await _serve(handler)
    monkeypatch.setattr(Route, "API_BASE_URL", f"http://127.0.0.1:{port}/api/v10")
    client = HTTPClient()
    try:
        await client.request(
            Route("POST", "/form"),
            form=[
                {"name": "payload_json", "value": b'{"a": 1}'},
                {"name": "files[0]", "value": b"binary", "filename": "a.txt"},
            ],
        )
    finally:
        await client.close()
        server.close()

    assert seen["headers"]["content-type"].startswith("multipart/form-data; boundary=")
    assert b"payload_json" in seen["body"]
    assert b'filename="a.txt"' in seen["body"]
