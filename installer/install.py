#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps 安装程序
双击运行即可安装，无需额外依赖（Python 内置 tkinter）
"""

import os
import sys
import shutil
import ctypes
import subprocess
from pathlib import Path

# ─── 配置 ───
APP_NAME = "NetOps"
APP_FULL_NAME = "NetOps 企业网络自动化运维平台"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), APP_NAME)
DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
START_MENU = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\Windows\Start Menu\Programs\NetOps"
)

# 源目录（installer/ 的上级目录，即项目根目录）
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DIST_DIR = PROJECT_DIR / "dist" / "NetOps"

# 需要打包的额外目录
EXTRA_DIRS = ["agents", "scripts"]
EXTRA_FILES = {
    "scripts": ["backup_all_config.py", "network_inspect.py", "run_trouble_cmd.py", "__init__.py"],
}

# 运行时数据目录（安装时预建，卸载时保留）
DATA_DIRS = ["config", "logs", "projects", "single", "activation"]


def is_admin():
    """检查是否以管理员权限运行。"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """请求以管理员权限重新运行。"""
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
    """创建 Windows 快捷方式。"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = working_dir
        if icon_path:
            shortcut.IconLocation = icon_path
        shortcut.save()
        return True
    except ImportError:
        # 无 pywin32，用 PowerShell 降级方案
        ps_cmd = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "{target}"; '
            f'$s.WorkingDirectory = "{working_dir}"; '
        )
        if icon_path:
            ps_cmd += f'$s.IconLocation = "{icon_path}"; '
        ps_cmd += '$s.Save()'
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        return os.path.exists(shortcut_path)


def install(install_dir, create_desktop=True, create_start_menu=True):
    """执行安装。

    Args:
        install_dir: 安装目标目录
        create_desktop: 是否创建桌面快捷方式
        create_start_menu: 是否创建开始菜单快捷方式
    """
    install_path = Path(install_dir)

    # 1. 检查源目录
    if not DIST_DIR.exists():
        print(f"错误：未找到构建产物 {DIST_DIR}")
        print("请先执行：pyinstaller NetworkConfigGenerator.spec --noconfirm")
        return False

    # 2. 创建安装目录
    print(f"安装目录：{install_path}")
    install_path.mkdir(parents=True, exist_ok=True)

    # 3. 复制主程序（dist/NetOps/*）
    print("复制主程序文件...")
    for item in DIST_DIR.iterdir():
        dest = install_path / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # 4. 复制额外目录
    for dirname in EXTRA_DIRS:
        src_dir = PROJECT_DIR / dirname
        dst_dir = install_path / dirname
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            if dirname in EXTRA_FILES:
                # 只复制指定文件
                dst_dir.mkdir(parents=True, exist_ok=True)
                for fname in EXTRA_FILES[dirname]:
                    src_file = src_dir / fname
                    if src_file.exists():
                        shutil.copy2(src_file, dst_dir / fname)
            else:
                shutil.copytree(src_dir, dst_dir)

    # 5. 创建运行时数据目录
    print("创建数据目录...")
    for dirname in DATA_DIRS:
        (install_path / dirname).mkdir(parents=True, exist_ok=True)

    # 6. 创建快捷方式
    exe_path = str(install_path / "NetOps.exe")
    if create_desktop:
        desktop_shortcut = os.path.join(DESKTOP, f"{APP_FULL_NAME}.lnk")
        print(f"创建桌面快捷方式...")
        create_shortcut(exe_path, desktop_shortcut, str(install_path), exe_path)

    if create_start_menu:
        os.makedirs(START_MENU, exist_ok=True)
        menu_shortcut = os.path.join(START_MENU, f"{APP_FULL_NAME}.lnk")
        print(f"创建开始菜单快捷方式...")
        create_shortcut(exe_path, menu_shortcut, str(install_path), exe_path)

        # 卸载快捷方式
        uninstall_script = str(install_path / "uninstall.bat")
        _create_uninstall_script(uninstall_script, str(install_path))
        uninstall_shortcut = os.path.join(START_MENU, "卸载 NetOps.lnk")
        create_shortcut(uninstall_script, uninstall_shortcut, str(install_path))

    print("\n安装完成！")
    print(f"  程序路径：{exe_path}")
    if create_desktop:
        print(f"  桌面快捷方式：{os.path.join(DESKTOP, f'{APP_FULL_NAME}.lnk')}")
    return True


