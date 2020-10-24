from os import listdir
from random import choice

from discord import File
from discord.ext import commands

from lib.utils import Cog, in_guild

class Fun(Cog):
  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  @commands.command()
  async def yoda(self, ctx: commands.Context):
    """ Yoda. """
    async with ctx.typing():
      with open("./assets/yoda_pics/" + choice(listdir("./assets/yoda_pics/")), "rb") as f:
        await ctx.send(file=File(f))
        await ctx.message.delete()
