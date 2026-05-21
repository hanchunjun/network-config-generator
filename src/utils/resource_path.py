"""
路径管理工具 — 管理EXE运行时所有文件路径。

⚠️ 核心规则：所有文件路径必须通过本模块获取，禁止硬编码绝对路径。
本模块是项目中被依赖最多的模块（几乎一切模块都依赖它）。

目录结构（ensure_dirs 创建）：
    EXE所在目录/
    ├── config/         系统配置（加密密钥、AI配置、项目索引）
    ├── logs/           运行日志
    ├── single/         单点运维数据（备份/报告/异常）
    └── projects/       项目数据（每个项目独立子目录）
"""

import os
import shutil
import sys
from typing import AnyStr

_app_dir: str = ""


def get_app_dir() -> str:
    """获取EXE所在目录根路径。

    打包后（PyInstaller）：返回 sys.executable 所在目录。
    开发时：返回当前工作目录。
    结果会被缓存，后续调用直接返回缓存值。

    Returns:
        str: EXE所在目录的绝对路径，如 'D:\\工具\\'

    示例:
        >>> get_app_dir()
        'D:\\\\工具\\\\'
    """
    global _app_dir
    if _app_dir:
        return _app_dir
    if getattr(sys, 'frozen', False):
        _app_dir = os.path.dirname(sys.executable)
    else:
        _app_dir = os.path.abspath(".")
    return _app_dir


def get_config_path(filename: str) -> str:
    """获取相对于EXE根目录的文件路径。

    Args:
        filename: 相对路径，如 'config/ai_config.json.enc'

    Returns:
        str: 完整绝对路径

    示例:
        >>> get_config_path('config/ai_config.json.enc')
        'D:\\\\工具\\\\config\\\\ai_config.json.enc'
    """
    return os.path.join(get_app_dir(), filename)


def get_config_dir() -> str:
    """获取系统配置目录路径。

    Returns:
        str: config/ 目录的绝对路径
    """
    return os.path.join(get_app_dir(), "config")


def get_single_dir() -> str:
    """获取单点运维数据目录路径。

    Returns:
        str: single/ 目录的绝对路径
    """
    return os.path.join(get_app_dir(), "single")


def _migrate_old_file(old_path: str, new_path: str, is_dir: bool = False) -> bool:
    """将旧版散迁移到新结构目录。

    仅在旧文件存在且新位置不存在时执行迁移。

    Args:
        old_path: 旧文件/目录路径
        new_path: 新文件/目录路径
        is_dir: 是否为目录

    Returns:
        bool: 迁移是否成功
    """
    if not os.path.exists(old_path):
        return False
    if os.path.exists(new_path):
        return False
    try:
        new_parent = os.path.dirname(new_path) if not is_dir else os.path.dirname(new_path)
        os.makedirs(new_parent, exist_ok=True)
        if is_dir:
            shutil.move(old_path, new_path)
        else:
            shutil.move(old_path, new_path)
        return True
    except Exception:
        return False


def _migrate_old_data(base: str) -> None:
    """将V0.2.1之前的散落文件迁移到三区分离结构。

    迁移列表：
        - ai_config.json.enc → config/
        - projects_config.json → config/
        - ai_recent_files.json → config/
        - single_devices.json.enc → single/
        - config_backup/ → single/
        - output/ → single/

    Args:
        base: EXE所在目录根路径
    """
    config_dir = os.path.join(base, "config")
    single_dir = os.path.join(base, "single")

    file_relocations: list[tuple[str, str, bool]] = [
        ("ai_config.json.enc", os.path.join("config", "ai_config.json.enc"), False),
        ("projects_config.json", os.path.join("config", "projects_config.json"), False),
        ("ai_recent_files.json", os.path.join("config", "ai_recent_files.json"), False),
        ("single_devices.json.enc", os.path.join("single", "single_devices.json.enc"), False),
        ("config_backup", os.path.join("single", "config_backup"), True),
        ("output", os.path.join("single", "output"), True),
    ]

    for old_rel, new_rel, is_dir in file_relocations:
        old_path = os.path.join(base, old_rel)
        new_path = os.path.join(base, new_rel)
        _migrate_old_file(old_path, new_path, is_dir)

    report_src = os.path.join(base, "report")
    report_dst = os.path.join(single_dir, "report")
    if os.path.isdir(report_src) and not os.path.exists(report_dst):
        try:
            os.makedirs(single_dir, exist_ok=True)
            shutil.move(report_src, report_dst)
        except Exception:
            pass

    logs_src = os.path.join(base, "logs")
    logs_dst = os.path.join(base, "logs")
    try:
        os.makedirs(logs_dst, exist_ok=True)
    except Exception:
        pass


def ensure_dirs():
    """创建所有必要目录结构，并执行旧数据迁移。

    由 main.py 在 QApplication 创建之前调用。
    创建顺序：config/ → single/子目录 → projects/ → logs/
    最后执行 _migrate_old_data() 迁移旧版散落文件。
    """
    base = get_app_dir()
    for subdir in ["config"]:
        os.makedirs(os.path.join(base, subdir), exist_ok=True)

    single_root = os.path.join(base, "single")
    for subdir in ["", "config_backup", os.path.join("output", "single_exception"),
                    os.path.join("report", "single_inspect"),
                    os.path.join("report", "compliance"),
                    os.path.join("report", "diagnosis")]:
        os.makedirs(os.path.join(single_root, subdir) if subdir else single_root, exist_ok=True)

    for subdir in ["projects", "logs"]:
        os.makedirs(os.path.join(base, subdir), exist_ok=True)

    _migrate_old_data(base)


def resource_path(relative_path: AnyStr) -> str:
    try:
        base_path: str = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, str(relative_path))