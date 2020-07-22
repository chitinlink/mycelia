#!/usr/bin/env bash

# Stop and disable
echo "Stopping service..."
systemctl --user stop biggs.service
echo "Disabling service..."
systemctl --user disable biggs.service

# Reload
echo "Reloading systemd..."
systemctl --user daemon-reload

echo "Done uninstalling!"
