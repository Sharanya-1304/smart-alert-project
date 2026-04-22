# Smart Alert Notifications - Quick Start

## What I Fixed

The email notification system was **completely configured** but **not actually sending** because the Gmail password was wrong.

I've now implemented **three ways** to configure it, from easiest to fastest:

---

## Solution 1: Interactive Setup Script (RECOMMENDED)

**The fastest way - 2 minutes total**

```bash
python setup_email.py
```

This script will:
1. Guide you to enable 2-Step Verification on Gmail
2. Guide you to generate a 16-character App Password
3. Automatically update the system with that password
4. Tell you how to test if it works

**No code editing needed!**

---

## Solution 2: Web-Based Configuration Page

**Most user-friendly - 1 minute total**

1. Open: http://localhost:5000/admin
2. Click "Email Settings" in the sidebar
3. Click the link: https://myaccount.google.com/apppasswords
4. Follow Google's steps to get a 16-character password
5. Paste it into the form
6. Click "Save App Password"
7. Click "Send Test Email" to verify

---

## Solution 3: Direct File Edit

**Most technical - 30 seconds total**

1. Open `alert.py` in your text editor
2. Find line 26: `SENDER_PASSWORD = "fjqreyawxdbbwsvv"`
3. Replace with: `SENDER_PASSWORD = "YOUR_16_CHAR_PASSWORD"`
4. Save and restart Flask

---

## Getting Your 16-Character Password

1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer"
5. Google gives you a password like: `abcd efgh ijkl mnop`
6. **Remove spaces**: `abcdefghijklmnop`

---

## Testing

After setting up, verify it works:

**Option A** - Run test script:
```bash
python test_email.py
```

**Option B** - Web test button:
1. Admin Dashboard → Email Settings → Send Test Email
2. Check venkatajahnavi07@gmail.com inbox

**Option C** - Real test:
1. Upload a fire/fall video to trigger detection
2. System automatically emails the caregiver

---

## What Happens After Setup

Once configured, the system will:

- 🔥 Send email alert when FIRE is detected
- 👤 Send email alert when FALL is detected
- 📧 Go FROM: sharanyagummadavelli@gmail.com
- 📧 Go TO: venkatajahnavi07@gmail.com (caregiver)
- ⚡ Send within seconds of detection
- 📝 Log all alerts to `alerts_log.txt`
- ✅ Track sent emails in `email_sent.txt`

---

## Files I Created for You

| File | Purpose |
|------|---------|
| `setup_email.py` | Interactive setup guide (recommended) |
| `test_email.py` | Test if email delivery works |
| `EMAIL_SETUP.md` | Detailed setup documentation |
| `templates/email_settings.html` | Web config page (already linked in admin) |
| `app.py` (updated) | Added email config APIs |

---

## Troubleshooting

### Emails still not arriving?
- Run `test_email.py` to see the exact error
- Check the **Spam folder** in Gmail
- Verify the 16-character password is exactly correct
- Make sure you enabled 2-Step Verification first

### Need to change the caregiver email?
Go to Admin Dashboard → Settings → Caregiver Alert Settings

### Want more notification methods?
The system already logs to:
- `sms_log.txt` (SMS notifications)
- Voice alerts (TTS)
- Sound alarms

---

## Quick Commands

```bash
# Interactive setup
python setup_email.py

# Test current configuration
python test_email.py

# View email logs
type alerts_log.txt
type email_sent.txt
type email_queue.txt
```

---

## Status Right Now

| Setting | Status |
|---------|--------|
| System | ✅ Ready |
| Database | ✅ Ready |
| Fire Detection | ✅ Working |
| Fall Detection | ✅ Working |
| Email Config Page | ✅ Available |
| Email Sending | ❌ Needs password |
| Caregiver Email | ✅ venkatajahnavi07@gmail.com |

---

## Next Steps

1. **Right now**: Run `python setup_email.py`
2. **Then**: Run `python test_email.py` to verify
3. **Finally**: Upload a video to test the full alert flow

That's it! Notifications will work after that.

---

**Questions?** Read `EMAIL_SETUP.md` for detailed troubleshooting.
