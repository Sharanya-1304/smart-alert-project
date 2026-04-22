#!/usr/bin/env python3
"""
Smart Alert - Quick Setup Script
Initializes the web application and downloads required models
"""

import os
import sys
import subprocess

def setup():
    print("\n" + "="*50)
    print("🚀 Smart Alert - Setup Script")
    print("="*50 + "\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected\n")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed\n")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("evidence", exist_ok=True)
    os.makedirs("stats", exist_ok=True)
    print("✓ Directories created\n")
    
    # Download models
    print("🤖 Downloading AI models (this may take a few minutes)...")
    try:
        from ultralytics import YOLO
        
        print("  - Downloading YOLOv8 person detection model...")
        YOLO('yolov8n.pt')
        
        print("  - Downloading YOLOv8 pose estimation model...")
        YOLO('yolov8n-pose.pt')
        
        print("✓ Models downloaded\n")
    except Exception as e:
        print(f"⚠️  Model download warning: {e}")
        print("   Models will be downloaded on first run\n")
    
    # Create database
    print("💾 Initializing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✓ Database initialized\n")
    except Exception as e:
        print(f"⚠️  Database warning: {e}\n")
    
    print("="*50)
    print("✅ Setup Complete!")
    print("="*50)
    print("\n🎉 Ready to run Smart Alert!")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nThen open: http://localhost:5000\n")

if __name__ == "__main__":
    setup()
