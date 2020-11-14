#!/usr/bin/env python3

"""
Usage:
  mycelia run       (biggs | smalls)
  mycelia install   (biggs | smalls | all)
  mycelia update    (biggs | smalls | all)
  mycelia uninstall (biggs | smalls | all)
  mycelia (-h | --help)
  mycelia (-v | --version)

Options:
  -h --help     Show this message.
  -v --version  Show version.
"""

# TODO figure out how to update lavalink easy
# TODO install/update etc stuff
# TODO sleuth this:
# geting this error:
# Unclosed client session
# client_session: <aiohttp.client.ClientSession object at 0x00000183E9CF2550>

import yaml
import os
import subprocess
from enum import Enum

from docopt import docopt

# Local dependencies
from lib.biggs import Biggs
from lib.smalls import Smalls
import logconfig

DIR = os.path.dirname(__file__)
VERSION = subprocess.check_output(
  "git rev-parse --short HEAD".split(" ")
).decode("utf-8").strip()

class Bot(Enum):
  """ Enum for the available bots. """
  BIGGS = "biggs"
  SMALLS = "smalls"

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
  print("Installing python requirements...")
  subprocess.run(list("pip3 install -r requirements.txt"))
  
  # Set systemd service WorkingDirectory to current dir
  print(f"Setting systemd working directory to {DIR}...")
  subprocess.run(list(f"sed -i \"s@^WorkingDirectory=.*@WorkingDirectory={DIR}@\" ./unit/{bot.value}.service"))

  # Link systemd service
  print("Linking systemd service...")
  subprocess.run(list(f"systemctl --user link ./unit/{bot.value}.service"))

  # Reload, enable & start
  print("Reloading systemd...")
  subprocess.run(list("systemctl --user daemon-reload"))
  print("Enabling and starting service...")
  subprocess.run(list(f"systemctl --user enable {bot.value}.service --now"))

  print("Done installing!")

def _uninstall(bot: Bot):
  # Stop and disable
  print("Stopping service...")
  subprocess.run(list(f"systemctl --user stop {bot.value}.service"))
  print("Disabling service...")
  subprocess.run(list(f"systemctl --user disable {bot.value}.service"))

  # Reload
  print("Reloading systemd...")
  subprocess.run(list("systemctl --user daemon-reload"))

  print("Done uninstalling!")

def _update(bot: Bot):
  # Uninstall
  print("Running uninstall script...")
  _uninstall(bot)

  # Discard changes
  print("Discarding changes...")
  # git checkout -- .

  # Pull latest
  print("Pulling latest version...")
  # git pull

  # Install
  print("Running install script...")
  _install(bot)

  print("Done updating!")

if __name__ == "__main__":
  os.makedirs("./data", exist_ok=True)

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
