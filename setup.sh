#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists, if not create it
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
    echo "Please fill in your API keys in the .env file before starting the application."
fi

# Start the Flask application
echo "Starting the Jarvis Gemini Assistant web interface..."
python app.py

# Deactivate the virtual environment when the script exits
trap "deactivate" EXIT