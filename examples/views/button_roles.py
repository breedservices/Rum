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
# button_roles.py
import os
import rum
from rum.ext import commands

"""
Let users assign themselves roles by clicking on Buttons.
The view made is persistent, so it will work even when the bot restarts.

See this example for more information about persistent views:
https://github.com/breedservices/Rum/blob/master/examples/views/persistent.py
Make sure to load this cog when your bot starts!
"""

# This is the list of role IDs that will be added as buttons.
role_ids = [...]


class RoleButton(rum.ui.Button):
    def __init__(self, role: rum.Role):
        """A button for one role. `custom_id` is needed for persistent views."""
        super().__init__(
            label=role.name,
            style=rum.ButtonStyle.primary,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: rum.Interaction):
        """
        This function will be called any time a user clicks on this button.

        Parameters
        ----------
        interaction: :class:`rum.Interaction`
            The interaction object that was created when a user clicks on a button.
        """
        # Get the user who clicked the button.
        user = interaction.user
        # Get the role this button is for (stored in the custom ID).
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # If the specified role does not exist, return nothing.
            # Error handling could be done here.
            return

        # Add the role and send a response to the user ephemerally (hidden to other users).
        if role not in user.roles:
            # Give the user the role if they don't already have it.
            await user.add_roles(role)
            await interaction.response.send_message(
                f"🎉 You have been given the role {role.mention}!",
                ephemeral=True,
            )
        else:
            # Otherwise, take the role away from the user.
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ The {role.mention} role has been taken from you!",
                ephemeral=True,
            )


class ButtonRoleCog(commands.Cog):
    """
    A cog with a slash command for posting the message with buttons
    and to initialize the view again when the bot is restarted.
    """

    def __init__(self, bot):
        self.bot = bot

    # Pass a list of guild IDs to restrict usage to the supplied guild IDs.
    @commands.slash_command(guild_ids=[...], description="Post the button role message")
    async def post(self, ctx: rum.ApplicationContext):
        """Slash command to post a new view with a button for each role."""

        # timeout is None because we want this view to be persistent.
        view = rum.ui.View(timeout=None)

        # Loop through the list of roles and add a new button to the view for each role.
        for role_id in role_ids:
            # Get the role from the guild by ID.
            role = ctx.guild.get_role(role_id)
            view.add_item(RoleButton(role))

        await ctx.respond("Click a button to assign yourself a role", view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        This method is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons),
        it will be loaded and the bot will start watching for button clicks again.
        """
        # We recreate the view as we did in the /post command.
        view = rum.ui.View(timeout=None)
        # Make sure to set the guild ID here to whatever server you want the buttons in!
        guild = self.bot.get_guild(...)
        for role_id in role_ids:
            role = guild.get_role(role_id)
            view.add_item(RoleButton(role))

        # Add the view to the bot so that it will watch for button interactions.
        self.bot.add_view(view)


def setup(bot):
    bot.add_cog(ButtonRoleCog(bot))


# The basic bot instance in a separate file should look something like this:
# bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
# bot.load_extension("button_roles")
# bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
