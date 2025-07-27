# App Configuration Update

This document shows how the existing `app_config.json` file in the `assets/config` folder will be automatically updated after creating Firebase apps for iOS, Android, and Web platforms.

## File Location

The system updates the existing configuration file at:
```
assets/config/app_config.json
```

## Example Updated app_config.json

```json
{
  "project": {
    "id": "myproject-abc123",
    "name": "myproject",
    "orgDomain": "meghzone",
    "createdAt": "2024-01-15T10:30:00.000Z",
    "firebaseAccount": "user@example.com",
    "lastUpdated": "2024-01-15T10:35:00.000Z"
  },
  "apps": {
    "ios": {
      "appId": "1:123456789:ios:abcdef123456",
      "bundleId": "com.meghzone.myproject",
      "configFile": "ios/Runner/GoogleService-Info.plist",
      "configExists": true,
      "lastUpdated": "2024-01-15T10:35:00.000Z"
    },
    "android": {
      "appId": "1:123456789:android:abcdef123456",
      "packageName": "com.meghzone.myproject",
      "configFile": "android/app/google-services.json",
      "configExists": true,
      "clientId": "123456789-abcdef.apps.googleusercontent.com",
      "lastUpdated": "2024-01-15T10:35:00.000Z"
    },
    "web": {
      "appId": "1:123456789:web:abcdef123456",
      "configFile": "web/firebase-config.js",
      "configExists": true,
      "lastUpdated": "2024-01-15T10:35:00.000Z"
    }
  },
  "firebase": {
    "projectId": "myproject-abc123",
    "storageBucket": "myproject-abc123.appspot.com",
    "apiKey": "AIzaSyC_YourActualApiKeyHere",
    "authDomain": "myproject-abc123.firebaseapp.com",
    "messagingSenderId": "123456789",
    "appId": "1:123456789:web:abcdef123456"
  },
  "summary": {
    "totalApps": 3,
    "successfulConfigs": 3,
    "platforms": {
      "ios": true,
      "android": true,
      "web": true
    },
    "lastUpdated": "2024-01-15T10:35:00.000Z"
  }
}
```

## Generated Files

The system will update/create two files:

1. **`assets/config/app_config.json`** - Updated with Firebase app information (preserves existing data)
2. **`lib/app_config.ts`** - TypeScript interface and typed configuration for Flutter/Dart projects

## Update Process

### 1. **Preserves Existing Data**
- Reads the existing `app_config.json` file
- Merges new Firebase information with existing configuration
- Maintains any existing custom fields or settings

### 2. **Updates Firebase Information**
- **Project details**: ID, name, domain, timestamps
- **App information**: Firebase app IDs, bundle IDs, config file paths
- **Firebase configuration**: API keys, domains, sender IDs extracted from downloaded configs

### 3. **Adds Timestamps**
- `createdAt`: When the project was first created
- `lastUpdated`: When the configuration was last updated
- Individual `lastUpdated` timestamps for each app

## Configuration Details

### Project Information
- `id`: The Firebase project ID
- `name`: The project name
- `orgDomain`: Your organization domain
- `createdAt`: Timestamp when the project was created
- `firebaseAccount`: The Firebase account used for creation
- `lastUpdated`: Timestamp when the config was last updated

### App Information
Each platform (iOS, Android, Web) includes:
- `appId`: The Firebase app ID
- `configFile`: Path to the configuration file
- `configExists`: Whether the config file was successfully downloaded
- `lastUpdated`: When this app's information was last updated
- Platform-specific fields (bundleId for iOS, packageName for Android, etc.)

### Firebase Configuration
Common Firebase settings extracted from the downloaded config files:
- `projectId`: Firebase project ID
- `storageBucket`: Firebase Storage bucket
- `apiKey`: Firebase API key
- `authDomain`: Firebase Auth domain
- `messagingSenderId`: Firebase Cloud Messaging sender ID
- `appId`: Primary app ID (usually from web config)

### Summary
- `totalApps`: Number of apps created
- `successfulConfigs`: Number of config files successfully downloaded
- `platforms`: Boolean flags for each platform
- `lastUpdated`: When the summary was last updated

## Usage

The updated `app_config.json` file can be used to:
- Track which Firebase apps were created
- Verify configuration file locations
- Access Firebase project settings programmatically
- Generate documentation or reports
- Validate the setup process
- Maintain history of configuration changes

The TypeScript interface in `lib/app_config.ts` provides type safety when using the configuration in Flutter/Dart projects.

## Error Handling

- If the existing `app_config.json` file doesn't exist, it will be created
- If the file exists but is corrupted, it will start with an empty configuration
- If config extraction fails, the process continues without failing the main workflow
- All updates include error information when applicable 