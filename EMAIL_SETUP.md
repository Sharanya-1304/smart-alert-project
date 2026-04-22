# Email Setup Guide - Smart Alert System

## Problem
Currently, notifications are **NOT being sent** because the Gmail password is incorrect.

## Solution
You need to get a valid **Gmail App Password** and configure it in the system.

---

## Step-by-Step Setup (Takes 2-3 minutes)

### Step 1: Enable 2-Step Verification on sharanyagummadavelli@gmail.com
1. Go to: https://myaccount.google.com/security
2. Look for "2-Step Verification"
3. Click "Enable 2-Step Verification" (follow the prompts)
4. Use your phone number to verify

### Step 2: Generate Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select:
   - **Application**: Mail
   - **Device**: Windows Computer
3. Click "Generate"
4. Google will show you a 16-character password with spaces, like:
   ```
   abcd efgh ijkl mnop
   ```
5. **Copy this password** (remove the spaces)
   ```
   abcdefghijklmnop
   ```

### Step 3: Configure in Smart Alert System

#### Option A: Web UI (EASIEST - Recommended)
1. Open: http://localhost:5000/admin
2. Click "Email Settings" in the left sidebar
3. Paste your 16-character password into the text box
4. Click "Save App Password"
5. Click "Send Test Email" to verify it works
6. **Done!** Notifications will now be sent to venkatajahnavi07@gmail.com

#### Option B: Direct File Edit (if web UI doesn't work)
1. Open `alert.py` in a text editor
2. Find line 26: `SENDER_PASSWORD = "fjqreyawxdbbwsvv"`
3. Replace with your password: `SENDER_PASSWORD = "abcdefghijklmnop"`
4. Save the file
5. Restart Flask
6. Notifications will now work

---

## Testing

After setup, you should see test emails arrive in venkatajahnavi07@gmail.com within 30 seconds.

If the test email doesn't arrive:
1. Check the **Spam folder** (Gmail sometimes puts test emails there)
2. Go back to Email Settings and click "Send Test Email" again
3. Check the error message for more details

---

## What Gets Sent

The system will now send **automatic alerts** to venkatajahnavi07@gmail.com whenever:
- 🔥 **FIRE** is detected in video
- 👤 **FALL** is detected in video

Each alert includes:
- Alert type (FIRE or FALL)
- Confidence percentage
- Exact timestamp
- Full video analysis details

---

## Current Configuration

- **Sending From**: sharanyagummadavelli@gmail.com
- **Sending To**: venkatajahnavi07@gmail.com (caregiver)
- **Notification Methods**:
  - Email ✅
  - SMS (logged to sms_log.txt)
  - Voice Alert (TTS)
  - Sound Alarm

---

## Troubleshooting

### Q: "Username and Password not accepted" error
**A**: The password is incorrect. Go back to Step 2 and copy the exact 16-character password without spaces.

### Q: "2-Step Verification" option not showing
**A**: You may need to log out and log back in to your Google account, or use a different browser.

### Q: Emails arrive in Spam folder
**A**: This is normal for test emails. Mark the sender as "Not Spam" and future emails will go to Inbox.

### Q: Still having issues?
**A**: Check these files for error logs:
- `alerts_log.txt` - All alert attempts
- `email_queue.txt` - Failed emails (will be retried when password is fixed)
- `email_sent.txt` - Successfully sent emails

---

## Alternative: Check Email Status Right Now

Run this test script to verify your setup:
```bash
python test_email.py
```

This will show you exactly where the problem is and guide you to fix it.

---

**Important**: Once you save the App Password in the Email Settings page, restart your Flask server for changes to take effect.

If your Flask is running, it will automatically reload the updated password when any file is modified. Just wait 2-3 seconds after saving.

