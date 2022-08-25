import os
import json
import nextcord
from nextcord.ext import commands
from bs4 import BeautifulSoup


class UrbandictionaryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.XRAPIDKEY = os.environ.get("XRAPIDKEY")

    @nextcord.slash_command(
        name="ud",
        description="Retrieves a definition from Urban Dictionary. Use without a keyword to get the Word of the Day.",
    )
    async def urbandictionary(
        self,
        interaction: nextcord.Interaction,
        keyword=nextcord.SlashOption(
            name="keyword",
            description="Type your search here. For WOTD, do not use this option.",
            required=False,
        ),
    ):
        if not interaction.channel.is_nsfw():
            await interaction.send("This command is only available in NSFW channels.", ephemeral=True)
            return
        wotd = False
        if not keyword:
            async with self.bot.aiohttp_session.get("https://urbandictionary.com") as resp:
                if resp.status != 200:
                    await interaction.send(
                        "Sorry, something went wrong while contacting Urban Dictionary.",
                        ephemeral=True,
                    )
                    self.bot.logger.error(
                        "URBANDICTIONARY | Received response code "
                        + str(resp.status)
                        + " from urbandictionary.com"
                    )
                    return
                ud_homepage = await resp.read()
                parsed_ud = BeautifulSoup(ud_homepage, "html.parser")
                keyword = parsed_ud.find("a", class_="word").get_text()
                wotd = True

        # set up xrapidapi httprequest
        endpoint = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        rapidhost = "mashape-community-urban-dictionary.p.rapidapi.com"
        headers = {
            "x-rapidapi-key": self.XRAPIDKEY,
            "x-rapidapi-host": rapidhost,
            "useQueryString": "true",
        }
        params = {"term": keyword}
        async with self.bot.aiohttp_session.get(endpoint, headers=headers, params=params) as resp:
            if resp.status != 200:
                await interaction.send(
                    "Sorry, something went wrong while contacting Urban Dictionary.", ephemeral=True
                )
                self.bot.logger.error(
                    "URBANDICTIONARY | Received response code " + str(resp.status) + "from rapidAPI"
                )
                return
            ud_data = json.loads(await resp.read())["list"]

        if len(ud_data) < 1:
            await interaction.send("Sorry boss, I got nothin'.", ephemeral=True)
            return

        embed_text = ud_data[0]["definition"]
        if len(embed_text) > 999:
            embed_text = embed_text[0:996] + "..."
        embed_title = keyword + " on Urban Dictionary"
        if wotd:
            embed_title = embed_title + " (Word of the Day)"
        embed_link = ud_data[0]["permalink"]
        embed_footer = str(ud_data[0]["thumbs_up"]) + "👍 " + str(ud_data[0]["thumbs_down"]) + "👎"
        embed_logo = "https://cdn.discordapp.com/attachments/910743765138939905/953730141308190750/keusf8I1.png"
        embed_author = ud_data[0]["author"]
        embed = nextcord.Embed(colour=nextcord.Colour.default())
        embed.set_author(name=embed_title, url=embed_link, icon_url=embed_logo)
        embed.add_field(name="Definition by " + embed_author, value=embed_text, inline=False)
        embed.set_footer(text=embed_footer)
        await interaction.send(embed=embed)


def setup(bot):
    if "XRAPIDKEY" not in os.environ:
        bot.logger.error("URBANDICTIONARY | Missing XRAPIDKEY in your .env file! Urbandictionary module not loaded.")
        bot.logger.error("URBANDICTIONARY | You need an XRapidApi key to use the urbandictionary endpoint."
                         " https://docs.rapidapi.com/docs/keys")
    else:
        bot.add_cog(UrbandictionaryCog(bot))
