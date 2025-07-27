#!/usr/bin/env python3
"""
Script to set up GitHub repository for NewProjWiz project
"""

import json
import requests
import subprocess
import sys
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def get_github_username(token):
    """Get GitHub username from token"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            return response.json()['login']
        else:
            print(f"Error getting GitHub username: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_github_repository(token, username, repo_name, description):
    """Create a new GitHub repository"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': repo_name,
        'description': description,
        'private': False,
        'auto_init': False,
        'gitignore_template': None,
        'license_template': None
    }
    
    try:
        response = requests.post(
            f'https://api.github.com/user/repos',
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            repo_data = response.json()
            return repo_data['html_url']
        else:
            print(f"Error creating repository: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def setup_git_remote(repo_url):
    """Set up Git remote and push code"""
    try:
        # Add remote origin
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        print(f"✅ Added remote origin: {repo_url}")
        
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ Successfully pushed code to GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up Git remote: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Setting up GitHub repository for NewProjWiz")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    github_token = config.get('github_token')
    
    if not github_token:
        print("❌ GitHub token not found in config.json")
        sys.exit(1)
    
    # Get GitHub username
    username = get_github_username(github_token)
    if not username:
        print("❌ Could not get GitHub username")
        sys.exit(1)
    
    print(f"✅ GitHub username: {username}")
    
    # Repository details
    repo_name = "newprojectwizard"
    description = "A comprehensive project creation wizard with Firebase and GitHub integration"
    
    print(f"📝 Repository name: {repo_name}")
    print(f"📝 Description: {description}")
    
    # Create repository
    print("\n🔄 Creating GitHub repository...")
    repo_url = create_github_repository(github_token, username, repo_name, description)
    
    if not repo_url:
        print("❌ Failed to create GitHub repository")
        sys.exit(1)
    
    print(f"✅ Repository created: {repo_url}")
    
    # Set up Git remote and push
    print("\n🔄 Setting up Git remote and pushing code...")
    if setup_git_remote(repo_url):
        print("\n🎉 Success! Your code is now on GitHub:")
        print(f"   Repository: {repo_url}")
        print(f"   Clone URL: {repo_url}.git")
    else:
        print("❌ Failed to push code to GitHub")

if __name__ == "__main__":
    main() 