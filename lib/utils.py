from discord.ext.commands import Context

# Checks
def bot_is_ready(ctx: Context) -> bool:
  """ True if the bot is ready. Included in the message funnel. """
  return ctx.bot.is_ready()

def not_from_bot(ctx: Context) -> bool:
  """ Checks that the author for the given context is not a bot. Included in the message funnel. """
  return not ctx.author.bot

def not_ignored_channel(ctx: Context) -> bool:
  """ Checks that the given context is not in an ignored channel. Included in the message funnel. """
  return ctx.channel not in ctx.bot._ignored_channels

def in_guild(ctx: Context) -> bool:
  """ Checks if the given context is in the configured guild. """
  return ctx.guild == ctx.bot._guild

def in_dms(ctx: Context) -> bool:
  """ Checks if the given context is in DMs. """
  return ctx.guild is None

def is_mod(ctx: Context) -> bool:
  """ Checks whether or not the author for the given context is a moderator based on their roles """
  return len(
    set(map(lambda r: r.id, ctx.author.roles)) &
    set(ctx.bot._config["mod_roles"])
  ) > 0

# Text formatting
def md_quote(text: str) -> str:
  """ Prefixes every line of given `text` with a ">" """
  return "> " + text.replace("\n", "\n> ")

def md_list(lst: iter) -> str:
  """ Formats a list of strings into a consistent style """
  return "\n".join([f"• {i}" for i in lst])

def md_codeblock(block: str, lang: str = "") -> str:
  """ Markdown code block """
  return f"```{lang}\n{block}```"

def md_code(text: str) -> str:
  """ Markdown inline code """
  return f"`{text}`"

def md_spoiler(text: str) -> str:
  """
    Markdown spoiler inline block

    Note issue #30.
  """
  return f"||{text}||"
