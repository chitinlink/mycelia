import subprocess

from discord import Guild, Message
from discord.ext import commands

from lib.utils.etc import Service
from lib.utils.text import fmt_guild

class Core(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__(bot)

    self.bot.add_listener(self.log_message, "on_message")
    self.bot.add_listener(self.log_command_error, "on_command_error")
    self.bot.add_listener(self.log_guild_join, "on_guild_join")
    self.bot.add_listener(self.log_guild_remove, "on_guild_remove")
    self.bot.add_listener(self.log_guild_update, "on_guild_update")

  @commands.command(name="version", aliases=["v", "hello"])
  async def version_command(self, ctx: commands.Context):
    """ Display current bot version. """
    _date = subprocess.check_output(
      "git log -1 --date=relative --format=%ad".split(" ")
    ).decode("utf-8").strip()
    await ctx.send(
      f"Mycelia (commit `{ctx.bot.version}`) — Last updated {_date}\n" \
      f":minidisc: <https://github.com/technoabyss/mycelia>"
    )

  # Log guild movements
  async def log_guild_join(self, guild: Guild):
    self.log.info(f"{self.bot.user} has joined the guild {fmt_guild(guild)}.")

  async def log_guild_remove(self, guild: Guild):
    self.log.info(f"{self.bot.user} has been removed from the guild {fmt_guild(guild)}.")

  async def log_guild_update(self, before: Guild, after: Guild):
    if before.name != after.name:
      self.log.info(f"The guild {before.name} has been renamed to {after.name}.")

  # Log messages
  async def log_message(self, message: Message):
    self.log.msg(f"{message.guild.id}@{message.channel.id}§{message.author}: {message.content}")

  # Log errors
  async def log_command_error(self, ctx: commands.Context, error: commands.CommandError):
    name = error.__class__.__name__
    if isinstance(error, (
      commands.CheckFailure,
      commands.DisabledCommand,
      commands.CommandNotFound,
      commands.CommandOnCooldown)):
      self.log.warning(error)
    else:
      self.log.error(f"{name}: {error}")
