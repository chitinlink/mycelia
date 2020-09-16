from discord.ext import commands

from lib.utils import in_dms

class Anon(commands.Cog):
  @commands.command()
  async def anon(self, ctx: commands.Context, *, msg: str):
    """ (DMs only) Send an anonymous message to the moderators """
    if in_dms(ctx):
      await ctx.bot._guild._notice_channel.send(
        f":eye_in_speech_bubble: {msg}"
      )
      await ctx.message.add_reaction(ctx.bot._reactions["confirm"])
    else:
      await ctx.message.add_reaction(ctx.bot._reactions["confused"])
      await ctx.send("This command is available only in DMs.", delete_after=10)
