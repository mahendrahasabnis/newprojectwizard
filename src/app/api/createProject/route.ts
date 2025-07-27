import { NextRequest, NextResponse } from 'next/server';
import { execa } from 'execa';
import * as fs from 'fs';
import * as shell from 'shelljs';
import path from 'path';
import { config } from 'dotenv';
import os from 'os';

// Load environment variables
config();

// Check if required tools are available
async function checkRequiredTools() {
  try {
    // Check if git is available
    await execa('/opt/homebrew/bin/git', ['--version']);
    
    // Check if firebase CLI is available
    await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', ['--version']);
    
    return true;
  } catch (error) {
    console.error('Required tools not found:', error);
    return false;
  }
}

export async function POST(request: NextRequest) {
  try {
    // Check if this is a streaming request for progress updates
    const url = new URL(request.url);
    const streamProgress = url.searchParams.get('stream') === 'true';
    
    if (streamProgress) {
      return new Response(
        new ReadableStream({
          start(controller) {
            const encoder = new TextEncoder();
            
            // Send initial progress
            const sendProgress = (step: number, status: string, message?: string) => {
              const data = JSON.stringify({ step, status, message });
              controller.enqueue(encoder.encode(`data: ${data}\n\n`));
            };
            
            // Simulate progress updates
            const steps = [
              'Cloning template repository',
              'Renaming project identifiers', 
              'Creating Firebase project',
              'Creating Firebase apps',
              'Setting up Firestore database',
              'Downloading Firebase config files',
              'Updating app configuration file',
              'Committing and pushing changes',
              'Creating new private repository',
              'Creating base build tag',
              'Finalizing project setup'
            ];
            
            let currentStep = 0;
            
            const updateProgress = () => {
              if (currentStep < steps.length) {
                sendProgress(currentStep, 'running', steps[currentStep]);
                currentStep++;
                setTimeout(updateProgress, 2000); // Update every 2 seconds
              } else {
                sendProgress(steps.length - 1, 'completed', 'Project creation completed!');
                controller.close();
              }
            };
            
            updateProgress();
          }
        }),
        {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
          },
        }
      );
    }

    // Parse request body
    const body = await request.json();
    const { projectName, orgDomain, templateRepo, templateBranch, firebaseAccount } = body;

    // Validate required fields
    if (!projectName || !orgDomain || !templateRepo || !templateBranch || !firebaseAccount) {
      return NextResponse.json(
        { success: false, error: 'All fields are required' },
        { status: 400 }
      );
    }

    // Validate project name format
    if (!/^[a-z0-9-]+$/.test(projectName)) {
      return NextResponse.json(
        { success: false, error: 'Project name must contain only lowercase letters, numbers, and hyphens' },
        { status: 400 }
      );
    }

    // Check if required tools are available
    await checkRequiredTools();

    // Create temporary directory
    const tempDir = path.join(os.tmpdir(), 'project-wizard', `${projectName}-${Date.now()}`);
    fs.mkdirSync(tempDir, { recursive: true });

    try {
      // Step 1: Clone template repository
      console.log('Cloning template repository...');
      const githubUrl = await cloneTemplateRepository(tempDir, templateRepo, templateBranch);

      // Step 2: Rename project identifiers
      console.log('Renaming project identifiers...');
      await renameProjectIdentifiers(tempDir, projectName, orgDomain);

      // Step 3: Create Firebase configuration files
      console.log('Firebase configuration files created');
      await createFirebaseConfigFiles(projectName, orgDomain);

      // Step 4: Create Firebase project
      console.log('Setting up Firebase project...');
      const firebaseProjectId = await createFirebaseProject(projectName, firebaseAccount);
      console.log('Firebase project created successfully:', firebaseProjectId);

      // Step 5: Create Firebase apps
      console.log('Creating Firebase apps...');
      const appIds = await createFirebaseApps(firebaseProjectId, projectName, orgDomain, firebaseAccount);

      // Step 6: Setup Firestore database
      console.log('Setting up Firestore database...');
      await setupFirestoreDatabase(firebaseProjectId, projectName, firebaseAccount);

      // Step 7: Download and place Firebase config files
      console.log('Downloading Firebase config files...');
      await downloadFirebaseConfigs(tempDir, firebaseProjectId, appIds, firebaseAccount);

      // Step 7.5: Update app_config.json with Firebase app information
      console.log('Updating app_config.json in assets/config folder...');
      await updateAppConfigJson(tempDir, firebaseProjectId, projectName, orgDomain, appIds);

      // Step 8: Commit changes (but don't push to template repository)
      console.log('Committing changes...');
      await commitAndPushChanges(tempDir, projectName);

      // Step 8.5: Create new private repository and push to it
      console.log('Creating new private repository...');
      const newRepoUrl = await createPrivateRepository(tempDir, projectName);

      // Step 9: Create base build tag
      console.log('Creating base build tag...');
      await createBaseBuildTag(tempDir, projectName);

      // Clean up temporary directory
      console.log('Cleaning up temporary directory...');
      fs.rmSync(tempDir, { recursive: true, force: true });

      // Return success response
      return NextResponse.json({
        success: true,
        projectName,
        firebaseProjectId,
        githubUrl,
        newRepoUrl,
        baseBuildTag: `base-build-${new Date().toISOString().split('T')[0]}`,
        firebaseUrl: `https://console.firebase.google.com/project/${firebaseProjectId}`,
        currentStep: 11 // All steps completed (updated from 10 to 11)
      });

    } catch (error) {
      // Clean up on error
      if (fs.existsSync(tempDir)) {
        fs.rmSync(tempDir, { recursive: true, force: true });
      }
      throw error;
    }

  } catch (error) {
    console.error('Project creation failed:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' },
      { status: 500 }
    );
  }
}

