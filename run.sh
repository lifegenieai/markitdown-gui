#!/bin/bash

echo "Starting MarkItDown Converter..."

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment and run the app
source venv/bin/activate && python app.py