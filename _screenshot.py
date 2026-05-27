"""Screenshot utility for NetOps UI check."""
import subprocess
import sys

ps_script = r"""
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
Write-Output "Screenshot saved to $savePath"
Write-Output "Resolution: $($bounds.Width)x$($bounds.Height)"
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True, text=True, timeout=15
)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
print(f"Exit code: {result.returncode}")
