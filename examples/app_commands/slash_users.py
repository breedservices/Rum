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


bot.run("TOKEN")
