#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员制码工具核心模块

职责：
1. 复用 activation_engine.generate_activation_code() 生成激活码
2. 本地台账记录（用户信息 + 机器码 + 激活码 + 时间）—— AES-GCM 加密存储
3. 方案B 黑名单管理（添加/移除/查看）
4. 台账导出/导入备份

文件结构（admin_data/ 独立目录，与用户端 activation/ 完全隔离）：
    admin_data/
    ├── records.dat       ← 授权台账（AES-GCM加密）
    ├── blacklist.txt     ← 本地黑名单
    └── backup/           ← 台账备份目录
        └── records_YYYYMMDD_HHMMSS.dat

此模块仅由管理员制码工具调用，绝不打包进用户端EXE。
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.core.activation_engine import generate_activation_code, BLACKLIST_URL
from src.core.logger import netops_logger
from src.utils.resource_path import get_admin_data_dir

# ─── 管理员数据目录（与用户端 activation/ 完全隔离）───
_ADMIN_DIR: str = get_admin_data_dir()
LICENSE_RECORDS_FILE: str = os.path.join(_ADMIN_DIR, "records.dat")
BLACKLIST_LOCAL_FILE: str = os.path.join(_ADMIN_DIR, "blacklist.txt")
BACKUP_DIR: str = os.path.join(_ADMIN_DIR, "backup")

# ─── 台账加密密钥（管理员工具专用，AES-256）───
# 密钥派生：固定盐 + 管理员目录路径 → SHA-256 → 32字节密钥
_ADMIN_KEY_SALT: str = "NetOps::AdminData::Salt::2026"


def _derive_admin_key() -> bytes:
    """派生管理员数据加密密钥。

    基于管理员目录路径 + 固定盐，确保每台管理员电脑的密钥不同。

    Returns:
        bytes: 32字节AES密钥
    """
    material = (_ADMIN_DIR + _ADMIN_KEY_SALT).encode("utf-8")
    return hashlib.sha256(material).digest()


def _encrypt_data(plaintext: str) -> bytes:
    """AES-GCM 加密字符串数据。

    Args:
        plaintext: 明文字符串

    Returns:
        bytes: nonce(12) + ciphertext + tag(16)
    """
    key = _derive_admin_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext


def _decrypt_data(data: bytes) -> str:
    """AES-GCM 解密数据。

    Args:
        data: nonce(12) + ciphertext + tag(16)

    Returns:
        str: 解密后的明文字符串
    """
    key = _derive_admin_key()
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")


def _ensure_admin_dirs():
    """确保管理员数据目录存在。"""
    Path(_ADMIN_DIR).mkdir(parents=True, exist_ok=True)
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 激活码生成
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# 台账管理（加密存储）
# ═══════════════════════════════════════════════════════════════

def save_record(name: str, machine_code: str, activation_code: str,
                note: str = "") -> bool:
    """保存授权台账记录（追加模式，加密存储）。

    Args:
        name: 用户姓名/标识
        machine_code: 机器码
        activation_code: 激活码
        note: 备注信息

    Returns:
        bool: 保存是否成功
    """
    try:
        _ensure_admin_dirs()
        records = load_records()
        record = {
            "name": name,
            "machine_code": machine_code.strip().upper(),
            "activation_code": activation_code,
            "note": note,
            "created_at": datetime.now().isoformat(),
        }
        records.append(record)

        plaintext = json.dumps(records, ensure_ascii=False, indent=2)
        encrypted = _encrypt_data(plaintext)

        tmp_file = f"{LICENSE_RECORDS_FILE}.tmp"
        with open(tmp_file, "wb") as f:
            f.write(encrypted)
        os.replace(tmp_file, LICENSE_RECORDS_FILE)

        netops_logger.get_logger().info(f"台账记录已保存: {name} / {machine_code[:8]}...")
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"台账保存失败: {e}")
        return False


def load_records() -> List[dict]:
    """加载全部台账记录（自动解密）。

    Returns:
        List[dict]: 记录列表，无记录或解密失败返回空列表
    """
    try:
        if not os.path.exists(LICENSE_RECORDS_FILE):
            return []
        with open(LICENSE_RECORDS_FILE, "rb") as f:
            encrypted = f.read()
        plaintext = _decrypt_data(encrypted)
        return json.loads(plaintext)
    except Exception as e:
        netops_logger.get_logger().error(f"台账读取失败: {e}")
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
            plaintext = json.dumps(records, ensure_ascii=False, indent=2)
            encrypted = _encrypt_data(plaintext)
            tmp_file = f"{LICENSE_RECORDS_FILE}.tmp"
            with open(tmp_file, "wb") as f:
                f.write(encrypted)
            os.replace(tmp_file, LICENSE_RECORDS_FILE)
            return True
        return False
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# 台账备份与恢复
# ═══════════════════════════════════════════════════════════════

