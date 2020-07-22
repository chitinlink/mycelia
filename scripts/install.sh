#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Set everything here to executable
echo "Setting everything in ./scripts +x"
chmod +x *

# Go up, now we're in /
cd ..

# Install python packages
echo "Installing python requirements..."
pip3 install -r requirements.txt

# Set systemd service WorkingDirectory to current dir
echo "Setting systemd working directory to ${PWD}..."
sed -i "s@^WorkingDirectory=.*@WorkingDirectory=${PWD}@" ./scripts/biggs.service

# Link systemd service
echo "Linking systemd service..."
systemctl --user link ./scripts/biggs.service

# Reload, enable & start
echo "Reloading systemd..."
systemctl --user daemon-reload
echo "Enabling and starting service..."
systemctl --user enable biggs.service --now

echo "Done installing!"
