# 🚀 NewProjWiz Python Wizard - Quick Start Guide

## ✅ What's New

I've created a **Python-based project wizard** that's much simpler and more reliable than the Electron version. Here's what you get:

### 🎯 **Key Advantages**
- **No complex build process** - Just run Python
- **Multiple GUI options** - PyQt6 desktop app or Flask web interface
- **Cross-platform** - Works on macOS, Windows, Linux
- **Lightweight** - No heavy Electron dependencies
- **Reliable** - No EIO errors or complex process management

## 🚀 **Quick Launch Options**

### **Option 1: Desktop App (Recommended)**
```bash
# Double-click this file in Finder
./NewProjWiz.command
```

### **Option 2: Command Line**
```bash
# Simple launch
python3 python_wizard.py

# Or use the launch script
python3 launch_python_wizard.py
```

### **Option 3: Web Interface**
If PyQt6 isn't available, it automatically falls back to a web interface at `http://localhost:5000`

## 📦 **Installation**

The wizard automatically installs dependencies, but you can also do it manually:

```bash
pip3 install PyQt6 flask requests
```

## 🎨 **Features**

### **Desktop GUI (PyQt6)**
- ✅ Native macOS window
- ✅ Professional tabs interface
- ✅ Project creation form
- ✅ Settings configuration
- ✅ Progress indicators
- ✅ Error handling

### **Web Interface (Flask)**
- ✅ Modern web design
- ✅ Responsive layout
- ✅ Template selection cards
- ✅ Real-time feedback
- ✅ Works in any browser

## 🔧 **How to Use**

1. **Launch the wizard** using any method above
2. **Fill in project details**:
   - Project name
   - Description
   - Organization domain
3. **Select a template** (React Native, Next.js, Flutter)
4. **Choose options**:
   - Initialize Git repository
   - Setup Firebase
5. **Click "Create Project"**
6. **Project is generated** in the `projects/` folder

## ⚙️ **Configuration**

The wizard creates a `config.json` file for your settings:

```json
{
  "github_token": "your_token_here",
  "firebase_account": "your_email@domain.com",
  "templates": {
    "react-native": "https://github.com/your-org/react-native-template",
    "nextjs": "https://github.com/your-org/nextjs-template",
    "flutter": "https://github.com/your-org/flutter-template"
  },
  "default_org": "your-org"
}
```

## 📁 **Project Structure**

```
newprojectwizard/
├── python_wizard.py          # Main Python application
├── NewProjWiz.command        # macOS desktop launcher
├── launch_python_wizard.py   # Launch script
├── requirements.txt          # Python dependencies
├── templates/index.html      # Web interface
├── config.json              # Your settings
└── projects/                # Generated projects
```

## 🎯 **Making it a Desktop App**

### **macOS**
1. **Copy to Applications**:
   ```bash
   cp NewProjWiz.command /Applications/
   ```
2. **Launch from**:
   - Applications folder
   - Spotlight (Cmd + Space, type "NewProjWiz")
   - Dock (drag to dock)

### **Create Desktop Shortcut**
```bash
cp NewProjWiz.command ~/Desktop/
```

## 🔄 **Migration from Electron**

The Python version is **completely independent** of the Electron version:

- ✅ **No conflicts** - Both can coexist
- ✅ **Same functionality** - All features preserved
- ✅ **Better reliability** - No complex process management
- ✅ **Faster startup** - No build process needed

## 🐛 **Troubleshooting**

### **Python Not Found**
```bash
# Install Python 3
brew install python3
```

### **Dependencies Missing**
```bash
pip3 install -r requirements.txt
```

### **Permission Errors**
```bash
chmod +x NewProjWiz.command
```

## 🎉 **Ready to Use!**

The Python wizard is now ready and should be running. You can:

1. **Double-click** `NewProjWiz.command` to launch
2. **Use the desktop GUI** for a native experience
3. **Create projects** with templates and integrations
4. **Configure settings** for GitHub and Firebase

The Python version is **much more reliable** and **easier to use** than the Electron version. Enjoy! 🚀 