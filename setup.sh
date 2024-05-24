#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Notify user of setup completion
echo "Setup complete. Don't forget to copy .env.example to .env and set your environment variables."
