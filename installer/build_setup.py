#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
installer/build_setup.py
从 dist/NetOps/ 生成带图标的自解压安装包 NetOps_Setup_0.4.0.exe

原理：
  1. 将 dist/NetOps/ 打包为 data.zip
  2. 将 data.zip 内容附加到引导脚本编译后的 EXE 文件尾部
  3. 引导脚本运行时从自身 EXE 尾部读取 zip 数据并解压安装
  4. 使用 assets/netops.ico 作为安装包图标

用法：
  1. 先执行 pyinstaller NetworkConfigGenerator.spec --noconfirm
  2. 再执行 python installer/build_setup.py
  3. 输出：installer/NetOps_Setup_0.4.0.exe
"""

import os
import sys
import shutil
import zipfile
import struct
import tempfile
import subprocess
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "NetOps"
ASSETS_DIR = PROJECT_ROOT / "assets"
ICON_FILE = ASSETS_DIR / "netops.ico"
OUTPUT_DIR = PROJECT_ROOT / "installer"
OUTPUT_EXE = OUTPUT_DIR / "NetOps_Setup_0.4.0.exe"
TEMP_DIR = Path(tempfile.mkdtemp(prefix="netops_sfx_"))

APP_NAME = "NetOps"
APP_FULL_NAME = "NetOps 企业网络自动化运维平台"
DEFAULT_INSTALL_DIR = os.path.join(
    os.environ.get("PROGRAMFILES", r"C:\Program Files"), APP_NAME
)
DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
START_MENU = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\Windows\Start Menu\Programs\NetOps"
)
DATA_DIRS = ["config", "logs", "projects", "single", "activation"]

# 自解压标记（用于从 EXE 尾部定位 zip 数据）
SFX_MARKER = b"NETOPS_SFX_DATA_V1\x00"
# ──────────────────────────────────────────────────────────


def create_data_zip(zip_path: Path) -> int:
    """将 dist/NetOps/ 打包为 zip"""
    count = 0
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(DIST_DIR)):
            dirs.sort()
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = str(fpath.relative_to(DIST_DIR))
                zf.write(str(fpath), arcname)
                count += 1
    size_kb = zip_path.stat().st_size / 1024
    print("[OK] data.zip: {} files, {:.1f} KB".format(count, size_kb))
    return count


def create_bootstrap_script(script_path: Path) -> None:
    """生成自解压引导脚本（打包为 EXE 后从自身尾部读取 zip）"""
    script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NetOps 自解压安装程序（由 build_setup.py 自动生成）"""

import os
import sys
import shutil
import zipfile
import ctypes
import subprocess
import tempfile
from pathlib import Path

APP_NAME = "''' + APP_NAME + '''"
APP_FULL_NAME = "''' + APP_FULL_NAME + '''"
DEFAULT_INSTALL_DIR = r"''' + DEFAULT_INSTALL_DIR + '''"
DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
START_MENU = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\\Windows\\Start Menu\\Programs\\NetOps"
)
DATA_DIRS = ''' + repr(DATA_DIRS) + '''
SFX_MARKER = ''' + repr(SFX_MARKER) + '''


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin():
    if is_admin():
        return True
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    except Exception:
        return False


def create_shortcut(target, shortcut_path, working_dir="", icon_path=""):
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        sc = shell.CreateShortCut(shortcut_path)
        sc.Targetpath = target
        sc.WorkingDirectory = working_dir
        if icon_path:
            sc.IconLocation = icon_path
        sc.save()
        return True
    except ImportError:
        ps = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut(r"{shortcut_path}"); '
            f'$s.TargetPath = r"{target}"; '
            f'$s.WorkingDirectory = r"{working_dir}"; '
        )
        if icon_path:
            ps += f'$s.IconLocation = r"{icon_path}"; '
        ps += '$s.Save()'
        subprocess.run(["powershell", "-Command", ps], capture_output=True)
        return os.path.exists(shortcut_path)


