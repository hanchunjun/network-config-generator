"""key_manager.py 单元测试 — 密钥管理与加密数据管理器。"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.key_manager import KeyManager, EncryptedDataManager


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def key_manager(tmp_dir):
    """创建使用临时目录的 KeyManager 实例。"""
    km = KeyManager()
    km.KEY_FILE = Path(tmp_dir) / "key_info.json"
    km.MACHINE_ID_FILE = Path(tmp_dir) / "machine_id.json"
    km._key_cache = None
    return km


@pytest.fixture
def enc_manager(key_manager):
    """创建绑定到临时 KeyManager 的 EncryptedDataManager。"""
    em = EncryptedDataManager()
    em.key_manager = key_manager
    return em


class TestKeyManagerDeriveKey:
    """测试密钥派生功能。"""

    def test_derive_key_returns_bytes(self, key_manager):
        """派生密钥应返回 bytes 类型。"""
        key = key_manager.derive_key()
        assert isinstance(key, bytes)

    def test_derive_key_32_bytes(self, key_manager):
        """派生密钥应为 32 字节（AES-256）。"""
        key = key_manager.derive_key()
        assert len(key) == 32

    def test_derive_key_caching(self, key_manager):
        """相同实例多次派生应返回缓存的密钥。"""
        key1 = key_manager.derive_key()
        key2 = key_manager.derive_key()
        assert key1 is key2

    def test_derive_key_deterministic(self, key_manager):
        """相同条件下派生密钥应确定。"""
        key1 = key_manager.derive_key()
        key_manager._key_cache = None
        key2 = key_manager.derive_key()
        assert key1 == key2


class TestKeyManagerKeyInfo:
    """测试密钥信息管理。"""

    def test_create_new_key_info(self, key_manager):
        """首次调用应创建新的密钥信息。"""
        info = key_manager._create_new_key_info()
        assert info["version"] == KeyManager.CURRENT_VERSION
        assert "salt" in info
        assert "machine_id" in info
        assert "backup_key" in info
        assert "created_at" in info

    def test_key_info_persisted(self, key_manager):
        """密钥信息应持久化到文件。"""
        key_manager.derive_key()
        assert key_manager.KEY_FILE.exists()

    def test_load_existing_key_info(self, key_manager):
        """已存在密钥文件时应加载而非重建。"""
        key_manager.derive_key()
        cached = key_manager._key_cache
        # 再次派生应使用缓存
        key_manager.derive_key()
        assert key_manager._key_cache is cached

    def test_validate_key_info_valid(self, key_manager):
        """有效的密钥信息应通过验证。"""
        info = key_manager._create_new_key_info()
        assert key_manager._validate_key_info(info) is True

    def test_validate_key_info_missing_version(self, key_manager):
        """缺少 version 字段应验证失败。"""
        info = {"salt": "abc"}
        assert key_manager._validate_key_info(info) is False

    def test_validate_key_info_missing_salt(self, key_manager):
        """缺少 salt 字段应验证失败。"""
        info = {"version": "v2"}
        assert key_manager._validate_key_info(info) is False

    def test_validate_key_info_invalid_salt(self, key_manager):
        """无效的 salt 格式应验证失败。"""
        info = {"version": "v2", "salt": "!!!invalid!!!"}
        assert key_manager._validate_key_info(info) is False


class TestKeyManagerVersion:
    """测试版本管理。"""

    def test_current_version_is_v2(self):
        assert KeyManager.CURRENT_VERSION == "v2"

    def test_get_key_version(self, key_manager):
        """get_key_version 应返回字符串。"""
        v = key_manager.get_key_version()
        assert isinstance(v, str)
        assert v == "v2"


class TestKeyManagerMachineId:
    """测试机器 ID 获取。"""

    def test_get_machine_id_not_empty(self, key_manager):
        """机器 ID 不应为空字符串。"""
        mid = key_manager._get_machine_id()
        assert isinstance(mid, str)
        assert len(mid) > 0

    def test_get_machine_id_contains_hostname(self, key_manager):
        """机器 ID 应包含主机名。"""
        import socket
        mid = key_manager._get_machine_id()
        assert socket.gethostname() in mid


class TestEncryptedDataManager:
    """测试加密数据管理器。"""

    def test_encrypt_produces_enc_prefix(self, enc_manager):
        """加密结果应以 ENC: 开头。"""
        result = enc_manager.encrypt("test_data")
        assert result.startswith("ENC:")

    def test_encrypt_decrypt_roundtrip(self, enc_manager):
        """加密后解密应还原原始数据。"""
        original = "sensitive_password_123"
        encrypted = enc_manager.encrypt(original)
        decrypted = enc_manager.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_empty_string(self, enc_manager):
        """空字符串加密应返回空字符串。"""
        result = enc_manager.encrypt("")
        assert result == ""

    def test_decrypt_plain_text_passthrough(self, enc_manager):
        """解密非加密文本应原样返回。"""
        plain = "not_encrypted_data"
        result = enc_manager.decrypt(plain)
        assert result == plain

    def test_decrypt_empty_string(self, enc_manager):
        """解密空字符串应返回空字符串。"""
        assert enc_manager.decrypt("") == ""

    def test_is_encrypted_true(self, enc_manager):
        """加密数据应被识别为已加密。"""
        encrypted = enc_manager.encrypt("test")
        assert enc_manager.is_encrypted(encrypted) is True

    def test_is_encrypted_false(self, enc_manager):
        """明文数据应被识别为未加密。"""
        assert enc_manager.is_encrypted("plain_text") is False

    def test_is_encrypted_empty(self, enc_manager):
        """空字符串应被识别为未加密。"""
        assert enc_manager.is_encrypted("") is False

    def test_encrypt_unicode(self, enc_manager):
        """Unicode 内容应能正确加密解密。"""
        original = "密码测试@#$%^&*()"
        encrypted = enc_manager.encrypt(original)
        decrypted = enc_manager.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_long_text(self, enc_manager):
        """长文本应能正确加密解密。"""
        original = "A" * 10000
        encrypted = enc_manager.encrypt(original)
        decrypted = enc_manager.decrypt(encrypted)
        assert decrypted == original

    def test_different_encryptions_differ(self, enc_manager):
        """同一明文两次加密结果应不同（随机 nonce）。"""
        enc1 = enc_manager.encrypt("same_text")
        enc2 = enc_manager.encrypt("same_text")
        assert enc1 != enc2

    def test_migrate_old_data_non_encrypted(self, enc_manager):
        """非加密数据迁移应原样返回。"""
        result = enc_manager.migrate_old_data("plain_data")
        assert result == "plain_data"
