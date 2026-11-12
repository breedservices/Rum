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
# cooldown.py
# This example requires the `message_content` privileged intent for prefixed commands.

import os
import rum
from rum.ext import commands

intents = rum.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), debug_guilds=[1548399850905665648], intents=intents
)
bypassing_users = []  # used in the dynamic cooldown below


# An application command with cooldown
@bot.slash_command()
@commands.cooldown(
    1, 5, commands.BucketType.user
)  # The command can only be used once in 5 seconds
async def slash(ctx: rum.ApplicationContext):
    await ctx.respond("You can use this command again in 5 seconds.")


# Application command error handler
@bot.event
async def on_application_command_error(
    ctx: rum.ApplicationContext, error: rum.DiscordException
):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown.")
    else:
        raise error  # Raise other errors so they aren't ignored


# A prefixed command with cooldown
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def prefixed(ctx: commands.Context):
    await ctx.send("You can use this command again in 5 seconds.")


# Dynamic cooldown function; allows for custom cooldown logic such as different cooldowns per-user
def my_cooldown(message):
    if message.author.id in bypassing_users:
        return None  # Let specific users bypass the cooldown entirely
    elif message.author.get_role(929080208148017242):
        return commands.Cooldown(
            2, 5
        )  # Users with the above role ID can use the command twice in 5 seconds
    else:
        return commands.Cooldown(
            1, 10
        )  # All other users can use the command once in 10 seconds


# A prefixed command with the dynamic cooldown defined above
@bot.command()
@commands.dynamic_cooldown(my_cooldown, commands.BucketType.user)
async def dynamic(ctx: commands.Context):
    await ctx.send("You can use this command again soon.")


# Prefixed command error handler
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is currently on cooldown.")
    else:
        raise error


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
