#!/bin/bash
# Wrapper to activate virtual environment

VENV_DIR="/home/qwkj/drass/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found at $VENV_DIR"
    echo "Run: bash /home/qwkj/drass/deployment/scripts/setup-venv.sh"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Export Python path
export PYTHON="$VENV_DIR/bin/python"
export PIP="$VENV_DIR/bin/pip"

echo "Virtual environment activated"
echo "Python: $(which python)"
echo "Version: $(python --version)"
