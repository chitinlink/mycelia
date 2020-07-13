#!/usr/bin/env python

import yaml
import gzip
from datetime import datetime
import logging
import logging.config
import os

import discord

from lib.biggs import Biggs

# Make sure logs/ exists
if not os.path.exists("./logs"): os.makedirs("logs")
# Make sure logs/latest.log exists
if not os.path.exists("./logs/latest.log"):
  open("./logs/latest.log", "w")
else: # If logs/latest.log exists, archive it
  with open("./logs/latest.log", "r") as f:
    # Decide on path for the archived log
    # The date of the log is in the first line
    path = f"./logs/{f.readline().strip()}"
    if os.path.exists(f"{path}.log.gz"):
      if os.path.exists(f"{path}-1.log.gz"):
        i = 2
        while True:
          if not os.path.exists(f"{path}-{i}.log.gz"):
            path += f"-{i}"
            break
          i += 1
      else:
        path += "-1"
    path += ".log.gz"

    # gzip file
    with open("./logs/latest.log", "rb") as _input, gzip.open(path, "wb") as _output:
      _output.writelines(_input)

# Write current date to file so we can reference it later when we archive it
with open("./logs/latest.log", "w") as f:
  f.write(datetime.now().strftime("%Y-%m-%d") + "\n")

# Logging
with open("logging.yml", "r") as y:
  config = yaml.load(y, Loader=yaml.FullLoader) # type: dict
  logging.config.dictConfig(config)
log = logging.getLogger("Biggs")

# Load config file and create an instance of Biggs
with open("biggs.yml", "r") as y:
  try:
    log.info("Loading biggs.yml...")
    config = yaml.load(y, Loader=yaml.FullLoader) # type: dict

    log.info("Instanciating Biggs...")
    biggs = Biggs()

    log.info("Starting Biggs...")
    biggs.setup(config)

  except Exception as exc: # FIXME
    log.error(exc)
    raise exc

  finally:
    log.info("Exiting")
    print(f"Log file available at ./logs/latest.log")
