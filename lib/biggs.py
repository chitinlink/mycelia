import logging
import json
import subprocess
from typing import Any

# External dependencies
import discord
import jsonschema
from tinydb import TinyDB, where
from discord.ext import tasks, commands

# Local dependencies
from lib.utils import fmt_guild, bot_is_ready, not_ignored_channel, not_from_bot
# Services
from lib.services.blacklist import Blacklist
from lib.services.role import Role
from lib.services.time import Time
from lib.services.anon import Anon
from lib.services.schedule import Schedule
from lib.services.reminder import Reminder
from lib.services.fun import Fun

# Logging
log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

# Intents
# https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
# Need members intent for lib.utils.is_guild_member
intents.members = True

class Biggs(commands.Bot):
  def __init__(self, config: dict, *bot_args):
    super().__init__(command_prefix=config["command_prefix"], intents=intents, *bot_args)

    self.version = subprocess.check_output(
      "git rev-parse --short HEAD".split(" ")
    ).decode("utf-8").strip()

    self._config = config
    self._done_setup = False

    self._db = TinyDB(f"{config['tinydb_path']}db.json")

    self.run(config["token"])

  async def on_ready(self):
    if not self._done_setup:
      # Internal props
      self._guild = self.get_guild(self._config["guild_id"])
      self._notice_channel = self.get_channel(self._config["notice_channel_id"])
      self._ignored_channels = [self.get_channel(c) for c in self._config["ignored_channels"]]

      def parse_reactions(_id):
        if type(_id) == int: return self.get_emoji(_id)
        if type(_id) == str: return _id
        raise ValueError("Only str or int allowed in the reactions.")

      self._reactions = { key: parse_reactions(_id) for key, _id in self._config["reactions"].items() }

      # Services
      self.add_cog(Blacklist(self))
      self.add_cog(Role(self))
      self.add_cog(Time())
      self.add_cog(Anon())
      self.add_cog(Schedule(self))
      self.add_cog(Reminder(self))
      self.add_cog(Fun())

      self._done_setup = True
      log.info("Initial setup done.")

    # Done loading
    log.info(f"Logged on as {self.user}!")

    log.info("Biggs is a member of these guilds:")
    for guild in self.guilds:
      log.info(f"• {fmt_guild(guild)}")

  # Log guild movements
  async def on_guild_join(self, guild: discord.Guild):
    log.info(f"Biggs has joined the guild {fmt_guild(guild)}.")

  async def on_guild_remove(self, guild: discord.Guild):
    log.info(f"Biggs has been removed from the guild {fmt_guild(guild)}.")

  async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
    if before.name != after.name:
      log.info(f"The guild {before.name} has been renamed to {after.name}.")

  # Log messages
  async def on_message(self, message: discord.Message):
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

  # Global check
  async def bot_check(self, ctx: commands.Context) -> bool:
    # Log all commands invoked
    log.info(f"Command invoked: {ctx.command.qualified_name}")
    # Ensure all of these basic checks pass
    return (
      bot_is_ready(ctx) and
      not_ignored_channel(ctx) and
      not_from_bot(ctx)
    )

  @commands.command(name="version", aliases=["v", "hello"])
  async def version_command(self, ctx: commands.Context):
    """ Display current bot version. """
    _date = subprocess.check_output(
      "git log -1 --date=relative --format=%ad".split(" ")
    ).decode("utf-8").strip()
    await ctx.send(
      f"{ctx.bot._reactions['header']} Biggs (commit `{self.version}`) — Last updated {_date}"
    )
