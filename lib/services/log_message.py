import logging

from discord import Message
from discord.ext import commands

log = logging.getLogger("Biggs")
logging.addLevelName(15, "MESSAGE")
def msg(self, message, *args, **kws):
  self._log(15, message, args, **kws)
logging.Logger.msg = msg

@commands.Cog.listener()
async def log_message(message: Message):
  log.msg(f"{message.channel}§{message.author}: {message.content}")
