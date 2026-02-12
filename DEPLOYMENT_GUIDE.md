# ParentEye Client EXE - Setup & Deployment Guide

## ✅ What You Have

A production-ready executable: **`dist/ParentEye.exe`** (122 MB)

This EXE includes:
- ✓ No console window (runs silently)
- ✓ Auto-registers device with admin panel
- ✓ Admin privilege elevation (UAC prompt on first run)
- ✓ Auto-adds itself to Windows Startup folder
- ✓ All dependencies bundled (Python runtime, libraries, etc.)
- ✓ Monitoring: Keylogging, screenshots, webcam, location, browser history
- ✓ Control: Website blocking, app blocking, alerts, lock/restart commands

---

## 🚀 How to Run on Child PC

### **Option 1: Direct Run (Recommended)**

1. **Copy the EXE** to the child's PC:
   - Copy `dist/ParentEye.exe` to the child's computer
   - Can be placed anywhere (Desktop, Downloads, Program Files, etc.)

2. **Run as Administrator**:
   - Right-click `ParentEye.exe`
   - Select "Run as administrator"
   - **IMPORTANT**: On first run, you'll see a Windows UAC (User Account Control) prompt asking for admin privileges
   - Click "Yes" to allow

3. **What Happens**:
   - Console window appears briefly to initialize
   - Device automatically registers with your admin panel
   - A **CLAIM CODE** appears in the console (save this!)
   - EXE adds itself to Windows Startup folder
   - Application starts monitoring silently in the background

4. **Expected Console Output**:
   ```
   ============================================================
   🚀 ParentEye Client Started
   ============================================================
   Device ID: CHILD-PC-NAME
   Backend Server: http://your-server:5000
   ============================================================
   
   ============================================================
   🔑 DEVICE CLAIM CODE
   Code: ABC123XYZ789
   Parent: login to dashboard and enter this code to claim this device
   ============================================================
   ```

---

### **Option 2: Silent Auto-Start (For Future Reboots)**

Once added to startup (from Option 1), the EXE will:
- Automatically run when the child's PC boots
- No console window visible
- No user intervention needed
- Runs completely silently in the background

**Note**: You can verify it's running by:
- Opening Task Manager (Ctrl+Shift+Esc)
- Look for "ParentEye" process
- Or check Startup folder:
  - Path: `C:\Users\[Username]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
  - Should see: `ParentEye_Client.lnk`

---

## 📋 Admin Panel Registration

### **After Running the EXE**:

1. **Login to your Admin Dashboard**
   - Go to: `http://your-server:5000/login` (or your configured backend URL)
   - Login with your admin credentials

2. **Register the Device**
   - Look for "Register Device" or "Claim Device" section
   - Enter the **CLAIM CODE** from the console output
   - Click "Claim" or "Register"

3. **Device Now Appears in Dashboard**:
   - Device name: `[Computer-Name] - Windows`
   - Device ID: Hostname
   - Status: ✅ Online
   - Can now assign commands, monitoring, blocking rules

---

## 🎮 Assigning Commands from Admin Panel

Once the device is registered:

1. **Select the child's device** from your dashboard
2. **Send Commands**:
   - **Screenshot**: Take a screenshot
   - **Webcam**: Capture webcam photo
   - **Lock**: Lock the workstation
   - **Shutdown**: Turn off the PC
   - **Restart**: Restart the PC
   - **Block Site**: Block websites (Google, YouTube, etc.)
   - **Unblock Site**: Unblock websites
   - **Block App**: Block applications (Games, Instagram, etc.)
   - **Keystroke Monitor**: Start/stop keystroke logging
   - **Location**: Get GPS location (if device has GPS or uses IP geolocation)
   - **Popup Alert**: Display alerts with voice

3. **Monitor in Real-Time**:
   - View screenshots
   - See webcam captures
   - Check keystroke logs
   - Monitor browser history
   - Track app usage
   - View visited websites

---

## 🔧 System Requirements (Child PC)

- **OS**: Windows 10 or Windows 11
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 200MB free space
- **Network**: Internet connection required
- **Permissions**: Must run with Administrator privileges

### **Database & Server Requirements (Admin/Parent PC)**

- **MongoDB**: Local or cloud MongoDB instance (configured in `.env`)
- **Backend**: Flask server running (`backend.py`)
- **Connection**: Both parent and child PCs need to reach the backend server

---

## 📁 File Structure After Build

