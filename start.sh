#!/bin/bash

# Start script for the automation service

echo "Starting Flexitask Social Media Automation Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Start the service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
