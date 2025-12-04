#!/bin/bash
set -e

echo "Starting environment setup..."

# 1. Setup .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
else
    echo ".env already exists."
fi

# 2. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 3. Run tests
echo "Running tests..."
python -m pytest tests/

echo "Environment setup complete!"
