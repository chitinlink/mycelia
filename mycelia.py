#!/usr/bin/env python3

"""
Usage:
  mycelia.py run       (biggs | smalls)
  mycelia.py install   (biggs | smalls | all)
  mycelia.py update    (biggs | smalls | all)
  mycelia.py uninstall (biggs | smalls | all)
  mycelia.py (-h | --help)
  mycelia.py (-v | --version)

Options:
  -h --help     Show this message.
  -v --version  Show version.
"""

# TODO figure out how to update lavalink easy
# TODO ensure were on the right dir

import os
import pathlib
from typing import List
from re import sub
import subprocess
import yaml
from shlex import split
from enum import Enum

from docopt import docopt

# Local dependencies
from lib.biggs import Biggs
from lib.smalls import Smalls
import logconfig

DIR = pathlib.Path(__file__).parent.absolute()
VERSION = subprocess.check_output(
  "git rev-parse --short HEAD".split(" ")
).decode("utf-8").strip()

class Bot(Enum):
  """ Enum for the available bots. """
  BIGGS = "biggs"
  SMALLS = "smalls"

UNIT = \
  "[Unit]\n" \
  "Description={title} (Discord bot)\n" \
  "\n" \
  "[Service]\n" \
  "Type=simple\n" \
  "WorkingDirectory={dir}\n" \
  "ExecStart=/bin/bash -c 'python3 ./mycelia.py run {name}'\n" \
  "Restart=on-failure\n" \
  "RestartSec=10\n" \
  "Environment=PYTHONUNBUFFERED=1\n" \
  "\n" \
  "[Install]\n" \
  "WantedBy=multi-user.target"

def sh(cmds: str) -> List[subprocess.CompletedProcess]:
  return [subprocess.run(split(line)) for line in cmds.strip().split("\n")]

def _run(bot: Bot):
  # Load config
  if not os.path.exists("settings.yml"):
    print("./settings.yml missing, exiting.")
    exit()
  with open("settings.yml", "r") as y:
    config = yaml.load(y, Loader=yaml.FullLoader) # type: dict

  # Set up logging
  if bot == Bot.BIGGS: log = logconfig.l_biggs
  elif bot == Bot.SMALLS: log = logconfig.l_smalls
  else: exit() # I hate my linter

  try:
    log.info(f"Commit {VERSION}")

    # Instantiate the bot
    if bot == Bot.BIGGS: Biggs(config["biggs"])
    elif bot == Bot.SMALLS: Smalls(config["smalls"])

  except KeyboardInterrupt: pass
  finally:
    log.info("Exiting")

def _install(bot: Bot):
  print(f"Installing {bot.value}")
  sh("""
    chmod +x ./mycelia.py
    pip3 install -r requirements.txt""")

  with open(f"./unit/{bot.value}.service", "w") as f:
    f.write(UNIT.format(title=bot.value.title(), name=bot.value, dir=DIR))

  sh(f"""
    systemctl --user link ./unit/{bot.value}.service
    systemctl --user daemon-reload
    systemctl --user enable {bot.value}.service --now""")

def _uninstall(bot: Bot):
  print(f"Uninstalling {bot.value}")

  sh(f"""
    systemctl --user stop {bot.value}.service
    systemctl --user disable {bot.value}.service
    systemctl --user daemon-reload""")

  if pathlib.Path(f"./unit/{bot.value}.service").is_file():
    os.remove(f"./unit/{bot.value}.service")

def _update(bot: Bot):
  print(f"Updating {bot.value}")

  _uninstall(bot)
  sh("""
    git checkout -- .
    git pull""")
  _install(bot)

if __name__ == "__main__":
  os.makedirs("./data", exist_ok=True)
  os.makedirs("./unit", exist_ok=True)

  args = docopt(__doc__, version=VERSION)

  if args["run"]:
    if args["biggs"]: _run(Bot.BIGGS)
    if args["smalls"]: _run(Bot.SMALLS)
  elif args["install"]:
    if args["all"] or args["biggs"]: _install(Bot.BIGGS)
    if args["all"] or args["smalls"]: _install(Bot.SMALLS)
  elif args["uninstall"]:
    if args["all"] or args["biggs"]: _uninstall(Bot.BIGGS)
    if args["all"] or args["smalls"]: _uninstall(Bot.SMALLS)
  elif args["update"]:
    if args["all"] or args["biggs"]: _update(Bot.BIGGS)
    if args["all"] or args["smalls"]: _update(Bot.SMALLS)