def backup_records() -> Tuple[bool, str]:
    """创建台账备份（带时间戳，加密副本）。

    Returns:
        Tuple[bool, str]: (是否成功, 备份文件路径或错误信息)
    """
    try:
        _ensure_admin_dirs()
        if not os.path.exists(LICENSE_RECORDS_FILE):
            return False, "台账文件为空，无需备份"

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"records_{ts}.dat"
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        shutil.copy2(LICENSE_RECORDS_FILE, backup_path)
        netops_logger.get_logger().info(f"台账已备份: {backup_path}")
        return True, backup_path
    except Exception as e:
        return False, str(e)


def list_backups() -> List[str]:
    """列出所有备份文件（按时间倒序）。

    Returns:
        List[str]: 备份文件名列表
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            return []
        files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".dat")]
        files.sort(reverse=True)
        return files
    except Exception:
        return []


def restore_backup(backup_filename: str) -> Tuple[bool, str]:
    """从备份文件恢复台账。

    恢复前自动创建当前台账的临时备份，防止误操作。

    Args:
        backup_filename: 备份文件名（不含路径）

    Returns:
        Tuple[bool, str]: (是否成功, 提示信息)
    """
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return False, f"备份文件不存在: {backup_filename}"

        # 如果当前台账存在，先创建临时备份
        if os.path.exists(LICENSE_RECORDS_FILE):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = os.path.join(BACKUP_DIR, f"auto_before_restore_{ts}.dat")
            shutil.copy2(LICENSE_RECORDS_FILE, safety_backup)

        shutil.copy2(backup_path, LICENSE_RECORDS_FILE)
        records = load_records()
        return True, f"已恢复 {len(records)} 条记录（操作前已自动备份）"
    except Exception as e:
        return False, str(e)


def export_records_to_json(export_path: str) -> Tuple[bool, str]:
    """导出台账为明文JSON（用于管理员自行存档）。

    Args:
        export_path: 导出文件完整路径

    Returns:
        Tuple[bool, str]: (是否成功, 提示信息)
    """
    try:
        records = load_records()
        if not records:
            return False, "台账为空"
        tmp_file = f"{export_path}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file, export_path)
        return True, f"已导出 {len(records)} 条记录到 {export_path}"
    except Exception as e:
        return False, str(e)


def import_records_from_json(import_path: str, merge: bool = True) -> Tuple[bool, str]:
    """从明文JSON文件导入台账。

    Args:
        import_path: 导入文件完整路径
        merge: True=合并到现有台账，False=覆盖

    Returns:
        Tuple[bool, str]: (是否成功, 提示信息)
    """
    try:
        if not os.path.exists(import_path):
            return False, f"文件不存在: {import_path}"
        with open(import_path, "r", encoding="utf-8") as f:
            imported = json.load(f)
        if not isinstance(imported, list):
            return False, "文件格式不正确"

        if merge:
            existing = load_records()
            existing_codes = {r.get("machine_code") for r in existing}
            new_count = 0
            for rec in imported:
                if rec.get("machine_code", "").upper() not in existing_codes:
                    existing.append(rec)
                    new_count += 1
            records = existing
            msg = f"导入完成：新增 {new_count} 条，共 {len(records)} 条"
        else:
            records = imported
            msg = f"覆盖导入完成：共 {len(records)} 条"

        _ensure_admin_dirs()
        plaintext = json.dumps(records, ensure_ascii=False, indent=2)
        encrypted = _encrypt_data(plaintext)
        tmp_file = f"{LICENSE_RECORDS_FILE}.tmp"
        with open(tmp_file, "wb") as f:
            f.write(encrypted)
        os.replace(tmp_file, LICENSE_RECORDS_FILE)
        return True, msg
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════
# 方案B：黑名单管理
# ═══════════════════════════════════════════════════════════════

def add_to_blacklist(machine_code: str) -> bool:
    """将机器码加入黑名单。

    Args:
        machine_code: 要封禁的机器码

    Returns:
        bool: 是否添加成功
    """
    try:
        _ensure_admin_dirs()
        code = machine_code.strip().upper()
        existing = load_blacklist()
        if code in existing:
            return True  # 已存在
        existing.append(code)

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
        _ensure_admin_dirs()
        code = machine_code.strip().upper()
        existing = load_blacklist()
        if code not in existing:
            return True
        existing.remove(code)

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
