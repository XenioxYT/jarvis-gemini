#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it and try again."
    exit 1
fi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install additional requirements for web interface
pip install flask flask-socketio

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    touch .env
    echo "Created .env file. Please fill in your API keys."
fi

# Create config.json if it doesn't exist
if [ ! -f config.json ]; then
    echo '{"enabled_tools": []}' > config.json
    echo "Created config.json file."
fi

# Start the web server within the virtual environment
python web_server.py