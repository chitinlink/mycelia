from os import listdir
from random import choice

from discord import File, AllowedMentions
from discord.ext import commands

from lib.utils.etc import Cog
from lib.utils.checks import in_guild

from owoify import Owoifator
owo = Owoifator()

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

  @commands.command()
  async def owo(self, ctx: commands.Context):
    """ Small. """
    async for msg in ctx.history(limit=1, before=ctx.message):
      await ctx.message.delete()
      owomsg = owo.owoify(msg.content)

      if len(msg.embeds) > 0:
        embeds = msg.embeds
        for embed in embeds:
          if embed.title:       embed.title = owo.owoify(embed.title)
          if embed.description: embed.description = owo.owoify(embed.description)
          if embed.footer:
            embed.set_footer(
              text=owo.owoify(embed.footer.text),
              icon_url=embed.footer.icon_url
            )
          if embed.author:
            embed.set_author(
              name=owo.owoify(embed.author.name),
              icon_url=embed.footer.icon_url
            )
          for f in range(len(embed.fields)):
            embed.set_field_at(f,
              name=owo.owoify(embed.fields[f].name),
              value=owo.owoify(embed.fields[f].value)
            )

        await ctx.send(owomsg, embed=embeds[0], allowed_mentions=AllowedMentions.none())

        if len(embeds) > 1:
          for e in embeds[1:]:
            await ctx.send(embed=e, allowed_mentions=AllowedMentions.none())

      elif owomsg != msg.content:
        await ctx.send(owomsg, allowed_mentions=AllowedMentions.none())
