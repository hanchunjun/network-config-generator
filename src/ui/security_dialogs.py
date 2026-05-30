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
        layout.setSpacing(10)
        layout.setContentsMargins(18, 16, 18, 16)

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
        confirm_btn.setFixedSize(100, 28)
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
        cancel_btn.setFixedSize(88, 28)
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


# NOTE: PasswordVisibilityDialog and DeleteDeviceDialog were removed as dead code.
# They were never referenced by any other module in the project.
# If needed in the future, git history contains the original implementation.
