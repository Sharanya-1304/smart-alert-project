#!/usr/bin/env python3
"""
Smart Alert - Email Setup Helper
Guides you through setting up Gmail notifications in 2 minutes
"""

import os
import re
import sys

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_step(num, title):
    print(f"\n[STEP {num}] {title}")
    print("-" * 80)

def read_user_input(prompt, placeholder=""):
    if placeholder:
        print(f"\n{prompt}")
        print(f"Example: {placeholder}")
        value = input("Your input: ").strip()
    else:
        value = input(f"\n{prompt}: ").strip()
    return value

print_header("SMART ALERT SYSTEM - EMAIL SETUP")

print("""
This guide will help you set up Gmail notifications in just a few minutes.

Your current status:
- Notifications are DISABLED (Gmail password is incorrect)
- Caregiver email: venkatajahnavi07@gmail.com
- Sender email: sharanyagummadavelli@gmail.com

Next steps:
1. Get a valid Gmail App Password (2 minutes)
2. Configure it in the system (30 seconds)
3. Test it works (instant!)
""")

input_confirm = input("\nReady to continue? (yes/no): ").strip().lower()
if input_confirm not in ['yes', 'y']:
    print("\nSetup cancelled. Run this script again when you're ready.")
    sys.exit(0)

# Step 1: Check if 2FA is enabled
print_step(1, "Verify 2-Step Verification is Enabled")

print("""
Gmail requires 2-Step Verification before you can create an App Password.

Do this NOW:
1. Open: https://myaccount.google.com/security
2. Log in with sharanyagummadavelli@gmail.com if not already logged in
3. Scroll down to "2-Step Verification"
4. If it says "Not set up", click it and enable it
5. Use your phone to verify

Come back when 2FA is enabled, then press any key to continue...
""")

input("Press ENTER to continue...")

# Step 2: Get App Password
print_step(2, "Generate 16-Character App Password")

print("""
Now you'll generate the special password:

Do this NOW:
1. Open: https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Windows Computer" as the device
4. Click "Generate"
5. Google will show a 16-character password with spaces

Example of what you'll see:
    abcd efgh ijkl mnop

Copy the password (without spaces):
    abcdefghijklmnop
""")

app_password = read_user_input(
    "Paste the 16-character password (without spaces)",
    "Example: abcdefghijklmnop"
)

if not app_password or len(app_password) < 8:
    print("\n[ERROR] Invalid password. Please try again.")
    sys.exit(1)

print(f"\n✓ Got password: {app_password[:4]}...{app_password[-4:]}")

# Step 3: Update alert.py
print_step(3, "Save Password to System")

alert_file = "alert.py"

try:
    # Read the current alert.py
    with open(alert_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the password line
    pattern = r'SENDER_PASSWORD = "[^"]*"'
    new_content = re.sub(
        pattern,
        f'SENDER_PASSWORD = "{app_password}"',
        content
    )

    # Write it back
    with open(alert_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Updated {alert_file} with new password")
    print(f"  Location: Line 26")

except Exception as e:
    print(f"[ERROR] Could not update {alert_file}: {str(e)}")
    print("\nManual fix:")
    print(f"  1. Open {alert_file}")
    print(f"  2. Find: SENDER_PASSWORD = \"fjqreyawxdbbwsvv\"")
    print(f"  3. Replace with: SENDER_PASSWORD = \"{app_password}\"")
    print(f"  4. Save the file")
    sys.exit(1)

# Step 4: Test it
print_step(4, "Test Email Delivery")

print(f"""
The password has been configured!

Now let's test if emails actually work:

Option A - Quick Test (Recommended):
    python test_email.py

Option B - Web UI Test:
    1. Open: http://localhost:5000/admin
    2. Click "Email Settings"
    3. Click "Send Test Email"
    4. Check venkatajahnavi07@gmail.com inbox in 30 seconds

Option C - Manual Test:
    Detect a fire or fall in a video, and the alert should
    automatically email venkatajahnavi07@gmail.com
""")

# Final summary
print_header("SETUP COMPLETE!")

print(f"""
Email configuration has been saved!

Configuration details:
  From: sharanyagummadavelli@gmail.com
  To:   venkatajahnavi07@gmail.com
  Password: {app_password[:4]}...{app_password[-4:]} (set)

Next actions:
  1. Restart your Flask server (Ctrl+C, then python app.py)
  2. Run: python test_email.py
  3. Check if test email arrives in 30 seconds

If you don't see emails:
  - Check the Spam folder
  - Run test_email.py to see detailed error messages
  - Read EMAIL_SETUP.md for troubleshooting

🎉 Your caregiver will now receive alerts when fire or fall is detected!
""")

print("\nQuestions? Read this file: EMAIL_SETUP.md")
