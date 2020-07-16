def quote(msg: str) -> str:
  """ Prefixes every line of given `msg` with a ">" """
  return "> " + msg.replace("\n", "\n> ")
