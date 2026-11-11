# Set the BOT_TOKEN environment variable before running this example:
#     BOT_TOKEN=your-token uv run examples/slash_options.py
import os
import rum
from rum import option

bot = rum.Bot()


# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with rum.Bot as well.


@bot.slash_command()
@option("name", description="Enter your name")
@option(
    "pokemon",
    description="Choose your starter Pokémon",
    choices=["Bulbasaur", "Squirtle", "Charmander", "Pikachu"],
)
@option(
    "age",
    description="Enter your age",
    min_value=1,
    max_value=99,
    default=18,
    # Passing the default value makes an argument optional.
    # You also can create optional arguments using:
    # age: Option(int, "Enter your age") = 18
)
async def hello(
    ctx: rum.ApplicationContext,
    name: str,
    pokemon: str,
    age: int,
):
    await ctx.respond(
        f"Hello {name}! Your starter Pokémon is {pokemon} and you are {age} years old."
    )


@bot.slash_command(name="channel")
@option(
    "channel",
    rum.TextChannel | rum.VoiceChannel,
    # You can specify allowed channel types by passing a union of them like this.
    description="Select a channel",
)
async def select_channel(
    ctx: rum.ApplicationContext,
    channel: rum.TextChannel | rum.VoiceChannel,
):
    await ctx.respond(f"Hi! You selected {channel.mention} channel.")


@bot.slash_command(name="attach_file")
@option(
    "attachment",
    rum.Attachment,
    description="A file to attach to the message",
    required=False,  # The default value will be None if the user doesn't provide a file.
)
async def say(
    ctx: rum.ApplicationContext,
    attachment: rum.Attachment,
):
    """This demonstrates how to attach a file with a slash command."""
    if attachment:
        file = await attachment.to_file()
        await ctx.respond("Here's your file!", file=file)
    else:
        await ctx.respond("You didn't give me a file to reply with! :sob:")


bot.run(os.environ["BOT_TOKEN"])
