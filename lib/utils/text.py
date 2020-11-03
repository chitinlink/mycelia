from discord import Guild
from typing import Union

def fmt_quote(text: str) -> str:
  """ Prefixes every line of given `text` with a ">". """
  return "> " + text.replace("\n", "\n> ")

def fmt_list(lst: iter) -> str:
  """ Formats a list of strings into a consistent style. """
  return "".join([fmt_list_item(i) for i in lst])

def fmt_list_item(text: str) -> str:
  """ Formats a single line of a consistent-style list. """
  return f"• {text}\n"

def fmt_codeblock(block: str, lang: str = "") -> str:
  """ Markdown code block. """
  return f"```{lang}\n{block}```"

def fmt_code(text: str) -> str:
  """ Markdown inline code. """
  return f"`{text}`"

def fmt_spoiler(text: str) -> str:
  """
    Markdown spoiler inline block.

    Note issue #30.
  """
  return f"||{text}||"

def fmt_guild(guild: Guild) -> str:
  """ Formats a Guild into a consistent style. """
  return f"<{guild.id}> {guild.name} ({guild.member_count} member{fmt_plur(guild.member_count)})"

def fmt_plur(t: Union[int, list, dict]) -> str:
  """ PLuralizes based on quantity. """
  if type(t) is int  and t      != 1: return "s"
  if type(t) is list and len(t) != 1: return "s"
  if type(t) is dict and len(t) != 1: return "s"
  return ""
