# Project Wizard Desktop App

This guide shows you how to run the Project Wizard as a desktop application with a clickable icon.

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
```bash
npm run launch
```

### Option 2: Development Mode
```bash
npm run electron-dev
```

### Option 3: Manual Steps
```bash
# Build the Next.js app
npm run build

# Start the desktop app
npm run electron
```

## 📦 Create Desktop Installer

### For macOS
```bash
npm run electron-dist
```
This creates a `.dmg` file in the `dist` folder.

### For Windows
```bash
npm run electron-dist
```
This creates an `.exe` installer in the `dist` folder.

### For Linux
```bash
npm run electron-dist
```
This creates an `.AppImage` file in the `dist` folder.

## 🎯 Features

- **Native Desktop App**: Runs as a standalone application
- **Full Functionality**: All web features work in the desktop version
- **Menu Bar**: Native menu with shortcuts (Cmd+N for new project)
- **External Links**: Opens GitHub and Firebase links in your default browser
- **Auto-start Server**: Automatically starts the Next.js server when needed

## 🔧 How It Works

The desktop app:
1. Builds the Next.js application
2. Starts a local Next.js server on port 3000
3. Opens an Electron window pointing to `http://localhost:3000`
4. Provides native desktop features like menus and window management

## 📁 File Structure

```
├── electron/
│   └── main.js          # Electron main process
├── launch-electron.js    # Simple launcher script
├── package.json         # Contains Electron scripts
└── DESKTOP_README.md    # This file
```

## 🛠️ Troubleshooting

### App won't start
- Make sure you have Node.js installed
- Run `npm install` to install dependencies
- Check that port 3000 is available

### Build errors
- Clear the `.next` folder: `rm -rf .next`
- Rebuild: `npm run build`

### Permission errors (macOS)
- Go to System Preferences > Security & Privacy
- Allow the app to run if blocked

## 🎨 Customization

### Change App Icon
Replace `public/favicon.ico` with your own icon file.

### Change Window Size
Edit `electron/main.js` and modify the `width` and `height` values in the `BrowserWindow` options.

### Add Menu Items
Edit the `createMenu()` function in `electron/main.js` to add custom menu items.

## 📱 Distribution

After running `npm run electron-dist`, you'll find the installer in the `dist` folder:

- **macOS**: `Project Wizard-0.1.0.dmg`
- **Windows**: `Project Wizard Setup 0.1.0.exe`
- **Linux**: `Project Wizard-0.1.0.AppImage`

Users can install these files just like any other desktop application! 