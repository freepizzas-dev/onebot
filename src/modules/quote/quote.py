from datetime import datetime
import random
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # creates the quote table in the server DB if it does not exist.
    def prep_db(self, server_id):
        db = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db.cursor()
        db_query = """CREATE TABLE IF NOT EXISTS "quotes" (
                "id"	INTEGER NOT NULL,
                "author"	TEXT,
                "content"	TEXT,
                "timestamp"	INTEGER,
                "display_count"	INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY("id" AUTOINCREMENT)
            );"""
        db_cursor.execute(db_query)
        db_query = """CREATE TABLE IF NOT EXISTS "quotes_display_timestamps" (
                "quote_id"	INTEGER NOT NULL,
                "timestamp"	INTEGER NOT NULL
            );"""
        db_cursor.execute(db_query)
        db_cursor.close()
        db.commit()
        db.close()

    # add quote to database. accepts two string parameters. returns newly added quote_data.
    def add_quote(self, author, quote, server_id):
        timestamp = datetime.now().timestamp()
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (
            author,
            quote,
            timestamp,
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO quotes (author, content, timestamp) VALUES (?, ?, ?)", db_param
        )
        db_cursor.execute("SELECT * FROM quotes WHERE id = ?", (db_cursor.lastrowid,))
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.commit()
        db_connection.close()
        return db_result

    # remove quote from database. checks for permissions (members_preferences table, can_delete_quote field)
    # accepts Member object for remove requestor, and int for quote_id
    # returns True on success, False on fail
    def remove_quote(self, requestor, quote_id, server_id):
        if requestor.guild_permissions.manage_guild:
            db = self.bot.db_utils.get_db_connection(server_id)
            db_cursor = db.cursor()
            db_param = (quote_id,)
            db_cursor.execute("SELECT * FROM quotes WHERE id = ?", db_param)
            db_result = db_cursor.fetchone()
            if not db_result:
                db_cursor.close()
                db.close()
                return False
            db_cursor.execute("DELETE FROM quotes WHERE id = ?", db_param)
            db_cursor.close()
            db.commit()
            db.close()
            return True
        else:
            return False

    # get any random quote.
    def get_random_quote(self, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1")
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        if not db_result:
            return None
        else:
            return db_result

    # get quote by id. return None if no quote found. accepts int parameter.
    def get_quote_by_id(self, quote_id, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (quote_id,)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM quotes WHERE id = ?", db_param)
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        return db_result

    # get quote by keyword. return random if more than one result or None if no quote found. accepts String parameter.
    def get_quote_by_keyword(self, keyword, server_id):
        keyword = "%" + keyword + "%"
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (
            keyword,
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM quotes WHERE content LIKE ? ORDER BY RANDOM() LIMIT 1",
            db_param,
        )
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        return db_result

    # get quote by author. same as above but checks Author field
    def get_quote_by_author(self, author, server_id):
        author = "%" + author + "%"
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (
            author,
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM quotes WHERE author LIKE ? ORDER BY RANDOM() LIMIT 1",
            db_param,
        )
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        return db_result

    # get quote by filtering by BOTH keyword and author
    def get_quote_by_keyword_and_author(self, keyword, author, server_id):
        keyword = "%" + keyword + "%"
        author = "%" + author + "%"
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (
            keyword,
            author,
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM quotes WHERE content LIKE ? AND author LIKE ? ORDER BY RANDOM() LIMIT 1",
            db_param,
        )
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        return db_result

    # get a 'recent' quote - within the last [limit] quotes. optional int parameter.
    # first, retrieves a list of the 100 most recent IDs (to skip deleted ones)
    # then, retrieves a random quote from that list.
    def get_quote_recent(self, server_id, limit=100):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (limit,)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM quotes ORDER BY id DESC LIMIT ?", db_param)
        selected_id = (random.choice(db_cursor.fetchall())["id"],)
        db_cursor.execute("SELECT * FROM quotes WHERE id = ?", selected_id)
        db_result = db_cursor.fetchone()
        db_cursor.close()
        db_connection.close()
        return db_result

    def get_top_10_quotes(self, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM quotes ORDER BY display_count DESC LIMIT 10")
        db_result = db_cursor.fetchall()
        return db_result

    def get_bottom_10_quotes(self, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM quotes ORDER BY display_count ASC LIMIT 10")
        db_result = db_cursor.fetchall()
        return db_result

    # get number of times quote was displayed. days specifies 'within last x days', 0 = no limit.
    def get_quote_stats_by_id(self, quote_id, server_id, days=0):
        current_time = datetime.now().timestamp()
        if days == 0:
            limit_time = 0
        else:
            limit_time = current_time - (86400 * days)
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_param = (
            int(quote_id),
            limit_time,
        )
        db_cursor.execute(
            "SELECT COUNT(*) FROM quotes_display_timestamps WHERE quote_id = ? AND timestamp > ?",
            db_param,
        )
        db_result = db_cursor.fetchall()
        display_count = db_result[0]["COUNT(*)"]
        return display_count

    # return a quote's display ranking
    def get_quote_rank_by_id(self, quote_id, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT id FROM quotes ORDER BY display_count DESC")
        ranking = 0
        db_result_quoteid = -1
        while int(db_result_quoteid) != int(quote_id):
            ranking += 1
            db_result_quote = db_cursor.fetchone()
            if not db_result_quote:
                ranking = -1
                break
            db_result_quoteid = db_result_quote["id"]
        db_cursor.close()
        db_connection.close()
        return ranking

    # increment_display_count also records a quote_display_timestamp for interesting statistics.
    def increment_display_count(self, quote_id, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_param = (quote_id, )
        db_cursor = db_connection.cursor()
        db_cursor.execute("UPDATE quotes SET display_count = display_count + 1 WHERE id = ?", db_param)
        timestamp = datetime.now().timestamp()
        db_param = (quote_id, timestamp, )
        db_cursor.execute("INSERT INTO quotes_display_timestamps (quote_id, timestamp) VALUES (?, ?)", db_param)
        db_cursor.close()
        db_connection.commit()
        db_connection.close()
        return

    # generate a nextcord Embed object using the specified quote data.
    def generate_quote_embed(self, quote_data):
        quote_id = "#" + str(quote_data["id"])
        quote_footer = []
        quote_author = quote_data["author"]
        if quote_author:
            quote_footer.append(quote_author)
        quote_content = quote_data["content"]
        quote_timestamp = quote_data["timestamp"]
        quote_time = None
        if quote_timestamp:
            quote_time = datetime.utcfromtimestamp(quote_timestamp).strftime("%b %d, %Y")
        if quote_time:
            quote_footer.append(quote_time)
        # check if quote is tagged as image and contains url
        if quote_content[0:6] == "image:":
            split_content = quote_content.split(" ", 1)
            url = str(split_content[0][6:])
            quote_tags = ""
            if len(split_content) > 1:
                quote_tags = split_content[1]
            quote_embed = nextcord.Embed(
                title=quote_id + ":", colour=nextcord.Colour.default(), description=quote_tags
            )
            quote_embed.set_image(url=url)
        else:
            quote_embed = nextcord.Embed(
                title=quote_id + ":", colour=nextcord.Colour.default(), description=quote_content
            )

        # set up the footer. depending on what data is available, the format differs.
        footer_text = ""
        for item in quote_footer:
            footer_text = footer_text + str(item)
            footer_text = footer_text + " | "
        footer_text = footer_text[0:-2]  # remove trailing separator
        quote_embed.set_footer(text=footer_text)
        return quote_embed

    # return the timestamp when the specified quote appeared last.
    def get_quote_last_appearance(self, quote_id, server_id):
        db_connection = self.bot.db_utils.get_db_connection(server_id)
        db_cursor = db_connection.cursor()
        db_param = (quote_id,)
        db_cursor.execute(
            "SELECT timestamp FROM quotes_display_timestamps WHERE quote_id = ? ORDER BY timestamp DESC LIMIT 1",
            db_param,
        )
        db_result = db_cursor.fetchall()[0]["timestamp"]
        quote_time = datetime.utcfromtimestamp(db_result).strftime("%b %d, %Y")
        return quote_time

    @nextcord.slash_command(
        name="quote", description="Retrieves one of the quotes you've added to the database."
    )
    async def quote(
        self,
        interaction: nextcord.Interaction,
        quote_id: int = SlashOption(
            name="quote_id",
            description="The ID number of the quote you are looking for.",
            required=False,
        ),
        keyword: str = SlashOption(
            name="keyword",
            description="A search term to look for when finding your quote.",
            required=False,
        ),
        author_name: str = SlashOption(
            name="author_name", description="Find a quote by the given author.", required=False
        ),
    ):
        self.prep_db(interaction.guild_id)
        quote_data = None
        if not (quote_id or keyword or author_name):
            quote_data = self.get_random_quote(interaction.guild_id)
            if not quote_data:
                await interaction.send("This server hasn't added any quotes yet. Try `/quoteadd`.", ephemeral=True)
                return
        elif quote_id:
            quote_data = self.get_quote_by_id(quote_id, interaction.guild_id)
        elif (keyword and author_name):
            # search by both keyword and author name
            quote_data = self.get_quote_by_keyword_and_author(keyword, author_name, interaction.guild_id)
        elif keyword:
            quote_data = self.get_quote_by_keyword(keyword, interaction.guild_id)
        elif author_name:
            quote_data = self.get_quote_by_author(author_name, interaction.guild_id)

        if quote_data:
            await interaction.send(embed=self.generate_quote_embed(quote_data))
            self.increment_display_count(quote_data["id"], interaction.guild_id)
        else:
            await interaction.send("Sorry, I couldn't find that quote.", ephemeral=True)

    @nextcord.slash_command(
        name="quoteadd",
        description="Add a quote to your quote database. Supports both text and image quotes.",
    )
    async def quoteadd(
        self,
        interaction: nextcord.Interaction,
        quote_text: str = SlashOption(
            name="text", description="The text you'd like the new quote to contain.", required=False
        ),
        quote_author: str = SlashOption(
            name="author",
            description="The author of the quote that you are adding.",
            required=False,
        ),
        quote_image: str = SlashOption(
            name="image_url",
            description="The URL of the image you'd like to display for this quote.",
            required=False,
        ),
    ):
        self.prep_db(interaction.guild_id)
        if not (quote_text or quote_author or quote_image):
            interaction.send("You can't add a completely blank quote!", ephemeral=True)
            return
        quote_data = ""
        if quote_image:
            quote_data = "image:" + quote_image + " "
        if quote_text:
            quote_data = quote_data + quote_text
        new_quote = self.add_quote(str(quote_author), quote_data, interaction.guild_id)
        await interaction.send(
            "Added quote #" + str(new_quote["id"]) + ".", embed=self.generate_quote_embed(new_quote)
        )

    @nextcord.slash_command(
        name="quoteremove",
        description="Remove a quote from your quote database. (Requires permissions)",
    )
    async def quoteremove(
        self,
        interaction: nextcord.Interaction,
        quote_id: int = SlashOption(
            name="quote_id", description="The ID of the quote you'd like to remove.", required=True
        ),
    ):
        self.prep_db(interaction.guild_id)
        remove_success = self.remove_quote(interaction.user, quote_id, interaction.guild_id)
        if remove_success:
            await interaction.send("Removed quote #" + str(quote_id) + ".")
            return
        else:
            await interaction.send(
                "Failed to remove quote. Either the quote ID was not found, or you do not have permission to do that."
            )
            return

    @nextcord.slash_command(
        name="quotestats",
        description="Detailed statistics about the quotes in your database and how frequently they appear.",
    )
    async def quotestats(
        self,
        interaction: nextcord.Interaction,
        quote_id: int = SlashOption(
            name="quote_id",
            description="Optionally, view statistics about a specific quote.",
            required=False,
        ),
    ):
        self.prep_db(interaction.guild_id)
        if not quote_id:
            top_10 = self.get_top_10_quotes(interaction.guild_id)
            bottom_10 = self.get_bottom_10_quotes(interaction.guild_id)
            top_10_index = 0
            top_10_text = ""
            bottom_10_index = 0
            bottom_10_text = ""

            # generate text for 'top10' half of embed
            for quote in top_10:
                top_10_index += 1
                quote_id = quote["id"]
                quote_display_count = quote["display_count"]
                # trim quote to first 20 characters
                quote_content = quote["content"]
                if len(quote_content) > 23:
                    quote_content = quote_content[0:20] + "..."
                top_10_text += str(top_10_index) + ". #" + str(quote_id)
                top_10_text += " (" + str(quote_display_count) + " times): "
                top_10_text += quote_content + "\n"

            # generate text for 'bottom10' half of embed
            for quote in bottom_10:
                bottom_10_index += 1
                quote_id = quote["id"]
                quote_display_count = quote["display_count"]
                # trim quote to first 20 characters
                quote_content = quote["content"]
                if len(quote_content) > 23:
                    quote_content = quote_content[0:20] + "..."
                bottom_10_text += str(bottom_10_index) + ". #" + str(quote_id)
                bottom_10_text += " (" + str(quote_display_count) + " times): "
                bottom_10_text += str(quote_content) + "\n"

            if not top_10_text or not bottom_10_text:
                await interaction.send("This server hasn't added any quotes yet. Try `/quoteadd`.")
                return

            # create Embed to display the rankings
            quote_embed = nextcord.Embed(title="Quote Rankings", colour=nextcord.Colour.default())
            quote_embed.add_field(name="Top 10", value=top_10_text, inline=True)
            quote_embed.add_field(name="Bottom 10", value=bottom_10_text, inline=True)
            await interaction.send(embed=quote_embed)
            return

        if self.get_quote_by_id(quote_id, interaction.guild_id):
            total_displayed = self.get_quote_stats_by_id(quote_id, interaction.guild_id)
            last_30_days = self.get_quote_stats_by_id(quote_id, interaction.guild_id, 30)
            last_7_days = self.get_quote_stats_by_id(quote_id, interaction.guild_id, 7)
            last_24_hrs = self.get_quote_stats_by_id(quote_id, interaction.guild_id, 1)
            quote_rank = self.get_quote_rank_by_id(quote_id, interaction.guild_id)
            quote_text = self.get_quote_by_id(quote_id, interaction.guild_id)["content"]
            quote_author = self.get_quote_by_id(quote_id, interaction.guild_id)["author"]
            if len(quote_text) > 75:
                quote_text = (quote_text[0:72]) + "..."
            description_text = "**Rank #" + str(quote_rank) + "**\n"
            description_text += quote_author + ': "' + quote_text + '"'
            recent_stats_text = "Last 24 hrs: " + str(last_24_hrs) + "\n"
            recent_stats_text += "Last 7 days: " + str(last_7_days) + "\n"
            recent_stats_text += "Last 30 days: " + str(last_30_days) + "\n"
            recent_stats_text += "All time: " + str(total_displayed)
            quote_embed = nextcord.Embed(
                title="Quotestats #" + str(quote_id),
                description=description_text,
                colour=nextcord.Colour.default(),
            )
            quote_embed.add_field(name="Recent Stats", value=recent_stats_text)
            if total_displayed == 0:
                quote_embed.set_footer(text="Last appearance: None yet!")
            else:
                quote_embed.set_footer(
                    text="Last appearance: "
                    + self.get_quote_last_appearance(quote_id, interaction.guild_id)
                )
            await interaction.send(embed=quote_embed)
            return

        else:
            await interaction.send("Sorry, I couldn't find that quote.", ephemeral=True)
            return


def setup(bot):
    bot.add_cog(QuoteCog(bot))
