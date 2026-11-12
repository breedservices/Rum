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
# create_private_emoji.py
import os

import rum

bot = rum.Bot()

allowed_content_types = [
    "image/jpeg",
    "image/png",
]  # Setting up allowed attachments types


# Discord doesn't support creating private emojis by default, its semi-implemented feature and can be done by bots only.


# This command is publicly available, to set up command permissions look for other examples in repo
@bot.command(guild_ids=[...])
async def add_private_emoji(
    ctx,
    name: rum.Option(str),
    image: rum.Option(rum.Attachment),
    role: rum.Option(rum.Role),
):
    if image.content_type not in allowed_content_types:
        return await ctx.respond("Invalid attachment type!", ephemeral=True)

    image_file = await image.read()  # Reading attachment's content to get bytes

    await ctx.guild.create_custom_emoji(
        name=name, image=image_file, roles=[role]
    )  # Image argument only takes bytes!
    await ctx.respond(content="Private emoji is successfully created!")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
