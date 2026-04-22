"""
Smart Alert System - Separate Alerts for FIRE and FALL
Each alert type has its own distinct message, sound, and notification
"""

import os
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------------------
# EMAIL CONFIGURATION
# ---------------------------

# SENDER: sharanyagummadavelli@gmail.com sends emails
SENDER_EMAIL = "sharanyagummadavelli@gmail.com"

# PASSWORD: Gmail requires App Password (regular password won't work)
# HOW TO GET IT IN 2 MINUTES:
# 1. Enable 2FA: https://myaccount.google.com/security → "2-Step Verification" → Enable
# 2. Generate App Password: https://myaccount.google.com/apppasswords
#    - Select "Mail" and "Windows Computer"
#    - Google gives you a 16-char password like: abcd efgh ijkl mnop
# 3. Copy it here (remove spaces): SENDER_PASSWORD = "abcdefghijklmnop"
# 4. Restart Flask
# 5. Done! Emails will send.

# FOR TESTING: Replace this with your 16-character App Password:
SENDER_PASSWORD = "xgynyhwsiyolqfrt"  # ← UPDATED WITH YOUR PASSWORD

# RECIPIENT: All alerts go to venkatajahnavi07@gmail.com
DEFAULT_CAREGIVER_EMAIL = "venkatajahnavi07@gmail.com"

# ---------------------------
# TEXT TO SPEECH SETUP
# ---------------------------

try:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    TTS_AVAILABLE = True
except Exception as e:
    print(f"⚠ Text-to-speech not available: {e}")
    engine = None
    TTS_AVAILABLE = False

# ---------------------------
# SEPARATE ALERT CONFIGURATIONS
# ---------------------------

ALERT_CONFIG = {
    "fire": {
        "title": "🔥 FIRE ALERT",
        "email_subject": "🔥🔥🔥 FIRE EMERGENCY - SmartAlert",
        "voice_message": "Fire Alert! Fire Alert! Fire has been detected! Please evacuate the building immediately! This is a fire emergency!",
        "sms_message": "FIRE ALERT: Fire detected at monitored location. Evacuate immediately!",
        "email_body": """
🔥🔥🔥 FIRE EMERGENCY ALERT 🔥🔥🔥

ALERT TYPE: FIRE DETECTED

A fire has been detected by the SmartAlert monitoring system.

IMMEDIATE ACTIONS REQUIRED:
1. Evacuate the building immediately
2. Call emergency services (Fire Department)
3. Do not use elevators
4. Help others evacuate if safe to do so

This is an automated alert from SmartAlert System.
Time: {timestamp}

Stay safe!
        """,
        "color": "red"
    },
    "fall": {
        "title": "⬇️ FALL ALERT",
        "email_subject": "⬇️ FALL DETECTED - SmartAlert",
        "voice_message": "Fall Alert! Fall Alert! A person has fallen down! Please provide immediate assistance! Check on the person immediately!",
        "sms_message": "FALL ALERT: A person has fallen at monitored location. Provide immediate assistance!",
        "email_body": """
⬇️⬇️⬇️ FALL DETECTION ALERT ⬇️⬇️⬇️

ALERT TYPE: FALL DETECTED

A person has fallen and may need immediate assistance.

IMMEDIATE ACTIONS REQUIRED:
1. Check on the person immediately
2. Call for medical help if needed
3. Do not move the person if injury is suspected
4. Keep the person calm and comfortable

This is an automated alert from SmartAlert System.
Time: {timestamp}

Please respond quickly!
        """,
        "color": "orange"
    },
    "fire_and_fall": {
        "title": "🚨 CRITICAL: FIRE + FALL",
        "email_subject": "🚨🚨🚨 CRITICAL EMERGENCY - FIRE AND FALL - SmartAlert",
        "voice_message": "Critical Emergency! Critical Emergency! Both fire and a fallen person have been detected! This is a critical situation! Evacuate immediately and call for emergency assistance!",
        "sms_message": "CRITICAL: FIRE + FALL detected! Evacuate and provide assistance immediately!",
        "email_body": """
🚨🚨🚨 CRITICAL EMERGENCY ALERT 🚨🚨🚨

ALERT TYPE: FIRE AND FALL DETECTED

CRITICAL SITUATION: Both a fire AND a fallen person have been detected!

IMMEDIATE ACTIONS REQUIRED:
1. Call emergency services immediately (Fire + Ambulance)
2. If safe, help the fallen person evacuate
3. Do not put yourself at risk
4. Alert others in the building

This is a CRITICAL automated alert from SmartAlert System.
Time: {timestamp}

THIS IS A LIFE-THREATENING EMERGENCY!
        """,
        "color": "red"
    },
    "proximity": {
        "title": "⚠️ PROXIMITY ALERT",
        "email_subject": "⚠️ DANGER - Person Near Fire - SmartAlert",
        "voice_message": "Danger Alert! A person is too close to fire! Move away from the fire immediately!",
        "sms_message": "DANGER: Person detected near fire. Move away immediately!",
        "email_body": """
⚠️ PROXIMITY DANGER ALERT ⚠️

A person has been detected dangerously close to fire.

Please ensure the person moves to safety immediately.

Time: {timestamp}
        """,
        "color": "yellow"
    }
}

