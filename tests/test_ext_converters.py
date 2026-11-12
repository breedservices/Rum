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
"""

import inspect

import pytest

import discord
import rum
from rum.ext import bridge, commands
from rum.ext.commands import converter
from rum.ext.commands.view import StringView


class FakeContext:
    """A minimal context that is just enough to run converters."""

    def __init__(self, content: str = ""):
        self.view = StringView(content)
        self.guild = None
        self.message = None
        self.bot = None


@pytest.mark.parametrize(
    "annotation",
    [
        rum.Member,
        rum.User,
        rum.Role,
        rum.TextChannel,
        discord.Member,
        discord.User,
        discord.Role,
        discord.TextChannel,
    ],
)
def test_builtin_types_use_their_converter(annotation):
    param = inspect.Parameter(
        "value", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation
    )
    assert converter.get_converter(param) is annotation
    assert annotation in converter.CONVERTER_MAPPING
    assert converter.CONVERTER_MAPPING[annotation].__module__.startswith("rum.")


def test_unknown_annotations_are_left_alone():
    class Custom:
        pass

    param = inspect.Parameter(
        "value", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Custom
    )
    assert converter.get_converter(param) is Custom


def _bridge_bot():
    bot = bridge.Bot(command_prefix="!", intents=rum.Intents.default())

    @bot.bridge_command()
    @bridge.bridge_option("seconds", choices=range(1, 11))
    async def wait(ctx: bridge.BridgeContext, seconds: int = 5):
        return seconds

    @bot.bridge_command()
    @bridge.bridge_option("value", choices=[1, 2, 3])
    async def choose(ctx: bridge.BridgeContext, value: int):
        return value

    return bot


@pytest.mark.asyncio
async def test_bridge_option_uses_the_signature_default():
    bot = _bridge_bot()
    command = bot.bridge_commands[0].ext_variant
    param = command.params["seconds"]

    assert await command.transform(FakeContext(), param) == 5
    assert await command.transform(FakeContext("7"), param) == 7


@pytest.mark.asyncio
async def test_bridge_option_converts_choices():
    bot = _bridge_bot()
    command = bot.bridge_commands[1].ext_variant
    param = command.params["value"]

    assert await command.transform(FakeContext("2"), param) == 2
    with pytest.raises(commands.BadArgument):
        await command.transform(FakeContext("5"), param)


@pytest.mark.asyncio
async def test_option_annotations_are_converted():
    option = rum.Option(str)

    async def callback(ctx, value=option):
        return value

    param = inspect.Parameter(
        "value",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=rum.Option,
        default=option,
    )
    command = commands.Command(callback, name="test")
    assert await command.transform(FakeContext("hello"), param) == "hello"
