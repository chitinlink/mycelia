#!/usr/bin/env python

import yaml
import gzip
from datetime import datetime
import logging
import logging.config
import os

# Local dependencies
from lib.biggs import Biggs

try:
  # Load config
  with open("biggs.yml", "r") as y:
    config = yaml.load(y, Loader=yaml.FullLoader) # type: dict

    path_latest = f"{config['logs_path']}latest.log"

    # Make sure logs dir exists
    if not os.path.exists(config["logs_path"]):
      os.makedirs(config["logs_path"])

    # Make sure logs/latest.log exists
    if not os.path.exists(path_latest):
      open(path_latest, "w", encoding="utf-8")

    # If logs/latest.log exists, archive it
    else:
      with open(path_latest, "r", encoding="utf8") as f:
        # Decide on path for the archived log
        # The date of the log is in the first line
        path = f"{config['logs_path']}{f.readline().strip()}"
        i = 0
        while True:
          if not os.path.exists(f"{path}-{i}.log.gz"):
            path += f"-{i}"
            break
          i += 1
        path += ".log.gz"

        # gzip file
        with open(path_latest, "rb") as _input, gzip.open(path, "wb") as _output:
          _output.writelines(_input)

    # Set up logging
    with open("logging.yml", "r", encoding="utf-8") as y:
      lconfig = yaml.load(y, Loader=yaml.FullLoader) # type: dict
      logging.config.dictConfig(lconfig)
    log = logging.getLogger("Biggs")

    # Write current date to file so we can reference it later when we archive it
    with open(path_latest, "w", encoding="utf-8") as f:
      f.write(datetime.now().strftime("%Y-%m-%d") + "\n")

    # Make sure data/ exists
    if not os.path.exists(f"{config['tinydb_path']}"):
      os.makedirs(f"{config['tinydb_path']}")
    # Make sure data/db.json exists
    if not os.path.exists(f"{config['tinydb_path']}db.json"):
      open(f"{config['tinydb_path']}db.json", "w", encoding="utf-8")

  # Create an instance of Biggs
  log.debug("Instanciating Biggs...")
  biggs = Biggs()

  # Start Biggs
  log.debug("Starting Biggs...")
  biggs.setup(config)

# Log exceptions
except Exception as exc: # FIXME
  log.error(exc, exc_info=True)

# And then exit
finally:
  log.info("Exiting")
  print(f"Log file available at ./logs/latest.log")
