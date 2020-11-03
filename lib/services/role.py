import logging

from discord import Role as dRole
from discord.ext import commands
from tinydb import where

from lib.utils.etc import Service, react
from lib.utils.checks import is_mod, in_guild
from lib.utils.text import fmt_list, fmt_code

class Role(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self._roles = bot._db.table("roles")

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  @commands.group(aliases=["r"])
  async def role(self, ctx: commands.Context):
    """ Manage your roles. """
    if ctx.invoked_subcommand is None: await ctx.send_help("role")

  @role.command(aliases=["a"])
  async def add(self, ctx: commands.Context, *, role: dRole):
    """ Assign yourself a role. """
    if self._roles.search(where("id") == role.id):
      await ctx.author.add_roles(role)
      await react(ctx, "confirm")
    else:
      await react(ctx, "confused")
      await ctx.send("Role not available.", delete_after=10)

  @role.command(aliases=["r"])
  async def remove(self, ctx: commands.Context, *, role: dRole):
    """ Remove a role you have. """
    if self._roles.search(where("id") == role.id):
      if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await react(ctx, "confirm")
      else:
        await react(ctx, "confused")
        await ctx.send("You can't remove that role, because you don't have it.", delete_after=10)
    else:
      await react(ctx, "confused")
      await ctx.send("Role not available.", delete_after=10)

  @role.command(aliases=["reg"])
  @commands.check(is_mod)
  async def register(self, ctx: commands.Context, *, role: dRole):
    """ (Restricted to moderators) Register a role. """
    if self._roles.search(where("id") == role.id):
      await react(ctx, "confused")
      await ctx.send("Role already registered.", delete_after=10)
    else:
      self._roles.insert({ "id": role.id })
      await react(ctx, "confirm")

  @role.command(aliases=["dereg"])
  @commands.check(is_mod)
  async def deregister(self, ctx: commands.Context, *, role: dRole):
    """ (Restricted to moderators) Deregister a role. """
    if self._roles.search(where("id") == role.id):
      self._roles.remove(where("id") == role.id)
      await react(ctx, "confirm")
    else:
      await react(ctx, "confused")
      await ctx.send("Role not registered.", delete_after=10)

  @add.error
  @remove.error
  async def addremove_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
      await react(ctx, "confused")
      await ctx.send(error, delete_after=10)

  @register.error
  @deregister.error
  async def regdereg_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
      await react(ctx, "confused")
      await ctx.send(error, delete_after=10)

  @role.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ List all the self-assignable roles """
    await ctx.send(
      "**List of self-assignable roles:**\n" +
      fmt_list(map(lambda r: fmt_code(ctx.bot._guild.get_role(r["id"]).name), self._roles)) + "\n" +
      "If you'd like a role added (especially pronouns), ask a moderator!"
    )
