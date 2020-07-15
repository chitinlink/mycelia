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
    self._db = TinyDB(f"{config['tinydb_path']}db.json")

    self._blacklist_member_schema = json.load(open("./lib/schema/blacklist_member.json"))

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

  def add_blacklist_member(self, blacklist_member: str):
    try:
      print(blacklist_member)
      # Parse JSON from string
      data = json.loads(blacklist_member)
      # Validate the JSON against the "blacklist" schema - throws if invalid.
      jsonschema.validate(instance=data, schema=self._blacklist_member_schema)
      # Submit validated JSON
      self._db.table("blacklist").insert(data)
    except Exception as exc:
      log.error(exc)
      raise exc

  async def process_command(self, message: discord.Message):
    """ Take in a message and decide if it"s a command,
        and do whatever we want afterwards """

    # Strip the message of Biggs mentions and split it into arguments
    args = re.findall(r'\{.*\}|".+?"|\w+', self.remove_mention(message.content))

    # TODO: extract this into a separate module, or organize it some other way
    # Select specific command
    if args[0] == "blacklist" and args[1] == "add":
      log.debug("Command \"blacklist add\" invoked.")
      try:
        self.add_blacklist_member(args[2])
        await message.channel.send(f"Added to blacklist")
      except Exception as exc:
        log.error(exc)
        await message.channel.send(f"Failed to submit to database, got exception: {exc}")
        raise exc
    else:
      await message.channel.send("I'm not sure what you mean.")

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

  async def on_message(self, message: discord.Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")

    try:
      # Ignore unless it's in the correct server.
      if message.guild.id == self._guild_id:
        # Check if we're being mentioned
        # and it's not from another bot
        if self.mentioning_me(message) and not message.author.bot:
          # Process the message as a command
          await self.process_command(message)

    except Exception as exc: # FIXME
      log.error(exc, exc_info=True)
      raise exc
