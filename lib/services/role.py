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
    """ Manage your roles """
    if ctx.invoked_subcommand is None: pass

  @role.command(aliases=["a"])
  async def add(self, ctx, *, role: dRole):
    """ Assign yourself a role """
    await ctx.author.add_roles(role)
    await ctx.message.add_reaction(self.bot._reactions["confirm"])

  @role.command(aliases=["r"])
  async def remove(self, ctx, *, role: dRole):
    """ Remove a role you have """
    await ctx.author.remove_roles(role)
    await ctx.message.add_reaction(self.bot._reactions["confirm"])

  @add.error
  @remove.error
  async def addremove_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.message.add_reaction(self.bot._reactions["confused"])
      await ctx.send(error, delete_after=10)

  @role.command(aliases=["l"])
  async def list(self, ctx):
    """ List all the self-assignable and requestable roles """
    await ctx.send(
      "**List of self-assignable roles:**\n" +
      "\n".join([f"• `{role.name}`" for role in self._roles]) + "\n" +
      "If you'd like a role added (especially pronouns), ask a moderator!"
    )
