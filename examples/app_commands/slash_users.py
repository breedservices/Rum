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
# slash_users.py
import os

import rum

# debug_guilds must not be set if we want to set contexts and integration_types on commands
bot = rum.Bot()


@bot.slash_command(
    # Can only be used in private messages
    contexts={rum.InteractionContextType.private_channel},
    # Can only be used if the bot is installed to your user account,
    # if left blank it can only be used when added to guilds
    integration_types={rum.IntegrationType.user_install},
)
async def greet(ctx: rum.ApplicationContext, user: rum.User):
    await ctx.respond(f"Hello, {user}!")


@bot.slash_command(
    # This command can be used by guild members, but also by users anywhere if they install it
    integration_types={
        rum.IntegrationType.guild_install,
        rum.IntegrationType.user_install,
    },
)
async def say_hello(ctx: rum.ApplicationContext):
    await ctx.respond("Hello!")


# If a bot is not installed to a guild and the channel has the `USE_EXTERNAL_APPS`
# permission disabled, the response will always be ephemeral.


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
