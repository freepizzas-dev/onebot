import nextcord
from nextcord.ext import commands
from modules.image.google_images_download import googleimagesdownload


class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="image", description="Search Google Images for an image using the specified keyword."
    )
    async def image(
        self,
        interaction: nextcord.Interaction,
        filter_keyword=nextcord.SlashOption(
            name="filter_keyword", description="Type your search here.", required=False
        ),
    ):
        if not filter_keyword:
            filter_keyword = await self.bot.utils.get_random_word(self.bot)
        filter_keyword = '"' + filter_keyword + '"'
        # search google with image with keyword
        # get 20 results, filter through blacklist, then pick a random one
        # this library is kinda buggy. sometimes it throws unpredictable exceptions.
        # i kind of want to write my own scraper for this.
        try:
            arguments = {
                "keywords": filter_keyword,
                "limit": 100,
                "safe_search": True,
                "no_download": True,
                "silent_mode": True,
            }
            response = googleimagesdownload()
            url_list = response.download(arguments)
        except:
            url_list = []
            pass

        # filter out blacklist phrases from URLs
        filtered_list = []
        for image in url_list:
            if not any(i in image for i in self.bot.config.ONEBOT_IMGBL):
                filtered_list.append(image)

        if len(filtered_list) == 0:
            await interaction.send("No image results for `" + filter_keyword + "`.", ephemeral=True)
            return

        view = ImagePager(interaction, filtered_list)
        await view.update()


class ImagePager(nextcord.ui.View):
    interaction = None
    view_message = None
    image_list = None
    displayed_page = 0
    btn_current_page = None
    command_user = None

    def __init__(self, interaction, image_list):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.command_user = interaction.user
        self.image_list = image_list

    @nextcord.ui.button(label="Prev Image", style=nextcord.ButtonStyle.blurple)
    async def prev(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.command_user:
            return
        if self.displayed_page > 0:
            self.displayed_page -= 1
        await self.update()

    @nextcord.ui.button(label="1 of #", style=nextcord.ButtonStyle.secondary)
    async def current_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label="Next Image", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.command_user:
            return
        if self.displayed_page < (len(self.image_list) - 1):
            self.displayed_page += 1
        await self.update()

    async def update(self):
        if not self.interaction:
            return
        # update middle button with current page number
        self.children[1].label = str(self.displayed_page + 1) + " of " + str(len(self.image_list))
        self.children[1].disabled = True
        # if we don't have more than one page of results, remove buttons
        if len(self.image_list) == 1:
            self.clear_items()
        image_url = self.image_list[self.displayed_page]
        if not self.view_message:
            await self.interaction.send(view=self, content=image_url)
            self.view_message = await self.interaction.original_message()
        else:
            await self.view_message.edit(view=self, content=image_url)


def setup(bot):
    bot.add_cog(ImageCog(bot))
