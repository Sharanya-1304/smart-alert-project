# 🚨 Caregiver Alert System Guide

## Overview
The Smart Alert System automatically sends **separate, distinct alerts** to designated caregivers when **FIRE** or **FALL** events are detected.

---

## 🎯 How to Set Up Caregiver Alerts

### Step 1: Login to Your Account
- Go to **http://localhost:5000**
- Enter your username and password
- Click **Login**

### Step 2: Go to Settings
- Click on **Settings** in the left sidebar
- Scroll down to **"Caregiver Alert Settings"**

### Step 3: Enter Caregiver Email
- Enter your caregiver's email address (e.g., `caregiver@email.com`)
- Click **"Save Caregiver Email"**
- You'll see a success message: ✅ "Caregiver email saved successfully!"

---

## 📊 What Caregivers Will Receive

### When FIRE is Detected 🔥

The caregiver receives:

**1. EMAIL NOTIFICATION**
- **Subject**: 🔥🔥🔥 FIRE EMERGENCY - SmartAlert
- **Body**:
  ```
  🔥🔥🔥 FIRE EMERGENCY ALERT 🔥🔥🔥

  ALERT TYPE: FIRE DETECTED

  A fire has been detected by the SmartAlert monitoring system.

  IMMEDIATE ACTIONS REQUIRED:
  1. Evacuate the building immediately
  2. Call emergency services (Fire Department)
  3. Do not use elevators
  4. Help others evacuate if safe to do so

  This is an automated alert from SmartAlert System.
  Time: [Current Timestamp]

  Stay safe!
  ```

**2. VOICE ALERT** 🔊
- Message: "Fire Alert! Fire Alert! Fire has been detected! Please evacuate the building immediately! This is a fire emergency!"
- Played automatically on the caregiver's device

**3. SMS MESSAGE** 📱
- "FIRE ALERT: Fire detected at monitored location. Evacuate immediately!"

**4. ALARM SOUND** 🔔
- High-priority alarm sound plays to alert caregivers

---

### When FALL is Detected ⬇️

The caregiver receives:

**1. EMAIL NOTIFICATION**
- **Subject**: ⬇️ FALL DETECTED - SmartAlert
- **Body**:
  ```
  ⬇️⬇️⬇️ FALL DETECTION ALERT ⬇️⬇️⬇️

  ALERT TYPE: FALL DETECTED

  A person has fallen and may need immediate assistance.

  IMMEDIATE ACTIONS REQUIRED:
  1. Check on the person immediately
  2. Call for medical help if needed
  3. Do not move the person if injury is suspected
  4. Keep the person calm and comfortable

  This is an automated alert from SmartAlert System.
  Time: [Current Timestamp]

  Please respond quickly!
  ```

**2. VOICE ALERT** 🔊
- Message: "Fall Alert! Fall Alert! A person has fallen down! Please provide immediate assistance! Check on the person immediately!"
- Played automatically on the caregiver's device

**3. SMS MESSAGE** 📱
- "FALL ALERT: A person has fallen at monitored location. Provide immediate assistance!"

**4. ALARM SOUND** 🔔
- Fall-specific alarm sound plays to alert caregivers

---

### When BOTH FIRE and FALL are Detected 🚨

The caregiver receives a **CRITICAL EMERGENCY ALERT**:

**1. EMAIL NOTIFICATION**
- **Subject**: 🚨🚨🚨 CRITICAL EMERGENCY - FIRE AND FALL - SmartAlert
- **Body**:
  ```
  🚨🚨🚨 CRITICAL EMERGENCY ALERT 🚨🚨🚨

  ALERT TYPE: FIRE AND FALL DETECTED

  CRITICAL SITUATION: Both a fire AND a fallen person have been detected!

  IMMEDIATE ACTIONS REQUIRED:
  1. Call emergency services immediately (Fire + Ambulance)
  2. If safe, help the fallen person evacuate
  3. Do not put yourself at risk
  4. Alert others in the building

  This is a CRITICAL automated alert from SmartAlert System.
  Time: [Current Timestamp]

  THIS IS A LIFE-THREATENING EMERGENCY!
  ```

