from discord.ext import commands

from lib.utils.etc import Cog, react
from lib.utils.checks import in_dms, is_guild_member

class Anon(Cog):
  @commands.command()
  @commands.check(is_guild_member)
  async def anon(self, ctx: commands.Context, *, msg: str):
    """ (DMs only) Send an anonymous message to the moderators """
    if in_dms(ctx):
      await ctx.bot._notice_channel.send(
        f":eye_in_speech_bubble: {msg}"
      )
      await react(ctx, "confirm")
    else:
      await react(ctx, "confused")
      await ctx.send("This command is available only in DMs.", delete_after=10)
