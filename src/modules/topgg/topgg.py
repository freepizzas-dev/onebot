import os
from nextcord.ext import tasks, commands


class TopggCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TOPGG_TOKEN = os.environ.get("TOPGG_TOKEN")

    @tasks.loop(minutes=120)
    async def update_topggstats(self):
        server_count = str(len(self.bot.guilds))
        headers = {"Authorization": self.TOPGG_TOKEN}
        bot_url = "https://top.gg/api/bots/" + str(self.bot.user.id) + "/stats"
        payload = {"server_count": server_count}
        async with self.bot.aiohttp_session.post(bot_url, data=payload, headers=headers) as resp:
            if resp.status != 200:
                self.bot.logger.error("TOPGG | Failed to post server count.")
                self.bot.logger.error("TOPGG | Response code: " + str(resp.status))
            else:
                self.bot.logger.info("TOPGG | Posted server count: " + server_count)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_topggstats.start()


def setup(bot):
    if "TOPGG_TOKEN" not in os.environ:
        bot.logger.error("TOPGG | Missing TOPGG_TOKEN in your .env file! TOPGG module not loaded.")
        bot.logger.error("TOPGG | You need a token to use top.gg's API. https://docs.top.gg/")
    else:
        bot.add_cog(TopggCog(bot))
