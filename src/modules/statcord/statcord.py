import os
import nextcord
from nextcord.ext import commands
import statcord
import types


class StatcordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = os.environ.get("STATCORDKEY")
        self.api = statcord.Client(self.bot, self.key)

    @commands.Cog.listener()
    async def on_ready(self):
        self.api.start_loop()  # don't start the loop until on_ready or the initial user count fails

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == nextcord.InteractionType.application_command:
            ctx = types.SimpleNamespace()
            ctx.author = interaction.user
            ctx.command = types.SimpleNamespace()
            ctx.command.name = str(interaction.data["name"])
            self.api.command_run(ctx)


def setup(bot):
    if "STATCORDKEY" not in os.environ:
        bot.logger.error("STATCORD | STATCORDKEY missing in your .env file! Statcord module not loaded.")
        bot.logger.error("STATCORD | You need a Statcord API key. https://docs.statcord.com/#/?id=get-your-key")
    else:
        bot.add_cog(StatcordCog(bot))
