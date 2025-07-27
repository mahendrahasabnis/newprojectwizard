# NewProjWiz - Python Project Wizard

A modern, Python-based desktop application for creating new projects with Firebase and GitHub integration.

## 🚀 Features

- **Multiple GUI Options**: PyQt6 desktop app or Flask web interface
- **Template System**: Clone from existing project templates
- **Git Integration**: Automatic git repository initialization
- **Firebase Setup**: Configure Firebase projects automatically
- **GitHub Integration**: Create repositories and manage tokens
- **Cross-Platform**: Works on macOS, Windows, and Linux

## 📋 Requirements

- Python 3.8 or higher
- Git (for repository operations)
- Firebase CLI (optional, for Firebase setup)

## 🛠️ Installation

### Option 1: Quick Start
```bash
# Clone or download the project
cd newprojectwizard

# Run the launch script
python launch_python_wizard.py
```

### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the wizard
python python_wizard.py
```

## 🎯 Usage

### Desktop GUI (PyQt6)
The application will automatically use PyQt6 if available, providing a native desktop experience:

1. **Project Details**: Enter project name, description, and organization domain
2. **Template Selection**: Choose from available project templates
3. **Options**: Configure Git initialization and Firebase setup
4. **Create**: Click "Create Project" to generate your project

### Web Interface (Flask)
If PyQt6 is not available, the app falls back to a web interface:

1. Open your browser to `http://localhost:5000`
2. Fill out the project form
3. Submit to create your project

## ⚙️ Configuration

The wizard creates a `config.json` file to store your settings:

```json
{
  "github_token": "your_github_token_here",
  "firebase_account": "your_email@domain.com",
  "templates": {
    "react-native": "https://github.com/your-org/react-native-template",
    "nextjs": "https://github.com/your-org/nextjs-template",
    "flutter": "https://github.com/your-org/flutter-template"
  },
  "default_org": "your-org"
}
```

### Setting up GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` and `workflow` permissions
3. Enter the token in the Settings tab

### Setting up Firebase
1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Enter your Firebase account email in the Settings tab

## 📁 Project Structure

```
newprojectwizard/
├── python_wizard.py          # Main application
├── launch_python_wizard.py   # Launch script
├── requirements.txt          # Python dependencies
├── config.json              # Configuration file
├── templates/               # Web interface templates
│   └── index.html
├── projects/                # Generated projects
└── PYTHON_WIZARD_README.md  # This file
```

## 🔧 Customization

### Adding New Templates
Edit the `config.json` file to add new templates:

```json
{
  "templates": {
    "your-template": "https://github.com/your-org/your-template-repo"
  }
}
```

### Customizing Project Generation
Modify the `ProjectWizard` class in `python_wizard.py` to customize:
- Project file updates
- Git repository setup
- Firebase configuration
- Additional integrations

## 🐛 Troubleshooting

### PyQt6 Not Available
If you get an error about PyQt6:
```bash
pip install PyQt6
```

### Flask Not Available
If you get an error about Flask:
```bash
pip install flask
```

### Git Not Found
Make sure Git is installed and available in your PATH:
- **macOS**: `brew install git`
- **Windows**: Download from https://git-scm.com/
- **Linux**: `sudo apt-get install git`

### Permission Errors
If you get permission errors when creating projects:
- Make sure you have write permissions in the current directory
- Try running with elevated permissions if needed

## 🚀 Advanced Features

### Custom Project Templates
Create your own templates by:
1. Creating a repository with your project structure
2. Adding it to the `config.json` templates
3. The wizard will clone and customize it

### Firebase Integration
The wizard can automatically:
- Create Firebase projects
- Configure Firebase settings
- Generate configuration files

### GitHub Integration
Features include:
- Repository creation
- Token validation
- Branch management
- Issue templates

## 📝 Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug output
python python_wizard.py
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🎨 GUI Options

### PyQt6 (Recommended)
- Native desktop experience
- Rich UI components
- Cross-platform compatibility
- Professional appearance

### Flask Web Interface
- Browser-based interface
- Modern web design
- Easy to customize
- Works on any device

## 🔒 Security

- GitHub tokens are stored locally in `config.json`
- No data is sent to external servers
- All operations happen locally
- Templates are cloned from trusted sources

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Check the console output for error messages
4. Create an issue with detailed information

---

**Happy coding! 🚀** 