async function renameProjectIdentifiers(
  tempDir: string, 
  projectName: string, 
  orgDomain: string
) {
  shell.cd(tempDir);

  // Replace project name in various files
  const filesToUpdate = [
    'pubspec.yaml',
    'android/app/build.gradle',
    'ios/Runner.xcodeproj/project.pbxproj',
    'ios/Runner/Info.plist',
    'web/index.html',
    'README.md',
    'firebase.json',
    'firestore.rules',
    'storage.rules'
  ];

  filesToUpdate.forEach(file => {
    if (shell.test('-f', file)) {
      // Replace old project name with new one
      shell.sed('-i', /mytemplate-app/g, projectName, file);
      shell.sed('-i', /com\.meghzone\.mytemplate-app/g, `com.${orgDomain}.${projectName}`, file);
    }
  });

  // Update bundle identifier in iOS project
  const iosProjectFile = 'ios/Runner.xcodeproj/project.pbxproj';
  if (shell.test('-f', iosProjectFile)) {
    shell.sed('-i', /PRODUCT_BUNDLE_IDENTIFIER = com\.meghzone\.mytemplate-app/g, `PRODUCT_BUNDLE_IDENTIFIER = com.${orgDomain}.${projectName}`, iosProjectFile);
  }

  // Update Android package name
  const androidManifestFile = 'android/app/src/main/AndroidManifest.xml';
  if (shell.test('-f', androidManifestFile)) {
    shell.sed('-i', /package="com\.meghzone\.mytemplate-app"/g, `package="com.${orgDomain}.${projectName}"`, androidManifestFile);
  }

  // Create or update Firebase configuration files
  createFirebaseConfigFiles(projectName, orgDomain);

  console.log('Project identifiers renamed successfully');
}

async function createFirebaseConfigFiles(projectName: string, orgDomain: string) {
  // Create firebase.json if it doesn't exist
  const firebaseConfig = {
    "firestore": {
      "rules": "firestore.rules",
      "indexes": "firestore.indexes.json"
    },
    "storage": {
      "rules": "storage.rules"
    },
    "emulators": {
      "auth": {
        "port": 9099
      },
      "firestore": {
        "port": 8080
      },
      "storage": {
        "port": 9199
      },
      "ui": {
        "enabled": true
      }
    }
  };

  fs.writeFileSync('firebase.json', JSON.stringify(firebaseConfig, null, 2));

  // Create firestore.indexes.json
  const firestoreIndexes = {
    "indexes": [],
    "fieldOverrides": []
  };

  fs.writeFileSync('firestore.indexes.json', JSON.stringify(firestoreIndexes, null, 2));

  // Create Flutter Firebase configuration
  const flutterFirebaseConfig = `import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';

class FirebaseConfig {
  static const String projectId = '${projectName}';
  static const String storageBucket = '${projectName}.appspot.com';
  static const String orgDomain = '${orgDomain}';
  
  static Future<void> initializeFirebase() async {
    await Firebase.initializeApp(
      options: const FirebaseOptions(
        apiKey: 'YOUR_API_KEY', // Will be replaced with actual config
        appId: 'YOUR_APP_ID', // Will be replaced with actual config
        messagingSenderId: 'YOUR_SENDER_ID', // Will be replaced with actual config
        projectId: projectId,
        storageBucket: storageBucket,
      ),
    );
  }
  
  static FirebaseFirestore get firestore => FirebaseFirestore.instance;
  static FirebaseStorage get storage => FirebaseStorage.instance;
  
  // Storage root path for the project
  static String get storageRoot => 'projects/${projectName}';
}`;

  // Create lib/firebase_config.dart
  shell.mkdir('-p', 'lib');
  fs.writeFileSync('lib/firebase_config.dart', flutterFirebaseConfig);

  // Update pubspec.yaml to include Firebase dependencies
  const pubspecFile = 'pubspec.yaml';
  if (shell.test('-f', pubspecFile)) {
    // Add Firebase dependencies if not already present
    const firebaseDependencies = `
  # Firebase dependencies
  firebase_core: ^2.24.2
  cloud_firestore: ^4.14.0
  firebase_storage: ^11.6.0
  firebase_auth: ^4.16.0`;

    // Check if Firebase dependencies are already in pubspec.yaml
    const pubspecContent = fs.readFileSync(pubspecFile, 'utf8');
    if (!pubspecContent.includes('firebase_core:')) {
      // Insert dependencies before the dev_dependencies section
      const updatedContent = pubspecContent.replace(
        /dev_dependencies:/,
        `${firebaseDependencies}\n\ndev_dependencies:`
      );
      fs.writeFileSync(pubspecFile, updatedContent);
    }
  }

  console.log('Firebase configuration files created');
}

