# NewProjWiz - Project Creation Wizard

A comprehensive project creation wizard with Firebase and GitHub integration, built in Python with a web interface.

## 🚀 Features

### Core Functionality
- **Project Creation**: Create new projects from templates with customizable configurations
- **Firebase Integration**: Automatic Firebase project, app, and configuration setup
- **GitHub Integration**: Create GitHub repositories and manage Git workflows
- **Multi-Platform Support**: iOS, Android, and Web app configurations
- **Real-time Progress**: Step-by-step progress updates in web interface
- **Configuration Management**: Preserve existing configurations while updating Firebase data

### Technical Features
- **Web Interface**: Clean, responsive web UI built with Python's standard library
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **Standalone Application**: Packaged as a native macOS application bundle
- **No External Dependencies**: Uses only Python standard library for web server
- **Clean Output**: Professional display without encoding issues

## 📋 Requirements

### System Requirements
- **Python 3.8+**: Required for running the wizard
- **Git**: For repository management
- **Firebase CLI**: For Firebase project setup
- **macOS**: For building the native application bundle

### Dependencies
- **requests**: For GitHub API integration
- **PyInstaller**: For packaging the application

## 🛠️ Installation

### Option 1: Native macOS Application (Recommended)

1. **Download the Application**:
   ```bash
   # Clone the repository
   git clone https://github.com/mahendrahasabnis/newprojectwizard.git
   cd newprojectwizard
   ```

2. **Build the Application**:
   ```bash
   # Run the build script
   python3 build_full_web.py
   ```

3. **Install to Applications**:
   ```bash
   # Use the install script
   ./install.sh
   ```

4. **Launch the Application**:
   - Open `/Applications/NewProjWiz_FullWeb/NewProjWiz_FullWeb`
   - Or use Spotlight: `Cmd + Space` and search for "NewProjWiz"

### Option 2: Run from Source

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mahendrahasabnis/newprojectwizard.git
   cd newprojectwizard
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure the Application**:
   ```bash
   # Edit config.json with your credentials
   nano config.json
   ```

4. **Run the Wizard**:
   ```bash
   python3 python_wizard_full_web.py
   ```

## ⚙️ Configuration

### Setup config.json

Create or edit `config.json` with your credentials:

```json
{
  "github_token": "YOUR_GITHUB_TOKEN_HERE",
  "firebase_account": "your-email@gmail.com",
  "templates": {
    "react-native": "https://github.com/your-org/react-native-template",
    "nextjs": "https://github.com/your-org/nextjs-template",
    "flutter": "https://github.com/your-org/flutter-template"
  },
  "default_org": "your-org-name"
}
```

### Required Credentials

1. **GitHub Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` and `user` permissions
   - Replace `YOUR_GITHUB_TOKEN_HERE` with your actual token

2. **Firebase Account**:
   - Use your Google account email associated with Firebase
   - Ensure Firebase CLI is installed and authenticated

## 🎯 Usage

### Creating a New Project

1. **Launch the Application**:
   - Open the NewProjWiz application
   - A web browser will automatically open to the wizard interface

2. **Fill in Project Details**:
   - **Project Name**: Enter a unique project name
   - **Description**: Provide a project description
   - **Template Repository**: Select from available templates
   - **Template Branch**: Choose the branch to clone from
   - **Organization Domain**: Enter your organization domain
   - **Firebase Account**: Your Firebase account email

3. **Configure Options**:
   - ✅ **Initialize Git**: Create a new GitHub repository
   - ✅ **Setup Firebase**: Create Firebase project and apps
   - ✅ **Download Configs**: Download Firebase configuration files

4. **Create Project**:
   - Click "Create Project" to start the process
   - Monitor real-time progress in the web interface
   - View detailed step-by-step updates

### What Happens During Creation

1. **Template Cloning**: Clones the selected template repository
2. **GitHub Repository**: Creates a new GitHub repository (if enabled)
3. **Firebase Setup**: 
   - Creates Firebase project
   - Creates iOS, Android, and Web apps
   - Downloads configuration files
   - Updates `app_config.json` with Firebase data
4. **Git Operations**: Commits and pushes changes to GitHub

## 📁 Project Structure

```
newprojectwizard/
├── python_wizard_full_web.py    # Main application file
├── build_full_web.py            # Build script for macOS app
├── install.sh                   # Installation script
├── config.json                  # Configuration file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── dist/                        # Build outputs (excluded from Git)
│   └── NewProjWiz_FullWeb/      # macOS application bundle
└── projects/                    # Generated projects
    └── [project-name]/          # Individual project directories
