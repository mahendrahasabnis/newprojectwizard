#!/bin/bash

echo "🧪 Testing Simplified NewProjWiz..."

# Kill any existing processes
pkill -f "next start" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true

# Wait a moment
sleep 2

# Run the simplified version
echo "Starting simplified version..."
npx electron electron/main-simple.js 