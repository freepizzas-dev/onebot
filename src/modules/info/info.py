from datetime import datetime
import nextcord
from nextcord.ext import commands


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="info", description="Shows various information about this bot.")
    async def info(self, interaction: nextcord.Interaction):
        self_name = self.bot.user.name + "#" + self.bot.user.discriminator
        guilds = self.bot.guilds
        guild_count = len(guilds)
        member_count = 0
        for guild in guilds:
            member_count = member_count + guild.member_count
        member_count = round(member_count, -2)
        command_count = len(self.bot.get_application_commands())
        uptime_tdelta = datetime.now() - self.bot.launch_time
        uptime = self.bot.utils.strfdelta(uptime_tdelta, "{D} day(s) {H:02}:{M:02}:{S:02}")
        embed_title = str(self_name) + " /info"
        embed_description = "I can see ~" + str(member_count) + " members in " + str(guild_count) + " server(s).\n"
        embed_description = embed_description + str(command_count) + " slash commands available globally.\n"
        embed_description = embed_description + "Uptime: " + str(uptime) + "\n"
        embed_description = embed_description + "For a list of available commands, type `/`."
        embed = nextcord.Embed(title=embed_title, description=embed_description)
        loaded_modules = ", ".join(self.bot.loaded_modules)
        error_modules = ", ".join(self.bot.error_modules)
        embed.add_field(name="Loaded modules ✅", value=loaded_modules, inline=False)
        if not error_modules:
            embed.add_field(name="Failed modules ❌", value="None. We're all good!", inline=False)
        else:
            embed.add_field(name="Failed modules ❌", value=error_modules, inline=False)
        links = ""
        config = self.bot.config
        if config.SUPPORT_SERVER:
            links = links + "[Join the Support Server](" + self.bot.config.SUPPORT_SERVER + ")\n"
        if config.GITHUB_LINK:
            links = links + "[Github Repository](" + self.bot.config.GITHUB_LINK + ")\n"
        if config.TOPGG_LINK:
            links = links + "[" + self.bot.user.name + " on Top.gg (vote now!)](" + self.bot.config.TOPGG_LINK + ")\n"
        if config.BOTSGG_LINK:
            links = links + "[" + self.bot.user.name + " on Bots.gg](" + self.bot.config.BOTSGG_LINK + ")"
        links = links.strip()
        if links:
            embed.add_field(name="Useful links", value=links, inline=False)
        footer = "Local time: " + datetime.now().strftime("%B %d, %Y %I:%M %p")
        embed.set_footer(text=footer)
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(InfoCog(bot))
