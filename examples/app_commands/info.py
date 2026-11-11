# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# info.py
# This example requires the 'members' privileged intent to use the Member converter.

import os
import rum

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(
    # debug_guilds=[123456789012345678],  # only sync commands in these guilds
    description="An example to showcase how to extract info about users.",
    intents=intents,
)


@bot.slash_command(name="userinfo", description="Gets info about a user.")
async def info(ctx: rum.ApplicationContext, user: rum.Member = None):
    user = (
        user or ctx.author
    )  # If no user is provided it'll use the author of the message
    embed = rum.Embed(
        fields=[
            rum.EmbedField(name="ID", value=str(user.id), inline=False),  # User ID
            rum.EmbedField(
                name="Created",
                value=rum.utils.format_dt(user.created_at, "F"),
                inline=False,
            ),  # When the user's account was created
        ],
    )
    embed.set_author(name=user.name)
    embed.set_thumbnail(url=user.display_avatar.url)

    if user.colour.value:  # If user has a role with a color
        embed.colour = user.colour

    if isinstance(user, rum.User):  # Checks if the user in the server
        embed.set_footer(text="This user is not in this server.")
    else:  # We end up here if the user is a rum.Member object
        embed.add_field(
            name="Joined",
            value=rum.utils.format_dt(user.joined_at, "F"),
            inline=False,
        )  # When the user joined the server

    await ctx.respond(embeds=[embed])  # Sends the embed


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
