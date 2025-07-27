#!/bin/bash

# NewProjWiz Python Wizard Launcher for macOS
# This file can be double-clicked to launch the wizard

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Launching NewProjWiz Python Wizard..."
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Launch the wizard
echo "✅ Starting NewProjWiz..."
python3 python_wizard.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ An error occurred. Check the output above."
    read -p "Press Enter to exit..."
fi 