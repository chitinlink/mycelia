from subprocess import check_output
import logging

from discord.ext.commands import Bot, Context
from discord import Intents

from lib.utils.text import fmt_guild

class Proto(Bot):
  """
    Superclass for bots.
    Please define a `do_setup` method.
  """
  def __init__(self, config: dict, *, intents: Intents = Intents.default()):
    super().__init__(command_prefix=config["command_prefix"], intents=intents)

    self.log = logging.getLogger(self.__class__.__name__)

    self.version = check_output(
      "git rev-parse --short HEAD".split(" ")
    ).decode("utf-8").strip()

    self._config = config
    self._done_setup = False

    self.run(config["token"])

  async def on_ready(self):
    if not self._done_setup:
      try: await self._do_setup()
      except Exception as exc:
        self.log.error(exc)
        exit()
      self._done_setup = True
    # Done loading
    self.log.info("Initial setup done.")

    self.log.info(f"Logged in as {self.user}, a member of these guilds:")
    for guild in self.guilds:
      self.log.info(f"• {fmt_guild(guild)}")

  def funnel(self, ctx: Context) -> bool:
    """
      "Command funnel" - Override this with any number of checks that must
      pass for commands to not be ignored.
    """
    return True

  # Global check
  async def bot_check(self, ctx: Context) -> bool:
    # Log all commands invoked
    self.log.info(f"Command invoked: {ctx.command.qualified_name}")
    return self.funnel(ctx)
