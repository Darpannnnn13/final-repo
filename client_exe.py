"""
PRODUCTION CLIENT FOR PARENTEYE - EXE WRAPPER
Runs on child's computer with admin privileges
Auto-registers device, adds to startup, runs silently
"""
import os
import sys
import ctypes
import json
import shutil
import winreg
from pathlib import Path

# Hide console window on Windows
def hide_console():
    """Hide the console window on Windows"""
    try:
        if sys.platform == 'win32':
            import ctypes
            FreeConsole = ctypes.windll.kernel32.FreeConsole
            FreeConsole()
    except Exception:
        pass

def is_admin():
    """Check if user has admin privileges"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except Exception:
        return False

def ensure_admin():
    """Re-run script with admin privileges if needed"""
    if not is_admin():
        # Try to re-run with admin privileges
        try:
            ctypes.windll.shell.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
            sys.exit()
        except Exception:
            print("ERROR: This application requires administrator privileges!")
            print("Please right-click and select 'Run as administrator' or reinstall.")
            import time
            time.sleep(3)
            sys.exit(1)

def add_to_startup(exe_path):
    """Add the program to Windows startup folder"""
    try:
        # Get the startup folder path
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_folder.mkdir(parents=True, exist_ok=True)
        
        # Create a shortcut (Windows .lnk) or batch file
        shortcut_path = startup_folder / "ParentEye_Client.lnk"
        
        # Create using VBScript (more reliable for creating shortcuts)
        vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_path}"
oLink.WorkingDirectory = "{Path(exe_path).parent}"
oLink.WindowStyle = 7
oLink.Save
'''
        vbs_file = Path(exe_path).parent / "create_shortcut.vbs"
        vbs_file.write_text(vbs_content)
        
        # Run the VBS script
        os.system(f'cscript.exe "{vbs_file}" //nologo')
        vbs_file.unlink()
        
        print(f" Added to startup folder: {shortcut_path}")
        return True
    except Exception as e:
        print(f"️ Warning: Could not add to startup folder: {e}")
        try:
            # Fallback: Add to registry
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "ParentEye", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(reg_key)
            print(f" Added to Windows registry startup")
            return True
        except Exception as e2:
            print(f" Failed to add to startup: {e2}")
            return False

def setup_environment():
    """Set up environment variables and config"""
    env_file = Path(__file__).parent / ".env"
    
    # If .env doesn't exist, create from example
    if not env_file.exists():
        example_file = Path(__file__).parent / ".env.example"
        if example_file.exists():
            shutil.copy(example_file, env_file)
            print(" Created .env from .env.example")

def main():
    """Main entry point"""
    # Ensure admin privileges
    ensure_admin()
    
    # Hide console window
    hide_console()
    
    # Setup environment
    setup_environment()
    
    # Get the path to this executable
    exe_path = sys.executable if hasattr(sys, 'frozen') else os.path.abspath(__file__)
    
    # Add to startup if this is the EXE
    if hasattr(sys, 'frozen'):
        add_to_startup(exe_path)
    
    print("\n" + "="*70)
    print(" ParentEye Client Starting...")
    print("="*70)
    
    # Now import and run the actual client
    try:
        print("Loading ParentEye monitoring modules...")
        from client import main as client_main
        
        # Run the client
        client_main()
        
    except ImportError as e:
        print(f" ERROR: Could not import client module: {e}")
        print("Make sure client.py is in the same directory")
        import time
        time.sleep(5)
        sys.exit(1)
    except Exception as e:
        print(f" UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        import time
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    main()
