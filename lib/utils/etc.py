import logging
from discord.ext.commands import Context, Cog as dCog
from discord import Emoji, PartialEmoji, Reaction, Guild
from datetime import timedelta
from typing import Union

from lib.utils.text import plur

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

async def react(ctx: Context, reaction: Union[Emoji, Reaction, PartialEmoji, str]):
  """ Add reaction to given context. """
  if type(reaction) is str and reaction in ctx.bot._reactions:
    await ctx.message.add_reaction(ctx.bot._reactions[reaction])
  else:
    await ctx.message.add_reaction(reaction)

# revised from zekel's answer at SO:
# https://stackoverflow.com/a/5333305/12086004
def readable_delta(delta: timedelta) -> str:
  """ Returns a human-readable timedelta. """

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

class Cog(dCog):
  """ <discord.ext.commands.Cog> superclass that adds a log field.  """
  def __init__(self):
    self.log = logging.getLogger("Biggs")
    self.log.info(f"Loading service: {self.__class__.__name__}")
