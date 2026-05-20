"""file_operators.py 单元测试 — 原子文件操作与 JSON/设备文件管理。"""
import json
import os
import tempfile
from pathlib import Path

import pytest

from src.utils.file_operators import (
    AtomicFileWriter,
    JSONFileManager,
    DeviceFileManager,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


class TestAtomicFileWriter:
    """测试原子文件写入器。"""

    def test_write_and_read(self, tmp_dir):
        """原子写入后应能正确读取。"""
        target = Path(tmp_dir) / "test.txt"
        with AtomicFileWriter(target) as tmp:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write("hello atomic")
        assert target.exists()
        with open(target, "r", encoding="utf-8") as f:
            assert f.read() == "hello atomic"

    def test_overwrite_existing(self, tmp_dir):
        """覆盖已有文件应更新内容。"""
        target = Path(tmp_dir) / "test.txt"
        target.write_text("old content", encoding="utf-8")
        with AtomicFileWriter(target) as tmp:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write("new content")
        assert target.read_text(encoding="utf-8") == "new content"

    def test_exception_rollback(self, tmp_dir):
        """写入异常时不应损坏原文件。"""
        target = Path(tmp_dir) / "test.txt"
        target.write_text("original", encoding="utf-8")
        try:
            with AtomicFileWriter(target) as tmp:
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write("partial")
                raise ValueError("simulated error")
        except ValueError:
            pass
        # 原文件应保持不变
        assert target.read_text(encoding="utf-8") == "original"

    def test_creates_parent_dirs(self, tmp_dir):
        """不存在的父目录应自动创建。"""
        target = Path(tmp_dir) / "sub" / "dir" / "test.txt"
        with AtomicFileWriter(target) as tmp:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write("nested")
        assert target.exists()

    def test_temp_file_cleaned_on_error(self, tmp_dir):
        """异常时临时文件应被清理。"""
        target = Path(tmp_dir) / "test.txt"
        temp_path = None
        try:
            with AtomicFileWriter(target) as tmp:
                temp_path = tmp
                raise RuntimeError("fail")
        except RuntimeError:
            pass
        if temp_path:
            assert not temp_path.exists()


class TestJSONFileManager:
    """测试 JSON 文件管理器。"""

    def test_save_and_load(self, tmp_dir):
        """保存后加载应返回相同数据。"""
        path = Path(tmp_dir) / "data.json"
        data = {"key": "value", "list": [1, 2, 3], "nested": {"a": True}}
        assert JSONFileManager.save_json(path, data) is True
        loaded = JSONFileManager.load_json(path)
        assert loaded == data

    def test_load_nonexistent_returns_default(self, tmp_dir):
        """加载不存在的文件应返回默认值。"""
        path = Path(tmp_dir) / "nonexistent.json"
        assert JSONFileManager.load_json(path) is None
        assert JSONFileManager.load_json(path, default={}) == {}
        assert JSONFileManager.load_json(path, default=[]) == []

    def test_save_overwrites(self, tmp_dir):
        """保存应覆盖已有文件。"""
        path = Path(tmp_dir) / "data.json"
        JSONFileManager.save_json(path, {"v": 1})
        JSONFileManager.save_json(path, {"v": 2})
        loaded = JSONFileManager.load_json(path)
        assert loaded["v"] == 2

    def test_save_unicode(self, tmp_dir):
        """Unicode 数据应正确保存。"""
        path = Path(tmp_dir) / "unicode.json"
        data = {"设备": "核心交换机", "厂商": "华为"}
        JSONFileManager.save_json(path, data)
        loaded = JSONFileManager.load_json(path)
        assert loaded == data

    def test_load_invalid_json_raises(self, tmp_dir):
        """加载无效 JSON 应抛出 ValueError。"""
        path = Path(tmp_dir) / "bad.json"
        path.write_text("{invalid json}", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON文件格式错误"):
            JSONFileManager.load_json(path)

    def test_save_returns_bool(self, tmp_dir):
        """save_json 应返回布尔值。"""
        path = Path(tmp_dir) / "test.json"
        result = JSONFileManager.save_json(path, {"x": 1})
        assert result is True


class TestDeviceFileManager:
    """测试设备文件管理器。"""

    def test_save_and_load_device_list(self, tmp_dir):
        """保存后加载设备列表应返回相同内容。"""
        path = Path(tmp_dir) / "devices.txt"
        lines = [
            "# 格式：IP,厂商,设备类型,用户名,密码,协议,特权密码\n",
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable\n",
        ]
        assert DeviceFileManager.save_device_list(path, lines) is True
        loaded = DeviceFileManager.load_device_list(path)
        assert loaded == lines

    def test_load_nonexistent_returns_empty(self, tmp_dir):
        """加载不存在的设备列表应返回空列表。"""
        path = Path(tmp_dir) / "nonexistent.txt"
        assert DeviceFileManager.load_device_list(path) == []

    def test_save_empty_list(self, tmp_dir):
        """保存空列表应创建空文件。"""
        path = Path(tmp_dir) / "empty.txt"
        DeviceFileManager.save_device_list(path, [])
        loaded = DeviceFileManager.load_device_list(path)
        assert loaded == []

    def test_save_unicode_devices(self, tmp_dir):
        """Unicode 设备信息应正确保存。"""
        path = Path(tmp_dir) / "devices.txt"
        lines = ["192.168.1.1,华为,核心交换机,管理员,密码,ssh,特权密码\n"]
        DeviceFileManager.save_device_list(path, lines)
        loaded = DeviceFileManager.load_device_list(path)
        assert loaded == lines

    def test_save_returns_bool(self, tmp_dir):
        """save_device_list 应返回布尔值。"""
        path = Path(tmp_dir) / "test.txt"
        result = DeviceFileManager.save_device_list(path, ["line\n"])
        assert result is True
