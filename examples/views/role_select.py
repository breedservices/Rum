import rum

# Role selects (dropdowns) are a new type of select menu/dropdown Discord has added so people can select server roles from a dropdown.


# Defines a simple View that allows the user to use the Select menu.
# In this view, we define the role_select with `rum.ui.role_select`
# Using the decorator automatically sets `select_type` to `rum.ComponentType.role_select`.
class DropdownView(rum.ui.View):
    @rum.ui.role_select(
        placeholder="Select roles...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 roles in the dropdown
    async def role_select_dropdown(
        self, select: rum.ui.RoleSelect, interaction: rum.Interaction
    ) -> None:
        # update the select default values to set them to the select ones
        select.default_values = select.values  # this is a list of Role
        await interaction.response.send_message(
            "You selected the following roles:"
            + ", ".join(f"{role.mention}" for role in select.values),
            view=self,
        )


bot: rum.Bot = rum.Bot()


@bot.slash_command()
async def role_select(ctx: rum.ApplicationContext) -> None:
    """Sends a message with our dropdown that contains a role select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select roles:", view=view)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
