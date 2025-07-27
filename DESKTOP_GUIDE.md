# 🖥️ Project Wizard Desktop App Guide

Your Project Wizard can now run as a desktop application! Here are multiple ways to launch it with a click of an icon.

## 🚀 Quick Launch Options

### Option 1: Simple Command (Recommended)
```bash
npm run launch
```
This automatically builds and starts the desktop app.

### Option 2: Shell Script
```bash
./launch.sh
```
A simple shell script that checks dependencies and launches the app.

### Option 3: Development Mode
```bash
npm run electron-dev
```
Launches in development mode with hot reloading.

## 📱 Create Desktop Installer

### Build Installer for Your Platform
```bash
npm run electron-dist
```

This creates platform-specific installers:
- **macOS**: `.dmg` file
- **Windows**: `.exe` installer  
- **Linux**: `.AppImage` file

### Install the App
1. Run `npm run electron-dist`
2. Find the installer in the `dist` folder
3. Double-click to install
4. The app will appear in your Applications/Programs folder

## 🍎 macOS-Specific Options

### Create Clickable App (AppleScript)
```bash
osascript create-app.applescript
```
This creates a native macOS app in your Applications folder.

### Manual App Creation
1. Open Automator
2. Create a new "Application"
3. Add a "Run Shell Script" action
4. Set the script to: `cd /path/to/your/project && npm run launch`
5. Save as "Project Wizard.app" in Applications

## 🪟 Windows-Specific Options

### Create Shortcut
1. Right-click on desktop
2. Create new shortcut
3. Target: `cmd /c "cd /d C:\path\to\your\project && npm run launch"`
4. Name it "Project Wizard"

### Pin to Taskbar
1. Create the shortcut above
2. Right-click the shortcut
3. Select "Pin to taskbar"

## 🐧 Linux-Specific Options

### Create Desktop Entry
Create `~/.local/share/applications/project-wizard.desktop`:
```ini
[Desktop Entry]
Name=Project Wizard
Comment=Create new projects with Firebase and GitHub
Exec=/usr/bin/node /path/to/your/project/launch-electron.js
Icon=/path/to/your/project/public/favicon.ico
Terminal=false
Type=Application
Categories=Development;
```

### Make Executable
```bash
chmod +x ~/.local/share/applications/project-wizard.desktop
```

## 🎯 Features of the Desktop App

- **Native Window**: Looks and feels like a native app
- **Menu Bar**: Native menus with keyboard shortcuts
- **Full Functionality**: All web features work perfectly
- **External Links**: Opens GitHub/Firebase in your browser
- **Auto-start**: Automatically starts the server when needed
- **Cross-platform**: Works on macOS, Windows, and Linux

## 🔧 Troubleshooting

### App Won't Start
- Check if Node.js is installed: `node --version`
- Check if npm is installed: `npm --version`
- Make sure port 3000 is available
- Try clearing the build: `rm -rf .next && npm run build`

### Permission Errors (macOS)
- Go to System Preferences > Security & Privacy
- Click "Allow Anyway" for the app
- Or run: `sudo spctl --master-disable`

### Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear build cache: `rm -rf .next`
- Rebuild: `npm run build`

### Port Already in Use
- Kill processes on port 3000: `lsof -ti:3000 | xargs kill -9`
- Or change the port in `electron/main.js`

## 🎨 Customization

### Change App Icon
Replace `public/favicon.ico` with your own icon:
- **macOS**: `.icns` format (recommended)
- **Windows**: `.ico` format
- **Linux**: `.png` format

### Change Window Size
Edit `electron/main.js`:
```javascript
mainWindow = new BrowserWindow({
  width: 1200,  // Change this
  height: 800,  // Change this
  // ...
});
```

### Add Custom Menu Items
Edit the `createMenu()` function in `electron/main.js` to add your own menu items.

## 📦 Distribution

### For Team/Company Use
1. Build the installer: `npm run electron-dist`
2. Share the installer file from the `dist` folder
3. Users can install it like any other app

### For Public Distribution
1. Update version in `package.json`
2. Build installer: `npm run electron-dist`
3. Upload to your website or app store

## 🔄 Updates

To update the desktop app:
1. Make your changes to the code
2. Update version in `package.json`
3. Rebuild: `npm run electron-dist`
4. Distribute the new installer

## 💡 Pro Tips

- **Quick Access**: Pin the app to your dock/taskbar for instant access
- **Keyboard Shortcuts**: Use Cmd+N (macOS) or Ctrl+N (Windows/Linux) for new projects
- **Multiple Windows**: You can open multiple instances if needed
- **Background Mode**: The app keeps running in the background for faster subsequent launches

---

**🎉 You now have a fully functional desktop version of Project Wizard!** 