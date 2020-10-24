from discord.ext.commands import Context
from datetime import timedelta
from typing import Union

# Constants
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Checks
def bot_is_ready(ctx: Context) -> bool:
  """ True if the bot is ready. Included in the message funnel. """
  return ctx.bot.is_ready()

def not_from_bot(ctx: Context) -> bool:
  """ Checks that the author for the given context is not a bot. Included in the message funnel. """
  return not ctx.author.bot

def not_ignored_channel(ctx: Context) -> bool:
  """ Checks that the given context is not in an ignored channel. Included in the message funnel. """
  return ctx.channel not in ctx.bot._ignored_channels

def in_guild(ctx: Context) -> bool:
  """ Checks if the given context is in the configured guild. """
  return ctx.guild == ctx.bot._guild

def in_dms(ctx: Context) -> bool:
  """ Checks if the given context is in DMs. """
  return ctx.guild is None

def is_mod(ctx: Context) -> bool:
  """ Checks whether or not the author for the given context is a moderator based on their roles """
  return len(
    set(map(lambda r: r.id, ctx.author.roles)) &
    set(ctx.bot._config["mod_roles"])
  ) > 0

async def is_guild_member(ctx: Context) -> bool:
  """ Intended for use in DMs, checks if author is a member of the guild """
  return await ctx.bot._guild.fetch_member(ctx.author.id)

# Text formatting
def md_quote(text: str) -> str:
  """ Prefixes every line of given `text` with a ">" """
  return "> " + text.replace("\n", "\n> ")

def md_list(lst: iter) -> str:
  """ Formats a list of strings into a consistent style """
  return "".join([md_list_item(i) for i in lst])

def md_list_item(text: str) -> str:
  """ Formats a single line of a consistent-style list """
  return f"• {text}\n"

def md_codeblock(block: str, lang: str = "") -> str:
  """ Markdown code block """
  return f"```{lang}\n{block}```"

def md_code(text: str) -> str:
  """ Markdown inline code """
  return f"`{text}`"

def md_spoiler(text: str) -> str:
  """
    Markdown spoiler inline block

    Note issue #30.
  """
  return f"||{text}||"

# Etc
async def react(ctx: Context, reaction: str):
  """ Add reaction to given context. """
  await ctx.message.add_reaction(ctx.bot._reactions[reaction])

# revised from zekel's answer at SO:
# https://stackoverflow.com/a/5333305/12086004
def readable_delta(delta: timedelta) -> str:
  """ Returns a human-readable timedelta. """

  def plur(num: int) -> str:
    return "" if num == 1 else "s"

  future = False
  if delta < timedelta(0):
    future = True
    delta = -delta

  delta_days = abs(delta.days)
  delta_seconds = abs(delta.seconds)
  delta_minutes = delta_seconds // 60
  delta_hours = delta_minutes // 60

  if delta_days:
    if delta_days > 364:
      delta_years = delta_days // 364
      out = f"{delta_years} year{plur(delta_years)}"
    elif delta_days > 30:
      delta_months = delta_days // 30
      out = f"{delta_months} month{plur(delta_months)}"
    else:
      out = f"{delta_days} day{plur(delta_days)}"
  elif delta_hours:
    out = f"{delta_hours} hour{plur(delta_hours)}"
  elif delta_minutes:
    out = f"{delta_minutes} minute{plur(delta_minutes)}"
  else:
    out = f"{delta_seconds} second{plur(delta_seconds)}"

  if future: return "in " + out
  else:      return out + " ago"
