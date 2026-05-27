"""Login to NetOps and then screenshot the main window."""
import subprocess
import time
import sys

# Find the login window and interact with it
# First, let's see the accessibility tree of the login window
ps_enum = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindowEx(IntPtr hwndParent, IntPtr hwndChildAfter, string lpszClass, string lpszWindow);
    [DllImport("user32.dll")]
    public static extern int SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, string lParam);
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    public const int WM_SETTEXT = 0x000C;
    public const int WM_CHAR = 0x0102;
    public const int BM_CLICK = 0x00F5;
    public const int WM_LBUTTONDOWN = 0x0201;
    public const int WM_LBUTTONUP = 0x0202;
    public const uint KEYEVENTF_KEYDOWN = 0x0000;
    public const uint KEYEVENTF_KEYUP = 0x0002;
}
"@

# Find NetOps login window
$hwnd = [Win32]::FindWindow($null, "NetOps 用户登录")
if ($hwnd -eq [IntPtr]::Zero) {
    # Try partial match
    [Win32]::EnumWindows([Win32+EnumWindowsProc]{
        param($h, $l)
        if ([Win32]::IsWindowVisible($h)) {
            $sb = New-Object System.Text.StringBuilder 512
            [Win32]::GetWindowText($h, $sb, 512) | Out-Null
            $t = $sb.ToString()
            if ($t -like "*NetOps*" -or $t -like "*登录*") {
                Write-Output "Found: '$t' handle=$h"
            }
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null
} else {
    Write-Output "Found login window: $hwnd"

    # Enumerate child controls
    $children = @()
    $child = [IntPtr]::Zero
    while ($true) {
        $child = [Win32]::FindWindowEx($hwnd, $child, $null, $null)
        if ($child -eq [IntPtr]::Zero) { break }
        $sb = New-Object System.Text.StringBuilder 256
        [Win32]::GetWindowText($child, $sb, 256) | Out-Null
        $text = $sb.ToString()
        Write-Output "Child: handle=$child text='$text'"
    }
}
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_enum],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