def _create_uninstall_script(script_path, install_dir):
    """生成卸载脚本。"""
    content = f"""@echo off
chcp 65001 >nul
echo.
echo ====================================
echo   {APP_FULL_NAME} - 卸载程序
echo ====================================
echo.
echo 卸载将删除程序文件，但保留用户数据（config/projects/single/activation）。
echo.
set /p confirm=确认卸载？(Y/N):
if /i not "%confirm%"=="Y" (
    echo 已取消卸载。
    pause
    exit /b 0
)

echo.
echo 正在删除快捷方式...
del /f /q "{os.path.join(DESKTOP, f'{APP_FULL_NAME}.lnk')}" 2>nul
rmdir /s /q "{START_MENU}" 2>nul

echo 正在删除程序文件...
:: 删除程序文件和目录（保留数据目录）
for /d %%d in ("{install_dir}\\_internal") do rmdir /s /q "%%d" 2>nul
del /f /q "{install_dir}\\NetOps.exe" 2>nul
del /f /q "{install_dir}\\uninstall.bat" 2>nul
:: 删除脚本和代理目录
rmdir /s /q "{install_dir}\\scripts" 2>nul
rmdir /s /q "{install_dir}\\agents" 2>nul

echo.
echo 卸载完成！用户数据目录已保留：
echo   {install_dir}\\config
echo   {install_dir}\\projects
echo   {install_dir}\\single
echo   {install_dir}\\activation
echo.
echo 如需彻底删除，请手动删除 {install_dir}
echo.
pause
"""
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)


# ─── GUI 安装界面 ───

def run_gui():
    """图形化安装界面。"""
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title(f"{APP_FULL_NAME} - 安装程序")
    root.geometry("520x380")
    root.resizable(False, False)

    # 居中显示
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 520) // 2
    y = (root.winfo_screenheight() - 380) // 2
    root.geometry(f"+{x}+{y}")

    bg = "#f5f5f5"
    root.configure(bg=bg)

    # 标题
    tk.Label(root, text=APP_FULL_NAME, font=("微软雅黑", 16, "bold"),
             bg=bg, fg="#1a1a1a").pack(pady=(20, 5))
    tk.Label(root, text="企业网络自动化运维平台安装程序", font=("微软雅黑", 10),
             bg=bg, fg="#666").pack()

    # 安装目录
    dir_frame = tk.LabelFrame(root, text="安装目录", font=("微软雅黑", 9),
                              bg=bg, padx=10, pady=8)
    dir_frame.pack(fill="x", padx=20, pady=(15, 5))

    dir_var = tk.StringVar(value=DEFAULT_INSTALL_DIR)
    dir_entry = tk.Entry(dir_frame, textvariable=dir_var, font=("Consolas", 9), width=45)
    dir_entry.pack(side="left", padx=(0, 5))

    def browse_dir():
        from tkinter import filedialog
        d = filedialog.askdirectory(initialdir=DEFAULT_INSTALL_DIR)
        if d:
            dir_var.set(d)

    tk.Button(dir_frame, text="浏览...", command=browse_dir,
              font=("微软雅黑", 9)).pack(side="right")

    # 选项
    opt_frame = tk.LabelFrame(root, text="附加选项", font=("微软雅黑", 9),
                              bg=bg, padx=10, pady=8)
    opt_frame.pack(fill="x", padx=20, pady=5)

    desktop_var = tk.BooleanVar(value=True)
    startmenu_var = tk.BooleanVar(value=True)
    tk.Checkbutton(opt_frame, text="创建桌面快捷方式", variable=desktop_var,
                   font=("微软雅黑", 9), bg=bg).pack(anchor="w")
    tk.Checkbutton(opt_frame, text="创建开始菜单快捷方式", variable=startmenu_var,
                   font=("微软雅黑", 9), bg=bg).pack(anchor="w")

    # 提示
    tk.Label(root, text="提示：安装需要管理员权限写入 Program Files 目录",
             font=("微软雅黑", 8), bg=bg, fg="#999").pack(pady=(5, 0))

    # 按钮
    btn_frame = tk.Frame(root, bg=bg)
    btn_frame.pack(pady=(15, 20))

    def on_install():
        install_dir = dir_var.get().strip()
        if not install_dir:
            messagebox.showwarning("提示", "请选择安装目录")
            return

        if os.path.exists(install_dir) and os.listdir(install_dir):
            if not messagebox.askyesno("提示", f"目录已存在且非空：\n{install_dir}\n\n继续安装将覆盖现有文件，是否继续？"):
                return

        # 禁用按钮
        install_btn.config(state="disabled", text="安装中...")
        root.update()

        try:
            success = install(install_dir, desktop_var.get(), startmenu_var.get())
            if success:
                messagebox.showinfo("安装完成",
                    f"安装成功！\n\n"
                    f"程序路径：{install_dir}\\NetOps.exe\n"
                    f"{'桌面快捷方式已创建' if desktop_var.get() else ''}\n\n"
                    f"是否立即启动？")
                # 启动程序
                exe = os.path.join(install_dir, "NetOps.exe")
                if os.path.exists(exe):
                    subprocess.Popen([exe])
                root.destroy()
            else:
                messagebox.showerror("安装失败", "安装过程中出现错误，请检查日志。")
                install_btn.config(state="normal", text="开始安装")
        except Exception as e:
            messagebox.showerror("安装失败", f"错误：{str(e)}")
            install_btn.config(state="normal", text="开始安装")

    install_btn = tk.Button(btn_frame, text="开始安装", command=on_install,
                           font=("微软雅黑", 11, "bold"), width=15, height=1,
                           bg="#0078d4", fg="white", relief="flat")
    install_btn.pack()

    tk.Button(btn_frame, text="退出", command=root.destroy,
              font=("微软雅黑", 9), width=8).pack(pady=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    run_gui()
