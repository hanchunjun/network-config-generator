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



class DeviceFormDialog(QDialog):
    def __init__(self, parent=None, device: Dict = None):
        super().__init__(parent)
        self.device = device or {}
        self.setWindowTitle("添加设备" if not device else "编辑设备")
        self.setMinimumWidth(480)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        form_group = QGroupBox("设备信息")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("设备IP："))
        self.ip_input = QLineEdit(self.device.get("ip", ""))
        self.ip_input.setPlaceholderText("如：192.168.1.1")
        r1.addWidget(self.ip_input)
        form_layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("厂商："))
        self.vendor_combo = QComboBox()
        self.vendor_combo.addItems(VENDORS)
        if self.device.get("vendor") in VENDORS:
            self.vendor_combo.setCurrentText(self.device["vendor"])
        r2.addWidget(self.vendor_combo)
        r2.addWidget(QLabel("类型："))
        self.type_combo = QComboBox()
        self.type_combo.addItems(DEVICE_TYPES)
        if self.device.get("device_type") in DEVICE_TYPES:
            self.type_combo.setCurrentText(self.device["device_type"])
        r2.addWidget(self.type_combo)
        form_layout.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("协议："))
        self.proto_combo = QComboBox()
        self.proto_combo.addItems(PROTOCOLS)
        if self.device.get("protocol") in PROTOCOLS:
            self.proto_combo.setCurrentText(self.device["protocol"])
        r3.addWidget(self.proto_combo)
        r3.addWidget(QLabel("用户名："))
        self.user_input = QLineEdit(self.device.get("username", ""))
        self.user_input.setPlaceholderText("SSH/Telnet用户名")
        r3.addWidget(self.user_input)
        form_layout.addLayout(r3)

        r4 = QHBoxLayout()
        r4.addWidget(QLabel("密码："))
        self.pwd_input = QLineEdit(self.device.get("password", ""))
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setPlaceholderText("登录密码")
        r4.addWidget(self.pwd_input)
        r4.addWidget(QLabel("特权密码："))
        self.enable_input = QLineEdit(self.device.get("enable_password", ""))
        self.enable_input.setEchoMode(QLineEdit.Password)
        self.enable_input.setPlaceholderText("可选")
        r4.addWidget(self.enable_input)
        form_layout.addLayout(r4)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        t = ThemeEngine.get().current_theme
        radius_md = t['radius_md']
        radius_sm = t['radius_sm']
        style = f"""
            QLabel {{ font-size: 11pt; color: {t['text_secondary']}; }}
            QLineEdit, QComboBox {{
                border: 1px solid {t['border']};
                border-radius: {radius_md}px;
                padding: 4px 8px;
                font-size: 11pt;
                background-color: {t['page_bg']};
            }}
            QLineEdit:focus, QComboBox:focus {{ border-color: {t['border']}; }}
            QGroupBox {{
                font-size: 11pt; font-weight: bold; color: {t['text_main']};
                border: 1px solid {t['border']}; border-radius: {radius_md}px;
                margin-top: 8px; padding: 12px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
            QPushButton {{ padding: 5px 8px; border-radius: {radius_md}px; font-size: 11pt; }}
        """
        self.setStyleSheet(style)

    def get_data(self) -> Optional[Dict]:
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "提示", "请输入设备IP地址")
            return None
        return {
            "ip": ip,
            "vendor": self.vendor_combo.currentText(),
            "device_type": self.type_combo.currentText(),
            "protocol": self.proto_combo.currentText(),
            "username": self.user_input.text().strip(),
            "password": self.pwd_input.text().strip(),
            "enable_password": self.enable_input.text().strip(),
            "last_status": "",
            "last_time": ""
        }
