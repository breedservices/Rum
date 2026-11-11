# Set the BOT_TOKEN environment variable before running this example:
#     BOT_TOKEN=your-token uv run examples/new_member.py
import os
import rum

intents = rum.Intents.default()
intents.members = True  # This intent requires "Server Member Intent" to be enabled at https://discord.com/developers
# ^ This may give you `read-only` warning, just ignore it.

bot = rum.Bot(intents=intents)


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_member_join(member: rum.Member):
    guild = member.guild
    if (
        guild.system_channel is not None
    ):  # For this to work, System Messages Channel should be set in guild settings.
        await guild.system_channel.send(f"Welcome {member.mention} to {guild.name}!")


bot.run(os.environ["BOT_TOKEN"])
