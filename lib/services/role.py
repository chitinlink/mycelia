from discord import Role as dRole, AllowedMentions
from discord.ext import commands
from tinydb import where

from lib.utils.etc import Service, react
from lib.utils.checks import is_mod, in_guild
from lib.utils.text import fmt_list

class Role(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__(bot)
    self._roles = bot._db.table("roles")

    self.bot.add_listener(self.catch_role_delete, "on_guild_role_delete")

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  async def catch_role_delete(self, role: dRole):
    if self._roles.search(where("id") == role.id):
      self._roles.remove(where("id") == role.id)
      await self.bot.notice_channel.send(f":x: Previously registered role deleted: {role.name} ({role.id})")

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
      await ctx.message.reply("Role not available.", delete_after=10, mention_author=False)

  @role.command(aliases=["r"])
  async def remove(self, ctx: commands.Context, *, role: dRole):
    """ Remove a role you have. """
    if self._roles.search(where("id") == role.id):
      if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await react(ctx, "confirm")
      else:
        await react(ctx, "confused")
        await ctx.reply("You can't remove that role, because you don't have it.", delete_after=10, mention_author=False)
    else:
      await react(ctx, "confused")
      await ctx.reply("Role not available.", delete_after=10, mention_author=False)

  @role.command(aliases=["reg"])
  @commands.check(is_mod)
  async def register(self, ctx: commands.Context, *, role: dRole):
    """ (Restricted to moderators) Register a role. """
    if self._roles.search(where("id") == role.id):
      await react(ctx, "confused")
      await ctx.reply("Role already registered.", delete_after=10, mention_author=False)
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
      await ctx.reply("Role not registered.", delete_after=10, mention_author=False)

  @add.error
  @remove.error
  async def addremove_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
      await react(ctx, "confused")
      await ctx.reply(error, delete_after=10, mention_author=False)

  @register.error
  @deregister.error
  async def regdereg_error(self, ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
      await react(ctx, "confused")
      await ctx.reply(error, delete_after=10, mention_author=False)

  @role.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ List all the self-assignable roles """
    roles = \
      map(lambda r: ctx.bot._guild.get_role(r["id"]).mention,
        self._roles)
    await ctx.send(
      "**List of self-assignable roles:**\n" +
      fmt_list(roles) + "\n" +
      "If you'd like a role added (especially pronouns), ask a moderator!",
      allowed_mentions=AllowedMentions.none()
    )
