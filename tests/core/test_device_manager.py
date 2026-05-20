"""device_manager.py 单元测试 — 设备管理器。"""
import json
import os
import tempfile
from pathlib import Path

import pytest

from src.core.device_manager import (
    DeviceManager,
    VENDORS,
    DEVICE_TYPES,
    PROTOCOLS,
    DEVICE_HEADERS,
    DEVICE_TEMPLATES,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def project_dir(tmp_dir):
    """创建标准项目目录结构。"""
    config_dir = Path(tmp_dir) / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "device_list.txt").write_text(
        "# 格式：IP,厂商,设备类型,用户名,密码,协议,特权密码,分组,标签\n",
        encoding="utf-8",
    )
    return str(tmp_dir)


@pytest.fixture
def device_manager(project_dir):
    """创建绑定到临时项目的 DeviceManager。"""
    dm = DeviceManager()
    dm.set_project(project_dir)
    return dm


class TestDeviceManagerInit:
    """测试初始化。"""

    def test_default_project_none(self):
        dm = DeviceManager()
        assert dm.project_path is None
        assert dm.devices == []

    def test_set_project(self, project_dir):
        dm = DeviceManager()
        dm.set_project(project_dir)
        assert dm.project_path == project_dir
        assert dm.devices == []


class TestDeviceManagerLoadDevices:
    """测试设备加载功能。"""

    def test_load_empty_list(self, device_manager):
        """空设备列表应返回空数组。"""
        devices = device_manager.load_devices()
        assert devices == []

    def test_load_valid_devices(self, project_dir):
        """加载有效设备列表。"""
        device_file = Path(project_dir) / "config" / "device_list.txt"
        device_file.write_text(
            "192.168.1.1,锐捷,核心交换机,admin,pass123,ssh,enable123,核心区,核心\n"
            "10.0.0.1,华为,接入交换机,admin,huawei123,ssh,enable456,接入层,办公\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = dm.load_devices()
        assert len(devices) == 2
        assert devices[0]["ip"] == "192.168.1.1"
        assert devices[1]["ip"] == "10.0.0.1"

    def test_load_skips_comments(self, project_dir):
        """应跳过注释行。"""
        device_file = Path(project_dir) / "config" / "device_list.txt"
        device_file.write_text(
            "# 这是注释\n"
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable,核心,标签\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = dm.load_devices()
        assert len(devices) == 1

    def test_load_skips_short_lines(self, project_dir):
        """字段不足的行应被跳过。"""
        device_file = Path(project_dir) / "config" / "device_list.txt"
        device_file.write_text(
            "192.168.1.1,锐捷\n"  # 只有2个字段
            "192.168.1.2,锐捷,核心交换机,admin,pass,ssh,enable,核心,标签\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = dm.load_devices()
        assert len(devices) == 1
        assert devices[0]["ip"] == "192.168.1.2"

    def test_load_no_project(self):
        """未设置项目路径应返回空列表。"""
        dm = DeviceManager()
        devices = dm.load_devices()
        assert devices == []

    def test_load_device_fields(self, project_dir):
        """加载的设备应包含所有必要字段。"""
        device_file = Path(project_dir) / "config" / "device_list.txt"
        device_file.write_text(
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable,核心区,核心\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = dm.load_devices()
        assert len(devices) == 1
        device = devices[0]
        assert "ip" in device
        assert "vendor" in device
        assert "device_type" in device
        assert "username" in device
        assert "password" in device
        assert "protocol" in device
        assert "enable_password" in device
        assert "group" in device
        assert "tags" in device

    def test_load_optional_fields_default(self, project_dir):
        """缺少可选字段时应使用默认值。"""
        device_file = Path(project_dir) / "config" / "device_list.txt"
        device_file.write_text(
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = dm.load_devices()
        assert len(devices) == 1
        assert devices[0]["group"] == ""
        assert devices[0]["tags"] == ""


class TestDeviceManagerSaveDevices:
    """测试设备保存功能。"""

    def test_save_creates_file(self, device_manager):
        """保存设备应创建设备列表文件。"""
        devices = [
            {
                "ip": "192.168.1.1",
                "vendor": "锐捷",
                "device_type": "核心交换机",
                "username": "admin",
                "password": "pass123",
                "protocol": "ssh",
                "enable_password": "enable123",
                "group": "核心区",
                "tags": "核心",
            }
        ]
        result = device_manager.save_devices(devices)
        assert result is True
        assert os.path.exists(device_manager._device_file())

    def test_save_returns_false_no_project(self):
        """未设置项目路径应返回 False。"""
        dm = DeviceManager()
        result = dm.save_devices([{"ip": "1.1.1.1"}])
        assert result is False

    def test_save_encrypts_passwords(self, device_manager):
        """保存时密码应被加密。"""
        devices = [
            {
                "ip": "192.168.1.1",
                "vendor": "锐捷",
                "device_type": "核心交换机",
                "username": "admin",
                "password": "plain_pass",
                "protocol": "ssh",
                "enable_password": "plain_enable",
                "group": "",
                "tags": "",
            }
        ]
        device_manager.save_devices(devices)
        content = Path(device_manager._device_file()).read_text(encoding="utf-8")
        # 密码应以 ENC: 前缀存储
        assert "ENC:" in content
        # 不应包含明文密码
        assert "plain_pass" not in content

    def test_save_roundtrip(self, project_dir):
        """保存后加载应还原设备数据。"""
        dm = DeviceManager()
        dm.set_project(project_dir)
        devices = [
            {
                "ip": "10.0.0.1",
                "vendor": "华为",
                "device_type": "路由器",
                "username": "admin",
                "password": "test_pass",
                "protocol": "ssh",
                "enable_password": "test_enable",
                "group": "出口区",
                "tags": "边界",
            }
        ]
        dm.save_devices(devices)
        dm2 = DeviceManager()
        dm2.set_project(project_dir)
        loaded = dm2.load_devices()
        assert len(loaded) == 1
        assert loaded[0]["ip"] == "10.0.0.1"
        assert loaded[0]["vendor"] == "华为"
        assert loaded[0]["password"] == "test_pass"
        assert loaded[0]["group"] == "出口区"


class TestDeviceManagerImport:
    """测试设备导入功能。"""

    def test_import_txt(self, tmp_dir):
        """从 TXT 文件导入设备。"""
        txt_path = Path(tmp_dir) / "import.txt"
        txt_path.write_text(
            "# 设备清单\n"
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable,核心,标签\n"
            "10.0.0.1,华为,接入交换机,admin,pass2,ssh,enable2,接入,标签2\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        devices = dm.import_txt(str(txt_path))
        assert len(devices) == 2
        assert devices[0]["ip"] == "192.168.1.1"
        assert devices[1]["vendor"] == "华为"

    def test_import_csv(self, tmp_dir):
        """从 CSV 文件导入设备。"""
        import csv
        csv_path = Path(tmp_dir) / "import.csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(DEVICE_HEADERS)
            writer.writerow([
                "192.168.1.1", "锐捷", "核心交换机", "admin",
                "pass", "ssh", "enable", "核心", "标签",
            ])
        dm = DeviceManager()
        devices = dm.import_csv(str(csv_path))
        assert len(devices) == 1
        assert devices[0]["ip"] == "192.168.1.1"

    def test_import_txt_skips_comments(self, tmp_dir):
        """导入 TXT 应跳过注释行。"""
        txt_path = Path(tmp_dir) / "import.txt"
        txt_path.write_text(
            "# 注释行\n"
            "192.168.1.1,锐捷,核心交换机,admin,pass,ssh,enable,核心,标签\n",
            encoding="utf-8",
        )
        dm = DeviceManager()
        devices = dm.import_txt(str(txt_path))
        assert len(devices) == 1


class TestDeviceManagerTemplate:
    """测试模板生成功能。"""

    def test_generate_csv_template(self, tmp_dir):
        """生成 CSV 模板应成功。"""
        path = Path(tmp_dir) / "template.csv"
        dm = DeviceManager()
        result = dm.generate_template(str(path), fmt="csv")
        assert result is True
        assert path.exists()

    def test_generate_txt_template(self, tmp_dir):
        """生成 TXT 模板应成功。"""
        path = Path(tmp_dir) / "template.txt"
        dm = DeviceManager()
        result = dm.generate_template(str(path), fmt="txt")
        assert result is True
        assert path.exists()

    def test_generate_csv_has_headers(self, tmp_dir):
        """CSV 模板应包含表头。"""
        import csv
        path = Path(tmp_dir) / "template.csv"
        dm = DeviceManager()
        dm.generate_template(str(path), fmt="csv")
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
        assert header == DEVICE_HEADERS

    def test_generate_txt_has_data_rows(self, tmp_dir):
        """TXT 模板应包含示例数据行。"""
        path = Path(tmp_dir) / "template.txt"
        dm = DeviceManager()
        dm.generate_template(str(path), fmt="txt")
        content = path.read_text(encoding="utf-8")
        # 应包含示例 IP
        assert "192.168.1.1" in content
        assert "192.168.1.2" in content


class TestDeviceManagerHistory:
    """测试历史记录功能。"""

    def test_record_and_get_history(self, device_manager):
        """记录历史后应能读取。"""
        device_manager.record_history("添加设备", "新增 192.168.1.1", 1)
        history = device_manager.get_history()
        assert len(history) == 1
        assert history[0]["action"] == "添加设备"
        assert history[0]["device_count"] == 1

    def test_history_contains_timestamp(self, device_manager):
        """历史记录应包含时间戳。"""
        device_manager.record_history("测试", "详情")
        history = device_manager.get_history()
        assert "timestamp" in history[0]

    def test_get_history_no_project(self):
        """未设置项目应返回空列表。"""
        dm = DeviceManager()
        assert dm.get_history() == []

    def test_history_trims_to_500(self, device_manager):
        """历史记录超过 500 条时应截断。"""
        for i in range(510):
            device_manager.record_history(f"action_{i}", f"detail_{i}")
        history = device_manager.get_history()
        assert len(history) == 500
        # 应保留最新的记录
        assert history[-1]["action"] == "action_509"


class TestDeviceManagerStats:
    """测试统计功能。"""

    def test_get_device_count(self, device_manager):
        """设备计数应正确。"""
        assert device_manager.get_device_count() == 0
        device_manager.devices = [{"ip": "1.1.1.1"}, {"ip": "2.2.2.2"}]
        assert device_manager.get_device_count() == 2

    def test_get_groups(self, device_manager):
        """分组列表应正确。"""
        device_manager.devices = [
            {"ip": "1.1.1.1", "group": "核心区"},
            {"ip": "2.2.2.2", "group": "接入层"},
            {"ip": "3.3.3.3", "group": "核心区"},
            {"ip": "4.4.4.4", "group": ""},
        ]
        groups = device_manager.get_groups()
        assert groups == ["接入层", "核心区"]

    def test_get_devices_by_group(self, device_manager):
        """按分组筛选设备应正确。"""
        device_manager.devices = [
            {"ip": "1.1.1.1", "group": "核心区"},
            {"ip": "2.2.2.2", "group": "接入层"},
            {"ip": "3.3.3.3", "group": "核心区"},
        ]
        core = device_manager.get_devices_by_group("核心区")
        assert len(core) == 2

    def test_get_stats(self, device_manager):
        """统计信息应包含所有维度。"""
        device_manager.devices = [
            {"ip": "1.1.1.1", "vendor": "锐捷", "device_type": "核心交换机", "group": "核心区"},
            {"ip": "2.2.2.2", "vendor": "华为", "device_type": "接入交换机", "group": "接入层"},
            {"ip": "3.3.3.3", "vendor": "锐捷", "device_type": "路由器", "group": "核心区"},
        ]
        stats = device_manager.get_stats()
        assert stats["total"] == 3
        assert stats["by_vendor"]["锐捷"] == 2
        assert stats["by_vendor"]["华为"] == 1
        assert stats["by_type"]["核心交换机"] == 1
        assert stats["by_group"]["核心区"] == 2


class TestDeviceManagerExport:
    """测试设备导出功能（parent_widget=None 绕过确认对话框）。"""

    def _make_dm_with_devices(self, project_dir, count=2):
        """创建带有测试设备的 DeviceManager。"""
        dm = DeviceManager()
        dm.set_project(project_dir)
        dm.devices = [
            {
                "ip": f"192.168.1.{i+1}",
                "vendor": "锐捷",
                "device_type": "核心交换机",
                "username": "admin",
                "password": f"pass{i}",
                "protocol": "ssh",
                "enable_password": f"enable{i}",
                "group": "核心区",
                "tags": "核心",
            }
            for i in range(count)
        ]
        return dm

    def test_export_txt_success(self, tmp_dir):
        """TXT 导出应成功创建文件。"""
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "锐捷",
                "device_type": "核心交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "核心", "tags": "标签",
            }
        ]
        path = Path(tmp_dir) / "export.txt"
        result = dm.export_txt(str(path), parent_widget=None)
        assert result is True
        assert path.exists()

    def test_export_txt_contains_warning(self, tmp_dir):
        """TXT 导出应包含安全警告。"""
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "锐捷",
                "device_type": "核心交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "", "tags": "",
            }
        ]
        path = Path(tmp_dir) / "export.txt"
        dm.export_txt(str(path), parent_widget=None)
        content = path.read_text(encoding="utf-8")
        assert "妥善保管" in content

    def test_export_csv_success(self, tmp_dir):
        """CSV 导出应成功创建文件。"""
        import csv
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "华为",
                "device_type": "接入交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "接入", "tags": "标签",
            }
        ]
        path = Path(tmp_dir) / "export.csv"
        result = dm.export_csv(str(path), parent_widget=None)
        assert result is True
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            row = next(reader)
        assert header == DEVICE_HEADERS
        assert row[0] == "192.168.1.1"

    def test_export_empty_devices(self, tmp_dir):
        """空设备列表导出应成功。"""
        dm = DeviceManager()
        dm.devices = []
        path = Path(tmp_dir) / "empty_export.txt"
        result = dm.export_txt(str(path), parent_widget=None)
        assert result is True


