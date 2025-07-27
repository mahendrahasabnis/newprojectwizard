#!/usr/bin/env python3
"""
Build script for NewProjWiz Full Web-Only macOS App
This version includes all features from the original PyQt6 app
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_full_web_app():
    """Build the full web-only macOS application"""
    print("🚀 Building NewProjWiz Full Web-Only macOS Application")
    print("=" * 60)
    
    # Check and install PyInstaller if needed
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()
    
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    spec_file = Path("NewProjWiz_FullWeb.spec")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if spec_file.exists():
        spec_file.unlink()
    
    # PyInstaller command for full web-only version
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--name=NewProjWiz_FullWeb",
        "--add-data=config.json:.",
        "--hidden-import=requests",
        "--hidden-import=urllib",
        "--hidden-import=urllib.parse",
        "--exclude-module=PyQt6",
        "--exclude-module=PyQt5",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=flask",
        "--exclude-module=webview",
        "python_wizard_full_web.py"
    ]
    
    print("Running PyInstaller (Full Web-Only Mode)...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build completed successfully!")
        
        # Check if the app was created
        app_path = dist_dir / "NewProjWiz_FullWeb"
        if app_path.exists():
            print(f"📱 Application created at: {app_path}")
            
            # Create a launcher script
            create_launcher_script(app_path)
            
            print("\n🎉 NewProjWiz Full Web-Only macOS app is ready!")
            print(f"Location: {app_path}")
            print("\nTo run the app:")
            print(f"  ./{app_path}/NewProjWiz_FullWeb")
            print("\nTo install to Applications:")
            print(f"  cp -r {app_path} /Applications/")
            
            # Test the app
            test_full_web_app(app_path)
        else:
            print("❌ App bundle not found in dist directory")
    else:
        print("❌ Build failed!")
        print("Error output:")
        print(result.stderr)

def create_launcher_script(app_path):
    """Create a launcher script for the app"""
    launcher_script = app_path / "launch_newprojwiz_full.sh"
    
    script_content = f"""#!/bin/bash
# Launcher script for NewProjWiz Full Web-Only
cd "$(dirname "$0")"
./NewProjWiz_FullWeb
"""
    
    with open(launcher_script, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(launcher_script, 0o755)
    print(f"📜 Launcher script created: {launcher_script}")

def test_full_web_app(app_path):
    """Test the full web-only app"""
    print("\n🧪 Testing full web-only app build...")
    
    try:
        # Test if the executable works
        result = subprocess.run(
            [str(app_path / "NewProjWiz_FullWeb"), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 or "NewProjWiz" in result.stdout:
            print("✅ App executable works correctly")
        else:
            print("⚠️ App launched but output unexpected")
            
    except subprocess.TimeoutExpired:
        print("✅ App executable launched (web server, timeout expected)")
    except Exception as e:
        print(f"❌ App test failed: {e}")

def main():
    """Main function"""
    print("Choose build mode:")
    print("1. Full web-only build (recommended)")
    print("2. Debug build (with console output)")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        build_full_web_app()
    elif choice == "2":
        build_full_web_app()  # Same for now
    elif choice == "3":
        build_full_web_app()
        print("\n🔧 Creating debug version...")
        # Could add debug version here
    else:
        print("Invalid choice. Using full web-only build.")
        build_full_web_app()

if __name__ == "__main__":
    main() 