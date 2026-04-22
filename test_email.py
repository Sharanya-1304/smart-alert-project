#!/usr/bin/env python3
"""Test Email Sending - Diagnose Issues"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SENDER_EMAIL = "sharanyagummadavelli@gmail.com"
SENDER_PASSWORD = "xgynyhwsiyolqfrt"
RECIPIENT_EMAIL = "venkatajahnavi07@gmail.com"

print("=" * 80)
print("EMAIL DELIVERY TEST")
print("=" * 80)
print(f"\nFROM: {SENDER_EMAIL}")
print(f"TO: {RECIPIENT_EMAIL}")
print(f"PASSWORD: {SENDER_PASSWORD[:4]}...{SENDER_PASSWORD[-4:]}")

# Step 1: Create message
print("\n[STEP 1] Creating email message...")
try:
    msg = MIMEMultipart()
    msg["Subject"] = "TEST: Smart Alert System"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    body = "This is a test email from the Smart Alert System.\n\nIf you see this, notifications are working!"
    msg.attach(MIMEText(body, "plain"))
    print("[OK] Message created successfully")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Step 2: Connect to Gmail
print("\n[STEP 2] Connecting to Gmail SMTP (smtp.gmail.com:587)...")
try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    print("[OK] Connected to SMTP server")
except Exception as e:
    print(f"[ERROR] {e}")
    print("\nTIP: Check your internet connection")
    exit(1)

# Step 3: StartTLS
print("\n[STEP 3] Starting TLS encryption...")
try:
    server.starttls()
    print("[OK] TLS enabled")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Step 4: Login
print("\n[STEP 4] Authenticating with Gmail...")
try:
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("[OK] Authentication SUCCESSFUL!")
except smtplib.SMTPAuthenticationError as e:
    print(f"[ERROR] AUTHENTICATION FAILED")
    print(f"\nDetails: {e}")
    print("\n" + "=" * 80)
    print("SOLUTION: Password is incorrect or not an App Password")
    print("=" * 80)
    print("\nTO FIX THIS:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Then go to: https://myaccount.google.com/apppasswords")
    print("4. Select 'Mail' and 'Windows Computer'")
    print("5. Copy the 16-character password (without spaces)")
    print("6. Update line 17 in alert.py with this new password")
    print("\n")
    server.quit()
    exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"Type: {type(e).__name__}")
    server.quit()
    exit(1)

# Step 5: Send email
print("\n[STEP 5] Sending email...")
try:
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("[OK] Email sent successfully!")
except Exception as e:
    print(f"[ERROR] {e}")
    server.quit()
    exit(1)

# Step 6: Close connection
print("\n[STEP 6] Closing connection...")
try:
    server.quit()
    print("[OK] Connection closed")
except Exception as e:
    print(f"[WARNING] {e}")

print("\n" + "=" * 80)
print("SUCCESS - Email delivery test passed!")
print("=" * 80)
print(f"\nCheck {RECIPIENT_EMAIL} inbox for the test email")
print("\n")
