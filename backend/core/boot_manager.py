import os
import sys
import winreg as reg

def set_autostart(app_name, exe_path):
    """Adds the app to the Windows Registry for startup."""
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_key, app_name, 0, reg.REG_SZ, exe_path)
        reg.CloseKey(open_key)
        return True
    except Exception as e:
        print(f"Failed to set autostart: {e}")
        return False
