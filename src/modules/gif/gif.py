import random
import os
import json
import nextcord
from nextcord.ext import commands

class GifCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TENOR_TOKEN = os.environ.get("TENOR_TOKEN")

    @nextcord.slash_command(
        name="gif",
        description="Post a random GIF. Optionally, use a keyword to filter the results.",
    )
    async def gif(
        self,
        interaction: nextcord.Interaction,
        filter_keyword=nextcord.SlashOption(
            name="filter_keyword", description="Filter the GIFs using this keyword", required=False
        ),
    ):
        random_gif = False
        if not filter_keyword:
            filter_keyword = await self.bot.utils.get_random_word(self.bot)
            random_gif = True
        attempts = 0
        results = []
        while attempts < 25:
            params = {"key": self.TENOR_TOKEN, "q": filter_keyword, "limit": 50}
            endpoint = "https://g.tenor.com/v1/random"
            async with self.bot.aiohttp_session.get(endpoint, params=params) as resp:
                if resp.status == 429:
                    await interaction.send(
                        "Tenor says: rate limit exceeded! (Server sent response code 429)",
                        ephemeral=True,
                    )
                    self.bot.logger.error("GIF | Received response code 429 from Tenor")
                    return
                elif resp.status != 200:
                    await interaction.send(
                        "Sorry, something went wrong on Tenor's end. (Server sent response code "
                        + str(resp.status)
                        + ")",
                        ephemeral=True,
                    )
                    self.bot.logger.error(
                        "GIF | Received response code " + str(resp.status) + " from Tenor"
                    )
                    return
                results = json.loads(await resp.read())

            #if we got a valid answer, send it.
            if results["results"]:
                # if there's only one result, set index to 0 or random.randint throws an exception
                if len(results["results"]) == 1:
                    gif_index = 0
                else:
                    gif_index = random.randint(0, len(results["results"]) - 1)
                await interaction.send(results["results"][gif_index]["url"])
                return

            # if we didn't get a valid answer...
            # if the user specified a keyword, we shouldn't try again in the case of 0 results.
            if not random_gif:
                await interaction.send(
                    "No GIF results for `" + filter_keyword + "`.", ephemeral=True
                )
                return
            # otherwise, increment attempts by 1 and generate a fresh random keyword.
            else:
                attempts += 1
                filter_keyword = await self.bot.utils.get_random_word(self.bot)
            if attempts == 25:
                await interaction.send("Sorry, something went wrong on Tenor's end.", ephemeral=True)
                self.bot.logger.error("GIF | Attempted and failed to retrieve a gif 25 times.")


def setup(bot):
    if "TENOR_TOKEN" not in os.environ:
        bot.logger.error("GIF | Missing TENOR_TOKEN in your .env file! Gif module not loaded.")
        bot.logger.error("GIF | You need a token to use Tenor's GIF API. https://tenor.com/gifapi/documentation")
    else:
        bot.add_cog(GifCog(bot))