class TestDeviceManagerExportErrors:
    """测试设备导出异常处理。"""

    def test_export_txt_exception_returns_false(self, tmp_dir, monkeypatch):
        """TXT 导出异常时应返回 False。"""
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "锐捷",
                "device_type": "核心交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "", "tags": "",
            }
        ]
        monkeypatch.setattr(
            "src.core.device_manager.AtomicFileWriter",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        path = Path(tmp_dir) / "fail.txt"
        result = dm.export_txt(str(path), parent_widget=None)
        assert result is False

    def test_export_csv_exception_returns_false(self, tmp_dir, monkeypatch):
        """CSV 导出异常时应返回 False。"""
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "锐捷",
                "device_type": "核心交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "", "tags": "",
            }
        ]
        monkeypatch.setattr(
            "src.core.device_manager.AtomicFileWriter",
            lambda _exc=Exception("forced"): (_ for _ in ()).throw(_exc)
        )
        path = Path(tmp_dir) / "fail.csv"
        result = dm.export_csv(str(path), parent_widget=None)
        assert result is False

    def test_export_excel_no_pandas_returns_false(self, tmp_dir, monkeypatch):
        """缺少 pandas 时 Excel 导出应返回 False。"""
        import src.core.device_manager as dm_module
        original_import = dm_module.__builtins__ if hasattr(dm_module, '__builtins__') else None
        import builtins
        orig_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pandas":
                raise ImportError("No module named 'pandas'")
            return orig_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        dm = DeviceManager()
        dm.devices = [
            {
                "ip": "192.168.1.1", "vendor": "锐捷",
                "device_type": "核心交换机", "username": "admin",
                "password": "pass", "protocol": "ssh",
                "enable_password": "enable", "group": "", "tags": "",
            }
        ]
        path = Path(tmp_dir) / "fail.xlsx"
        result = dm.export_excel(str(path), parent_widget=None)
        assert result is False

    def test_import_excel_no_pandas_returns_none(self, tmp_dir, monkeypatch):
        """缺少 pandas 时 Excel 导入应返回 None。"""
        import builtins
        orig_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pandas":
                raise ImportError("No module named 'pandas'")
            return orig_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        dm = DeviceManager()
        path = Path(tmp_dir) / "test.xlsx"
        result = dm.import_excel(str(path))
        assert result is None


