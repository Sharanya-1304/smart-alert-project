#!/bin/bash
# Quick Setup Script for Smart Alert Website

echo "🚀 Smart Alert - Quick Setup"
echo "============================"

# Check Python
echo "✓ Checking Python installation..."
python --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
call venv\Scripts\activate.bat

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Create database
echo "✓ Setting up database..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"

# Download models
echo "✓ Downloading AI models..."
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt'); YOLO('yolov8n-pose.pt')"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "To start the web application, run:"
echo "  python app.py"
echo ""
echo "Then open your browser and go to:"
echo "  http://localhost:5000"
echo ""
