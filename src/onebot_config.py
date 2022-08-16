import logging

# This is the config file for onebot.
# Changes won't be reflected until you restart the bot.

# Whether or not the bot should use sharding.
# https://discord.com/developers/docs/topics/gateway#sharding
AUTOSHARDING = False

# Define your bot's 'Activity' here. It will show up as the 'status' in the user list.
ACTIVITY = "onebot twobot redbot bluebot"

# Modules you'd like to load. If it's not here, it won't be loaded.
ONEBOT_MODULES = [
    "db_maint",
    "debug",
    "define",
    "emote",
    "gif",
    "google",
    "image",
    "info",
    "joke",
    "moon",
    "quote",
    "statcord",
    "topgg",
    "urbandictionary",
    "weather",
]

# Image results containing any of these phrases will be discarded from /image.
# This contains domains that disallow hotlinking from Discord.
# Using it allows for a better user experience, because non-embedding images
# are REALLY annoying.
# You can use this to filter image results by any keyword you want, but it will
# only apply to the URL portion of the result.
ONEBOT_IMGBL = [
    "lookaside.fbsbx.com",
    "licdn.com",
    "asos-media.com",
    "fashionphile.com",
    "fjcdn.com",
    "x-raw-image",
    "wordpress.com",
    "worthpoint.com",
    ".svg",
    "iconspng.com",
    "ytimg.com",
    "squadhelp.com",
    "washingtonpost.com",
    "tiktok.com",
    "panerabread.com",
    "sevenstore.com",
    "alamy.com",
    "fabulistmagazine.com",
    "chewy.com",
    "support.discord.com",
    "naijafinix.com",
]

# Local sqlite3 database path -- default is usually ok
# but you can make this anything you want.
# Changing it won't make onebot copy your databases over, so make sure to do that
# unless you want the bot to start fresh.
DB_PATH = "./db/"

# If onebot is removed from a server, that server's data will be removed in this many days.
# Set to 0 to disable this behavior, but you shouldn't do that with a verified bot.
DB_EXPIRY_DAYS = 90

# Set the minimum severity level a message must be to be written to the disk log.
# By default, this is set to logging.INFO. You'll get messages about guild and user count,
# and when your bot is joining or leaving a guild.
# If you find it to be too chatty, use logging.WARNING.
# For testing, you might find logging.DEBUG useful.
LOG_LEVEL = logging.INFO

# You can specify various links that appear in the "/info" command below
# Set to an empty string or remove entirely to hide the link from the command
GITHUB_LINK = "https://github.com/freepizzas-dev/onebot"
SUPPORT_SERVER = "https://discord.gg/cwWDVtCW3x"
TOPGG_LINK = "https://top.gg/bot/825499706724843573"
BOTSGG_LINK = "https://discord.bots.gg/bots/825499706724843573"
