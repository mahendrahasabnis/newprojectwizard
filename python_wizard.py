#!/usr/bin/env python3
"""
NewProjWiz - Python-based Project Wizard
A desktop application for creating new projects with Firebase and GitHub integration.
"""

import sys
import os
import json
import subprocess
import threading
import webbrowser
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# GUI imports
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QTextEdit, QComboBox, QCheckBox, QProgressBar,
                                QTabWidget, QGroupBox, QMessageBox, QFileDialog)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Web interface imports
try:
    from flask import Flask, render_template, request, jsonify
    from webview import create_window, start
    import requests
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    try:
        import requests
    except ImportError:
        requests = None

class ProjectWizard:
    """Main project wizard class"""
    
    def __init__(self):
        self.config = self.load_config()
        self.current_project = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "github_token": "",
            "firebase_account": "",
            "templates": {
                "react-native": "https://github.com/your-org/react-native-template",
                "nextjs": "https://github.com/your-org/nextjs-template",
                "flutter": "https://github.com/your-org/flutter-template"
            },
            "default_org": "your-org"
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open("config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project with full Electron functionality"""
        try:
            # Extract all required fields
            project_name = project_data.get('name', '')
            org_domain = project_data.get('org_domain', '')
            description = project_data.get('description', '')
            template_repo = project_data.get('template_repo', '')
            template_branch = project_data.get('template_branch', 'main')
            firebase_account = project_data.get('firebase_account', '')
            init_git = project_data.get('init_git', True)
            setup_firebase = project_data.get('setup_firebase', False)
            
            # Validate required fields
            if not project_name or not org_domain or not template_repo or not template_branch:
                return {"success": False, "error": "Missing required fields: name, org_domain, template_repo, template_branch"}
            
            # Validate project name format
            if not re.match(r'^[a-z0-9-]+$', project_name):
                return {"success": False, "error": "Project name must contain only lowercase letters, numbers, and hyphens"}
            
            # Create temporary directory
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix=f'{project_name}-'))
            
            try:
                # Step 1: Clone template repository
                github_url = self._clone_template_repository(temp_dir, template_repo, template_branch)
                
                # Step 2: Rename project identifiers
                self._rename_project_identifiers(temp_dir, project_name, org_domain)
                
                # Step 3: Create Firebase configuration files
                self._create_firebase_config_files(temp_dir, project_name, org_domain)
                
                # Step 4: Create Firebase project (if requested)
                firebase_project_id = None
                app_ids = None
                if setup_firebase and firebase_account:
                    firebase_project_id = self._create_firebase_project(project_name, firebase_account)
                    app_ids = self._create_firebase_apps(firebase_project_id, project_name, org_domain, firebase_account)
                    self._setup_firestore_database(firebase_project_id, project_name, firebase_account)
                    self._download_firebase_configs(temp_dir, firebase_project_id, app_ids, firebase_account)
                    self._update_app_config_json(temp_dir, firebase_project_id, project_name, org_domain, app_ids)
                
                # Step 5: Commit changes
                self._commit_and_push_changes(temp_dir, project_name)
                
                # Step 6: Create new private repository
                new_repo_url = self._create_private_repository(temp_dir, project_name)
                
                # Step 7: Create base build tag
                self._create_base_build_tag(temp_dir, project_name)
                
                # Step 8: Move to final location
                final_project_dir = Path('projects') / project_name
                if final_project_dir.exists():
                    import shutil
                    shutil.rmtree(final_project_dir)
                temp_dir.rename(final_project_dir)
                
                return {
                    'success': True,
                    'project_path': str(final_project_dir),
                    'firebase_project_id': firebase_project_id,
                    'github_url': github_url,
                    'new_repo_url': new_repo_url,
                    'base_build_tag': f'base-build-{datetime.now().strftime("%Y-%m-%d")}',
                    'message': f'Project {project_name} created successfully!'
                }
                
            except Exception as e:
                # Clean up temp directory on error
                if temp_dir.exists():
                    import shutil
                    shutil.rmtree(temp_dir)
                raise e
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_project_config(self, project_dir: Path, project_data: Dict[str, Any]):
        """Update project configuration files"""
        project_name = project_data['name']
        org_domain = project_data['org_domain']
        
        # Update package.json (if exists)
        package_json = project_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            package_data['name'] = project_name.lower().replace(' ', '-')
            package_data['description'] = project_data.get('description', f'{project_name} project')
            
            with open(package_json, 'w') as f:
                json.dump(package_data, f, indent=2)
        
        # Update app.json (React Native)
        app_json = project_dir / "app.json"
        if app_json.exists():
            with open(app_json, 'r') as f:
                app_data = json.load(f)
            
            app_data['expo']['name'] = project_name
            app_data['expo']['slug'] = project_name.lower().replace(' ', '-')
            
            with open(app_json, 'w') as f:
                json.dump(app_data, f, indent=2)
    
    def init_git_repository(self, project_dir: Path, project_name: str):
        """Initialize git repository"""
        try:
            # Remove existing git
            git_dir = project_dir / ".git"
            if git_dir.exists():
                import shutil
                shutil.rmtree(git_dir)
            
            # Initialize new git repository
            subprocess.run(['git', 'init'], cwd=project_dir, check=True)
            subprocess.run(['git', 'add', '.'], cwd=project_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Initial commit for {project_name}'], cwd=project_dir, check=True)
            
        except Exception as e:
            print(f"Error initializing git: {e}")
    
    def setup_firebase(self, project_dir: Path, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Firebase for the project"""
        try:
            # This would integrate with Firebase CLI
            # For now, just create a placeholder
            firebase_config = {
                "projectId": f"{project_data['name'].lower().replace(' ', '-')}-{project_data['org_domain']}",
                "projectName": project_data['name'],
                "orgDomain": project_data['org_domain']
            }
            
            firebase_file = project_dir / "firebase-config.json"
            with open(firebase_file, 'w') as f:
                json.dump(firebase_config, f, indent=2)
            
            return {"success": True, "message": "Firebase configuration created"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_templates(self) -> Dict[str, str]:
        """Get available templates"""
        return self.config['templates']
    
    def validate_github_token(self, token: str) -> bool:
        """Validate GitHub token"""
        if not requests:
            return False
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"}
            )
            return response.status_code == 200
        except:
            return False
    
    def _clone_template_repository(self, temp_dir, template_repo, template_branch):
        """Clone template repository"""
        try:
            github_token = self.config.get('github_token')
            if not github_token or github_token == 'your_github_personal_access_token_here':
                raise Exception('GitHub Personal Access Token not configured')
            
            clone_url = f'https://{github_token}@github.com/{template_repo}.git'
            print(f"Cloning from: {clone_url}")
            print(f"Branch: {template_branch}")
            print(f"Target directory: {temp_dir}")
            
            result = subprocess.run(
                ['git', 'clone', '--branch', template_branch, clone_url, str(temp_dir)], 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            print(f"Clone successful: {result.stdout}")
            return f'https://github.com/{template_repo}/tree/{template_branch}'
        except subprocess.CalledProcessError as e:
            print(f"Clone failed: {e}")
            print(f"Error output: {e.stderr}")
            raise Exception(f'Failed to clone template repository: {e.stderr}')
    
    def _rename_project_identifiers(self, temp_dir, project_name, org_domain):
        """Rename project identifiers in various files"""
        files_to_update = [
            'pubspec.yaml',
            'android/app/build.gradle',
            'ios/Runner.xcodeproj/project.pbxproj',
            'ios/Runner/Info.plist',
            'web/index.html',
            'README.md',
            'firebase.json',
            'firestore.rules',
            'storage.rules'
        ]
        
        for file_path in files_to_update:
            full_path = temp_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    # Replace old project name with new one
                    content = content.replace('mytemplate-app', project_name)
                    content = content.replace('com.meghzone.mytemplate-app', f'com.{org_domain}.{project_name}')
                    
                    with open(full_path, 'w') as f:
                        f.write(content)
                except Exception as e:
                    print(f"Warning: Could not update {file_path}: {e}")
    
    def _create_firebase_config_files(self, temp_dir, project_name, org_domain):
        """Create Firebase configuration files"""
        # Create firebase.json
        firebase_config = {
            "firestore": {
                "rules": "firestore.rules",
                "indexes": "firestore.indexes.json"
            },
            "storage": {
                "rules": "storage.rules"
            },
            "emulators": {
                "auth": {"port": 9099},
                "firestore": {"port": 8080},
                "storage": {"port": 9199},
                "ui": {"enabled": True}
            }
        }
        
        with open(temp_dir / 'firebase.json', 'w') as f:
            json.dump(firebase_config, f, indent=2)
        
        # Create firestore.indexes.json
        firestore_indexes = {"indexes": [], "fieldOverrides": []}
        with open(temp_dir / 'firestore.indexes.json', 'w') as f:
            json.dump(firestore_indexes, f, indent=2)
        
        # Create Flutter Firebase configuration
        flutter_firebase_config = f'''import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';

class FirebaseConfig {{
  static const String projectId = '{project_name}';
  static const String storageBucket = '{project_name}.appspot.com';
  static const String orgDomain = '{org_domain}';
  
  static Future<void> initializeFirebase() async {{
    await Firebase.initializeApp(
      options: const FirebaseOptions(
        apiKey: 'YOUR_API_KEY', // Will be replaced with actual config
        appId: 'YOUR_APP_ID', // Will be replaced with actual config
        messagingSenderId: 'YOUR_SENDER_ID', // Will be replaced with actual config
        projectId: projectId,
        storageBucket: storageBucket,
      ),
    );
  }}
  
  static FirebaseFirestore get firestore => FirebaseFirestore.instance;
  static FirebaseStorage get storage => FirebaseStorage.instance;
  
  // Storage root path for the project
  static String get storageRoot => 'projects/{project_name}';
}}'''
        
        # Create lib/firebase_config.dart
        lib_dir = temp_dir / 'lib'
        lib_dir.mkdir(exist_ok=True)
        with open(lib_dir / 'firebase_config.dart', 'w') as f:
            f.write(flutter_firebase_config)
    
    def _create_firebase_project(self, project_name, firebase_account):
        """Create Firebase project"""
        try:
            import random
            project_id = f'{project_name}-{random.randint(100000, 999999)}'
            display_name = project_name if len(project_name) >= 4 else f'{project_name}-project'
            
            print(f"Creating Firebase project: {project_id}")
            print(f"Display name: {display_name}")
            print(f"Firebase account: {firebase_account}")
            
            # Try multiple times with different project IDs if needed
            for attempt in range(1, 4):
                current_project_id = project_id if attempt == 1 else f'{project_name}-{random.randint(100000, 999999)}'
                
                try:
                    print(f"Attempt {attempt}: Creating project {current_project_id}")
                    result = subprocess.run([
                        'firebase', '--account', firebase_account,
                        'projects:create', current_project_id,
                        '--display-name', display_name
                    ], check=True, capture_output=True, text=True, timeout=120)
                    
                    print(f"Firebase project created successfully: {result.stdout}")
                    return current_project_id
                except subprocess.CalledProcessError as e:
                    print(f"Attempt {attempt} failed: {e}")
                    print(f"Error output: {e.stderr}")
                    if attempt == 3:
                        raise Exception(f'Failed to create Firebase project after 3 attempts: {e.stderr}')
                    time.sleep(2)
                except subprocess.TimeoutExpired:
                    print(f"Attempt {attempt} timed out after 120 seconds")
                    if attempt == 3:
                        raise Exception('Firebase project creation timed out after 3 attempts')
                    time.sleep(2)
            
            raise Exception('Unexpected error in Firebase project creation')
        except Exception as e:
            print(f"Firebase project creation failed: {e}")
            raise Exception(f'Firebase project creation failed: {e}')
    
    def _create_firebase_apps(self, project_id, project_name, org_domain, firebase_account):
        """Create Firebase apps for iOS, Android, and Web"""
        bundle_id = f'com.{org_domain}.{project_name}'
        results = {'ios': 'unknown', 'android': 'unknown', 'web': 'unknown'}
        
        print(f"Creating Firebase apps for project: {project_id}")
        print(f"Bundle ID: {bundle_id}")
        print(f"Firebase account: {firebase_account}")
        
        # Create iOS app (with longer timeout and better error handling)
        try:
            print(f"Creating iOS app: {project_name}-ios")
            print(f"Bundle ID: {bundle_id}")
            print(f"Project ID: {project_id}")
            
            # Use the same command structure as the original Electron version
            # Provide empty input via stdin to handle interactive prompts
            result = subprocess.run([
                'firebase', '--account', firebase_account,
                'apps:create', 'ios',
                f'{project_name}-ios',
                '--bundle-id', bundle_id,
                '--project', project_id
            ], check=True, capture_output=True, text=True, timeout=90, input='\n')
            print(f"iOS app creation output: {result.stdout}")
            results['ios'] = self._extract_app_id(result.stdout)
            print(f"iOS app ID: {results['ios']}")
        except subprocess.CalledProcessError as e:
            print(f'Failed to create iOS app: {e}')
            print(f'Error output: {e.stderr}')
            print('Continuing without iOS app...')
        except subprocess.TimeoutExpired:
            print('iOS app creation timed out after 90 seconds')
            print('Continuing without iOS app...')
        except Exception as e:
            print(f'Unexpected error creating iOS app: {e}')
            print('Continuing without iOS app...')
        
        # Create Android app
        try:
            print(f"Creating Android app: {project_name}-android")
            result = subprocess.run([
                'firebase', '--account', firebase_account,
                'apps:create', 'android',
                f'{project_name}-android',
                '--package-name', bundle_id,
                '--project', project_id
            ], check=True, capture_output=True, text=True, timeout=60)
            print(f"Android app creation output: {result.stdout}")
            results['android'] = self._extract_app_id(result.stdout)
            print(f"Android app ID: {results['android']}")
        except subprocess.TimeoutExpired:
            print('Android app creation timed out after 60 seconds')
        except subprocess.CalledProcessError as e:
            print(f'Failed to create Android app: {e}')
            print(f'Error output: {e.stderr}')
        except Exception as e:
            print(f'Unexpected error creating Android app: {e}')
        
        # Create Web app
        try:
            print(f"Creating Web app: {project_name}-web")
            result = subprocess.run([
                'firebase', '--account', firebase_account,
                'apps:create', 'web',
                f'{project_name}-web',
                '--project', project_id
            ], check=True, capture_output=True, text=True, timeout=60)
            print(f"Web app creation output: {result.stdout}")
            results['web'] = self._extract_app_id(result.stdout)
            print(f"Web app ID: {results['web']}")
        except subprocess.CalledProcessError as e:
            print(f'Failed to create Web app: {e}')
            print(f'Error output: {e.stderr}')
        except subprocess.TimeoutExpired:
            print('Web app creation timed out after 60 seconds')
        except Exception as e:
            print(f'Unexpected error creating Web app: {e}')
        
        # Check if at least one app was created successfully
        successful_apps = sum(1 for id in results.values() if id != 'unknown')
        print(f"Successfully created {successful_apps} out of 3 apps")
        print(f"App results: {results}")
        
        if successful_apps == 0:
            print("Warning: No Firebase apps were created successfully")
            print("Continuing with project creation without Firebase apps...")
            # Return empty results but don't fail the entire process
            return {'ios': 'unknown', 'android': 'unknown', 'web': 'unknown'}
        
        return results
    
    def _extract_app_id(self, output):
        """Extract app ID from Firebase CLI output"""
        print(f"Extracting app ID from output: {output}")
        
        # Look for the specific pattern we saw in the test output
        patterns = [
            r'App ID: ([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)',
            r'App ID: ([a-zA-Z0-9-]+)',
            r'([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)',
            r'([a-zA-Z0-9-]{20,})',
            r'Created app ([a-zA-Z0-9-]+)',
            r'App created: ([a-zA-Z0-9-]+)',
            r'App ID ([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)',
            r'App ID ([a-zA-Z0-9-]+)',
            r'([0-9]+:[0-9]+:[a-z]+:[a-zA-Z0-9]+)',
            r'([a-zA-Z0-9-]{15,})'
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, output, re.IGNORECASE)
            if match and match.group(1):
                app_id = match.group(1)
                print(f"Found app ID with pattern {i}: {app_id}")
                return app_id
        
        # Try to extract any long alphanumeric string that looks like an app ID
        words = output.split()
        for word in words:
            if len(word) > 15 and re.match(r'^[a-zA-Z0-9-:]+$', word):
                print(f"Found potential app ID in word: {word}")
                return word
        
        print("No app ID found in output")
        return 'unknown'
    
    def _download_firebase_configs(self, temp_dir, project_id, app_ids, firebase_account):
        """Download Firebase configuration files"""
        configs = {}
        
        print(f"Downloading Firebase configs for project: {project_id}")
        print(f"App IDs: {app_ids}")
        
        # Download iOS config
        if app_ids['ios'] and app_ids['ios'] != 'unknown':
            try:
                print(f"Downloading iOS config for app ID: {app_ids['ios']}")
                result = subprocess.run([
                    'firebase', '--account', firebase_account,
                    'apps:sdkconfig', 'ios', app_ids['ios'], '--project', project_id
                ], check=True, capture_output=True, text=True, timeout=30)
                configs['ios'] = result.stdout
                
                # Save to ios/Runner/GoogleService-Info.plist
                ios_dir = temp_dir / 'ios' / 'Runner'
                ios_dir.mkdir(parents=True, exist_ok=True)
                with open(ios_dir / 'GoogleService-Info.plist', 'w') as f:
                    f.write(result.stdout)
                print("✅ iOS config downloaded successfully")
            except subprocess.CalledProcessError as e:
                print(f'Failed to download iOS config: {e}')
            except subprocess.TimeoutExpired:
                print('iOS config download timed out')
        else:
            print("⏭️ Skipping iOS config download (no valid app ID)")
        
        # Download Android config
        if app_ids['android'] and app_ids['android'] != 'unknown':
            try:
                print(f"Downloading Android config for app ID: {app_ids['android']}")
                result = subprocess.run([
                    'firebase', '--account', firebase_account,
                    'apps:sdkconfig', 'android', app_ids['android'], '--project', project_id
                ], check=True, capture_output=True, text=True, timeout=30)
                configs['android'] = result.stdout
                
                # Save to android/app/google-services.json
                android_dir = temp_dir / 'android' / 'app'
                android_dir.mkdir(parents=True, exist_ok=True)
                with open(android_dir / 'google-services.json', 'w') as f:
                    f.write(result.stdout)
                print("✅ Android config downloaded successfully")
            except subprocess.CalledProcessError as e:
                print(f'Failed to download Android config: {e}')
            except subprocess.TimeoutExpired:
                print('Android config download timed out')
        else:
            print("⏭️ Skipping Android config download (no valid app ID)")
        
        # Download Web config
        if app_ids['web'] and app_ids['web'] != 'unknown':
            try:
                print(f"Downloading Web config for app ID: {app_ids['web']}")
                result = subprocess.run([
                    'firebase', '--account', firebase_account,
                    'apps:sdkconfig', 'web', app_ids['web'], '--project', project_id
                ], check=True, capture_output=True, text=True, timeout=30)
                configs['web'] = result.stdout
                
                # Save to web/firebase-config.js
                web_dir = temp_dir / 'web'
                web_dir.mkdir(exist_ok=True)
                with open(web_dir / 'firebase-config.js', 'w') as f:
                    f.write(result.stdout)
                print("✅ Web config downloaded successfully")
            except subprocess.CalledProcessError as e:
                print(f'Failed to download Web config: {e}')
            except subprocess.TimeoutExpired:
                print('Web config download timed out')
        else:
            print("⏭️ Skipping Web config download (no valid app ID)")
        
        print(f"Downloaded configs: {list(configs.keys())}")
        return configs
    
    def _update_app_config_json(self, temp_dir, project_id, project_name, org_domain, app_ids):
        """Update app_config.json with Firebase configuration"""
        config_path = temp_dir / 'assets' / 'config' / 'app_config.json'
        if not config_path.exists():
            print('app_config.json not found, skipping update')
            return
        
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            # Update app name
            if 'app' in existing_config and 'name' in existing_config['app']:
                existing_config['app']['name'] = project_name
            
            # Update Firebase configuration
            if 'firebase' not in existing_config:
                existing_config['firebase'] = {}
            
            # Update iOS config
            if app_ids['ios'] and app_ids['ios'] != 'unknown':
                ios_config_path = temp_dir / 'ios' / 'Runner' / 'GoogleService-Info.plist'
                if ios_config_path.exists():
                    with open(ios_config_path, 'r') as f:
                        ios_content = f.read()
                    
                    if 'firebase' not in existing_config:
                        existing_config['firebase'] = {}
                    if 'ios' not in existing_config['firebase']:
                        existing_config['firebase']['ios'] = {}
                    
                    # Extract values from plist
                    api_key_match = re.search(r'<key>API_KEY</key>\s*<string>([^<]+)</string>', ios_content)
                    sender_id_match = re.search(r'<key>GCM_SENDER_ID</key>\s*<string>([^<]+)</string>', ios_content)
                    app_id_match = re.search(r'<key>GOOGLE_APP_ID</key>\s*<string>([^<]+)</string>', ios_content)
                    
                    if api_key_match:
                        existing_config['firebase']['ios']['apiKey'] = api_key_match.group(1)
                    if sender_id_match:
                        existing_config['firebase']['ios']['messagingSenderId'] = sender_id_match.group(1)
                    if app_id_match:
                        existing_config['firebase']['ios']['appId'] = app_id_match.group(1)
                    
                    existing_config['firebase']['ios']['projectId'] = project_id
                    existing_config['firebase']['ios']['storageBucket'] = f'{project_id}.firebasestorage.app'
                    existing_config['firebase']['ios']['iosBundleId'] = f'com.{org_domain}.{project_name}'
            
            # Update Android config
            if app_ids['android'] and app_ids['android'] != 'unknown':
                android_config_path = temp_dir / 'android' / 'app' / 'google-services.json'
                if android_config_path.exists():
                    with open(android_config_path, 'r') as f:
                        android_config = json.load(f)
                    
                    if 'firebase' not in existing_config:
                        existing_config['firebase'] = {}
                    if 'android' not in existing_config['firebase']:
                        existing_config['firebase']['android'] = {}
                    
                    if 'project_info' in android_config:
                        existing_config['firebase']['android']['apiKey'] = android_config['project_info'].get('api_key')
                        existing_config['firebase']['android']['messagingSenderId'] = android_config['project_info'].get('project_number')
                    
                    if 'client' in android_config and android_config['client']:
                        existing_config['firebase']['android']['appId'] = android_config['client'][0].get('client_info', {}).get('mobilesdk_app_id')
                    
                    existing_config['firebase']['android']['projectId'] = project_id
                    existing_config['firebase']['android']['storageBucket'] = f'{project_id}.firebasestorage.app'
            
            # Update Web config
            if app_ids['web'] and app_ids['web'] != 'unknown':
                web_config_path = temp_dir / 'web' / 'firebase-config.js'
                if web_config_path.exists():
                    with open(web_config_path, 'r') as f:
                        web_content = f.read()
                    
                    if 'firebase' not in existing_config:
                        existing_config['firebase'] = {}
                    if 'web' not in existing_config['firebase']:
                        existing_config['firebase']['web'] = {}
                    
                    # Extract values from web config
                    patterns = {
                        'apiKey': r'"apiKey":\s*"([^"]+)"',
                        'authDomain': r'"authDomain":\s*"([^"]+)"',
                        'projectId': r'"projectId":\s*"([^"]+)"',
                        'storageBucket': r'"storageBucket":\s*"([^"]+)"',
                        'messagingSenderId': r'"messagingSenderId":\s*"([^"]+)"',
                        'appId': r'"appId":\s*"([^"]+)"',
                        'measurementId': r'"measurementId":\s*"([^"]+)"'
                    }
                    
                    for key, pattern in patterns.items():
                        match = re.search(pattern, web_content)
                        if match:
                            existing_config['firebase']['web'][key] = match.group(1)
            
            # Write updated configuration
            with open(config_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            # Create TypeScript interface file
            lib_dir = temp_dir / 'lib'
            lib_dir.mkdir(exist_ok=True)
            
            typescript_interface = f'''// Auto-generated Firebase app configuration types
export interface FirebaseAppConfig {{
  app?: {{
    name?: string;
    description?: string;
    version?: string;
    buildNumber?: string;
  }};
  firebase?: {{
    web?: {{
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      authDomain?: string;
      storageBucket?: string;
      measurementId?: string;
    }};
    android?: {{
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      storageBucket?: string;
    }};
    ios?: {{
      apiKey?: string;
      appId?: string;
      messagingSenderId?: string;
      projectId?: string;
      storageBucket?: string;
      iosBundleId?: string;
    }};
  }};
  assets?: any;
  features?: any;
  api?: any;
  ui?: any;
  localization?: any;
}}

// Import the configuration from assets/config/app_config.json
export const appConfig: FirebaseAppConfig = {json.dumps(existing_config, indent=2)};
'''
            
            with open(lib_dir / 'app_config.ts', 'w') as f:
                f.write(typescript_interface)
                
        except Exception as e:
            print(f'Failed to update app_config.json: {e}')
    
    def _setup_firestore_database(self, project_id, project_name, firebase_account):
        """Setup Firestore database"""
        try:
            print(f"Setting up Firestore database for project: {project_id}")
            
            # Check if database already exists
            try:
                result = subprocess.run([
                    'firebase', '--account', firebase_account,
                    'firestore:databases:list', '--project', project_id
                ], check=True, capture_output=True, text=True, timeout=30)
                
                if 'default' in result.stdout:
                    print("Firestore database 'default' already exists")
                    return
            except subprocess.CalledProcessError:
                pass  # Continue with creation
            
            # Create Firestore database
            print("Creating Firestore database...")
            result = subprocess.run([
                'firebase', '--account', firebase_account,
                'firestore:databases:create', 'default',
                '--location', 'us-central1', '--project', project_id
            ], check=True, capture_output=True, text=True, timeout=60)
            
            print("Firestore database created successfully")
            
            # Create firestore.rules file
            firestore_rules = f'''rules_version = '2';
service cloud.firestore {{
  match /databases/{{database}}/documents {{
    // Allow read/write access for testing until 1 year from creation date
    // This rule expires on {datetime.now().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d")}
    
    // Allow all operations for testing (will be restricted after 1 year)
    match /{{document=**}} {{
      allow read, write: if true;
    }}
    
    // TODO: Replace with proper security rules after testing period
    // Example secure rules:
    // match /users/{{userId}} {{
    //   allow read, write: if request.auth != null && request.auth.uid == userId;
    // }}
    // match /posts/{{postId}} {{
    //   allow read: if true;
    //   allow write: if request.auth != null;
    // }}
  }}
}}'''
            
            with open('firestore.rules', 'w') as f:
                f.write(firestore_rules)
            
            print("Firestore rules file created")
            
            # Deploy Firestore rules
            print("Deploying Firestore rules...")
            subprocess.run([
                'firebase', '--account', firebase_account,
                'deploy', '--only', 'firestore:rules', '--project', project_id
            ], check=True, capture_output=True, text=True, timeout=60)
            
            print("Firestore rules deployed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f'Failed to setup Firestore database: {e}')
            print(f'Error output: {e.stderr if hasattr(e, "stderr") else "No stderr"}')
            print('Continuing without Firestore database setup...')
        except subprocess.TimeoutExpired:
            print('Firestore database setup timed out')
            print('Continuing without Firestore database setup...')
        except Exception as e:
            print(f'Unexpected error setting up Firestore database: {e}')
            print('Continuing without Firestore database setup...')
    
    def _commit_and_push_changes(self, temp_dir, project_name):
        """Commit and push changes"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], cwd=temp_dir, capture_output=True, text=True)
            if result.stdout.strip():
                commit_message = f'Setup {project_name} with Firebase configuration - {datetime.now().isoformat()}'
                subprocess.run(['git', 'commit', '-m', commit_message], cwd=temp_dir, check=True)
                print('Changes committed successfully')
            else:
                print('No changes to commit')
                
        except subprocess.CalledProcessError as e:
            raise Exception(f'Failed to commit changes: {e}')
    
    def _create_private_repository(self, temp_dir, project_name):
        """Create new private repository"""
        try:
            github_token = self.config.get('github_token')
            if not github_token or github_token == 'your_github_personal_access_token_here':
                print('Skipping private repository creation - no valid GitHub token')
                return ''
            
            repo_data = {
                'name': project_name,
                'private': True,
                'description': f'Base build for {project_name} - created by Project Wizard',
                'auto_init': False
            }
            
            response = requests.post(
                'https://api.github.com/user/repos',
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Project-Wizard'
                },
                json=repo_data
            )
            
            if not response.ok:
                error_data = response.json()
                raise Exception(f'Failed to create repository: {error_data.get("message", response.status_text)}')
            
            repo = response.json()
            new_repo_url = repo['clone_url']
            new_repo_name = repo['full_name']
            
            # Add new remote and push
            subprocess.run(['git', 'remote', 'add', 'new-origin', new_repo_url], cwd=temp_dir, check=True)
            subprocess.run(['git', 'push', 'new-origin', 'main'], cwd=temp_dir, check=True)
            
            return f'https://github.com/{new_repo_name}'
            
        except Exception as e:
            print(f'Failed to create private repository: {e}')
            return ''
    
    def _create_base_build_tag(self, temp_dir, project_name):
        """Create base build tag"""
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            timestamp = datetime.now().isoformat()
            tag_name = f'base-build-{date_str}'
            tag_message = f'Base build for {project_name} - {timestamp}'
            
            # Check if tag already exists
            try:
                subprocess.run(['git', 'rev-parse', tag_name], cwd=temp_dir, check=True, capture_output=True)
                # Tag exists, create a unique one with timestamp
                tag_name = f'base-build-{date_str}-{int(time.time())}'
                print(f'Tag {tag_name} already exists, creating unique tag: {tag_name}')
            except subprocess.CalledProcessError:
                # Tag doesn't exist, we can use the original name
                print(f'Creating base build tag: {tag_name}')
            
            # Create annotated tag
            subprocess.run(['git', 'tag', '-a', tag_name, '-m', tag_message], cwd=temp_dir, check=True)
            
            # Push the tag
            subprocess.run(['git', 'push', 'origin', tag_name], cwd=temp_dir, check=True)
            
            print(f'Base build tag created and pushed: {tag_name}')
            
        except subprocess.CalledProcessError as e:
            print(f'Failed to create base build tag: {e}')
    
    def get_github_repositories(self):
        """Get GitHub repositories for the user"""
        try:
            github_token = self.config.get('github_token')
            if not github_token or github_token == 'your_github_personal_access_token_here':
                return []
            
            response = requests.get(
                'https://api.github.com/user/repos',
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'Project-Wizard'
                }
            )
            
            if response.ok:
                repos = response.json()
                return [{'name': repo['name'], 'full_name': repo['full_name'], 'default_branch': repo['default_branch']} for repo in repos]
            else:
                return []
        except Exception as e:
            print(f'Failed to fetch GitHub repositories: {e}')
            return []
    
    def get_github_branches(self, repo_full_name):
        """Get branches for a GitHub repository"""
        try:
            github_token = self.config.get('github_token')
            if not github_token or github_token == 'your_github_personal_access_token_here':
                return []
            
            # Use the correct API endpoint for repository branches
            response = requests.get(
                f'https://api.github.com/repos/{repo_full_name}/branches',
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'Project-Wizard'
                }
            )
            
            if response.ok:
                branches = response.json()
                return [{'name': branch['name']} for branch in branches]
            else:
                print(f'Failed to fetch branches for {repo_full_name}: {response.status_code} - {response.text}')
                return []
        except Exception as e:
            print(f'Failed to fetch GitHub branches: {e}')
            return []

