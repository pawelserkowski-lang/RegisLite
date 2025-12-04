#!/bin/bash
set -e

# Setup .env if it doesn't exist
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests to verify setup
echo "Running tests..."
python3 -m pytest
