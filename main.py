#!/usr/bin/env python3

import yaml
import gzip
from datetime import datetime
import logging
import logging.config
import os
import subprocess

# Local dependencies
from lib.biggs import Biggs

# Load config
if not os.path.exists("biggs.yml"):
  print("./biggs.yml missing, exiting.")
  exit()
else:
  with open("biggs.yml", "r") as y:
    config = yaml.load(y, Loader=yaml.FullLoader) # type: dict

path_latest = f"{config['logs_path']}latest.log"

# Make sure logs dir exists
if not os.path.exists(config["logs_path"]):
  os.makedirs(config["logs_path"])

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
v = subprocess.check_output(
  "git rev-parse --short HEAD".split(" ")
).decode("utf-8").strip()

# Write current date to file so we can reference it later when we archive it
with open(path_latest, "w", encoding="utf-8") as f:
  f.write(datetime.utcnow().strftime("%Y-%m-%d") + "\n")

# Make sure data/ exists
if not os.path.exists(config["tinydb_path"]):
  os.makedirs(config["tinydb_path"])

# Create an instance of Biggs
log.info(f"Biggs commit {v}")
biggs = Biggs(config)

log.info("Exiting")
print(f"Log file available at ./logs/latest.log")
