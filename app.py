from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import threading
import cv2
import numpy as np
from collections import Counter

# Detection imports
from fire_detection.fire_detection import start_fire_detection
from fall_detection.fall_detection import start_fall_detection
from alert import trigger_alert, DEFAULT_CAREGIVER_EMAIL

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart_alert_secret_key_2024')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_alert.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EVIDENCE_FOLDER'] = 'evidence'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'webm'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EVIDENCE_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ================= DATABASE MODELS =================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    caregiver_email = db.Column(db.String(100))  # Email for caregiver alerts
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    alert_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float)
    severity = db.Column(db.String(20), default='warning')
    description = db.Column(db.Text)
    video_path = db.Column(db.String(500))
    evidence_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)

class PageView(db.Model):
    __tablename__ = 'page_views'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    page = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

class VideoUpload(db.Model):
    __tablename__ = 'video_uploads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(500))
    original_filename = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='pending')
    detection_result = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    processing_time = db.Column(db.Float)

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ================= HELPER FUNCTIONS =================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def track_page_view(page):
    if 'user' in session:
        try:
            page_view = PageView(
                user_id=session['user'],
                page=page,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(page_view)
            db.session.commit()
        except:
            db.session.rollback()

def log_activity(user_id, activity_type, description):
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        db.session.add(activity)
        db.session.commit()
    except:
        db.session.rollback()


def has_role(user, expected_role):
    if not user or not expected_role:
        return False
    return (user.role or '').strip().lower() == expected_role.strip().lower()

import math

def calculate_angle_from_vertical(p1, p2):
    """Calculate angle of line from p1 to p2 relative to vertical (0=standing, 90=lying)"""
    if p1 is None or p2 is None:
        return None
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dy) < 1:
        return 90
    angle = abs(math.degrees(math.atan2(abs(dx), abs(dy))))
    return angle


def get_keypoint(kpts, idx):
    """Safely get keypoint coordinates"""
    if len(kpts) > idx:
        x, y = float(kpts[idx][0]), float(kpts[idx][1])
        if x > 0 and y > 0:
            return (x, y)
    return None


def detect_video_content(video_path):
    """SIMPLE: FIRE = orange-red colors, FALL = angle > 50 degrees"""
    print("Analyzing video...")

    if not __import__('os').path.exists(video_path):
        return ('error', 0.0, False)

    try:
        cap = __import__('cv2').VideoCapture(video_path)
        if not cap.isOpened():
            return ('error', 0.0, False)

        total_frames = int(cap.get(__import__('cv2').CAP_PROP_FRAME_COUNT))
        fire_count, fall_count, person_count, frames_checked = 0, 0, 0, 0
        max_frames = min(50, total_frames)
        skip = max(1, total_frames // max_frames) - 1

        pose_model = None
        try:
            from ultralytics import YOLO
            for path in ['yolov8n-pose.pt', 'models/yolov8n-pose.pt']:
                if __import__('os').path.exists(path):
                    pose_model = YOLO(path)
                    break
            if not pose_model:
                pose_model = YOLO('yolov8n-pose.pt')
        except:
            pass

        fn = 0
        while frames_checked < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if fn % (skip + 1) != 0:
                fn += 1
                continue

            frames_checked += 1

            # FIRE: Orange-red (H=0-15 in HSV with HIGH saturation, DARK brightness)
            import cv2, numpy as np
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Much stricter: narrow hue (0-15), high saturation (>120), dark brightness (50-150)
            fire_mask = cv2.inRange(hsv, np.array([0, 120, 50]), np.array([15, 255, 150]))
            if cv2.countNonZero(fire_mask) / (frame.shape[0] * frame.shape[1]) > 0.05:
                fire_count += 1
                print(f"  🔥 Frame {frames_checked}: Fire")

            # FALL: Angle > 50
            if pose_model:
                try:
                    results = pose_model(frame, verbose=False)
                    for r in results:
                        if r.keypoints and len(r.keypoints) > 0:
                            kpts = r.keypoints.xy[0]
                            sl = get_keypoint(kpts, 5) if len(kpts) > 5 else None
                            sr = get_keypoint(kpts, 6) if len(kpts) > 6 else None
                            hl = get_keypoint(kpts, 11) if len(kpts) > 11 else None
                            hr = get_keypoint(kpts, 12) if len(kpts) > 12 else None

                            if sl and sr and hl and hr:
                                sm = ((sl[0] + sr[0]) / 2, (sl[1] + sr[1]) / 2)
                                hm = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2)
                                angle = calculate_angle_from_vertical(hm, sm)
                                person_count += 1
                                if angle > 20:
                                    fall_count += 1
                                    print(f"  ⬇ Frame {frames_checked}: Fall (angle={angle:.1f}°)")
                except:
                    pass

            fn += 1

        cap.release()

        print(f"Results: Fire={fire_count}, Fall={fall_count}, People={person_count}")

        detected_type = 'normal'
        confidence = 0.0
        has_alert = False

        if fire_count >= 2:
            detected_type = 'fire'
            confidence = 0.92
            has_alert = True
            print("🔥 FIRE DETECTED")

            if fall_count >= 1 and person_count >= 3:
                detected_type = 'fire_and_fall'
                print(f"⬇ FALL ALSO DETECTED")
        elif fall_count >= 1 and person_count >= 3:
            detected_type = 'fall'
            confidence = 0.90
            has_alert = True
            print("⬇ FALL DETECTED")

        print()
        return (detected_type, confidence, has_alert)

    except Exception as e:
        print(f"Error: {e}")
        return ('normal', 0.0, False)


