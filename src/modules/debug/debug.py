from datetime import datetime
import nextcord
from nextcord.ext import commands


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def separator(self):
        self.bot.logger.info("--------------------------------------------------------------")

    @commands.Cog.listener()
    async def on_ready(self):
        self.separator()
        self.bot.logger.info("Online at " + datetime.now().strftime("%Y-%b-%d-%H:%M:%S"))
        guild_count = len(self.bot.guilds)
        member_count = 0
        for guild in self.bot.guilds:
            # apparently guild.member_count doesn't exist at all if the inviter
            # declines the Members intent soooooo
            try:
                guild_members = guild.member_count
            except Exception:
                guild_members = "unknown"
            try:
                total_chan_cnt = len(guild.channels)
                voice_chan_cnt = 0
                cat_chan_cnt = 0
                for channel in guild.channels:
                    if channel.type is nextcord.ChannelType.voice:
                        voice_chan_cnt += 1
                    if channel.type is nextcord.ChannelType.category:
                        cat_chan_cnt += 1
                guild_channels = (
                    str(total_chan_cnt) + " total, " + str(voice_chan_cnt) + " voice, "
                    + str(cat_chan_cnt) + " category"
                )
            except Exception:
                guild_channels = "unknown"
            if guild_members != "unknown":
                member_count = member_count + guild.member_count
            self.bot.logger.info(str(guild.id) + ": " + str(guild_members) + " members, "
                + str(guild_channels) + " channels | " + str(guild.name)
            )
        self.bot.logger.info(str(member_count) + " members in " + str(guild_count) + " guilds.")
        self.separator()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            guild_members = guild.member_count
        except Exception:
            guild_members = "unknown"
        self.separator()
        self.bot.logger.info("!! NEW GUILD !! ")
        self.bot.logger.info("ID: " + str(guild.id))
        self.bot.logger.info("Name: " + str(guild.name))
        self.bot.logger.info("Members: " + str(guild_members))
        self.separator()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.separator()
        self.bot.logger.info('Left guild "' + str(guild.name) + '" (ID: ' + str(guild.id) + ")")
        self.separator()

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == nextcord.InteractionType.application_command:
            command_name = str(interaction.data["name"])
            guild_id = str(interaction.guild_id)
            user = str(interaction.user.name)
            if "options" in interaction.data:
                options = interaction.data["options"]
                self.bot.logger.debug(
                    "/" + command_name + " | " + guild_id + ": " + user + " | options: " + str(options)
                )
            else:
                self.bot.logger.debug("/" + command_name + " | " + guild_id + ": " + user)


def setup(bot):
    bot.add_cog(DebugCog(bot))
