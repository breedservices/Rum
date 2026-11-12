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
# slash_cog_groups.py
# This example requires the 'members' privileged intent to use the Member converter.

import os

import rum
from rum.commands import SlashCommandGroup
from rum.ext import commands

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(intents=intents, owner_id=...)  # Main file


class Example(commands.Cog):
    def __init__(self, bot_: rum.Bot):
        self.bot = bot_

    greetings = SlashCommandGroup("greetings", "Various greeting from cogs!")

    international_greetings = greetings.create_subgroup(
        "international", "International greetings"
    )

    secret_greetings = SlashCommandGroup(
        "secret_greetings",
        "Secret greetings",
        checks=[
            commands.is_owner().predicate
        ],  # Ensures the owner_id user can access this group, and no one else
    )

    @greetings.command()
    async def hello(self, ctx: rum.ApplicationContext):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")

    @international_greetings.command()
    async def aloha(self, ctx: rum.ApplicationContext):
        await ctx.respond("Aloha, a Hawaiian greeting")

    @secret_greetings.command()
    async def secret_handshake(
        self, ctx: rum.ApplicationContext, member: rum.Member
    ):
        await ctx.respond(f"{member.mention} secret handshakes you")

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: rum.ApplicationContext, error: rum.DiscordException
    ):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("You can't use that command!")
        else:
            raise error  # Raise other errors so they aren't ignored


bot.add_cog(Example(bot))  # Put in a setup function for cog files
bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))  # Main file
