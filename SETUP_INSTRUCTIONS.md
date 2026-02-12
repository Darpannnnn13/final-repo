# 🎯 PARENTEYE - COMPLETE DEPLOYMENT READY

## ✅ Status: READY FOR PRODUCTION

Your **ParentEye Client EXE** is ready to deploy! All files are prepared and tested.

---

## 📦 YOUR FINAL DELIVERABLE

**Location**: `dist/ParentEye.exe`  
**Size**: 117 MB (includes Python runtime + all dependencies)  
**Platform**: Windows 10/11  
**Privileges**: Automatic admin escalation

---

## 🚀 THREE SIMPLE STEPS TO DEPLOY

### **Step 1: Setup Admin Server (On Your PC)**
```bash
Double-click: RUN_SERVER.bat

This will:
  ✓ Check Python installation
  ✓ Install dependencies
  ✓ Configure settings
  ✓ Start the backend server
```

Expected output:
```
WARNING in app.run_simple - Running on http://127.0.0.1:5000
```

Then:
- Open browser: `http://localhost:5000`
- Login with credentials from `.env` file

---

### **Step 2: Deploy on Child PC**
```
1. Copy: dist/ParentEye.exe
   To: Child's computer (any folder)

2. Right-click ParentEye.exe
   Select: "Run as administrator"

3. Windows will ask for permission (click "Yes")

4. Console window appears with setup info
   - Look for: "🔑 DEVICE CLAIM CODE"
   - Save the code (example: ABC123XYZ789)

5. Wait 3-5 seconds, console closes automatically

6. Device added to Windows Startup (auto-runs on boot)
```

---

### **Step 3: Register in Admin Dashboard**
```
1. Login to dashboard: http://localhost:5000

2. Go to: Devices → Register New Device
   (or look for "Claim Device" button)

3. Enter the CLAIM CODE from Step 2

4. Click "Register" or "Claim"

5. Device appears in dashboard with:
   - Device Name: [Computer Name] - Windows
   - Status: ✅ ONLINE
   - Ready to control!
```

---

## 📋 WHAT HAPPENS AFTER FIRST RUN

### **Automatic Actions**:
- ✅ Device registers with your server
- ✅ Adds itself to Windows Startup folder
- ✅ Starts all monitoring (keystrokes, screenshots, location)
- ✅ No console window appears on subsequent boots
- ✅ Runs silently in background

### **On Every Restart**:
- Automatically starts with Windows
- No user action needed
- No console visible
- Completely silent

### **In Your Admin Dashboard**:
- See device online with ✅ status
- View real-time screenshots
- Monitor keystroke logs
- Block websites and apps
- Send remote commands
- View browser history

---

## 🎮 CONTROL COMMANDS AVAILABLE

Once device is registered, send commands from dashboard:

| Command | Effect |
|---------|--------|
| **Screenshot** | Capture current screen |
| **Webcam** | Take photo from webcam |
| **Lock** | Lock workstation |
| **Restart** | Restart computer |
| **Shutdown** | Turn off computer |
| **Block Site** | Block websites (Google, YouTube, etc.) |
| **Unblock Site** | Unblock websites |
| **Block App** | Block programs (Steam, Instagram, etc.) |
| **Start Keystroke Monitor** | Record what they type |
| **Stop Keystroke Monitor** | Stop recording |
| **Get Location** | Send GPS/IP location |
| **Popup Alert** | Show message with sound |

---

## 📁 FILE REFERENCE

### **For Child PC (Deploy These)**
```
dist/ParentEye.exe          ⭐ Main file - copy to child PC
.env.example                 (if needed for config)
```

### **For Parent/Admin PC (Run These)**
```
RUN_SERVER.bat              ⭐ Start the admin dashboard
                               (double-click to run)

backend.py                   (Python server - run by RUN_SERVER.bat)
requirements.txt             (dependencies - installed by RUN_SERVER.bat)
.env                         (configuration file)
```

### **Documentation**
```
QUICKSTART.md               📖 Quick reference
DEPLOYMENT_GUIDE.md         📖 Detailed guide
SETUP_INSTRUCTIONS.md       📖 This file
```

---

## ⚙️ CONFIGURATION (`.env`)

Before first run, update `.env`:

```env
# Where your backend server is running
BACKEND_URL=http://localhost:5000

# Your MongoDB database
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=child_monitoring

# Admin login password
ADMIN_PASSWORD=YourSecurePassword123
SUPER_ADMIN_PASSWORD=SuperAdmin@2026
```

**Note**: `RUN_SERVER.bat` will help you edit this.

---

## 🔐 SECURITY FEATURES