class TestDeviceManagerImportExcel:
    """测试 Excel 导入功能。"""

    def test_import_excel_returns_none_for_missing_file(self):
        """导入不存在的 Excel 文件应抛出 FileNotFoundError。"""
        dm = DeviceManager()
        with pytest.raises(FileNotFoundError):
            dm.import_excel("/nonexistent/path.xlsx")

    def test_import_excel_with_pandas(self, tmp_dir):
        """有 pandas 时应能导入 Excel 文件。"""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not installed")

        path = Path(tmp_dir) / "test_import.xlsx"
        data = [
            ["192.168.1.1", "锐捷", "核心交换机", "admin",
             "pass", "ssh", "enable", "核心", "标签"],
        ]
        df = pd.DataFrame(data, columns=DEVICE_HEADERS)
        df.to_excel(str(path), index=False, engine="openpyxl")

        dm = DeviceManager()
        devices = dm.import_excel(str(path))
        assert devices is not None
        assert len(devices) == 1
        assert devices[0]["ip"] == "192.168.1.1"


class TestDeviceManagerHistoryFileExists:
    """测试历史记录文件已存在的场景。"""

    def test_record_history_existing_file(self, device_manager):
        """历史文件已存在时应追加记录。"""
        # 先创建历史文件
        history_file = Path(device_manager._history_file())
        history_file.parent.mkdir(parents=True, exist_ok=True)
        history_file.write_text(
            json.dumps({"changes": [{"timestamp": "2024-01-01", "action": "初始", "details": "test", "device_count": 0}]}),
            encoding="utf-8",
        )
        device_manager.record_history("新增", "detail", 1)
        history = device_manager.get_history()
        assert len(history) == 2
        assert history[-1]["action"] == "新增"


