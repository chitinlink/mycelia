import logging

from discord import Role as dRole
from discord.ext import commands

from lib.utils import quote

class Role(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._roles = list(map(
      lambda id: self.bot._guild.get_role(id),
      self.bot._config["self_assignable_roles"]))

  @commands.group(aliases=["r"])
  async def role(self, ctx):
    if ctx.invoked_subcommand is None: pass

  @role.command(aliases=["a"])
  async def add(self, ctx, *, role: dRole):
    """ Assign yourself a role """
    if role in self._roles:
      await ctx.author.add_roles(role)

  @role.command(aliases=["r"])
  async def remove(self, ctx, *, role: dRole):
    """ Remove a role you have """
    if role in self._roles:
      await ctx.author.remove_roles(role)

  @role.command(aliases=["l"])
  async def list(self, ctx):
    """ List all the self-assignable and requestable roles """
    await ctx.send(
      "**List of self-assignable roles:**\n" +
      "\n".join([f"• `{role.name}`" for role in self._roles]) + "\n" +
      "If you'd like a role added (especially pronouns), ask a moderator!"
    )
