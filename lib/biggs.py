#!/usr/bin/env python

import logging
import json
import re
import sys
from math import ceil

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
    self._config = config
    self._db = TinyDB(f"{config['tinydb_path']}db.json")

    self._blacklist_member_schema = json.load(open("./lib/schema/blacklist_member.json"))

    self.run(config["token"])

  def mentioning_me(self, message: discord.Message) -> bool:
    """ Returns true if Biggs is mentioned in the given message. """
    return self.user in message.mentions

  def remove_mention(self, message: str) -> str:
    """ Intended to be used on messages mentioning Biggs,
        removes the mention(s) and returns the remaining text. """
    return message.replace(f"<@!{self.user.id}>", "").strip()

  def add_blacklist_member(self, blacklist_member: str):
    # Parse JSON from string
    data = json.loads(blacklist_member)
    # Validate the JSON against the "blacklist" schema - throws if invalid.
    jsonschema.validate(instance=data, schema=self._blacklist_member_schema)
    # Submit validated JSON
    self._db.table("blacklist").insert(data)

  async def process_command(self, message: discord.Message):
    """ Take in a message and decide if it"s a command,
        and do whatever we want afterwards """

    # Strip the message of Biggs mentions and split it into arguments
    args = re.findall(r'\{.*\}|".+?"|\w+', self.remove_mention(message.content))

    # TODO: extract this into a separate module, or organize it some other way
    # TODO: check if user is allowed to use the command
    # Select specific command
    if args[0] == "blacklist":
      if len(args) >= 2:
        if args[1] == "add":
          log.debug("Command \"blacklist add\" invoked.")
          try:
            self.add_blacklist_member(args[2])
            await message.channel.send(f"Added to blacklist")
          except jsonschema.exceptions.ValidationError as exc:
            await message.channel.send(f"Error: {exc.message}")
          except json.decoder.JSONDecodeError as exc:
            await message.channel.send(f"Error: {exc.msg}")
        elif args[1] == "list":
          log.debug("Command \"blacklist list\" invoked.")
          page = 0
          if len(args) >= 3:
            try: page = int(args[2]) - 1 # try to interpret argument 2 as a number
            except ValueError: pass # otherwise just shrug it off
          bl = self._db.table("blacklist").all()
          msg = f"**Blacklist page {page + 1}/{ceil(len(bl) / 10)}:**\n"
          for i in bl[page * 10 :(page + 1) * 10]:
            name = i['name']
            aliases = "/".join(i['aliases'])
            reason = i['reason']['short']
            msg += f"**`{name}`**: {aliases} - {reason}\n"
          await message.channel.send(msg)
      else:
        await message.channel.send(
          "Available **blacklist** commands:\n" +
          "• blacklist add <json>\n"
          "• blacklist list [page number]\n"
        )
    else:
      await message.channel.send("I'm not sure what you mean.")

  async def post_notice(self, message: str):
    await self._notice_channel.send(message)

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

    self._guild = self.get_guild(self._config["guild_id"])
    self._notice_channel = self.get_channel(self._config["notice_channel_id"])

    # await self.post_notice("Hello")

  async def on_message(self, message: discord.Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")

    # Ignore unless it's in the correct server.
    if message.guild == self._guild:
      # Check if we're being mentioned
      # and it's not from another bot
      if self.mentioning_me(message) and not message.author.bot:
        # Process the message as a command
        await self.process_command(message)
