#!/bin/bash
# Installation script for Ubuntu on WSL (Windows 11)

echo "Starting AIPyCraft Installation..."

# Check if requirements.txt exists
echo "Checking for requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found in the current directory."
    exit 1
fi

# Check for python3-venv package
echo "Checking for python3-venv package..."
dpkg -s python3-venv &> /dev/null
if [ $? -ne 0 ]; then
    echo "python3-venv package not found. Attempting to install..."
    sudo apt update
    sudo apt install -y python3-venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install python3-venv. Please install it manually and re-run this script."
        exit 1
    fi
    echo "python3-venv installed successfully."
fi

# Create Python virtual environment
echo "Creating Python virtual environment (venv)..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment. Make sure Python 3 and python3-venv are correctly installed."
    exit 1
fi

# Install dependencies using the virtual environment's pip
echo "Installing dependencies from requirements.txt..."
venv/bin/python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies from requirements.txt. Check the output above for details."
    exit 1
fi

echo
echo "Installation complete."
echo "You can now run the application using: bash run.sh"
echo "(This script automatically uses the correct Python environment)."
echo
echo "Alternatively, to activate the environment manually, run: source venv/bin/activate"
echo
exit 0
