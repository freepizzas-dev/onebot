import nextcord
from nextcord.ext import commands
import googlesearch


class GoogleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="google",
        description='Shows you the first Google result ("I\'m Feeling Lucky!") for a given search term.',
    )
    async def google(self, interaction: nextcord.Interaction, search_term):
        results = googlesearch.search(search_term, num_results=1)
        try:
            link = results.__next__()
            await interaction.send(link)
        except StopIteration:
            await interaction.send(
                "No Google Search results for `" + search_term + "`.", ephemeral=True
            )


def setup(bot):
    bot.add_cog(GoogleCog(bot))
