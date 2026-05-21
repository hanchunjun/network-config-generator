#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员制码工具独立打包脚本

用法：
    python scripts/build_admin_tool.py

输出：
    dist/AdminKeyGenTool.exe
"""

import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    """打包管理员制码工具"""
    os.chdir(PROJECT_ROOT)
    spec_file = os.path.join(PROJECT_ROOT, "admin_tool.spec")

    if not os.path.exists(spec_file):
        print(f"错误：找不到 spec 文件: {spec_file}")
        sys.exit(1)

    print("=" * 60)
    print("开始打包管理员制码工具...")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        spec_file,
        "--noconfirm",
        "--clean",
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        exe_path = os.path.join(PROJECT_ROOT, "dist", "AdminKeyGenTool.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ 打包成功！")
            print(f"   输出: {exe_path}")
            print(f"   大小: {size_mb:.1f} MB")
        else:
            print("\n⚠️ 打包完成但未找到 EXE 文件")
    else:
        print(f"\n❌ 打包失败，退出码: {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
