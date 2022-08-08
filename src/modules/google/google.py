import nextcord
from nextcord.ext import commands
from googlesearch import search


class GoogleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="google",
        description='Shows you the first Google result ("I\'m Feeling Lucky!") for a given search term.',
    )
    async def google(self, interaction: nextcord.Interaction, search_term):
        results = search(search_term, tld="com", num=1, stop=1, safe="active")
        try:
            link = results.__next__()
            await interaction.send(link)
        except StopIteration:
            await interaction.send(
                "No Google Search results for `" + search_term + "`.", ephemeral=True
            )


def setup(bot):
    bot.add_cog(GoogleCog(bot))
