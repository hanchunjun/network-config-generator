"""Capture NetOps screenshots with auto-login."""
import subprocess
import time
import sys
import os

# Use ctypes for window manipulation
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Constants
SW_RESTORE = 9
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
SRCCOPY = 0x00CC0020

class RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_long), ("Top", ctypes.c_long),
                ("Right", ctypes.c_long), ("Bottom", ctypes.c_long)]

def find_netops_window():
    """Find NetOps window handle."""
    result = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    def enum_callback(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            if "NetOps" in title and "Code" not in title:
                result.append((hwnd, title))
        return True
    user32.EnumWindows(enum_callback, 0)
    return result

def get_window_rect(hwnd):
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r

def set_foreground(hwnd):
    user32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(0.5)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.8)

def screenshot_window(hwnd, save_path):
    """Take screenshot of a window and save to file."""
    set_foreground(hwnd)
    r = get_window_rect(hwnd)
    w = r.Right - r.Left
    h = r.Bottom - r.Top
    if w <= 0 or h <= 0:
        print(f"  Invalid size: {w}x{h}")
        return None, None, None

    # Use PIL for screenshot
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(r.Left, r.Top, r.Right, r.Bottom))
        img.save(save_path)
        print(f"  Saved: {save_path} ({w}x{h})")
        return img, w, h
    except ImportError:
        print("  PIL not available, trying ctypes approach...")
        return screenshot_window_ctypes(hwnd, save_path, r, w, h)

def screenshot_window_ctypes(hwnd, save_path, r, w, h):
    """Fallback screenshot using ctypes + GDI."""
    from PIL import Image
    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    gdi32.SelectObject(hdc_mem, hbitmap)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, r.Left, r.Top, SRCCOPY)

    # Convert to PIL
    bmpinfo = ctypes.c_buffer(40)
    gdi32.GetObjectW(hbitmap, 40, bmpinfo)

    img = Image.frombuffer(
        'RGB', (w, h),
        ctypes.string_at(bmpinfo.raw, w * h * 4)[::-1],
        'raw', 'BGRX', 0, 1
    )
    img = img.convert('RGB')
    img.save(save_path)

    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    print(f"  Saved: {save_path} ({w}x{h})")
    return img, w, h

def click_at(x, y):
    """Click at absolute screen position."""
    user32.SetCursorPos(x, y)
    time.sleep(0.15)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.15)

def type_string(s):
    """Type a string using SendKeys via PowerShell."""
    # Escape for SendKeys
    escaped = s.replace('+', '{+}').replace('^', '{^}').replace('%', '{%}').replace('~', '{~}').replace('(', '{(}').replace(')', '{)}')
    subprocess.run([
        'powershell', '-Command',
        f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{escaped}")'
    ], capture_output=True)
    time.sleep(0.3)

def main():
    out_dir = r"E:\Claude-Work\Projects\NetOps"

    # Step 1: Kill existing NetOps
    print("Step 1: Cleaning up old processes...")
    subprocess.run(['powershell', '-Command',
        'Get-Process -Name "pythonw","python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*NetOps*" } | Stop-Process -Force -ErrorAction SilentlyContinue'
    ], capture_output=True)
    time.sleep(2)

    # Step 2: Start NetOps
    print("Step 2: Starting NetOps...")
    subprocess.Popen(['pythonw', 'main.py'], cwd=r'E:\Claude-Work\Projects\NetOps')
    time.sleep(7)

    # Step 3: Find login window
    print("Step 3: Finding NetOps window...")
    windows = find_netops_window()
    if not windows:
        print("ERROR: No NetOps window found!")
        return

    hwnd, title = windows[0]
    print(f"  Found: {title}")

    # Step 4: Screenshot login window
    print("Step 4: Screenshotting login window...")
    login_path = os.path.join(out_dir, "ui_login_fresh.png")
    screenshot_window(hwnd, login_path)

    # Step 5: Login
    print("Step 5: Attempting login...")
    r = get_window_rect(hwnd)
    win_w = r.Right - r.Left
    win_h = r.Bottom - r.Top
    cx = r.Left + win_w // 2

    # Click username field
    print("  Clicking username field...")
    click_at(cx, r.Top + 85)
    time.sleep(0.3)
    type_string("admin")

    # Click password field
    print("  Clicking password field...")
    click_at(cx, r.Top + 145)
    time.sleep(0.3)
    type_string("admin")

    # Click login button
    print("  Clicking login button...")
    click_at(cx, r.Top + 210)
    time.sleep(1)

    # Step 6: Wait for main window
    print("Step 6: Waiting for main window...")
    time.sleep(4)

    # Find the window again
    windows = find_netops_window()
    if not windows:
        print("ERROR: No window after login!")
        return

    hwnd2, title2 = windows[0]
    print(f"  Window: {title2}")

    r2 = get_window_rect(hwnd2)
    w2 = r2.Right - r2.Left
    h2 = r2.Bottom - r2.Top
    print(f"  Size: {w2}x{h2}")

    if w2 < 400 or h2 < 400:
        print("  Still on login or small dialog, retrying click...")
        # Maybe the button position was wrong, try again
        cx2 = r2.Left + w2 // 2
        click_at(cx2, r2.Top + 200)
        time.sleep(0.5)
        type_string("admin")
        time.sleep(0.3)
        click_at(cx2, r2.Top + 250)
        time.sleep(4)

        windows = find_netops_window()
        if windows:
            hwnd2, title2 = windows[0]
            r2 = get_window_rect(hwnd2)
            w2 = r2.Right - r2.Left
            h2 = r2.Bottom - r2.Top
            print(f"  Retry window: {title2} Size: {w2}x{h2}")

    # Step 7: Screenshot main window
    print("Step 7: Capturing main window screenshots...")

    # Full window
    main_path = os.path.join(out_dir, "ui_check.png")
    screenshot_window(hwnd2, main_path)

    # Nav area
    nav_w = min(240, w2)
    nav_path = os.path.join(out_dir, "ui_nav_detail.png")
    set_foreground(hwnd2)
    time.sleep(0.3)
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(r2.Left, r2.Top, r2.Left + nav_w, r2.Bottom))
        img.save(nav_path)
        print(f"  Nav area saved: {nav_path}")
    except:
        pass

    # Top buttons
    top_path = os.path.join(out_dir, "ui_top_buttons.png")
    try:
        img = ImageGrab.grab(bbox=(r2.Left, r2.Top + 45, r2.Right, r2.Top + 175))
        img.save(top_path)
        print(f"  Top buttons saved: {top_path}")
    except:
        pass

    # Content area
    content_path = os.path.join(out_dir, "ui_content.png")
    try:
        cw = w2 - 240
        ch = h2 - 175
        if cw > 0 and ch > 0:
            img = ImageGrab.grab(bbox=(r2.Left + 240, r2.Top + 175, r2.Right, r2.Bottom))
            img.save(content_path)
            print(f"  Content area saved: {content_path}")
    except:
        pass

    print("\nDone! All screenshots captured.")

if __name__ == "__main__":
    main()
