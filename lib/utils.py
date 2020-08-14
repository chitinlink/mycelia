def md_quote(text: str) -> str:
  """ Prefixes every line of given `text` with a ">" """
  return "> " + text.replace("\n", "\n> ")

def md_list(lst: iter) -> str:
  """ Formats a list of strings into a consistent style """
  return [f"• {i}\n" for i in lst][:-1]

def md_codeblock(block: str, lang: str = "") -> str:
  """ Markdown code block """
  return f"```{lang}\n{block}```"

def md_spoiler(text: str) -> str:
  """
    Markdown spoiler inline block

    Note issue #30.
  """
  return f"||{text}||"
