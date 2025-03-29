#!/bin/bash
# Helper script to run the AIPyCraft application using the virtual environment

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define the path to the virtual environment's Python executable
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

# Check if the virtual environment's Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment Python not found at $VENV_PYTHON"
    echo "Please run the installation script (install.sh) first."
    exit 1
fi

# Execute the main application script using the virtual environment's Python
echo "Running AIPyCraft..."
"$VENV_PYTHON" "$SCRIPT_DIR/main.py" "$@"

exit $?
