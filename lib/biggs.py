#!/usr/bin/env python

import logging
import json

# External dependencies
import discord
from tinydb import TinyDB, Query

log = logging.getLogger("Biggs")

def check_prefix(command_prefix: str, message: discord.Message):
  return message.content.startswith(command_prefix)

def remove_prefix(command_prefix: str, message: discord.Message):
  return message.content.replace(command_prefix, '')

class Biggs(discord.Client):
  def setup(self, config: dict):
    self.run(config["token"])
    self.tinydb_instance = TinyDB(config["tinydb_path"])
    self._server_id = config["server_id"] # type: int
    self._notice_channel_id = config["notice_channel_id"] # type: int

  def db_insert(self, message_contents: str):
    parsed_json = json.loads(message_contents)
    self.tinydb_instance.insert(parsed_json)

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

  async def on_message(self, message: discord.Message):
    try:
      log.info(f"Message from {message.author}: {message.content}")
      if check_prefix("$inserttest", message):
        self.db_insert(remove_prefix("$inserttest", message))

    except Exception as exc:
      log.error(exc)
      raise exc
