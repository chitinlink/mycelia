#!/usr/bin/env python

import logging
import json
import re
import sys

# External dependencies
import discord
import jsonschema
from tinydb import TinyDB, Query

# Logging
log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws): self._log(15, message, args, **kws)
logging.Logger.msg = msg

class Biggs(discord.Client):
  def setup(self, config: dict):
    self._tinydb_instance = TinyDB(f"{config['tinydb_path']}db.json")

    self._blacklist_schema = json.load(open('blacklist_schema.json'))

    self._guild_id = config["guild_id"] # type: int

    self._notice_channel_id = config["notice_channel_id"] # type: int

    self.run(config["token"])

  def mentioning_me(self, message: discord.Message) -> bool:
    """ Returns true if Biggs is mentioned in the given message. """
    return self.user in message.mentions

  def remove_mention(self, message: str) -> str:
    """ Intended to be used on messages mentioning Biggs,
        removes the mention(s) and returns the remaining text. """
    return message.replace(f"<@!{self.user.id}>", "").strip()

  def db_insert(self, parsed_json):
    self._tinydb_instance.insert(parsed_json)

  def add_blacklist(blacklist_json: str):
    try:
      # Parse JSON from string
      parsed_json = json.loads(blacklist_json)
      # Validate the JSON against the 'blacklist' schema - throws if invalid.
      jsonschema.validate(instance=parsed_json, schema=self._blacklist_schema)
      # Submit validated JSON
      db_insert(parsed_json)
    except:
      e = sys.exc_info()[0]
      log.info(f"Invalid JSON submitted, got exception: {e}")
      raise e

  async def process_command(self, message: discord.Message):
    """ Take in a message and decide if it's a command,
        and do whatever we want afterwards """

    # Strip the message of Biggs mentions and split it into arguments
    args = re.findall(r'\{.+?\}|".+?"|\w+', self.remove_mention(message.content))

    # Select specific command
    # TODO: extract this into a separate module, or organize it some other way
    if args[0] == "addblacklist":
      log.debug("addblacklist invoked.")
      try:
        self.add_blacklist(args[1])
        await message.channel.send(f"Added new blacklist to database")
      except:
        e = sys.exc_info()[0]
        await message.channel.send(f"Failed to submit to database, got exception: {e}")
    else:
      await message.channel.send("I'm not sure what you mean.")

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

  async def on_message(self, message: discord.Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")

    try:
      # Check if we're being mentioned
      if self.mentioning_me(message):
        # Shrug off message if it's from another bot
        if message.author.bot: return
        # Process the message as a command
        await self.process_command(message)

    except Exception as exc: # FIXME
      log.error(exc, exc_info=True)
      raise exc
