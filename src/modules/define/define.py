import nextcord
import nextcord.ext
from nextcord.ext import commands
from wiktionaryparser import WiktionaryParser


class DefineCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="define",
        description="Search Wiktionary for the definition of a specified word. Supports any language on Wiktionary.",
    )
    async def define(
        self,
        interaction: nextcord.Interaction,
        keyword=nextcord.SlashOption(
            name="keyword", description="The word to define", required=True
        ),
        language=nextcord.SlashOption(
            name="language",
            description="The language for the word you'd like to define (Default: English)",
            required=False,
        ),
    ):
        if not language:
            language = "english"
        await DefinePager(language, keyword, interaction).update()

    @nextcord.slash_command(
        name="etym",
        description="Search Wiktionary for the etymology of a specified word. Supports any language on Wiktionary.",
    )
    async def etym(
        self,
        interaction: nextcord.Interaction,
        keyword=nextcord.SlashOption(
            name="keyword", description="The word to find an etymology for.", required=True
        ),
        language=nextcord.SlashOption(
            name="language",
            description="The language for the word you'd like to search (Default: English)",
            required=False,
        ),
    ):
        if not language:
            language = "english"
        await DefinePager(language, keyword, interaction, etym_only=True).update()


class DefinePager(nextcord.ui.View):
    interaction = None
    view_message = None
    keyword = None
    language = None
    define_data = None
    etym_only = False
    displayed_page = 0

    def __init__(self, language, keyword, interaction, etym_only=False):
        super().__init__(timeout=None)
        self.language = language
        self.keyword = keyword
        self.interaction = interaction
        self.etym_only = etym_only
        self.get_new_data()
        # Wiktionary terms are case sensitive, and users sometimes specify the wrong case.
        # We should check if the keyword we searched returned any data. if not, swap the case
        # of the first letter and search again.
        # (see Issue #7 on GitHub. thanks to laralove143)
        if self.is_data_empty():
            self.keyword = self.keyword[0].swapcase() + self.keyword[1:]
            self.get_new_data()

    def get_new_data(self):
        definitions = {}
        definer = WiktionaryParser()
        definer.set_default_language(self.language)
        fetch_data = definer.fetch(self.keyword)
        definitions["data"] = fetch_data
        definitions["language"] = self.language
        definitions["keyword"] = self.keyword
        self.define_data = definitions

    def is_data_empty(self):
        if not self.define_data:
            return True
        if len(self.define_data["data"]) == 0:
            return True
        if not (self.define_data["data"][0]["etymology"] or self.define_data["data"][0]["definitions"]):
            return True
        return False

    def browse_data(self, definitions, page_num=0):
        define_data = definitions["data"]
        page_count = len(define_data)
        language = definitions["language"]
        keyword = definitions["keyword"]
        # check if we have the requested page
        if page_count <= page_num:
            return {}
        data_page = define_data[page_num]
        # make sure page is not empty
        if len(data_page["definitions"]) == 0:
            return {}
        # trim etym text if it won't fit in discord's 1000 char limit.
        if len(data_page["etymology"]) > 999:
            data_page["etymology"] = data_page["etymology"][0:997] + "..."
        pronunciations_data = data_page["pronunciations"]["text"]
        pronunciations_text = ""
        # use only IPA pronunciations for now; otherwise this section gets lengthy
        for pronun in pronunciations_data:
            if "IPA" in pronun:
                pronunciations_text = pronunciations_text + pronun + ", "

        # generate and dress up definition URL
        url = "https://en.wiktionary.org/wiki/" + keyword
        url_title = keyword + " on Wiktionary"
        if language != "english":
            url = url + "#" + language.capitalize()
            url_title = url_title + " (" + language.capitalize() + ")"
        url = url.replace(" ", "%20")

        return_data = {}
        return_data["page_num"] = page_num
        return_data["num_results"] = len(define_data)
        return_data["etymology"] = data_page["etymology"]
        return_data["definitions"] = data_page["definitions"]
        return_data["pronunciations"] = pronunciations_text
        return_data["url"] = url
        return_data["url_title"] = url_title
        wiktionary_logo = "https://cdn.discordapp.com/attachments/933365248998658139/933889889219543080/unknown.png"
        return_data["url_logo"] = wiktionary_logo

        return return_data

    def etym_only_embed(self, embed_data):
        define_embed = nextcord.Embed(colour=nextcord.Colour.default())
        define_embed.set_author(
            name=embed_data["url_title"],
            url=embed_data["url"],
            icon_url=embed_data["url_logo"],
        )
        # if we have more than one etymology, the result should tell us which one we're looking at
        if embed_data["num_results"] > 1:
            field_title = "Etymology " + str(embed_data["page_num"] + 1)
        else:
            field_title = "Etymology"
        if len(embed_data["etymology"]) == 0:
            etym_text = "(This etymology is blank. You can improve it by clicking the link above.)"
        else:
            etym_text = embed_data["etymology"]
        define_embed.add_field(name=field_title, value=etym_text, inline=False)
        define_embed.set_footer(
            text="Page " + str(self.displayed_page + 1) + "/" + str(len(self.define_data["data"]))
        )
        return define_embed

    def define_embed(self, embed_data):
        # set etymology length limit (in characters) here. max: 1020
        ETYMOLOGY_LIMIT = 150
        # set definition length limit (in characters) here. max: 1020
        DEFINITION_LIMIT = 800
        define_embed = nextcord.Embed(colour=nextcord.Colour.default())
        define_embed.set_author(
            name=embed_data["url_title"],
            url=embed_data["url"],
            icon_url=embed_data["url_logo"],
        )

        # trim etymology if it's too long
        etymology = embed_data["etymology"]
        if len(etymology) > ETYMOLOGY_LIMIT:
            etymology = embed_data["etymology"][0:ETYMOLOGY_LIMIT] + "..."

        # combine etymology and pronunciation sections.
        field_text = ""
        if (len(etymology) != 0) and (len(embed_data["pronunciations"]) != 0):
            field_text = etymology + "\n" + embed_data["pronunciations"]
        elif len(etymology) != 0:
            field_text = etymology
        elif len(embed_data["pronunciations"]) != 0:
            field_text = embed_data["pronunciations"]

        # if field_text isn't empty, add it to the embed.
        if len(field_text) > 0:
            # if we have more than one etymology, the result should tell us which one we're looking at
            if embed_data["num_results"] > 1:
                field_title = "Etymology " + str(embed_data["page_num"] + 1)
            else:
                field_title = "Etymology"
            define_embed.add_field(name=field_title, value=field_text, inline=False)

        # add a new section for each part of speech and populate it with definition text.
        for definition_part in embed_data["definitions"]:
            part_of_speech = definition_part["partOfSpeech"]
            definition_count = 1
            definition_text = ""
            # skip the first entry, it's not actual definitions
            for definition in definition_part["text"][1:]:
                definition_text += str(definition_count) + ". "
                definition_text += definition + "\n"
                definition_count += 1
            # trim definition_text if it's too long; Discord limit is 1024 chars.
            # we're gonna stick to 800, 1000 is a little long.
            if len(definition_text) > DEFINITION_LIMIT:
                definition_text = definition_text[0:DEFINITION_LIMIT] + "..."
            define_embed.add_field(name=part_of_speech, value=definition_text, inline=True)

        define_embed.set_footer(
            text="Page " + str(self.displayed_page + 1) + "/" + str(len(self.define_data["data"]))
        )

        return define_embed

    @nextcord.ui.button(label="Prev Page", style=nextcord.ButtonStyle.blurple)
    async def prev(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.displayed_page > 0:
            self.displayed_page -= 1
        await self.update()

    @nextcord.ui.button(label="Next Page", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.displayed_page < (len(self.define_data["data"]) - 1):
            self.displayed_page += 1
        await self.update()

    async def update(self):
        if not self.interaction:
            return
        if self.is_data_empty():
            await self.interaction.send(content="Sorry boss, I got nothin'.", ephemeral=True)
            return
        # if we don't have more than one page of results, remove buttons
        if len(self.define_data["data"]) < 2:
            self.clear_items()
        if self.etym_only:
            gen_embed = self.etym_only_embed(
                self.browse_data(self.define_data, self.displayed_page)
            )
        else:
            gen_embed = self.define_embed(
                self.browse_data(self.define_data, self.displayed_page)
            )
        if not self.view_message:
            await self.interaction.send(view=self, embed=gen_embed)
            self.view_message = await self.interaction.original_message()
        else:
            await self.view_message.edit(view=self, embed=gen_embed)


def setup(bot):
    bot.add_cog(DefineCog(bot))
