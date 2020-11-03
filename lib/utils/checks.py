from discord.ext.commands import Context

def is_bot_ready(ctx: Context) -> bool:
  """ True if the bot is ready. Included in the command funnel. """
  return ctx.bot.is_ready()

def is_not_from_bot(ctx: Context) -> bool:
  """ Checks that the author for the given context is not a bot. Included in the command funnel. """
  return not ctx.author.bot

def is_not_ignored_channel(ctx: Context) -> bool:
  """ Checks that the given context is not in an ignored channel. Included in the command funnel. """
  return ctx.channel not in ctx.bot._ignored_channels

def in_guild(ctx: Context) -> bool:
  """ Checks if the given context is in the configured guild. """
  return ctx.guild == ctx.bot._guild

def in_dms(ctx: Context) -> bool:
  """ Checks if the given context is in DMs. """
  return ctx.guild is None

def is_mod(ctx: Context) -> bool:
  """ Checks whether or not the author for the given context is a moderator based on their roles. """
  return len(
    set(map(lambda r: r.id, ctx.author.roles)) &
    set(ctx.bot._config["mod_roles"])
  ) > 0

async def is_guild_member(ctx: Context) -> bool:
  """ Intended for use in DMs, checks if author is a member of the guild. """
  return await ctx.bot._guild.fetch_member(ctx.author.id)
