#!/usr/bin/env bash

# Make sure we're in /scripts/
cd "${0%/*}"

# Uninstall
echo "Running uninstall script..."
sh ./uninstall.sh

# Go back up
cd ..

# Discard changes
echo "Discarding changes..."
git checkout -- .

# Pull latest
echo "Pulling latest version..."
git pull

# Install
echo "Running install script..."
sh ./scripts/install.sh

echo "Done updating!"
