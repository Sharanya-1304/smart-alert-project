"""
Verification Script - Test all imports and basic functionality
Run this before starting the main application
"""

print("="*70)
print("🧪 SMART ALERT - SYSTEM VERIFICATION")
print("="*70)

# Test 1: Python Version
print("\n1. Checking Python version...")
import sys
if sys.version_info >= (3, 8):
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (3.8+ required)")

# Test 2: Flask
print("\n2. Checking Flask...")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__}")
except ImportError as e:
    print(f"   ❌ Flask not installed: {e}")

# Test 3: SQLAlchemy
print("\n3. Checking SQLAlchemy...")
try:
    import sqlalchemy
    print(f"   ✅ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"   ❌ SQLAlchemy not installed: {e}")

# Test 4: OpenCV
print("\n4. Checking OpenCV...")
try:
    import cv2
    print(f"   ✅ OpenCV {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ OpenCV not installed: {e}")

# Test 5: NumPy
print("\n5. Checking NumPy...")
try:
    import numpy as np
    print(f"   ✅ NumPy {np.__version__}")
except ImportError as e:
    print(f"   ❌ NumPy not installed: {e}")

# Test 6: PyTorch
print("\n6. Checking PyTorch...")
try:
    import torch
    print(f"   ✅ PyTorch {torch.__version__}")
except ImportError as e:
    print(f"   ❌ PyTorch not installed: {e}")

# Test 7: Ultralytics (YOLOv8)
print("\n7. Checking Ultralytics YOLO...")
try:
    from ultralytics import YOLO
    print(f"   ✅ Ultralytics installed")
except ImportError as e:
    print(f"   ❌ Ultralytics not installed: {e}")

# Test 8: Text-to-Speech
print("\n8. Checking pyttsx3 (Text-to-Speech)...")
try:
    import pyttsx3
    print(f"   ✅ pyttsx3 installed")
except ImportError as e:
    print(f"   ⚠ pyttsx3 not installed (optional): {e}")

# Test 9: Directory Structure
print("\n9. Checking directory structure...")
import os
dirs = ['uploads', 'evidence', 'logs', 'stats', 'models', 'templates',
        'fire_detection', 'fall_detection']
for directory in dirs:
    if os.path.exists(directory):
        print(f"   ✅ {directory}/")
    else:
        print(f"   ❌ {directory}/ (missing)")

# Test 10: YOLO Models
print("\n10. Checking YOLO models...")
models = ['models/yolov8n.pt', 'models/yolov8n-pose.pt']
for model in models:
    if os.path.exists(model):
        size = os.path.getsize(model) / (1024*1024)
        print(f"   ✅ {model} ({size:.1f} MB)")
    else:
        print(f"   ❌ {model} (not found)")

# Test 11: Templates
print("\n11. Checking HTML templates...")
templates = ['dashboard.html', 'detection.html', 'login.html', 'register.html',
             'result.html', 'history.html', 'settings.html']
for template in templates:
    path = f'templates/{template}'
    if os.path.exists(path):
        print(f"   ✅ {template}")
    else:
        print(f"   ❌ {template} (missing)")

# Test 12: Import Detection Modules
print("\n12. Checking detection modules...")
try:
    from fire_detection.fire_detection import start_fire_detection
    print(f"   ✅ fire_detection module")
except Exception as e:
    print(f"   ❌ fire_detection module: {e}")

try:
    from fall_detection.fall_detection import start_fall_detection
    print(f"   ✅ fall_detection module")
except Exception as e:
    print(f"   ❌ fall_detection module: {e}")

# Test 13: Import Alert System
print("\n13. Checking alert system...")
try:
    from alert import trigger_alert
    print(f"   ✅ alert module")
except Exception as e:
    print(f"   ❌ alert module: {e}")

# Test 14: Import Utils
print("\n14. Checking utilities...")
try:
    from utils import save_evidence, log_event
    print(f"   ✅ utils module")
except Exception as e:
    print(f"   ❌ utils module: {e}")

# Test 15: App.py syntax
print("\n15. Checking app.py syntax...")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    compile(app_code, 'app.py', 'exec')
    print(f"   ✅ app.py syntax valid")
except SyntaxError as e:
    print(f"   ❌ app.py syntax error: {e}")
except Exception as e:
    print(f"   ❌ app.py error: {e}")

# Summary
print("\n"+"="*70)
print("📊 VERIFICATION COMPLETE")
print("="*70)
print("\n💡 Next Steps:")
print("   1. Install missing packages: pip install -r requirements.txt")
print("   2. Download YOLO models if missing")
print("   3. Run the application: python app.py")
print("   4. Open browser: http://localhost:5000")
print("\n"+"="*70)
