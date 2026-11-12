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
# slash_options.py
import os

import rum
from rum import option

bot = rum.Bot()


# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with rum.Bot as well.


@bot.slash_command()
@option("name", description="Enter your name")
@option(
    "pokemon",
    description="Choose your starter Pokémon",
    choices=["Bulbasaur", "Squirtle", "Charmander", "Pikachu"],
)
@option(
    "age",
    description="Enter your age",
    min_value=1,
    max_value=99,
    default=18,
    # Passing the default value makes an argument optional.
    # You also can create optional arguments using:
    # age: Option(int, "Enter your age") = 18
)
async def hello(
    ctx: rum.ApplicationContext,
    name: str,
    pokemon: str,
    age: int,
):
    await ctx.respond(
        f"Hello {name}! Your starter Pokémon is {pokemon} and you are {age} years old."
    )


@bot.slash_command(name="channel")
@option(
    "channel",
    rum.TextChannel | rum.VoiceChannel,
    # You can specify allowed channel types by passing a union of them like this.
    description="Select a channel",
)
async def select_channel(
    ctx: rum.ApplicationContext,
    channel: rum.TextChannel | rum.VoiceChannel,
):
    await ctx.respond(f"Hi! You selected {channel.mention} channel.")


@bot.slash_command(name="attach_file")
@option(
    "attachment",
    rum.Attachment,
    description="A file to attach to the message",
    required=False,  # The default value will be None if the user doesn't provide a file.
)
async def say(
    ctx: rum.ApplicationContext,
    attachment: rum.Attachment,
):
    """This demonstrates how to attach a file with a slash command."""
    if attachment:
        file = await attachment.to_file()
        await ctx.respond("Here's your file!", file=file)
    else:
        await ctx.respond("You didn't give me a file to reply with! :sob:")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
