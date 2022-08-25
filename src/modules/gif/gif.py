import random
import os
import json
import nextcord
from nextcord.ext import commands


class GifCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TENOR_TOKEN = os.environ.get("TENOR_TOKEN")

    async def get_gif_links(self, keyword):
        params = {"key": self.TENOR_TOKEN, "q": keyword, "limit": 50}
        endpoint = "https://g.tenor.com/v1/search"
        async with self.bot.aiohttp_session.get(endpoint, params=params) as resp:
            if resp.status != 200:
                self.bot.logger.error("GIF | Received response code " + str(resp.status) + " from Tenor")
                return "error"
            results = json.loads(await resp.read())
            return results

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
        results = []
        if not filter_keyword:  # select a random gif if no keyword specified
            attempts = 0
            while attempts < 25:
                random_word = await self.bot.utils.get_random_word(self.bot)
                if random_word == '':
                    await interaction.send("Sorry, I couldn't choose a random GIF.", ephemeral=True)
                    return
                results = await self.get_gif_links(random_word)
                if results != "error":
                    if results["results"]:
                        break
                attempts += 1
                if attempts == 25:
                    await interaction.send("Failed to get a gif too many times. Try again later.", ephemeral=True)
                    self.bot.logger.error("GIF | Attempted and failed to retrieve a gif 25 times.")
        else:  # otherwise, look up the keyword once and return results
            results = await self.get_gif_links(filter_keyword)
        if not results["results"]:
            await interaction.send("Sorry, no results for that GIF search.", ephemeral=True)

        view = GifPager(interaction, results["results"])
        await view.update()


class GifPager(nextcord.ui.View):
    interaction = None
    view_message = None
    gif_list = None
    displayed_page = 0
    btn_current_page = None
    command_user = None

    def __init__(self, interaction, gif_list):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.command_user = interaction.user
        self.gif_list = gif_list

    @nextcord.ui.button(label="Prev GIF", style=nextcord.ButtonStyle.blurple)
    async def prev(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user == self.command_user:
            if self.displayed_page > 0:
                self.displayed_page -= 1
            await self.update()

    @nextcord.ui.button(label="1 of #", style=nextcord.ButtonStyle.secondary)
    async def current_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label="Next GIF", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user == self.command_user:
            if self.displayed_page < (len(self.gif_list) - 1):
                self.displayed_page += 1
            await self.update()

    @nextcord.ui.button(label="❌", style=nextcord.ButtonStyle.danger)
    async def hide_buttons(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user == self.command_user:
            self.clear_items()
            await self.update()

    async def update(self):
        if not self.interaction:
            return
        # update middle button with current page number
        if self.children:
            self.children[1].label = str(self.displayed_page + 1) + " of " + str(len(self.gif_list))
            self.children[1].disabled = True
        # if we don't have more than one page of results, remove buttons
        if len(self.gif_list) == 1:
            self.clear_items()
        gif_url = self.gif_list[self.displayed_page]["url"]
        if not self.view_message:
            await self.interaction.send(view=self, content=gif_url)
            self.view_message = await self.interaction.original_message()
        else:
            await self.view_message.edit(view=self, content=gif_url)


def setup(bot):
    if "TENOR_TOKEN" not in os.environ:
        bot.logger.error("GIF | Missing TENOR_TOKEN in your .env file! Gif module not loaded.")
        bot.logger.error("GIF | You need a token to use Tenor's GIF API. https://tenor.com/gifapi/documentation")
    else:
        bot.add_cog(GifCog(bot))
