#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Set everything here to executable
chmod +x *

# Go back up, now we're in /
cd ..
# Install python packages
pip3 install -r requirements.txt

# Link
sudo systemctl link ./scripts/biggs.service

# Reload, enable, start
sudo systemctl daemon-reload
sudo systemctl enable biggs.service
sudo systemctl start biggs.service
