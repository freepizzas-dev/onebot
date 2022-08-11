from datetime import datetime
import os
import sys
import logging
import nextcord
from nextcord.ext import commands
import aiohttp
from dotenv import load_dotenv

import onebot_config
import onebot_utils
import onebot_db_utils

load_dotenv()

# we don't need typing or user presence events, and disabling the intent
# cuts down on events received from the gateway.
intents = nextcord.Intents.default()
intents.typing = False
if onebot_config.AUTOSHARDING:
    onebot = commands.AutoShardedBot(intents=intents)
else:
    onebot = commands.Bot(intents=intents)
onebot.config = onebot_config
onebot.utils = onebot_utils
onebot.db_utils = onebot_db_utils
onebot.aiohttp_session = None #async init happens later, in on_ready
onebot.launch_time = datetime.now()
onebot.log_filename = "log/onebot-" + str(onebot.launch_time.strftime("%Y%b%d-%H%M%S")) + ".log"
logging.basicConfig(
    filename=onebot.log_filename, level=onebot.config.LOG_LEVEL, format="%(asctime)s:%(levelname)s:%(message)s"
)
onebot.logger = logging.getLogger("main")
onebot.logger.info("Launched at " + onebot.launch_time.strftime("%Y-%b-%d-%H:%M:%S"))

if "DISCORD_TOKEN" not in os.environ:
    onebot.logger.critical("DISCORD_TOKEN missing from your .env file! I can't run without it.")
    onebot.logger.critical("Get a token at https://discord.com/developers/applications")
    onebot.logger.critical("Exiting.")
    sys.exit("No DISCORD_TOKEN specified")

# simple module loader
for module in onebot.config.ONEBOT_MODULES:
    module = "modules." + module + "." + module
    try:
        onebot.load_extension(module)
    except commands.ExtensionNotFound as e:
        onebot.logger.error("Module " + module + " couldn't be found.")
        onebot.logger.error(e.__traceback__)
    except commands.ExtensionAlreadyLoaded as e:
        onebot.logger.error("Duplicate module " + module + " not loaded.")
        onebot.logger.error(e.__traceback__)
    except (commands.NoEntryPointError, commands.ExtensionFailed) as e:
        onebot.logger.error("Something went wrong while loading module " + module + ".")
        onebot.logger.error(e.__traceback__)

# what to do when connection to Discord is established
@onebot.event
async def on_ready():
    if not onebot.aiohttp_session:
        onebot.aiohttp_session = aiohttp.ClientSession()
    activity = nextcord.Game(name=onebot.config.ACTIVITY)
    await onebot.change_presence(activity=activity)

# do we need to do any cleanup on close?
@onebot.event
async def on_close():
    if onebot.aiohttp_session:
        await onebot.aiohttp_session.close()

# start the bot
discord_token = os.environ.get("DISCORD_TOKEN")
onebot.run(discord_token)
