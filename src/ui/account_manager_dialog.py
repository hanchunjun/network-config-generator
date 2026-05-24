#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账户管理弹窗

主界面导航栏「账户管理」按钮触发。
支持修改用户名和密码，密码需满足复杂度要求。
"""

import sys
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox
)

from src.core.account_manager import AccountManager
from src.core.logger import netops_logger


class AccountManagerDialog(QDialog):
    """账户管理弹窗。

    支持修改用户名和密码。
    密码修改需通过复杂度校验（≥8位，含大小写字母+数字）。

    Attributes:
        _account_manager: 账户管理器实例
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._account_manager = AccountManager()
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        """构建账户管理窗口UI。"""
        self.setWindowTitle("账户管理")
        self.setFixedSize(420, 340)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(12)

        # ── 标题 ──
        title_label = QLabel("🔑  账户管理")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #165DFF;")
        layout.addWidget(title_label)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E5E6EB;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # ── 新用户名 ──
        username_label = QLabel("新用户名")
        username_label.setFont(QFont("Microsoft YaHei", 10))
        username_label.setStyleSheet("color: #4E5969;")
        layout.addWidget(username_label)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("请输入新用户名")
        self._username_input.setFont(QFont("Microsoft YaHei", 11))
        self._username_input.setMinimumHeight(36)
        self._username_input.setStyleSheet(
            "QLineEdit {"
            "  border: 1px solid #C9CDD4;"
            "  border-radius: 4px;"
            "  padding: 4px 12px;"
            "  color: #1D2129;"
            "}"
            "QLineEdit:focus { border-color: #165DFF; }"
        )
        # 预填当前用户名
        account = self._account_manager._load_account()
        current_username = account.get("username", "admin")
        self._username_input.setText(current_username)
        layout.addWidget(self._username_input)

        # ── 新密码 ──
        password_label = QLabel("新密码")
        password_label.setFont(QFont("Microsoft YaHei", 10))
        password_label.setStyleSheet("color: #4E5969;")
        layout.addWidget(password_label)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("请输入新密码（≥8位，含大小写字母+数字）")
        self._password_input.setFont(QFont("Microsoft YaHei", 11))
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(36)
        self._password_input.setStyleSheet(
            "QLineEdit {"
            "  border: 1px solid #C9CDD4;"
            "  border-radius: 4px;"
            "  padding: 4px 12px;"
            "  color: #1D2129;"
            "}"
            "QLineEdit:focus { border-color: #165DFF; }"
        )
        layout.addWidget(self._password_input)

        # ── 确认密码 ──
        confirm_label = QLabel("确认密码")
        confirm_label.setFont(QFont("Microsoft YaHei", 10))
        confirm_label.setStyleSheet("color: #4E5969;")
        layout.addWidget(confirm_label)

        self._confirm_input = QLineEdit()
        self._confirm_input.setPlaceholderText("请再次输入新密码")
        self._confirm_input.setFont(QFont("Microsoft YaHei", 11))
        self._confirm_input.setEchoMode(QLineEdit.Password)
        self._confirm_input.setMinimumHeight(36)
        self._confirm_input.setStyleSheet(
            "QLineEdit {"
            "  border: 1px solid #C9CDD4;"
            "  border-radius: 4px;"
            "  padding: 4px 12px;"
            "  color: #1D2129;"
            "}"
            "QLineEdit:focus { border-color: #165DFF; }"
        )
        self._confirm_input.returnPressed.connect(self._on_save)
        layout.addWidget(self._confirm_input)

        layout.addSpacing(4)

        # ── 保存按钮 ──
        save_btn = QPushButton("💾  保存修改")
        save_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        save_btn.setMinimumHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        save_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #00B42A;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover { background-color: #009A29; }"
            "QPushButton:pressed { background-color: #008624; }"
        )
        layout.addWidget(save_btn)

        # ── 底部提示 ──
        tip_label = QLabel("修改后密码加密存储，重启软件生效")
        tip_label.setFont(QFont("Microsoft YaHei", 8))
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("color: #C9CDD4;")
        layout.addWidget(tip_label)

    def _apply_style(self) -> None:
        """应用全局样式。"""
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")

    def _on_save(self) -> None:
        """点击「保存修改」按钮处理。"""
        new_username = self._username_input.text().strip()
        new_password = self._password_input.text()
        confirm_password = self._confirm_input.text()

        if not new_username:
            QMessageBox.warning(self, "输入错误", "用户名不能为空")
            self._username_input.setFocus()
            return

        if not new_password:
            QMessageBox.warning(self, "输入错误", "新密码不能为空")
            self._password_input.setFocus()
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致，请重新输入")
            self._confirm_input.clear()
            self._confirm_input.setFocus()
            return

        # 密码复杂度校验
        is_valid, msg = AccountManager.validate_password_complexity(new_password)
        if not is_valid:
            QMessageBox.warning(self, "密码不符合要求", msg)
            self._password_input.setFocus()
            return

        # 保存
        success, msg = self._account_manager.change_account(new_username, new_password)
        if success:
            netops_logger.get_logger().info(f"账户信息已更新，新用户名: {new_username}")
            QMessageBox.information(self, "修改成功", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "保存失败", msg)


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    dialog = AccountManagerDialog()
    dialog.exec_()
