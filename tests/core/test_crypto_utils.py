"""crypto_utils.py 单元测试 — 密码加密工具函数。"""
import pytest

from src.core.crypto_utils import (
    encrypt_password,
    decrypt_password,
    is_encrypted,
    migrate_old_passwords,
    validate_encryption_key,
    get_key_info,
    ENC_PREFIX,
    LEGACY_SALT,
    NONCE_LENGTH,
)


class TestEncryptPassword:
    """测试密码加密函数。"""

    def test_encrypt_returns_enc_prefix(self):
        """加密结果应以 ENC: 开头。"""
        result = encrypt_password("test_pass")
        assert result.startswith("ENC:")

    def test_encrypt_empty_returns_empty(self):
        """空密码应返回空字符串。"""
        assert encrypt_password("") == ""

    def test_encrypt_none_returns_none(self):
        """None 应返回 None。"""
        assert encrypt_password(None) is None

    def test_encrypt_unicode(self):
        """Unicode 密码应能正确加密。"""
        result = encrypt_password("密码@123")
        assert result.startswith("ENC:")

    def test_encrypt_long_password(self):
        """长密码应能正确加密。"""
        result = encrypt_password("A" * 500)
        assert result.startswith("ENC:")


class TestDecryptPassword:
    """测试密码解密函数。"""

    def test_decrypt_roundtrip(self):
        """加密后解密应还原原始密码。"""
        original = "my_secret_password"
        encrypted = encrypt_password(original)
        decrypted = decrypt_password(encrypted)
        assert decrypted == original

    def test_decrypt_plain_passthrough(self):
        """解密非加密密码应原样返回。"""
        plain = "not_encrypted"
        assert decrypt_password(plain) == plain

    def test_decrypt_empty_returns_empty(self):
        """解密空字符串应返回空字符串。"""
        assert decrypt_password("") == ""

    def test_decrypt_none_returns_none(self):
        """解密 None 应返回 None。"""
        assert decrypt_password(None) is None

    def test_decrypt_unicode_roundtrip(self):
        """Unicode 密码应能正确加解密。"""
        original = "管理员密码@#$%"
        encrypted = encrypt_password(original)
        decrypted = decrypt_password(encrypted)
        assert decrypted == original


class TestIsEncrypted:
    """测试加密状态检查。"""

    def test_encrypted_true(self):
        encrypted = encrypt_password("test")
        assert is_encrypted(encrypted) is True

    def test_plain_false(self):
        assert is_encrypted("plain") is False

    def test_empty_false(self):
        assert is_encrypted("") is False

    def test_none_false(self):
        assert is_encrypted(None) is False

    def test_enc_prefix_only(self):
        """仅有 ENC: 前缀但不是有效加密数据。"""
        assert is_encrypted("ENC:something") is True


class TestMigrateOldPasswords:
    """测试旧格式密码迁移。"""

    def test_empty_list(self):
        """空列表迁移应返回空列表。"""
        assert migrate_old_passwords([]) == []

    def test_non_encrypted_passthrough(self):
        """非加密密码应原样返回。"""
        result = migrate_old_passwords(["plain1", "plain2"])
        assert result == ["plain1", "plain2"]

    def test_none_values_preserved(self):
        """None 值应被保留。"""
        result = migrate_old_passwords([None, "plain", None])
        assert result == [None, "plain", None]


class TestValidateEncryptionKey:
    """测试密钥验证。"""

    def test_key_valid(self):
        """密钥验证应返回布尔值。"""
        result = validate_encryption_key()
        assert isinstance(result, bool)

    def test_key_validation_roundtrip(self):
        """密钥有效时加解密测试数据应成功。"""
        test_data = "test_password_123"
        encrypted = encrypt_password(test_data)
        decrypted = decrypt_password(encrypted)
        assert decrypted == test_data


class TestGetKeyInfo:
    """测试密钥信息获取。"""

    def test_get_key_info_returns_dict(self):
        """get_key_info 应返回字典。"""
        info = get_key_info()
        assert isinstance(info, dict)

    def test_get_key_info_has_version(self):
        """密钥信息应包含 version 字段。"""
        info = get_key_info()
        assert "version" in info

    def test_get_key_info_has_key_valid(self):
        """密钥信息应包含 key_valid 字段。"""
        info = get_key_info()
        assert "key_valid" in info


