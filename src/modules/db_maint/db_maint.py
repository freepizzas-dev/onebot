from datetime import datetime
from nextcord.ext import tasks, commands

# a simple cog to handle periodic DB tasks
# currently, it just updates when a guild was last seen, and deleted a guild's
# data after it hasn't been seen for 90 days.
class DBMaintCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_last_seen.start()
        self.loop_init = False

    @tasks.loop(minutes=60)
    async def update_last_seen(self):
        guilds = self.bot.guilds
        for guild in guilds:
            self.bot.db_utils.set_server_pref(guild.id, "last_seen", datetime.now().timestamp())
            self.bot.db_utils.clear_server_pref(guild.id, "marked_delete")
        # check if database expiry is disabled via config
        if not self.bot.config.DB_EXPIRY_DAYS:
            return
        # we want this loop to trigger the second one, because we should wait for
        # the bot to be ready and update the last seen timestamps first.
        if not self.loop_init:
            self.delete_old_data.start()
            self.loop_init = True

    @update_last_seen.before_loop
    async def before_update_last_seen(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=120)
    async def delete_old_data(self):
        dbs = self.bot.db_utils.list_db()
        now = datetime.now().timestamp()
        timeout = float(self.bot.config.DB_EXPIRY_DAYS * 60 * 60 * 24)
        for db in dbs:
            last_seen = float(self.bot.db_utils.get_server_pref(db, "last_seen"))
            if last_seen + timeout < now:
                if self.bot.db_utils.get_server_pref(db, "marked_delete"):
                    self.bot.db_utils.delete_db(db)
                    self.bot.logger.info("DB_MAINT | Deleted DB " + str(db) + " due to inactivity.")
                else:
                    self.bot.db_utils.set_server_pref(db, "marked_delete", 1)
                    self.bot.logger.info("DB_MAINT | DB " + str(db) + " marked for deletion. This database will be deleted the next time the cleanup task runs.")

def setup(bot):
    bot.add_cog(DBMaintCog(bot))
