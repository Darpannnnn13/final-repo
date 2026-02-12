# ParentEye Client - Quick Start

## 🎯 TL;DR (Too Long; Didn't Read)

### For Admin/Parent PC Setup:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env with your settings
# Edit .env file with your MongoDB URL and admin passwords

# 3. Start the backend server
python backend.py

# Server will run on: http://localhost:5000
# Login with admin credentials from .env
```

### For Child PC Setup:
```
1. Copy dist/ParentEye.exe to child's PC
2. Right-click ParentEye.exe → Run as administrator
3. Look for CLAIM CODE in console output
4. Save the claim code
5. Wait 10 seconds for console to close
6. Device will auto-start with Windows
```

### To Register Device:
```
1. Login to admin dashboard (http://localhost:5000)
2. Go to "Devices" or "Register Device"
3. Enter the CLAIM CODE
4. Click "Register" or "Claim"
5. Device appears in dashboard
6. Start assigning commands!
```

---

## 📦 What's Included

### Parent PC (Admin Dashboard):
- **backend.py**: REST API server with web interface
- **templates/**: Admin dashboard HTML
- **static/**: CSS and JavaScript files

### Child PC (Monitoring Client):
- **dist/ParentEye.exe**: Single executable (122 MB)
- **Self-contained**: All dependencies bundled
- **No installation needed**: Just copy and run

---

## 🔑 Key Features

✅ Auto-registers device  
✅ No visible console window (after startup)  
✅ Auto-adds to Windows Startup  
✅ Real-time keystroke monitoring  
✅ Screenshot capture  
✅ Webcam capture  
✅ Website blocking  
✅ App blocking  
✅ Browser history tracking  
✅ Location tracking  
✅ Remote lock/restart commands  
✅ Pop-up alerts with voice

---

## 🚀 Deployment Steps

### Step 1: Prepare Parent PC
```bash
cd ParentEye1
pip install -r requirements.txt
# Edit .env with your settings
python backend.py
```

### Step 2: Deploy to Child PC
```
Copy: dist/ParentEye.exe
To: Child's PC (anywhere: Desktop, Downloads, etc.)
```

### Step 3: Run on Child PC
```
Right-click ParentEye.exe → Run as administrator
Approve UAC prompt
Save CLAIM CODE from console
```

### Step 4: Register in Dashboard
```
Login to admin panel
Enter claim code
Device registered!
```

---

## 📊 File Sizes

- `dist/ParentEye.exe`: 122 MB (includes Python runtime + all libraries)
- Uncompressed after install: ~400-500 MB

---

## 🔧 Configuration

Edit `.env` before running:

```env
BACKEND_URL=http://localhost:5000          # Your server address
MONGODB_URI=mongodb://localhost:27017/     # MongoDB connection
DB_NAME=child_monitoring                    # Database name

ADMIN_PASSWORD=YourSecurePassword123        # Admin panel password
SUPER_ADMIN_PASSWORD=SuperAdmin@2026        # Super admin password
```

---

## ⚡ Quick Commands

| Command | Action |
|---------|--------|
| `python backend.py` | Start admin server |
| `build_exe.bat` | Rebuild the client EXE |
| `python -m PyInstaller ParentEye_Client.spec` | Manual build |

---

## ❓ First Run Checklist

- [ ] Backend (`backend.py`) is running
- [ ] MongoDB is accessible
- [ ] `.env` is configured
- [ ] `ParentEye.exe` exists in `dist/`
- [ ] Child PC has admin account
- [ ] Firewall allows connection to backend

---

## 📌 Important Notes

1. **First Run Takes 3-5 minutes** to extract all files and register
2. **Console closes automatically** after initialization
3. **Device appears in dashboard** after 10-15 seconds
4. **Autostart is enabled** after first run
5. **No user interaction needed** on subsequent boots

---

**Need more details?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
