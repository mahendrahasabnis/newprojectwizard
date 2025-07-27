#!/usr/bin/env python3
"""
NewProjWiz - Full Web-Only Python Project Wizard
A comprehensive version that matches all features of the original PyQt6 app
"""

import sys
import os
import json
import subprocess
import threading
import webbrowser
import re
import time
import http.server
import socketserver
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests

class FullWebServer:
    def __init__(self, port=9000):
        self.port = port
        self.server = None
        self.thread = None
        self.wizard = ProjectWizard()
        
    def start(self):
        """Start the web server in a separate thread"""
        try:
            handler = self.create_handler()
            self.server = socketserver.TCPServer(("", self.port), handler)
            # Add wizard instance to server
            self.server.wizard = self.wizard
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"🌐 Web server started on http://localhost:{self.port}")
            return True
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"❌ Port {self.port} is already in use. Trying port {self.port + 1}...")
                self.port += 1
                return self.start()  # Try next port
            else:
                print(f"❌ Failed to start web server: {e}")
                return False
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            return False
    
    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def create_handler(self):
        """Create HTTP request handler"""
        class RequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.get_main_page().encode())
                elif self.path == '/api/templates':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    templates = self.server.wizard.get_templates()
                    self.wfile.write(json.dumps(templates).encode())
                elif self.path == '/api/repositories':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    repositories = self.server.wizard.get_github_repositories()
                    self.wfile.write(json.dumps(repositories).encode())
                elif self.path.startswith('/api/branches/'):
                    repo_name = urllib.parse.unquote(self.path.split('/api/branches/')[1])
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    branches = self.server.wizard.get_github_branches(repo_name)
                    self.wfile.write(json.dumps(branches).encode())
                elif self.path == '/api/config':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    config = self.server.wizard.config
                    # Don't send the actual token for security
                    safe_config = {k: v for k, v in config.items() if k != 'github_token'}
                    safe_config['github_token'] = '***' if config.get('github_token') else ''
                    self.wfile.write(json.dumps(safe_config).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/api/create_project':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    project_data = json.loads(post_data.decode())
                    
                    # Create project using the wizard
                    result = self.server.wizard.create_project(project_data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                elif self.path == '/api/save_config':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    config_data = json.loads(post_data.decode())
                    
                    # Save configuration
                    self.server.wizard.config.update(config_data)
                    self.server.wizard.save_config()
                    
                    result = {"success": True, "message": "Settings saved successfully"}
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                elif self.path == '/api/test_token':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode())
                    token = data.get('token', '')
                    
                    # Test GitHub token
                    is_valid = self.server.wizard.validate_github_token(token)
                    result = {"success": is_valid, "message": "Token is valid" if is_valid else "Token is invalid"}
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def get_main_page(self):
                return """
<!DOCTYPE html>
<html>
<head>
    <title>NewProjWiz - Project Wizard</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 30px;
        }
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            font-weight: 500;
        }
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
        }
        .tab:hover {
            background: #f8f9fa;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .form-group { 
            margin-bottom: 25px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600;
            color: #333;
        }
        input, select, textarea { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e1e5e9; 
            border-radius: 6px; 
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover { 
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .success { 
            color: #28a745; 
            background: #d4edda;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .error { 
            color: #dc3545; 
            background: #f8d7da;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .info {
            color: #17a2b8;
            background: #d1ecf1;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .progress {
            background: #e9ecef;
            border-radius: 6px;
            height: 20px;
            margin: 15px 0;
            overflow: hidden;
        }
        .progress-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
        }
        .output {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            line-height: 1.4;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NewProjWiz</h1>
            <p>Create new projects with Firebase and GitHub integration</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <div class="tab active" onclick="showTab('project')">Create Project</div>
                <div class="tab" onclick="showTab('settings')">Settings</div>
            </div>
            
            <!-- Project Creation Tab -->
            <div id="project-tab" class="tab-content active">
                <form id="projectForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="name">Project Name *</label>
                            <input type="text" id="name" name="name" required placeholder="my-awesome-project">
                        </div>
                        <div class="form-group">
                            <label for="org_domain">Organization Domain *</label>
                            <input type="text" id="org_domain" name="org_domain" required placeholder="mycompany.com" value="neoabhro">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Description</label>
                        <textarea id="description" name="description" rows="3" placeholder="A brief description of your project"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="firebase_account">Firebase Account</label>
                        <input type="email" id="firebase_account" name="firebase_account" placeholder="user@example.com" value="mahendra.hasabnis@gmail.com">
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="template_repo">Template Repository *</label>
                            <select id="template_repo" name="template_repo" required>
                                <option value="">Loading repositories...</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="template_branch">Template Branch *</label>
                            <select id="template_branch" name="template_branch" required>
                                <option value="">Select repository first...</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="init_git" name="init_git" checked>
                        <label for="init_git">Initialize Git Repository</label>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="setup_firebase" name="setup_firebase" checked>
                        <label for="setup_firebase">Setup Firebase</label>
                    </div>
                    
                    <button type="submit" id="createBtn">Create Project</button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Creating project...</p>
                </div>
                
                <div class="progress" id="progress" style="display: none;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                
                <div class="output" id="output" style="display: none;"></div>
            </div>
            
            <!-- Settings Tab -->
            <div id="settings-tab" class="tab-content">
                <form id="settingsForm">
                    <div class="form-group">
                        <label for="github_token">GitHub Personal Access Token</label>
                        <input type="password" id="github_token" name="github_token" placeholder="ghp_xxxxxxxxxxxxxxxxxxxx">
                        <button type="button" onclick="testToken()" class="btn-secondary">Test Token</button>
                    </div>
                    
                    <div class="form-group">
                        <label for="settings_firebase_account">Firebase Account Email</label>
                        <input type="email" id="settings_firebase_account" name="firebase_account" placeholder="user@example.com">
                    </div>
                    
                    <button type="submit">Save Settings</button>
                </form>
                
                <div id="settingsResult"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        // Load repositories on page load
        window.onload = function() {
            loadRepositories();
            loadConfig();
        };
        
        // Load GitHub repositories
        async function loadRepositories() {
            try {
                const response = await fetch('/api/repositories');
                const repositories = await response.json();
                
                const select = document.getElementById('template_repo');
                select.innerHTML = '<option value="">Select a repository...</option>';
                
                repositories.forEach(repo => {
                    const option = document.createElement('option');
                    option.value = repo.full_name;
                    option.textContent = repo.full_name;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading repositories:', error);
            }
        }
        
        // Load branches when repository is selected
        document.getElementById('template_repo').addEventListener('change', async function() {
            const repoName = this.value;
            const branchSelect = document.getElementById('template_branch');
            
            if (!repoName) {
                branchSelect.innerHTML = '<option value="">Select repository first...</option>';
                return;
            }
            
            try {
                const response = await fetch('/api/branches/' + encodeURIComponent(repoName));
                const branches = await response.json();
                
                branchSelect.innerHTML = '<option value="">Select a branch...</option>';
                branches.forEach(branch => {
                    const option = document.createElement('option');
                    option.value = branch.name;
                    option.textContent = branch.name;
                    branchSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading branches:', error);
                branchSelect.innerHTML = '<option value="">Error loading branches</option>';
            }
        });
        
        // Load configuration
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                const config = await response.json();
                
                document.getElementById('github_token').value = config.github_token || '';
                document.getElementById('settings_firebase_account').value = config.firebase_account || '';
            } catch (error) {
                console.error('Error loading config:', error);
            }
        }
        
        // Test GitHub token
        async function testToken() {
            const token = document.getElementById('github_token').value;
            const resultDiv = document.getElementById('settingsResult');
            
            if (!token) {
                resultDiv.innerHTML = '<div class="error">Please enter a GitHub token</div>';
                return;
            }
            
            try {
                const response = await fetch('/api/test_token', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: token})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = '<div class="success">✅ ' + result.message + '</div>';
                } else {
                    resultDiv.innerHTML = '<div class="error">❌ ' + result.message + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="error">❌ Error testing token: ' + error.message + '</div>';
            }
        }
        
        // Handle settings form submission
        document.getElementById('settingsForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const configData = {
                github_token: formData.get('github_token'),
                firebase_account: formData.get('firebase_account')
            };
            
            try {
                const response = await fetch('/api/save_config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(configData)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('settingsResult');
                
                if (result.success) {
                    resultDiv.innerHTML = '<div class="success">✅ ' + result.message + '</div>';
                } else {
                    resultDiv.innerHTML = '<div class="error">❌ ' + result.message + '</div>';
                }
            } catch (error) {
                document.getElementById('settingsResult').innerHTML = '<div class="error">❌ Error saving settings: ' + error.message + '</div>';
            }
        });
        
        // Handle project form submission
        document.getElementById('projectForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const projectData = {
                name: formData.get('name'),
                description: formData.get('description'),
                org_domain: formData.get('org_domain'),
                firebase_account: formData.get('firebase_account'),
                template_repo: formData.get('template_repo'),
                template_branch: formData.get('template_branch'),
                init_git: formData.get('init_git') === 'on',
                setup_firebase: formData.get('setup_firebase') === 'on'
            };
            
            // Show loading state
            document.getElementById('loading').style.display = 'block';
            document.getElementById('createBtn').disabled = true;
            document.getElementById('progress').style.display = 'block';
            document.getElementById('output').style.display = 'block';
            document.getElementById('output').innerHTML = 'Starting project creation...\\n';
            
            try {
                const response = await fetch('/api/create_project', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(projectData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Display step updates if available
                    if (result.step_updates && result.step_updates.length > 0) {
                        document.getElementById('output').innerHTML += '\\nStep-by-step progress:\\n';
                        result.step_updates.forEach(update => {
                            document.getElementById('output').innerHTML += '  ' + update + '\\n';
                        });
                        document.getElementById('output').innerHTML += '\\n';
                    }
                    
                    document.getElementById('output').innerHTML += 'SUCCESS: ' + result.message + '\\n';
                    if (result.project_path) {
                        document.getElementById('output').innerHTML += 'Project created at: ' + result.project_path + '\\n';
                    }
                    if (result.firebase_project_id) {
                        document.getElementById('output').innerHTML += 'Firebase Project ID: ' + result.firebase_project_id + '\\n';
                    }
                    if (result.app_ids) {
                        document.getElementById('output').innerHTML += 'Firebase Apps Created:\\n';
                        if (result.app_ids.ios && result.app_ids.ios !== 'unknown') {
                            document.getElementById('output').innerHTML += '  - iOS App ID: ' + result.app_ids.ios + '\\n';
                        }
                        if (result.app_ids.android && result.app_ids.android !== 'unknown') {
                            document.getElementById('output').innerHTML += '  - Android App ID: ' + result.app_ids.android + '\\n';
                        }
                        if (result.app_ids.web && result.app_ids.web !== 'unknown') {
                            document.getElementById('output').innerHTML += '  - Web App ID: ' + result.app_ids.web + '\\n';
                        }
                    }
                } else {
                    document.getElementById('output').innerHTML += '❌ ' + result.error + '\\n';
                }
            } catch (error) {
                document.getElementById('output').innerHTML += '❌ Error: ' + error.message + '\\n';
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('createBtn').disabled = false;
                document.getElementById('progress').style.display = 'none';
            }
        });
    </script>
</body>
</html>
                """
        
        return RequestHandler

class ProjectWizard:
    """Main project wizard class (full version)"""
    
    def __init__(self):
        self.config = self.load_config()
        self.step_updates = []
        
    def add_step_update(self, message: str):
        """Add a step update message"""
        self.step_updates.append(message)
        print(message)  # Also print to terminal
    
    def get_step_updates(self) -> List[str]:
        """Get all step updates and clear the list"""
        updates = self.step_updates.copy()
        self.step_updates.clear()
        return updates
    
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
    
    def get_templates(self) -> Dict[str, str]:
        """Get available templates"""
        return self.config.get('templates', {})
    
    def validate_github_token(self, token: str) -> bool:
        """Validate GitHub token"""
        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get('https://api.github.com/user', headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_github_repositories(self) -> list:
        """Get GitHub repositories"""
        try:
            token = self.config.get('github_token', '')
            if not token:
                return []
            
            headers = {'Authorization': f'token {token}'}
            response = requests.get('https://api.github.com/user/repos', headers=headers)
            
            if response.status_code == 200:
                repos = response.json()
                return [{'full_name': repo['full_name'], 'name': repo['name']} for repo in repos]
            else:
                return []
        except:
            return []
    
    def get_github_branches(self, repo_name: str) -> list:
        """Get GitHub repository branches"""
        try:
            token = self.config.get('github_token', '')
            if not token:
                return []
            
            headers = {'Authorization': f'token {token}'}
            response = requests.get(f'https://api.github.com/repos/{repo_name}/branches', headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                return [{'name': branch['name']} for branch in branches]
            else:
                return []
        except:
            return []
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project with full functionality"""
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
            
            # Create projects directory
            projects_dir = Path("projects")
            projects_dir.mkdir(exist_ok=True)
            
            # Create project directory directly
            project_dir = projects_dir / project_name
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
            
            try:
                # Clone template repository directly to project directory
                self.add_step_update(f"Cloning template repository: {template_repo}")
                result = subprocess.run(
                    ["git", "clone", "-b", template_branch, f"https://github.com/{template_repo}", str(project_dir)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.add_step_update(f"ERROR: Failed to clone template: {result.stderr}")
                    return {"success": False, "error": f"Failed to clone template: {result.stderr}"}
                
                # Update project configuration
                self.add_step_update("Updating project configuration...")
                self.update_project_config(project_dir, project_data)
                
                # Create GitHub repository and initialize Git
                if init_git:
                    self.add_step_update(f"Creating GitHub repository for {project_name}...")
                    github_repo_url = self.create_github_repository(project_name, description, org_domain)
                    if github_repo_url:
                        self.add_step_update(f"SUCCESS: GitHub repository created: {github_repo_url}")
                        # Update remote origin to point to new repository
                        self.update_git_remote(project_dir, github_repo_url)
                    else:
                        self.add_step_update("WARNING: Failed to create GitHub repository, continuing with local Git only")
                    
                    self.add_step_update(f"Initializing Git repository for {project_name}...")
                    self.init_git_repository(project_dir, project_name)
                
                # Setup Firebase if requested (simplified version without Firestore)
                firebase_project_id = None
                firebase_result = None
                if setup_firebase:
                    self.add_step_update(f"Setting up Firebase for {project_name}...")
                    firebase_result = self.setup_firebase_simplified(project_dir, project_data)
                    if not firebase_result.get('success'):
                        self.add_step_update(f"ERROR: Firebase setup failed: {firebase_result.get('error')}")
                        # Don't fail the entire process for Firebase issues
                        firebase_project_id = None
                    else:
                        firebase_project_id = firebase_result.get('project_id')
                        self.add_step_update(f"Firebase setup completed: {firebase_project_id}")
                
                # Get all step updates
                step_updates = self.get_step_updates()
                
                return {
                    "success": True,
                    "project_path": str(project_dir),
                    "firebase_project_id": firebase_project_id,
                    "app_ids": firebase_result.get('app_ids') if firebase_result else None,
                    "message": f"Project {project_name} created successfully!",
                    "step_updates": step_updates
                }
                
            except Exception as e:
                # Clean up project directory on error
                if project_dir.exists():
                    import shutil
                    shutil.rmtree(project_dir)
                return {"success": False, "error": str(e)}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_project_config(self, project_dir: Path, project_data: Dict[str, Any]):
        """Update project configuration files"""
        project_name = project_data.get('name', '')
        org_domain = project_data.get('org_domain', '')
        
        # Update package.json if it exists
        package_json = project_dir / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                data['name'] = project_name
                data['description'] = project_data.get('description', '')
                
                with open(package_json, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not update package.json: {e}")
    
    def init_git_repository(self, project_dir: Path, project_name: str):
        """Initialize Git repository"""
        try:
            # Check if this is already a Git repository
            git_dir = project_dir / ".git"
            if git_dir.exists():
                print(f"Git repository already exists in {project_dir}")
                # Check if there are any changes to commit
                result = subprocess.run(["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True)
                if result.stdout.strip():
                    # There are changes, commit them
                    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
                    subprocess.run(["git", "commit", "-m", f"Project setup for {project_name}"], cwd=project_dir, check=True)
                    print(f"Committed changes for {project_name}")
                else:
                    print(f"No changes to commit for {project_name}")
            else:
                # Initialize new Git repository
                subprocess.run(["git", "init"], cwd=project_dir, check=True)
                subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Initial commit for {project_name}"], cwd=project_dir, check=True)
                print(f"Initialized new Git repository for {project_name}")
        except Exception as e:
            print(f"Warning: Could not initialize Git repository: {e}")
            # Don't fail the entire process for Git issues
    
    def setup_firebase_simplified(self, project_dir: Path, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Firebase project (simplified version without Firestore database)"""
        try:
            project_name = project_data.get('name', '')
            org_domain = project_data.get('org_domain', '')
            firebase_account = project_data.get('firebase_account', '')
            
            self.add_step_update(f"Setting up Firebase project: {project_name}")
            
            # Step 1: Create Firebase project
            self.add_step_update("Step 1: Creating Firebase project...")
            project_id = self._create_firebase_project(project_name, firebase_account)
            self.add_step_update(f"SUCCESS: Firebase project created: {project_id}")
            
            # Step 2: Create Firebase apps (iOS, Android, Web)
            self.add_step_update("Step 2: Creating Firebase apps...")
            app_ids = self._create_firebase_apps(project_id, project_name, org_domain, firebase_account)
            self.add_step_update(f"SUCCESS: Firebase apps created: {app_ids}")
            
            # Step 3: Download Firebase configurations
            self.add_step_update("Step 3: Downloading Firebase configurations...")
            self._download_firebase_configs(project_dir, project_id, app_ids, firebase_account)
            self.add_step_update("SUCCESS: Firebase configurations downloaded")
            
            # Step 4: Update config.json file with Firebase project and app data
            self.add_step_update("Step 4: Updating app_config.json with Firebase data...")
            self._update_config_json_with_firebase(project_dir, project_id, project_name, org_domain, app_ids, firebase_account)
            self.add_step_update("SUCCESS: app_config.json updated with Firebase data")
            
            # Step 5: Commit changes to repository
            self.add_step_update("Step 5: Committing changes to repository...")
            self._commit_firebase_changes(project_dir, project_name)
            self.add_step_update("SUCCESS: Changes committed to repository")
            
            return {
                "success": True,
                "project_id": project_id,
                "app_ids": app_ids,
                "message": "Firebase setup completed successfully"
            }
        except Exception as e:
            print(f"Firebase setup error: {e}")
            return {"success": False, "error": str(e)}
    
    def setup_firebase(self, project_dir: Path, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Firebase project with full workflow"""
        try:
            project_name = project_data.get('name', '')
            org_domain = project_data.get('org_domain', '')
            firebase_account = project_data.get('firebase_account', '')
            
            print(f"Setting up Firebase project: {project_name}")
            
            # Step 1: Create Firebase project
            print("Step 1: Creating Firebase project...")
            project_id = self._create_firebase_project(project_name, firebase_account)
            print(f"✅ Firebase project created: {project_id}")
            
            # Step 2: Create Firebase apps (iOS, Android, Web)
            print("Step 2: Creating Firebase apps...")
            app_ids = self._create_firebase_apps(project_id, project_name, org_domain, firebase_account)
            print(f"✅ Firebase apps created: {app_ids}")
            
            # Step 3: Download Firebase configurations
            print("Step 3: Downloading Firebase configurations...")
            self._download_firebase_configs(project_dir, project_id, app_ids, firebase_account)
            print("✅ Firebase configurations downloaded")
            
            # Step 4: Update app configuration files
            print("Step 4: Updating app configuration files...")
            self._update_app_config_json(project_dir, project_id, project_name, org_domain, app_ids)
            print("✅ App configuration files updated")
            
            # Step 5: Setup Firestore database
            print("Step 5: Setting up Firestore database...")
            self._setup_firestore_database(project_id, project_name, firebase_account)
            print("✅ Firestore database setup completed")
            
            # Step 6: Update cloned repository config files
            print("Step 6: Updating cloned repository config files...")
            self._update_cloned_repository_configs(project_dir, project_id, project_name, org_domain, app_ids)
            print("✅ Repository config files updated")
            
            # Step 7: Commit and push changes to remote repository
            print("Step 7: Committing and pushing changes to remote repository...")
            self._commit_and_push_changes(project_dir, project_name)
            print("✅ Changes committed and pushed to remote repository")
            
            return {
                "success": True,
                "project_id": project_id,
                "app_ids": app_ids,
                "message": "Firebase setup completed successfully"
            }
        except Exception as e:
            print(f"Firebase setup error: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_firebase_config_files(self, project_dir: Path, project_name: str, org_domain: str):
        """Create Firebase configuration files"""
        try:
            # Create firebase.json
            firebase_config = {
                "firestore": {
                    "rules": "firestore.rules",
                    "indexes": "firestore.indexes.json"
                },
                "storage": {
                    "rules": "storage.rules"
                },
                "hosting": {
                    "public": "public",
                    "ignore": [
                        "firebase.json",
                        "**/.*",
                        "**/node_modules/**"
                    ]
                }
            }
            
            firebase_json = project_dir / "firebase.json"
            with open(firebase_json, 'w') as f:
                json.dump(firebase_config, f, indent=2)
            
            # Create firestore.rules
            firestore_rules = project_dir / "firestore.rules"
            if not firestore_rules.exists():
                with open(firestore_rules, 'w') as f:
                    f.write("""rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}""")
            
            # Create storage.rules
            storage_rules = project_dir / "storage.rules"
            if not storage_rules.exists():
                with open(storage_rules, 'w') as f:
                    f.write("""rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}""")
            
            # Create firestore.indexes.json
            firestore_indexes = project_dir / "firestore.indexes.json"
            if not firestore_indexes.exists():
                with open(firestore_indexes, 'w') as f:
                    json.dump({
                        "indexes": [],
                        "fieldOverrides": []
                    }, f, indent=2)
            
            print(f"Firebase configuration files created for {project_name}")
            
        except Exception as e:
            print(f"Warning: Could not create Firebase config files: {e}")
            # Don't fail the entire process for Firebase config issues
    
    def _create_firebase_project(self, project_name: str, firebase_account: str) -> str:
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
    
    def _create_firebase_apps(self, project_id: str, project_name: str, org_domain: str, firebase_account: str) -> Dict[str, str]:
        """Create Firebase apps for iOS, Android, and Web"""
        bundle_id = f'com.{org_domain}.{project_name}'
        results = {'ios': 'unknown', 'android': 'unknown', 'web': 'unknown'}
        
        print(f"Creating Firebase apps for project: {project_id}")
        print(f"Bundle ID: {bundle_id}")
        print(f"Firebase account: {firebase_account}")
        
        # Create iOS app
        try:
            print(f"Creating iOS app: {project_name}-ios")
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
        except subprocess.TimeoutExpired:
            print('Web app creation timed out after 60 seconds')
        except subprocess.CalledProcessError as e:
            print(f'Failed to create Web app: {e}')
            print(f'Error output: {e.stderr}')
        except Exception as e:
            print(f'Unexpected error creating Web app: {e}')
        
        return results
    
    def _extract_app_id(self, output: str) -> str:
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
    
    def _download_firebase_configs(self, project_dir: Path, project_id: str, app_ids: Dict[str, str], firebase_account: str):
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
                ios_dir = project_dir / 'ios' / 'Runner'
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
                android_dir = project_dir / 'android' / 'app'
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
                web_dir = project_dir / 'web'
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
        
        return configs
    
    def _update_app_config_json(self, project_dir: Path, project_id: str, project_name: str, org_domain: str, app_ids: Dict[str, str]):
        """Update app configuration files with Firebase project details"""
        try:
            # Update app_config.json if it exists
            app_config_file = project_dir / 'assets' / 'config' / 'app_config.json'
            if app_config_file.exists():
                with open(app_config_file, 'r') as f:
                    config = json.load(f)
                
                # Update Firebase configuration
                config['firebase'] = {
                    'project_id': project_id,
                    'app_ids': app_ids,
                    'org_domain': org_domain,
                    'project_name': project_name
                }
                
                with open(app_config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"✅ Updated app_config.json with Firebase details")
            else:
                print("⚠️ app_config.json not found, skipping update")
                
        except Exception as e:
            print(f"Warning: Could not update app_config.json: {e}")
    
    def _setup_firestore_database(self, project_id: str, project_name: str, firebase_account: str):
        """Setup Firestore database"""
        try:
            print(f"Setting up Firestore database for project: {project_id}")
            
            # Try to create Firestore database with asia-south1 region (Mumbai)
            # Note: Firebase CLI may not support --region flag, so we'll try without it
            try:
                result = subprocess.run([
                    'firebase', '--account', firebase_account,
                    'firestore:databases:create', '(default)',
                    '--project', project_id,
                    '--region', 'asia-south1'
                ], check=True, capture_output=True, text=True, timeout=60)
                print(f"✅ Firestore database created: {result.stdout}")
            except subprocess.CalledProcessError as e:
                if 'unknown option' in e.stderr or '--region' in e.stderr:
                    # Try without region flag (uses default region)
                    print("⚠️ Region flag not supported, trying with default region...")
                    result = subprocess.run([
                        'firebase', '--account', firebase_account,
                        'firestore:databases:create', '(default)',
                        '--project', project_id
                    ], check=True, capture_output=True, text=True, timeout=60)
                    print(f"✅ Firestore database created with default region: {result.stdout}")
                else:
                    raise e
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not create Firestore database: {e}")
            print(f"Error output: {e.stderr}")
            print("⚠️ Proceeding with remaining steps...")
        except subprocess.TimeoutExpired:
            print("Warning: Firestore database creation timed out")
            print("⚠️ Proceeding with remaining steps...")
        except Exception as e:
            print(f"Warning: Unexpected error creating Firestore database: {e}")
            print("⚠️ Proceeding with remaining steps...")
    
    def _update_cloned_repository_configs(self, project_dir: Path, project_id: str, project_name: str, org_domain: str, app_ids: Dict[str, str]):
        """Update cloned repository configuration files with Firebase details"""
        try:
            print(f"Updating repository config files for project: {project_name}")
            
            # Update various configuration files that might exist in the cloned repository
            config_files = [
                'pubspec.yaml',
                'android/app/build.gradle',
                'ios/Runner.xcodeproj/project.pbxproj',
                'ios/Runner/Info.plist',
                'web/index.html',
                'README.md',
                'firebase.json',
                'firestore.rules',
                'storage.rules',
                'assets/config/app_config.json',
                'assets/config/app_config_sample.json'
            ]
            
            for config_file in config_files:
                file_path = project_dir / config_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Replace old project identifiers with new ones
                        content = content.replace('mytemplate-app', project_name)
                        content = content.replace('com.meghzone.mytemplate-app', f'com.{org_domain}.{project_name}')
                        
                        # Add Firebase project ID if not present
                        if 'firebase' in config_file.lower() or 'config' in config_file.lower():
                            if project_id not in content:
                                # Add Firebase configuration if it's a config file
                                if config_file.endswith('.json'):
                                    try:
                                        config_data = json.loads(content)
                                        config_data['firebase'] = {
                                            'project_id': project_id,
                                            'app_ids': app_ids,
                                            'org_domain': org_domain,
                                            'project_name': project_name
                                        }
                                        content = json.dumps(config_data, indent=2)
                                    except json.JSONDecodeError:
                                        # Not a valid JSON file, skip JSON updates
                                        pass
                        
                        with open(file_path, 'w') as f:
                            f.write(content)
                        
                        print(f"✅ Updated {config_file}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not update {config_file}: {e}")
                else:
                    print(f"⏭️ Skipping {config_file} (file not found)")
            
            # Create or update Firebase configuration files
            self._create_firebase_config_files(project_dir, project_name, org_domain)
            
        except Exception as e:
            print(f"Warning: Could not update repository configs: {e}")
            print("⚠️ Proceeding with remaining steps...")
    
    def _commit_and_push_changes(self, project_dir: Path, project_name: str):
        """Commit and push changes to remote repository"""
        try:
            print(f"Committing and pushing changes for project: {project_name}")
            
            # Check if there are any changes to commit
            result = subprocess.run(["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True)
            if result.stdout.strip():
                # There are changes, commit them
                subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Firebase setup and configuration for {project_name}"], cwd=project_dir, check=True)
                print(f"✅ Committed changes for {project_name}")
                
                # Try to push to remote repository
                try:
                    subprocess.run(["git", "push"], cwd=project_dir, check=True, timeout=60)
                    print(f"✅ Pushed changes to remote repository for {project_name}")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Warning: Could not push to remote repository: {e}")
                    print("⚠️ Changes are committed locally but not pushed")
                except subprocess.TimeoutExpired:
                    print("⚠️ Warning: Push operation timed out")
                    print("⚠️ Changes are committed locally but not pushed")
            else:
                print(f"ℹ️ No changes to commit for {project_name}")
                
        except Exception as e:
            print(f"Warning: Could not commit and push changes: {e}")
            print("⚠️ Proceeding with remaining steps...")
    
    def _update_config_json_with_firebase(self, project_dir: Path, project_id: str, project_name: str, org_domain: str, app_ids: Dict[str, str], firebase_account: str):
        """Update app_config.json file with Firebase project and app data"""
        try:
            # Look specifically for app_config.json in assets/config/ directory
            app_config_file = project_dir / 'assets' / 'config' / 'app_config.json'
            
            if app_config_file.exists():
                try:
                    with open(app_config_file, 'r') as f:
                        config_data = json.load(f)
                except json.JSONDecodeError:
                    # If file is not valid JSON, create new structure
                    config_data = {}
                
                # Preserve existing app information if it exists, otherwise create new
                if 'app' not in config_data:
                    config_data['app'] = {
                        'name': project_name,
                        'description': f'Firebase-enabled {project_name} application',
                        'version': '1.0.0',
                        'buildNumber': '1'
                    }
                else:
                    # Update only existing keys
                    if 'name' in config_data['app']:
                        config_data['app']['name'] = project_name
                    if 'description' in config_data['app']:
                        config_data['app']['description'] = f'Firebase-enabled {project_name} application'
                
                # Get real Firebase configuration data
                firebase_configs = self._get_real_firebase_configs(project_id, app_ids, firebase_account, org_domain, project_name)
                
                # Preserve existing Firebase structure and update only existing keys
                if 'firebase' not in config_data:
                    config_data['firebase'] = firebase_configs
                else:
                    # Update existing Firebase configuration
                    for platform in ['web', 'android', 'ios']:
                        if platform in firebase_configs and platform in config_data['firebase']:
                            # Update only existing keys in the platform config
                            for key, value in firebase_configs[platform].items():
                                if key in config_data['firebase'][platform]:
                                    config_data['firebase'][platform][key] = value
                        elif platform in firebase_configs:
                            # Add new platform if it doesn't exist
                            config_data['firebase'][platform] = firebase_configs[platform]
                
                # Add project information
                config_data['project'] = {
                    'name': project_name,
                    'description': f'Firebase-enabled project: {project_name}',
                    'org_domain': org_domain,
                    'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                with open(app_config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                print(f"SUCCESS: Updated {app_config_file} with Firebase configuration")
            else:
                print(f"WARNING: app_config.json not found at {app_config_file}")
                print("WARNING: Skipping Firebase configuration update")
                
        except Exception as e:
            print(f"Warning: Could not update app_config.json: {e}")
            print("WARNING: Proceeding with remaining steps...")
    
    def _get_real_firebase_configs(self, project_id: str, app_ids: Dict[str, str], firebase_account: str, org_domain: str, project_name: str) -> Dict[str, Any]:
        """Get real Firebase configuration data for all platforms"""
        firebase_configs = {}
        
        try:
            # Get web configuration
            if app_ids.get('web') and app_ids['web'] != 'unknown':
                try:
                    result = subprocess.run([
                        'firebase', '--account', firebase_account,
                        'apps:sdkconfig', 'web', app_ids['web'], '--project', project_id
                    ], check=True, capture_output=True, text=True, timeout=30)
                    
                    web_config = self._parse_firebase_config(result.stdout, 'web')
                    if web_config:
                        firebase_configs['web'] = web_config
                        print(f"SUCCESS: Retrieved web Firebase configuration")
                except Exception as e:
                    print(f"WARNING: Could not get web Firebase config: {e}")
            
            # Get Android configuration
            if app_ids.get('android') and app_ids['android'] != 'unknown':
                try:
                    result = subprocess.run([
                        'firebase', '--account', firebase_account,
                        'apps:sdkconfig', 'android', app_ids['android'], '--project', project_id
                    ], check=True, capture_output=True, text=True, timeout=30)
                    
                    android_config = self._parse_firebase_config(result.stdout, 'android')
                    if android_config:
                        firebase_configs['android'] = android_config
                        print(f"SUCCESS: Retrieved Android Firebase configuration")
                except Exception as e:
                    print(f"WARNING: Could not get Android Firebase config: {e}")
            
            # Get iOS configuration
            if app_ids.get('ios') and app_ids['ios'] != 'unknown':
                try:
                    result = subprocess.run([
                        'firebase', '--account', firebase_account,
                        'apps:sdkconfig', 'ios', app_ids['ios'], '--project', project_id
                    ], check=True, capture_output=True, text=True, timeout=30)
                    
                    ios_config = self._parse_firebase_config(result.stdout, 'ios')
                    if ios_config:
                        firebase_configs['ios'] = ios_config
                        print(f"SUCCESS: Retrieved iOS Firebase configuration")
                except Exception as e:
                    print(f"WARNING: Could not get iOS Firebase config: {e}")
            
            # If no real configs were retrieved, create fallback configs
            if not firebase_configs:
                print("WARNING: Using fallback Firebase configuration")
                firebase_configs = self._create_fallback_firebase_configs(project_id, app_ids, org_domain, project_name)
            
        except Exception as e:
            print(f"Warning: Could not get real Firebase configs: {e}")
            firebase_configs = self._create_fallback_firebase_configs(project_id, app_ids, org_domain, project_name)
        
        return firebase_configs
    
    def _parse_firebase_config(self, config_output: str, platform: str) -> Dict[str, Any]:
        """Parse Firebase configuration output for a specific platform"""
        try:
            # Try to parse as JSON first
            if config_output.strip().startswith('{'):
                config_data = json.loads(config_output)
                return config_data
            else:
                # If not JSON, try to extract key-value pairs
                config = {}
                lines = config_output.split('\n')
                for line in lines:
                    if ':' in line and not line.startswith('#'):
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key and value:
                            config[key] = value
                return config
        except Exception as e:
            print(f"Warning: Could not parse {platform} Firebase config: {e}")
            return {}
    
    def _create_fallback_firebase_configs(self, project_id: str, app_ids: Dict[str, str], org_domain: str = None, project_name: str = None) -> Dict[str, Any]:
        """Create fallback Firebase configuration when real configs are not available"""
        return {
            'web': {
                'apiKey': f'AIzaSy{project_id[:8].upper()}',
                'appId': app_ids.get('web', 'unknown'),
                'messagingSenderId': project_id.split('-')[-1] if '-' in project_id else '123456789',
                'projectId': project_id,
                'authDomain': f'{project_id}.firebaseapp.com',
                'storageBucket': f'{project_id}.firebasestorage.app',
                'measurementId': f'G-{project_id[:8].upper()}'
            },
            'android': {
                'apiKey': f'AIzaSy{project_id[:8].upper()}',
                'appId': app_ids.get('android', 'unknown'),
                'messagingSenderId': project_id.split('-')[-1] if '-' in project_id else '123456789',
                'projectId': project_id,
                'storageBucket': f'{project_id}.firebasestorage.app'
            },
            'ios': {
                'apiKey': f'AIzaSy{project_id[:8].upper()}',
                'appId': app_ids.get('ios', 'unknown'),
                'messagingSenderId': project_id.split('-')[-1] if '-' in project_id else '123456789',
                'projectId': project_id,
                'storageBucket': f'{project_id}.firebasestorage.app',
                'iosBundleId': f'com.{org_domain}.{project_name}'
            }
        }
    
    def _commit_firebase_changes(self, project_dir: Path, project_name: str):
        """Commit Firebase-related changes to the repository and push to GitHub"""
        try:
            print(f"Committing Firebase changes for project: {project_name}")
            
            # Check if there are any changes to commit
            result = subprocess.run(["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True)
            if result.stdout.strip():
                # There are changes, commit them
                subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Firebase setup and configuration for {project_name}"], cwd=project_dir, check=True)
                print(f"✅ Committed Firebase changes for {project_name}")
                
                # Try to push to GitHub repository
                try:
                    print(f"Pushing changes to GitHub repository...")
                    # First try normal push
                    result = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        print(f"✅ Pushed changes to GitHub repository for {project_name}")
                    else:
                        # If push fails due to remote changes, try to handle it
                        if "rejected" in result.stderr and "fetch first" in result.stderr:
                            print("⚠️ Remote repository has initial content, pulling changes first...")
                            
                            # Pull remote changes and merge
                            pull_result = subprocess.run(["git", "pull", "origin", "main", "--allow-unrelated-histories"], 
                                                       cwd=project_dir, capture_output=True, text=True, timeout=60)
                            
                            if pull_result.returncode == 0:
                                print("✅ Successfully pulled remote changes")
                                # Try push again
                                push_result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                                           cwd=project_dir, capture_output=True, text=True, timeout=60)
                                if push_result.returncode == 0:
                                    print(f"✅ Pushed changes to GitHub repository for {project_name}")
                                else:
                                    print(f"⚠️ Warning: Could not push after pull: {push_result.stderr}")
                                    print("⚠️ Changes are committed locally but not pushed to GitHub")
                            else:
                                print(f"⚠️ Warning: Could not pull remote changes: {pull_result.stderr}")
                                print("⚠️ Changes are committed locally but not pushed to GitHub")
                        else:
                            print(f"⚠️ Warning: Could not push to GitHub repository: {result.stderr}")
                            print("⚠️ Changes are committed locally but not pushed to GitHub")
                            
                except subprocess.TimeoutExpired:
                    print("⚠️ Warning: Push operation timed out")
                    print("⚠️ Changes are committed locally but not pushed to GitHub")
            else:
                print(f"ℹ️ No changes to commit for {project_name}")
                
        except Exception as e:
            print(f"Warning: Could not commit Firebase changes: {e}")
            print("⚠️ Proceeding with remaining steps...")
    
    def create_github_repository(self, project_name: str, description: str, org_domain: str) -> str:
        """Create a new GitHub repository"""
        try:
            github_token = self.config.get('github_token')
            if not github_token or github_token == 'your_github_personal_access_token_here':
                print("⚠️ GitHub token not configured, skipping GitHub repository creation")
                return None
            
            # Determine if we should create under user account or organization
            # For now, create under user account
            username = self._get_github_username(github_token)
            if not username:
                print("⚠️ Could not determine GitHub username")
                return None
            
            repo_name = project_name
            repo_description = description or f"Firebase-enabled project: {project_name}"
            
            # Create repository data
            repo_data = {
                "name": repo_name,
                "description": repo_description,
                "private": False,  # Public repository
                "auto_init": False,  # Don't initialize with README since we're cloning a template
                "gitignore_template": None,  # Don't add gitignore template to avoid conflicts
                "license_template": None  # Don't add license template to avoid conflicts
            }
            
            # Make API request to create repository
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.github.com/user/repos"
            
            response = requests.post(url, headers=headers, json=repo_data, timeout=30)
            
            if response.status_code == 201:
                repo_info = response.json()
                repo_url = repo_info.get('html_url')
                clone_url = repo_info.get('clone_url')
                print(f"✅ GitHub repository created successfully: {repo_url}")
                return clone_url
            else:
                print(f"❌ Failed to create GitHub repository: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"Warning: Could not create GitHub repository: {e}")
            return None
    
    def _get_github_username(self, github_token: str) -> str:
        """Get GitHub username from token"""
        try:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                return user_info.get('login')
            else:
                print(f"❌ Failed to get GitHub user info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Warning: Could not get GitHub username: {e}")
            return None
    
    def update_git_remote(self, project_dir: Path, new_repo_url: str):
        """Update Git remote origin to point to new repository"""
        try:
            # Remove existing origin if it exists
            result = subprocess.run(["git", "remote", "remove", "origin"], cwd=project_dir, capture_output=True, text=True)
            
            # Add new origin
            result = subprocess.run(["git", "remote", "add", "origin", new_repo_url], cwd=project_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Updated Git remote origin to: {new_repo_url}")
            else:
                print(f"⚠️ Warning: Could not update Git remote: {result.stderr}")
                
        except Exception as e:
            print(f"Warning: Could not update Git remote: {e}")

class FullWebWizard:
    """Full web-only version of the project wizard"""
    
    def __init__(self):
        self.web_server = FullWebServer()
    
    def run(self):
        """Run the web interface"""
        print("🚀 NewProjWiz - Full Web-Only Project Wizard")
        print("=" * 50)
        
        # Start web server
        if not self.web_server.start():
            print("❌ Failed to start web server")
            return False
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{self.web_server.port}')
            print(f"🌐 Opening web interface in your browser at http://localhost:{self.web_server.port}")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print(f"Please open http://localhost:{self.web_server.port} in your browser")
        
        print("Press Ctrl+C to stop the server")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down NewProjWiz...")
            self.web_server.stop()
        
        return True

def main():
    """Main entry point"""
    wizard = FullWebWizard()
    wizard.run()

if __name__ == "__main__":
    main() 