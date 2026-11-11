# Set the BOT_TOKEN environment variable before running this example:
#     BOT_TOKEN=your-token uv run examples/edits.py
import asyncio
import os

import rum

intents = rum.Intents.default()
intents.message_content = (
    True  # < This may give you `read-only` warning, just ignore it.
)
# This intent requires "Message Content Intent" to be enabled at https://discord.com/developers


bot = rum.Bot(intents=intents)


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_message(message: rum.Message):
    if message.content.startswith("!editme"):
        msg = await message.channel.send("10")
        await asyncio.sleep(3.0)
        await msg.edit(content="40")


@bot.event
async def on_message_edit(before: rum.Message, after: rum.Message):
    msg = (
        f"**{before.author}** edited their message:\n{before.content} ->"
        f" {after.content}"
    )
    await before.channel.send(msg)


bot.run(os.environ["BOT_TOKEN"])
