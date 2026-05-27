"""Auto login to NetOps using keyboard simulation, then screenshot main window."""
import subprocess
import time
import sys

# Bring login window to foreground and type credentials
ps_login = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindowEx(IntPtr hwndParent, IntPtr hwndChildAfter, string lpszClass, string lpszWindow);
    [DllImport("user32.dll")]
    public static extern int SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, string lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    public const int WM_SETTEXT = 0x000C;
    public const int BM_CLICK = 0x00F5;
    public const uint KEYEVENTF_KEYDOWN = 0x0000;
    public const uint KEYEVENTF_KEYUP = 0x0002;
    public const byte VK_TAB = 0x09;
    public const byte VK_RETURN = 0x0D;
}
"@

# Find NetOps login window
$hwnd = [Win32]::FindWindow($null, "NetOps 用户登录")
if ($hwnd -eq [IntPtr]::Zero) {
    # Try partial title
    [Win32]::EnumWindows([Win32+EnumWindowsProc]{
        param($h, $l)
        if ([Win32]::IsWindowVisible($h)) {
            $sb = New-Object System.Text.StringBuilder 512
            [Win32]::GetWindowText($h, $sb, 512) | Out-Null
            $t = $sb.ToString()
            if ($t -like "*NetOps*") {
                $script:foundHwnd = $h
            }
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null
    $hwnd = $script:foundHwnd
}

if ($hwnd -eq [IntPtr]::Zero) {
    Write-Output "ERROR: NetOps login window not found"
    exit 1
}

Write-Output "Login window HWND: $hwnd"
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

# Find child controls - QLineEdit for username/password, QPushButton for login
$allChildren = @()
$child = [IntPtr]::Zero
while ($true) {
    $child = [Win32]::FindWindowEx($hwnd, $child, $null, $null)
    if ($child -eq [IntPtr]::Zero) { break }
    $sb = New-Object System.Text.StringBuilder 256
    [Win32]::GetWindowText($child, $sb, 256) | Out-Null
    $text = $sb.ToString()
    $allChildren += @{Handle=$child; Text=$text}
    Write-Output "Child handle=$child text='$text'"
}

# Try to find QLineEdit controls and set text directly
$editCount = 0
foreach ($c in $allChildren) {
    # QLineEdit controls usually have empty text initially
    if ($c.Text -eq "" -and $c.Handle -ne [IntPtr]::Zero) {
        $editCount++
        if ($editCount -eq 1) {
            # Username field
            [Win32]::SendMessage($c.Handle, 0x000C, [IntPtr]::Zero, "admin") | Out-Null
            Write-Output "Set username to admin (handle $($c.Handle))"
        } elseif ($editCount -eq 2) {
            # Password field
            [Win32]::SendMessage($c.Handle, 0x000C, [IntPtr]::Zero, "admin") | Out-Null
            Write-Output "Set password (handle $($c.Handle))"
        }
    }
}

Start-Sleep -Milliseconds 500

# Find and click the login button
foreach ($c in $allChildren) {
    if ($c.Text -like "*登录*" -or $c.Text -like "*Login*" -or $c.Text -like "*确定*") {
        [Win32]::SendMessage($c.Handle, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
        Write-Output "Clicked login button: '$($c.Text)' (handle $($c.Handle))"
        break
    }
}

Write-Output "Login attempt completed"
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_login],
    capture_output=True, text=True, timeout=15
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)

# Wait for main window to appear
print("Waiting for main window...")
time.sleep(5)

# Screenshot
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
Write-Output "Screenshot saved"
"""

result2 = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_shoot],
    capture_output=True, text=True, timeout=15
)
print(result2.stdout)
