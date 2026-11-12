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

# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# bridge_commands.py
# This example requires the `message_content` privileged intent for prefixed commands.

import asyncio
import os

import rum
from rum.ext import bridge, commands

intents = rum.Intents.default()
intents.message_content = True

bot = bridge.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents
)


@bot.bridge_command()
async def ping(ctx: bridge.BridgeContext):
    await ctx.respond("Pong!")


@bot.bridge_command()
@bridge.bridge_option("value", choices=[1, 2, 3])
async def choose(ctx: bridge.BridgeContext, value: int):
    await ctx.respond(f"You chose: {value}!")


@bot.bridge_command()
async def welcome(ctx: bridge.BridgeContext, member: rum.Member):
    await ctx.respond(f"Welcome {member.mention}!")


@bot.bridge_command()
@bridge.bridge_option("seconds", choices=range(1, 11))
async def wait(ctx: bridge.BridgeContext, seconds: int = 5):
    await ctx.defer()
    await asyncio.sleep(seconds)
    await ctx.respond(f"Waited for {seconds} seconds!")


@bot.bridge_group(invoke_without_command=True)
@bridge.map_to("help")
async def specialcmd(ctx: bridge.BridgeContext):
    # with the `map_to` decorator, the main command becomes
    # accessible through the slash command `/specialcmd help`
    await ctx.respond("This is a special command!")


@specialcmd.command()
async def file(ctx: bridge.BridgeContext, attachment: rum.Attachment):
    await ctx.respond(f"The name of that file is `{attachment.filename}`")

    url_msg = f"psss, here's its url: {attachment.url}"

    if ctx.is_app:
        # the command was run from a slash
        # command, so we can use a followup
        await ctx.followup.send(url_msg, ephemeral=True)
    else:
        await ctx.author.send(url_msg)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    # This is raised when a choice outside the given choices is selected on a prefixed command.
    if isinstance(error, commands.BadArgument):
        if ctx.command.name == "choose":
            await ctx.reply("Hey! The valid choices are 1, 2, or 3!")
        else:
            await ctx.reply("I couldn't understand that argument.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"You're missing the `{error.param.name}` argument.")
    else:
        raise error  # Raise other errors so they aren't ignored


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