class TestDeviceManagerSaveErrors:
    """测试保存异常处理。"""

    def test_save_returns_false_on_write_error(self, device_manager, monkeypatch):
        """写入失败时应返回 False。"""
        monkeypatch.setattr(
            "src.core.device_manager.DeviceFileManager.save_device_list",
            lambda *a, **kw: False
        )
        result = device_manager.save_devices([{
            "ip": "1.1.1.1", "vendor": "锐捷",
            "device_type": "核心交换机", "username": "admin",
            "password": "pass", "protocol": "ssh",
            "enable_password": "enable", "group": "", "tags": "",
        }])
        assert result is False


class TestDeviceManagerConstants:
    """测试常量定义。"""

    def test_vendors_list(self):
        assert "锐捷" in VENDORS
        assert "华为" in VENDORS
        assert "H3C" in VENDORS
        assert "思科" in VENDORS
        assert len(VENDORS) == 4

    def test_device_types_list(self):
        assert "核心交换机" in DEVICE_TYPES
        assert "接入交换机" in DEVICE_TYPES
        assert "路由器" in DEVICE_TYPES
        assert "AC控制器" in DEVICE_TYPES

    def test_protocols_list(self):
        assert "ssh" in PROTOCOLS
        assert "telnet" in PROTOCOLS

    def test_device_headers_count(self):
        assert len(DEVICE_HEADERS) == 9

    def test_device_templates_coverage(self):
        """设备模板应覆盖所有厂商和设备类型组合。"""
        for vendor in VENDORS:
            for dtype in ["核心交换机", "接入交换机", "路由器", "AC控制器"]:
                key = f"{vendor}-{dtype}"
                assert key in DEVICE_TEMPLATES, f"缺少模板: {key}"
