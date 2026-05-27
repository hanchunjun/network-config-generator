"""Use pyautogui to login to NetOps and screenshot."""
import pyautogui
import time
import subprocess
import sys

# Safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

# Bring NetOps window to front using PowerShell
ps = """
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@
[Win32]::EnumWindows([Win32+EnumWindowsProc]{
    param($h, $l)
    if ([Win32]::IsWindowVisible($h)) {
        $sb = New-Object System.Text.StringBuilder 512
        [Win32]::GetWindowText($h, $sb, 512) | Out-Null
        $t = $sb.ToString()
        if ($t -like "*NetOps*") {
            [Win32]::ShowWindow($h, 9)
            [Win32]::SetForegroundWindow($h)
            Write-Output "Found and focused: '$t' handle=$h"
        }
    }
    return $true
}, [IntPtr]::Zero) | Out-Null
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
time.sleep(1)

# Take screenshot of login window first
print("Taking screenshot of login window...")
pyautogui.screenshot(r"E:\Claude-Work\Projects\NetOps\screenshot_login.png")
print("Login screenshot saved")

# Now try to find and interact with the login form
# The login window should be in the foreground
# We'll use Tab to navigate and type credentials

# Click in the center of the screen to make sure the window is focused
screen_w, screen_h = pyautogui.size()
print(f"Screen: {screen_w}x{screen_h}")

# Press Tab to focus the username field, type username
pyautogui.press('tab')
time.sleep(0.2)
pyautogui.typewrite('admin', interval=0.05)
time.sleep(0.3)

# Press Tab to go to password field
pyautogui.press('tab')
time.sleep(0.2)
pyautogui.typewrite('admin', interval=0.05)
time.sleep(0.3)

# Press Enter to submit
pyautogui.press('enter')
print("Submitted login credentials")
time.sleep(5)

# Take screenshot after login
print("Taking screenshot after login...")
pyautogui.screenshot(r"E:\Claude-Work\Projects\NetOps\screenshot_after_login.png")
print("After-login screenshot saved")

# Check if we're on main window or activation dialog
time.sleep(2)
pyautogui.screenshot(r"E:\Claude-Work\Projects\NetOps\screenshot_check.png")
print("Final screenshot saved to screenshot_check.png")
