# 🚀 SETUP AND RUN GUIDE

## ✅ PRE-FLIGHT CHECKLIST

Before running the application:

### 1. Verify Setup
```bash
python verify_setup.py
```

This will check:
- ✅ Python version (3.8+)
- ✅ All required packages
- ✅ Directory structure
- ✅ YOLO models
- ✅ Template files
- ✅ Code syntax

### 2. Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

**Expected time**: 5-10 minutes (downloads AI libraries)

### 3. Download YOLO Models (if missing)

**Option A - Automatic:**
```python
python
>>> from ultralytics import YOLO
>>> YOLO('yolov8n.pt')
>>> YOLO('yolov8n-pose.pt')
>>> exit()
```

**Option B - Manual:**
- Download from: https://github.com/ultralytics/ultralytics/releases
- Place in `models/` folder:
  - `models/yolov8n.pt` (~6 MB)
  - `models/yolov8n-pose.pt` (~6 MB)

---

## 🎯 RUNNING THE APPLICATION

### Standard Run:
```bash
python app.py
```

**Expected output:**
```
✅ Database initialized
✅ Smart Alert System Ready!
🚀 Starting server on http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### Open Browser:
```
http://localhost:5000
```

---

## 📝 FIRST TIME USAGE

1. **Register Account**
   - Click "Register"
   - Enter: username, email, password
   - Click "Register"

2. **Login**
   - Enter credentials
   - Access dashboard

3. **Explore Dashboard**
   - View real user statistics
   - See analytics charts
   - Check activity metrics

4. **Test Detection**
   - Click "Start Detection"
   - Upload test video
   - Wait for results
   - View alerts

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: Port 5000 already in use
```bash
# Fix Option 1: Use different port
# Edit app.py, line 555, change to:
app.run(debug=True, host='0.0.0.0', port=5001)

# Fix Option 2: Kill process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

### Issue 2: ModuleNotFoundError
```bash
# Install missing package
pip install <package_name>

# Or reinstall all
pip install -r requirements.txt --upgrade
```

### Issue 3: YOLO models not found
```bash
# Download models using Python
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt'); YOLO('yolov8n-pose.pt')"
```

### Issue 4: OpenCV window issues
- This is normal when running as web app
- Detection still works in background
- Results shown on web interface

### Issue 5: Email not sending
```python
# Edit alert.py lines 17-19:
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Not regular password!
GUARDIAN_EMAIL = "recipient@gmail.com"

# Gmail users:
# 1. Enable 2FA: https://myaccount.google.com/security
# 2. Generate app password: https://myaccount.google.com/apppasswords
# 3. Use app password in alert.py
```

### Issue 6: Database locked
```bash
# Delete database and restart
del instance\smart_alert.db
python app.py
```

### Issue 7: ImportError for detection modules
```bash
# Verify __init__.py files exist:
touch fire_detection/__init__.py
touch fall_detection/__init__.py
```

---

## 🎬 DEMO WORKFLOW

### For Placement Interviews:

1. **Start Application**
   ```bash
   python app.py
   ```

2. **Open Browser**
   - Navigate to http://localhost:5000

3. **Show Registration**
   - Create new account
   - Explain password hashing

4. **Show Dashboard**
   - Point out real user count
   - Explain Chart.js integration
   - Show analytics tracking

5. **Demo Detection**
   - Upload fire video
   - Explain unified detection
   - Show auto-recognition
   - Display results with alerts

6. **Show Code**
   - Open app.py
   - Explain Flask structure
   - Show database models
   - Discuss API endpoints

7. **Explain Architecture**
   - Draw system diagram
   - Discuss scalability
   - Mention security features

---

## 📊 TEST DATA

### Test Videos Needed:
1. **Fire Detection**: Video with flames/fire
2. **Fall Detection**: Video of person falling
3. **Normal**: Regular video (no threats)

### Where to Find:
- YouTube (download 10-30 second clips)
- Record your own using phone
- Use stock footage websites

---

## 🔧 TROUBLESHOOTING COMMANDS

```bash
# Check if Flask is running
netstat -ano | findstr :5000

# View database
python -c "from app import app, db; from sqlalchemy import inspect; print(inspect(db.engine).get_table_names())"

# Test imports
python verify_setup.py

# Check Python version
python --version

# List installed packages
pip list

# Check OpenCV
python -c "import cv2; print(cv2.__version__)"

# Check YOLO
python -c "from ultralytics import YOLO; print('YOLO OK')"

# Test alert system
python alert.py
```

---

## 📞 GETTING HELP

### Sequence to Follow:

1. **Run Verification**
   ```bash
   python verify_setup.py
   ```

2. **Check Logs**
   - Look in `logs/alerts_log.txt`
   - Check console output

3. **Read Error Message**
   - Note exact error text
   - Check line number

4. **Search Documentation**
   - Check README.md
   - Read QUICK_START.md
   - Review PROJECT_HIGHLIGHTS.md

5. **Common Solutions**
   - Reinstall dependencies
   - Delete database
   - Download models
   - Check Python version

---

## ✨ PRODUCTION DEPLOYMENT

### For Advanced Users:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (production server)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With Nginx (reverse proxy)
# Configure Nginx to proxy to http://127.0.0.1:5000
```

---

## 🎓 FOR PLACEMENT SUCCESS

### What to Practice:

1. **5-Minute Demo** - Run through complete flow
2. **Code Explanation** - Explain any function
3. **Architecture Discussion** - Draw diagrams
4. **Challenges Solved** - Discuss problems faced
5. **Future Improvements** - Scaling ideas

### What to Know:

- Database schema (all 5 tables)
- API endpoints (all 15+)
- Detection algorithm (HSV color, YOLO)
- Threading usage (background processing)
- Security features (password hashing, etc.)

---

## 🎯 QUICK REFERENCE

| Command | Purpose |
|---------|---------|
| `python verify_setup.py` | Check installation |
| `python app.py` | Run application |
| `python alert.py` | Test alerts |
| `pip install -r requirements.txt` | Install packages |
| `Ctrl + C` | Stop server |

| URL | Page |
|-----|------|
| `http://localhost:5000` | Home/Login |
| `http://localhost:5000/register` | Registration |
| `http://localhost:5000/dashboard` | Dashboard |
| `http://localhost:5000/detection` | Upload Video |

---

**ALL CODE IS NOW ERROR-FREE AND READY TO RUN! ✅**

**Good luck with your project! 🚀**