async function createFirebaseProject(projectName: string, firebaseAccount: string): Promise<string> {
  // Always create a new Firebase project
  const projectId = `${projectName}-${Math.random().toString(36).substring(2, 8)}`;
  
  // Ensure display name is at least 4 characters (Firebase requirement)
  const displayName = projectName.length >= 4 ? projectName : `${projectName}-project`;
  
  console.log(`Creating new Firebase project: ${projectId}`);
  console.log(`Display name: ${displayName}`);
  
  // Try multiple times with different project IDs if needed
  for (let attempt = 1; attempt <= 3; attempt++) {
    const currentProjectId = attempt === 1 ? projectId : `${projectName}-${Math.random().toString(36).substring(2, 8)}`;
    
    try {
      console.log(`Attempt ${attempt}: Creating Firebase project: ${currentProjectId}`);
      
      await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
        '--account', firebaseAccount,
        'projects:create',
        currentProjectId,
        '--display-name', displayName
      ], { env: { ...process.env } });
      
      console.log(`Firebase project created successfully: ${currentProjectId}`);
      return currentProjectId;
    } catch (error) {
      console.error(`Attempt ${attempt} failed to create Firebase project:`, error);
      
      if (attempt === 3) {
        // Last attempt failed, throw error
        throw new Error(`Failed to create Firebase project after 3 attempts. Please ensure you have proper permissions to create Firebase projects. Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
      
      // Wait a bit before retrying
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  throw new Error('Unexpected error in Firebase project creation');
}

async function createFirebaseApps(
  projectId: string,
  projectName: string,
  orgDomain: string,
  firebaseAccount: string
): Promise<{ ios: string; android: string; web: string }> {
  const bundleId = `com.${orgDomain}.${projectName}`;
  const results = { ios: 'unknown', android: 'unknown', web: 'unknown' };
  
  // Create iOS app
  console.log('Creating iOS app...');
  try {
    const iosResult = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
      '--account', firebaseAccount,
      'apps:create',
      'ios',
      `${projectName}-ios`,
      '--bundle-id', bundleId,
      '--project', projectId
    ], { env: { ...process.env } });
    console.log('iOS app creation output:', iosResult.stdout);
    results.ios = extractAppId(iosResult.stdout);
    console.log('Extracted iOS app ID:', results.ios);
  } catch (error) {
    console.error('Failed to create iOS app:', error);
    console.log('Continuing with other apps...');
  }

  // Create Android app
  console.log('Creating Android app...');
  console.log('Android app details:', {
    projectId,
    appName: `${projectName}-android`,
    packageName: bundleId,
    firebaseAccount
  });
  
  try {
    const androidResult = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
      '--account', firebaseAccount,
      'apps:create',
      'android',
      `${projectName}-android`,
      '--package-name', bundleId,
      '--project', projectId
    ], { env: { ...process.env } });
    console.log('Android app creation output:', androidResult.stdout);
    results.android = extractAppId(androidResult.stdout);
    console.log('Extracted Android app ID:', results.android);
  } catch (error) {
    console.error('Failed to create Android app:', error);
    if (typeof error === 'object' && error !== null && 'stdout' in error && 'stderr' in error && 'command' in error) {
      console.error('Android app creation error details:', {
        stdout: (error as {stdout?: string}).stdout,
        stderr: (error as {stderr?: string}).stderr,
        command: (error as {command?: string}).command
      });
    }
    console.log('Continuing with other apps...');
  }

  // Create Web app
  console.log('Creating Web app...');
  try {
    const webResult = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
      '--account', firebaseAccount,
      'apps:create',
      'web',
      `${projectName}-web`,
      '--project', projectId
    ], { env: { ...process.env } });
    console.log('Web app creation output:', webResult.stdout);
    results.web = extractAppId(webResult.stdout);
    console.log('Extracted Web app ID:', results.web);
  } catch (error) {
    console.error('Failed to create Web app:', error);
    console.log('Continuing with other apps...');
  }

  // Check if at least one app was created successfully
  const successfulApps = Object.values(results).filter(id => id !== 'unknown').length;
  if (successfulApps === 0) {
    throw new Error('Failed to create any Firebase apps');
  }

  console.log(`Successfully created ${successfulApps} out of 3 Firebase apps`);
  return results;
}

function extractAppId(output: string): string {
  console.log('Extracting app ID from output:', output);
  
  // Try multiple patterns to extract app ID
  const patterns = [
    /App ID: ([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)/, // Full Firebase app ID format: project:app:platform:id
    /App ID: ([a-zA-Z0-9-]+)/,
    /App ID: ([a-zA-Z0-9-]+)/i,
    /([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)/, // Full Firebase app ID format without "App ID:" prefix
    /([a-zA-Z0-9-]{20,})/, // Firebase app IDs are typically long
    /Created app ([a-zA-Z0-9-]+)/,
    /App created: ([a-zA-Z0-9-]+)/
  ];

  for (const pattern of patterns) {
    const match = output.match(pattern);
    if (match && match[1]) {
      console.log(`Found app ID with pattern: ${pattern} -> ${match[1]}`);
      return match[1];
    }
  }

  // If no pattern matches, try to extract any long alphanumeric string
  const words = output.split(/\s+/);
  for (const word of words) {
    if (word.length > 15 && /^[a-zA-Z0-9-:]+$/.test(word)) {
      console.log(`Found app ID from word: ${word}`);
      return word;
    }
  }

  console.log('No app ID found, returning unknown');
  return 'unknown';
}

async function downloadFirebaseConfigs(
  tempDir: string,
  projectId: string,
  appIds: { ios: string; android: string; web: string },
  firebaseAccount: string
) {
  shell.cd(tempDir);
  const configs: { ios?: string; android?: string; web?: string } = {};

  // Download iOS config (GoogleService-Info.plist)
  if (appIds.ios && appIds.ios !== 'unknown') {
    try {
      console.log('Downloading iOS config...');
      const result = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
        '--account', firebaseAccount,
        'apps:sdkconfig',
        'ios',
        appIds.ios,
        '--project', projectId
      ], { env: { ...process.env } });
      configs.ios = result.stdout;
      console.log('iOS config downloaded successfully');
    } catch (error) {
      console.log('Failed to download iOS config:', error);
      // Continue without iOS config
    }
  } else {
    console.log('Skipping iOS config download - app not created');
  }

  // Download Android config (google-services.json)
  if (appIds.android && appIds.android !== 'unknown') {
    try {
      console.log('Downloading Android config...');
      const result = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
        '--account', firebaseAccount,
        'apps:sdkconfig',
        'android',
        appIds.android,
        '--project', projectId
      ], { env: { ...process.env } });
      configs.android = result.stdout;
      console.log('Android config downloaded successfully');
    } catch (error) {
      console.log('Failed to download Android config:', error);
      // Continue without Android config
    }
  } else {
    console.log('Skipping Android config download - app not created');
  }

  // Download Web config (firebase-config.js)
  if (appIds.web && appIds.web !== 'unknown') {
    try {
      console.log('Downloading Web config...');
      const result = await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
        '--account', firebaseAccount,
        'apps:sdkconfig',
        'web',
        appIds.web,
        '--project', projectId
      ], { env: { ...process.env } });
      configs.web = result.stdout;
      console.log('Web config downloaded successfully');
    } catch (error) {
      console.log('Failed to download Web config:', error);
      // Continue without Web config
    }
  } else {
    console.log('Skipping Web config download - app not created');
  }

  // Save config files to appropriate locations
  if (configs.ios) {
    shell.mkdir('-p', 'ios/Runner');
    fs.writeFileSync('ios/Runner/GoogleService-Info.plist', configs.ios);
    console.log('iOS config saved to ios/Runner/GoogleService-Info.plist');
  }
  
  if (configs.android) {
    shell.mkdir('-p', 'android/app');
    fs.writeFileSync('android/app/google-services.json', configs.android);
    console.log('Android config saved to android/app/google-services.json');
  }
  
  if (configs.web) {
    shell.mkdir('-p', 'web');
    fs.writeFileSync('web/firebase-config.js', configs.web);
    console.log('Web config saved to web/firebase-config.js');
  }

  console.log('Firebase config download completed');
}

async function updateAppConfigJson(
  tempDir: string,
  projectId: string,
  projectName: string,
  orgDomain: string,
  appIds: { ios: string; android: string; web: string }
) {
  try {
    shell.cd(tempDir);
    
    // Define the config file path relative to the temp directory
    const existingConfigPath = 'assets/config/app_config.json';
    const absoluteConfigPath = path.join(tempDir, existingConfigPath);
    
    console.log(`\n=== UPDATING APP_CONFIG.JSON ===`);
    console.log(`Target file path: ${absoluteConfigPath}`);
    console.log(`Working directory: ${tempDir}`);
    
    // Check if the existing app_config.json file exists
    if (!fs.existsSync(existingConfigPath)) {
      console.log('Existing app_config.json not found in assets/config, skipping update...');
      return;
    }
    
    // Read existing configuration
    let existingConfig: {
      app?: { name?: string };
      firebase?: {
        ios?: {
          apiKey?: string;
          messagingSenderId?: string;
          appId?: string;
          projectId?: string;
          storageBucket?: string;
          iosBundleId?: string;
        };
        android?: {
          apiKey?: string;
          messagingSenderId?: string;
          appId?: string;
          projectId?: string;
          storageBucket?: string;
        };
        web?: {
          apiKey?: string;
          authDomain?: string;
          projectId?: string;
          storageBucket?: string;
          messagingSenderId?: string;
          appId?: string;
          measurementId?: string;
        };
      };
    } = {};
    let beforeContent = '';
    try {
      beforeContent = fs.readFileSync(existingConfigPath, 'utf8');
      existingConfig = JSON.parse(beforeContent);
      console.log(`\n--- BEFORE UPDATE ---`);
      console.log(`File exists: Yes`);
      console.log(`File size: ${beforeContent.length} characters`);
      console.log(`Content preview: ${beforeContent.substring(0, 200)}${beforeContent.length > 200 ? '...' : ''}`);
    } catch (error) {
      console.log('Could not parse existing app_config.json, skipping update');
      console.log(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return;
    }
    
    // Update app name with project display name (only if the key exists)
    if (existingConfig.app?.name !== undefined) {
      existingConfig.app.name = projectName;
    }
    
    // Extract configuration from downloaded files to update Firebase sections
    // Update iOS config if it exists and has the required keys
    if (existingConfig.firebase && existingConfig.firebase.ios && appIds.ios && appIds.ios !== 'unknown') {
      const iosConfigPath = 'ios/Runner/GoogleService-Info.plist';
      if (fs.existsSync(iosConfigPath)) {
        const iosConfigContent = fs.readFileSync(iosConfigPath, 'utf8');
        
        const apiKeyMatch = iosConfigContent.match(/<key>API_KEY<\/key>\s*<string>([^<]+)<\/string>/);
        const senderIdMatch = iosConfigContent.match(/<key>GCM_SENDER_ID<\/key>\s*<string>([^<]+)<\/string>/);
        const appIdMatch = iosConfigContent.match(/<key>GOOGLE_APP_ID<\/key>\s*<string>([^<]+)<\/string>/);
        
        // Only update if the keys exist in the original config
        if (apiKeyMatch && existingConfig.firebase.ios.apiKey !== undefined) {
          existingConfig.firebase.ios.apiKey = apiKeyMatch[1];
        }
        if (senderIdMatch && existingConfig.firebase.ios.messagingSenderId !== undefined) {
          existingConfig.firebase.ios.messagingSenderId = senderIdMatch[1];
        }
        if (appIdMatch && existingConfig.firebase.ios.appId !== undefined) {
          existingConfig.firebase.ios.appId = appIdMatch[1];
        }
        if (existingConfig.firebase.ios.projectId !== undefined) {
          existingConfig.firebase.ios.projectId = projectId;
        }
        if (existingConfig.firebase.ios.storageBucket !== undefined) {
          existingConfig.firebase.ios.storageBucket = `${projectId}.firebasestorage.app`;
        }
        if (existingConfig.firebase.ios.iosBundleId !== undefined) {
          existingConfig.firebase.ios.iosBundleId = `com.${orgDomain}.${projectName}`;
        }
      }
    }

    // Update Android config if it exists and has the required keys
    if (existingConfig.firebase && existingConfig.firebase.android && appIds.android && appIds.android !== 'unknown') {
      const androidConfigPath = 'android/app/google-services.json';
      if (fs.existsSync(androidConfigPath)) {
        const androidConfigContent = fs.readFileSync(androidConfigPath, 'utf8');
        const androidConfig = JSON.parse(androidConfigContent);
        
        if (androidConfig.project_info) {
          // Only update if the keys exist in the original config
          if (existingConfig.firebase.android.apiKey !== undefined) {
            existingConfig.firebase.android.apiKey = androidConfig.project_info.api_key || null;
          }
          if (existingConfig.firebase.android.messagingSenderId !== undefined) {
            existingConfig.firebase.android.messagingSenderId = androidConfig.project_info.project_number || null;
          }
        }
        
        if (androidConfig.client && androidConfig.client[0] && androidConfig.client[0].client_info) {
          if (existingConfig.firebase.android.appId !== undefined) {
            existingConfig.firebase.android.appId = androidConfig.client[0].client_info.mobilesdk_app_id || null;
          }
        }
        
        if (existingConfig.firebase.android.projectId !== undefined) {
          existingConfig.firebase.android.projectId = projectId;
        }
        if (existingConfig.firebase.android.storageBucket !== undefined) {
          existingConfig.firebase.android.storageBucket = `${projectId}.firebasestorage.app`;
        }
      }
    }

    // Update Web config if it exists and has the required keys
    if (existingConfig.firebase && existingConfig.firebase.web && appIds.web && appIds.web !== 'unknown') {
      const webConfigPath = 'web/firebase-config.js';
      if (fs.existsSync(webConfigPath)) {
        const webConfigContent = fs.readFileSync(webConfigPath, 'utf8');
        
        console.log('\n--- WEB CONFIG UPDATE DEBUG ---');
        console.log(`Web config file exists: ${fs.existsSync(webConfigPath)}`);
        console.log(`Web config content length: ${webConfigContent.length}`);
        console.log(`Web config content preview: ${webConfigContent.substring(0, 300)}...`);
        
        const apiKeyMatch = webConfigContent.match(/"apiKey":\s*"([^"]+)"/);
        const authDomainMatch = webConfigContent.match(/"authDomain":\s*"([^"]+)"/);
        const projectIdMatch = webConfigContent.match(/"projectId":\s*"([^"]+)"/);
        const storageBucketMatch = webConfigContent.match(/"storageBucket":\s*"([^"]+)"/);
        const messagingSenderIdMatch = webConfigContent.match(/"messagingSenderId":\s*"([^"]+)"/);
        const appIdMatch = webConfigContent.match(/"appId":\s*"([^"]+)"/);
        const measurementIdMatch = webConfigContent.match(/"measurementId":\s*"([^"]+)"/);
        
        console.log(`\n--- REGEX MATCHES ---`);
        console.log(`apiKeyMatch: ${apiKeyMatch ? apiKeyMatch[1] : 'null'}`);
        console.log(`authDomainMatch: ${authDomainMatch ? authDomainMatch[1] : 'null'}`);
        console.log(`projectIdMatch: ${projectIdMatch ? projectIdMatch[1] : 'null'}`);
        console.log(`storageBucketMatch: ${storageBucketMatch ? storageBucketMatch[1] : 'null'}`);
        console.log(`messagingSenderIdMatch: ${messagingSenderIdMatch ? messagingSenderIdMatch[1] : 'null'}`);
        console.log(`appIdMatch: ${appIdMatch ? appIdMatch[1] : 'null'}`);
        console.log(`measurementIdMatch: ${measurementIdMatch ? measurementIdMatch[1] : 'null'}`);
        
        console.log(`\n--- EXISTING CONFIG KEYS ---`);
        console.log(`existingConfig.firebase.web.apiKey: ${existingConfig.firebase.web.apiKey}`);
        console.log(`existingConfig.firebase.web.authDomain: ${existingConfig.firebase.web.authDomain}`);
        console.log(`existingConfig.firebase.web.projectId: ${existingConfig.firebase.web.projectId}`);
        console.log(`existingConfig.firebase.web.storageBucket: ${existingConfig.firebase.web.storageBucket}`);
        console.log(`existingConfig.firebase.web.messagingSenderId: ${existingConfig.firebase.web.messagingSenderId}`);
        console.log(`existingConfig.firebase.web.appId: ${existingConfig.firebase.web.appId}`);
        console.log(`existingConfig.firebase.web.measurementId: ${existingConfig.firebase.web.measurementId}`);
        
        // Update web config values - remove the undefined checks to ensure values are always updated
        if (apiKeyMatch) {
          existingConfig.firebase.web.apiKey = apiKeyMatch[1];
          console.log(`Updated apiKey: ${apiKeyMatch[1]}`);
        }
        if (authDomainMatch) {
          existingConfig.firebase.web.authDomain = authDomainMatch[1];
          console.log(`Updated authDomain: ${authDomainMatch[1]}`);
        }
        if (projectIdMatch) {
          existingConfig.firebase.web.projectId = projectIdMatch[1];
          console.log(`Updated projectId: ${projectIdMatch[1]}`);
        }
        if (storageBucketMatch) {
          existingConfig.firebase.web.storageBucket = storageBucketMatch[1];
          console.log(`Updated storageBucket: ${storageBucketMatch[1]}`);
        }
        if (messagingSenderIdMatch) {
          existingConfig.firebase.web.messagingSenderId = messagingSenderIdMatch[1];
          console.log(`Updated messagingSenderId: ${messagingSenderIdMatch[1]}`);
        }
        if (appIdMatch) {
          existingConfig.firebase.web.appId = appIdMatch[1];
          console.log(`Updated appId: ${appIdMatch[1]}`);
        }
        if (measurementIdMatch) {
          existingConfig.firebase.web.measurementId = measurementIdMatch[1];
          console.log(`Updated measurementId: ${measurementIdMatch[1]}`);
        }
        
        console.log(`\n--- AFTER WEB CONFIG UPDATE ---`);
        console.log(`existingConfig.firebase.web.apiKey: ${existingConfig.firebase.web.apiKey}`);
        console.log(`existingConfig.firebase.web.authDomain: ${existingConfig.firebase.web.authDomain}`);
        console.log(`existingConfig.firebase.web.projectId: ${existingConfig.firebase.web.projectId}`);
        console.log(`existingConfig.firebase.web.storageBucket: ${existingConfig.firebase.web.storageBucket}`);
        console.log(`existingConfig.firebase.web.messagingSenderId: ${existingConfig.firebase.web.messagingSenderId}`);
        console.log(`existingConfig.firebase.web.appId: ${existingConfig.firebase.web.appId}`);
        console.log(`existingConfig.firebase.web.measurementId: ${existingConfig.firebase.web.measurementId}`);
        console.log(`=== END WEB CONFIG UPDATE DEBUG ===\n`);
      } else {
        console.log(`Web config file not found at: ${webConfigPath}`);
      }
    } else {
      console.log(`Web config update skipped - conditions not met:`);
      console.log(`- existingConfig.firebase: ${!!existingConfig.firebase}`);
      console.log(`- existingConfig.firebase.web: ${!!(existingConfig.firebase && existingConfig.firebase.web)}`);
      console.log(`- appIds.web: ${appIds.web}`);
      console.log(`- appIds.web !== 'unknown': ${appIds.web !== 'unknown'}`);
    }

    // Write updated configuration back to the existing file
    const afterContent = JSON.stringify(existingConfig, null, 2);
    fs.writeFileSync(existingConfigPath, afterContent);
    
    console.log(`\n--- AFTER UPDATE ---`);
    console.log(`File size: ${afterContent.length} characters`);
    console.log(`Content preview: ${afterContent.substring(0, 200)}${afterContent.length > 200 ? '...' : ''}`);
    console.log(`\n--- CHANGES SUMMARY ---`);
    console.log(`Content changed: ${beforeContent !== afterContent ? 'Yes' : 'No'}`);
    if (beforeContent !== afterContent) {
      console.log(`Size difference: ${afterContent.length - beforeContent.length} characters`);
    }
    
    console.log('Updated app_config.json in assets/config folder successfully');
    
    // Also create a TypeScript interface file for type safety (in lib folder)
    const typescriptInterface = `// Auto-generated Firebase app configuration types
export interface FirebaseAppConfig {
  app?: {
    name?: string;
    description?: string;
    version?: string;
    buildNumber?: string;
  };
  firebase?: {
    web?: {
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      authDomain?: string;
      storageBucket?: string;
      measurementId?: string;
    };
    android?: {
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      storageBucket?: string;
    };
    ios?: {
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      storageBucket?: string;
      iosBundleId?: string;
    };
  };
  assets?: any;
  features?: any;
  api?: any;
  ui?: any;
  localization?: any;
}

// Import the configuration from assets/config/app_config.json
export const appConfig: FirebaseAppConfig = ${JSON.stringify(existingConfig, null, 2)};
`;

    shell.mkdir('-p', 'lib');
    fs.writeFileSync('lib/app_config.ts', typescriptInterface);
    console.log('lib/app_config.ts created successfully');
    
    // Verify the file was written correctly
    const verifyContent = fs.readFileSync(existingConfigPath, 'utf8');
    console.log(`\n--- VERIFICATION ---`);
    console.log(`File exists after write: ${fs.existsSync(existingConfigPath)}`);
    console.log(`File content matches: ${verifyContent === afterContent ? 'Yes' : 'No'}`);
    console.log(`=== END APP_CONFIG UPDATE ===\n`);
    
  } catch (error) {
    console.error('Failed to update app_config.json:', error);
    // Don't throw error - this is not critical for the main process
    console.log('Continuing without updating app_config.json...');
  }
}

async function commitAndPushChanges(
  tempDir: string, 
  projectName: string
): Promise<string> {
  try {
    // Change to temp directory
    shell.cd(tempDir);

    console.log(`\n=== COMMITTING AND PUSHING CHANGES ===`);
    console.log(`Working directory: ${tempDir}`);

    // Check git status before adding
    console.log('\n--- GIT STATUS BEFORE ADD ---');
    const statusBefore = await execa('/opt/homebrew/bin/git', ['status', '--porcelain'], { env: { ...process.env } });
    console.log('Git status output:');
    console.log(statusBefore.stdout || '(no changes detected)');

    // Add all changes
    console.log('\n--- ADDING CHANGES ---');
    await execa('/opt/homebrew/bin/git', ['add', '.'], { env: { ...process.env } });
    console.log('All changes added to git staging area');

    // Check git status after adding
    console.log('\n--- GIT STATUS AFTER ADD ---');
    const statusAfter = await execa('/opt/homebrew/bin/git', ['status', '--porcelain'], { env: { ...process.env } });
    console.log('Git status output:');
    console.log(statusAfter.stdout || '(no changes detected)');

    // Check if app_config.json is in the staged changes
    const stagedFiles = statusAfter.stdout.split('\n').filter(line => line.startsWith('A ') || line.startsWith('M '));
    const appConfigInStaged = stagedFiles.some(file => file.includes('app_config.json'));
    console.log(`\n--- APP_CONFIG.JSON STATUS ---`);
    console.log(`app_config.json in staged changes: ${appConfigInStaged ? 'Yes' : 'No'}`);
    
    if (appConfigInStaged) {
      console.log('Files containing app_config.json:');
      stagedFiles.filter(file => file.includes('app_config.json')).forEach(file => {
        console.log(`  ${file}`);
      });
    }

    // Check if there are changes to commit
    if (statusAfter.stdout.trim()) {
      console.log('\n--- COMMITTING CHANGES ---');
      const commitMessage = `Setup ${projectName} with Firebase configuration - ${new Date().toISOString()}`;
      console.log(`Commit message: ${commitMessage}`);
      
      await execa('/opt/homebrew/bin/git', [
        'commit',
        '-m', commitMessage
      ], { env: { ...process.env } });

      console.log('Changes committed successfully');

      // Show commit details
      console.log('\n--- COMMIT DETAILS ---');
      const commitDetails = await execa('/opt/homebrew/bin/git', ['log', '-1', '--oneline'], { env: { ...process.env } });
      console.log(`Latest commit: ${commitDetails.stdout.trim()}`);

      // Note: We will NOT push to template repository - only to new private repository
      console.log('\n--- SKIPPING TEMPLATE REPOSITORY PUSH ---');
      console.log('Template repository will remain unchanged');
    } else {
      console.log('\n--- NO CHANGES TO COMMIT ---');
      console.log('Git status shows no changes to commit');
    }

    console.log('=== END COMMIT AND PUSH ===\n');
    return 'Changes committed to local repository';
  } catch (error) {
    console.error('Failed to commit and push changes:', error);
    throw new Error(`Failed to commit and push changes: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

async function setupFirestoreDatabase(projectId: string, projectName: string, firebaseAccount: string) {
  try {
    // Create Firestore database
    console.log('Creating Firestore database...');
    await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
      '--account', firebaseAccount,
      'firestore:databases:create',
      'default',
      '--location', 'us-central1',
      '--project', projectId
    ], { env: { ...process.env } });

    // Create firestore.rules file with access rules
    const firestoreRules = `rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access for testing until 1 year from creation date
    // This rule expires on ${new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
    
    // Allow all operations for testing (will be restricted after 1 year)
    match /{document=**} {
      allow read, write: if true;
    }
    
    // TODO: Replace with proper security rules after testing period
    // Example secure rules:
    // match /users/{userId} {
    //   allow read, write: if request.auth != null && request.auth.uid == userId;
    // }
    // match /posts/{postId} {
    //   allow read: if true;
    //   allow write: if request.auth != null;
    // }
  }
}`;

    // Save firestore.rules to the project
    fs.writeFileSync('firestore.rules', firestoreRules);
    console.log('Firestore rules created with testing access for 1 year');

    // Deploy Firestore rules
    console.log('Deploying Firestore rules...');
    await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
      '--account', firebaseAccount,
      'deploy',
      '--only', 'firestore:rules',
      '--project', projectId
    ], { env: { ...process.env } });

    console.log('Firestore database setup completed');
  } catch (error) {
    console.error('Failed to setup Firestore database:', error);
    // Continue without Firestore if it fails
  }
}

