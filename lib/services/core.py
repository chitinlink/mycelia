import subprocess
import logging

from discord import Guild, Message
from discord.ext import commands

from lib.utils.etc import Service
from lib.utils.text import fmt_guild

log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

class Core(Service):
  @commands.command(name="version", aliases=["v", "hello"])
  async def version_command(self, ctx: commands.Context):
    """ Display current bot version. """
    _date = subprocess.check_output(
      "git log -1 --date=relative --format=%ad".split(" ")
    ).decode("utf-8").strip()
    await ctx.send(
      f"{ctx.bot._reactions['header']} Biggs (commit `{ctx.bot.version}`) — Last updated {_date}"
    )

  # Log guild movements
  async def on_guild_join(self, guild: Guild):
    log.info(f"Biggs has joined the guild {fmt_guild(guild)}.")

  async def on_guild_remove(self, guild: Guild):
    log.info(f"Biggs has been removed from the guild {fmt_guild(guild)}.")

  async def on_guild_update(self, before: Guild, after: Guild):
    if before.name != after.name:
      log.info(f"The guild {before.name} has been renamed to {after.name}.")

  # Log messages
  async def on_message(self, message: Message):
    log.msg(f"{message.channel}§{message.author}: {message.content}")
    await self.process_commands(message)

  # Log errors
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
    name = error.__class__.__name__
    if isinstance(error, (
      commands.CheckFailure,
      commands.DisabledCommand,
      commands.CommandNotFound,
      commands.CommandOnCooldown)):
      log.warning(f"{name}: {error}")
    else:
      log.error(f"Command error ({name}): {error}")
