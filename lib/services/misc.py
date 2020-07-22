import logging
import subprocess

from discord import Message
from discord.ext import commands

log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

@commands.Cog.listener()
async def log_message(message: Message):
  log.msg(f"{message.channel}§{message.author}: {message.content}")

@commands.command(aliases=["v", "hello"])
async def version(ctx):
  _hash = subprocess.check_output(
    "git rev-parse --short HEAD".split(" ")
  ).decode("utf-8").strip()
  _date = subprocess.check_output(
    "git log -1 --date=relative --format=%ad".split(" ")
  ).decode("utf-8").strip()
  await ctx.send(
    f"Biggs (commit `{_hash}`) -- Last updated {_date}"
  )
