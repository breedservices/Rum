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

"""Tests for the guild id sanitisation used when syncing application commands."""

import rum
from rum.bot import _sanitize_guild_ids


def test_sanitize_guild_ids_filters_placeholders():
    # ``...`` is what Ellipsis evaluates to and is used as a placeholder in
    # the examples. Passing it to Discord results in a 400 response.
    assert _sanitize_guild_ids([...]) == []
    assert _sanitize_guild_ids([Ellipsis]) == []
    assert _sanitize_guild_ids([123, ...]) == [123]
    assert _sanitize_guild_ids([123, 456]) == [123, 456]
    assert _sanitize_guild_ids([]) == []
    assert _sanitize_guild_ids(None) is None
    assert _sanitize_guild_ids(123) == [123]


def test_sanitize_guild_ids_ignores_booleans():
    assert _sanitize_guild_ids([True]) == []


def test_bot_debug_guilds_are_sanitized():
    bot = rum.Bot(debug_guilds=[...])
    assert bot.debug_guilds == []


def test_bot_debug_guilds_keep_valid_ids():
    bot = rum.Bot(debug_guilds=[123, 456])
    assert bot.debug_guilds == [123, 456]
