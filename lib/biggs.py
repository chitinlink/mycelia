#!/usr/bin/env python

import logging
import json

# External dependencies
import discord
from tinydb import TinyDB, Query

# Logging
log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws): self._log(15, message, args, **kws)
logging.Logger.msg = msg

def check_prefix(command_prefix: str, message: str):
  return message.startswith(command_prefix)

def remove_prefix(command_prefix: str, message: str):
  return message.replace(command_prefix, "")

class Biggs(discord.Client):
  def setup(self, config: dict):
    self._tinydb_instance   = TinyDB(f"{config['tinydb_path']}db.json")
    self._server_id         = config["server_id"] # type: int
    self._notice_channel_id = config["notice_channel_id"] # type: int

    self.run(config["token"])

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

  async def process_command(self, message: discord.Message):
    """ Take in a message and decide if it's a command,
        and do whatever we want afterwards """

    # Strip the message of Biggs mentions and split it into arguments
    args = self.remove_mention(message.content).split()

    # Select specific command
    # TODO: extract this into a separate module, or organize it some other way
    if args[0] == "inserttest":
      log.debug("inserttest invoked.")
      self.db_insert(remove_prefix("inserttest", self.remove_mention(message.content)))
      await message.channel.send("Added to the database.")
    else:
      await message.channel.send("I'm not sure what you mean.")

  def mentioning_me(self, message: discord.Message) -> bool:
    """ Returns true if Biggs is mentioned in the given message. """
    return self.user in message.mentions

  def remove_mention(self, message: str) -> str:
    """ Intended to be used on messages mentioning Biggs,
        removes the mention(s) and returns the remaining text. """
    return message.replace(f"<@!{self.user.id}>", "").strip()

  def db_insert(self, message_contents: str):
    parsed_json = json.loads(message_contents)
    self._tinydb_instance.insert(parsed_json)
