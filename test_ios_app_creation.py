#!/usr/bin/env python3
"""
Test iOS app creation with stdin input
"""

import subprocess
import sys

def test_ios_app_creation():
    """Test iOS app creation with stdin input"""
    print("🧪 Testing iOS app creation with stdin input...")
    
    # Test project ID (use an existing project)
    project_id = "perfectplay-619658"
    firebase_account = "mahendra.hasabnis@gmail.com"
    bundle_id = "com.test.iosapp6"
    app_name = "test-ios-app-6"
    
    print(f"Testing with project: {project_id}")
    print(f"Bundle ID: {bundle_id}")
    print(f"App name: {app_name}")
    
    try:
        # Test iOS app creation with stdin input
        result = subprocess.run([
            'firebase', '--account', firebase_account,
            'apps:create', 'ios',
            app_name,
            '--bundle-id', bundle_id,
            '--project', project_id
        ], capture_output=True, text=True, timeout=30, input='\n')
        
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
        if result.returncode == 0:
            print("✅ iOS app creation successful!")
        else:
            print("❌ iOS app creation failed")
            
    except subprocess.TimeoutExpired:
        print("❌ iOS app creation timed out")
    except Exception as e:
        print(f"❌ iOS app creation failed: {e}")

if __name__ == "__main__":
    test_ios_app_creation() 