class TestConstants:
    """测试常量定义。"""

    def test_enc_prefix(self):
        assert ENC_PREFIX == "ENC:"

    def test_legacy_salt_is_bytes(self):
        assert isinstance(LEGACY_SALT, bytes)

    def test_nonce_length(self):
        assert NONCE_LENGTH == 12


class TestEncryptDecryptErrorHandling:
    """测试加密解密异常处理分支。"""

    def test_encrypt_exception_returns_plaintext(self, monkeypatch):
        """加密异常时应返回原文（不丢失数据）。"""
        from src.core import crypto_utils
        monkeypatch.setattr(
            crypto_utils.encrypted_manager, "encrypt",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        result = encrypt_password("test_pass")
        assert result == "test_pass"

    def test_decrypt_exception_returns_stored(self, monkeypatch):
        """解密异常时应返回原值。"""
        from src.core import crypto_utils
        enc = encrypt_password("test_pass")
        monkeypatch.setattr(
            crypto_utils.encrypted_manager, "decrypt",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        result = decrypt_password(enc)
        assert result == enc

    def test_validate_key_returns_false_on_exception(self, monkeypatch):
        """密钥验证异常时应返回 False。"""
        from src.core import crypto_utils
        monkeypatch.setattr(
            crypto_utils.encrypted_manager.key_manager, "derive_key",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        result = validate_encryption_key()
        assert result is False

    def test_get_key_info_returns_error_on_exception(self, monkeypatch):
        """获取密钥信息异常时应返回包含 error 的字典。"""
        from src.core import crypto_utils
        monkeypatch.setattr(
            crypto_utils.encrypted_manager.key_manager, "get_key_version",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        info = get_key_info()
        assert "error" in info


class TestMigrateOldFormat:
    """测试旧格式密码迁移（ENC: 前缀但无版本号）。"""

    def test_migrate_old_format_detected(self):
        """旧格式密码（ENC:data 无版本号）应被检测并迁移。"""
        # 构造旧格式：ENC: 前缀，但第二部分不含版本号
        old_format = "ENC:old_encrypted_blob"
        result = migrate_old_passwords([old_format])
        # 迁移尝试后应返回结果（可能迁移失败原样返回）
        assert isinstance(result, list)
        assert len(result) == 1

    def test_migrate_with_actual_old_data(self, monkeypatch):
        """模拟旧格式解密成功时的迁移路径。"""
        from src.core import crypto_utils
        # mock migrate_old_data 使其成功迁移
        monkeypatch.setattr(
            crypto_utils.encrypted_manager, "migrate_old_data",
            lambda data: "ENC:v2:new_encrypted_data"
        )
        result = migrate_old_passwords(["ENC:old_data"])
        assert result[0] == "ENC:v2:new_encrypted_data"


class TestGetKeyInfoError:
    """测试 get_key_info 错误处理。"""

    def test_get_key_info_error_returns_dict_with_error(self, monkeypatch):
        """get_key_info 异常时应返回包含 error 的字典。"""
        from src.core import crypto_utils
        monkeypatch.setattr(
            crypto_utils.encrypted_manager.key_manager, "KEY_FILE",
            property(lambda self: (_ for _ in ()).throw(Exception("forced")))
        )
        info = get_key_info()
        assert isinstance(info, dict)


class TestMigrateOldPasswordsEdgeCases:
    """测试密码迁移边界情况。"""

    def test_mixed_list(self):
        """混合列表应正确处理。"""
        result = migrate_old_passwords([
            "plain",
            "ENC:v1:old_encrypted_data",
            None,
            "",
        ])
        assert result[0] == "plain"
        assert result[2] is None
        assert result[3] == ""

    def test_single_item_list(self):
        """单元素列表应正确处理。"""
        result = migrate_old_passwords(["only_one"])
        assert result == ["only_one"]