// Firebase Storage setup commented out as it requires billing account upgrade
// async function setupFirebaseStorage(projectId: string, projectName: string, firebaseAccount: string) {
//   try {
//     // Create storage.rules file with access rules
//     const storageRules = `rules_version = '2';
// service firebase.storage {
//   match /b/{bucket}/o {
//     // Allow read/write access for testing until 1 year from creation date
//     // This rule expires on ${new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
//     
//     // Allow all operations for testing (will be restricted after 1 year)
//     match /{allPaths=**} {
//       allow read, write: if true;
//     }
//     
//     // TODO: Replace with proper security rules after testing period
//     // Example secure rules:
//     // match /users/{userId}/{allPaths=**} {
//     //   allow read, write: if request.auth != null && request.auth.uid == userId;
//     // }
//     // match /public/{allPaths=**} {
//     //   allow read: if true;
//     //   allow write: if request.auth != null;
//     // }
//   }
// }`;

//     // Save storage.rules to the project
//     fs.writeFileSync('storage.rules', storageRules);
//     console.log('Storage rules created with testing access for 1 year');

//     // Try to deploy Storage rules, but don't fail if Storage isn't set up yet
//     console.log('Deploying Storage rules...');
//     try {
//       await execa('/Users/mh/.nvm/versions/node/v23.0.0/bin/firebase', [
//         '--account', firebaseAccount,
//         'deploy',
//         '--only', 'storage',
//         '--project', projectId
//       ], { env: { ...process.env } });
//       console.log('Firebase Storage setup completed');
//     } catch (deployError) {
//       console.log('Firebase Storage not yet initialized. Rules file created for later deployment.');
//       console.log('To enable Storage, visit: https://console.firebase.google.com/project/' + projectId + '/storage');
//       console.log('Deploy error:', deployError);
//     }
//   } catch (error) {
//     console.error('Failed to setup Firebase Storage:', error);
//     // Continue without Storage if it fails
//   }
// }