```

## 🔧 Build Scripts

### Available Build Options

1. **Full Web-Only Build** (Recommended):
   ```bash
   python3 build_full_web.py
   # Choose option 1 for full web-only build
   ```

2. **Debug Build**:
   ```bash
   python3 build_full_web.py
   # Choose option 2 for debug build with console output
   ```

3. **Both Builds**:
   ```bash
   python3 build_full_web.py
   # Choose option 3 for both builds
   ```

### Build Outputs

- **Full Build**: `dist/NewProjWiz_FullWeb/` - Production-ready macOS app
- **Debug Build**: `dist/NewProjWiz_FullWeb_debug/` - Debug version with console output

## 🎨 Features in Detail

### Emoji-Free Interface
- Clean, professional display without encoding issues
- Clear status messages: `SUCCESS:`, `WARNING:`, `ERROR:`
- Cross-platform compatible output

### Configuration Preservation
- Preserves existing `app_config.json` structure
- Updates only Firebase-related keys
- Maintains custom configurations and user-defined values
- Incremental updates without data loss

### Real-time Progress Updates
- Step-by-step progress display in web interface
- Detailed status messages for each operation
- Terminal-style output in web browser

### Firebase Integration
- **Project Creation**: Automatic Firebase project setup
- **App Creation**: iOS, Android, and Web app registration
- **Configuration Download**: Automatic config file downloads
- **Data Updates**: Updates `app_config.json` with real Firebase data

### GitHub Integration
- **Repository Creation**: Automatic GitHub repository setup
- **Git Operations**: Clone, commit, and push operations
- **Conflict Resolution**: Handles push conflicts automatically
- **Remote Management**: Updates Git remotes for new repositories

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   - The application automatically finds an available port
   - If issues persist, restart the application

2. **Firebase CLI Not Found**:
   ```bash
   # Install Firebase CLI
   npm install -g firebase-tools
   firebase login
   ```

3. **GitHub Token Issues**:
   - Ensure your GitHub token has the required permissions
   - Check that the token is valid and not expired

4. **Large File Issues**:
   - Build outputs are automatically excluded via `.gitignore`
   - Large files are not included in the repository

### Debug Mode

Run the application in debug mode for detailed output:

```bash
# Run from source with debug output
python3 python_wizard_full_web.py

# Or use the debug build
./dist/NewProjWiz_FullWeb_debug/NewProjWiz_FullWeb_debug
```

## 📚 Documentation

### Additional Documentation Files

- `EMOJI_FIXES_AND_CONFIG_UPDATE.md`: Details about emoji fixes and config preservation
- `STEP_UPDATES_FEATURE.md`: Information about real-time progress updates
- `GITHUB_PUSH_CONFLICT_FIX.md`: GitHub integration troubleshooting
- `ENHANCED_FIREBASE_CONFIG_UPDATE.md`: Firebase configuration details

### API Documentation

The application uses several key methods:

- `ProjectWizard.create_project()`: Main project creation method
- `ProjectWizard.setup_firebase_simplified()`: Firebase setup workflow
- `ProjectWizard.create_github_repository()`: GitHub repository creation
- `ProjectWizard._update_config_json_with_firebase()`: Configuration updates

## 🤝 Contributing

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your improvements
4. **Test Thoroughly**: Ensure all functionality works correctly
5. **Submit a Pull Request**: Create a PR with detailed description

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add comprehensive error handling
- Include docstrings for all functions
- Test on multiple platforms when possible
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Firebase Team**: For the excellent Firebase CLI and API
- **GitHub Team**: For the comprehensive GitHub API
- **Python Community**: For the robust standard library
- **PyInstaller Team**: For the excellent packaging solution

## 📞 Support

For support and questions:

1. **Check Documentation**: Review the documentation files in the repository
2. **Search Issues**: Look for similar issues in the GitHub issues section
3. **Create Issue**: Open a new issue with detailed information
4. **Contact**: Reach out through GitHub discussions

---

**NewProjWiz** - Streamlining project creation with Firebase and GitHub integration! 🚀
