#!/bin/bash

# NewProjWiz macOS App Installer
# This script installs the NewProjWiz app to the Applications folder

set -e

echo "📱 NewProjWiz macOS App Installer"
echo "=================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only"
    exit 1
fi

# Check if any app exists
FULL_WEB_APP="dist/NewProjWiz_FullWeb"
SIMPLE_WEB_APP="dist/NewProjWiz_SimpleWeb"
WEB_ONLY_APP="dist/NewProjWiz_WebOnly"
WEB_ONLY_DEBUG_APP="dist/NewProjWiz_WebOnly_debug"
REGULAR_APP="dist/NewProjWiz.app"
SIMPLE_APP="dist/NewProjWiz"

if [ -d "$FULL_WEB_APP" ]; then
    APP_PATH="$FULL_WEB_APP"
    APP_NAME="NewProjWiz_FullWeb"
    echo "✅ Found full web-only app at $APP_PATH (recommended - all features)"
elif [ -d "$SIMPLE_WEB_APP" ]; then
    APP_PATH="$SIMPLE_WEB_APP"
    APP_NAME="NewProjWiz_SimpleWeb"
    echo "✅ Found simple web-only app at $APP_PATH"
elif [ -d "$WEB_ONLY_APP" ]; then
    APP_PATH="$WEB_ONLY_APP"
    APP_NAME="NewProjWiz_WebOnly"
    echo "✅ Found web-only app at $APP_PATH"
elif [ -d "$WEB_ONLY_DEBUG_APP" ]; then
    APP_PATH="$WEB_ONLY_DEBUG_APP"
    APP_NAME="NewProjWiz_WebOnly_debug"
    echo "✅ Found web-only debug app at $APP_PATH"
elif [ -d "$REGULAR_APP" ]; then
    APP_PATH="$REGULAR_APP"
    APP_NAME="NewProjWiz"
    echo "✅ Found regular app at $APP_PATH"
elif [ -d "$SIMPLE_APP" ]; then
    APP_PATH="$SIMPLE_APP"
    APP_NAME="NewProjWiz"
    echo "✅ Found simple app at $APP_PATH"
else
    echo "❌ No app found in dist directory"
    echo "Please run one of the build scripts first:"
    echo "  python3 build_full_web.py (recommended - all features)"
    echo "  python3 build_simple_web.py"
    echo "  python3 build_web_only.py"
    echo "  python3 build_macos_app_simple.py"
    echo "  python3 build_macos_app.py"
    exit 1
fi

# Check if app is already installed
INSTALL_PATH="/Applications/$APP_NAME"
if [ -d "$INSTALL_PATH" ]; then
    echo "⚠️  $APP_NAME is already installed at $INSTALL_PATH"
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing installation..."
        sudo rm -rf "$INSTALL_PATH"
    else
        echo "❌ Installation cancelled"
        exit 1
    fi
fi

# Install the app
echo "📦 Installing $APP_NAME to Applications..."
sudo cp -r "$APP_PATH" "/Applications/"

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R root:wheel "/Applications/$APP_NAME"
sudo chmod -R 755 "/Applications/$APP_NAME"

echo "✅ $APP_NAME installed successfully!"
echo ""
echo "🎉 You can now launch $APP_NAME from:"
echo "   - Applications folder"
echo "   - Spotlight (Cmd+Space, then type '$APP_NAME')"
echo "   - Dock (drag from Applications to Dock)"
echo ""
if [ "$APP_NAME" = "NewProjWiz_WebOnly" ]; then
    echo "🌐 This is the web-only version that opens in your browser"
    echo "   It avoids PyQt6 crashes and provides the same functionality"
fi
echo ""
echo "📝 To uninstall later, simply drag $APP_NAME from Applications to Trash" 