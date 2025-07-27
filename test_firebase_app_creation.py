#!/usr/bin/env python3
"""
Test Firebase app creation commands
"""

import subprocess
import sys

def test_firebase_app_creation():
    """Test Firebase app creation commands"""
    print("🧪 Testing Firebase app creation...")
    
    # Test project ID (use an existing project)
    project_id = "mplay-565448"  # Use the project that was created earlier
    firebase_account = "mahendra.hasabnis@gmail.com"
    
    print(f"Testing with project: {project_id}")
    print(f"Firebase account: {firebase_account}")
    
    # Test 1: iOS app creation
    print("\n📱 Testing iOS app creation...")
    try:
        result = subprocess.run([
            'firebase', '--account', firebase_account,
            'apps:create', 'IOS', 'test-ios-app',
            '--bundle-id', 'com.test.iosapp',
            '--project', project_id
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ iOS app creation timed out")
    except Exception as e:
        print(f"❌ iOS app creation failed: {e}")
    
    # Test 2: Android app creation
    print("\n🤖 Testing Android app creation...")
    try:
        result = subprocess.run([
            'firebase', '--account', firebase_account,
            'apps:create', 'ANDROID', 'test-android-app',
            '--package-name', 'com.test.androidapp',
            '--project', project_id
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Android app creation timed out")
    except Exception as e:
        print(f"❌ Android app creation failed: {e}")
    
    # Test 3: Web app creation
    print("\n🌐 Testing Web app creation...")
    try:
        result = subprocess.run([
            'firebase', '--account', firebase_account,
            'apps:create', 'WEB', 'test-web-app',
            '--project', project_id
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Web app creation timed out")
    except Exception as e:
        print(f"❌ Web app creation failed: {e}")

if __name__ == "__main__":
    test_firebase_app_creation() 