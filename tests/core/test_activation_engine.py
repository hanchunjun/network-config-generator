#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活引擎单元测试

覆盖：
- 机器码生成（格式、长度、大写）
- 激活码生成（格式、长度、大写、一致性）
- 激活码校验（正确/错误码）
- 授权文件加密存储与读取
- 启动激活状态校验
- 方案B：180天黑名单校验逻辑
"""

import hashlib
import json
import os
import time
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pytest

from src.core.activation_engine import (
    get_machine_code,
    generate_activation_code,
    verify_activation_code,
    save_license,
    load_license,
    check_activation,
    get_last_check_time,
    set_last_check_time,
    is_due_for_check,
    check_blacklist,
    perform_silent_check,
    LICENSE_FILE,
    BLACKLIST_CHECK_FILE,
    BLACKLIST_URL,
    CHECK_INTERVAL_SECONDS,
    _ACTIVATION_SECRET_KEY,
)


# ─── 机器码生成测试 ───

class TestMachineCode:
    def test_machine_code_length(self):
        """机器码应为32位"""
        code = get_machine_code()
        assert len(code) == 32

    def test_machine_code_uppercase(self):
        """机器码应全部大写"""
        code = get_machine_code()
        assert code == code.upper()

    def test_machine_code_hex_format(self):
        """机器码应为十六进制字符"""
        code = get_machine_code()
        assert all(c in "0123456789ABCDEF" for c in code)

    def test_machine_code_consistency(self):
        """同一设备多次获取机器码应一致"""
        code1 = get_machine_code()
        code2 = get_machine_code()
        assert code1 == code2


# ─── 激活码生成测试 ───

class TestActivationCode:
    def test_activation_code_length(self):
        """激活码应为16位"""
        code = generate_activation_code("A" * 32)
        assert len(code) == 16

    def test_activation_code_uppercase(self):
        """激活码应全部大写"""
        code = generate_activation_code("a" * 32)
        assert code == code.upper()

    def test_activation_code_hex_format(self):
        """激活码应为十六进制字符"""
        code = generate_activation_code("A" * 32)
        assert all(c in "0123456789ABCDEF" for c in code)

    def test_activation_code_deterministic(self):
        """相同机器码应生成相同激活码"""
        mc = "A" * 32
        code1 = generate_activation_code(mc)
        code2 = generate_activation_code(mc)
        assert code1 == code2

    def test_activation_code_different_machine(self):
        """不同机器码应生成不同激活码"""
        code1 = generate_activation_code("A" * 32)
        code2 = generate_activation_code("B" * 32)
        assert code1 != code2

    def test_activation_code_algorithm(self):
        """验证算法：MD5(machine_code + secret) → 前16位大写"""
        mc = "TESTMACHINECODE1234567890123456"
        combined = f"{mc}{_ACTIVATION_SECRET_KEY}"
        expected = hashlib.md5(combined.encode("utf-8")).hexdigest()[:16].upper()
        assert generate_activation_code(mc) == expected


# ─── 激活码校验测试 ───

class TestVerifyActivationCode:
    def test_correct_code(self):
        """正确激活码应校验通过"""
        mc = "A" * 32
        code = generate_activation_code(mc)
        assert verify_activation_code(code, mc) is True

    def test_wrong_code(self):
        """错误激活码应校验失败"""
        mc = "A" * 32
        assert verify_activation_code("WRONGCODE12345678", mc) is False

    def test_empty_code(self):
        """空激活码应校验失败"""
        assert verify_activation_code("", "A" * 32) is False

    def test_case_insensitive_input(self):
        """用户输入小写应自动转大写后校验"""
        mc = "A" * 32
        code = generate_activation_code(mc)
        assert verify_activation_code(code.lower(), mc) is True

    def test_wrong_machine_code(self):
        """机器码不匹配应校验失败"""
        mc1 = "A" * 32
        mc2 = "B" * 32
        code = generate_activation_code(mc1)
        assert verify_activation_code(code, mc2) is False


# ─── 授权文件存储测试 ───

class TestLicenseFile:
    """测试授权文件加密存储与读取"""

    def setup_method(self):
        """每个测试前创建临时目录"""
        self._tmpdir = tempfile.mkdtemp()
        self._license_path = os.path.join(self._tmpdir, "license.dat")

    def teardown_method(self):
        """每个测试后清理临时目录"""
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_save_and_load_license(self):
        """保存后应能正确读取"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        assert save_license(mc, code, license_path=self._license_path) is True

        data = load_license(license_path=self._license_path)
        assert data is not None
        assert data["machine_code"] == mc
        assert data["activation_code"] == code

    def test_load_nonexistent_license(self):
        """无授权文件时应返回None"""
        assert load_license(license_path=self._license_path) is None

    def test_license_file_encrypted(self):
        """授权文件不应包含明文机器码"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        save_license(mc, code, license_path=self._license_path)

        with open(self._license_path, "rb") as f:
            raw = f.read()
        assert mc.encode("utf-8") not in raw

    def test_tampered_license_fails(self):
        """篡改授权文件后读取应失败"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        save_license(mc, code, license_path=self._license_path)

        with open(self._license_path, "rb") as f:
            raw = f.read()
        with open(self._license_path, "wb") as f:
            f.write(raw[:-5] + b"XXXXX")

        assert load_license(license_path=self._license_path) is None


