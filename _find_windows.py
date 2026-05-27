"""Find all NetOps-related windows and their states."""
import subprocess

# Find all windows belonging to NetOps processes
ps_script = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

# List all processes with NetOps name
Get-Process | Where-Object { $_.ProcessName -like '*NetOps*' -or $_.ProcessName -like '*python*' } | ForEach-Object {
    Write-Output "Process: $($_.ProcessName) PID=$($_.Id) MainWindowHandle=$($_.MainWindowHandle) Title='$($_.MainWindowTitle)'"
}

Write-Output "---"

# Try to find by window title
$hwnd = [Win32]::FindWindow($null, "NetOps")
Write-Output "FindWindow 'NetOps': $hwnd"

# Try common PyQt5 window class
$hwnd2 = [Win32]::FindWindow("Qt5QWindowIcon", $null)
Write-Output "FindWindow Qt5QWindowIcon: $hwnd2"

# Enumerate all visible windows with titles
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class WindowEnum {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

[WindowEnum]::EnumWindows([WindowEnum+EnumWindowsProc]{
    param($hWnd, $lParam)
    if ([WindowEnum]::IsWindowVisible($hWnd)) {
        $sb = New-Object System.Text.StringBuilder 256
        [WindowEnum]::GetWindowText($hWnd, $sb, 256) | Out-Null
        $title = $sb.ToString()
        $pid = 0
        [WindowEnum]::GetWindowThreadProcessId($hWnd, [ref]$pid) | Out-Null
        if ($title -ne "") {
            Write-Output "Visible Window: title='$title' handle=$hWnd pid=$pid"
        }
    }
    return $true
}, [IntPtr]::Zero) | Out-Null
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
