from os import listdir
from random import choice

from discord import File, AllowedMentions, Message
from discord import NotFound
from discord.ext import commands

from lib.utils.etc import Service
from lib.utils.checks import in_guild, is_not_from_bot

from owoify import Owoifator
owo = Owoifator()

class Fun(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot

    self.bot.add_listener(self.combo, "on_message")

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  @commands.command()
  async def yoda(self, ctx: commands.Context):
    """ Yoda. """
    async with ctx.typing():
      with open("./assets/yoda_pics/" + choice(listdir("./assets/yoda_pics/")), "rb") as f:
        await ctx.send(file=File(f))
        try: await ctx.message.delete()
        except NotFound as exc: pass

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

  async def combo(self, msg: Message):
    authors = [msg.author.id]
    contents = [(msg.content, msg.embeds)]
    async for message in msg.channel.history(before=msg, limit=4):
      authors.append(message.author.id)
      contents.append((message.content, message.embeds))

    # The previous 5 messages were the exact same, and all by different people.
    if (
      list(set(authors)) == authors and
      self.bot.user.id not in set(authors) and
      len(set(contents)) == 1
    ):
      self.log.info("Combo-ing.")
      # Join in
      await msg.channel.send(msg.content, embed=msg.embeds[0])
