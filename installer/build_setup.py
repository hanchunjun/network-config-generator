#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
installer/build_setup.py
从 dist/NetOps/ 生成带图标的自解压安装包 NetOps_Setup_0.4.3.exe

原理：
  1. 将 dist/NetOps/ 打包为 data.zip
  2. 用 PyInstaller --onefile 打包引导脚本，通过 --add-data 嵌入 data.zip
  3. 引导脚本运行时从 PyInstaller 临时解压目录读取 data.zip 并解压安装
  4. 使用 assets/netops.ico 作为安装包图标

用法：
  1. 先执行 pyinstaller NetworkConfigGenerator.spec --noconfirm
  2. 再执行 python installer/build_setup.py
  3. 输出：installer/NetOps_Setup_0.4.3.exe
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "NetOps"
ASSETS_DIR = PROJECT_ROOT / "assets"
ICON_FILE = ASSETS_DIR / "netops.ico"
OUTPUT_DIR = PROJECT_ROOT / "installer"
OUTPUT_EXE = OUTPUT_DIR / "NetOps_Setup_0.4.3.exe"
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
    """生成自解压引导脚本（PyInstaller --onefile 打包，data.zip 通过 --add-data 嵌入）"""
    script = r'''#!/usr/bin/env python3
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

APP_NAME = "''' + APP_NAME + r'''"
APP_FULL_NAME = "''' + APP_FULL_NAME + r'''"
DEFAULT_INSTALL_DIR = r"''' + DEFAULT_INSTALL_DIR + r'''"
DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
START_MENU = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\Windows\Start Menu\Programs\NetOps"
)
DATA_DIRS = ''' + repr(DATA_DIRS) + r'''


def get_data_zip_path():
    """获取嵌入的 data.zip 路径（兼容 PyInstaller --onefile 临时目录和开发模式）"""
    # PyInstaller --onefile 解压到 sys._MEIPASS
    if hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / "data.zip"
        if p.exists():
            return str(p)
    # 开发模式：查找脚本同目录
    p = Path(__file__).parent / "data.zip"
    if p.exists():
        return str(p)
    raise RuntimeError("无法找到安装数据 (data.zip)")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin_restart(install_dir):
    """以管理员权限重新启动自身"""
    try:
        args = [sys.executable, "--install", install_dir]
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(args), None, 1
        )
        return True
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


def _register_uninstall(install_dir):
    """写入注册表卸载信息，使程序出现在控制面板「程序和功能」中"""
    try:
        import winreg
    except ImportError:
        return  # 非 Windows 跳过
    exe_path = os.path.join(install_dir, "NetOps.exe")
    # 卸载命令：UninstallString 带弹窗确认，QuietUninstallString 静默执行
    uninstall_cmd = '"{}" --uninstall "{}"'.format(exe_path, install_dir)
    silent_uninstall_cmd = '"{}" --uninstall-silent "{}"'.format(exe_path, install_dir)
    # 优先写入 HKLM（所有用户可见），权限不足时回退 HKCU
    for hkey, key_path in [
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NetOps"),
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NetOps"),
    ]:
        try:
            key = winreg.CreateKeyEx(hkey, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ,
                              APP_FULL_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "0.4.3")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "NetOps")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
            winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ,
                              silent_uninstall_cmd)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, exe_path)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            print("[OK] 卸载注册: {}".format(key_path))
            return
        except PermissionError:
            continue
        except Exception as e:
            print("[WARN] 卸载注册失败: {}".format(e))
            continue
    print("[WARN] 无法写入卸载注册表（可能需要管理员权限）")


def perform_uninstall(install_dir):
    """执行卸载：删除程序文件，保留用户数据"""
    install_path = Path(install_dir)
    if not install_path.exists():
        print("[WARN] 安装目录不存在: {}".format(install_dir))
        return

    # ── 第1步：清理快捷方式（先于文件删除，避免依赖程序文件）──
    desktop_sc = os.path.join(DESKTOP, "{}.lnk".format(APP_FULL_NAME))
    if os.path.exists(desktop_sc):
        try:
            os.remove(desktop_sc)
        except Exception:
            pass
    startmenu_sc = os.path.join(START_MENU, "{}.lnk".format(APP_FULL_NAME))
    if os.path.exists(startmenu_sc):
        try:
            os.remove(startmenu_sc)
        except Exception:
            pass
    # 清理开始菜单卸载快捷方式
    unins_sc = os.path.join(START_MENU, "卸载 NetOps.lnk")
    if os.path.exists(unins_sc):
        try:
            os.remove(unins_sc)
        except Exception:
            pass
    # 清理开始菜单目录
    if os.path.exists(START_MENU) and not os.listdir(START_MENU):
        try:
            os.rmdir(START_MENU)
        except Exception:
            pass

    # ── 第2步：清理注册表 ──
    try:
        import winreg
        for hkey, key_path in [
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NetOps"),
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NetOps"),
        ]:
            try:
                winreg.DeleteKey(hkey, key_path)
                print("[OK] 注册表清理: {}".format(key_path))
            except FileNotFoundError:
                pass
            except Exception as e:
                print("[WARN] 注册表清理失败: {}".format(e))
    except ImportError:
        pass

    # ── 第3步：删除程序文件（保留数据目录）──
    exe_path = str(install_path / "NetOps.exe")
    for item in install_path.iterdir():
        name = item.name
        if name in DATA_DIRS:
            continue  # 保留用户数据
        if str(item) == exe_path:
            continue  # 自身最后删除
        try:
            if item.is_dir():
                shutil.rmtree(str(item))
            else:
                item.unlink()
        except Exception as e:
            print("[WARN] 删除失败: {} ({})".format(name, e))

    # ── 第4步：删除自身（NetOps.exe），使用 MoveFileEx 延迟删除 ──
    try:
        import ctypes
        # MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
        kernel32 = ctypes.windll.kernel32
        result = kernel32.MoveFileExW(
            exe_path, None, 0x4
        )
        if result:
            print("[OK] 自身删除已延迟到重启后")
        else:
            # 回退：直接删除
            os.remove(exe_path)
    except Exception:
        try:
            os.remove(exe_path)
        except Exception as e:
            print("[WARN] 自身删除失败: {}".format(e))

    # ── 第5步：如果目录仅剩数据目录，保留；否则尝试删除空目录 ──
    remaining = list(install_path.iterdir())
    non_data = [x for x in remaining if x.name not in DATA_DIRS]
    if not non_data:
        print("[OK] 用户数据已保留: {}".format(install_dir))
    else:
        # 还有非数据文件（删除失败的），保留目录
        pass

    print("[OK] 卸载完成")


def perform_install(install_dir, create_desktop, create_startmenu, launch_after):
    """执行实际安装（可被 GUI 或命令行调用）"""
    install_path = Path(install_dir)
    zip_path = get_data_zip_path()

    print("[INFO] 解压到: {}".format(install_path))
    install_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(str(install_path))

    # 创建数据目录
    for d in DATA_DIRS:
        (install_path / d).mkdir(parents=True, exist_ok=True)

    # 创建快捷方式
    exe_path = str(install_path / "NetOps.exe")
    if create_desktop:
        sc = os.path.join(DESKTOP, "{}.lnk".format(APP_FULL_NAME))
        create_shortcut(exe_path, sc, str(install_path), exe_path)
    if create_startmenu:
        os.makedirs(START_MENU, exist_ok=True)
        sc = os.path.join(START_MENU, "{}.lnk".format(APP_FULL_NAME))
        create_shortcut(exe_path, sc, str(install_path), exe_path)
        # 创建开始菜单卸载快捷方式
        unins_sc = os.path.join(START_MENU, "卸载 NetOps.lnk")
        unins_target = os.path.join(install_dir, "NetOps.exe")
        create_shortcut(
            unins_target, unins_sc, install_dir,
            unins_target,  # 图标用主程序图标
        )
        # 写入卸载快捷方式的参数（通过 PowerShell 设置 Arguments）
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            sc_obj = shell.CreateShortCut(unins_sc)
            sc_obj.Arguments = '--uninstall "{}"'.format(install_dir)
            sc_obj.save()
        except Exception:
            pass  # win32com 不可用时静默跳过

    # 注册卸载信息到注册表（控制面板「程序和功能」）
    _register_uninstall(install_dir)

    print("[OK] 安装完成: {}".format(exe_path))

    if launch_after and os.path.exists(exe_path):
        subprocess.Popen([exe_path])


def run_gui():
    import tkinter as tk
    from tkinter import messagebox, filedialog

    root = tk.Tk()
    root.title("{} - 安装程序".format(APP_FULL_NAME))
    root.geometry("520x440")
    root.resizable(False, False)
    root.configure(bg="#f5f5f5")

    root.update_idletasks()
    x = (root.winfo_screenwidth() - 520) // 2
    y = (root.winfo_screenheight() // 2) - 220
    root.geometry("+{}+{}".format(x, y))

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

    startmenu_var = tk.BooleanVar(value=True)
    launch_var = tk.BooleanVar(value=False)
    tk.Label(opt_frame, text="✓ 安装完成后自动创建桌面快捷方式",
             font=("Microsoft YaHei", 9), bg=bg, fg="#333").pack(anchor="w")
    tk.Checkbutton(opt_frame, text="创建开始菜单快捷方式", variable=startmenu_var,
                   font=("Microsoft YaHei", 9), bg=bg).pack(anchor="w")
    tk.Checkbutton(opt_frame, text="安装完成后启动程序", variable=launch_var,
                   font=("Microsoft YaHei", 9), bg=bg).pack(anchor="w")

    tk.Label(root, text="提示：安装到 Program Files 需要管理员权限",
             font=("Microsoft YaHei", 8), bg=bg, fg="#999").pack(pady=(5, 0))

    # 状态标签
    status_var = tk.StringVar(value="就绪，点击「开始安装」")
    status_label = tk.Label(root, textvariable=status_var,
                            font=("Microsoft YaHei", 9), bg=bg, fg="#666")
    status_label.pack(pady=(8, 0))

    btn_frame = tk.Frame(root, bg=bg)
    btn_frame.pack(pady=(10, 20))

    install_btn = tk.Button(btn_frame, text="开始安装",
                             font=("Microsoft YaHei", 11, "bold"),
                             width=15, height=1, bg="#0078d4", fg="white", relief="flat")
    install_btn.pack()

    tk.Button(btn_frame, text="退出", command=root.destroy,
              font=("Microsoft YaHei", 9), width=8).pack(pady=(8, 0))

    def do_install():
        install_dir = dir_var.get().strip()
        if not install_dir:
            messagebox.showwarning("提示", "请选择安装目录")
            return

        install_path = Path(install_dir)
        if install_path.exists() and any(install_path.iterdir()):
            if not messagebox.askyesno("提示",
                "目录已存在且非空：\n{}\n\n继续安装将覆盖现有文件，是否继续？".format(install_dir)):
                return

        # Program Files 需要管理员权限
        if install_dir.lower().startswith(r"c:\program files"):
            if not is_admin():
                if messagebox.askyesno("提示",
                    "安装到 Program Files 需要管理员权限。\n\n是否以管理员权限重新启动？"):
                    request_admin_restart(install_dir)
                    root.destroy()
                    return
                else:
                    return

        install_btn.config(state="disabled")
        status_var.set("正在安装，请稍候...")
        root.update()

        try:
            perform_install(
                install_dir,
                True,
                startmenu_var.get(),
                launch_var.get()
            )
            status_var.set("✓ 安装完成！")
            root.after(800, root.destroy)
        except Exception as e:
            messagebox.showerror("安装失败", "错误：{}".format(str(e)))
            install_btn.config(state="normal")
            status_var.set("安装失败，请重试")

    install_btn.config(command=do_install)
    root.mainloop()


def run_cli(install_dir):
    """命令行模式安装"""
    perform_install(install_dir, True, True, False)
    print("[OK] 安装完成: {}".format(install_dir))


if __name__ == "__main__":
    # 命令行参数处理
    #   安装:   NetOps.exe --install "D:\NetOps"
    #   卸载:   NetOps.exe --uninstall "D:\NetOps"
    #   静默卸载: NetOps.exe --uninstall-silent "D:\NetOps"
    if len(sys.argv) >= 3 and sys.argv[1] == "--install":
        run_cli(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "--uninstall-silent":
        # 静默卸载（由控制面板调用，不弹窗）
        perform_uninstall(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "--uninstall":
        # 交互式卸载（开始菜单/手动运行，弹窗确认）
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            if messagebox.askyesno("确认卸载",
                "确定要卸载 {} 吗？\n\n安装目录：{}\n\n（用户数据 config/logs/projects 等将被保留）".format(
                    APP_FULL_NAME, sys.argv[2])):
                perform_uninstall(sys.argv[2])
                messagebox.showinfo("卸载完成", "已成功卸载 {}".format(APP_FULL_NAME))
            root.destroy()
        except Exception:
            # tkinter 不可用时回退到静默卸载
            perform_uninstall(sys.argv[2])
    else:
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

    print("[INFO] 编译安装包...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "NetOps_Setup",
        "--icon", str(ICON_FILE),
        "--add-data", "{};.".format(str(data_zip).replace("\\", "/")),
        "--clean",
        "--noconfirm",
        str(bootstrap),
    ]

    result = subprocess.run(cmd, cwd=str(TEMP_DIR))
    if result.returncode != 0:
        print("[ERROR] PyInstaller 打包失败")
        sys.exit(1)

    # 复制输出
    built_exe = TEMP_DIR / "dist" / "NetOps_Setup.exe"
    if not built_exe.exists():
        print("[ERROR] 未找到打包输出: {}".format(built_exe))
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(built_exe), str(OUTPUT_EXE))

    size_mb = OUTPUT_EXE.stat().st_size / (1024 * 1024)
    print("[OK] 安装包已生成: {}".format(OUTPUT_EXE))
    print("     文件大小: {:.1f} MB".format(size_mb))


if __name__ == "__main__":
    print("=" * 50)
    print("  NetOps Setup 安装包构建工具")
    print("  版本: 0.4.3")
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

    print("\n提示: 双击 {} 即可运行安装程序".format(OUTPUT_EXE))
