"""account_manager.py 单元测试 — 账户管理核心模块。"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.account_manager import AccountManager


@pytest.fixture
def temp_account_dir(tmp_path):
    """创建临时账户配置文件目录，测试结束后清理。"""
    # 使用临时目录替代真实 config 目录
    with patch.object(AccountManager, 'ACCOUNT_FILE', tmp_path / "account.json"):
        yield tmp_path


@pytest.fixture
def account_manager(temp_account_dir):
    """创建 AccountManager 实例（自动初始化默认账户）。"""
    return AccountManager()


class TestAccountManagerInit:
    """测试账户管理器初始化。"""

    def test_init_creates_default_account(self, temp_account_dir):
        """首次初始化应自动创建默认账户文件。"""
        account_file = temp_account_dir / "account.json"
        assert not account_file.exists()
        AccountManager()
        assert account_file.exists()

    def test_default_account_username(self, temp_account_dir):
        """默认账户用户名应为 admin。"""
        manager = AccountManager()
        account = manager._load_account()
        assert account["username"] == "admin"

    def test_default_account_password_encrypted(self, temp_account_dir):
        """默认账户密码应加密存储。"""
        manager = AccountManager()
        account = manager._load_account()
        assert account["password"].startswith("ENC:")

    def test_init_idempotent(self, temp_account_dir):
        """多次初始化不应覆盖已有账户。"""
        manager1 = AccountManager()
        manager1.change_account("custom_user", "NewPass123")

        # 重新创建管理器，不应覆盖
        manager2 = AccountManager()
        account = manager2._load_account()
        assert account["username"] == "custom_user"


class TestVerifyPassword:
    """测试密码验证。"""

    def test_verify_default_password(self, account_manager):
        """默认密码 admin 应验证通过。"""
        assert account_manager.verify_password("admin") is True

    def test_verify_wrong_password(self, account_manager):
        """错误密码应验证失败。"""
        assert account_manager.verify_password("wrong_password") is False

    def test_verify_empty_password(self, account_manager):
        """空密码应验证失败。"""
        assert account_manager.verify_password("") is False


class TestVerifyLogin:
    """测试登录验证。"""

    def test_login_default_account(self, account_manager):
        """默认账户登录应成功。"""
        assert account_manager.verify_login("admin", "admin") is True

    def test_login_wrong_username(self, account_manager):
        """错误用户名应登录失败。"""
        assert account_manager.verify_login("wrong", "admin") is False

    def test_login_wrong_password(self, account_manager):
        """错误密码应登录失败。"""
        assert account_manager.verify_login("admin", "wrong") is False

    def test_login_empty_username(self, account_manager):
        """空用户名应登录失败。"""
        assert account_manager.verify_login("", "admin") is False

    def test_login_empty_password(self, account_manager):
        """空密码应登录失败。"""
        assert account_manager.verify_login("admin", "") is False


class TestPasswordComplexity:
    """测试密码复杂度校验。"""

    def test_valid_password(self):
        """合规密码（大小写+数字，≥8位）应通过。"""
        valid, msg = AccountManager.validate_password_complexity("Abcdef12")
        assert valid is True

    def test_too_short(self):
        """少于8位应失败。"""
        valid, msg = AccountManager.validate_password_complexity("Ab1")
        assert valid is False
        assert "8" in msg

    def test_only_uppercase(self):
        """纯大写字母应失败。"""
        valid, _ = AccountManager.validate_password_complexity("ABCDEFGH")
        assert valid is False

    def test_only_lowercase(self):
        """纯小写字母应失败。"""
        valid, _ = AccountManager.validate_password_complexity("abcdefgh")
        assert valid is False

    def test_only_digits(self):
        """纯数字应失败。"""
        valid, _ = AccountManager.validate_password_complexity("12345678")
        assert valid is False

    def test_upper_and_lower_no_digit(self):
        """大小写但缺数字应失败。"""
        valid, _ = AccountManager.validate_password_complexity("Abcdefgh")
        assert valid is False

    def test_upper_and_digit_no_lower(self):
        """大写+数字但缺小写应失败。"""
        valid, _ = AccountManager.validate_password_complexity("ABCDEFG1")
        assert valid is False

    def test_lower_and_digit_no_upper(self):
        """小写+数字但缺大写应失败。"""
        valid, _ = AccountManager.validate_password_complexity("abcdefg1")
        assert valid is False

    def test_exactly_8_chars(self):
        """刚好8位且合规应通过。"""
        valid, _ = AccountManager.validate_password_complexity("Aa123456")
        assert valid is True

    def test_complex_password(self):
        """复杂密码应通过。"""
        valid, _ = AccountManager.validate_password_complexity("MyP@ssw0rd")
        assert valid is True


class TestChangeAccount:
    """测试修改账户。"""

    def test_change_username_and_password(self, account_manager):
        """修改用户名和密码后应能用新凭证登录。"""
        success, msg = account_manager.change_account("newuser", "NewPass123")
        assert success is True
        assert account_manager.verify_login("newuser", "NewPass123") is True

    def test_change_password_only(self, account_manager):
        """仅修改密码后旧密码应失效。"""
        success, _ = account_manager.change_account("admin", "Admin1234")
        assert success is True
        assert account_manager.verify_password("admin") is False
        assert account_manager.verify_password("Admin1234") is True

    def test_change_username_empty(self, account_manager):
        """用户名为空应失败。"""
        success, msg = account_manager.change_account("", "NewPass123")
        assert success is False

    def test_change_username_whitespace_only(self, account_manager):
        """用户名仅空格应失败。"""
        success, msg = account_manager.change_account("   ", "NewPass123")
        assert success is False

    def test_change_persists_to_file(self, account_manager, temp_account_dir):
        """修改后应持久化到文件。"""
        account_manager.change_account("persist_user", "Persist123")

        # 直接读取文件验证
        with open(temp_account_dir / "account.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["username"] == "persist_user"
        assert data["password"].startswith("ENC:")

    def test_change_account_new_manager(self, account_manager, temp_account_dir):
        """修改后新管理器实例应读取到修改后的数据。"""
        account_manager.change_account("another", "Another12")

        manager2 = AccountManager()
        assert manager2.verify_login("another", "Another12") is True

    def test_change_account_old_password_invalid(self, account_manager):
        """修改后旧密码应无法登录。"""
        account_manager.change_account("admin", "FreshP@ss1")
        assert account_manager.verify_password("admin") is False


class TestCorruptedAccountFile:
    """测试账户文件损坏时的恢复。"""

    def test_corrupted_json_resets_default(self, temp_account_dir):
        """损坏的JSON文件应自动重置为默认账户。"""
        account_file = temp_account_dir / "account.json"
        account_file.write_text("not valid json{{{", encoding='utf-8')

        manager = AccountManager()
        # 损坏文件应被重置
        account = manager._load_account()
        assert account["username"] == "admin"
        assert manager.verify_password("admin") is True

    def test_non_dict_json_resets_default(self, temp_account_dir):
        """非字典JSON应自动重置为默认账户。"""
        account_file = temp_account_dir / "account.json"
        json.dump(["not", "a", "dict"], account_file.open('w', encoding='utf-8'))

        manager = AccountManager()
        account = manager._load_account()
        assert account["username"] == "admin"
