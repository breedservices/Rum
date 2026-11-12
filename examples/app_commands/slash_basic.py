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
# slash_basic.py
# This example requires the 'members' privileged intent to use the Member converter.

import os
import rum

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(intents=intents)
# The debug guilds parameter can be used to restrict slash command registration to only the supplied guild IDs.
# This is done like so: rum.Bot()
# Without this, all commands are made global unless they have a guild_ids parameter in the command decorator.

# Note: If you want you can use commands.Bot instead of rum.Bot.
# Use rum.Bot if you don't want prefixed message commands.

# With rum.Bot you can use @bot.command as an alias
# of @bot.slash_command but this is overridden by commands.Bot.


@bot.slash_command(guild_ids=[...])  # Create a slash command
async def hello(ctx: rum.ApplicationContext):
    """Say hello to the bot"""  # The command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")
    # Note: interactions must be responded to within 3 seconds, if they're not, an
    # "Unknown interaction" error will be raised, you can circumvent this by using "ctx.defer()".
    # Additional note: You cannot respond to the same interaction twice!


@bot.slash_command(name="hi")
async def global_command(
    ctx: rum.ApplicationContext, num: int
):  # Takes one integer parameter
    await ctx.respond(f"This is a global command, {num}!")


@bot.slash_command(guild_ids=[...])
async def joined(ctx: rum.ApplicationContext, member: rum.Member = None):
    # Setting a default value for the member parameter makes it optional ^
    user = member or ctx.author
    await ctx.respond(
        f"{user.name} joined at {rum.utils.format_dt(user.joined_at)}"
    )


# To learn how to add descriptions and choices to options, check slash_options.py
bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
