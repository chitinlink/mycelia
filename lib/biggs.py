# External dependencies
from tinydb import TinyDB
from discord import Intents
from discord.ext.commands import Context

# Local dependencies
from lib.proto import Proto
from lib.utils.checks import is_bot_ready, is_not_ignored_channel, is_not_from_bot
# Services
from lib.services.core import Core
from lib.services.role import Role
from lib.services.time import Time
from lib.services.anon import Anon
from lib.services.schedule import Schedule
from lib.services.reminder import Reminder
from lib.services.fun import Fun

class Biggs(Proto):
  def __init__(self, config: dict):
    # Intents
    # https://discordpy.readthedocs.io/en/stable/intents.html
    intents = Intents.default()
    # Need members intent for lib.utils.checks.is_guild_member
    intents.members = True
    super().__init__(config, intents=intents)

  async def _do_setup(self):
    # Internal props
    self._db = TinyDB(f"./data/biggs.json")
    self._guild = self.get_guild(self._config["guild_id"])
    self._notice_channel = self.get_channel(self._config["notice_channel_id"])
    self._ignored_channels = [self.get_channel(c) for c in self._config["ignored_channels"]]

    def parse_reactions(_id):
      if type(_id) == int: return self.get_emoji(_id)
      if type(_id) == str: return _id
      raise ValueError("Only str or int allowed in the reactions.")

    self._reactions = { key: parse_reactions(_id) for key, _id in self._config["reactions"].items() }

    # Services
    self.add_cog(Core(self))
    self.add_cog(Role(self))
    self.add_cog(Time(self))
    self.add_cog(Anon(self))
    self.add_cog(Schedule(self))
    self.add_cog(Reminder(self))
    self.add_cog(Fun(self))

  def funnel(self, ctx: Context) -> bool:
    return (
      is_bot_ready(ctx) and
      is_not_ignored_channel(ctx) and
      is_not_from_bot(ctx)
    )
