#!/usr/bin/env python3
"""
Test Firebase CLI functionality
"""

import subprocess
import sys

def test_firebase_cli():
    """Test Firebase CLI commands"""
    print("🧪 Testing Firebase CLI...")
    
    # Test 1: Check if Firebase CLI is installed
    try:
        result = subprocess.run(['firebase', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"✅ Firebase CLI version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Firebase CLI not found: {e}")
        return False
    
    # Test 2: Check if user is logged in
    try:
        result = subprocess.run(['firebase', 'login:list'], 
                              capture_output=True, text=True, timeout=10)
        print(f"📋 Login status: {result.stdout}")
    except Exception as e:
        print(f"❌ Failed to check login status: {e}")
    
    # Test 3: Test apps:create command syntax
    print("\n🔍 Testing Firebase apps:create command syntax...")
    
    # Test iOS app creation syntax
    try:
        result = subprocess.run([
            'firebase', 'apps:create', '--help'
        ], capture_output=True, text=True, timeout=10)
        print("✅ Firebase apps:create help:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except Exception as e:
        print(f"❌ Failed to get apps:create help: {e}")
    
    return True

if __name__ == "__main__":
    test_firebase_cli() 