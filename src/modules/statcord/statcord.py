import os
from discord.ext import commands
import statcord


class StatcordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = os.environ.get("STATCORDKEY")
        self.api = statcord.Client(self.bot, self.key)
        self.api.start_loop()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.api.command_run(ctx)


def setup(bot):
    if "STATCORDKEY" not in os.environ:
        bot.logger.error("STATCORD | STATCORDKEY missing in your .env file! Statcord module not loaded.")
        bot.logger.error("STATCORD | You need a Statcord API key. https://docs.statcord.com/#/?id=get-your-key")
    else:
        bot.add_cog(StatcordCog(bot))
