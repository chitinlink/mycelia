#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Set everything here to executable
chmod +x *

# Soft link
sudo systemctl link /etc/systemd/system/biggs.service

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable biggs.service
