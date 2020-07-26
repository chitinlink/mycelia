import logging
import json
import re
import sys
from math import ceil
from typing import Any
from functools import reduce

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

# Logging
log = logging.getLogger("Biggs")

class Biggs(commands.Bot):
  def setup(self, config: dict):
    self._config = config
    self._done_setup = False

    self._db = TinyDB(f"{config['tinydb_path']}db.json")
    self._blacklist = self._db.table("blacklist")

    self.run(config["token"])

  async def on_ready(self):
    if not self._done_setup:
      # Internal props
      self._guild = self.get_guild(self._config["guild_id"])
      self._notice_channel = self.get_channel(self._config["notice_channel_id"])
      self._ignored_channels = [self.get_channel(c) for c in self._config["ignored_channels"]] + [self._notice_channel]

      def parse_reactions(_id):
        if type(_id) == int: return self.get_emoji(_id)
        if type(_id) == str: return _id
        raise ValueError("Only str or int allowed in the reactions.")

      self._reactions = { key: parse_reactions(_id) for key, _id in self._config["reactions"].items() }

      # Bot internals -- do not remove this
      self.add_cog(Core(self))

      # Commands
      self.add_cog(Blacklist(self))
      self.add_cog(Role(self))
      self.add_cog(Time(self))

      self._done_setup = True
      log.info("Initial setup done.")

    # Done loading
    log.info(f"Logged on as {self.user}!")

  def is_mod(self, member: discord.Member) -> bool:
    """ Checks whether or not the given member is a moderator based on their roles """
    return len(set(map(lambda r: r.id, member.roles)) & set(self._config["mod_roles"])) > 0

  async def post_notice(self, kind: str = "plain", original_message: discord.Message = None, data: Any = None):
    # Plain message
    if kind == "plain":
      await self._notice_channel.send(data)

    # Scan match
    elif kind == "scan_match":
      names = ", ".join(map(lambda m: f"`{m['name']}`", data))

      entry = "<entry>"
      if len(data) == 1: entry = data[0]["name"]

      await self._notice_channel.send(
        f"**Blacklist match:** {names}\n" +
        f"by {original_message.author.mention} in {original_message.channel.mention}:\n" +
        md_quote(original_message.content) + "\n" +
        f"{original_message.jump_url}\n" +
        f"Use `blacklist view {entry}` for details"
      )

    # Unknown?
    else:
      exc = f"Unknown post_notice kind: {kind}"
      log.error(exc)
      raise ValueError(exc)
