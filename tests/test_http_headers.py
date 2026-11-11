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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""Tests for the wreq header handling.

``wreq`` returns header names and values as read-only ``memoryview`` objects
rather than strings, so the library has to decode them before comparing them
against strings.
"""

import pytest

from rum import utils
from rum.http import _ResponseProxy, parse_response


class FakeHeaderMap:
    """Mimics ``wreq.HeaderMap``: case-insensitive, memoryview values."""

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
    assert utils._decode_header_value(memoryview(b"application/json")) == "application/json"
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
