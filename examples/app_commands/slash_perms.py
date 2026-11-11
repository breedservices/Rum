# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# slash_perms.py
import os
import rum

bot = rum.Bot()


@bot.slash_command()
@rum.default_permissions(
    administrator=True,
)  # Only members with this permission can use this command.
async def admin_only(ctx: rum.ApplicationContext):
    await ctx.respond(f"Hello {ctx.author}, you are an administrator.")


@bot.slash_command()
@rum.default_permissions(
    manage_messages=True,
    ban_members=True,
)  # You can supply multiple permissions that are required to use the command.
async def staff_only(ctx: rum.ApplicationContext):
    await ctx.respond(f"Hello {ctx.author}, you can manage messages and ban members.")


"""
Server owners and administrators have all permissions and can change required permissions per-server.
If the member viewing commands does not have the required permissions, the commands will show up disabled.
"""


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
