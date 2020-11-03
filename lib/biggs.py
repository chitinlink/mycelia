import logging
import subprocess

# External dependencies
from tinydb import TinyDB
from discord import Intents
from discord.ext import tasks, commands

# Local dependencies
from lib.utils.etc import Service
from lib.utils.text import fmt_guild
from lib.utils.checks import is_bot_ready, is_not_ignored_channel, is_not_from_bot
# Services
from lib.services.core import Core
from lib.services.blacklist import Blacklist
from lib.services.role import Role
from lib.services.time import Time
from lib.services.anon import Anon
from lib.services.schedule import Schedule
from lib.services.reminder import Reminder
from lib.services.fun import Fun

# Intents
# https://discordpy.readthedocs.io/en/stable/intents.html
intents = Intents.default()
# Need members intent for lib.utils.checks.is_guild_member
intents.members = True

# Logging
log = logging.getLogger("Biggs")

class Biggs(commands.Bot):
  def __init__(self, config: dict, *bot_args):
    super().__init__(command_prefix=config["command_prefix"], intents=intents, *bot_args)

    self.version = subprocess.check_output(
      "git rev-parse --short HEAD".split(" ")
    ).decode("utf-8").strip()

    self._config = config
    self._done_setup = False

    self._db = TinyDB(f"{config['tinydb_path']}db.json")

    self.run(config["token"])

  async def on_ready(self):
    if not self._done_setup:
      # Internal props
      self._guild = self.get_guild(self._config["guild_id"])
      self._notice_channel = self.get_channel(self._config["notice_channel_id"])
      self._ignored_channels = [self.get_channel(c) for c in self._config["ignored_channels"]]

      def parse_reactions(_id):
        if type(_id) == int: return self.get_emoji(_id)
        if type(_id) == str: return _id
        raise ValueError("Only str or int allowed in the reactions.")

      self._reactions = { key: parse_reactions(_id) for key, _id in self._config["reactions"].items() }

      # Services
      self.add_cog(Core())
      self.add_cog(Blacklist(self))
      self.add_cog(Role(self))
      self.add_cog(Time())
      self.add_cog(Anon())
      self.add_cog(Schedule(self))
      self.add_cog(Reminder(self))
      self.add_cog(Fun())

      self._done_setup = True
      log.info("Initial setup done.")

    # Done loading
    log.info(f"Logged on as {self.user}!")

    log.info("Biggs is a member of these guilds:")
    for guild in self.guilds:
      log.info(f"• {fmt_guild(guild)}")

  # Global check
  async def bot_check(self, ctx: commands.Context) -> bool:
    # Log all commands invoked
    log.info(f"Command invoked: {ctx.command.qualified_name}")

    # "Command funnel"
    # Ensure all of these basic checks pass
    return (
      is_bot_ready(ctx) and
      is_not_ignored_channel(ctx) and
      is_not_from_bot(ctx)
    )
