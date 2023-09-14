Another Discord bot written in Python using the nextcord library.

Below is the public description for the developer-hosted live version of oneBot, followed by some implementation details and information on how to host your own copy or create new modules for the bot.



-------




```
                   ____        _   
                  |  _ \      | |  
   ___  _ __   ___| |_) | ___ | |_ 
  / _ \| '_ \ / _ \  _ < / _ \| __|
 | (_) | | | |  __/ |_) | (_) | |_ 
  \___/|_| |_|\___|____/ \___/ \__|
                                   
               ...to rule them all.
```

A powerful one-stop-shop inspired by IRC.

Google Web Search, Image Search, Gif Search, Weather, Wiktionary, Urban Dictionary.

Don't see what you need?

----> [join the Discord server!](https://discord.gg/cwWDVtCW3x)<----

Feature requests are always welcome.

----> [test the bot HERE!](https://discord.gg/cwWDVtCW3x)<----

----> [Rate and review the bot on top.gg!](https://top.gg/bot/825499706724843573)<----

### HOW TO HOST YOUR OWN VERSION OF ONEBOT
First, familiarize yourself with the [Discord Developer Portal](https://discord.com/developers/applications). You'll need to create an application for your bot and set it up. There are plenty of tutorials online on how to accomplish this, so I won't get in to it here.

This bot requires python3, at least version 3.9, but I recommend the latest.

After you have a bot set up, download the files in this repository. This bot relies a lot on third-party libraries, so you'll need to install those first. The `requirements` file lists all the python modules you'll need, and I recommend reviewing it so you don't install anything you don't want. You can use pip to install this list automagically using `pip -r requirements.txt`. 

Once you have all the requirements installed, you need to specify at least the Discord token for your application in the `.env` file. Replace [Your Discord Token Here] with your actual token from the Discord Developer Portal.

Note that there are various other tokens required to get the full functionality of the bot. Refer to the `.env` file to see what you need. However, to get the bot started, you only need the Discord token, and the modules that require the others will stay un-loaded.

Finally, check the `onebot_config.py` file for configuration options. You can leave them set to the defaults, and the bot will work fine. But I really suggest reviewing them to customize your bot experience!

You are now ready to start your bot. Use your python interpreter to start the bot by running the `onebot.py` file. The bot is designed to be run in the background as a service, so you can start it headless and check the `/log` directory for output. Your bot should be up and running!

### COMMAND REFERENCE

`/info` - show a simple information display for the bot, which includes useful links.

#### SEARCH

`/google` - an "I'm Feeling Lucky" search for the specified keywords. Works great for YouTube too! Try `/google yt keyboard cat`.

`/image` - a Google image search (SafeSearch enabled!). You can also use this without keywords for completely random images.

`/gif` - a random GIF search. Retrieves a random gif with the specified keyword, or, if no keyword is specified, a totally random GIF!

`/ud` - search Urban Dictionary for the most popular definition of the specified keyword. Supports Word of the Day.

`/define` - search Wiktionary for a definition. Supports any language -- use the `language` parameter to specify.
Related: `/etym`

`/etym` - Display the full etymology of a word from Wiktionary. Supports the `language` parameter to specify any language.


#### SOCIAL


`/quote` - Retrieve your favorite quotes from the server. Retrieve them later using their ID, or just use the command by itself for a random quote.

`/quoteadd` - Add a new quote to your quote database!

`/quoteremove` - Remove a quote from the quote database. Requires `Manage Server` permissions to use.

`/quotestats` - Show stats from your `/quote` database. See the top 10 and bottom 10 quotes, or use the quote ID parameter to see detailed stats for a specific quote.

`/weather` - Retrieves the weather for a specific location. Allows you to set your default location for quicker future use by using the `setdefault` parameter. 

`/moon` - Tells you if the moon is waxing or waning.

`/joke` - Retrieves a random dad joke. Supports searching by keyword.

`/emote` - display a large, upscaled emote for the custom server emoji that you specify.

### HOW TO CREATE YOUR OWN MODULE FOR ONEBOT
It's really easy. First, decide on a name for your module. This isn't important and doesn't have to match the name of the slash command you want to make. Create a folder in the `modules` folder with the name of your module, then create a python file inside that folder with the same name.

For example, if I wanted to make a module called `Foo`, I'd make a `modules/foo` folder and inside that folder is `foo.py`.

Finally, I would add the module `foo` to the file `onebot_config.py` under the `ONEBOT_MODULES` setting to tell onebot to load my new `foo` module.

#### MODULE TEMPLATE
Below is a template for a simple module that sends a message to the channel.
Example `foo.py`:

```py
import nextcord
from nextcord.ext import commands

class FooCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="foo",
        description='Sends the message "foo foo foo!" as a response.',
    )
    async def foo(self, interaction: nextcord.Interaction):
        await interaction.send("foo foo foo!")

def setup(bot):
    bot.add_cog(FooCog(bot))
```

This can be considered a `module skeleton`, and nearly all modules will follow this format.

Onebot uses the [nextcord library](https://github.com/nextcord/nextcord), so to do anything more complicated I recommend checking our their excellent [documentation](https://docs.nextcord.dev/en/stable/).
#### UTILITY FUNCTIONS
Onebot contains utility modules that handle storing and retrieving data from a database, and a few other tasks.

##### DB_UTILS
You can access the database utility functions by using `self.bot.db_utils` in your module. `db_utils` contains the following functions:

`list_db()`

Returns a list of database files available to onebot.

`create_db(server_id)`

Creates a new database for the specified server id. NOTE: This happens automatically if a db doesn't exist, so you shouldn't have to call this function manually.

`delete_db(server_id)`

Deletes the database for the specified server id.

`get_db_connection(server_id)`

Returns an sqlite3 Connection object.

`get_server_pref(server_id, preference)`

Returns the stored value for the specified String `preference` for the specified server. Can be used to read server-wide preferences that are set by a server user.

`set_server_pref(server_id, preference, value)`

Stores a value for the specified String `preference` for the specified server. Used to store server-wide preferences that a set using a slash command.

`clear_server_pref(server_id, preference)`

Clears the specified String `preference` for the specified server by removing it from the database.

`get_member_pref(server_id, member_id, preference)`

Retrieves the *user-specific* stored value for the specified String `preference` for the specified server. Used to read *member-specific* preferences (for example, a user's default weather location that they saved earlier).

`set_member_pref(server_id, member_id, preference, value)`

Stores the *user-specific* value for the specified String `preference` for the specified server. Used to store *member-specific* preferences (like the aforementioned default weather location).


You can use these `db_utils` to read/write from an sqlite3 database easily.

##### OTHER UTILS
Similarly, `self.bot.utils` contains more utility features, and these are non-database related. `self.bot.utils` contains the following functions:

`get_random_word(bot)`

Returns a String random word. Used to retrieve random gifs and images for `/gif` and `/image`. You can use this in your own modules by passing the `bot` context object to this function.

#### EXAMPLE MODULE WITH DATABASE OPERATIONS
Below is an example `ReadWrite` module that demonstrates how to use the built-in database functions to store and retrieve a user string.

Example `readwrite.py`:

```py
import nextcord
from nextcord.ext import commands

class ReadWriteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="read",
        description='Sends the stored user string.',
    )
    async def read(self, interaction: nextcord.Interaction):
        stored_data = self.bot.db_utils.get_member_pref(interaction.guild_id, interaction.user.id, 'readwritecog.data')
        await interaction.send(stored_data)
    
    @nextcord.slash_command(
        name="write",
        description='Stores the string that the user specifies.',
    )
    async def write(self, interaction: nextcord.Interaction, data_to_store: str = SlashOption(
            name="data to store",
            description="Type what you want to store in the database",
            required=True,
        ),):
        self.bot.db_utils.set_member_pref(interaction.guild_id, interaction.user.id, 'readwritecog.data', data_to_store)
        await interaction.send("Stored your data in the database! Use /read to retrieve it.")

def setup(bot):
    bot.add_cog(ReadWriteCog(bot))
```

If you need functionality that extends beyond one-row storage and retrieval, you can use `bot.db_utils.get_db_connection(server_id)` to get your own sqlite3 Connection object, and do anything you want!
