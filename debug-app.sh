#!/bin/bash

echo "🔍 Debugging NewProjWiz App Launch..."

# Check if app bundle exists
if [ -d "dist/mac-arm64/NewProjWiz.app" ]; then
    echo "✅ App bundle found"
else
    echo "❌ App bundle not found"
    exit 1
fi

# Check if Next.js build exists
if [ -d ".next" ]; then
    echo "✅ Next.js build exists"
else
    echo "❌ Next.js build not found"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "NewProjWiz" 2>/dev/null || true
pkill -f "next start" 2>/dev/null || true

# Wait a moment
sleep 2

# Launch app with console output
echo "🚀 Launching app with debug output..."
echo "=================================="

# Use the development version to see console output
npm run electron-dev 