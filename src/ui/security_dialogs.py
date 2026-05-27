from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QCheckBox, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt

from src.core.theme_engine import ThemeEngine


class ExportWarningDialog(QDialog):
    """导出安全警告对话框"""

    def __init__(self, parent=None, export_type="txt", device_count=0):
        super().__init__(parent)
        self.export_type = export_type
        self.device_count = device_count
        self._theme_engine = ThemeEngine.get()
        self.init_ui()

    def init_ui(self):
        t = self._theme_engine.current_theme
        self.setWindowTitle("安全警告")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # 警告图标和标题
        title_label = QLabel("⚠️ 导出操作将包含敏感信息")
        title_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {t['text_secondary']};")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 风险说明
        risk_text = QLabel(
            f"您即将导出 {self.device_count} 台设备的配置信息：\n\n"
            "• 密码将以明文形式保存在导出文件中\n"
            "• 导出文件需要严格保管，防止泄露\n"
            "• 建议导出后及时删除临时文件\n"
            "• 仅导出必要的设备信息\n"
            "• 确保导出目录访问权限安全\n\n"
            f"导出格式：{self.export_type.upper()}\n"
            f"包含信息：设备IP、厂商、类型、用户名、密码、特权密码、分组、标签"
        )
        risk_text.setWordWrap(True)
        risk_text.setStyleSheet(f"font-size: 13pt; line-height: 1.6; color: {t['text_main']};")
        layout.addWidget(risk_text)

        # 安全提醒
        reminder_box = QTextEdit()
        reminder_box.setReadOnly(True)
        reminder_box.setMaximumHeight(80)
        reminder_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {t['warning_bg']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                padding: 8px;
                font-size: 12pt;
                color: {t['warning']};
            }}
        """)
        reminder_box.setText(
            "🔐 安全提醒：\n"
            "• 请勿将导出文件发送给未授权人员\n"
            "• 建议对导出文件进行加密存储\n"
            "• 导出完成后及时从临时目录删除"
        )
        layout.addWidget(reminder_box)

        # 安全确认复选框
        self.confirm_checkbox = QCheckBox("我已了解上述安全风险，确认继续导出")
        self.confirm_checkbox.setStyleSheet(f"font-size: 14pt; color: {t['text_secondary']};")
        layout.addWidget(self.confirm_checkbox)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        confirm_btn = QPushButton("确认导出")
        confirm_btn.setFixedSize(120, 30)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                font-weight: bold;
                padding: 6px;
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
        confirm_btn.clicked.connect(self._on_confirm)
        confirm_btn.setEnabled(False)

        self.confirm_checkbox.stateChanged.connect(
            lambda state: confirm_btn.setEnabled(state == Qt.Checked)
        )

        cancel_btn = QPushButton("取消导出")
        cancel_btn.setFixedSize(120, 30)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                font-weight: bold;
                padding: 6px;
            }}
            QPushButton:hover {{ border-color: {t['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _on_confirm(self):
        self.accept()


class PasswordVisibilityDialog(QDialog):
    """密码可见性确认对话框"""

    def __init__(self, parent=None, device_ip=""):
        super().__init__(parent)
        self.device_ip = device_ip
        self._theme_engine = ThemeEngine.get()
        self.init_ui()

    def init_ui(self):
        t = self._theme_engine.current_theme
        self.setWindowTitle("查看密码确认")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 警告信息
        warning_label = QLabel(
            f"您即将查看设备 {self.device_ip} 的密码信息：\n\n"
            "密码将以明文形式显示在界面上。\n"
            "请确保当前环境安全，防止他人窥屏。"
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(f"font-size: 13pt; color: {t['text_main']};")
        layout.addWidget(warning_label)

        # 确认复选框
        self.confirm_checkbox = QCheckBox("当前环境安全，确认查看密码")
        self.confirm_checkbox.setStyleSheet(f"font-size: 14pt; color: {t['text_secondary']};")
        layout.addWidget(self.confirm_checkbox)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        confirm_btn = QPushButton("确认查看")
        confirm_btn.setFixedSize(100, 30)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                padding: 6px;
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
        confirm_btn.clicked.connect(self._on_confirm)
        confirm_btn.setEnabled(False)

        self.confirm_checkbox.stateChanged.connect(
            lambda state: confirm_btn.setEnabled(state == Qt.Checked)
        )

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 30)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                padding: 6px;
            }}
            QPushButton:hover {{ border-color: {t['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _on_confirm(self):
        self.accept()


class DeleteDeviceDialog(QDialog):
    """删除设备确认对话框"""

    def __init__(self, parent=None, device_ip="", device_name=""):
        super().__init__(parent)
        self.device_ip = device_ip
        self.device_name = device_name
        self._theme_engine = ThemeEngine.get()
        self.init_ui()

    def init_ui(self):
        t = self._theme_engine.current_theme
        self.setWindowTitle("确认删除")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 确认信息
        info_label = QLabel(
            f"确认删除以下设备吗？\n\n"
            f"设备IP：{self.device_ip}\n"
            f"设备名称：{self.device_name}\n\n"
            "此操作将永久删除设备信息，无法恢复。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"font-size: 13pt; color: {t['text_main']};")
        layout.addWidget(info_label)

        # 风险提醒
        risk_label = QLabel("⚠️ 删除后相关配置和历史记录也将被清除")
        risk_label.setStyleSheet(f"font-size: 12pt; color: {t['text_secondary']};")
        layout.addWidget(risk_label)

        # 确认复选框
        self.confirm_checkbox = QCheckBox("确认删除此设备")
        self.confirm_checkbox.setStyleSheet(f"font-size: 14pt; color: {t['text_secondary']};")
        layout.addWidget(self.confirm_checkbox)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        confirm_btn = QPushButton("确认删除")
        confirm_btn.setFixedSize(100, 30)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                padding: 6px;
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
        confirm_btn.clicked.connect(self._on_confirm)
        confirm_btn.setEnabled(False)

        self.confirm_checkbox.stateChanged.connect(
            lambda state: confirm_btn.setEnabled(state == Qt.Checked)
        )

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 30)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
                padding: 6px;
            }}
            QPushButton:hover {{ border-color: {t['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _on_confirm(self):
        self.accept()
