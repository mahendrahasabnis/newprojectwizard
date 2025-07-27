# 🚀 NewProjWiz - Complete Step-by-Step Guide

## 📋 Overview
The NewProjWiz Python wizard automates the creation of Flutter projects with Firebase integration. Here's the complete step-by-step process:

## 🔄 Complete Workflow

### **Phase 1: Project Setup & Validation**
1. **📋 Validate Project Data**
   - Check project name format (alphanumeric + hyphens)
   - Validate organization domain
   - Ensure template repository and branch are selected
   - Verify Firebase account (if Firebase setup is enabled)

2. **📁 Create Temporary Workspace**
   - Create temporary directory with project name prefix
   - Set up clean workspace for cloning and processing

### **Phase 2: Template Repository Processing**
3. **📥 Clone Template Repository**
   - Use GitHub Personal Access Token for authentication
   - Clone specific branch from selected repository
   - Verify successful clone with detailed logging
   - **Files affected**: Entire repository structure

4. **🔄 Rename Project Identifiers**
   - Update `pubspec.yaml`: project name, description, version
   - Update `android/app/build.gradle`: application ID, version
   - Update `ios/Runner.xcodeproj/project.pbxproj`: bundle identifier
   - Update `ios/Runner/Info.plist`: bundle identifier, display name
   - Update `web/index.html`: title, meta descriptions
   - Update `README.md`: project name, description
   - Update `firebase.json`: project configuration
   - Update `firestore.rules` and `storage.rules`: project references

### **Phase 3: Firebase Configuration (Optional)**
5. **📝 Create Firebase Configuration Files**
   - Generate `firebase.json` with project settings
   - Create `firestore.indexes.json` for database indexing
   - Generate `lib/firebase_config.dart` for Flutter Firebase integration

6. **🔥 Create Firebase Project** (if enabled)
   - Generate unique project ID with random suffix
   - Create Firebase project via Firebase CLI
   - Retry logic for project ID conflicts (up to 3 attempts)
   - **Output**: Firebase Project ID

7. **📱 Create Firebase Apps**
   - **iOS App**: Create iOS Firebase app with bundle ID
   - **Android App**: Create Android Firebase app with package name
   - **Web App**: Create Web Firebase app
   - **Output**: App IDs for all platforms

8. **🗄️ Setup Firestore Database**
   - Create Firestore database in specified region
   - Deploy basic security rules
   - Configure database settings

9. **⬇️ Download Firebase Configuration Files**
   - Download `GoogleService-Info.plist` → `ios/Runner/`
   - Download `google-services.json` → `android/app/`
   - Download `firebase-config.js` → `web/`
   - Verify file integrity and placement

10. **⚙️ Update App Configuration**
    - Read existing `assets/config/app_config.json`
    - Update with Firebase project details:
      - Project ID
      - App IDs (iOS, Android, Web)
      - API keys and configuration
    - Generate `lib/app_config.ts` for TypeScript type safety
    - Update app configuration with new project data

### **Phase 4: Git & Repository Management**
11. **💾 Commit Project Changes**
    - Add all modified files to Git
    - Create commit with descriptive message
    - Include project name and creation timestamp

12. **🆕 Create Private Repository** (if GitHub token available)
    - Create new private GitHub repository
    - Push project to new repository
    - Set up remote origin
    - **Output**: New repository URL

13. **🏷️ Create Base Build Tag**
    - Create and push base build tag
    - Tag format: `base-build-YYYY-MM-DD`
    - Mark initial project state

### **Phase 5: Finalization**
14. **📦 Move to Final Location**
    - Move from temporary directory to `projects/` folder
    - Clean up temporary workspace
    - Verify final project structure

## 🎯 Detailed Step Breakdown

### **Step 3: Clone Template Repository**
```bash
# Command executed:
git clone --branch <branch> https://<token>@github.com/<repo>.git <temp_dir>

# What happens:
- Authenticates with GitHub using Personal Access Token
- Clones specific branch from template repository
- Downloads all project files and Git history
- Creates local copy in temporary directory
```

### **Step 4: Rename Project Identifiers**
**Files Modified:**
- `pubspec.yaml`: Project metadata
- `android/app/build.gradle`: Android configuration
- `ios/Runner.xcodeproj/project.pbxproj`: iOS bundle settings
- `ios/Runner/Info.plist`: iOS app metadata
- `web/index.html`: Web app configuration
- `README.md`: Project documentation
- `firebase.json`: Firebase project settings
- `firestore.rules`: Database security rules
- `storage.rules`: Storage security rules

### **Step 6: Create Firebase Project**
```bash
# Command executed:
firebase --account <account> projects:create <project_id> --display-name <name>

# What happens:
- Generates unique project ID (name + random number)
- Creates Firebase project via CLI
- Sets display name for project
- Returns project ID for further use
```

### **Step 7: Create Firebase Apps**
```bash
# iOS App:
firebase --account <account> apps:create <project_id> IOS <bundle_id>

# Android App:
firebase --account <account> apps:create <project_id> ANDROID <package_name>

# Web App:
firebase --account <account> apps:create <project_id> WEB <app_name>
```

### **Step 9: Download Firebase Configs**
```bash
# Download commands:
firebase --account <account> apps:sdkconfig IOS <app_id> --out <path>/GoogleService-Info.plist
firebase --account <account> apps:sdkconfig ANDROID <app_id> --out <path>/google-services.json
firebase --account <account> apps:sdkconfig WEB <app_id> --out <path>/firebase-config.js
```

## 🔍 Error Handling & Debugging

### **Common Issues & Solutions**

1. **GitHub Token Issues**
   - **Error**: "GitHub Personal Access Token not configured"
   - **Solution**: Configure token in Settings tab
   - **Debug**: Check token validity with GitHub API

2. **Firebase Project Creation Failures**
   - **Error**: Project ID already exists
   - **Solution**: Automatic retry with new random ID
   - **Debug**: Check Firebase CLI authentication

3. **Repository Clone Failures**
   - **Error**: Repository not found or access denied
   - **Solution**: Verify repository exists and token has access
   - **Debug**: Check clone URL and authentication

4. **File Permission Issues**
   - **Error**: Cannot write to project directory
   - **Solution**: Check directory permissions
   - **Debug**: Verify temp directory creation

### **Progress Tracking**
The wizard now shows detailed progress for each step:
- ✅ Step completion indicators
- 📊 Real-time progress updates
- 🐛 Detailed error messages
- 📝 Console logging for debugging

## 🎉 Success Indicators

### **Project Creation Success**
- ✅ All files properly renamed and configured
- ✅ Firebase project created (if enabled)
- ✅ Configuration files downloaded and placed
- ✅ Git repository initialized and committed
- ✅ Project moved to final location
- ✅ Success message with project details

### **Output Files Generated**
- `projects/<project_name>/` - Complete project directory
- `GoogleService-Info.plist` - iOS Firebase config
- `google-services.json` - Android Firebase config
- `firebase-config.js` - Web Firebase config
- `assets/config/app_config.json` - Updated app configuration
- `lib/app_config.ts` - TypeScript configuration types

## 🚀 Next Steps After Creation

1. **Open Project**: Use "Open Project Folder" button
2. **Install Dependencies**: Run `flutter pub get`
3. **Configure Firebase**: Verify Firebase setup
4. **Test Build**: Run `flutter build` for each platform
5. **Deploy**: Push to your new repository

---

**🎯 The wizard handles all the complex setup automatically, giving you a fully configured Flutter project with Firebase integration ready for development!** 