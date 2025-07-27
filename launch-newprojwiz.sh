#!/bin/bash

# NewProjWiz Desktop App Launcher
# This script launches the NewProjWiz desktop application

echo "🚀 Launching NewProjWiz Desktop App..."

# Check if the app bundle exists
if [ -d "dist/mac-arm64/NewProjWiz.app" ]; then
    echo "✅ Found NewProjWiz.app, launching..."
    open "dist/mac-arm64/NewProjWiz.app"
else
    echo "❌ NewProjWiz.app not found. Building first..."
    npm run electron-dist
    if [ -d "dist/mac-arm64/NewProjWiz.app" ]; then
        echo "✅ Build completed! Launching NewProjWiz..."
        open "dist/mac-arm64/NewProjWiz.app"
    else
        echo "❌ Failed to build NewProjWiz.app"
        exit 1
    fi
fi 