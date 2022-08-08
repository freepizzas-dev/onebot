import nextcord
from nextcord.ext import commands
from astral import moon


class MoonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="moon", description="Tells you if the moon is currently waxing or waning."
    )
    async def moon(self, interaction: nextcord.Interaction):
        if moon.phase() < 14:
            await interaction.send("moon is **waxing**")
        else:
            await interaction.send("moon is **waning**")


def setup(bot):
    bot.add_cog(MoonCog(bot))