# ─── 启动校验测试 ───

class TestCheckActivation:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self._license_path = os.path.join(self._tmpdir, "license.dat")
        # 通过 patch 让 check_activation 使用临时路径
        self._patcher = patch("src.core.activation_engine.LICENSE_FILE",
                              self._license_path)
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_not_activated(self):
        """无授权文件应返回未激活"""
        active, status, info = check_activation()
        assert active is False
        assert status == "未激活"
        # 未激活时 info 为空字典
        assert isinstance(info, dict)

    def test_activated(self):
        """有效授权应返回已激活"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        save_license(mc, code, license_path=self._license_path)

        active, status, info = check_activation()
        assert active is True
        assert status == "已激活"
        assert info["is_permanent"] is True
        assert info["days_remaining"] == -1

    def test_activated_with_validity(self):
        """有期限授权应返回已激活且剩余天数正确"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        save_license(mc, code, validity_days=365, license_path=self._license_path)

        active, status, info = check_activation()
        assert active is True
        assert status == "已激活"
        assert info["is_permanent"] is False
        assert info["validity_days"] == 365
        assert 360 <= info["days_remaining"] <= 365
        assert info["expire_at"] != ""

    def test_activated_expired(self):
        """已过期授权应返回未激活（授权已过期）"""
        mc = get_machine_code()
        code = generate_activation_code(mc)
        # 保存一个已经过期的授权（回溯到昨天，有效期1天）
        save_license(mc, code, validity_days=1, license_path=self._license_path)
        # 手动修改授权文件中的到期时间为昨天
        from datetime import datetime, timedelta
        import json as _json
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        license_data = load_license(license_path=self._license_path)
        assert license_data is not None
        license_data["expire_at"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        # 重新加密写入
        key_data = None
        try:
            import json as _j
            km_path = os.path.join(os.path.dirname(self._license_path), "key_info.json")
            if not os.path.exists(km_path):
                km_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "key_info.json")
        except Exception:
            pass
        # 直接覆写：用原始加密方式重新写入
        raw_license = _json.dumps(license_data).encode("utf-8")
        # 通过 save_license 的加密路径重新写入——需要先篡改 expire_at
        # 最简单的方式：直接 patch load_license 的返回值
        # 这里改用 patch 方式测试
        with patch("src.core.activation_engine.load_license") as mock_load:
            mock_load.return_value = license_data
            active, status, info = check_activation()
            assert active is False
            assert status == "授权已过期"
            assert info["days_remaining"] == 0
            assert info["is_permanent"] is False

    def test_machine_mismatch(self):
        """机器码不匹配时，授权文件无法解密，应返回未激活"""
        real_mc = get_machine_code()
        fake_mc = "A" * 32
        if fake_mc == real_mc:
            fake_mc = "B" * 32
        code = generate_activation_code(fake_mc)
        # 用假机器码加密保存
        save_license(fake_mc, code, license_path=self._license_path)

        # 真实机器码无法解密假机器码的授权文件 → 返回未激活
        active, status, info = check_activation(license_path=self._license_path)
        assert active is False
        assert status == "未激活"


# ─── 方案B：180天校验测试 ───

