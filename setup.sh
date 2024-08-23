#!/usr/bin/env bash

# Constants
VENV_NAME="jarvis_gemini"
VENV_PATH="venv"
REQUIREMENTS_FILE="requirements.txt"

# Activate the virtual environment
activate_venv() {
    source "$VENV_PATH/bin/activate"
}

# Deactivate the virtual environment
deactivate_venv() {
    deactivate &>/dev/null
}

# Install or update packages from requirements.txt
install_packages() {
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
}

# Create the virtual environment and install specified packages
create_venv() {
    echo "Creating Python virtual environment for Jarvis Gemini Assistant..."
    python3 -m venv "$VENV_PATH"
    activate_venv
    install_packages
    echo "Installation completed."
    deactivate_venv
}

# Update the virtual environment with new or updated packages
update_venv() {
    [[ -d "$VENV_PATH" ]] || { echo "Virtual environment does not exist, creating..."; create_venv; return; }
    echo "Updating Python virtual environment for Jarvis Gemini Assistant..."
    activate_venv
    install_packages
    echo "Update completed."
    deactivate_venv
}

# Check and create .env file if it doesn't exist
check_env_file() {
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        touch .env
        echo "Please fill in your API keys in the .env file before starting the application."
    fi
}

# Start the Flask application
start_app() {
    activate_venv
    echo "Starting the Jarvis Gemini Assistant web interface..."
    python app.py
    deactivate_venv
}

# Display help
display_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  -h, --help     Display this help message.
  -c, --create   Create a new Python virtual environment and install dependencies.
  -u, --update   Update the existing Python virtual environment.
  -r, --run      Start the Jarvis Gemini Assistant web interface.

Examples:
  $0 -h
  $0 -c
  $0 -r
EOF
}

# Parse command-line options
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -h|--help) display_help; exit 0 ;;
        -c|--create) create_venv; check_env_file; exit 0 ;;
        -u|--update) update_venv; check_env_file; exit 0 ;;
        -r|--run) check_env_file; start_app; exit 0 ;;
        *) echo "Invalid option: $1" >&2; display_help; exit 1 ;;
    esac
    shift
done

# If no arguments provided, show help
display_help