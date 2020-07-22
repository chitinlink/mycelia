#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Set everything here to executable
chmod +x *

# Go up, now we're in /
cd ..
# Install python packages
pip3 install -r requirements.txt

# Link systemd service
systemctl --user link ./scripts/biggs.service

# Reload, enable & start
systemctl daemon-reload
systemctl enable biggs.service --now
