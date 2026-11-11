# Set the BOT_TOKEN environment variable before running this example:
#     BOT_TOKEN=your-token uv run examples/create_private_emoji.py
import os
import rum

bot = rum.Bot()

allowed_content_types = [
    "image/jpeg",
    "image/png",
]  # Setting up allowed attachments types


# Discord doesn't support creating private emojis by default, its semi-implemented feature and can be done by bots only.


# This command is publicly available, to set up command permissions look for other examples in repo
@bot.command(guild_ids=[...])
async def add_private_emoji(
    ctx,
    name: rum.Option(str),
    image: rum.Option(rum.Attachment),
    role: rum.Option(rum.Role),
):
    if image.content_type not in allowed_content_types:
        return await ctx.respond("Invalid attachment type!", ephemeral=True)

    image_file = await image.read()  # Reading attachment's content to get bytes

    await ctx.guild.create_custom_emoji(
        name=name, image=image_file, roles=[role]
    )  # Image argument only takes bytes!
    await ctx.respond(content="Private emoji is successfully created!")


bot.run(os.environ["BOT_TOKEN"])
