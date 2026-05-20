"""validators.py 单元测试 — IP/设备/项目验证器。"""
import pytest
from src.utils.validators import IPValidator, DeviceValidator, ProjectValidator


class TestIPValidator:
    """IP地址验证器测试"""

    @pytest.mark.parametrize("ip", [
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1",
        # 255.255.255.255 是保留地址，不列入有效IP测试
        # "255.255.255.255",
        "0.0.0.0",
    ])
    def test_valid_ip(self, ip):
        valid, err = IPValidator.validate_ip(ip)
        assert valid is True
        assert err is None

    @pytest.mark.parametrize("ip,expected_err_substr", [
        ("", "不能为空"),
        ("abc", "格式不正确"),
        ("192.168.1", "格式不正确"),
        ("192.168.1.1.1", "格式不正确"),
        ("192.168.1.256", "超出范围"),
        ("192.168.01.1", "前导零"),
        ("127.0.0.1", "回环地址"),
        ("224.0.0.1", "组播地址"),
    ])
    def test_invalid_ip(self, ip, expected_err_substr):
        valid, err = IPValidator.validate_ip(ip)
        assert valid is False
        assert expected_err_substr in err


class TestDeviceValidator:
    """设备数据验证器测试"""

    def _make_device(self, **kwargs):
        base = {
            "ip": "192.168.1.100",
            "vendor": "华为",
            "device_type": "核心交换机",
            "username": "admin",
            "password": "test123",
            "protocol": "ssh",
        }
        base.update(kwargs)
        return base

    def test_valid_device(self):
        d = self._make_device()
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is True
        assert err is None

    def test_invalid_ip(self):
        d = self._make_device(ip="999.999.999.999")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False

    def test_invalid_vendor(self):
        d = self._make_device(vendor="迈普")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False
        assert "不在支持列表中" in err

    def test_invalid_device_type(self):
        d = self._make_device(device_type="防火墙墙")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False
        assert "不在支持列表中" in err

    def test_empty_username(self):
        d = self._make_device(username="")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False
        assert "用户名不能为空" in err

    def test_long_username(self):
        d = self._make_device(username="a" * 65)
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False
        assert "不能超过64" in err

    def test_invalid_protocol(self):
        d = self._make_device(protocol="rdp")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is False
        assert "不支持" in err

    def test_duplicate_ip(self):
        d = self._make_device(ip="192.168.1.100")
        valid, err = DeviceValidator.validate_device_data(d, existing_ips=["192.168.1.100"])
        assert valid is False
        assert "已存在" in err

    def test_empty_password_allowed(self):
        """密码为空应允许通过（调用者决定是否确认）"""
        d = self._make_device(password="")
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is True

    @pytest.mark.parametrize("vendor", ["锐捷", "华为", "H3C", "思科"])
    def test_all_vendors(self, vendor):
        d = self._make_device(vendor=vendor)
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is True

    @pytest.mark.parametrize("dtype", [
        "核心交换机", "接入交换机", "路由器", "AC控制器", "防火墙", "负载均衡", "服务器"
    ])
    def test_all_device_types(self, dtype):
        d = self._make_device(device_type=dtype)
        valid, err = DeviceValidator.validate_device_data(d)
        assert valid is True


class TestProjectValidator:
    """项目名称验证器测试"""

    def test_valid_name(self):
        valid, err = ProjectValidator.validate_project_name("政务网核心改造")
        assert valid is True
        assert err is None

    @pytest.mark.parametrize("name,expected_substr", [
        ("", "不能为空"),
        ("a", "至少"),
        ("a" * 51, "不能超过50"),
        ("项目<名称>", "非法字符"),
        ('项目"名称', "非法字符"),
        ("项目/名称", "非法字符"),
        ("项目\\名称", "非法字符"),
        ("项目|名称", "非法字符"),
        ("项目?名称", "非法字符"),
        ("项目*名称", "非法字符"),
    ])
    def test_invalid_name(self, name, expected_substr):
        valid, err = ProjectValidator.validate_project_name(name)
        assert valid is False
        assert expected_substr in err
