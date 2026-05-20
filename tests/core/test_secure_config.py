"""secure_config.py 单元测试 — 加密配置文件读写。"""
import json
import os
import tempfile
from pathlib import Path

import pytest

from src.core.secure_config import SecureConfigFile


@pytest.fixture
def tmp_dir():
    """创建临时目录，测试结束后清理。"""
    d = tempfile.mkdtemp()
    yield d
    # 清理
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def config_file(tmp_dir):
    """返回临时配置文件路径。"""
    return os.path.join(tmp_dir, "test_config.json")


@pytest.fixture
def secure_config():
    """返回 SecureConfigFile 单例（重置）。"""
    SecureConfigFile._instance = None
    return SecureConfigFile.instance()


class TestSecureConfigSave:
    """测试加密保存功能。"""

    def test_save_creates_enc_file(self, secure_config, config_file):
        """保存后应生成 .enc 文件。"""
        data = {"key": "value", "number": 42}
        result = secure_config.save(config_file, data)
        assert result is True
        assert os.path.exists(config_file + ".enc")

    def test_save_removes_plain_file(self, secure_config, config_file):
        """保存加密文件后，明文文件应被删除。"""
        # 先写一个明文文件
        with open(config_file, "w") as f:
            f.write("plain")
        secure_config.save(config_file, {"a": 1})
        assert not os.path.exists(config_file)

    def test_save_returns_true_on_success(self, secure_config, config_file):
        result = secure_config.save(config_file, {"test": True})
        assert result is True

    def test_save_nested_dict(self, secure_config, config_file):
        """嵌套字典应能正确保存。"""
        data = {
            "level1": {
                "level2": [1, 2, 3],
                "str": "hello",
            },
            "bool": True,
            "null": None,
        }
        assert secure_config.save(config_file, data) is True

    def test_save_unicode_content(self, secure_config, config_file):
        """Unicode 内容应能正确保存。"""
        data = {"设备": "核心交换机", "厂商": "华为", "描述": "测试配置"}
        assert secure_config.save(config_file, data) is True


class TestSecureConfigLoad:
    """测试加密加载功能。"""

    def test_load_encrypted_file(self, secure_config, config_file):
        """加载加密文件应返回原始数据。"""
        original = {"api_key": "sk-test-123", "url": "https://api.example.com"}
        secure_config.save(config_file, original)
        loaded = secure_config.load(config_file)
        assert loaded is not None
        assert loaded["api_key"] == "sk-test-123"
        assert loaded["url"] == "https://api.example.com"

    def test_load_plain_json_migrates(self, secure_config, config_file):
        """加载明文 JSON 应自动加密迁移。"""
        data = {"plain": "data"}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        loaded = secure_config.load(config_file)
        assert loaded is not None
        assert loaded["plain"] == "data"
        # 迁移后应生成 .enc 文件
        assert os.path.exists(config_file + ".enc")

    def test_load_nonexistent_file(self, secure_config, tmp_dir):
        """加载不存在的文件应返回 None。"""
        result = secure_config.load(os.path.join(tmp_dir, "nonexistent.json"))
        assert result is None

    def test_load_returns_dict(self, secure_config, config_file):
        """加载返回值应为 dict 类型。"""
        secure_config.save(config_file, {"x": 1})
        loaded = secure_config.load(config_file)
        assert isinstance(loaded, dict)

    def test_load_preserves_types(self, secure_config, config_file):
        """加载应保留原始数据类型。"""
        data = {
            "str": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, "two", 3.0],
            "dict": {"nested": True},
        }
        secure_config.save(config_file, data)
        loaded = secure_config.load(config_file)
        assert loaded["str"] == "hello"
        assert loaded["int"] == 42
        assert abs(loaded["float"] - 3.14) < 1e-9
        assert loaded["bool"] is True
        assert loaded["null"] is None
        assert loaded["list"] == [1, "two", 3.0]
        assert loaded["dict"] == {"nested": True}

    def test_load_empty_dict(self, secure_config, config_file):
        """空字典应能保存和加载。"""
        secure_config.save(config_file, {})
        loaded = secure_config.load(config_file)
        assert loaded is not None
        assert loaded == {}


class TestSecureConfigRoundTrip:
    """测试加密-解密往返一致性。"""

    def test_multiple_save_load_cycles(self, secure_config, config_file):
        """多次保存-加载循环应保持数据一致。"""
        for i in range(5):
            data = {"cycle": i, "data": f"iteration_{i}"}
            secure_config.save(config_file, data)
            loaded = secure_config.load(config_file)
            assert loaded["cycle"] == i
            assert loaded["data"] == f"iteration_{i}"

    def test_overwrite_existing(self, secure_config, config_file):
        """覆盖已有文件应更新内容。"""
        secure_config.save(config_file, {"version": 1})
        secure_config.save(config_file, {"version": 2})
        loaded = secure_config.load(config_file)
        assert loaded["version"] == 2


class TestSecureConfigSingleton:
    """测试单例模式。"""

    def test_same_instance(self):
        """多次调用 instance() 应返回同一对象。"""
        SecureConfigFile._instance = None
        a = SecureConfigFile.instance()
        b = SecureConfigFile.instance()
        assert a is b

    def test_new_instance_after_reset(self):
        """重置后应创建新实例。"""
        SecureConfigFile._instance = None
        a = SecureConfigFile.instance()
        SecureConfigFile._instance = None
        b = SecureConfigFile.instance()
        assert a is not b
