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
# community_invites.py
import os

import rum
from rum.utils import users_to_csv

bot = rum.Bot()


@bot.slash_command()
async def create_custom_invite(ctx: rum.ApplicationContext, user_ids: str):
    """Create an invite that only works for the specified users."""
    await ctx.defer()
    user_id_list = [int(uid.strip()) for uid in user_ids.split(",")]
    target_users_file = rum.File(
        users_to_csv([rum.Object(uid) for uid in user_id_list]),
        filename="users.csv",
    )
    invite = await ctx.channel.create_invite(
        max_age=3600,
        max_uses=1,
        target_users_file=target_users_file,
    )
    job_status = await invite.fetch_target_users_job_status()
    await ctx.respond(f"Invite created: {invite.url}, Job status: {job_status.status}")


@bot.slash_command()
async def create_custom_invite_from_file(
    ctx: rum.ApplicationContext, target_users: rum.Attachment
):
    await ctx.defer()
    target_users_file = await target_users.to_file()
    invite = await ctx.channel.create_invite(
        max_age=3600,
        max_uses=1,
        target_users_file=target_users_file,
    )
    job_status = await invite.fetch_target_users_job_status()
    await ctx.respond(f"Invite created: {invite.url}. Job status: {job_status.status}")


@bot.slash_command()
async def update_custom_invite(
    ctx: rum.ApplicationContext, invite_code: str, target_users: rum.Attachment
):
    await ctx.defer()
    invite = await bot.fetch_invite(invite_code)

    if invite.guild.id != ctx.guild.id:
        return await ctx.respond("You can only update invites from this server.")

    target_users_file = await target_users.to_file()
    await invite.edit_target_users(target_users_file=target_users_file)
    job_status = await invite.fetch_target_users_job_status()
    await ctx.respond(f"Invite updated: {invite.url}. Job status: {job_status.status}")


@bot.slash_command()
async def get_invite_target_users(ctx: rum.ApplicationContext, code: str):
    await ctx.defer()
    invite = await bot.fetch_invite(code)
    if invite.guild.id != ctx.guild.id:
        return await ctx.respond(
            "You can only get target users from invites from this server."
        )
    user_ids = await invite.target_users.as_user_ids()
    await ctx.respond(f"Target user IDs: {user_ids}")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
