#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员制码工具核心模块

职责：
1. 复用 activation_engine.generate_activation_code() 生成激活码
2. 本地台账记录（用户信息 + 机器码 + 激活码 + 时间）
3. 方案B 黑名单管理（添加/移除/查看）

此模块仅由管理员制码工具调用，绝不打包进用户端EXE。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.core.activation_engine import generate_activation_code, BLACKLIST_URL
from src.core.logger import netops_logger
from src.utils.resource_path import get_activation_dir

# ─── 激活文件路径（activation/ 独立目录）───
_ACTIVATION_DIR: str = get_activation_dir()
LICENSE_RECORDS_FILE: str = os.path.join(_ACTIVATION_DIR, "admin_records.json")
BLACKLIST_LOCAL_FILE: str = os.path.join(_ACTIVATION_DIR, "blacklist_local.txt")


def generate_code_for_machine(machine_code: str) -> str:
    """为指定机器码生成激活码。

    Args:
        machine_code: 用户提供的32位机器码

    Returns:
        str: 16位大写激活码
    """
    code = generate_activation_code(machine_code.strip().upper())
    netops_logger.get_logger().info(f"生成激活码: 机器码={machine_code[:8]}... → 激活码={code}")
    return code


def save_record(name: str, machine_code: str, activation_code: str,
                note: str = "") -> bool:
    """保存授权台账记录。

    Args:
        name: 用户姓名/标识
        machine_code: 机器码
        activation_code: 激活码
        note: 备注信息

    Returns:
        bool: 保存是否成功
    """
    try:
        records = load_records()
        record = {
            "name": name,
            "machine_code": machine_code.strip().upper(),
            "activation_code": activation_code,
            "note": note,
            "created_at": datetime.now().isoformat(),
        }
        records.append(record)

        Path(LICENSE_RECORDS_FILE).parent.mkdir(parents=True, exist_ok=True)
        tmp_file = f"{LICENSE_RECORDS_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file, LICENSE_RECORDS_FILE)

        netops_logger.get_logger().info(f"台账记录已保存: {name} / {machine_code[:8]}...")
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"台账保存失败: {e}")
        return False


def load_records() -> List[dict]:
    """加载全部台账记录。

    Returns:
        List[dict]: 记录列表，无记录返回空列表
    """
    try:
        if not os.path.exists(LICENSE_RECORDS_FILE):
            return []
        with open(LICENSE_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def delete_record(index: int) -> bool:
    """删除指定索引的台账记录。

    Args:
        index: 记录索引

    Returns:
        bool: 是否删除成功
    """
    try:
        records = load_records()
        if 0 <= index < len(records):
            records.pop(index)
            tmp_file = f"{LICENSE_RECORDS_FILE}.tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            os.replace(tmp_file, LICENSE_RECORDS_FILE)
            return True
        return False
    except Exception:
        return False


# ─── 方案B：黑名单管理 ───

def add_to_blacklist(machine_code: str) -> bool:
    """将机器码加入黑名单。

    Args:
        machine_code: 要封禁的机器码

    Returns:
        bool: 是否添加成功
    """
    try:
        code = machine_code.strip().upper()
        existing = load_blacklist()
        if code in existing:
            return True  # 已存在
        existing.append(code)

        Path(BLACKLIST_LOCAL_FILE).parent.mkdir(parents=True, exist_ok=True)
        tmp_file = f"{BLACKLIST_LOCAL_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            for mc in existing:
                f.write(mc + "\n")
        os.replace(tmp_file, BLACKLIST_LOCAL_FILE)

        netops_logger.get_logger().info(f"已加入黑名单: {code[:8]}...")
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"加入黑名单失败: {e}")
        return False


def remove_from_blacklist(machine_code: str) -> bool:
    """从黑名单中移除机器码。

    Args:
        machine_code: 要解封的机器码

    Returns:
        bool: 是否移除成功
    """
    try:
        code = machine_code.strip().upper()
        existing = load_blacklist()
        if code not in existing:
            return True
        existing.remove(code)

        Path(BLACKLIST_LOCAL_FILE).parent.mkdir(parents=True, exist_ok=True)
        tmp_file = f"{BLACKLIST_LOCAL_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            for mc in existing:
                f.write(mc + "\n")
        os.replace(tmp_file, BLACKLIST_LOCAL_FILE)

        netops_logger.get_logger().info(f"已从黑名单移除: {code[:8]}...")
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"移除黑名单失败: {e}")
        return False


def load_blacklist() -> List[str]:
    """加载本地黑名单列表。

    Returns:
        List[str]: 机器码列表
    """
    try:
        if not os.path.exists(BLACKLIST_LOCAL_FILE):
            return []
        with open(BLACKLIST_LOCAL_FILE, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except Exception:
        return []


def export_blacklist_for_upload() -> str:
    """导出黑名单内容为上传格式（每行一个机器码）。

    Returns:
        str: 黑名单文本内容
    """
    codes = load_blacklist()
    return "\n".join(codes) + "\n" if codes else ""
