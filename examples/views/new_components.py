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
# new_components.py
import os
from io import BytesIO

from rum import (
    ApplicationContext,
    Bot,
    ButtonStyle,
    Color,
    File,
    Interaction,
    SeparatorSpacingSize,
    User,
)
from rum.ui import (
    ActionRow,
    Button,
    Container,
    DesignerView,
    MediaGallery,
    Section,
    Separator,
    TextDisplay,
    Thumbnail,
    button,
)


class MyRow(ActionRow):

    @button(label="Delete Message", style=ButtonStyle.red, id=200)
    async def delete_button(self, button: Button, interaction: Interaction):
        await interaction.response.defer(invisible=True)
        await interaction.message.delete()


class MyView(DesignerView):
    def __init__(self, user: User):
        super().__init__(timeout=30)
        text1 = TextDisplay("### This is a sample `TextDisplay` in a `Section`.")
        text2 = TextDisplay(
            "This section is contained in a `Container`.\nTo the right, you can see a `Thumbnail`."
        )
        thumbnail = Thumbnail(user.display_avatar.url)

        section = Section(text1, text2, accessory=thumbnail)
        section.add_text("-# Small text")

        container = Container(
            section,
            TextDisplay("Another `TextDisplay` separate from the `Section`."),
            color=Color.blue(),
        )
        container.add_separator(divider=True, spacing=SeparatorSpacingSize.large)
        container.add_item(Separator())
        container.add_file("attachment://sample.png")
        container.add_text("Above is two `Separator`s followed by a `File`.")

        gallery = MediaGallery()
        gallery.add_item(user.default_avatar.url)
        gallery.add_item(user.avatar.url)

        self.add_item(container)
        self.add_item(gallery)
        self.add_item(
            TextDisplay("Above is a `MediaGallery` containing two `MediaGalleryItem`s.")
        )
        row = MyRow()
        self.add_item(row)

    async def on_timeout(self):
        self.get_item(200).disabled = True
        await self.parent.edit(view=self)


bot = Bot()


@bot.command()
async def show_view(ctx: ApplicationContext):
    """Display a sample View showcasing various new components."""

    f = await ctx.author.display_avatar.read()
    file = File(BytesIO(f), filename="sample.png")
    await ctx.respond(view=MyView(ctx.author), files=[file])


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