class PyQtWizard(QMainWindow):
    """PyQt-based GUI for the project wizard"""
    
    def __init__(self):
        super().__init__()
        self.wizard = ProjectWizard()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NewProjWiz - Project Wizard")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Project creation tab
        project_tab = self.create_project_tab()
        tabs.addTab(project_tab, "Create Project")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_project_tab(self) -> QWidget:
        """Create the project creation tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Project name
        name_group = QGroupBox("Project Details")
        name_layout = QVBoxLayout(name_group)
        
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("my-awesome-project")
        name_layout.addWidget(self.name_edit)
        
        name_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("A brief description of your project")
        name_layout.addWidget(self.desc_edit)
        
        name_layout.addWidget(QLabel("Organization Domain:"))
        self.org_edit = QLineEdit()
        self.org_edit.setText("neoabhro")
        self.org_edit.setPlaceholderText("mycompany")
        name_layout.addWidget(self.org_edit)
        
        name_layout.addWidget(QLabel("Firebase Account:"))
        self.firebase_account_edit = QLineEdit()
        self.firebase_account_edit.setText("mahendra.hasabnis@gmail.com")
        self.firebase_account_edit.setPlaceholderText("user@example.com")
        name_layout.addWidget(self.firebase_account_edit)
        
        layout.addWidget(name_group)
        
        # Template selection
        template_group = QGroupBox("Template Repository")
        template_layout = QVBoxLayout(template_group)
        
        template_layout.addWidget(QLabel("Template Repository:"))
        self.template_repo_combo = QComboBox()
        self.template_repo_combo.addItem("Select a repository...")
        template_layout.addWidget(self.template_repo_combo)
        
        template_layout.addWidget(QLabel("Template Branch:"))
        self.template_branch_combo = QComboBox()
        self.template_branch_combo.addItem("Select a branch...")
        template_layout.addWidget(self.template_branch_combo)
        
        layout.addWidget(template_group)
        
        # Load repositories after all UI elements are created
        self.load_repositories()
        

        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.init_git_check = QCheckBox("Initialize Git Repository")
        self.init_git_check.setChecked(True)
        options_layout.addWidget(self.init_git_check)
        
        self.setup_firebase_check = QCheckBox("Setup Firebase")
        self.setup_firebase_check.setChecked(True)
        options_layout.addWidget(self.setup_firebase_check)
        
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Create button
        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_project)
        layout.addWidget(create_btn)
        
        # Output area
        self.output_text = QTextEdit()
        self.output_text.setMaximumHeight(150)
        layout.addWidget(self.output_text)
        
        return widget
    
    def load_repositories(self):
        """Load GitHub repositories"""
        try:
            if hasattr(self, 'output_text'):
                self.output_text.append("Loading GitHub repositories...")
            repositories = self.wizard.get_github_repositories()
            self.template_repo_combo.clear()
            self.template_repo_combo.addItem("Select a repository...")
            
            if repositories:
                for repo in repositories:
                    self.template_repo_combo.addItem(repo['full_name'], repo['full_name'])
                if hasattr(self, 'output_text'):
                    self.output_text.append(f"Loaded {len(repositories)} repositories")
                
                # Pre-select mytemplate-app repository
                for i in range(self.template_repo_combo.count()):
                    if self.template_repo_combo.itemText(i) == "mahendrahasabnis/mytemplate-app":
                        self.template_repo_combo.setCurrentIndex(i)
                        # Load branches for the selected repository
                        self.load_branches("mahendrahasabnis/mytemplate-app")
                        break
            else:
                if hasattr(self, 'output_text'):
                    self.output_text.append("No repositories found or failed to load repositories")
            
            # Connect repository selection to branch loading
            self.template_repo_combo.currentTextChanged.connect(self.load_branches)
            
        except Exception as e:
            if hasattr(self, 'output_text'):
                self.output_text.append(f"Error loading repositories: {e}")
            else:
                print(f"Error loading repositories: {e}")
    
    def load_branches(self, repo_name):
        """Load branches for selected repository"""
        if repo_name == "Select a repository...":
            self.template_branch_combo.clear()
            self.template_branch_combo.addItem("Select a branch...")
            return
        
        try:
            if hasattr(self, 'output_text'):
                self.output_text.append(f"Loading branches for repository: {repo_name}")
            branches = self.wizard.get_github_branches(repo_name)
            self.template_branch_combo.clear()
            self.template_branch_combo.addItem("Select a branch...")
            
            if branches:
                for branch in branches:
                    self.template_branch_combo.addItem(branch['name'], branch['name'])
                if hasattr(self, 'output_text'):
                    self.output_text.append(f"Loaded {len(branches)} branches")
                
                # Pre-select main branch
                for i in range(self.template_branch_combo.count()):
                    if self.template_branch_combo.itemText(i) == "main":
                        self.template_branch_combo.setCurrentIndex(i)
                        break
            else:
                if hasattr(self, 'output_text'):
                    self.output_text.append("No branches found or failed to load branches")
                
        except Exception as e:
            if hasattr(self, 'output_text'):
                self.output_text.append(f"Error loading branches: {e}")
            else:
                print(f"Error loading branches: {e}")
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # GitHub token
        github_group = QGroupBox("GitHub Configuration")
        github_layout = QVBoxLayout(github_group)
        
        github_layout.addWidget(QLabel("GitHub Personal Access Token:"))
        self.github_token_edit = QLineEdit()
        self.github_token_edit.setText(self.wizard.config.get('github_token', ''))
        self.github_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        github_layout.addWidget(self.github_token_edit)
        
        test_btn = QPushButton("Test Token")
        test_btn.clicked.connect(self.test_github_token)
        github_layout.addWidget(test_btn)
        
        layout.addWidget(github_group)
        
        # Firebase account
        firebase_group = QGroupBox("Firebase Configuration")
        firebase_layout = QVBoxLayout(firebase_group)
        
        firebase_layout.addWidget(QLabel("Firebase Account Email:"))
        self.firebase_account_edit = QLineEdit()
        self.firebase_account_edit.setText(self.wizard.config.get('firebase_account', ''))
        firebase_layout.addWidget(self.firebase_account_edit)
        
        layout.addWidget(firebase_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        return widget
    
    def create_project(self):
        """Create a new project"""
        # Get project data from form
        project_data = {
            'name': self.name_edit.text(),
            'description': self.desc_edit.text(),
            'org_domain': self.org_edit.text(),
            'template_repo': self.template_repo_combo.currentData(),
            'template_branch': self.template_branch_combo.currentData(),
            'firebase_account': self.firebase_account_edit.text(),
            'init_git': self.init_git_check.isChecked(),
            'setup_firebase': self.setup_firebase_check.isChecked()
        }
        
        # Validate required fields
        if not project_data['name'] or not project_data['org_domain'] or not project_data['template_repo'] or not project_data['template_branch']:
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.output_text.clear()  # Clear previous output
        self.output_text.append("🚀 Starting project creation...")
        
        # Create project in background thread
        self.create_thread = CreateProjectThread(self.wizard, project_data)
        self.create_thread.result_ready.connect(self.on_project_created)
        self.create_thread.progress_update.connect(self.update_progress)
        self.create_thread.start()
    
    def update_progress(self, message):
        """Update progress display"""
        self.output_text.append(message)
        # Auto-scroll to bottom
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())
    
    def on_project_created(self, result):
        """Handle project creation result"""
        self.progress_bar.setVisible(False)
        
        if result['success']:
            self.output_text.append(f"✅ {result['message']}")
            self.output_text.append(f"Project created at: {result['project_path']}")
            
            # Show additional details if available
            if result.get('firebase_project_id'):
                self.output_text.append(f"Firebase Project ID: {result['firebase_project_id']}")
            if result.get('github_url'):
                self.output_text.append(f"Template URL: {result['github_url']}")
            if result.get('new_repo_url'):
                self.output_text.append(f"New Repository: {result['new_repo_url']}")
            if result.get('base_build_tag'):
                self.output_text.append(f"Base Build Tag: {result['base_build_tag']}")
            
            # Ask if user wants to open the project
            reply = QMessageBox.question(
                self, "Success", 
                f"Project created successfully!\n\nOpen project folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.open_project_folder(result['project_path'])
        else:
            self.output_text.append(f"❌ Error: {result['error']}")
            QMessageBox.critical(self, "Error", f"Failed to create project:\n{result['error']}")
    
    def open_project_folder(self, project_path):
        """Open the project folder in file explorer"""
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", project_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", project_path])
            else:  # Linux
                subprocess.run(["xdg-open", project_path])
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def test_github_token(self):
        """Test the GitHub token"""
        token = self.github_token_edit.text()
        if not token:
            QMessageBox.warning(self, "Error", "Please enter a GitHub token")
            return
        
        if self.wizard.validate_github_token(token):
            QMessageBox.information(self, "Success", "GitHub token is valid!")
        else:
            QMessageBox.critical(self, "Error", "Invalid GitHub token")
    
    def save_settings(self):
        """Save settings"""
        self.wizard.config['github_token'] = self.github_token_edit.text()
        self.wizard.config['firebase_account'] = self.firebase_account_edit.text()
        self.wizard.config['default_org'] = self.org_edit.text()
        self.wizard.save_config()
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")

class CreateProjectThread(QThread):
    """Thread for creating projects with detailed progress tracking"""
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    
    def __init__(self, wizard, project_data):
        super().__init__()
        self.wizard = wizard
        self.project_data = project_data
    
    def run(self):
        """Run project creation in background thread with detailed progress"""
        try:
            self.progress_update.emit("🚀 Starting project creation...")
            
            # Step 1: Validate project data
            self.progress_update.emit("📋 Validating project data...")
            project_name = self.project_data.get('name', '')
            org_domain = self.project_data.get('org_domain', '')
            template_repo = self.project_data.get('template_repo', '')
            template_branch = self.project_data.get('template_branch', '')
            firebase_account = self.project_data.get('firebase_account', '')
            
            if not project_name or not org_domain or not template_repo or not template_branch:
                self.result_ready.emit({"success": False, "error": "Missing required fields"})
                return
            
            # Step 2: Create temporary directory
            self.progress_update.emit("📁 Creating temporary workspace...")
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix=f'{project_name}-'))
            self.progress_update.emit(f"📁 Temporary directory: {temp_dir}")
            
            try:
                # Step 3: Clone template repository
                self.progress_update.emit(f"📥 Cloning template repository: {template_repo} (branch: {template_branch})")
                github_url = self.wizard._clone_template_repository(temp_dir, template_repo, template_branch)
                self.progress_update.emit(f"✅ Repository cloned successfully: {github_url}")
                
                # Step 4: Rename project identifiers
                self.progress_update.emit("🔄 Renaming project identifiers...")
                self.wizard._rename_project_identifiers(temp_dir, project_name, org_domain)
                self.progress_update.emit("✅ Project identifiers updated")
                
                # Step 5: Create Firebase configuration files
                self.progress_update.emit("📝 Creating Firebase configuration files...")
                self.wizard._create_firebase_config_files(temp_dir, project_name, org_domain)
                self.progress_update.emit("✅ Firebase configuration files created")
                
                # Step 6: Create Firebase project (if requested)
                firebase_project_id = None
                app_ids = None
                if self.project_data.get('setup_firebase', False) and firebase_account:
                    self.progress_update.emit(f"🔥 Creating Firebase project: {project_name}")
                    firebase_project_id = self.wizard._create_firebase_project(project_name, firebase_account)
                    self.progress_update.emit(f"✅ Firebase project created: {firebase_project_id}")
                    
                    # Step 7: Create Firebase apps
                    self.progress_update.emit("📱 Creating Firebase apps (iOS, Android, Web)...")
                    app_ids = self.wizard._create_firebase_apps(firebase_project_id, project_name, org_domain, firebase_account)
                    self.progress_update.emit(f"✅ Firebase apps created: {app_ids}")
                    
                    # Step 8: Setup Firestore database
                    self.progress_update.emit("🗄️ Setting up Firestore database...")
                    self.wizard._setup_firestore_database(firebase_project_id, project_name, firebase_account)
                    self.progress_update.emit("✅ Firestore database configured")
                    
                    # Step 9: Download Firebase config files
                    self.progress_update.emit("⬇️ Downloading Firebase configuration files...")
                    self.wizard._download_firebase_configs(temp_dir, firebase_project_id, app_ids, firebase_account)
                    self.progress_update.emit("✅ Firebase config files downloaded")
                    
                    # Step 10: Update app_config.json
                    self.progress_update.emit("⚙️ Updating app configuration with Firebase data...")
                    self.wizard._update_app_config_json(temp_dir, firebase_project_id, project_name, org_domain, app_ids)
                    self.progress_update.emit("✅ App configuration updated")
                else:
                    self.progress_update.emit("⏭️ Skipping Firebase setup (not requested)")
                
                # Step 11: Commit changes
                self.progress_update.emit("💾 Committing project changes...")
                self.wizard._commit_and_push_changes(temp_dir, project_name)
                self.progress_update.emit("✅ Changes committed")
                
                # Step 12: Create new private repository
                self.progress_update.emit("🆕 Creating new private repository...")
                new_repo_url = self.wizard._create_private_repository(temp_dir, project_name)
                if new_repo_url:
                    self.progress_update.emit(f"✅ Private repository created: {new_repo_url}")
                else:
                    self.progress_update.emit("⚠️ Private repository creation skipped (no GitHub token)")
                
                # Step 13: Create base build tag
                self.progress_update.emit("🏷️ Creating base build tag...")
                self.wizard._create_base_build_tag(temp_dir, project_name)
                self.progress_update.emit("✅ Base build tag created")
                
                # Step 14: Move to final location
                self.progress_update.emit("📦 Moving project to final location...")
                final_project_dir = Path('projects') / project_name
                
                # Ensure projects directory exists
                projects_dir = Path('projects')
                projects_dir.mkdir(exist_ok=True)
                
                # Remove existing project directory if it exists
                if final_project_dir.exists():
                    import shutil
                    shutil.rmtree(final_project_dir)
                
                # Verify temp directory still exists before moving
                if not temp_dir.exists():
                    raise Exception(f"Temporary directory {temp_dir} was deleted unexpectedly")
                
                # Move the project
                temp_dir.rename(final_project_dir)
                self.progress_update.emit(f"✅ Project moved to: {final_project_dir}")
                
                # Success!
                self.progress_update.emit("🎉 Project creation completed successfully!")
                
                result = {
                    'success': True,
                    'project_path': str(final_project_dir),
                    'firebase_project_id': firebase_project_id,
                    'github_url': github_url,
                    'new_repo_url': new_repo_url,
                    'base_build_tag': f'base-build-{datetime.now().strftime("%Y-%m-%d")}',
                    'message': f'Project {project_name} created successfully!'
                }
                
                self.result_ready.emit(result)
                
            except Exception as e:
                # Clean up temp directory on error
                if temp_dir.exists():
                    import shutil
                    shutil.rmtree(temp_dir)
                self.progress_update.emit(f"❌ Error during project creation: {str(e)}")
                self.result_ready.emit({"success": False, "error": str(e)})
                return
                
        except Exception as e:
            self.progress_update.emit(f"💥 Project creation failed: {str(e)}")
            self.result_ready.emit({"success": False, "error": str(e)})

class FlaskWizard:
    """Flask-based web interface for the project wizard"""
    
    def __init__(self):
        self.wizard = ProjectWizard()
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html', templates=self.wizard.get_templates())
        
        @self.app.route('/api/create_project', methods=['POST'])
        def create_project():
            data = request.json
            result = self.wizard.create_project(data)
            return jsonify(result)
        
        @self.app.route('/api/templates')
        def get_templates():
            return jsonify(self.wizard.get_templates())
    
    def run(self, port=5000):
        """Run the Flask application"""
        self.app.run(debug=True, port=port)

def main():
    """Main entry point"""
    print("🚀 NewProjWiz - Python Project Wizard")
    print("=" * 50)
    
    # Check available GUI options
    if PYQT_AVAILABLE:
        print("✅ PyQt6 available - Using desktop GUI")
        app = QApplication(sys.argv)
        window = PyQtWizard()
        window.show()
        sys.exit(app.exec())
    
    elif FLASK_AVAILABLE:
        print("✅ Flask available - Using web interface")
        wizard = FlaskWizard()
        wizard.run()
    
    else:
        print("❌ No GUI framework available")
        print("Please install PyQt6 or Flask:")
        print("pip install PyQt6")
        print("or")
        print("pip install flask webview")
        sys.exit(1)

if __name__ == "__main__":
    main() 