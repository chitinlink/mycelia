#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Set everything here to executable
chmod +x *

# Link
sudo systemctl link ./biggs.service

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable biggs.service
