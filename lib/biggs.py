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

    # blacklist
    if args[0] == "blacklist":
      if len(args) >= 2:

        # blacklist add
        if args[1] == "add":
          log.debug("Command \"blacklist add\" invoked.")
          try:
            self.add_blacklist_member(args[2])
            await message.channel.send(f"Added to blacklist")
          except jsonschema.exceptions.ValidationError as exc:
            await message.channel.send(f"Error: {exc.message}")
          except json.decoder.JSONDecodeError as exc:
            await message.channel.send(f"Error: {exc.msg}")

        # blacklist list
        elif args[1] == "list":
          log.debug("Command \"blacklist list\" invoked.")
          msg = "**Blacklist:**\n\n"
          for i in self._db.table("blacklist").all():
            msg += f"`{i['name']}`   "
          msg += "\n\nUse `blacklist view <entry>` for details."
          await message.channel.send(msg)

        # blacklist view
        elif args[1] == "view":
          log.debug("Command \"blacklist view\" invoked.")
          if len(args) >= 3:

            q = self._db.table("blacklist").get(Query().name == args[2])

            long = ""
            if len(args) >= 4 and args[3] == "long":
              long += "\nLong reason:\n"
              long += q['reason']['long']
            else:
              long += f"\nUse `blacklist view {q['name']} long` to view the long reason."

            if q != "":
              aliases = "/".join(q['aliases'])
              short = q['reason']['short']
              await message.channel.send(
                f"**`{q['name']}`** aka {aliases}\n" +
                f"Short reason: {short}" +
                long
              )
            else:
              await message.channel.send("No such user.\nTry `blacklist list` first.")
          else:
            await message.channel.send("Syntax: `blacklist view <entry> [long]`")

      else:
        await message.channel.send(
          "Available `blacklist` commands:\n" +
          "• `blacklist add <json>`\n" +
          "• `blacklist list [page number]`\n" +
          "• `blacklist view <entry> [long]`"
        )
    else:
      await message.channel.send(
        "Available commands:\n" +
        "• `blacklist`"
      )

  async def post_notice(self, message: str):
    await self._notice_channel.send(message)

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

    self._guild = self.get_guild(self._config["guild_id"])
    self._notice_channel = self.get_channel(self._config["notice_channel_id"])

    # await self.post_notice("Hello")

  async def on_message(self, message: discord.Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")

    # Ignore unless it's in the correct server, and not from a bot (incl. Biggs)
    if message.guild == self._guild and not message.author.bot:
      # Check if we're being mentioned
      if self.mentioning_me(message):
        # Process the message as a command
        await self.process_command(message)