✅ Admin privilege requirement (cannot be bypassed)  
✅ Windows UAC protection  
✅ Encrypted database connection  
✅ Secure password authentication  
✅ Admin credentials in `.env` (not hardcoded)  
✅ Activity logging in MongoDB  
✅ Command verification and tracking  

---

## ⚡ QUICK TROUBLESHOOTING

### Device doesn't appear in dashboard?
```
1. Check backend is running:
   - RUN_SERVER.bat should show "Running on http://..."

2. Verify .env settings:
   BACKEND_URL must match where backend.py is running

3. Wait 15 seconds after running EXE on child PC

4. Refresh dashboard in browser

5. Check Windows Firewall allows connection
```

### EXE won't run on child PC?
```
1. Right-click ParentEye.exe
2. Properties → Compatibility
3. Check: "Run this program as an administrator"
4. Click Apply → OK
5. Run normally
```

### "Connection refused" error?
```
1. Make sure RUN_SERVER.bat is running
2. Child PC must be on same network as your PC
3. Check Windows Firewall isn't blocking port 5000
4. Check BACKEND_URL in .env matches your IP
```

---

## 📊 SYSTEM REQUIREMENTS

### **Child PC (Where EXE Runs)**
- Windows 10 or 11
- 2GB RAM minimum (4GB recommended)
- 200MB free disk space
- Admin account
- Internet connection

### **Parent/Admin PC (Where You Control)**
- Windows, Mac, or Linux
- Web browser (Chrome, Edge, Firefox)
- MongoDB access (local or cloud)
- Network connection to child PC

---

## 🎯 DEPLOYMENT CHECKLIST

Before deploying to child:
- [ ] MongoDB is installed and running (or cloud instance configured)
- [ ] `MONGODB_URI` in `.env` is correct
- [ ] `BACKEND_URL` in `.env` is configured
- [ ] `RUN_SERVER.bat` works and shows connection confirmed
- [ ] You can login to dashboard at http://localhost:5000
- [ ] Child PC has admin account
- [ ] `dist/ParentEye.exe` exists and is 117+ MB
- [ ] Network between PCs is working

---

## 📞 QUICK START SUMMARY

### Admin PC:
```bash
1. Double-click RUN_SERVER.bat
2. Wait for "Running on http://...:5000"
3. Open browser to http://localhost:5000
4. Login with .env password
```

### Child PC:
```bash
1. Copy ParentEye.exe from dist/ folder
2. Right-click → Run as administrator
3. Save the CLAIM CODE from console
4. Device auto-registers with your server
5. Startup folder is updated automatically
```

### Dashboard:
```
1. Enter CLAIM CODE in admin dashboard
2. Device appears online
3. Start sending commands!
```

---

## 🔄 IF YOU REBUILD THE EXE

If you modify `client.py` or code:

```bash
Double-click: build_exe.bat

OR manually:

python -m PyInstaller ParentEye_Client.spec --distpath=dist --workpath=build
```

New `ParentEye.exe` will be in `dist/` folder.

---

## ✨ WHAT'S NEW IN THIS VERSION

✅ **Silent EXE** - No console window (unless errors)  
✅ **Auto-Register** - Device registers on first run  
✅ **Auto-Startup** - Adds itself to Windows startup  
✅ **Admin Auto-Elevate** - Requests permissions automatically  
✅ **Bundled Runtime** - Includes Python (no installation needed)  
✅ **Full Monitoring** - Keystrokes, screenshots, location, history  
✅ **Remote Control** - Lock, restart, shutdown, block sites/apps  
✅ **Alerts** - Pop-up messages with voice synthesis  

---

## 🎓 NEXT STEPS

1. ✅ **Verify**: Check all files are present
2. ✅ **Configure**: Edit `.env` with your settings
3. ✅ **Start Server**: Run `RUN_SERVER.bat`
4. ✅ **Test**: Login to `http://localhost:5000`
5. ✅ **Deploy**: Copy `ParentEye.exe` to child PC
6. ✅ **Register**: Enter claim code in dashboard
7. ✅ **Control**: Start sending commands!

---

## 📝 IMPORTANT NOTES

1. **First run takes 3-5 minutes** - EXE extracts and initializes
2. **Console line output helps debug** - Read it on first run
3. **Claim code is important** - Save it during setup
4. **Device needs internet** - Constant connection to backend
5. **Admin rights required** - Cannot monitor without them
6. **Startup enabled by default** - Runs on every boot
7. **Multiple child PCs** - Register each one separately

---

**🎉 Your ParentEye system is ready to deploy!**

Questions? Check `DEPLOYMENT_GUIDE.md` or `QUICKSTART.md`

---

*ParentEye © 2026 - Parental Control & Monitoring System*
