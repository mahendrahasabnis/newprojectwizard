#!/bin/bash

echo "🚀 Launching NewProjWiz (No Build Mode)..."

# Check if build exists
if [ ! -d ".next" ]; then
    echo "❌ Build not found. Please run: npm run build"
    exit 1
fi

# Kill any existing processes
pkill -f "next start" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true

# Wait a moment
sleep 2

# Launch with the no-build version
echo "Starting app..."
npx electron electron/main-no-build.js 