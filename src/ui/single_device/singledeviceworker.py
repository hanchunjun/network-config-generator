import os
import sys
import json
import time
import glob as glob_mod
import ssl
import socket
import subprocess
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
import certifi
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QTextEdit, QMessageBox, QProgressBar,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QDialogButtonBox, QCheckBox, QMenu,
                               QAction, QAbstractItemView, QTabWidget,
                               QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

from src.utils.resource_path import resource_path, get_app_dir, get_config_path, get_single_dir
from src.core.secure_config import SecureConfigFile
from src.core.local_audit_engine import LocalAuditEngine, AuditResult, Severity
from src.core.local_diagnostic_engine import LocalDiagnosticEngine, DiagResult, DiagSeverity
from src.core.theme_engine import ThemeEngine
from src.ui.system_settings_page import get_active_ai_config

SCRIPTS_DIR = resource_path("scripts")
sys.path.insert(0, SCRIPTS_DIR)

AI_CONFIG_PATH = get_config_path("config/ai_config.json")
SINGLE_DEVICES_PATH = os.path.join(get_single_dir(), "single_devices.json")

VENDORS = ["锐捷", "华为", "H3C", "思科"]
DEVICE_TYPES = ["核心交换机", "汇聚交换机", "接入交换机", "路由器", "防火墙", "AC控制器", "AP"]
PROTOCOLS = ["ssh", "telnet"]

DEV_TYPE_MAP = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

TEST_CMD_MAP = {
    "锐捷": ["show version", "show clock"],
    "华为": ["display version", "display clock"],
    "H3C": ["display version", "display clock"],
    "思科": ["show version", "show clock"]
}

INSPECT_EXCEPTION_KEYS = [
    "Down", "Error", "Warning", "CPU", "内存", "过载", "告警", "故障",
    "CRC", "reset", "spanning-tree", "邻居", "会话"
]

INSPECT_TYPE_NORMALIZE = {
    "核心交换机": "交换机", "汇聚交换机": "交换机", "接入交换机": "交换机",
    "交换机": "交换机", "路由器": "路由器", "防火墙": "交换机",
    "AC控制器": "交换机", "AP": "交换机",
}

INSPECT_DEFAULT_CMDS = ["show version", "show ip interface brief", "show cpu", "show memory"]

INSPECT_BASE_CMD_LIB: Dict[str, Dict[str, List[str]]] = {
    "锐捷": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip route", "show cpu", "show memory", "show logging"]
    },
    "华为": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "H3C": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "思科": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip interface brief", "show ip route", "show cpu", "show memory", "show logging"]
    }
}

FULL_CONFIG_CMD_MAP: Dict[str, str] = {
    "锐捷": "show running-config",
    "华为": "display current-configuration",
    "H3C": "display current-configuration",
    "思科": "show running-config"
}

STATUS_ICONS = {"success": "✅", "failed": "❌", "pending": "⚪"}
TAB_LOG = 0
TAB_BACKUP = 1
TAB_REPORT = 2
TAB_DIAGNOSIS = 3
TAB_COMPLIANCE = 4

COMPLIANCE_PROMPT = """{reviewer_rules}

---
设备IP: {device_ip}
配置:
{config_content}
"""

COMPLIANCE_API_TIMEOUT = 120
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 10]
MAX_RULES_LENGTH = 2000

RATE_LIMIT_MAX_RETRIES = 3
RATE_LIMIT_BACKOFF_BASE = 30
PROBE_TIMEOUT = 15