class TestBlacklistCheck:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self._bl_path = os.path.join(self._tmpdir, "bl_check.dat")
        self._patcher = patch("src.core.activation_engine.BLACKLIST_CHECK_FILE",
                              self._bl_path)
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_set_and_get_check_time(self):
        """设置和读取校验时间"""
        assert get_last_check_time() is None
        set_last_check_time(1000000)
        assert get_last_check_time() == 1000000

    def test_default_check_time_is_now(self):
        """默认时间应为当前时间附近"""
        set_last_check_time()
        t = get_last_check_time()
        assert t is not None
        assert abs(t - time.time()) < 5

    def test_not_due_when_checked_recently(self):
        """刚校验过不应再触发"""
        set_last_check_time()
        assert is_due_for_check() is False

    def test_due_when_expired(self):
        """超过180天应触发校验"""
        old_time = time.time() - CHECK_INTERVAL_SECONDS - 100
        set_last_check_time(old_time)
        assert is_due_for_check() is True

    def test_due_when_never_checked(self):
        """从未校验过应立即触发"""
        assert is_due_for_check() is True

    def test_check_blacklist_network_failure(self):
        """联网失败应跳过，不判失效"""
        import urllib.request
        with patch.object(urllib.request, "urlopen",
                          side_effect=Exception("网络错误")):
            in_list, msg = check_blacklist()
            assert in_list is False
            assert "联网失败" in msg

    def test_check_blacklist_not_in_list(self):
        """不在黑名单应通过"""
        import urllib.request
        mock_response = MagicMock()
        mock_response.read.return_value = b"OTHERCODE1234567890123456789012\n"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch.object(urllib.request, "urlopen",
                          return_value=mock_response):
            in_list, msg = check_blacklist()
            assert in_list is False
            assert "校验通过" in msg

    def test_check_blacklist_in_list(self):
        """在黑名单应返回封禁"""
        import urllib.request
        real_mc = get_machine_code()
        mock_response = MagicMock()
        mock_response.read.return_value = f"{real_mc}\n".encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch.object(urllib.request, "urlopen",
                          return_value=mock_response):
            in_list, msg = check_blacklist()
            assert in_list is True
            assert "封禁" in msg

    def test_perform_silent_check_not_due(self):
        """未到周期直接通过"""
        set_last_check_time()
        valid, msg = perform_silent_check()
        assert valid is True
        assert "未到校验周期" in msg

    def test_perform_silent_check_network_failure(self):
        """静默校验联网失败应跳过"""
        import urllib.request
        old_time = time.time() - CHECK_INTERVAL_SECONDS - 100
        set_last_check_time(old_time)

        with patch.object(urllib.request, "urlopen",
                          side_effect=Exception("网络错误")):
            valid, msg = perform_silent_check()
            assert valid is True
            assert "联网失败" in msg


# ─── admin_keygen 测试 ───

