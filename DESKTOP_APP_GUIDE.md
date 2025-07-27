# NewProjWiz Desktop App Guide

## 🚀 How to Launch NewProjWiz as a Desktop App

### Option 1: Quick Launch (Recommended)
```bash
./launch-newprojwiz.sh
```

### Option 2: Direct App Launch
```bash
open dist/mac-arm64/NewProjWiz.app
```

### Option 3: Build and Launch
```bash
npm run electron-dist
open dist/mac-arm64/NewProjWiz.app
```

## 📱 Making NewProjWiz a Permanent Desktop App

### Method 1: Add to Applications Folder
1. Copy the app to your Applications folder:
   ```bash
   cp -r dist/mac-arm64/NewProjWiz.app /Applications/
   ```
2. Now you can launch it from:
   - Applications folder
   - Spotlight (Cmd + Space, then type "NewProjWiz")
   - Dock (drag the app to your dock)

### Method 2: Create Desktop Shortcut
1. Right-click on your Desktop
2. Select "New Folder" and name it "NewProjWiz"
3. Copy the app into this folder:
   ```bash
   cp -r dist/mac-arm64/NewProjWiz.app ~/Desktop/NewProjWiz/
   ```

### Method 3: Add to Launchpad
1. Copy the app to Applications folder (see Method 1)
2. The app will automatically appear in Launchpad
3. You can also organize it into folders in Launchpad

## 🔧 Development Mode

For development with hot reloading:
```bash
npm run electron-dev
```

## 📦 Building for Distribution

### Create DMG Installer
```bash
npm run electron-dist
```

The DMG file will be created in `dist/mac-arm64/` and can be shared with others.

### Create App Bundle Only
```bash
npm run build
npm run electron
```

## 🎯 App Features

NewProjWiz is a desktop wizard that helps you:
- Create new projects from templates
- Set up Firebase projects
- Configure GitHub repositories
- Generate project configurations
- Set up development environments

## 🛠️ Troubleshooting

### App Won't Launch
1. Check if the build completed successfully
2. Try rebuilding: `npm run electron-dist`
3. Check console for errors: `npm run electron-dev`

### Port Issues
The app automatically finds available ports starting from 3000.

### Permission Issues
If you get permission errors, run:
```bash
chmod +x launch-newprojwiz.sh
```

## 📁 File Structure
```
newprojectwizard/
├── dist/mac-arm64/NewProjWiz.app    # Desktop app bundle
├── launch-newprojwiz.sh             # Quick launch script
├── electron/main.js                  # Electron main process
└── src/                             # Next.js app source
```

## 🎨 Customization

You can customize the app by:
- Changing the app name in `package.json`
- Updating the icon in `public/favicon.ico`
- Modifying the window size in `electron/main.js`
- Adding menu items in `electron/main.js` 