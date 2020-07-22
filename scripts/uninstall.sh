#!/usr/bin/env bash

# Stop and disable
systemctl --user stop biggs.service
systemctl --user disable biggs.service

# Reload
systemctl --user daemon-reload