class TestAdminKeygen:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        import src.core.admin_keygen as ak
        self._orig_records = ak.LICENSE_RECORDS_FILE
        self._orig_bl = ak.BLACKLIST_LOCAL_FILE
        ak.LICENSE_RECORDS_FILE = os.path.join(self._tmpdir, "records.json")
        ak.BLACKLIST_LOCAL_FILE = os.path.join(self._tmpdir, "blacklist.txt")

    def teardown_method(self):
        import src.core.admin_keygen as ak
        ak.LICENSE_RECORDS_FILE = self._orig_records
        ak.BLACKLIST_LOCAL_FILE = self._orig_bl
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_generate_code_matches_engine(self):
        """制码工具生成的激活码前16位应与引擎一致"""
        from src.core.admin_keygen import generate_code_for_machine
        mc = "A" * 32
        code1 = generate_code_for_machine(mc)  # 18位（含2位有效期编码）
        code2 = generate_activation_code(mc)   # 16位基础激活码
        assert code1[:16] == code2
        assert len(code1) == 18  # 新格式为18位

    def test_save_and_load_records(self):
        """台账保存和读取"""
        from src.core.admin_keygen import save_record, load_records
        save_record("测试用户", "A" * 32, "CODE123456789012", "测试备注")
        records = load_records()
        assert len(records) == 1
        assert records[0]["name"] == "测试用户"
        assert records[0]["note"] == "测试备注"

    def test_blacklist_add_remove(self):
        """黑名单添加和移除"""
        from src.core.admin_keygen import (
            add_to_blacklist, remove_from_blacklist, load_blacklist
        )
        mc = "B" * 32
        add_to_blacklist(mc)
        assert mc in load_blacklist()
        remove_from_blacklist(mc)
        assert mc not in load_blacklist()

    def test_save_record_with_validity(self):
        """台账保存含有效期时，expire_at 字段应正确写入"""
        from src.core.admin_keygen import save_record, load_records
        mc = "D" * 32
        code = "VALIDITY12345678"
        save_record("有效期用户", mc, code, "测试5年有效期", validity_days=1825)
        records = load_records()
        assert len(records) == 1
        rec = records[0]
        assert rec["validity_days"] == 1825
        assert rec["expire_at"] != ""
        # 验证到期时间格式正确（YYYY-MM-DD）
        from datetime import datetime
        expire_dt = datetime.strptime(rec["expire_at"], "%Y-%m-%d")
        # 到期时间应在当前时间+1825天附近（误差1天内）
        from datetime import timedelta
        expected = datetime.now() + timedelta(days=1825)
        delta = abs((expire_dt - expected).days)
        assert delta <= 1

    def test_format_record_time(self):
        """format_record_time 应正确格式化时间字符串"""
        from src.core.admin_keygen import format_record_time
        result = format_record_time("2026-05-21 14:30:00")
        assert "2026" in result
        assert "05" in result or "5月" in result

    def test_get_record_expire_status(self):
        """get_record_expire_status 应返回正确的状态描述"""
        from src.core.admin_keygen import get_record_expire_status
        # 永久授权
        rec_permanent = {"validity_days": 0, "expire_at": ""}
        status = get_record_expire_status(rec_permanent)
        assert "永久" in status

    def test_blacklist_duplicate_add(self):
        """重复添加不报错"""
        from src.core.admin_keygen import add_to_blacklist, load_blacklist
        mc = "C" * 32
        add_to_blacklist(mc)
        add_to_blacklist(mc)  # 重复
        codes = load_blacklist()
        assert codes.count(mc) == 1


# ─── machine_code 参数测试（V0.3.7 新增） ─────────────────────────────────

class TestActivationEngineMachineCodeParam:
    """check_activation() machine_code 参数测试。"""

    def test_check_activation_accepts_machine_code_param(self):
        """check_activation() 接受可选 machine_code 参数。"""
        import inspect
        sig = inspect.signature(check_activation)
        assert "machine_code" in sig.parameters

    def test_check_activation_with_mock_machine_code(self):
        """传入 machine_code 参数时，不再调用 get_machine_code()。"""
        with patch("src.core.activation_engine.get_machine_code") as mock_wmic:
            # 传入 machine_code，不应触发 WMIC
            result = check_activation(machine_code="A" * 32)
            mock_wmic.assert_not_called()

    def test_check_activation_without_machine_code_calls_wmic(self):
        """不传 machine_code 时，内部调用 get_machine_code()（向后兼容）。"""
        fake_license = {
            "machine_code": "B" * 32,
            "activated_at": "2026-01-01 00:00:00",
            "validity_days": 0,
            "expire_at": "",
        }
        with patch("src.core.activation_engine.load_license", return_value=fake_license), \
             patch("src.core.activation_engine.get_machine_code",
                   return_value="B" * 32) as mock_wmic:
            result = check_activation()
            mock_wmic.assert_called_once()

    def test_machine_code_param_avoids_duplicate_wmic(self):
        """传入 machine_code 可避免重复 WMIC 调用（优化 1 核心验证）。"""
        fake_license = {
            "machine_code": "A" * 32,
            "activated_at": "2026-01-01 00:00:00",
            "validity_days": 0,
            "expire_at": "",
        }
        with patch("src.core.activation_engine.load_license", return_value=fake_license), \
             patch("src.core.activation_engine.get_machine_code") as mock_wmic:
            # 模拟 main.py 启动链：一次 get_machine_code() → 传给 check_activation()
            code = "A" * 32
            # 传入 machine_code，不再触发 WMIC
            check_activation(machine_code=code)
            mock_wmic.assert_not_called()
