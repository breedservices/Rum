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
# modal_dialogs.py
# This example requires the `message_content` privileged intent for prefixed commands.

import os

import rum
from rum.ext import commands

intents = rum.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents
)


class MyModal(rum.ui.DesignerModal):
    def __init__(self, *args, **kwargs) -> None:
        first_input = rum.ui.Label(
            "Short Input",
            rum.ui.InputText(
                placeholder="Placeholder Test",
            ),
        )
        second_input = rum.ui.Label(
            "Longer Input",
            rum.ui.InputText(
                placeholder="Placeholder Test",
                value="Longer Value\nSuper Long Value",
                style=rum.InputTextStyle.long,
            ),
            description="You can also describe the purpose of this input.",
        )
        select = rum.ui.Label(
            "What's your favorite color?",
            rum.ui.Select(
                placeholder="Select a color",
                options=[
                    rum.SelectOption(label="Red", emoji="🟥"),
                    rum.SelectOption(label="Green", emoji="🟩"),
                    rum.SelectOption(label="Blue", emoji="🟦"),
                ],
                required=False,
            ),
            description="If it is not listed, skip this question.",
        )
        file = rum.ui.Label(
            "What's your favorite picture?",
            rum.ui.FileUpload(
                max_values=1,
                required=False,
            ),
            description="You may only pick one! Chose wisely!",
        )
        super().__init__(
            first_input,
            second_input,
            rum.ui.TextDisplay(
                "# Personal Questions"
            ),  # TextDisplay does NOT use Label
            select,
            file,
            *args,
            **kwargs,
        )

    async def callback(self, interaction: rum.Interaction):
        await interaction.response.defer()
        embed = rum.Embed(
            title="Your Modal Results",
            fields=[
                rum.EmbedField(
                    name="First Input", value=self.children[0].item.value, inline=False
                ),
                rum.EmbedField(
                    name="Second Input", value=self.children[1].item.value, inline=False
                ),
                rum.EmbedField(
                    name="Favorite Color",
                    value=self.children[3].item.values[0],
                    inline=False,
                ),
            ],
            color=rum.Color.random(),
        )
        attachment = (
            self.children[4].item.values[0] if self.children[4].item.values else None
        )
        if attachment:
            embed.set_image(url=f"attachment://{attachment.filename}")
        await interaction.followup.send(
            embeds=[embed],
            files=[await attachment.to_file()] if attachment else [],
        )


@bot.slash_command(name="modaltest")
async def modal_slash(ctx: rum.ApplicationContext):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = MyModal(title="Slash Command Modal")
    await ctx.send_modal(modal)


@bot.message_command(name="messagemodal")
async def modal_message(ctx: rum.ApplicationContext, message: rum.Message):
    """Shows an example of a modal dialog being invoked from a message command."""
    modal = MyModal(title="Message Command Modal")
    modal.title = f"Modal for Message ID: {message.id}"
    await ctx.send_modal(modal)


@bot.user_command(name="usermodal")
async def modal_user(ctx: rum.ApplicationContext, member: rum.Member):
    """Shows an example of a modal dialog being invoked from a user command."""
    modal = MyModal(title="User Command Modal")
    modal.title = f"Modal for User: {member.display_name}"
    await ctx.send_modal(modal)


@bot.command()
async def modaltest(ctx: commands.Context):
    """Shows an example of modals being invoked from an interaction component (e.g. a button or select menu)"""

    class MyView(rum.ui.View):
        @rum.ui.button(label="Modal Test", style=rum.ButtonStyle.primary)
        async def button_callback(
            self, button: rum.ui.Button, interaction: rum.Interaction
        ):
            modal = MyModal(title="Modal Triggered from Button")
            await interaction.response.send_modal(modal)

        @rum.ui.select(
            placeholder="Pick Your Modal",
            min_values=1,
            max_values=1,
            options=[
                rum.SelectOption(
                    label="First Modal", description="Shows the first modal"
                ),
                rum.SelectOption(
                    label="Second Modal", description="Shows the second modal"
                ),
            ],
        )
        async def select_callback(
            self, select: rum.ui.Select, interaction: rum.Interaction
        ):
            modal = MyModal(title="Temporary Title")
            modal.title = select.values[0]
            await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.send("Click Button, Receive Modal", view=view)


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
