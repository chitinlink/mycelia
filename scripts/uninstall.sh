#!/usr/bin/env bash

# Stop and disable
sudo systemctl stop biggs.service
sudo systemctl disable biggs.service

# Unlink
sudo unlink /etc/systemd/system/biggs.service

# Reload
sudo systemctl daemon-reload
