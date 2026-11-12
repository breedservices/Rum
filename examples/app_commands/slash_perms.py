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
# slash_perms.py
import os
import rum

bot = rum.Bot()


@bot.slash_command()
@rum.default_permissions(
    administrator=True,
)  # Only members with this permission can use this command.
async def admin_only(ctx: rum.ApplicationContext):
    await ctx.respond(f"Hello {ctx.author}, you are an administrator.")


@bot.slash_command()
@rum.default_permissions(
    manage_messages=True,
    ban_members=True,
)  # You can supply multiple permissions that are required to use the command.
async def staff_only(ctx: rum.ApplicationContext):
    await ctx.respond(f"Hello {ctx.author}, you can manage messages and ban members.")


"""
Server owners and administrators have all permissions and can change required permissions per-server.
If the member viewing commands does not have the required permissions, the commands will show up disabled.
"""


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
