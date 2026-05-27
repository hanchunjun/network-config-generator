"""Final screenshot with NetOps window forced to front."""
import subprocess
import time
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

# Bring NetOps to front
ps = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@
$target = [IntPtr]::Zero
[Win32]::EnumWindows([Win32+EnumWindowsProc]{
    param($h, $l)
    if ([Win32]::IsWindowVisible($h)) {
        $sb = New-Object System.Text.StringBuilder 512
        [Win32]::GetWindowText($h, $sb, 512) | Out-Null
        $t = $sb.ToString()
        $pid = 0
        [Win32]::GetWindowThreadProcessId($h, [ref]$pid) | Out-Null
        if ($pid -eq 2928) {
            $script:target = $h
            Write-Output "TARGET: '$t' handle=$h pid=$pid"
        }
    }
    return $true
}, [IntPtr]::Zero) | Out-Null
if ($target -ne [IntPtr]::Zero) {
    [Win32]::ShowWindow($target, 9)
    [Win32]::SetForegroundWindow($target)
    Write-Output "Focused target window"
} else {
    Write-Output "No target window found for PID 2928"
}
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}")

time.sleep(2)

# Take screenshot
pyautogui.screenshot(r"E:\Claude-Work\Projects\NetOps\screenshot_check.png")
print("Screenshot saved to screenshot_check.png")

# Also take a second one after a short delay
time.sleep(1)
pyautogui.screenshot(r"E:\Claude-Work\Projects\NetOps\screenshot_check2.png")
print("Screenshot2 saved to screenshot_check2.png")
