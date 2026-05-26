#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份/巡检脚本并发执行测试（V0.3.7 新增）

覆盖：
- run_backup() 并发模式返回有序结果
- run_inspect() 并发模式返回有序结果
- max_workers=1 时保持串行行为
- 空设备清单返回提示信息
- 并发异常设备不影响其他设备结果
"""

import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest


class TestBackupConcurrent:
    """backup_all_config.py 并发执行测试。"""

    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        # 创建 device_list.txt
        device_file = os.path.join(self._tmpdir, "config", "device_list.txt")
        os.makedirs(os.path.dirname(device_file), exist_ok=True)
        with open(device_file, "w", encoding="utf-8") as f:
            f.write("192.168.1.1,锐捷,接入交换机,admin,password,ssh,enablepass\n")
            f.write("192.168.1.2,华为,核心交换机,admin,password,ssh,enablepass\n")
            f.write("192.168.1.3,H3C,路由器,admin,password,ssh,enablepass\n")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_concurrent_results_ordered(self):
        """并发执行返回结果顺序与设备清单一致。"""
        from scripts.backup_all_config import run_backup

        def mock_backup(dev_info):
            return f"【{dev_info[0]}】备份完成"

        with patch("scripts.backup_all_config.backup_one_device", side_effect=mock_backup):
            results = run_backup(self._tmpdir, max_workers=3)

        assert len(results) == 3
        assert "192.168.1.1" in results[0]
        assert "192.168.1.2" in results[1]
        assert "192.168.1.3" in results[2]

    def test_serial_mode_max_workers_1(self):
        """max_workers=1 时保持串行行为。"""
        from scripts.backup_all_config import run_backup

        call_order = []

        def mock_backup(dev_info):
            call_order.append(dev_info[0])
            return f"【{dev_info[0]}】备份完成"

        with patch("scripts.backup_all_config.backup_one_device", side_effect=mock_backup):
            results = run_backup(self._tmpdir, max_workers=1)

        assert len(results) == 3
        # 串行模式按顺序执行
        assert call_order == ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

    def test_empty_device_list(self):
        """空设备清单返回提示信息。"""
        from scripts.backup_all_config import run_backup

        # 创建空设备清单
        empty_dir = tempfile.mkdtemp()
        device_file = os.path.join(empty_dir, "config", "device_list.txt")
        os.makedirs(os.path.dirname(device_file), exist_ok=True)
        with open(device_file, "w", encoding="utf-8") as f:
            f.write("")

        results = run_backup(empty_dir)
        assert len(results) == 1
        assert "未读取" in results[0]

        import shutil
        shutil.rmtree(empty_dir, ignore_errors=True)

    def test_concurrent_with_exception(self):
        """某设备异常不影响其他设备结果。"""
        from scripts.backup_all_config import run_backup

        def mock_backup(dev_info):
            if dev_info[0] == "192.168.1.2":
                raise Exception("连接超时")
            return f"【{dev_info[0]}】备份完成"

        with patch("scripts.backup_all_config.backup_one_device", side_effect=mock_backup):
            results = run_backup(self._tmpdir, max_workers=3)

        assert len(results) == 3
        # 第一台和第三台正常
        assert "备份完成" in results[0]
        assert "备份完成" in results[2]
        # 第二台异常
        assert "备份异常" in results[1] or "连接超时" in results[1]

    def test_progress_callback_called(self):
        """进度回调在并发模式下被正确调用。"""
        from scripts.backup_all_config import run_backup

        progress_calls = []

        def mock_backup(dev_info):
            return f"【{dev_info[0]}】备份完成"

        def progress_cb(completed, total, message):
            progress_calls.append((completed, total, message))

        with patch("scripts.backup_all_config.backup_one_device", side_effect=mock_backup):
            run_backup(self._tmpdir, progress_callback=progress_cb, max_workers=3)

        # 应有 3 次中间进度 + 1 次完成回调
        assert len(progress_calls) == 4
        # 最后一次是完成回调
        assert progress_calls[-1][0] == progress_calls[-1][1]  # completed == total


class TestInspectConcurrent:
    """network_inspect.py 并发执行测试。"""

    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        device_file = os.path.join(self._tmpdir, "config", "device_list.txt")
        os.makedirs(os.path.dirname(device_file), exist_ok=True)
        with open(device_file, "w", encoding="utf-8") as f:
            f.write("192.168.1.1,锐捷,接入交换机,admin,password,ssh,enablepass\n")
            f.write("192.168.1.2,华为,核心交换机,admin,password,ssh,enablepass\n")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_concurrent_inspect_results_ordered(self):
        """并发巡检返回结果顺序与设备清单一致。"""
        from scripts.network_inspect import run_inspect

        def mock_inspect(dev_info, progress_cb=None):
            return f"【{dev_info[0]}】巡检完成"

        with patch("scripts.network_inspect.device_inspect", side_effect=mock_inspect):
            results = run_inspect(self._tmpdir, max_workers=2)

        assert len(results) == 2
        assert "192.168.1.1" in results[0]
        assert "192.168.1.2" in results[1]

    def test_empty_device_list_inspect(self):
        """空设备清单返回提示信息。"""
        from scripts.network_inspect import run_inspect

        empty_dir = tempfile.mkdtemp()
        device_file = os.path.join(empty_dir, "config", "device_list.txt")
        os.makedirs(os.path.dirname(device_file), exist_ok=True)
        with open(device_file, "w", encoding="utf-8") as f:
            f.write("")

        results = run_inspect(empty_dir)
        assert len(results) == 1
        assert "未读取" in results[0]

        import shutil
        shutil.rmtree(empty_dir, ignore_errors=True)
