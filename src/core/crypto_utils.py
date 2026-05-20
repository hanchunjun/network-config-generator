#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密工具模块
提供密码的加密、解密和密钥管理功能
"""

import os
import sys
import base64
import socket
import subprocess
import threading
from typing import Optional
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature

from src.core.logger import netops_logger
from src.core.key_manager import encrypted_manager

# 兼容性常量
LEGACY_SALT: bytes = b"NetworkConfigGenerator::AES::Salt::2024"
ENC_PREFIX: str = "ENC:"
NONCE_LENGTH: int = 12

# 缓存密钥以提高性能
_cached_key: Optional[bytes] = None
_key_lock = threading.Lock()


def encrypt_password(plaintext: str) -> str:
    """
    加密密码

    Args:
        plaintext: 明文密码

    Returns:
        加密后的密码字符串
    """
    if not plaintext:
        return plaintext

    try:
        encrypted = encrypted_manager.encrypt(plaintext)
        logger = netops_logger.get_logger()
        logger.debug(f"密码加密成功，长度: {len(plaintext)} -> {len(encrypted)}")
        return encrypted
    except Exception as e:
        logger = netops_logger.get_logger()
        logger.error(f"密码加密失败: {e}")
        # 加密失败时返回原密码（避免数据丢失）
        return plaintext


def decrypt_password(stored: str) -> str:
    """
    解密密码

    Args:
        stored: 存储的密码（可能已加密）

    Returns:
        解密后的明文密码
    """
    if not stored:
        return stored

    try:
        # 检查是否已加密
        if not is_encrypted(stored):
            return stored

        decrypted = encrypted_manager.decrypt(stored)
        logger = netops_logger.get_logger()
        logger.debug(f"密码解密成功，长度: {len(stored)} -> {len(decrypted)}")
        return decrypted
    except Exception as e:
        logger = netops_logger.get_logger()
        logger.error(f"密码解密失败: {e}")
        # 解密失败时返回原值（避免数据丢失）
        return stored


def is_encrypted(stored: str) -> bool:
    """
    检查密码是否已加密

    Args:
        stored: 存储的密码

    Returns:
        是否已加密
    """
    if not stored:
        return False
    return encrypted_manager.is_encrypted(stored)


def migrate_old_passwords(passwords: list) -> list:
    """
    迁移旧格式的加密密码

    Args:
        passwords: 密码列表

    Returns:
        迁移后的密码列表
    """
    migrated = []
    migrated_count = 0

    for pwd in passwords:
        if pwd and pwd.startswith("ENC:") and ":" not in pwd[4:]:
            # 检测到旧格式
            new_pwd = encrypted_manager.migrate_old_data(pwd)
            if new_pwd != pwd:
                migrated_count += 1
            migrated.append(new_pwd)
        else:
            migrated.append(pwd)

    if migrated_count > 0:
        logger = netops_logger.get_logger()
        logger.info(f"迁移了 {migrated_count} 个旧格式加密密码")

    return migrated


def validate_encryption_key() -> bool:
    """
    验证加密密钥是否有效

    Returns:
        密钥是否有效
    """
    try:
        # 尝试派生密钥
        key = encrypted_manager.key_manager.derive_key()
        if not key or len(key) != 32:
            return False

        # 测试加密解密
        test_data = "test_password_123"
        encrypted = encrypted_manager.encrypt(test_data)
        decrypted = encrypted_manager.decrypt(encrypted)

        return decrypted == test_data
    except Exception as e:
        logger = netops_logger.get_logger()
        logger.error(f"密钥验证失败: {e}")
        return False


def get_key_info() -> dict:
    """
    获取密钥信息

    Returns:
        密钥信息字典
    """
    try:
        key_manager = encrypted_manager.key_manager
        return {
            "version": key_manager.get_key_version(),
            "key_file": str(key_manager.KEY_FILE),
            "machine_id_file": str(key_manager.MACHINE_ID_FILE),
            "key_valid": validate_encryption_key()
        }
    except Exception as e:
        logger = netops_logger.get_logger()
        logger.error(f"获取密钥信息失败: {e}")
        return {"error": str(e)}


def _get_machine_id():
    """获取机器ID（兼容性函数）"""
    return encrypted_manager.key_manager._get_machine_id()


def _derive_key() -> bytes:
    """派生密钥（兼容性函数）"""
    return encrypted_manager.key_manager.derive_key()


# 测试函数
def _test_encryption():
    """测试加密功能"""
    test_passwords = [
        "simple_password",
        "ComplexP@ssw0rd!#$%",
        "密码123",
        "",  # 空密码
        "a" * 100,  # 长密码
        "special_chars_!@#$%^&*()_+-=[]{}|;:',.<>?/~`",
    ]

    print("测试加密功能:")
    print("=" * 50)

    for pwd in test_passwords:
        try:
            encrypted = encrypt_password(pwd)
            decrypted = decrypt_password(encrypted)
            status = "✓" if decrypted == pwd else "✗"
            print(f"{status} 原密码: '{pwd}'")
            print(f"  加密后: '{encrypted}'")
            print(f"  解密后: '{decrypted}'")
            print()
        except Exception as e:
            print(f"✗ 密码 '{pwd}' 处理失败: {e}")
            print()

    print("密钥信息:")
    print("=" * 50)
    key_info = get_key_info()
    for k, v in key_info.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    _test_encryption()