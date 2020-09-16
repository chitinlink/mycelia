from discord.ext.commands import Context

# Checks
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
