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
# ephemeral.py
import os

import rum


# Define a simple View that gives us a counter button.
class Counter(rum.ui.View):
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled, and it turns green.
    # NOTE: The name of the function does not matter to the library.
    @rum.ui.button(label="0", style=rum.ButtonStyle.red)
    async def count(self, button: rum.ui.Button, interaction: rum.Interaction):
        number = int(button.label) if button.label else 0
        if number >= 4:
            button.style = rum.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


# Define a View that will give us our own personal counter button.
class EphemeralCounter(rum.ui.View):
    # When this button is pressed, it will respond with a Counter View that will
    # give the button presser their own personal button they can press 5 times.
    @rum.ui.button(label="Click", style=rum.ButtonStyle.blurple)
    async def receive(
        self, button: rum.ui.Button, interaction: rum.Interaction
    ):
        # ephemeral=True makes the message hidden from everyone except the button presser.
        await interaction.response.send_message(
            "Enjoy!", view=Counter(), ephemeral=True
        )


bot = rum.Bot()


@bot.slash_command()
async def counter(ctx: rum.ApplicationContext):
    """Starts a counter for pressing."""
    await ctx.respond("Press!", view=EphemeralCounter())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