def extract_self():
    """从自身 EXE 尾部提取 zip 数据，返回临时 zip 路径"""
    exe_path = sys.executable
    with open(exe_path, "rb") as f:
        data = f.read()

    # 从尾部查找标记
    marker_pos = data.rfind(SFX_MARKER)
    if marker_pos < 0:
        # 开发模式：查找外部 data.zip
        dev_zip = Path(__file__).parent / "data.zip"
        if dev_zip.exists():
            return str(dev_zip)
        raise RuntimeError("无法找到安装数据")

    # 标记后 8 字节是 zip 数据长度（小端 uint64）
    length_pos = marker_pos + len(SFX_MARKER)
    zip_length = int.from_bytes(data[length_pos:length_pos + 8], "little")
    zip_start = length_pos + 8
    zip_data = data[zip_start:zip_start + zip_length]

    # 写入临时文件
    tmp = Path(tempfile.mkdtemp(prefix="netops_install_")) / "data.zip"
    with open(str(tmp), "wb") as f:
        f.write(zip_data)
    return str(tmp)


def run_gui():
    import tkinter as tk
    from tkinter import messagebox, filedialog

    root = tk.Tk()
    root.title(f"{APP_FULL_NAME} - 安装程序")
    root.geometry("520x420")
    root.resizable(False, False)
    root.configure(bg="#f5f5f5")

    root.update_idletasks()
    x = (root.winfo_screenwidth() - 520) // 2
    y = (root.winfo_screenheight() - 420) // 2
    root.geometry(f"+{x}+{y}")

    bg = "#f5f5f5"

    tk.Label(root, text=APP_FULL_NAME, font=("Microsoft YaHei", 16, "bold"),
             bg=bg, fg="#1a1a1a").pack(pady=(20, 5))
    tk.Label(root, text="企业网络自动化运维平台安装程序", font=("Microsoft YaHei", 10),
             bg=bg, fg="#666").pack()

    # 安装目录
    dir_frame = tk.LabelFrame(root, text="安装目录", font=("Microsoft YaHei", 9),
                              bg=bg, padx=10, pady=8)
    dir_frame.pack(fill="x", padx=20, pady=(15, 5))

    dir_var = tk.StringVar(value=DEFAULT_INSTALL_DIR)
    dir_entry = tk.Entry(dir_frame, textvariable=dir_var, font=("Consolas", 9), width=45)
    dir_entry.pack(side="left", padx=(0, 5))

    def browse():
        d = filedialog.askdirectory(initialdir=DEFAULT_INSTALL_DIR)
        if d:
            dir_var.set(d)

    tk.Button(dir_frame, text="浏览...", command=browse,
              font=("Microsoft YaHei", 9)).pack(side="right")

    # 选项
    opt_frame = tk.LabelFrame(root, text="附加选项", font=("Microsoft YaHei", 9),
                              bg=bg, padx=10, pady=8)
    opt_frame.pack(fill="x", padx=20, pady=5)

    desktop_var = tk.BooleanVar(value=True)
    startmenu_var = tk.BooleanVar(value=True)
    launch_var = tk.BooleanVar(value=True)
    tk.Checkbutton(opt_frame, text="创建桌面快捷方式", variable=desktop_var,
                   font=("Microsoft YaHei", 9), bg=bg).pack(anchor="w")
    tk.Checkbutton(opt_frame, text="创建开始菜单快捷方式", variable=startmenu_var,
                   font=("Microsoft YaHei", 9), bg=bg).pack(anchor="w")
    tk.Checkbutton(opt_frame, text="安装完成后启动", variable=launch_var,
                   font=("Microsoft YaHei", 9), bg=bg).pack(anchor="w")

    tk.Label(root, text="提示：安装到 Program Files 需要管理员权限",
             font=("Microsoft YaHei", 8), bg=bg, fg="#999").pack(pady=(5, 0))

    btn_frame = tk.Frame(root, bg=bg)
    btn_frame.pack(pady=(15, 20))

    def do_install():
        install_dir = dir_var.get().strip()
        if not install_dir:
            messagebox.showwarning("提示", "请选择安装目录")
            return

        install_path = Path(install_dir)
        if install_path.exists() and any(install_path.iterdir()):
            if not messagebox.askyesno("提示",
                f"目录已存在且非空：\\n{install_dir}\\n\\n继续安装将覆盖现有文件，是否继续？"):
                return

        # Program Files 需要管理员权限
        if install_dir.lower().startswith(r"c:\\program files"):
            if not is_admin():
                if messagebox.askyesno("提示",
                    "安装到 Program Files 需要管理员权限。\\n\\n是否以管理员权限重新启动？"):
                    request_admin()
                    return
                else:
                    return

        install_btn.config(state="disabled", text="安装中...")
        root.update()

        try:
            # 解压
            zip_path = extract_self()
            print(f"[INFO] 解压到: {install_path}")
            install_path.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(str(install_path))

            # 创建数据目录
            for d in DATA_DIRS:
                (install_path / d).mkdir(parents=True, exist_ok=True)

            # 创建快捷方式
            exe_path = str(install_path / "NetOps.exe")
            if desktop_var.get():
                sc = os.path.join(DESKTOP, f"{APP_FULL_NAME}.lnk")
                create_shortcut(exe_path, sc, str(install_path), exe_path)
            if startmenu_var.get():
                os.makedirs(START_MENU, exist_ok=True)
                sc = os.path.join(START_MENU, f"{APP_FULL_NAME}.lnk")
                create_shortcut(exe_path, sc, str(install_path), exe_path)

            messagebox.showinfo("安装完成",
                f"安装成功！\\n\\n程序路径：{exe_path}\\n\\n"
                f"{'桌面快捷方式已创建' if desktop_var.get() else ''}")

            if launch_var.get() and os.path.exists(exe_path):
                subprocess.Popen([exe_path])
            root.destroy()
        except Exception as e:
            messagebox.showerror("安装失败", f"错误：{str(e)}")
            install_btn.config(state="normal", text="开始安装")

    tk.Button(btn_frame, text="开始安装", command=do_install,
              font=("Microsoft YaHei", 11, "bold"), width=15, height=1,
              bg="#0078d4", fg="white", relief="flat").pack()
    tk.Button(btn_frame, text="退出", command=root.destroy,
              font=("Microsoft YaHei", 9), width=8).pack(pady=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    run_gui()
'''
    with open(str(script_path), "w", encoding="utf-8") as f:
        f.write(script)


def build_setup_exe() -> None:
    """构建自解压安装包"""
    print("[INFO] 生成引导脚本...")
    bootstrap = TEMP_DIR / "netops_bootstrap.py"
    create_bootstrap_script(bootstrap)

    print("[INFO] 打包数据...")
    data_zip = TEMP_DIR / "data.zip"
    create_data_zip(data_zip)

    if not ICON_FILE.exists():
        print("[ERROR] 图标文件不存在: {}".format(ICON_FILE))
        sys.exit(1)

    print("[INFO] 编译引导程序...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "NetOps_Setup",
        "--icon", str(ICON_FILE),
        "--clean",
        "--noconfirm",
        str(bootstrap),
    ]

    result = subprocess.run(cmd, cwd=str(TEMP_DIR))
    if result.returncode != 0:
        print("[ERROR] PyInstaller 打包失败")
        sys.exit(1)

    # 将 zip 数据附加到 EXE 尾部
    built_exe = TEMP_DIR / "dist" / "NetOps_Setup.exe"
    if not built_exe.exists():
        print("[ERROR] 未找到打包输出")
        sys.exit(1)

    print("[INFO] 附加安装数据...")
    with open(str(built_exe), "rb") as f:
        exe_data = f.read()
    with open(str(data_zip), "rb") as f:
        zip_data = f.read()

    # 构造：EXE + MARKER + zip_length(8字节LE) + zip_data
    marker = SFX_MARKER
    length_bytes = struct.pack("<Q", len(zip_data))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(str(OUTPUT_EXE), "wb") as f:
        f.write(exe_data)
        f.write(marker)
        f.write(length_bytes)
        f.write(zip_data)

    size_mb = OUTPUT_EXE.stat().st_size / (1024 * 1024)
    print("[OK] 安装包已生成: {}".format(OUTPUT_EXE))
    print("     文件大小: {:.1f} MB".format(size_mb))
    print("     包含: {} + data.zip ({:.1f} MB)".format(
        "NetOps_Setup.exe", len(zip_data) / (1024 * 1024)))


if __name__ == "__main__":
    print("=" * 50)
    print("  NetOps Setup 安装包构建工具")
    print("  版本: 0.4.0")
    print("  图标: 华文行楷 \"Net\" + 科技蓝渐变")
    print("=" * 50)

    if not DIST_DIR.exists():
        print("[ERROR] 未找到构建产物: {}".format(DIST_DIR))
        print("  请先执行: pyinstaller NetworkConfigGenerator.spec --noconfirm")
        sys.exit(1)

    build_setup_exe()

    # 清理临时目录
    try:
        shutil.rmtree(str(TEMP_DIR))
    except Exception:
        pass

    print("\\n提示: 双击 {} 即可运行安装程序".format(OUTPUT_EXE))
