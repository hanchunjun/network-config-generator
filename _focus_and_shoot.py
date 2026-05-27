"""Find NetOps window, bring to foreground, wait, then screenshot."""
import subprocess
import time
import sys

# Step 1: Find all windows and bring NetOps to front
ps_find = r"""
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
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

# Find python process (NetOps runs as python.exe)
$pyProc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 }
if ($pyProc) {
    foreach ($p in $pyProc) {
        Write-Output "Python PID=$($p.Id) Handle=$($pMainWindowHandle) Title='$($p.MainWindowTitle)'"
        [Win32]::ShowWindow($p.MainWindowHandle, 9)
        [Win32]::SetForegroundWindow($p.MainWindowHandle)
        Write-Output "Set foreground for handle $($p.MainWindowHandle)"
    }
} else {
    Write-Output "No python process with window found"
    # Try to find any visible window
    [Win32]::EnumWindows([Win32+EnumWindowsProc]{
        param($hWnd, $lParam)
        if ([Win32]::IsWindowVisible($hWnd)) {
            $sb = New-Object System.Text.StringBuilder 512
            [Win32]::GetWindowText($hWnd, $sb, 512) | Out-Null
            $title = $sb.ToString()
            $pid = 0
            [Win32]::GetWindowThreadProcessId($hWnd, [ref]$pid) | Out-Null
            $procName = ""
            try { $procName = (Get-Process -Id $pid -ErrorAction SilentlyContinue).ProcessName } catch {}
            if ($title -ne "") {
                Write-Output "Window: '$title' handle=$hWnd pid=$pid proc=$procName"
            }
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null
}
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_find],
    capture_output=True, text=True, timeout=10
)
print("=== Window Find ===")
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)

# Wait for window to come to front
time.sleep(3)

# Take screenshot
ps_shoot = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$savePath = 'E:\Claude-Work\Projects\NetOps\screenshot_check.png'
$bitmap.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
Write-Output "Screenshot saved: $($bounds.Width)x$($bounds.Height)"
"""

result2 = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_shoot],
    capture_output=True, text=True, timeout=15
)
print("=== Screenshot ===")
print(result2.stdout)
if result2.stderr:
    print(f"STDERR: {result2.stderr}", file=sys.stderr)
