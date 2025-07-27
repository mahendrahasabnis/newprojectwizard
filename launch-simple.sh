#!/bin/bash

echo "🚀 Launching NewProjWiz (Simple Mode)..."

# Check if build exists
if [ ! -d ".next" ]; then
    echo "Building Next.js app first..."
    npm run build
fi

# Kill any existing processes
pkill -f "next start" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true

# Wait a moment
sleep 2

# Launch with the simple version
echo "Starting app..."
npx electron electron/main-simple.js 