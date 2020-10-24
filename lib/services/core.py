import logging
import subprocess

from discord import Message
from discord.ext import commands

from lib.utils import Cog, bot_is_ready, not_ignored_channel, not_from_bot

logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

class Core(Cog):
  @commands.command(aliases=["v", "hello"])
  async def version(self, ctx: commands.Context):
    """ Display current bot version. """
    _hash = subprocess.check_output(
      "git rev-parse --short HEAD".split(" ")
    ).decode("utf-8").strip()
    _date = subprocess.check_output(
      "git log -1 --date=relative --format=%ad".split(" ")
    ).decode("utf-8").strip()
    await ctx.send(
      f"{ctx.bot._reactions['header']} Biggs (commit `{_hash}`) — Last updated {_date}"
    )

  # Global check
  async def bot_check(self, ctx: commands.Context) -> bool:
    # Log all commands invoked
    self.log.info(f"Command invoked: {ctx.command.qualified_name}")
    # Ensure all of these basic checks pass
    return (
      bot_is_ready(ctx) and
      not_ignored_channel(ctx) and
      not_from_bot(ctx)
    )

  @commands.Cog.listener(name="on_message")
  async def log_message(self, message: Message):
    # Log messages
    self.log.msg(f"{message.channel}§{message.author}: {message.content}")

  @commands.Cog.listener(name="on_command_error")
  async def log_error(self, ctx: commands.Context, error: commands.CommandError):
    name = error.__class__.__name__
    if isinstance(error, (commands.CheckFailure, commands.DisabledCommand, commands.CommandNotFound, commands.CommandOnCooldown)):
      self.log.warning(f"{name}: {error}")
    else:
      self.log.error(f"Command error ({name}): {error}")