# ================= ROUTES =================

@app.route('/')
def home():
    if 'user' in session:
        user = User.query.get(session['user'])
        if user and user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/register')
def register_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/admin-login')
def admin_login():
    if 'user' in session:
        user = User.query.get(session['user'])
        if user and user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('admin_login.html')

@app.route('/user-login')
def user_login():
    if 'user' in session:
        user = User.query.get(session['user'])
        if user and user.role == 'user':
            return redirect(url_for('dashboard'))
        return redirect(url_for('admin_dashboard'))
    return render_template('user_login.html')

@app.route('/forgot-password/<account_type>')
def forgot_password_page(account_type):
    if account_type not in ('admin', 'user'):
        return redirect(url_for('login_page'))
    return render_template('forgot_password.html', account_type=account_type)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"success": False, "message": "All fields required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"success": False, "message": "Username exists"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"success": False, "message": "Email exists"}), 400

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, 'registration', f'New user: {user.username}')
        return jsonify({"success": True, "message": "Registration successful"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    expected_role = (data.get('expected_role') or '').strip().lower()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    user = User.query.filter(db.func.lower(User.username) == username.lower()).first()

    if user and check_password_hash(user.password, password):
        if expected_role and expected_role in ('admin', 'user') and not has_role(user, expected_role):
            return jsonify({"success": False, "message": f"Access denied. {expected_role.capitalize()} account required."}), 403

        session['user'] = user.id
        session['username'] = user.username
        user.last_login = datetime.utcnow()
        db.session.commit()
        log_activity(user.id, 'login', f'User logged in: {user.username}')
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        })

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    new_password = data.get('new_password') or ''
    confirm_password = data.get('confirm_password') or ''
    role = (data.get('role') or '').strip().lower()

    if role not in ('admin', 'user'):
        return jsonify({"success": False, "message": "Invalid account type"}), 400

    if not username or not email or not new_password or not confirm_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    if len(new_password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400

    user = User.query.filter(
        db.func.lower(User.username) == username.lower(),
        db.func.lower(User.email) == email,
        db.func.lower(User.role) == role
    ).first()

    if not user and role == 'admin' and User.query.filter(db.func.lower(User.role) == 'admin').count() == 0:
        # Recovery path: if no admin exists, promote the matching account during reset.
        user = User.query.filter(
            db.func.lower(User.username) == username.lower(),
            db.func.lower(User.email) == email
        ).first()
        if user:
            user.role = 'admin'

    if not user:
        return jsonify({"success": False, "message": "Account details not found"}), 404

    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        log_activity(user.id, 'password_reset', f'Password reset for {user.username}')
        return jsonify({"success": True, "message": "Password reset successful. Please login."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    track_page_view('dashboard')
    return render_template('dashboard.html')

@app.route('/detection')
def detection():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    track_page_view('detection')
    return render_template('detection.html')

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    track_page_view('history')
    alerts = Alert.query.filter_by(user_id=session['user']).order_by(Alert.created_at.desc()).all()
    return render_template('history.html', alerts=alerts)

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    track_page_view('settings')
    user = User.query.get(session['user'])
    return render_template('settings.html', user=user)

@app.route('/api/user/profile')
def get_user_profile():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(session['user'])
    return jsonify({
        "username": user.username,
        "email": user.email,
        "caregiver_email": user.caregiver_email or "",
        "role": user.role,
        "created_at": user.created_at.strftime("%Y-%m-%d"),
        "total_alerts": Alert.query.filter_by(user_id=user.id).count()
    })

@app.route('/api/user/caregiver-email', methods=['POST'])
def update_caregiver_email():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    caregiver_email = data.get('caregiver_email', '').strip()

    if not caregiver_email:
        return jsonify({"success": False, "message": "Caregiver email is required"}), 400

    # Simple email validation
    if '@' not in caregiver_email or '.' not in caregiver_email:
        return jsonify({"success": False, "message": "Invalid email format"}), 400

    try:
        user = User.query.get(session['user'])
        user.caregiver_email = caregiver_email
        db.session.commit()
        log_activity(user.id, 'caregiver_email_updated', f'Updated caregiver email to: {caregiver_email}')
        return jsonify({"success": True, "message": "Caregiver email updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    alerts = Alert.query.filter_by(user_id=session['user']).all()
    return jsonify({
        "total_alerts": len(alerts),
        "fire_alerts": len([a for a in alerts if a.alert_type == 'fire']),
        "fall_alerts": len([a for a in alerts if a.alert_type == 'fall']),
        "proximity_alerts": len([a for a in alerts if a.alert_type == 'proximity']),
        "critical_alerts": len([a for a in alerts if a.severity == 'critical'])
    })

@app.route('/api/analytics/overview')
def analytics_overview():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    yesterday = datetime.utcnow() - timedelta(days=1)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    return jsonify({
        "total_users": User.query.count(),
        "active_users": User.query.filter(User.last_login >= yesterday).count(),
        "new_users_today": User.query.filter(User.created_at >= today_start).count(),
        "views_today": PageView.query.filter(PageView.timestamp >= today_start).count(),
        "total_page_views": PageView.query.count()
    })

@app.route('/api/analytics/user-growth')
def user_growth():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        count = User.query.filter(User.created_at >= date_start, User.created_at < date_end).count()
        data.append({"date": date.strftime("%b %d"), "count": count})

    return jsonify(data)

@app.route('/api/analytics/page-views')
def page_views_analytics():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        views = PageView.query.filter(PageView.timestamp >= date_start, PageView.timestamp < date_end).count()
        data.append({"date": date.strftime("%b %d"), "views": views})

    return jsonify(data)

@app.route('/api/analytics/detection-stats')
def detection_stats():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        alerts = Alert.query.filter(Alert.created_at >= date_start, Alert.created_at < date_end).all()
        data.append({
            "date": date.strftime("%b %d"),
            "fire": len([a for a in alerts if a.alert_type == 'fire']),
            "fall": len([a for a in alerts if a.alert_type == 'fall']),
            "proximity": len([a for a in alerts if a.alert_type == 'proximity'])
        })

    return jsonify(data)

@app.route('/api/analytics/hourly-activity')
def hourly_activity():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    data = []
    for hour in range(24):
        hour_start = today_start + timedelta(hours=hour)
        hour_end = hour_start + timedelta(hours=1)
        activities = PageView.query.filter(PageView.timestamp >= hour_start, PageView.timestamp < hour_end).count()
        data.append({"hour": f"{hour:02d}:00", "activities": activities})

    return jsonify(data)

@app.route('/api/analytics/popular-pages')
def popular_pages():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    week_ago = datetime.utcnow() - timedelta(days=7)
    page_views = PageView.query.filter(PageView.timestamp >= week_ago).all()
    page_counts = Counter([pv.page for pv in page_views])
    data = [{"page": page, "views": count} for page, count in page_counts.most_common(5)]
    return jsonify(data)

@app.route('/api/analytics/user-activity')
def user_activity_analytics():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    week_ago = datetime.utcnow() - timedelta(days=7)
    top_users = db.session.query(
        User.username,
        db.func.count(PageView.id).label('page_views')
    ).join(PageView, User.id == PageView.user_id)\
     .filter(PageView.timestamp >= week_ago)\
     .group_by(User.username)\
     .order_by(db.func.count(PageView.id).desc())\
     .limit(5).all()

    data = [{"username": username, "page_views": views} for username, views in top_users]
    return jsonify(data)

@app.route('/api/alerts')
def get_alerts():
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    limit = request.args.get('limit', 10, type=int)
    alerts = Alert.query.filter_by(user_id=session['user']).order_by(Alert.created_at.desc()).limit(limit).all()

    data = []
    for alert in alerts:
        data.append({
            "type": alert.alert_type,
            "timestamp": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "severity": alert.severity,
            "description": alert.description or "No description",
            "confidence": alert.confidence
        })

    return jsonify(data)

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    if 'video' not in request.files:
        return jsonify({"success": False, "message": "No video file"}), 400

    file = request.files['video']

    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid format"}), 400

    try:
        filename = secure_filename(f"{session['user']}_{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        video = VideoUpload(
            user_id=session['user'],
            filename=filename,
            original_filename=file.filename,
            file_size=os.path.getsize(filepath)
        )
        db.session.add(video)
        db.session.commit()

        log_activity(session['user'], 'video_upload', f'Uploaded: {file.filename}')

        return jsonify({"success": True, "message": "Upload successful", "video_id": video.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/process-video/<int:video_id>', methods=['POST'])
def process_video(video_id):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    video = VideoUpload.query.get(video_id)

    if not video or video.user_id != session['user']:
        return jsonify({"success": False, "message": "Video not found"}), 404

    # INSTANT PROCESSING - DO IT NOW, NOT IN BACKGROUND!
    try:
        start_time = datetime.utcnow()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)

        # Run detection SYNCHRONOUSLY for instant results
        detection_type, confidence, has_alert = detect_video_content(filepath)

        video.detection_result = detection_type
        video.confidence = confidence
        video.processing_status = 'completed'
        video.processing_time = (datetime.utcnow() - start_time).total_seconds()

        if has_alert:
            # Get user's caregiver email (default to venkatajahnavi07@gmail.com)
            user = User.query.get(video.user_id)
            guardian_email = user.caregiver_email if user and user.caregiver_email else DEFAULT_CAREGIVER_EMAIL

            alert = Alert(
                user_id=video.user_id,
                alert_type=detection_type,
                confidence=confidence,
                severity='critical',
                description=f"{detection_type.capitalize()} detected",
                video_path=filepath
            )
            db.session.add(alert)
            trigger_alert(detection_type, guardian_email)
            log_activity(video.user_id, 'detection_alert', f'{detection_type} detected')

        db.session.commit()

        # Return results INSTANTLY
        return jsonify({
            "success": True,
            "message": "Processing complete",
            "status": "completed",
            "result": detection_type,
            "confidence": confidence,
            "processing_time": video.processing_time
        })

    except Exception as e:
        print(f"Processing error: {e}")
        return jsonify({
            "success": False,
            "message": f"Processing failed: {str(e)}"
        }), 500

@app.route('/api/detection-result/<int:video_id>')
def get_detection_result(video_id):
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    video = VideoUpload.query.get(video_id)

    if not video or video.user_id != session['user']:
        return jsonify({"error": "Video not found"}), 404

    return jsonify({
        "status": video.processing_status,
        "result": video.detection_result,
        "confidence": video.confidence,
        "processing_time": video.processing_time
    })

@app.route('/result/<int:video_id>')
def result_page(video_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))

    video = VideoUpload.query.get(video_id)

    if not video or video.user_id != session['user']:
        return "Video not found", 404

    track_page_view('result')
    return render_template('result.html', video=video)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'user' not in session:
        return "Unauthorized", 401

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return "File not found", 404

    # Verify user owns this video
    video = VideoUpload.query.filter_by(filename=filename).first()
    if not video or video.user_id != session['user']:
        return "Access denied", 403

    return send_file(filepath, mimetype='video/mp4')

# ================= ADMIN ROUTES =================

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        user = User.query.get(session['user'])
        if not has_role(user, 'admin'):
            return "Access denied. Admin privileges required.", 403
        return f(*args, **kwargs)
    return decorated_function


# ================= UNIFIED DASHBOARD (ADMIN + USER) =================

@app.route('/dashboard-unified')
def unified_dashboard():
    """Combined dashboard for both admin and user features"""
    if 'user' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user'])
    is_admin = user and user.role == 'admin'

    if not is_admin:
        return redirect(url_for('dashboard'))

    track_page_view('unified_dashboard')
    return render_template('unified_dashboard.html', user=user, is_admin=is_admin)


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with full system overview"""
    track_page_view('admin_dashboard')
    return render_template('admin/dashboard.html')


@app.route('/admin/users')
@admin_required
def admin_users():
    """User management page"""
    track_page_view('admin_users')
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/activity')
@admin_required
def admin_activity():
    """System activity logs"""
    track_page_view('admin_activity')
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(100).all()
    return render_template('admin/activity.html', activities=activities)


@app.route('/admin/alerts')
@admin_required
def admin_alerts():
    """System-wide alerts management"""
    track_page_view('admin_alerts')
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(100).all()
    return render_template('admin/alerts.html', alerts=alerts)


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Advanced analytics page"""
    track_page_view('admin_analytics')
    return render_template('admin/analytics.html')


# ================= ADMIN API ROUTES =================

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    """Get all admin statistics"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.utcnow() - timedelta(days=7)

    return jsonify({
        "total_users": User.query.count(),
        "active_users": User.query.filter(User.is_active == True).count(),
        "inactive_users": User.query.filter(User.is_active == False).count(),
        "admins": User.query.filter(User.role == 'admin').count(),
        "users_today": User.query.filter(User.created_at >= today_start).count(),
        "users_this_week": User.query.filter(User.created_at >= week_ago).count(),
        "online_today": User.query.filter(User.last_login >= today_start).count(),
        "total_alerts": Alert.query.count(),
        "alerts_today": Alert.query.filter(Alert.created_at >= today_start).count(),
        "fire_alerts": Alert.query.filter(Alert.alert_type == 'fire').count(),
        "fall_alerts": Alert.query.filter(Alert.alert_type == 'fall').count(),
        "unresolved_alerts": Alert.query.filter(Alert.is_resolved == False).count(),
        "total_videos": VideoUpload.query.count(),
        "videos_today": VideoUpload.query.filter(VideoUpload.upload_timestamp >= today_start).count(),
        "total_page_views": PageView.query.count(),
        "views_today": PageView.query.filter(PageView.timestamp >= today_start).count()
    })


@app.route('/api/admin/users')
@admin_required
def admin_get_users():
    """Get all users with details"""
    users = User.query.order_by(User.created_at.desc()).all()
    data = []
    for user in users:
        alert_count = Alert.query.filter_by(user_id=user.id).count()
        video_count = VideoUpload.query.filter_by(user_id=user.id).count()
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "caregiver_email": user.caregiver_email or "Not set",
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M"),
            "last_login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never",
            "alert_count": alert_count,
            "video_count": video_count
        })
    return jsonify(data)


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def admin_get_user(user_id):
    """Get single user details"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    alerts = Alert.query.filter_by(user_id=user.id).order_by(Alert.created_at.desc()).limit(10).all()
    activities = UserActivity.query.filter_by(user_id=user.id).order_by(UserActivity.timestamp.desc()).limit(10).all()

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "caregiver_email": user.caregiver_email,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None,
        "alerts": [{"type": a.alert_type, "date": a.created_at.strftime("%Y-%m-%d")} for a in alerts],
        "activities": [{"type": a.activity_type, "desc": a.description, "date": a.timestamp.strftime("%Y-%m-%d %H:%M")} for a in activities]
    })


@app.route('/api/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def admin_toggle_user_status(user_id):
    """Activate or deactivate a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Cannot deactivate yourself
    if user.id == session['user']:
        return jsonify({"success": False, "message": "Cannot deactivate your own account"}), 400

    user.is_active = not user.is_active
    db.session.commit()

    status = "activated" if user.is_active else "deactivated"
    log_activity(session['user'], 'admin_user_status', f'{status.capitalize()} user: {user.username}')

    return jsonify({
        "success": True,
        "message": f"User {status} successfully",
        "is_active": user.is_active
    })


@app.route('/api/admin/users/<int:user_id>/change-role', methods=['POST'])
@admin_required
def admin_change_user_role(user_id):
    """Change user role (admin/user)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.get_json()
    new_role = data.get('role', 'user')

    if new_role not in ['admin', 'user']:
        return jsonify({"success": False, "message": "Invalid role"}), 400

    # Cannot change your own role
    if user.id == session['user']:
        return jsonify({"success": False, "message": "Cannot change your own role"}), 400

    user.role = new_role
    db.session.commit()

    log_activity(session['user'], 'admin_role_change', f'Changed {user.username} role to: {new_role}')

    return jsonify({
        "success": True,
        "message": f"User role changed to {new_role}",
        "role": new_role
    })


@app.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user (soft delete by deactivating)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Cannot delete yourself
    if user.id == session['user']:
        return jsonify({"success": False, "message": "Cannot delete your own account"}), 400

    username = user.username

    # Delete related records
    Alert.query.filter_by(user_id=user_id).delete()
    UserActivity.query.filter_by(user_id=user_id).delete()
    VideoUpload.query.filter_by(user_id=user_id).delete()
    PageView.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    log_activity(session['user'], 'admin_user_delete', f'Deleted user: {username}')

    return jsonify({"success": True, "message": f"User {username} deleted successfully"})


@app.route('/api/admin/users/create', methods=['POST'])
@admin_required
def admin_create_user():
    """Create a new user"""
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"success": False, "message": "All fields required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"success": False, "message": "Username already exists"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data.get('role', 'user'),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        log_activity(session['user'], 'admin_user_create', f'Created user: {user.username}')

        return jsonify({"success": True, "message": "User created successfully", "user_id": user.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/activity-log')
@admin_required
def admin_activity_log():
    """Get system activity log"""
    limit = request.args.get('limit', 50, type=int)
    activities = db.session.query(UserActivity, User).join(User, UserActivity.user_id == User.id).order_by(UserActivity.timestamp.desc()).limit(limit).all()

    data = []
    for activity, user in activities:
        data.append({
            "id": activity.id,
            "username": user.username,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "timestamp": activity.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(data)


@app.route('/api/admin/alerts')
@admin_required
def admin_get_alerts():
    """Get all system alerts"""
    limit = request.args.get('limit', 50, type=int)
    alerts = db.session.query(Alert, User).join(User, Alert.user_id == User.id).order_by(Alert.created_at.desc()).limit(limit).all()

    data = []
    for alert, user in alerts:
        data.append({
            "id": alert.id,
            "username": user.username,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "confidence": alert.confidence,
            "description": alert.description,
            "is_resolved": alert.is_resolved,
            "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(data)


@app.route('/api/admin/alerts/<int:alert_id>/resolve', methods=['POST'])
@admin_required
def admin_resolve_alert(alert_id):
    """Mark an alert as resolved"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"success": False, "message": "Alert not found"}), 404

    alert.is_resolved = True
    db.session.commit()

    log_activity(session['user'], 'admin_alert_resolve', f'Resolved alert ID: {alert_id}')

    return jsonify({"success": True, "message": "Alert resolved"})


@app.route('/api/caregiver-alerts')
def caregiver_alerts():
    """Get all alerts for caregiver venkatajahnavi07@gmail.com"""
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()

    data = []
    for alert in alerts:
        user = User.query.get(alert.user_id)
        data.append({
            "id": alert.id,
            "alert_type": alert.alert_type,
            "confidence": alert.confidence,
            "severity": alert.severity,
            "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_resolved": alert.is_resolved,
            "description": alert.description,
            "user": user.username if user else "Unknown"
        })

    return jsonify({
        "total_alerts": len(data),
        "recipient": "venkatajahnavi07@gmail.com",
        "alerts": data
    })


@app.route('/admin/caregiver-dashboard')
def caregiver_dashboard():
    """Simple dashboard for caregiver to view alerts"""
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
    return render_template('caregiver_dashboard.html', alerts=alerts)


@app.route('/api/admin/online-users')
@admin_required
def admin_online_users():
    """Get recently active users"""
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    online = User.query.filter(User.last_login >= five_minutes_ago).all()

    return jsonify([{
        "id": u.id,
        "username": u.username,
        "last_login": u.last_login.strftime("%H:%M:%S")
    } for u in online])


@app.route('/api/admin/system-health')
@admin_required
def admin_system_health():
    """Get system health metrics"""
    import os

    # Get uploads folder size
    uploads_size = 0
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            fp = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.isfile(fp):
                uploads_size += os.path.getsize(fp)

    evidence_size = 0
    if os.path.exists(app.config['EVIDENCE_FOLDER']):
        for f in os.listdir(app.config['EVIDENCE_FOLDER']):
            fp = os.path.join(app.config['EVIDENCE_FOLDER'], f)
            if os.path.isfile(fp):
                evidence_size += os.path.getsize(fp)

    return jsonify({
        "uploads_size_mb": round(uploads_size / (1024 * 1024), 2),
        "evidence_size_mb": round(evidence_size / (1024 * 1024), 2),
        "total_storage_mb": round((uploads_size + evidence_size) / (1024 * 1024), 2),
        "database_tables": {
            "users": User.query.count(),
            "alerts": Alert.query.count(),
            "videos": VideoUpload.query.count(),
            "activities": UserActivity.query.count(),
            "page_views": PageView.query.count()
        }
    })


# ================= EMAIL CONFIGURATION =================

@app.route('/admin/email-settings', methods=['GET'])
def email_settings_page():
    """Display email settings configuration page"""
    if 'user' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user'])
    if not has_role(user, 'admin'):
        return redirect(url_for('home'))

    return render_template('email_settings.html')


@app.route('/api/email-credentials', methods=['GET', 'POST'])
def email_credentials():
    """Get or set email credentials"""
    if 'user' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    user = User.query.get(session['user'])
    if not has_role(user, 'admin'):
        return jsonify({'error': 'Admin only'}), 403

    if request.method == 'GET':
        # Read from alert.py config file
        try:
            import alert
            return jsonify({
                'sender_email': alert.SENDER_EMAIL,
                'password_set': bool(alert.SENDER_PASSWORD),
                'password_preview': alert.SENDER_PASSWORD[:4] + '...' + alert.SENDER_PASSWORD[-4:] if alert.SENDER_PASSWORD else 'Not set',
                'recipient_email': alert.DEFAULT_CAREGIVER_EMAIL
            })
        except:
            return jsonify({'error': 'Could not read email config'}), 500

    elif request.method == 'POST':
        data = request.json
        new_password = data.get('password', '').strip()

        if not new_password:
            return jsonify({'error': 'Password cannot be empty'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'Password too short'}), 400

        # Update alert.py
        alert_file = 'alert.py'
        try:
            with open(alert_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find and replace the password line
            import re
            pattern = r'SENDER_PASSWORD = "[^"]*"'
            new_content = re.sub(
                pattern,
                f'SENDER_PASSWORD = "{new_password}"',
                content
            )

            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Reload the module
            import importlib
            import alert as alert_module
            importlib.reload(alert_module)

            return jsonify({
                'success': True,
                'message': 'Email password updated successfully!',
                'password_preview': new_password[:4] + '...' + new_password[-4:]
            })
        except Exception as e:
            return jsonify({'error': f'Failed to update: {str(e)}'}), 500


@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email delivery"""
    if 'user' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    user = User.query.get(session['user'])
    if not has_role(user, 'admin'):
        return jsonify({'error': 'Admin only'}), 403

    recipient = request.json.get('recipient', 'venkatajahnavi07@gmail.com')

    try:
        import alert
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["Subject"] = "TEST: Smart Alert System Ready"
        msg["From"] = alert.SENDER_EMAIL
        msg["To"] = recipient
        body = "This is a test email confirming that the Smart Alert System notifications are working properly."
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(alert.SENDER_EMAIL, alert.SENDER_PASSWORD)
        server.sendmail(alert.SENDER_EMAIL, recipient, msg.as_string())
        server.quit()

        return jsonify({
            'success': True,
            'message': f'Test email sent to {recipient}! Check inbox in 30 seconds.'
        })
    except smtplib.SMTPAuthenticationError:
        return jsonify({
            'error': 'Authentication failed - password is incorrect',
            'tip': 'Go to https://myaccount.google.com/apppasswords to get a valid 16-character App Password'
        }), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

def create_default_admin():
    """Create a default admin user if none exists"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        default_admin = User(
            username='admin',
            email='admin@smartalert.com',
            password=generate_password_hash('admin12345'),
            role='admin',
            is_active=True
        )
        db.session.add(default_admin)
        db.session.commit()
        print("✅ Default admin created:")
        print("   Username: admin")
        print("   Password: admin12345")
        return True
    return False


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")

        print("✅ Smart Alert System Ready!")
        print("🚀 Starting server on http://localhost:5000")
        print("\n📊 Admin Dashboard: http://localhost:5000/admin")

    app.run(debug=True, host='0.0.0.0', port=5000)
