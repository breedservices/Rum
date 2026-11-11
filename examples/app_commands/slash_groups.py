# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# slash_groups.py
import os
import rum

bot = rum.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with rum.Bot as well.

# Create a slash command group:
math = bot.create_group("math", "Commands related to mathematics.")

# The group can also be created manually, but only one of the two ways may
# be used, otherwise the command name would be registered twice:
# math = rum.SlashCommandGroup("math", "Commands related to mathematics.")


@math.command()  # Create a slash command under the math group
async def add(ctx: rum.ApplicationContext, num1: int, num2: int):
    """Get the sum of 2 integers."""
    await ctx.respond(f"The sum of these numbers is **{num1+num2}**")


bot.add_application_command(math)
bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
