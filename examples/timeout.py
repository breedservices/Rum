# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# timeout.py
import datetime
import os

import rum

bot = rum.Bot()


@bot.slash_command()
async def timeout(
    ctx: rum.ApplicationContext, member: rum.Member, minutes: int
):
    """Apply a timeout to a member."""

    duration = datetime.timedelta(minutes=minutes)
    await member.timeout_for(duration)
    await ctx.respond(f"Member timed out for {minutes} minutes.")

    """
    The method used above is a shortcut for:

    until = rum.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until)
    """


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