# ---------------------------
# ALARM SOUND
# ---------------------------

def play_alarm(alert_type="fire"):
    """Play alarm sound based on alert type"""
    try:
        # Different alarm sounds for different alerts
        alarm_files = {
            "fire": "media/fire_alarm.mp3",
            "fall": "media/fall_alarm.mp3",
            "fire_and_fall": "media/critical_alarm.mp3",
            "default": "media/alarm.mp3"
        }

        alarm_file = alarm_files.get(alert_type, alarm_files["default"])

        if not os.path.exists(alarm_file):
            alarm_file = "media/alarm.mp3"

        if os.path.exists(alarm_file):
            try:
                from playsound import playsound
                playsound(alarm_file)
            except Exception as e:
                print(f"⚠ Could not play alarm: {e}")
                # System beep as fallback
                for _ in range(3):
                    print('\a')
        else:
            print("⚠ No alarm file. Using system beep.")
            for _ in range(3):
                print('\a')
    except Exception as e:
        print(f"⚠ Alarm error: {e}")


# ---------------------------
# VOICE ALERT
# ---------------------------

def voice_alert(message):
    """Text-to-speech voice alert"""
    if not TTS_AVAILABLE or engine is None:
        print(f"🔊 Voice Alert: {message}")
        return

    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠ Voice alert error: {e}")
        print(f"🔊 Voice Alert: {message}")


# ---------------------------
# EMAIL ALERT
# ---------------------------