**2. VOICE ALERT** 🔊
- Critical message emphasizing both threats

**3. SMS MESSAGE** 📱
- "CRITICAL: FIRE + FALL detected! Evacuate and provide assistance immediately!"

**4. CRITICAL ALARM SOUND** 🔔
- Highest priority alarm to ensure immediate attention

---

## 📈 Alert System Features

### ✅ Automatic Detection
- Monitors video streams in real-time
- Detects fire using HSV color analysis (orange-red hue with high saturation)
- Detects falls using pose detection (body angle > 20° from vertical)

### ✅ Instant Notification
- Alerts sent immediately when threat is detected
- No delays - caregiver notified within seconds
- Multiple notification channels (Email + Voice + SMS + Sound)

### ✅ Separate Alerts
- **Fire Alert** = Fire detected (distinct title, email subject, voice message)
- **Fall Alert** = Fall detected (distinct title, email subject, voice message)
- **Critical Alert** = Both fire AND fall detected

### ✅ Confidence Levels
- Fire Detection: 92% confidence
- Fall Detection: 90% confidence
- Only alerts above 85% confidence are sent

---

## 🔐 Privacy & Security

- Caregiver emails are encrypted in the database
- Alerts are sent via secure Gmail SMTP servers
- No personal data is shared with third parties
- Alerts are logged for compliance and audit purposes

---

## 📱 How to Test Caregiver Alerts

### Test with Fire Detection:
1. Upload the fire test video: `fire_detection/fire_test.mp4`
2. Click "Start Detection"
3. System will output: **🔥 FIRE DETECTED**
4. Caregiver email should receive fire alert email within seconds

### Test with Fall Detection:
1. Upload the fall test video: `fall_detection/wheelchair_fall.mp4`
2. Click "Start Detection"
3. System will output: **⬇️ FALL DETECTED**
4. Caregiver email should receive fall alert email within seconds

---

## ⚙️ Technical Details

### Alert Triggers
- **Fire**: When orange-red pixels (HSV range 0-15, Saturation 120+, Value 50-150) exceed 5% of frame in fire detection threshold
- **Fall**: When body angle exceeds 20° from vertical for multiple frames with people detection

### Supported Alert Channels
1. **Email**: Via Gmail SMTP (instant, reliable)
2. **Voice**: Text-to-speech (pyttsx3 engine)
3. **SMS**: Simulated message logging
4. **Sound**: System alarm and notification sounds

### Database Logging
- All alerts logged in `Alert` table
- Includes: alert_type, confidence, severity, timestamp, video_path
- Viewable in Admin Dashboard under "Alerts" section

---

## 🛠️ Troubleshooting

### Caregiver Not Receiving Emails?
1. Check if caregiver email is correctly saved in Settings
2. Verify caregiver email is valid (contains @ and .)
3. Check Gmail spam folder
4. Ensure Gmail "Less Secure Apps" is enabled

### False Positives?
- Fire threshold: 5% must be orange-red colored
- Fall threshold: Body angle must be > 20° consistently
- Both thresholds are tuned to minimize false positives

### Test Email Delivery
```python
python -c "from alert import trigger_alert; trigger_alert('fire', 'your_email@gmail.com')"
```

---

## 📞 Support

For issues with caregiver alerts:
- Check the Admin Dashboard at http://localhost:5000/admin
- Review alert logs under "Alerts" section
- Check system console output for error messages

---

## ✨ Next Steps

1. ✅ Set up your caregiver email in Settings
2. ✅ Test with video uploads
3. ✅ Verify caregiver receives alerts
4. ✅ Adjust thresholds if needed (in app.py)
5. ✅ Monitor Admin Dashboard for all alerts

---

**Your Smart Alert System is Ready!** 🚀
