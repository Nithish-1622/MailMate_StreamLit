#!/usr/bin/env python3
"""
MailMate Deployment Helper Script
Prepares the project for Streamlit Cloud deployment
"""

import os
import shutil
import subprocess
import sys

def check_git():
    """Check if git is initialized and configured"""
    if not os.path.exists('.git'):
        print("❌ Git not initialized. Run: git init")
        return False
    return True

def prepare_deployment():
    """Prepare files for deployment"""
    print("🚀 Preparing MailMate for Streamlit Cloud deployment...")
    
    # Copy streamlit requirements
    if os.path.exists('requirements_streamlit.txt'):
        shutil.copy('requirements_streamlit.txt', 'requirements.txt')
        print("✅ Updated requirements.txt for Streamlit Cloud")
    
    # Check for necessary files
    required_files = ['dashboard.py', '.streamlit/config.toml', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} ready")
        else:
            print(f"❌ {file} missing")
    
    print("\n📋 Deployment Checklist:")
    print("1. ✅ Files prepared")
    print("2. 🔄 Push to GitHub: git add . && git commit -m 'Deploy to Streamlit' && git push")
    print("3. 🌐 Deploy at: https://share.streamlit.io")
    print("4. 🔐 Add API keys in Streamlit Cloud secrets")
    print("5. 🎉 Launch your app!")

if __name__ == "__main__":
    prepare_deployment()
