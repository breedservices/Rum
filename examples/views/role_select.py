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
# role_select.py
import os

import rum

# Role selects (dropdowns) are a new type of select menu/dropdown Discord has added so people can select server roles from a dropdown.


# Defines a simple View that allows the user to use the Select menu.
# In this view, we define the role_select with `rum.ui.role_select`
# Using the decorator automatically sets `select_type` to `rum.ComponentType.role_select`.
class DropdownView(rum.ui.View):
    @rum.ui.role_select(
        placeholder="Select roles...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 roles in the dropdown
    async def role_select_dropdown(
        self, select: rum.ui.RoleSelect, interaction: rum.Interaction
    ) -> None:
        # update the select default values to set them to the select ones
        select.default_values = select.values  # this is a list of Role
        await interaction.response.send_message(
            "You selected the following roles:"
            + ", ".join(f"{role.mention}" for role in select.values),
            view=self,
        )


bot: rum.Bot = rum.Bot()


@bot.slash_command()
async def role_select(ctx: rum.ApplicationContext) -> None:
    """Sends a message with our dropdown that contains a role select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select roles:", view=view)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
