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
# persistent.py
# This example requires the `message_content` privileged intent for prefixed commands.

import os
import rum
from rum.ext import commands


# Define a simple View that persists between bot restarts.
# In order for a View to persist between restarts it needs to meet the following conditions:
# 1) The timeout of the View has to be set to None
# 2) Every item in the View has to have a custom_id set
# It is recommended that the custom_id be sufficiently unique to
# prevent conflicts with other buttons the bot sends.
# For this example the custom_id is prefixed with the name of the bot.
# Note that custom_ids can only be up to 100 characters long.
class PersistentView(rum.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @rum.ui.button(
        label="Green",
        style=rum.ButtonStyle.green,
        custom_id="persistent_view:green",
    )
    async def green(self, button: rum.ui.Button, interaction: rum.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)

    @rum.ui.button(
        label="Red", style=rum.ButtonStyle.red, custom_id="persistent_view:red"
    )
    async def red(self, button: rum.ui.Button, interaction: rum.Interaction):
        await interaction.response.send_message("This is red.", ephemeral=True)

    @rum.ui.button(
        label="Grey", style=rum.ButtonStyle.grey, custom_id="persistent_view:grey"
    )
    async def grey(self, button: rum.ui.Button, interaction: rum.Interaction):
        await interaction.response.send_message("This is grey.", ephemeral=True)


class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = rum.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=intents
        )
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            # Register the persistent view for listening here.
            # Note that this does not send the view to any message.
            # In order to do this you need to first send a message with the View, which is shown below.
            # If you have the message_id you can also pass it as a keyword argument,
            # but for this example we don't have one.
            self.add_view(PersistentView())
            self.persistent_views_added = True

        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


bot = PersistentViewBot()


@bot.command()
@commands.is_owner()
async def prepare(ctx: commands.Context):
    """Starts a persistent view."""
    # In order for a persistent view to be listened to, it needs to be sent to an actual message.
    # Call this method once just to store it somewhere.
    # In a more complicated program you might fetch the message_id from a database for use later.
    # However, this is outside the scope of this simple example.
    await ctx.send("What's your favourite colour?", view=PersistentView())


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
