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
# link.py
import os
from urllib.parse import quote_plus

import rum


# Define a simple View that gives us a Google link button.
# We take in `query` as the query that the command author requests for.
class Google(rum.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # We need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f"https://www.google.com/search?q={query}"

        # Link buttons cannot be made with the
        # decorator, so we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(rum.ui.Button(label="Click Here", url=url))

        # Initializing the view and adding the button can actually be done in a one-liner at the start if preferred:
        # super().__init__(rum.ui.Button(label="Click Here", url=url))


bot = rum.Bot()


@bot.slash_command()
async def google(ctx: rum.ApplicationContext, query: str):
    """Returns a google link for a query."""
    await ctx.respond(f"Google Result for: `{query}`", view=Google(query))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