```
ParentEye1/
├── dist/
│   ├── ParentEye.exe          ⭐ Main executable (deploy this!)
│   └── [other runtime files]
├── build/                      (temporary, can delete)
├── client.py                   (source code)
├── client_exe.py              (wrapper for EXE)
├── backend.py                 (admin server - run on parent PC)
├── ParentEye_Client.spec      (PyInstaller configuration)
├── build_exe.bat              (compile script)
└── .env                       (configuration)
```

---

## 🔐 Environment Configuration (`.env`)

The EXE reads from `.env` file in the same directory. Make sure these are set:

```env
# Backend server URL
BACKEND_URL=http://localhost:5000

# MongoDB connection
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=child_monitoring

# Admin credentials
ADMIN_PASSWORD=YourSecurePassword123
SUPER_ADMIN_PASSWORD=SuperAdmin@2026
```

**If `.env` is missing**, the EXE will:
- Create it from `.env.example` automatically
- Use default values (localhost)
- **You'll need to configure it before first run**

---

## ⚡ Troubleshooting

### **Problem: "Admin privileges required" error**

**Solution**:
- Right-click `ParentEye.exe` → Properties
- Select "Compatibility" tab
- Check "Run this program as an administrator"
- Click "Apply" → "OK"
- Run the EXE normally (admin mode is now always enabled)

---

### **Problem: Device doesn't appear in admin panel**

**Solution**:
1. Check if backend server is running:
   ```bash
   python backend.py
   ```
   - Should show: `WARNING in app.run_simple - Running on http://0.0.0.0:5000`

2. Verify `.env` settings match:
   - `BACKEND_URL` must point to where backend.py is running
   - `MONGODB_URI` must be accessible

3. Check internet connection on child PC

4. Wait 10-15 seconds after running EXE (registration happens automatically)

5. Try refreshing the admin dashboard page

---

### **Problem: "Connection refused" or "Cannot reach backend"**

**Solution**:
- Make sure backend server is running
- Check if child PC can reach the backend PC (same network)
- Verify firewall isn't blocking port 5000
- Test connection: ping backend-pc-address

---

### **Problem: EXE won't exit or stays running after 'Stop' command**

**Normal Behavior**: 
- The EXE runs continuously in the background
- It's supposed to keep running for monitoring
- If you want to stop it:
  1. Press `Ctrl+C` in the console (if still visible)
  2. Or kill process in Task Manager: `ParentEye.exe`
  3. Or use admin panel: "Logout" or "Shutdown" command

---

## 📊 What the EXE Monitors

Once running, the EXE automatically:

1. **Keystrokes**: Records all keyboard input
2. **Screenshots**: Takes periodic screenshots
3. **Apps**: Tracks active applications
4. **Browser History**: Monitors visited websites
5. **Browser Usage**: Tracks Chrome, Edge, Firefox usage time
6. **Location**: Sends GPS/IP location periodically
7. **System Info**: Monitors CPU, RAM, disk usage
8. **Webcam**: Can capture on command
9. **Screen Recording**: Can record screen on command

All data is sent to MongoDB backend in real-time.

---

## 🔄 Rebuilding the EXE (After Code Changes)

If you modify `client.py` or `client_exe.py`:

```bash
# Run the build script
build_exe.bat

# Or manually:
python -m PyInstaller ParentEye_Client.spec --distpath=dist --workpath=build

# New EXE will be in: dist/ParentEye.exe
```

---

## 📝 Deployment Checklist

- [ ] `.env` configured with correct server URL and MongoDB
- [ ] Backend server (`backend.py`) is running
- [ ] MongoDB instance is accessible
- [ ] Firewall port 5000 is open (or adjust in `.env`)
- [ ] `dist/ParentEye.exe` is on child PC
- [ ] Child PC has admin account
- [ ] EXE is run with admin privileges
- [ ] CLAIM CODE is obtained from console output
- [ ] Device is registered in admin panel
- [ ] Admin panel shows device as "Online"

---

## 🎯 Next Steps

1. ✅ **Copy EXE**: Move `dist/ParentEye.exe` to child's PC
2. ✅ **Run with Admin**: Right-click → Run as administrator
3. ✅ **Get Claim Code**: Copy the code from console
4. ✅ **Register**: Login to dashboard and enter claim code
5. ✅ **Start Monitoring**: Receive device in admin panel
6. ✅ **Assign Commands**: Send control commands from dashboard
7. ✅ **Monitor Activity**: View all logs, screenshots, history

---

## ❓ Questions?

- **Backend not accessible?** Check `BACKEND_URL` in `.env`
- **Device won't register?** Verify MongoDB connection
- **Commands not executing?** Check device status in admin panel
- **Need to trace issues?** Run with console: `python client_exe.py`

---

**ParentEye © 2026** - Child Monitoring & Parental Control System
