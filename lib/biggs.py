#!/usr/bin/env python

import logging
import json
import re
import sys
from math import ceil
from typing import Any
from functools import reduce

# Local dependencies
from lib.utils import quote

# External dependencies
import discord
import jsonschema
from tinydb import TinyDB, where

# Logging
log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws): self._log(15, message, args, **kws)
logging.Logger.msg = msg

class Biggs(discord.Client):
  def setup(self, config: dict):
    self._config = config

    self._db = TinyDB(f"{config['tinydb_path']}db.json")
    self._blacklist = self._db.table("blacklist")

    self._blacklist_member_schema = json.load(open("./lib/schema/blacklist_member.json"))

    self.run(config["token"])

  def mentioning_me(self, message: discord.Message) -> bool:
    """ Returns true if Biggs is mentioned in the given message. """
    return self.user in message.mentions

  def remove_mention(self, message: str) -> str:
    """ Intended to be used on messages mentioning Biggs,
        removes the mention(s) and returns the remaining text. """
    return message.replace(f"<@!{self.user.id}>", "").strip()

  def add_blacklist_member(self, blacklist_member: str) -> object:
    # Parse JSON from string
    data = json.loads(blacklist_member)
    # Validate the JSON against the "blacklist" schema - throws if invalid.
    jsonschema.validate(instance=data, schema=self._blacklist_member_schema)
    # Submit validated JSON
    self._blacklist.insert(data)
    # Return the JSON
    return data

  async def process_command(self, message: discord.Message):
    """ Take in a message and decide if it"s a command,
        and do whatever we want afterwards """

    # Strip the message of Biggs mentions and split it into arguments
    args = re.findall(r'\{.*\}|".+?"|\w+', self.remove_mention(message.content))

    # TODO: extract this into a separate module, or organize it some other way
    # TODO: check if user is allowed to use the command
    # Select specific command

    # blacklist
    if len(args) >= 1:
      if args[0] == "blacklist":
        if len(args) >= 2:

          # blacklist add
          if args[1] == "add":
            log.info("Command \"blacklist add\" invoked.")
            try:
              member = self.add_blacklist_member(args[2])
              await message.channel.send(f"Added `{member['name']}` to blacklist")
            except jsonschema.exceptions.ValidationError as exc:
              await message.channel.send(f"Error: {exc.message}")
            except json.decoder.JSONDecodeError as exc:
              await message.channel.send(f"Error: {exc.msg}")

          # blacklist list
          elif args[1] == "list":
            log.info("Command \"blacklist list\" invoked.")
            msg = "**Blacklist:**\n\n"
            for i in self._blacklist.all():
              msg += f"`{i['name']}`   "
            msg += "\n\nUse `blacklist view <entry>` for details."
            await message.channel.send(msg)

          # blacklist view
          elif args[1] == "view":
            log.info("Command \"blacklist view\" invoked.")
            if len(args) >= 3:

              q = self._blacklist.get(where("name") == args[2])

              long = ""
              if len(args) >= 4 and args[3] == "long":
                long += "\n**Long reason:**\n"
                long += q['reason']['long']
              else:
                long += f"\nUse `blacklist view {q['name']} long` to view the long reason."

              if q != "":
                aliases = "/".join(q['aliases'])
                short = q['reason']['short']
                handles = ""
                if "handles" in q:
                  handles += "**Known handles:**\n"
                  for h in q['handles']:
                    _type = list(h)[0]
                    value = h[list(h)[0]]
                    handles += "• "
                    if _type == "url":
                      handles += f"<{value}>"
                    elif _type == "regex":
                      handles += f"Regular expression: `{value}`"
                    elif _type == "twitter":
                      handles += f"{value} - <https://twitter.com/{value[1:]}>"
                    elif _type == "tumblr":
                      handles += f"<https://{value}.tumblr.com> / <https://www.tumblr.com/dashboard/blog/{value}>"
                    handles += "\n"

                await message.channel.send(
                  f"**`{q['name']}`** aka {aliases}\n" +
                  quote(
                    handles +
                    f"**Short reason:** {short}" +
                    long
                  )
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
    else:
      await message.channel.send("What?")

  async def scan_message(self, message: discord.Message):

    matches = []

    # For each blacklist entry...
    for member in self._blacklist.all():
      # ...For each of its handles...
      if "handles" in member:
        for h in member["handles"]:
          # ...If none of the handles match the message, skip
          _type = list(h)[0]
          value = h[list(h)[0]]
          if _type == "url":
            if not re.search(value, message.content): continue
          elif _type == "regex":
            if not re.compile(value).match(message.content): continue
          elif _type == "twitter":
            if not (
                    re.search(value, message.content) or
                    re.search(f"https://www.twitter.com/{value[1:]}", message.content)
                  ): continue
          elif _type == "tumblr":
            if not (
                    re.search(value, message.content) or
                    re.search(f"https://{value}.tumblr.com", message.content) or
                    re.search(f"https://www.tumblr.com/dashboard/blog/{value}", message.content)
                  ): continue
          # Otherwise add to matches
          matches.append(member)

    # Search for *all* documents...
    matches += self._blacklist.search(
      # ... where any of their aliases...
      where("aliases").any(
        # ... match any of the words in the message.
        # ("words" is loosely defined by the regex below,
        #  which is supposed to catch usernames mostly)
        re.findall(r"([\w'_]+)", message.content)
      )
    )

    # Unique values only
    matches = list({ e["name"]: e for e in matches }.values())

    # If there are any matches:
    if matches:
      await self.post_notice(kind="scan_match", data=matches, original_message=message)

  async def post_notice(self, kind: str = "plain", original_message: discord.Message = None, data: Any = None):
    # Plain message
    if kind == "plain":
      await self._notice_channel.send(data)

    # Scan match
    elif kind == "scan_match":
      names = "/".join(map(lambda m: f"`{m['name']}`", data))

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

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

    self._guild = self.get_guild(self._config["guild_id"])
    self._notice_channel = self.get_channel(self._config["notice_channel_id"])

    # await self.post_notice(kind="plain", data="I'm ready.")

  async def on_message(self, message: discord.Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")

    # Ignore if the bot isn't ready
    if self.is_ready():
      # Ignore unless it's in the correct server, and not from a bot (incl. Biggs)
      if message.guild == self._guild and not message.author.bot:
        # Check if we're being mentioned
        if self.mentioning_me(message):
          # Process the message as a command
          await self.process_command(message)
        else: #if message.channel != self._notice_channel:
          # Scan the message (unless it's in the notice channel)
          await self.scan_message(message)