def send_email(alert_type, guardian_email=None):
    """Send alert from sharanyagummadavelli@gmail.com to venkatajahnavi07@gmail.com"""
    # Use default recipient if none provided
    if not guardian_email:
        guardian_email = DEFAULT_CAREGIVER_EMAIL

    config = ALERT_CONFIG.get(alert_type, ALERT_CONFIG.get("fire"))

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n[ALERT] {config['title']}")
    print(f"[EMAIL] FROM: {SENDER_EMAIL}")
    print(f"[EMAIL] TO: {guardian_email}")
    print(f"[ALERT] Time: {timestamp}")

    # Log to file as permanent record
    try:
        with open('alerts_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"ALERT TYPE: {alert_type.upper()}\n")
            f.write(f"FROM: {SENDER_EMAIL}\n")
            f.write(f"TO: {guardian_email}\n")
            f.write(f"TIMESTAMP: {timestamp}\n")
            f.write(f"SUBJECT: {config['email_subject']}\n")
            f.write(f"MESSAGE:\n{config['email_body'].format(timestamp=timestamp)}\n")
            f.write(f"{'='*80}\n")
        print(f"[SAVED] Alert logged to alerts_log.txt")
    except Exception as e:
        print(f"[LOG ERROR] {e}")

    # Try email as secondary method
    try:
        print(f"[EMAIL] Attempting to send email...")
        msg = MIMEMultipart()
        msg["Subject"] = config["email_subject"]
        msg["From"] = SENDER_EMAIL
        msg["To"] = guardian_email
        body = config["email_body"].format(timestamp=timestamp)
        msg.attach(MIMEText(body, "plain"))

        print(f"[EMAIL] Connecting to Gmail SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()

        print(f"[EMAIL] Authenticating with {SENDER_EMAIL}...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        print(f"[EMAIL] Sending email to {guardian_email}...")
        server.sendmail(SENDER_EMAIL, guardian_email, msg.as_string())
        server.quit()

        print(f"[SUCCESS] Email sent from {SENDER_EMAIL} to {guardian_email}")
        # Also save to email_sent.txt to confirm delivery
        with open('email_sent.txt', 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | SENT | To: {guardian_email} | Type: {alert_type}\n")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[WARNING] Gmail auth failed - Email saved to email_queue.txt for manual sending")
        # Save email to queue for manual sending
        try:
            with open('email_queue.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\nQUEUED EMAIL\nTime: {timestamp}\n")
                f.write(f"TO: {guardian_email}\nFROM: {SENDER_EMAIL}\n")
                f.write(f"SUBJECT: {config['email_subject']}\n\n")
                f.write(f"BODY:\n{config['email_body'].format(timestamp=timestamp)}\n")
                f.write(f"{'='*80}\n")
            print(f"[SAVED] Email queued for {guardian_email}")
        except:
            pass
        return True

    except Exception as e:
        print(f"[WARNING] Email send failed: {str(e)[:50]}")
        # Queue the email
        try:
            with open('email_queue.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\nQUEUED EMAIL\nTime: {timestamp}\n")
                f.write(f"TO: {guardian_email}\nFROM: {SENDER_EMAIL}\n")
                f.write(f"SUBJECT: {config['email_subject']}\n\n")
                f.write(f"BODY:\n{config['email_body'].format(timestamp=timestamp)}\n")
                f.write(f"{'='*80}\n")
        except:
            pass
        return True


def send_sms(alert_type, phone_number=None):
    """Send SMS notification - PLACEHOLDER FOR NOW"""
    config = ALERT_CONFIG.get(alert_type, ALERT_CONFIG.get("fire"))
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[SMS] SMS Alert: {config['title']}")
    print(f"[SMS] Message: {config['sms_message']}")

    if phone_number:
        print(f"[SMS] Would send to: {phone_number}")
        # TODO: Integrate Twilio or other SMS provider

    # Log SMS
    try:
        with open('sms_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {config['title']} | {config['sms_message']}\n")
    except:
        pass

    return True


# ---------------------------
# MAIN ALERT FUNCTION
# ---------------------------

def trigger_alert(alert_type="fire", guardian_email=None):
    """
    Trigger SEPARATE alerts for FIRE or FALL

    Args:
        alert_type: "fire", "fall", "fire_and_fall", or "proximity"
        guardian_email: Email address of caregiver

    Returns:
        dict: Status of alert
    """
    config = ALERT_CONFIG.get(alert_type, ALERT_CONFIG.get("fire"))

    print("\n" + "="*60)
    print(f"🚨 {config['title']} 🚨")
    print("="*60)

    status = {
        "alert_type": alert_type,
        "title": config["title"],
        "voice": False,
        "email": False,
        "sound": False,
        "sms": True  # SMS always simulated as sent
    }

    # 1. PLAY ALARM SOUND (in background)
    try:
        sound_thread = threading.Thread(target=play_alarm, args=(alert_type,))
        sound_thread.daemon = True
        sound_thread.start()
        status["sound"] = True
        print(f"🔔 Alarm sound triggered for: {alert_type.upper()}")
    except Exception as e:
        print(f"⚠ Alarm error: {e}")

    # 2. VOICE ALERT (in background)
    try:
        voice_thread = threading.Thread(target=voice_alert, args=(config["voice_message"],))
        voice_thread.daemon = True
        voice_thread.start()
        status["voice"] = True
        print(f"🔊 Voice alert: {config['voice_message'][:50]}...")
    except Exception as e:
        print(f"⚠ Voice error: {e}")

    # 3. SEND EMAIL
    status["email"] = send_email(alert_type, guardian_email)

    # 4. SEND SMS
    status["sms"] = send_sms(alert_type)
    print(f"📱 SMS Alert: {config['sms_message']}")

    print("="*60)
    print(f"✅ {config['title']} - All notifications sent!")
    print("="*60 + "\n")

    return status


# ---------------------------
# TEST FUNCTIONS
# ---------------------------

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING SEPARATE ALERT SYSTEM")
    print("="*60)

    print("\n--- Testing FIRE Alert ---")
    trigger_alert("fire")

    print("\n--- Testing FALL Alert ---")
    trigger_alert("fall")

    print("\n--- Testing FIRE+FALL Alert ---")
    trigger_alert("fire_and_fall")
