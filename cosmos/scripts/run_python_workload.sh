#!/bin/bash

# === CONFIGURATION ==="
PROJECT_DIR="/tmp/ycsb/ycsb-azurecosmos-binding-0.18.0-SNAPSHOT"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_SCRIPT="$PROJECT_DIR/CosmosClient.py"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
LOG_FILE="$PROJECT_DIR/python_cosmos.log"

PYTHON_ARGS="$@"

# === FUNCTIONS ===
create_venv_if_needed() {
  sudo apt install python3.8-venv --yes
  if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Virtual environment not found. Creating at $VENV_DIR..."
    sudo python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
      echo "❌ Failed to create virtual environment."
      exit 1
    fi
    echo "✅ Virtual environment created."
  else
    echo "✅ Virtual environment already exists."
  fi
}

install_requirements() {
  sudo apt-get install python3-pip --yes
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "📚 Installing dependencies from $REQUIREMENTS_FILE..."
    source "$VENV_DIR/bin/activate"
    sudo $(which pip3) install --upgrade pip
    sudo $(which pip3) install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
      echo "❌ Failed to install requirements."
      exit 1
    fi
    echo "✅ Dependencies installed."
  else
    echo "⚠️  No requirements.txt found at $REQUIREMENTS_FILE. Skipping dependency installation."
  fi
}

launch_script() {
  if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python script not found at $PYTHON_SCRIPT"
    exit 1
  fi

  echo "🚀 Launching $PYTHON_SCRIPT in background using venv..."

  source "$VENV_DIR/bin/activate"
  sudo $(which python3) "$PYTHON_SCRIPT" $PYTHON_ARGS > "$LOG_FILE" 2>&1 &
  PID=$!
  echo "✅ Script launched with PID $PID. Logging to $LOG_FILE"
}

# === EXECUTION ===
set -x
create_venv_if_needed
install_requirements
launch_script
set +x