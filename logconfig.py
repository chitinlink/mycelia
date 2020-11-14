import os
import logging
import logging.handlers
import colorlog
from sys import stdout

FMT_BASIC = "{asctime} {name:<16} {levelname:<8} {message}"
FMT_COLOR = "{blue}{asctime}{reset} {name:<16} {log_color}{levelname:<8}{reset} {message}"
FMT_DATETIME = "[%Y/%m/%d-%H:%M:%S]"
MAXSIZE = (1024 ** 2) * 5 # 5MB I think?
BACKUPCOUNT = 10

# Make sure ./logs exists
os.makedirs("./logs", exist_ok=True)

# Custom "MESSAGE" log level
logging.MESSAGE = 15
logging.addLevelName(logging.MESSAGE, "MESSAGE")
def msg(self, message, *args, **kws):
  if self.isEnabledFor(logging.MESSAGE):
    self._log(logging.MESSAGE, message, args, **kws)
logging.Logger.msg = msg
logging.Logger.message = logging.Logger.msg

# Formatters
fmt_basic = logging.Formatter(
  fmt=FMT_BASIC, datefmt=FMT_DATETIME, style="{")
fmt_color = colorlog.ColoredFormatter(
  fmt=FMT_COLOR, datefmt=FMT_DATETIME, style="{",
  log_colors={
		"DEBUG":    "cyan",
    "MESSAGE":  "white",
		"INFO":     "green",
		"WARNING":  "yellow",
		"ERROR":    "red",
		"CRITICAL": "red,bg_white",
	},
)

# Handlers
hnd_console = logging.StreamHandler(stream=stdout)
hnd_console.setFormatter(fmt_color)

hnd_file_biggs = logging.handlers.RotatingFileHandler(
  filename="./logs/biggs.log", encoding="utf-8",
  maxBytes=MAXSIZE, backupCount=BACKUPCOUNT
)
hnd_file_biggs.setFormatter(fmt_basic)

hnd_file_smalls = logging.handlers.RotatingFileHandler(
  filename="./logs/smalls.log", encoding="utf-8",
  maxBytes=MAXSIZE, backupCount=BACKUPCOUNT
)
hnd_file_smalls.setFormatter(fmt_basic)

# Loggers
l_discord = logging.getLogger("discord")
l_biggs = logging.getLogger("Biggs")
l_smalls = logging.getLogger("Smalls")

l_discord.setLevel(logging.INFO)
l_biggs.setLevel(logging.DEBUG)
l_smalls.setLevel(logging.DEBUG)

l_biggs.addHandler(hnd_console)
l_smalls.addHandler(hnd_console)
l_discord.addHandler(hnd_console)

l_biggs.addHandler(hnd_file_biggs)
l_discord.addHandler(hnd_file_biggs)

l_smalls.addHandler(hnd_file_smalls)
l_discord.addHandler(hnd_file_smalls)

if __name__ == "__main__":
  print("This file is not meant to be ran.")
  exit()
