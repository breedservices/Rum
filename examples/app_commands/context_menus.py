# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# context_menus.py
# This example requires the 'members' privileged intent to use the Member converter.

import os
import rum

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(intents=intents)
# Remove debug_guilds and set guild_ids in the slash command decorators
# to restrict specific commands to the supplied guild IDs.


@bot.user_command()  # Create a global user command
async def mention(
    ctx: rum.ApplicationContext, member: rum.Member
):  # User commands give a member param
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")


# User commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # Creates a global message command
async def show_id(
    ctx: rum.ApplicationContext, message: rum.Message
):  # Message commands give a message param
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
