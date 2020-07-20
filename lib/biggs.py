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
from lib.utils import quote
# Services
from lib.services.log_message import log_message
from lib.services.blacklist import Blacklist
from lib.services.funnel import Funnel

# Logging
log = logging.getLogger("Biggs")

class Biggs(commands.Bot):
  def setup(self, config: dict):
    self._config = config

    self._db = TinyDB(f"{config['tinydb_path']}db.json")
    self._blacklist = self._db.table("blacklist")

    self.run(config["token"])

  async def on_ready(self):
    # Internal props
    self._guild = self.get_guild(self._config["guild_id"])
    self._notice_channel = self.get_channel(self._config["notice_channel_id"])
    self._ignored_channels = [self.get_channel(c) for c in self._config["ignored_channels"]] + [self._notice_channel]

    # Command funnel -- do not remove this
    self.add_cog(Funnel(self))

    # Commands
    self.add_cog(Blacklist(self))

    # Listeners
    self.add_listener(log_message, "on_message")

    # Done loading
    log.info(f"Logged on as {self.user}!")

  def is_mod(self, member: discord.Member) -> bool:
    """ Checks whether or not the given member is a moderator based on their roles """
    return len(set(member.roles) & set(self._config["mod_roles"])) > 0

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
        quote(original_message.content) + "\n" +
        f"{original_message.jump_url}\n" +
        f"Use `blacklist view {entry}` for details"
      )

    # Unknown?
    else:
      exc = f"Unknown post_notice kind: {kind}"
      log.error(exc)
      raise ValueError(exc)
