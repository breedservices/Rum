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
# context_menus.py
# This example requires the 'members' privileged intent to use the Member converter.

import os
import rum

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(intents=intents)
# Remove debug_guilds and set guild_ids in the slash command decorators
# to restrict specific commands to the supplied guild IDs.


@bot.user_command()  # Create a global user command
async def mention(
    ctx: rum.ApplicationContext, member: rum.Member
):  # User commands give a member param
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")


# User commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # Creates a global message command
async def show_id(
    ctx: rum.ApplicationContext, message: rum.Message
):  # Message commands give a message param
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
