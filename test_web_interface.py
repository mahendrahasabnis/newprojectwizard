#!/usr/bin/env python3
"""
Test script for the Flask web interface
"""

import sys
import subprocess

def test_web_interface():
    """Test the Flask web interface"""
    print("🧪 Testing Flask Web Interface...")
    
    try:
        # Import Flask
        from flask import Flask
        print("✅ Flask is available")
        
        # Test the web interface
        from python_wizard import FlaskWizard
        
        print("🚀 Starting Flask web interface...")
        print("📱 Open your browser to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop")
        
        wizard = FlaskWizard()
        wizard.run(port=5000)
        
    except ImportError as e:
        print(f"❌ Flask not available: {e}")
        print("Install with: pip3 install flask")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_web_interface() 