#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户端激活弹窗

模态弹窗，无关闭按钮、无跳过按钮、无试用入口。
未激活状态下锁定软件全部功能。

定稿文案严格按 .claude/rules/08-activation-plan.md 实现。
"""

import sys
from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy, QMessageBox
)

from src.core.activation_engine import (
    get_machine_code,
    verify_activation_code,
    save_license,
    check_activation,
)
from src.core.logger import netops_logger


class ActivationDialog(QDialog):
    """软件激活弹窗。

    模态显示，阻塞主程序直到激活成功或用户退出。
    无关闭按钮、无跳过按钮、无试用入口。

    Attributes:
        _activated: 激活是否成功
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._activated: bool = False
        self._machine_code: str = get_machine_code()
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        """构建弹窗UI"""
        # 窗口属性：无关闭按钮、固定大小
        self.setWindowFlags(
            Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint
        )
        self.setWindowTitle("软件未激活・请完成正版激活")
        self.setFixedSize(560, 420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)

        # ── 标题 ──
        title_label = QLabel("⚠️  软件未激活")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #E53935;")
        layout.addWidget(title_label)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E0E0E0;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # ── 正文说明 ──
        desc_label = QLabel(
            "当前软件暂未完成授权激活，暂时无法正常使用全部功能。"
        )
        desc_label.setFont(QFont("Microsoft YaHei", 10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #333333;")
        layout.addWidget(desc_label)

        # ── 机器码区域 ──
        machine_label = QLabel("【本机设备唯一机器码】")
        machine_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        machine_label.setStyleSheet("color: #1565C0; margin-top: 8px;")
        layout.addWidget(machine_label)

        # 机器码展示 + 复制按钮
        code_layout = QHBoxLayout()
        code_layout.setSpacing(10)

        self._code_display = QLineEdit(self._machine_code)
        self._code_display.setReadOnly(True)
        self._code_display.setFont(QFont("Consolas", 11, QFont.Bold))
        self._code_display.setAlignment(Qt.AlignCenter)
        self._code_display.setMinimumHeight(38)
        self._code_display.setStyleSheet(
            "QLineEdit {"
            "  background-color: #F5F5F5;"
            "  border: 1px solid #BDBDBD;"
            "  border-radius: 4px;"
            "  padding: 4px 8px;"
            "  color: #212121;"
            "}"
        )
        code_layout.addWidget(self._code_display, stretch=1)

        copy_btn = QPushButton("📋 一键复制")
        copy_btn.setFont(QFont("Microsoft YaHei", 9))
        copy_btn.setFixedSize(110, 38)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(self._copy_machine_code)
        copy_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #1565C0;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover { background-color: #0D47A1; }"
            "QPushButton:pressed { background-color: #0A3680; }"
        )
        code_layout.addWidget(copy_btn)
        layout.addLayout(code_layout)

        # ── 操作指引 ──
        guide_label = QLabel(
            "操作指引：\n"
            "1. 点击「一键复制」完整复制机器码\n"
            "2. 将机器码发送给管理员【天技老韩】申领激活码\n"
            "   QQ：223518  微信：tachlaohan\n"
            "3. 填写管理员发放的激活码，点击「立即激活」"
        )
        guide_label.setFont(QFont("Microsoft YaHei", 9))
        guide_label.setWordWrap(True)
        guide_label.setStyleSheet("color: #555555; margin-top: 4px;")
        layout.addWidget(guide_label)

        # ── 激活码输入 ──
        act_label = QLabel("激活码：")
        act_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        act_label.setStyleSheet("color: #333333; margin-top: 8px;")
        layout.addWidget(act_label)

        self._activation_input = QLineEdit()
        self._activation_input.setPlaceholderText("请输入16位激活码")
        self._activation_input.setFont(QFont("Consolas", 12, QFont.Bold))
        self._activation_input.setAlignment(Qt.AlignCenter)
        self._activation_input.setMinimumHeight(40)
        self._activation_input.setMaxLength(16)
        self._activation_input.setStyleSheet(
            "QLineEdit {"
            "  border: 2px solid #BDBDBD;"
            "  border-radius: 4px;"
            "  padding: 4px 12px;"
            "  color: #212121;"
            "}"
            "QLineEdit:focus { border-color: #1565C0; }"
        )
        layout.addWidget(self._activation_input)

        # ── 激活按钮 ──
        activate_btn = QPushButton("🔓  立即激活")
        activate_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        activate_btn.setMinimumHeight(44)
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.clicked.connect(self._on_activate)
        activate_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #43A047;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover { background-color: #2E7D32; }"
            "QPushButton:pressed { background-color: #1B5E20; }"
        )
        layout.addWidget(activate_btn)

        # ── 温馨须知 ──
        note_label = QLabel(
            "💡 温馨须知：本软件绑定单台设备使用，更换电脑需重新申请激活。"
            "无自助开通、无自助付费通道，全部由管理员人工统一发放权限。"
        )
        note_label.setFont(QFont("Microsoft YaHei", 8))
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #9E9E9E; margin-top: 4px;")
        layout.addWidget(note_label)

    def _apply_style(self) -> None:
        """应用全局样式"""
        self.setStyleSheet(
            "QDialog {"
            "  background-color: #FFFFFF;"
            "}"
        )

    def _copy_machine_code(self) -> None:
        """一键复制机器码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self._machine_code)
        netops_logger.get_logger().info("机器码已复制到剪贴板")

    def _on_activate(self) -> None:
        """点击「立即激活」按钮处理"""
        code = self._activation_input.text().strip().upper()

        if not code:
            QMessageBox.warning(self, "提示", "请输入激活码")
            return

        if len(code) != 16:
            QMessageBox.warning(self, "提示", "激活码格式不正确，请输入16位激活码")
            return

        if verify_activation_code(code, self._machine_code):
            if save_license(self._machine_code, code):
                self._activated = True
                netops_logger.get_logger().info("软件激活成功")
                QMessageBox.information(self, "激活成功", "软件已成功激活，感谢使用！")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "激活信息保存失败，请重试")
        else:
            netops_logger.get_logger().warning(f"激活码校验失败: {code}")
            QMessageBox.warning(
                self, "激活失败",
                "激活码无效，请确认后重试。\n\n"
                "请检查：\n"
                "1. 激活码是否输入正确（16位大写字母+数字）\n"
                "2. 激活码是否与当前设备匹配\n"
                "3. 联系管理员【天技老韩】确认激活码\n"
                "   QQ：223518  微信：tachlaohan"
            )

    @property
    def activated(self) -> bool:
        """激活是否成功"""
        return self._activated

    def closeEvent(self, event) -> None:
        """禁止关闭弹窗（无关闭按钮，此处为二次保险）"""
        if not self._activated:
            event.ignore()
        else:
            event.accept()

    def keyPressEvent(self, event) -> None:
        """禁止ESC键关闭"""
        if event.key() == Qt.Key_Escape and not self._activated:
            event.ignore()
        else:
            super().keyPressEvent(event)


def show_activation_dialog(parent=None) -> bool:
    """显示激活弹窗的便捷函数。

    Args:
        parent: 父窗口

    Returns:
        bool: 是否激活成功
    """
    dialog = ActivationDialog(parent)
    dialog.exec_()
    return dialog.activated


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    result = show_activation_dialog()
    print(f"激活结果: {result}")
    sys.exit(0 if result else 1)
