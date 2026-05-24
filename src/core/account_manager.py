#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账户管理核心模块
负责账户数据的读写、密码加密/验证、复杂度校验、首次初始化。

默认账户：admin / admin
存储路径：config/account.json（用户名明文 + 密码AES-GCM密文）
"""

import json
import re
from pathlib import Path
from typing import Tuple

from src.core.crypto_utils import encrypt_password, decrypt_password
from src.core.logger import netops_logger
from src.utils.resource_path import get_config_path
from src.utils.file_operators import AtomicFileWriter


class AccountManager:
    """账户管理器。

    单文件JSON存储，原子写入，AES-GCM密码加密。
    首次运行时自动初始化默认账户（admin/admin）。

    Attributes:
        ACCOUNT_FILE: 账户配置文件路径
        DEFAULT_USERNAME: 默认用户名
        DEFAULT_PASSWORD: 默认密码
        MIN_PASSWORD_LENGTH: 密码最小长度
    """

    ACCOUNT_FILE: Path = Path(get_config_path("config/account.json"))
    DEFAULT_USERNAME: str = "admin"
    DEFAULT_PASSWORD: str = "admin"
    MIN_PASSWORD_LENGTH: int = 8

    def __init__(self) -> None:
        """初始化账户管理器，确保账户文件存在。"""
        self._ensure_account_file()

    def _ensure_account_file(self) -> None:
        """确保账户文件存在，不存在则创建默认账户。"""
        if not self.ACCOUNT_FILE.exists():
            self.ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._init_default_account()

    def _init_default_account(self) -> None:
        """创建默认账户（admin/admin），密码加密存储。"""
        encrypted_pwd = encrypt_password(self.DEFAULT_PASSWORD)
        account_data = {
            "username": self.DEFAULT_USERNAME,
            "password": encrypted_pwd,
        }
        self._write_account_file(account_data)
        netops_logger.get_logger().info("已初始化默认账户（admin）")

    def _load_account(self) -> dict:
        """加载账户配置文件。

        Returns:
            账户数据字典 {"username": str, "password": str}
        """
        try:
            with open(self.ACCOUNT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("账户配置文件格式错误")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            netops_logger.get_logger().error(f"账户配置文件损坏: {e}，重置为默认账户")
            self._init_default_account()
            return {"username": self.DEFAULT_USERNAME, "password": encrypt_password(self.DEFAULT_PASSWORD)}
        except Exception as e:
            netops_logger.get_logger().error(f"读取账户配置文件失败: {e}")
            return {"username": self.DEFAULT_USERNAME, "password": encrypt_password(self.DEFAULT_PASSWORD)}

    def _write_account_file(self, account_data: dict) -> bool:
        """原子写入账户配置文件。

        Args:
            account_data: 账户数据字典

        Returns:
            是否写入成功
        """
        try:
            self.ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with AtomicFileWriter(self.ACCOUNT_FILE) as temp_file:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(account_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            netops_logger.get_logger().error(f"写入账户配置文件失败: {e}")
            return False

    def verify_password(self, input_password: str) -> bool:
        """验证输入的密码是否正确。

        Args:
            input_password: 用户输入的明文密码

        Returns:
            密码是否匹配
        """
        account = self._load_account()
        stored_password = account.get("password", "")

        try:
            decrypted = decrypt_password(stored_password)
            return decrypted == input_password
        except Exception as e:
            netops_logger.get_logger().error(f"密码验证失败: {e}")
            return False

    def verify_login(self, username: str, password: str) -> bool:
        """验证用户名和密码。

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            是否验证通过
        """
        account = self._load_account()
        stored_username = account.get("username", self.DEFAULT_USERNAME)

        if username != stored_username:
            return False

        return self.verify_password(password)

    def change_account(self, new_username: str, new_password: str) -> Tuple[bool, str]:
        """修改账户信息。

        Args:
            new_username: 新用户名
            new_password: 新明文密码（调用方需先校验复杂度）

        Returns:
            (是否成功, 提示消息)
        """
        if not new_username or not new_username.strip():
            return False, "用户名不能为空"

        new_username = new_username.strip()

        try:
            encrypted_pwd = encrypt_password(new_password)
            account_data = {
                "username": new_username,
                "password": encrypted_pwd,
            }
            if self._write_account_file(account_data):
                netops_logger.get_logger().info(f"账户信息已更新，新用户名: {new_username}")
                return True, "账户信息已加密保存，重启软件生效"
            else:
                return False, "配置保存失败，请稍后重试"
        except Exception as e:
            netops_logger.get_logger().error(f"修改账户失败: {e}")
            return False, "配置保存失败，请稍后重试"

    @staticmethod
    def validate_password_complexity(password: str) -> Tuple[bool, str]:
        """校验密码复杂度。

        规则：
        - 长度 ≥ 8 位
        - 必须同时包含大写字母、小写字母、阿拉伯数字

        Args:
            password: 待校验的明文密码

        Returns:
            (是否合规, 提示消息)
        """
        if len(password) < 8:
            return False, "密码长度不能少于 8 位，请重新设置"

        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))

        if not (has_upper and has_lower and has_digit):
            return False, "密码必须包含大写字母、小写字母与数字组合"

        return True, "密码合规"
