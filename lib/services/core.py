import logging
import subprocess

from discord import Message
from discord.ext import commands

log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

def funnel(bot, message: Message):
  # Ignore if the bot isn't ready
  if bot.is_ready():
    # Ignore unless it's in the correct server (which implies also not a DM)
    if message.guild == bot._guild:
      # Ignore unless:
      if (
        # It's not from a bot (incl. Biggs)
        not message.author.bot and
        # and it's not in an ignored channel
        message.channel not in bot._ignored_channels
      ): return True
  return False

class Core(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

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
      f"{self.bot._reactions['header']} Biggs (commit `{_hash}`) — Last updated {_date}"
    )

  # Global check
  async def bot_check(self, ctx: commands.Context) -> bool:
    # Log all commands invoked
    log.info(f"Command invoked: {ctx.command.qualified_name}")
    # Pass all commands through the funnel
    return funnel(self.bot, ctx.message)

  @commands.Cog.listener(name="on_message")
  async def log_message(self, message: Message):
    # Log messages
    log.msg(f"{message.channel}§{message.author}: {message.content}")

  @commands.Cog.listener(name="on_command_error")
  async def log_error(self, ctx: commands.Context, error: commands.CommandError):
    log.warning(f"Command error ({error.__class__.__name__}): {error}")
