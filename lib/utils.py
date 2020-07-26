def md_quote(msg: str) -> str:
  """ Prefixes every line of given `msg` with a ">" """
  return "> " + msg.replace("\n", "\n> ")

def md_list(lst: iter) -> str:
  """ Formats a list of strings into a consistent style """
  out = ""
  for i in lst: out += f"• {i}\n"
  return out[:-1]