class SingleDeviceWorker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int, str, str)
    error_signal = pyqtSignal(int, str)
    batch_progress = pyqtSignal(int, int)

    def __init__(self, task_type: str, devices: List[Dict], row_indices: List[int] = None):
        super().__init__()
        self.task_type = task_type
        self.devices = devices
        self.row_indices = row_indices or list(range(len(devices)))
        self._cancelled = False

    def run(self):
        total = len(self.devices)
        for idx, dev in enumerate(self.devices):
            if self._cancelled:
                break
            row_idx = self.row_indices[idx] if idx < len(self.row_indices) else idx
            try:
                if self.task_type == "inspect":
                    self._do_inspect(dev, row_idx, idx, total)

                elif self.task_type == "backup":
                    self._do_backup(dev, row_idx, idx, total)

                elif self.task_type == "test_connect":
                    self._do_test_connection(dev, row_idx)

            except ImportError as e:
                self.error_signal.emit(row_idx, f"模块导入失败：{str(e)}")
            except Exception as e:
                self.error_signal.emit(row_idx, str(e))

            self.batch_progress.emit(idx + 1, total)

    @staticmethod
    def _is_permission_error(e: Exception) -> bool:
        if isinstance(e, OSError) and e.errno == 10013:
            return True
        err_str = str(e)
        return "10013" in err_str or "access" in err_str.lower() and "socket" in err_str.lower()

    def _build_conn_params(self, dev: Dict) -> Dict:
        ip = dev["ip"]
        proto = dev.get("protocol", "ssh")
        vendor = dev.get("vendor", "锐捷")
        dev_type = DEV_TYPE_MAP.get(vendor, "cisco_ios")
        return {
            "device_type": dev_type,
            "host": ip,
            "username": dev["username"],
            "password": dev["password"],
            "secret": dev.get("enable_password", ""),
            "timeout": 120,
            "conn_timeout": 30,
            "auth_timeout": 60,
            "banner_timeout": 60,
            "allow_auto_change": True,
            "global_delay_factor": 2 if vendor == "锐捷" else 1,
            "port": 22 if proto == "ssh" else 23,
            "keepalive": 30,
        }

    def _do_backup(self, dev: Dict, row_idx: int, idx: int, total: int):
        from netmiko import ConnectHandler
        from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = dev["device_type"]
        proto = dev.get("protocol", "ssh")
        port = 22 if proto == "ssh" else 23

        config_cmd = FULL_CONFIG_CMD_MAP.get(vendor, "show running-config")

        required_fields = ["ip", "vendor", "device_type", "username", "password", "protocol"]
        missing = [f for f in required_fields if not dev.get(f)]
        if missing:
            self.error_signal.emit(row_idx, f"备份参数缺失: {', '.join(missing)}")
            return

        conn_params = self._build_conn_params(dev)

        self.progress_signal.emit(f"[{idx+1}/{total}] 开始备份 {ip} ...")
        self.progress_signal.emit(f"连接参数: device_type={conn_params['device_type']}, host={ip}, port={port}")

        base_dir = get_single_dir()
        backup_dir = os.path.join(base_dir, "config_backup")
        safe_dev_mod = "".join(c for c in device_type if c.isalnum() or c in '._-')

        max_retries = 3
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    delay = attempt * 2
                    self.progress_signal.emit(f"第{attempt}次: 等待{delay}s后重试...")
                    time.sleep(delay)

                self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")
                with ConnectHandler(**conn_params) as conn:
                    try:
                        conn.enable()
                    except Exception:
                        pass
                    config = conn.send_command(config_cmd)

                if not config or len(config) < 100:
                    self.finished_signal.emit(row_idx, f"【{ip}】配置获取失败，配置过短", "")
                    return

                os.makedirs(backup_dir, exist_ok=True)
                file_name = f"{safe_dev_mod}_{ip}_配置备份.txt"
                file_path = os.path.join(backup_dir, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"【设备厂商】：{vendor}\n")
                    f.write(f"【设备类型】：{device_type}\n")
                    f.write(f"【设备IP】：{ip}\n")
                    f.write(f"配置备份时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(config)

                hint = f"\n📁 备份目录：{backup_dir}"
                if attempt > 1:
                    self.finished_signal.emit(row_idx, f"【{ip}】第{attempt}次重试后备份成功", hint)
                else:
                    self.finished_signal.emit(row_idx, f"【{ip}】配置备份成功", hint)
                return

            except NetmikoAuthenticationException as e:
                last_err = f"认证失败: {str(e)}"
                self.progress_signal.emit(f"SSH认证: {last_err}")
            except (NetmikoTimeoutException, socket.timeout) as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"SSH超时: {last_err}")
            except socket.gaierror as e:
                last_err = f"DNS解析失败: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except ConnectionRefusedError as e:
                last_err = f"端口被拒绝: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except OSError as e:
                if self._is_permission_error(e):
                    last_err = "系统权限被拒绝(WinError 10013)\n⚠️ 可能原因：杀毒软件/防火墙拦截了程序的网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到杀毒软件白名单"
                    self.progress_signal.emit(f"权限错误: {last_err}")
                else:
                    last_err = f"OSError({e.errno}): {str(e)}"
                    self.progress_signal.emit(f"OS错误: {last_err}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"异常: {last_err}")

            if attempt < max_retries:
                self.progress_signal.emit(f"第{attempt}次失败，准备重试...")
                continue
            self.finished_signal.emit(row_idx, f"【{ip}】备份失败（已重试{max_retries}次）\n详情：{last_err}", "")
            return

    def _do_inspect(self, dev: Dict, row_idx: int, idx: int, total: int):
        from netmiko import ConnectHandler
        from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = dev["device_type"]
        proto = dev.get("protocol", "ssh")
        port = 22 if proto == "ssh" else 23

        if vendor not in DEV_TYPE_MAP:
            self.finished_signal.emit(row_idx, f"【{ip}】暂不支持该厂商适配", "")
            return

        normalized_type = INSPECT_TYPE_NORMALIZE.get(device_type, "交换机")
        cmd_list = INSPECT_BASE_CMD_LIB.get(vendor, {}).get(normalized_type, INSPECT_DEFAULT_CMDS)

        conn_params = self._build_conn_params(dev)

        self.progress_signal.emit(f"[{idx+1}/{total}] 开始巡检 {ip} ...")
        self.progress_signal.emit(f"连接参数: device_type={conn_params['device_type']}, host={ip}, port={port}")
        inspect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        base_dir = get_single_dir()

        max_retries = 3
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    delay = attempt * 2
                    self.progress_signal.emit(f"第{attempt}次: 等待{delay}s后重试...")
                    time.sleep(delay)

                self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")
                with ConnectHandler(**conn_params) as conn:
                    try:
                        conn.enable()
                    except Exception:
                        pass
                    res = ""
                    for cmd in cmd_list:
                        res += f"\n===== {cmd} =====\n"
                        try:
                            output = conn.send_command(cmd)
                            res += output if output.strip() else "(无输出)"
                        except Exception:
                            res += "(命令执行失败)"

                    err_flag = False
                    for key in INSPECT_EXCEPTION_KEYS:
                        if key in res:
                            err_flag = True
                            break

                    full_config_cmd = FULL_CONFIG_CMD_MAP.get(vendor, "")
                    if err_flag and full_config_cmd:
                        try:
                            res += f"\n\n===== 故障设备抓取完整运行配置 =====\n"
                            res += conn.send_command(full_config_cmd)
                        except Exception:
                            res += "(配置抓取失败)"

                status_line = "\u26a0\ufe0f 发现异常" if err_flag else "\u2705 巡检正常"

                full_report = (
                    f"===== 设备巡检报告 =====\n"
                    f"【设备IP】：{ip}\n"
                    f"【厂商】：{vendor}\n"
                    f"【设备类型】：{device_type}\n"
                    f"【巡检时间】：{inspect_time}\n"
                    f"【执行命令数】：{len(cmd_list)}\n"
                    f"{res}\n\n"
                    f"===== 巡检状态 =====\n"
                    f"{status_line}\n"
                )

                report_dir = os.path.join(base_dir, "report", "single_inspect")
                os.makedirs(report_dir, exist_ok=True)
                safe_ip = ip.replace(".", "_")
                report_name = f"{safe_ip}_{inspect_time.replace(':', '').replace(' ', '_')}_巡检报告.txt"
                report_path = os.path.join(report_dir, report_name)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(full_report)

                if err_flag:
                    exc_dir = os.path.join(base_dir, "output", "single_exception")
                    os.makedirs(exc_dir, exist_ok=True)
                    exc_name = f"{device_type}_{ip}_异常.txt"
                    exc_path = os.path.join(exc_dir, exc_name)
                    with open(exc_path, "w", encoding="utf-8") as f:
                        f.write(f"【设备厂商】：{vendor}\n")
                        f.write(f"【设备类型】：{device_type}\n")
                        f.write(f"【设备IP】：{ip}\n")
                        f.write(f"【巡检时间】：{inspect_time}\n\n")
                        f.write(full_report)

                hint = f"\n📄 报告已保存至：single/report/single_inspect/"
                if attempt > 1:
                    self.finished_signal.emit(row_idx, f"【{ip}】第{attempt}次重试后巡检成功\n{full_report}", hint)
                else:
                    self.finished_signal.emit(row_idx, full_report, hint)
                return

            except NetmikoAuthenticationException as e:
                last_err = f"认证失败: {str(e)}"
                self.progress_signal.emit(f"SSH认证: {last_err}")
            except (NetmikoTimeoutException, socket.timeout) as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"SSH超时: {last_err}")
            except socket.gaierror as e:
                last_err = f"DNS解析失败: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except ConnectionRefusedError as e:
                last_err = f"端口被拒绝: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except OSError as e:
                if self._is_permission_error(e):
                    last_err = "系统权限被拒绝(WinError 10013)\n⚠️ 可能原因：杀毒软件/防火墙拦截了程序的网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到杀毒软件白名单"
                    self.progress_signal.emit(f"权限错误: {last_err}")
                else:
                    last_err = f"OSError({e.errno}): {str(e)}"
                    self.progress_signal.emit(f"OS错误: {last_err}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"异常: {last_err}")

            if attempt < max_retries:
                self.progress_signal.emit(f"第{attempt}次失败，准备重试...")
                continue
            self.finished_signal.emit(row_idx, f"【{ip}】巡检失败（已重试{max_retries}次）\n详情：{last_err}", "")
            return

    def _do_test_connection(self, dev: Dict, row_idx: int):
        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = DEV_TYPE_MAP.get(vendor, "cisco_ios")

        self.progress_signal.emit(f"正在Ping {ip} ...")
        try:
            count_param = "-n" if os.name == "nt" else "-c"
            timeout_param = "-w" if os.name == "nt" else "-W"
            timeout_val = "2000" if os.name == "nt" else "2"
            subprocess.run(
                ["ping", count_param, "1", timeout_param, timeout_val, str(ip)],
                capture_output=True, text=True, timeout=5
            )
            ping_ok = True
        except Exception:
            ping_ok = False

        if not ping_ok:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"【测试时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"🔴 连接失败：设备不可达\n"
                f"原因：Ping超时，设备无响应\n\n"
                f"========== 测试结束 ==========", "")
            return

        self.progress_signal.emit(f"Ping成功，正在尝试{vendor}登录 ...")

        try:
            from netmiko import ConnectHandler
            from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

            conn_params = self._build_conn_params(dev)
            proto = dev.get("protocol", "ssh")
            port = 22 if proto == "ssh" else 23

            self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")

            start = datetime.now()
            with ConnectHandler(**conn_params) as conn:
                try:
                    conn.enable()
                except Exception:
                    pass
                ver_output = ""
                test_cmds = TEST_CMD_MAP.get(vendor, ["show version"])
                for cmd in test_cmds:
                    try:
                        out = conn.send_command(cmd)
                        ver_output += f"\n----- {cmd} -----\n{out}\n" if out.strip() else ""
                    except Exception:
                        pass

                elapsed = (datetime.now() - start).total_seconds()

                report = (
                    f"========== 连接测试报告 ==========\n"
                    f"【设备IP】：{ip}\n"
                    f"【厂商】：{vendor}\n"
                    f"【设备类型】：{dev['device_type']}\n"
                    f"【测试时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"【总耗时】：{elapsed:.1f}秒\n"
                    f"🟢 登录认证：成功\n"
                    f"{ver_output}\n"
                    f"========== 测试结束 =========="
                )
                self.finished_signal.emit(row_idx, report, "")

        except NetmikoAuthenticationException:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 网络可达，但登录失败\n"
                f"原因：账号密码认证错误\n"
                f"========== 测试结束 ==========", "")
        except NetmikoTimeoutException:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接超时\n"
                f"原因：SSH协议握手超时或被拒绝\n"
                f"========== 测试结束 ==========", "")
        except socket.timeout:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接超时\n"
                f"原因：TCP/SSH层超时\n"
                f"========== 测试结束 ==========", "")
        except OSError as e:
            if self._is_permission_error(e):
                reason = "系统权限被拒绝(WinError 10013)\n⚠️ 杀毒软件/防火墙可能拦截了程序网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到白名单"
            else:
                err_msg = str(e)
                if "10061" in err_msg or "refused" in err_msg.lower():
                    reason = "SSH端口被拒绝（可能未开启或防火墙拦截）"
                elif "10060" in err_msg or "timed out" in err_msg.lower():
                    reason = "连接超时（网络不通或设备无响应）"
                else:
                    reason = f"网络异常: {err_msg}"
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接失败\n"
                f"原因：{reason}\n"
                f"========== 测试结束 ==========", "")
        except Exception as e:
            self.error_signal.emit(row_idx, f"测试连接异常：{str(e)}")

    def cancel(self):
        self._cancelled = True
