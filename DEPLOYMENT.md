# Backend Deployment Guide

## 🔒 SECURITY WARNING
Your .env file was on GitHub! The credentials are now public. You MUST:
1. ✅ Change MongoDB password in Atlas
2. ✅ Regenerate Gemini API key in Google Cloud Console
3. ✅ Change ADMIN_PASSWORD and SUPER_ADMIN_PASSWORD

## 📦 Files Needed on Deployment Server

```
backend.py
templates/
  └── index.html
.env (create fresh on server)
requirements.txt
```

## 🚀 Deployment Steps

### 1. On Deployment Server (VPS/Cloud)

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Clone repo (without .env - it's now ignored)
git clone https://github.com/RONITTELI/ParentEye1.git
cd ParentEye1

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Create .env on Server

Create a NEW `.env` file on the server with:

```env
# CHANGE THIS to your server's public IP or domain!
BACKEND_URL=http://YOUR_SERVER_IP:5000

# MongoDB Atlas (CHANGE PASSWORD!)
MONGODB_URI=mongodb+srv://ParentEye:NEW_PASSWORD_HERE@cyber-lab.7x3prok.mongodb.net/?appName=Cyber-Lab
DB_NAME=child_monitoring

# Change these passwords!
ADMIN_PASSWORD=NewSecurePassword123!
SUPER_ADMIN_PASSWORD=NewAdminPass456!

# Regenerate this API key in Google Cloud Console!
GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
GEMINI_MODEL=gemini-1.0-pro

# Production settings
FLASK_ENV=production
SECRET_KEY=generate_random_key_here
```

### 3. Configure MongoDB Atlas

1. Go to MongoDB Atlas → Network Access
2. Add your server's IP address to IP Whitelist
3. Or use `0.0.0.0/0` (allow all - less secure)

### 4. Run Backend

**Option A: Direct Run (Testing)**
```bash
python backend.py
```

**Option B: Production with Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend:app
```

**Option C: Background with systemd (Linux)**
Create `/etc/systemd/system/parenteye.service`:
```ini
[Unit]
Description=ParentEye Backend
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/path/to/ParentEye1
Environment="PATH=/path/to/ParentEye1/.venv/bin"
ExecStart=/path/to/ParentEye1/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 backend:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable parenteye
sudo systemctl start parenteye
sudo systemctl status parenteye
```

### 5. Firewall Configuration

**Open port 5000:**
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 6. Update Client .env Files

On each child PC, update `.env`:
```env
BACKEND_URL=http://YOUR_SERVER_PUBLIC_IP:5000
MONGODB_URI=mongodb+srv://...same as backend...
DB_NAME=child_monitoring
```

### 7. Test Deployment

1. Open browser: `http://YOUR_SERVER_IP:5000`
2. Login with new credentials
3. Check if dashboard loads
4. Start client on child PC
5. Verify device appears in dashboard

## 🔐 Security Checklist

- [ ] Changed MongoDB password
- [ ] Regenerated Gemini API key
- [ ] Changed ADMIN_PASSWORD
- [ ] Changed SUPER_ADMIN_PASSWORD
- [ ] Added SECRET_KEY to .env
- [ ] Whitelisted server IP in MongoDB Atlas
- [ ] Configured firewall rules
- [ ] .env files are NOT in git

## 🌐 Optional: Use Domain Name

1. Point domain to server IP (DNS A record)
2. Update BACKEND_URL to: `http://yourdomain.com:5000`
3. Consider using nginx reverse proxy for SSL (HTTPS)

## 📊 Monitor Deployment

Check logs:
```bash
# If using systemd
sudo journalctl -u parenteye -f

# If running directly
python backend.py  # logs show in terminal
```

## ⚠️ Important Notes

- Port 5000 must be accessible from internet for clients to connect
- Use HTTPS in production (setup nginx with Let's Encrypt SSL)
- Keep .env file secure - never commit to git
- Backup MongoDB regularly
