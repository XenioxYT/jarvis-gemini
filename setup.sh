#!/bin/bash

# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    sudo apt install -y python3 python3-pip python3-venv
fi

# Check if python is python3
if ! command -v python &> /dev/null || [ "$(python --version 2>&1)" != "$(python3 --version 2>&1)" ]; then
    echo "Setting up 'python' to point to 'python3'..."
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
fi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

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