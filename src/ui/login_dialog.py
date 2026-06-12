#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录认证弹窗

程序启动后、主窗口加载前强制弹出。
无关闭按钮、无跳过按钮，必须成功登录方可进入主界面。
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
from src.core.theme_engine import ThemeEngine


class LoginDialog(QDialog):
    """用户登录弹窗。

    模态显示，阻塞主程序直到登录成功。
    无关闭按钮、无跳过按钮、禁止ESC键关闭。

    Attributes:
        _account_manager: 账户管理器实例
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._account_manager = AccountManager()
        self._theme = ThemeEngine.get().current_theme
        self._setup_ui()
        self._apply_style()
        # 主题切换已取消，信号连接已移除

    def _setup_ui(self) -> None:
        """构建登录窗口UI。"""
        # 窗口属性：无关闭按钮、固定大小
        self.setWindowFlags(
            Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint |
            Qt.MSWindowsFixedSizeDialogHint
        )
        self.setWindowTitle("NetOps 用户登录")
        self.setFixedSize(400, 320)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(10)

        t = self._theme

        # ── 标题 ──
        title_label = QLabel("🔐  用户登录")
        title_label.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {t['text_secondary']};")
        layout.addWidget(title_label)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {t['border']};")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # ── 用户名 ──
        username_label = QLabel("用户名")
        username_label.setFont(QFont("Microsoft YaHei", 10))
        username_label.setStyleSheet(f"color: {t['text_secondary']};")
        layout.addWidget(username_label)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("请输入用户名")
        self._username_input.setFont(QFont("Microsoft YaHei", 11))
        self._username_input.setMinimumHeight(26)
        self._username_input.setStyleSheet(
            f"QLineEdit {{"
            f"  border: 1px solid {t['input_border']};"
            f"  border-radius: {t['radius_md']}px;"
            f"  padding: 4px 8px;"
            f"  background-color: {t['input_bg']};"
            f"  color: {t['text_main']};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {t['border']}; }}"
        )
        layout.addWidget(self._username_input)

        # ── 密码 ──
        password_label = QLabel("密码")
        password_label.setFont(QFont("Microsoft YaHei", 10))
        password_label.setStyleSheet(f"color: {t['text_secondary']};")
        layout.addWidget(password_label)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("请输入密码")
        self._password_input.setFont(QFont("Microsoft YaHei", 11))
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(26)
        self._password_input.setStyleSheet(
            f"QLineEdit {{"
            f"  border: 1px solid {t['input_border']};"
            f"  border-radius: {t['radius_md']}px;"
            f"  padding: 4px 8px;"
            f"  background-color: {t['input_bg']};"
            f"  color: {t['text_main']};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {t['border']}; }}"
        )
        self._password_input.returnPressed.connect(self._on_login)
        layout.addWidget(self._password_input)

        layout.addSpacing(4)

        # ── 登录按钮 ──
        login_btn = QPushButton("登 录")
        login_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        login_btn.setMinimumHeight(36)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._on_login)
        login_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: transparent;"
            f"  color: {t['text_main']};"
            f"  border: 1px solid {t['border']};"
            f"  border-radius: {t['radius_md']}px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: transparent;"
            f"  border-color: {t['border']};"
            f"  color: {t['text_secondary']};"
            f"}}"
            f"QPushButton:disabled {{"
            f"  background-color: transparent;"
            f"  border-color: {t['border']};"
            f"  color: {t['text_tertiary']};"
            f"}}"
        )
        layout.addWidget(login_btn)

        # ── 底部提示 ──
        tip_label = QLabel("默认账户：admin / admin")
        tip_label.setFont(QFont("Microsoft YaHei", 8))
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet(f"color: {t['text_tertiary']};")
        layout.addWidget(tip_label)

    def _apply_style(self) -> None:
        """应用全局样式。"""
        t = self._theme
        self.setStyleSheet(
            f"QDialog {{ background-color: {t['card_bg']}; }}"
            f"QLabel {{ color: {t['text_secondary']}; }}"
        )

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题切换时刷新样式。"""
        self._theme = ThemeEngine.get().current_theme
        self.setStyleSheet(f"QDialog {{ background-color: {self._theme['card_bg']}; }}")
        self._apply_style()
        self.update()

    def _on_login(self) -> None:
        """点击「登录」按钮处理。"""
        username = self._username_input.text().strip()
        password = self._password_input.text()

        if not username:
            QMessageBox.warning(self, "提示", "请输入用户名")
            self._username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "提示", "请输入密码")
            self._password_input.setFocus()
            return

        if self._account_manager.verify_login(username, password):
            netops_logger.get_logger().info(f"用户 [{username}] 登录成功")
            self.accept()
        else:
            netops_logger.get_logger().warning(f"用户 [{username}] 登录失败")
            QMessageBox.warning(self, "登录失败", "用户名或密码不正确，请重新输入")
            self._password_input.clear()
            self._password_input.setFocus()

    def closeEvent(self, event) -> None:
        """禁止关闭弹窗，必须登录才能关闭。"""
        event.ignore()

    def keyPressEvent(self, event) -> None:
        """禁止ESC键关闭弹窗。"""
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    result = dialog.exec_()
    print(f"登录结果: {result}")
    sys.exit(0 if result == QDialog.Accepted else 1)
