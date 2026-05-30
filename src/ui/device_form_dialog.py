import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QComboBox, QPushButton, QFormLayout,
                               QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt

from src.core.device_manager import VENDORS, DEVICE_TYPES, PROTOCOLS
from src.core.logger import netops_logger
from src.core.theme_engine import ThemeEngine
from src.utils.validators import DeviceValidator


class DeviceFormDialog(QDialog):
    def __init__(self, parent=None, device=None, existing_ips=None):
        super().__init__(parent)
        self.device = device
        self.existing_ips = existing_ips or []
        self._theme_engine = ThemeEngine.get()
        self.setWindowTitle("编辑设备" if device else "新增设备")
        self.setMinimumWidth(480)
        self.init_ui()
        if device:
            self._load_device(device)

    def init_ui(self):
        t = self._theme_engine.current_theme
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("新增设备" if not self.device else "编辑设备")
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {t['text_main']};")
        layout.addWidget(title)

        form_group = QGroupBox("设备信息")
        form_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14pt; font-weight: bold; color: {t['text_main']};
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                margin-top: 8px; padding: 12px; background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignRight)

        input_style = f"""
            QLineEdit, QComboBox {{
                border: 1px solid {t['input_border']}; border-radius: {t['radius_md']}px;
                padding: 4px 8px; font-size: 11pt; background-color: {t['card_bg']};
                min-height: 26px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {t['border']};
            }}
            QComboBox::drop-down {{ border: none; }}
        """

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("例如：192.168.1.1")
        self.ip_input.setStyleSheet(input_style)
        form_layout.addRow("IP地址：", self.ip_input)

        self.vendor_combo = QComboBox()
        self.vendor_combo.addItems(VENDORS)
        self.vendor_combo.setStyleSheet(input_style)
        self.vendor_combo.currentTextChanged.connect(self._on_vendor_changed)
        form_layout.addRow("厂商：", self.vendor_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(DEVICE_TYPES)
        self.type_combo.setStyleSheet(input_style)
        form_layout.addRow("设备类型：", self.type_combo)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("SSH/Telnet 用户名")
        self.username_input.setStyleSheet(input_style)
        form_layout.addRow("用户名：", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("登录密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(input_style)
        form_layout.addRow("密码：", self.password_input)

        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(PROTOCOLS)
        self.protocol_combo.setStyleSheet(input_style)
        form_layout.addRow("协议：", self.protocol_combo)

        self.enable_input = QLineEdit()
        self.enable_input.setPlaceholderText("特权模式密码（可选）")
        self.enable_input.setEchoMode(QLineEdit.Password)
        self.enable_input.setStyleSheet(input_style)
        form_layout.addRow("特权密码：", self.enable_input)

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("例如：核心区、接入层、出口区")
        self.group_input.setStyleSheet(input_style)
        form_layout.addRow("分组：", self.group_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("多个标签用逗号分隔，例如：核心,生产")
        self.tags_input.setStyleSheet(input_style)
        form_layout.addRow("标签：", self.tags_input)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(88, 28)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 11pt; color: {t['text_secondary']}; padding: 6px;
            }}
            QPushButton:hover {{ border: 1px solid {t['border']}; color: {t['text_secondary']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(88, 28)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 12pt; padding: 6px;
            }}
            QPushButton:hover {{
                background-color: transparent;
                border-color: {t['border']};
                color: {t['text_secondary']};
            }}
            QPushButton:disabled {{
                background-color: transparent;
                border-color: {t['border']};
                color: {t['text_tertiary']};
            }}
        """)
        save_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _on_vendor_changed(self, vendor):
        pass

    def _load_device(self, device):
        self.ip_input.setText(device.get("ip", ""))
        idx = self.vendor_combo.findText(device.get("vendor", ""))
        if idx >= 0:
            self.vendor_combo.setCurrentIndex(idx)
        idx = self.type_combo.findText(device.get("device_type", ""))
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.username_input.setText(device.get("username", ""))
        self.password_input.setText(device.get("password", ""))
        idx = self.protocol_combo.findText(device.get("protocol", ""))
        if idx >= 0:
            self.protocol_combo.setCurrentIndex(idx)
        self.enable_input.setText(device.get("enable_password", ""))
        self.group_input.setText(device.get("group", ""))
        self.tags_input.setText(device.get("tags", ""))

    def _validate_and_accept(self):
        ip = self.ip_input.text().strip()
        vendor = self.vendor_combo.currentText().strip()
        device_type = self.type_combo.currentText().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        protocol = self.protocol_combo.currentText().strip()
        enable_password = self.enable_input.text()
        group = self.group_input.text().strip()
        tags = self.tags_input.text().strip()

        # 构建设备数据
        device_data = {
            "ip": ip,
            "vendor": vendor,
            "device_type": device_type,
            "username": username,
            "password": password,
            "protocol": protocol,
            "enable_password": enable_password,
            "group": group,
            "tags": tags
        }

        # 验证设备数据
        existing_ips = self.existing_ips if not self.device else [ip for ip in self.existing_ips if ip != self.device.get("ip")]
        is_valid, error = DeviceValidator.validate_device_data(device_data, existing_ips)

        if not is_valid:
            QMessageBox.warning(self, "校验失败", error)
            return

        # 密码为空确认
        if not password:
            reply = QMessageBox.question(self, "确认", "密码为空，确定继续吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        # 记录操作日志
        logger = netops_logger.get_logger()
        if self.device:
            logger.info(f"编辑设备: {ip}")
        else:
            logger.info(f"新增设备: {ip}")

        self.accept()

    def get_device_data(self):
        return {
            "ip": self.ip_input.text().strip(),
            "vendor": self.vendor_combo.currentText().strip(),
            "device_type": self.type_combo.currentText().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "protocol": self.protocol_combo.currentText().strip(),
            "enable_password": self.enable_input.text(),
            "group": self.group_input.text().strip(),
            "tags": self.tags_input.text().strip(),
        }