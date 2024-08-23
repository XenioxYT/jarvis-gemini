#!/bin/bash

# Function to show a spinner
spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Update and upgrade system packages
echo "Updating and upgrading system packages..."
sudo apt update && sudo apt upgrade -y & spinner

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    sudo apt install -y python3 python3-pip python3-venv & spinner
fi

# Check if python is python3
if ! command -v python &> /dev/null || [ "$(python --version 2>&1)" != "$(python3 --version 2>&1)" ]; then
    echo "Setting up 'python' to point to 'python3'..."
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1 & spinner
fi

# Create and activate virtual environment
echo "Creating and activating virtual environment..."
python3 -m venv venv & spinner
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip & spinner

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt & spinner

# Install additional requirements for web interface
echo "Installing additional requirements for web interface..."
pip install flask flask-socketio & spinner

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
echo "Starting the web server..."
source venv/bin/activate  # Ensure the venv is activated
python web_server.py