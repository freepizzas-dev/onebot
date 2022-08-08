import nextcord
from nextcord.ext import commands


class JokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="joke", description="Tells you a random dad joke.")
    async def joke(
        self,
        interaction: nextcord.Interaction,
        search_term=nextcord.SlashOption(
            name="search_term",
            description="Type your search here, or leave it blank for a random joke.",
            required=False,
        ),
    ):
        random_joke = False
        if not search_term:
            random_joke = True
        headers = {"Accept": "text/plain"}
        if random_joke:
            async with self.bot.aiohttp_session.get(
                "https://icanhazdadjoke.com/", headers=headers
            ) as resp:
                if resp.status != 200:
                    await interaction.send(
                        "Sorry boss, all out of jokes for now. (Server responded with HTTP code "
                        + str(resp.status)
                        + ")",
                        ephemeral=True,
                    )
                    self.bot.logger.error(
                        "JOKE | icanhazdadjoke responded with code " + str(resp.status)
                    )
                    return
                joke = await resp.text(encoding="utf-8")
        else:
            params = {"term": str(search_term), "limit": 1}
            async with self.bot.aiohttp_session.get(
                "https://icanhazdadjoke.com/search", headers=headers, params=params
            ) as resp:
                if resp.status != 200:
                    await interaction.send(
                        "Sorry boss, all out of jokes for now. (Server responded with HTTP code "
                        + str(resp.status)
                        + ")",
                        ephemeral=True,
                    )
                    self.bot.logger.error(
                        "JOKE | icanhazdadjoke responded with code " + str(resp.status)
                    )
                    return
                joke = await resp.text(encoding="utf-8")
        if not random_joke and len(joke) == 0:
            await interaction.send("No jokes found for `" + search_term + "`.", ephemeral=True)
            return
        embed_title = "A random joke:"
        if not random_joke:
            embed_title = 'A "' + search_term + '" joke:'
        embed = nextcord.Embed(title=embed_title, description=joke)
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(JokeCog(bot))
