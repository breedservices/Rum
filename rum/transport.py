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

The HTTP and websocket transport of the library.

The transport is written on h11 and wsproto, which speak HTTP/1.1 and the
websocket protocol over asyncio. Doing it here keeps the library free of the
heavier HTTP clients, which cost tens of megabytes of memory before the bot
has done anything at all.
"""

from __future__ import annotations

import asyncio
import base64
import os
import ssl
import uuid
from http import HTTPStatus
from collections.abc import AsyncIterator, Iterable, Mapping
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any
from urllib.parse import urlencode, urlsplit

import h11
import wsproto
from wsproto.connection import Connection as WSConnection
from wsproto.events import (
    BytesMessage,
    CloseConnection,
    Message,
    Ping,
    Pong,
    TextMessage,
)

from . import utils

__all__ = ("Session", "WebSocket", "multipart_body")

#: How much of a response is read at once.
CHUNK_SIZE = 65536


def multipart_body(form: Iterable[dict[str, Any]]) -> tuple[bytes, str]:
    """Builds a multipart body and returns it with its content type."""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for params in form:
        name = params.get("name")
        value = params.get("value")
        if hasattr(value, "read"):
            value = value.read()
        if isinstance(value, str):
            value = value.encode("utf-8")
        filename = params.get("filename")
        content_type = params.get("content_type") or params.get("content-type")
        body += f"--{boundary}\r\n".encode()
        disposition = f'form-data; name="{name}"'
        if filename is not None:
            disposition += f'; filename="{filename}"'
        body += f"Content-Disposition: {disposition}\r\n".encode()
        if content_type is not None:
            body += f"Content-Type: {content_type}\r\n".encode()
        body += b"\r\n"
        body += value
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def _headers_to_dict(headers: Any) -> dict[str, str]:
    """Turns the headers of h11 into a dictionary of strings."""
    return {
        key.decode("latin-1").lower(): value.decode("latin-1") for key, value in headers
    }


class Response:
    """The response of an HTTP request."""

    __slots__ = ("_body", "_headers", "_status")

    def __init__(
        self, status: int, headers: list[tuple[bytes, bytes]], body: bytes
    ) -> None:
        self._status = status
        self._headers = _headers_to_dict(headers)
        self._body = body

    @property
    def status(self) -> int:
        """The status of the response."""
        return self._status

    @property
    def headers(self) -> dict[str, str]:
        """The headers of the response."""
        return self._headers

    @property
    def reason(self) -> str:
        """The reason phrase of the response."""
        try:
            return HTTPStatus(self._status).phrase
        except ValueError:
            return ""

    async def bytes(self) -> bytes:
        """The body of the response."""
        return self._body

    async def text(self, encoding: str = "utf-8") -> str:
        """The body of the response, as text."""
        return self._body.decode(encoding, errors="replace")


class _Connection:
    """One HTTP/1.1 connection to a host."""

    __slots__ = (
        "_h11",
        "_host",
        "_port",
        "_reader",
        "_ssl_context",
        "_timeout",
        "_writer",
    )

    def __init__(
        self,
        host: str,
        port: int,
        *,
        ssl_context: ssl.SSLContext | None,
        timeout: float,
    ) -> None:
        self._host = host
        self._port = port
        self._ssl_context = ssl_context
        self._timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._h11: h11.Connection | None = None

    async def open(self) -> None:
        """Opens the connection."""
        context = self._ssl_context
        if context is None and self._port == 443:
            context = ssl.create_default_context()
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(
                self._host,
                self._port,
                ssl=context,
                server_hostname=self._host if context is not None else None,
            ),
            self._timeout,
        )
        self._h11 = h11.Connection(h11.CLIENT)

    async def close(self) -> None:
        """Closes the connection."""
        writer, self._writer = self._writer, None
        self._reader = None
        self._h11 = None
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    @property
    def closed(self) -> bool:
        """Whether the connection is closed."""
        return self._writer is None or self._writer.is_closing()

    async def send(
        self,
        method: str,
        target: str,
        headers: list[tuple[str, str]],
        body: bytes | None,
    ) -> None:
        """Sends a request."""
        assert self._h11 is not None and self._writer is not None
        if self._h11.our_state is h11.DONE:
            # h11 keeps the state of one request, the next one starts a new cycle
            self._h11.start_next_cycle()
        self._writer.write(
            self._h11.send(
                h11.Request(
                    method=method,
                    target=target,
                    headers=[
                        (key.encode("latin-1"), value.encode("latin-1"))
                        for key, value in headers
                    ],
                )
            )
        )
        if body:
            self._writer.write(self._h11.send(h11.Data(data=body)))
        self._writer.write(self._h11.send(h11.EndOfMessage()))
        await self._writer.drain()

    async def receive(self) -> Response:
        """Reads a response."""
        assert self._h11 is not None and self._reader is not None
        while True:
            event = self._h11.next_event()
            if isinstance(event, h11.Response):
                body = bytearray()
                while True:
                    body_event = self._h11.next_event()
                    if isinstance(body_event, h11.Data):
                        body.extend(body_event.data)
                    elif isinstance(body_event, h11.EndOfMessage):
                        break
                    elif body_event is h11.NEED_DATA:
                        await self._read_more()
                return Response(event.status_code, list(event.headers), bytes(body))
            if event is h11.NEED_DATA:
                await self._read_more()

    async def stream(self) -> AsyncIterator[bytes]:
        """Yields the body of the response as it comes in."""
        assert self._h11 is not None
        while True:
            event = self._h11.next_event()
            if isinstance(event, h11.Data):
                yield event.data
            elif isinstance(event, h11.EndOfMessage):
                return
            elif event is h11.NEED_DATA:
                await self._read_more()

    async def _read_more(self) -> None:
        assert self._reader is not None and self._h11 is not None
        data = await asyncio.wait_for(self._reader.read(CHUNK_SIZE), self._timeout)
        if not data:
            raise ConnectionError("the connection was closed")
        self._h11.receive_data(data)


class Session:
    """The HTTP session of the client.

    The session keeps one connection per host alive and reuses it, the way a
    browser does.

    Parameters
    ----------
    proxy: :class:`str` | :obj:`None`
        The proxy every request of the session goes through.
    timeout: :class:`float`
        How long a request may take, in seconds.
    """

    __slots__ = ("_connections", "_timeout")

    def __init__(self, *, proxy: str | None = None, timeout: float = 30.0) -> None:
        self._timeout = timeout
        self._connections: dict[tuple[str, int], _Connection] = {}

    @asynccontextmanager
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        json: Any = None,
        multipart: Iterable[dict[str, Any]] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> AsyncIterator[Response]:
        """Makes a request and returns the response."""
        response = await self._request(
            method,
            url,
            headers=headers,
            body=body,
            json=json,
            multipart=multipart,
            params=params,
        )
        yield response

    async def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        json: Any = None,
        multipart: Iterable[dict[str, Any]] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Response:
        """Makes a request and returns the response."""
        if params:
            url = f"{url}?{urlencode(params)}"
        headers = dict(headers or {})
        if multipart is not None:
            body, content_type = multipart_body(multipart)
            headers.setdefault("Content-Type", content_type)
        elif json is not None:
            body = utils._to_json(json).encode("utf-8")
        if body is not None:
            headers.setdefault("Content-Length", str(len(body)))

        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port or (443 if parts.scheme == "https" else 80)
        target = parts.path or "/"
        if parts.query:
            target = f"{target}?{parts.query}"

        request_headers = [("Host", parts.netloc)]
        request_headers.extend(headers.items())

        connection = self._connections.get((host, port))
        if connection is None or connection.closed:
            connection = _Connection(
                host, port, ssl_context=None, timeout=self._timeout
            )
            await connection.open()
            self._connections[(host, port)] = connection

        await connection.send(method, target, request_headers, body)
        return await connection.receive()

    @asynccontextmanager
    async def get(self, url: str) -> AsyncIterator[Response]:
        """Makes a GET request and returns the response."""
        async with self.request("GET", url) as response:
            yield response

    async def stream(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> AsyncIterator[bytes]:
        """Makes a request and yields the body as it comes in."""
        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port or (443 if parts.scheme == "https" else 80)
        target = parts.path or "/"
        if parts.query:
            target = f"{target}?{parts.query}"
        request_headers = [("Host", parts.netloc)]
        request_headers.extend((headers or {}).items())

        connection = self._connections.get((host, port))
        if connection is None or connection.closed:
            connection = _Connection(
                host, port, ssl_context=None, timeout=self._timeout
            )
            await connection.open()
            self._connections[(host, port)] = connection

        await connection.send(method, target, request_headers, None)
        async for chunk in connection.stream():
            yield chunk

    async def aclose(self) -> None:
        """Closes the session and its connections."""
        connections = list(self._connections.values())
        self._connections.clear()
        for connection in connections:
            await connection.close()

    async def __aenter__(self) -> Session:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()


class WebSocket:
    """A websocket client, written on h11 and wsproto."""

    __slots__ = ("_close_code", "_closed", "_reader", "_writer", "_ws")

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._ws = WSConnection(wsproto.ConnectionType.CLIENT)
        self._closed = False
        self._close_code: int | None = None

    @classmethod
    async def connect(
        cls,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> WebSocket:
        """Opens a websocket connection."""
        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port or (443 if parts.scheme == "wss" else 80)
        context = ssl.create_default_context() if parts.scheme == "wss" else None
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                host,
                port,
                ssl=context,
                server_hostname=host if context is not None else None,
            ),
            timeout,
        )
        socket = cls(reader, writer)
        await socket._handshake(parts, headers or {})
        return socket

    async def _handshake(self, parts: Any, headers: Mapping[str, str]) -> None:
        connection = h11.Connection(h11.CLIENT)
        key = base64.b64encode(os.urandom(16)).decode()
        target = parts.path or "/"
        if parts.query:
            target = f"{target}?{parts.query}"
        request_headers = [
            ("Host", parts.netloc),
            ("Upgrade", "websocket"),
            ("Connection", "Upgrade"),
            ("Sec-WebSocket-Key", key),
            ("Sec-WebSocket-Version", "13"),
        ]
        request_headers.extend(headers.items())
        self._writer.write(
            connection.send(
                h11.Request(
                    method="GET",
                    target=target,
                    headers=[
                        (name.encode("latin-1"), value.encode("latin-1"))
                        for name, value in request_headers
                    ],
                )
            )
        )
        self._writer.write(connection.send(h11.EndOfMessage()))
        await self._writer.drain()

        while True:
            event = connection.next_event()
            if isinstance(event, h11.InformationalResponse):
                if event.status_code != 101:
                    raise ConnectionError(
                        f"the server refused the upgrade: {event.status_code}"
                    )
                break
            if event is h11.NEED_DATA:
                data = await self._reader.read(CHUNK_SIZE)
                if not data:
                    raise ConnectionError("the connection was closed")
                connection.receive_data(data)
            elif isinstance(event, h11.Response):
                raise ConnectionError(
                    f"the server refused the upgrade: {event.status_code}"
                )

        trailing = connection.trailing_data
        if trailing and trailing[0]:
            self._ws.receive_data(trailing[0])

    @property
    def closed(self) -> bool:
        """Whether the connection is closed."""
        return self._closed

    @property
    def close_code(self) -> int | None:
        """The code the connection was closed with."""
        return self._close_code

    async def send(self, data: str | bytes) -> None:
        """Sends a message."""
        if self._closed:
            raise ConnectionError("the connection is closed")
        event = Message(data=data)
        self._writer.write(self._ws.send(event))
        await self._writer.drain()

    async def recv(self, timeout: float | None = None) -> str | bytes | None:
        """Receives a message, or ``None`` when the connection is closed."""
        while True:
            # the generator of the events ends when there is nothing to yield,
            # so a new one is taken every time
            event = next(self._ws.events(), None)
            if event is None:
                data = await asyncio.wait_for(self._reader.read(CHUNK_SIZE), timeout)
                if not data:
                    self._closed = True
                    return None
                self._ws.receive_data(data)
                continue
            if isinstance(event, (TextMessage, BytesMessage)):
                return event.data
            if isinstance(event, CloseConnection):
                self._closed = True
                self._close_code = event.code
                return None
            if isinstance(event, Ping):
                self._writer.write(self._ws.send(Pong(payload=event.payload)))
                await self._writer.drain()

    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Closes the connection."""
        if self._closed:
            return
        self._closed = True
        self._close_code = code
        try:
            self._writer.write(self._ws.send(CloseConnection(code=code, reason=reason)))
            await self._writer.drain()
        except Exception:
            pass
        self._writer.close()