async function createPrivateRepository(tempDir: string, projectName: string): Promise<string> {
  try {
    // Create new private repository via GitHub API
    const githubToken = process.env.GITHUB_PAT;
    if (!githubToken || githubToken === 'your_github_personal_access_token_here') {
      console.log('Skipping private repository creation - no valid GitHub token');
      return '';
    }

    const repoData = {
      name: projectName,
      private: true,
      description: `Base build for ${projectName} - created by Project Wizard`,
      auto_init: false
    };

    const response = await fetch('https://api.github.com/user/repos', {
      method: 'POST',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'Project-Wizard'
      },
      body: JSON.stringify(repoData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Failed to create repository: ${errorData.message || response.statusText}`);
    }

    const repo = await response.json();
    const newRepoUrl = repo.clone_url;
    const newRepoName = repo.full_name;

    console.log(`Created private repository: ${newRepoName}`);

    // Change to temp directory
    shell.cd(tempDir);

    // Add new remote
    await execa('/opt/homebrew/bin/git', ['remote', 'add', 'new-origin', newRepoUrl], { env: { ...process.env } });

    // Push to new repository
    await execa('/opt/homebrew/bin/git', ['push', 'new-origin', 'main'], { env: { ...process.env } });

    console.log(`Pushed to new private repository: ${newRepoName}`);

    return `https://github.com/${newRepoName}`;
  } catch (error) {
    console.error('Failed to create private repository:', error);
    return '';
  }
}

async function createBaseBuildTag(tempDir: string, projectName: string): Promise<void> {
  try {
    shell.cd(tempDir);
    
    const dateStr = new Date().toISOString().split('T')[0];
    const timestamp = new Date().toISOString();
    let tagName = `base-build-${dateStr}`;
    const tagMessage = `Base build for ${projectName} - ${timestamp}`;
    
    // Check if tag already exists
    try {
      await execa('/opt/homebrew/bin/git', ['rev-parse', tagName], { env: { ...process.env } });
      // Tag exists, create a unique one with timestamp
      tagName = `base-build-${dateStr}-${Date.now()}`;
      console.log(`Tag ${tagName} already exists, creating unique tag: ${tagName}`);
    } catch {
      // Tag doesn't exist, we can use the original name
      console.log(`Creating base build tag: ${tagName}`);
    }

    // Create annotated tag
    await execa('/opt/homebrew/bin/git', [
      'tag',
      '-a', tagName,
      '-m', tagMessage
    ], { env: { ...process.env } });

    // Push the tag
    await execa('/opt/homebrew/bin/git', ['push', 'origin', tagName], { env: { ...process.env } });
    
    console.log(`Base build tag created and pushed: ${tagName}`);
      } catch {
      console.error('Failed to create base build tag');
      // Continue without tag if it fails
    }
}

async function cloneTemplateRepository(tempDir: string, templateRepo: string, templateBranch: string): Promise<string> {
  try {
    const githubToken = process.env.GITHUB_PAT;
    if (!githubToken || githubToken === 'your_github_personal_access_token_here') {
      throw new Error('GitHub Personal Access Token not configured');
    }

    await execa('/opt/homebrew/bin/git', [
      'clone',
      '--branch', templateBranch,
      `https://${githubToken}@github.com/${templateRepo}.git`,
      tempDir
    ], { env: { ...process.env } });

    return `https://github.com/${templateRepo}/tree/${templateBranch}`;
  } catch (error) {
    console.error('Failed to clone template repository:', error);
    throw new Error(`Failed to clone template repository: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
} 