import logging

from discord import Role as dRole
from discord.ext import commands

from lib.utils import md_list, md_code

class Role(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self._roles = list(map(
      lambda id: self.bot._guild.get_role(id),
      self.bot._config["self_assignable_roles"]))

  @commands.group(aliases=["r"])
  async def role(self, ctx: commands.Context):
    """ Manage your roles """
    if ctx.invoked_subcommand is None: await ctx.send_help("role")

  @role.command(aliases=["a"])
  async def add(self, ctx: commands.Context, *, role: dRole):
    """ Assign yourself a role """
    if role in self._roles:
      await ctx.author.add_roles(role)
      await ctx.message.add_reaction(self.bot._reactions["confirm"])
    else:
      await ctx.message.add_reaction(self.bot._reactions["confused"])
      await ctx.send("Role not available.", delete_after=10)

  @role.command(aliases=["r"])
  async def remove(self, ctx: commands.Context, *, role: dRole):
    """ Remove a role you have """
    if role in self._roles:
      if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await ctx.message.add_reaction(self.bot._reactions["confirm"])
      else:
        await ctx.message.add_reaction(self.bot._reactions["confused"])
        await ctx.send("You can't remove that role, because you don't have it.", delete_after=10)
    else:
      await ctx.message.add_reaction(self.bot._reactions["confused"])
      await ctx.send("Role not available.", delete_after=10)

  @add.error
  @remove.error
  async def addremove_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
      await ctx.message.add_reaction(self.bot._reactions["confused"])
      await ctx.send(error, delete_after=10)

  @role.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ List all the self-assignable and requestable roles """
    await ctx.send(
      "**List of self-assignable roles:**\n" +
      md_list(map(lambda r: md_code(r.name), self._roles)) + "\n" +
      "If you'd like a role added (especially pronouns), ask a moderator!"
    )
