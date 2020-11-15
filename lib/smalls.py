# External dependencies
from discord.ext.commands import Context

# Local dependencies
from lib.proto import Proto
from lib.utils.checks import is_bot_ready, is_not_from_bot
# Services
from lib.services.core import Core
from lib.services.music import Music

class Smalls(Proto):
  async def _do_setup(self):
    self.add_cog(Core(self))
    self.add_cog(Music(self))

  def funnel(self, ctx: Context) -> bool:
    return (
      is_bot_ready(ctx) and
      is_not_from_bot(ctx)
    )
