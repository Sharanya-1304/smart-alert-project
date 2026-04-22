# QUICK START - CAREGIVER ALERTS

## In 5 Minutes

### 1. Login
- URL: http://localhost:5000
- Username: your_username
- Password: your_password

### 2. Go to Settings
- Click "Settings" in left menu
- URL: http://localhost:5000/settings

### 3. Add Caregiver Email
- Field: "Caregiver Email Address"
- Enter caregiver's email: e.g., `mom@gmail.com`
- Click "Save Caregiver Email"

### 4. Test - Upload Video
- Go to "Start Detection" page
- Upload: `fire_detection/fire_test.mp4` (for fire test)
- OR upload: `fall_detection/wheelchair_fall.mp4` (for fall test)
- System automatically detects threat

### 5. Caregiver Gets Alert
- Email sent instantly to `mom@gmail.com`
- Voice message played
- SMS message logged
- Alarm sound triggered

---

## Endpoints Reference

| Purpose | URL |
|---------|-----|
| Main App | http://localhost:5000 |
| Settings | http://localhost:5000/settings |
| Detection | http://localhost:5000/detection |
| History | http://localhost:5000/history |
| Admin Dashboard | http://localhost:5000/admin |
| View All Alerts | http://localhost:5000/admin/alerts |
| View Caregivers | http://localhost:5000/admin/users |

---

## Alert Types

| Type | When | Caregiver Gets |
|------|------|----------------|
| FIRE | Fire detected (confidence 92%+) | Email + Voice + SMS + Sound |
| FALL | Person falls (confidence 90%+) | Email + Voice + SMS + Sound |
| CRITICAL | Both fire AND fall | Emergency level notification |

---

## Email Examples

### Fire Alert Email
```
Subject: FIRE EMERGENCY - SmartAlert
From: sharanyagummadavelli@gmail.com

FIRE EMERGENCY ALERT

A fire has been detected!

ACTIONS:
1. Evacuate immediately
2. Call fire department
3. Help others evacuate

Time: 2025-03-23 14:32:45
```

### Fall Alert Email
```
Subject: FALL DETECTED - SmartAlert
From: sharanyagummadavelli@gmail.com

FALL DETECTION ALERT

A person has fallen!

ACTIONS:
1. Check on person
2. Call medical help
3. Don't move injured person

Time: 2025-03-23 14:32:45
```

---

## Database Fields

Caregiver email stored in:
```
Table: user
Field: caregiver_email
Type: String(255)
```

Alert records stored in:
```
Table: alert
Fields:
  - alert_type (fire / fall / fire_and_fall)
  - user_id (monitored person)
  - confidence (92% / 90% / 85%+)
  - created_at (timestamp)
  - is_resolved (yes/no)
```

---

## System Flow Diagram

```
User Uploads Video
       ↓
Detection Runs (Fire/Fall)
       ↓
Threat Detected?
    ↙        ↘
   YES       NO → End
    ↓
Get Caregiver Email
    ↓
Trigger Alert
    ↓
        ├─→ Send Email
        ├─→ Play Voice
        ├─→ Send SMS
        └─→ Sound Alert
    ↓
Alert Saved to Database
    ↓
Admin Can View
```

---

## Testing Commands

### Test Fire Alert (Python)
```python
from alert import trigger_alert
trigger_alert('fire', 'caregiver@gmail.com')
```

### Test Fall Alert (Python)
```python
from alert import trigger_alert
trigger_alert('fall', 'caregiver@gmail.com')
```

### Test Critical Alert (Python)
```python
from alert import trigger_alert
trigger_alert('fire_and_fall', 'caregiver@gmail.com')
```

---

## Admin Commands

### View All Alerts
- Go to: http://localhost:5000/admin/alerts
- See: All fire/fall/critical alerts

### View User Caregivers
- Go to: http://localhost:5000/admin/users
- See: Each user's caregiver email

### Resolve Alerts
- Click alert in admin dashboard
- Mark as resolved
- Alert stays in history

---

## Troubleshooting

**Q: Caregiver not receiving email?**
A: Check caregiver email is correctly saved in Settings. Verify email format.

**Q: Fire being detected on normal video?**
A: System threshold is 5% orange-red pixels. Adjust threshold in app.py line 188.

**Q: Fall not detecting?**
A: Body angle threshold is 20°. Adjust threshold in app.py line 210.

**Q: Voice message not playing?**
A: pyttsx3 text-to-speech may be disabled. Enable in settings.

---

## API Endpoints (Manual Testing)

```bash
# Get user profile
curl http://localhost:5000/api/user/profile

# Update caregiver email
curl -X POST http://localhost:5000/api/user/caregiver-email \
  -H "Content-Type: application/json" \
  -d '{"caregiver_email":"caregiver@gmail.com"}'

# Get all alerts
curl http://localhost:5000/api/admin/alerts

# Get user stats
curl http://localhost:5000/api/stats
```

---

## Files Modified for Caregiver Alerts

1. `app.py` - Lines 593-606: Trigger alert on detection
2. `app.py` - Lines 361-384: Save caregiver email API
3. `app.py` - Lines 346-359: Get user profile with caregiver email
4. `templates/settings.html` - Added caregiver email form
5. `alert.py` - trigger_alert() function handles all notifications

---

**Your Smart Alert System is fully operational!**
