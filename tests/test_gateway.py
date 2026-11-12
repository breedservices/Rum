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

Tests for the gateway transport: the websocket and the zstd compression.
"""

import asyncio
import json

import h11
import pytest
import wsproto
from wsproto.connection import Connection as WSConnection
from wsproto.events import Message
from wsproto.utilities import generate_accept_token

from rum.gateway import DiscordWebSocket, _WebSocketAdapter, _ZstdStream
from rum.http import HTTPClient

try:  # Python 3.14 and later
    from compression import zstd

    def compress(data: bytes) -> bytes:
        return zstd.compress(data)

except ImportError:  # pragma: no cover
    import zstandard

    def compress(data: bytes) -> bytes:
        return zstandard.ZstdCompressor().compress(data)


async def _echo_server(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """A websocket server that answers with a message and closes."""
    http = h11.Connection(h11.SERVER)
    key = ""
    while True:
        event = http.next_event()
        if isinstance(event, h11.Request):
            key = dict(event.headers).get(b"sec-websocket-key", b"")
            break
        if event is h11.NEED_DATA:
            data = await reader.read(65536)
            if not data:
                writer.close()
                return
            http.receive_data(data)

    writer.write(
        http.send(
            h11.InformationalResponse(
                status_code=101,
                headers=[
                    ("Upgrade", "websocket"),
                    ("Connection", "Upgrade"),
                    (
                        "Sec-WebSocket-Accept",
                        generate_accept_token(key).decode("latin-1"),
                    ),
                ],
            )
        )
    )
    await writer.drain()

    connection = WSConnection(wsproto.ConnectionType.SERVER)
    while True:
        data = await reader.read(65536)
        if not data:
            break
        connection.receive_data(data)
        event = next(connection.events(), None)
        if event is None:
            continue
        if isinstance(event, Message):
            writer.write(connection.send(Message(data="hello")))
            await writer.drain()
            writer.write(connection.send(wsproto.events.CloseConnection(code=4000)))
            await writer.drain()
            break
    writer.close()


@pytest.mark.asyncio
async def test_the_gateway_sends_and_receives():
    """The gateway talks to a websocket server."""
    server = await asyncio.start_server(_echo_server, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    client = HTTPClient()
    try:
        socket = await client.ws_connect(f"ws://127.0.0.1:{port}")
        adapter = _WebSocketAdapter(socket)
        await adapter.send_str("ping")
        assert await adapter.receive(timeout=5) == "hello"
        assert await adapter.receive(timeout=5) is None
        assert adapter.closed
        assert adapter.close_code == 4000
    finally:
        await client.close()
        server.close()


@pytest.mark.asyncio
async def test_the_gateway_reads_a_message_over_several_messages():
    """A gateway message can be split over several websocket messages."""
    stream = _ZstdStream()
    event = {"op": 0, "t": "RESUMED", "s": 3, "d": {}}
    compressed = compress(json.dumps(event).encode())

    assert stream.message(compressed[:5]) is None
    assert stream.message(compressed[5:]) == json.dumps(event)


@pytest.mark.asyncio
async def test_the_gateway_decompresses_a_zstd_message():
    """A compressed gateway message is decompressed."""
    server = await asyncio.start_server(_echo_server, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    client = HTTPClient()
    try:
        socket = await client.ws_connect(f"ws://127.0.0.1:{port}")
        gateway = DiscordWebSocket(socket, loop=asyncio.get_running_loop())
        gateway.shard_id = 0
        gateway._discord_parsers = {}
        received = []
        gateway._dispatch = lambda event, *args: received.append((event, args))

        event = {"op": 0, "t": "RESUMED", "s": 3, "d": {}}
        await gateway.received_message(compress(json.dumps(event).encode()))

        assert received[0][0] == "socket_event_type"
        assert received[0][1] == ("RESUMED",)
    finally:
        await client.close()
        server.close()
