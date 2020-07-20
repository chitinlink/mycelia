#!/usr/bin/env bash

# Stop
sudo systemctl stop biggs.service

# Then pull
git pull

# Then resume
sudo systemctl start biggs.service
