import logging
import json
import re

from discord import Message
from discord.ext import commands
from tinydb import where
import jsonschema

from lib.utils import md_quote
from lib.services.core import funnel

class Blacklist(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self._blacklist = self.bot._db.table("blacklist")
    self._blacklist_member_schema = json.load(open("./lib/schema/blacklist_member.json"))

  # You must be a moderator to run any of these commands
  async def cog_check(self, ctx: commands.Context):
    return self.bot.is_mod(ctx.author)

  # Commands
  @commands.group(aliases=["bl"])
  async def blacklist(self, ctx: commands.Context):
    """ Restricted to moderators """
    if ctx.invoked_subcommand is None: await ctx.send_help("blacklist")

  @blacklist.command(aliases=["a"])
  async def add(self, ctx: commands.Context, *, member_json: str):
    """ Adds an entry to the blacklist """

    try:
      # Parse JSON from string
      data = json.loads(member_json)
      # Validate the JSON against the "blacklist" schema - throws if invalid.
      jsonschema.validate(instance=data, schema=self._blacklist_member_schema)
      # Submit validated JSON
      self._blacklist.insert(data)

      await ctx.message.add_reaction(self.bot._reactions["confirm"])
      await ctx.send(f"Added `{data['name']}` to blacklist")

    except (jsonschema.exceptions.ValidationError, json.decoder.JSONDecodeError) as exc:
      await ctx.message.add_reaction(self.bot._reactions["deny"])
      if exc.__class__ == json.decoder.JSONDecodeError: msg = exc
      else:                                             msg = exc.message
      await ctx.send(f"JSON Error: {msg}")

  @blacklist.command(aliases=["v"])
  async def view(self, ctx: commands.Context, entry: str):
    """ View entry in the blacklist """

    q = self._blacklist.get(where("name") == entry)

    if q:
      aliases = ", ".join(q["aliases"])
      short = q["reason"]["short"]
      handles = ""
      if "handles" in q:
        handles += "**Known handles:**\n"
        for h in q['handles']:
          _type = h["type"]
          value = h["handle"]
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


      await ctx.send(
        f"**`{q['name']}`** aka {aliases}\n" +
        md_quote(
          handles +
          f"**Short reason:** {short}\n" +
          "**Long reason:**||\n" +
          f"{q['reason']['long']}||"
        )
      )
    else:
      await ctx.message.add_reaction(self.bot._reactions["confused"])
      await ctx.send("No such user.\nTry `blacklist list` first.")

  @blacklist.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ List everything in the blacklist """

    msg = "**Blacklist:**\n\n"
    for i in self._blacklist.all():
      msg += f"`{i['name']}`   "
    msg += "\n\nUse `blacklist view <entry>` for details."

    await ctx.send(msg)

  # Message scanner
  @commands.Cog.listener("on_message")
  async def scan_message(self, message: Message):
    # Run the message through the funnel first
    if funnel(self.bot, message):
      # Make sure it's not a blacklist command
      ctx = await self.bot.get_context(message)
      if not (ctx.command and ctx.command.qualified_name == "blacklist"):

        matches = []

        # For each blacklist entry...
        for member in self._blacklist.all():
          # ...For each of its handles...
          if "handles" in member:
            for h in member["handles"]:
              # ...If none of the handles match the message, skip
              _type = h["type"]
              value = h["handle"]
              if _type == "url":
                if not re.search(value, message.content): continue
              elif _type == "regex":
                if not re.compile(value).match(message.content): continue
              elif _type == "twitter":
                if not (re.search(
                  re.compile(f"((https?://)?(mobile.)?twitter.com/)?{value[1:]}|{value}"),
                  message.content
                )): continue
              elif _type == "tumblr":
                if not (
                  re.search(value, message.content) or
                  re.search(f"(https?://)?{value}.tumblr(.com)?", message.content) or
                  re.search(f"(https?://)?(www.)?tumblr.com/blog/view/{value}", message.content)
                ): continue
              # Otherwise add to matches
              matches.append(member)

        # Search for *all* documents...
        matches += self._blacklist.search(
          # where any of their aliases match any of the words in the message.
          # ("words" is loosely defined by the regex below,
          #  which is supposed to catch usernames mostly)
          where("aliases").any(re.findall(r"([\w'_]+)", message.content))
        )

        # Unique values only
        matches = list({ e["name"]: e for e in matches }.values())

        # If there are any matches:
        if matches:
          await self.bot.post_notice(
            kind="scan_match",
            data=matches,
            original_message=message)
