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
# reaction_roles.py
import os
import rum

intents = rum.Intents.default()
intents.members = True  # < This may give you `read-only` warning, just ignore it.
# This intent requires "Server Members Intent" to be enabled at https://discord.com/developers


bot = rum.Bot(intents=intents)

role_message_id = (
    0  # ID of the message that can be reacted to for adding/removing a role.
)

emoji_to_role = {
    rum.PartialEmoji(
        name="🔴"
    ): 0,  # ID of the role associated with unicode emoji '🔴'.
    rum.PartialEmoji(
        name="🟡"
    ): 0,  # ID of the role associated with unicode emoji '🟡'.
    rum.PartialEmoji(
        name="green", id=0
    ): 0,  # ID of the role associated with a partial emoji's ID.
}


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_raw_reaction_add(payload: rum.RawReactionActionEvent):
    """Gives a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about.
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Make sure we're still in the guild, and it's cached.
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    try:
        # Finally, add the role.
        await payload.member.add_roles(role)
    except rum.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass


@bot.event
async def on_raw_reaction_remove(payload: rum.RawReactionActionEvent):
    """Removes a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about.
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Make sure we're still in the guild, and it's cached.
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    # The payload for `on_raw_reaction_remove` does not provide `.member`
    # so we must get the member ourselves from the payload's `.user_id`.
    member = guild.get_member(payload.user_id)
    if member is None:
        # Make sure the member still exists and is valid.
        return

    try:
        # Finally, remove the role.
        await member.remove_roles(role)
    except rum.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
