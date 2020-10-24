import logging
import json
from typing import Any

# External dependencies
import discord
import jsonschema
from tinydb import TinyDB, where
from discord.ext import tasks, commands

# Local dependencies
from lib.utils import md_quote
# Services
from lib.services.core import Core
from lib.services.blacklist import Blacklist
from lib.services.role import Role
from lib.services.time import Time
from lib.services.anon import Anon
from lib.services.schedule import Schedule
from lib.services.reminder import Reminder
from lib.services.fun import Fun

# Logging
log = logging.getLogger("Biggs")

# Intents
# https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
# Need members intent for lib.utils.is_guild_member
intents.members = True

class Biggs(commands.Bot):
  def __init__(self, config: dict, *bot_args):
    super().__init__(command_prefix=config["command_prefix"], intents=intents, *bot_args)

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

      # Bot internals -- do not remove this
      self.add_cog(Core())

      # Commands
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
