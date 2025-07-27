# Project Wizard

A full-stack Next.js 15 application that automates creating new projects by cloning a private GitHub repo, renaming identifiers, creating Firebase projects and apps (iOS, Android, Web), downloading config files, committing changes to a new GitHub branch, and returning success info.

## 🚀 Quick Start

### Web App
```bash
npm run dev
```
Visit `http://localhost:3000` to use the web interface.

### Desktop App (Recommended)
```bash
npm run launch
```
Launches a native desktop application with full functionality.

## 🖥️ Desktop App Options

### macOS
```bash
# Simple launch
npm run launch

# Shell script
./launch.sh

# Create installer
npm run electron-dist
```

### Windows
```bash
# Simple launch
npm run launch

# Batch file
launch.bat

# Create installer
npm run electron-dist
```

### Linux
```bash
# Simple launch
npm run launch

# Shell script
./launch.sh

# Create installer
npm run electron-dist
```

## 📦 Features

- **GitHub Integration**: Clone private repositories and create new branches
- **Firebase Setup**: Create projects, apps (iOS/Android/Web), and download config files
- **Project Renaming**: Automatically rename project identifiers throughout the codebase
- **Multi-Platform**: Works on macOS, Windows, and Linux
- **Desktop App**: Native desktop application with full functionality
- **Real-time Progress**: See project creation progress in real-time
- **Error Handling**: Comprehensive error handling and recovery

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, React 19, Tailwind CSS
- **Backend**: Next.js API routes, tRPC
- **Desktop**: Electron
- **Process Management**: Node.js child_process/execa
- **File Operations**: shelljs
- **Validation**: Zod
- **Environment**: dotenv

## 🔧 Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd newprojectwizard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create `.env.local`:
   ```env
   GITHUB_PAT=your_github_personal_access_token_here
   FIREBASE_TOKEN=your_firebase_token_here
   ```

4. **Run the application**
   ```bash
   # Web app
   npm run dev
   
   # Desktop app
   npm run launch
   ```

## 📱 Desktop App Features

- **Native Window**: Looks and feels like a native app
- **Menu Bar**: Native menus with keyboard shortcuts (Cmd+N for new project)
- **Full Functionality**: All web features work perfectly
- **External Links**: Opens GitHub and Firebase links in your browser
- **Auto-start Server**: Automatically starts the Next.js server when needed
- **Cross-platform**: Works on macOS, Windows, and Linux

## 🎯 Usage

1. **Fill out the form** with your project details
2. **Select template repository** and branch
3. **Choose Firebase account** for project creation
4. **Click "Create Project"** and watch the magic happen!
5. **Get your new project** with all Firebase configs and GitHub repository

## 📁 Project Structure

```
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── api/            # API routes
│   │   ├── new/            # Project creation form
│   │   └── success/        # Success page
│   ├── lib/                # Shared utilities
│   └── types.ts            # TypeScript types
├── electron/               # Desktop app files
│   └── main.js            # Electron main process
├── public/                 # Static assets
├── launch-electron.js      # Desktop app launcher
├── launch.sh              # macOS/Linux launcher
├── launch.bat             # Windows launcher
└── package.json           # Dependencies and scripts
```

## 🔧 Troubleshooting

### Desktop App Issues
- **App won't start**: Check if Node.js and npm are installed
- **Build errors**: Clear `.next` folder and rebuild
- **Permission errors**: Allow the app in System Preferences (macOS)

### Firebase Issues
- **Project creation fails**: Ensure Firebase CLI is logged in with correct account
- **Storage setup fails**: Storage rules are created but may need manual initialization
- **Config download fails**: Check Firebase project permissions

### GitHub Issues
- **Repository access**: Ensure GitHub PAT has correct permissions
- **Branch creation**: Check repository write permissions

## 📦 Distribution

### Create Desktop Installer
```bash
npm run electron-dist
```

This creates platform-specific installers:
- **macOS**: `.dmg` file
- **Windows**: `.exe` installer
- **Linux**: `.AppImage` file

### Share with Team
1. Build the installer: `npm run electron-dist`
2. Share the installer file from the `dist` folder
3. Users can install it like any other app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**🎉 Happy project creation!**
