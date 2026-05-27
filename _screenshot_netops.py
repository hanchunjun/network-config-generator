"""Screenshot NetOps window specifically by bringing it to foreground."""
import subprocess
import sys
import time

# First, bring NetOps.exe window to foreground using PowerShell
bring_to_front = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);
}
"@
$proc = Get-Process | Where-Object { $_.ProcessName -eq 'NetOps' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($proc) {
    $hwnd = $proc.MainWindowHandle
    [Win32]::ShowWindow($hwnd, 9)  # SW_RESTORE = 9
    [Win32]::SetForegroundWindow($hwnd)
    Write-Output "Brought NetOps to front, HWND: $hwnd"
    Write-Output "Title: $($proc.MainWindowTitle)"
} else {
    Write-Output "ERROR: NetOps main window not found"
    Get-Process | Where-Object { $_.ProcessName -like '*NetOps*' } | ForEach-Object {
        Write-Output "Found: $($_.ProcessName) PID=$($_.Id) Title='$($_.MainWindowTitle)' Handle=$($_.MainWindowHandle)"
    }
}
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", bring_to_front],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)

# Wait for window to come to front
time.sleep(2)

# Now take screenshot
ps_screenshot = r"""
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
Write-Output "Screenshot saved"
"""

result2 = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_screenshot],
    capture_output=True, text=True, timeout=15
)
print(result2.stdout)
if result2.stderr:
    print(f"STDERR: {result2.stderr}", file=sys.stderr)
print(f"Exit code: {result2.returncode}")
