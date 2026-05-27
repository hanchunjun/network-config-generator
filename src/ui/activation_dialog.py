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
    decode_activation_code,
)
from src.core.logger import netops_logger
from src.core.theme_engine import ThemeEngine


class ActivationDialog(QDialog):
    """软件激活弹窗。

    模态显示，阻塞主程序直到激活成功或用户退出。
    无关闭按钮、无跳过按钮、无试用入口。

    Attributes:
        _activated: 激活是否成功
    """

    def __init__(self, parent=None, trial_mode: bool = False):
        super().__init__(parent)
        self._activated: bool = False
        self._trial_mode: bool = trial_mode
        self._machine_code: str = get_machine_code()
        self._theme = ThemeEngine.get().current_theme
        self._setup_ui()
        self._apply_style()
        ThemeEngine.get().theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        """构建弹窗UI"""
        self.setWindowFlags(
            Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint |
            Qt.MSWindowsFixedSizeDialogHint
        )
        self.setWindowTitle("软件未激活・请完成正版激活")
        self.setFixedSize(580, 560)
        self.setMinimumSize(580, 560)
        self.setMaximumSize(580, 560)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setModal(True)

        t = self._theme
        r = t["radius_md"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)

        # ── 标题 ──
        title_label = QLabel("⚠️  软件未激活")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {t['danger']};")
        layout.addWidget(title_label)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {t['border']};")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # ── 正文说明 ──
        desc_label = QLabel(
            "感谢您使用 NetOps！当前为试用模式，已开放【锐捷接入交换机配置】和"
            "【批量命令生成】两项基础功能。激活后即可解锁全部功能："
            "四厂商全设备配置、批量运维巡检、AI智能诊断等。"
        )
        desc_label.setFont(QFont("Microsoft YaHei", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {t['text_secondary']};")
        layout.addWidget(desc_label)

        # ── 机器码区域 ──
        machine_label = QLabel("【本机设备唯一机器码】")
        machine_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        machine_label.setStyleSheet(f"color: {t['primary_light']}; margin-top: 8px;")
        layout.addWidget(machine_label)

        # 机器码展示 + 复制按钮
        code_layout = QHBoxLayout()
        code_layout.setSpacing(10)

        self._code_display = QLineEdit(self._machine_code)
        self._code_display.setReadOnly(True)
        self._code_display.setFont(QFont("Consolas", 11, QFont.Bold))
        self._code_display.setAlignment(Qt.AlignCenter)
        self._code_display.setMinimumHeight(28)
        self._code_display.setStyleSheet(
            f"QLineEdit {{"
            f"  background-color: {t['code_bg']};"
            f"  border: 1px solid {t['input_border']};"
            f"  border-radius: {r}px;"
            f"  padding: 4px 8px;"
            f"  color: {t['primary_light']};"
            f"}}"
        )
        code_layout.addWidget(self._code_display, stretch=1)

        copy_btn = QPushButton("📋 一键复制")
        copy_btn.setFont(QFont("Microsoft YaHei", 10))
        copy_btn.setFixedSize(110, 30)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(self._copy_machine_code)
        copy_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {t['hover_bg']};"
            f"  color: {t['text_main']};"
            f"  border: 1px solid {t['border']};"
            f"  border-radius: {r}px;"
            f"  padding: 0 16px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {t['card_bg']};"
            f"  border-color: {t['primary']};"
            f"  color: {t['primary']};"
            f"}}"
            f"QPushButton:disabled {{"
            f"  background-color: {t['hover_bg']};"
            f"  border-color: {t['border']};"
            f"  color: {t['text_tertiary']};"
            f"}}"
        )
        code_layout.addWidget(copy_btn)
        layout.addLayout(code_layout)

        # ── 操作指引 ──
        guide_label = QLabel(
            "① 点击「📋一键复制」机器码 → 发送给老韩（QQ:223518 / 微信:tachlaohan）"
            "  ② 收到激活码后填入上方输入框 → 点击「立即激活」"
        )
        guide_label.setFont(QFont("Microsoft YaHei", 10))
        guide_label.setWordWrap(True)
        guide_label.setStyleSheet(f"color: {t['text_tertiary']}; margin-top: 4px;")
        layout.addWidget(guide_label)

        # ── 激活码输入 ──
        act_label = QLabel("激活码：")
        act_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        act_label.setStyleSheet(f"color: {t['text_main']}; margin-top: 8px;")
        layout.addWidget(act_label)

        self._activation_input = QLineEdit()
        self._activation_input.setPlaceholderText("请输入16位或18位激活码")
        self._activation_input.setFont(QFont("Consolas", 12, QFont.Bold))
        self._activation_input.setAlignment(Qt.AlignCenter)
        self._activation_input.setMinimumHeight(28)
        self._activation_input.setMaxLength(18)
        self._activation_input.setStyleSheet(
            f"QLineEdit {{"
            f"  border: 2px solid {t['input_border']};"
            f"  border-radius: {r}px;"
            f"  padding: 4px 8px;"
            f"  background-color: {t['input_bg']};"
            f"  color: {t['text_main']};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {t['primary']}; }}"
        )
        layout.addWidget(self._activation_input)

        # ── 激活按钮 ──
        activate_btn = QPushButton("🔓  立即激活")
        activate_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        activate_btn.setMinimumHeight(28)
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.clicked.connect(self._on_activate)
        activate_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {t['hover_bg']};"
            f"  color: {t['text_main']};"
            f"  border: 1px solid {t['border']};"
            f"  border-radius: {r}px;"
            f"  padding: 5px 8px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {t['card_bg']};"
            f"  border-color: {t['primary']};"
            f"  color: {t['primary']};"
            f"}}"
            f"QPushButton:disabled {{"
            f"  background-color: {t['hover_bg']};"
            f"  border-color: {t['border']};"
            f"  color: {t['text_tertiary']};"
            f"}}"
        )
        layout.addWidget(activate_btn)

        # ── 稍后再说（仅试用模式显示）──
        if self._trial_mode:
            later_btn = QPushButton("稍后再说")
            later_btn.setFont(QFont("Microsoft YaHei", 10))
            later_btn.setMinimumHeight(28)
            later_btn.setCursor(Qt.PointingHandCursor)
            later_btn.clicked.connect(self._on_later)
            later_btn.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: transparent;"
                f"  color: {t['warning']};"
                f"  border: 1px solid {t['warning']};"
                f"  border-radius: {r}px;"
                f"  font-weight: bold;"
                f"  padding: 0 16px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {t['warning_bg']};"
                f"  color: {t['warning_hover']};"
                f"  border-color: {t['warning_hover']};"
                f"}}"
            )
            layout.addWidget(later_btn)

        # ── 温馨须知 ──
        note_label = QLabel(
            "💡 本软件一机一码，换电脑需重新申请。无自助开通渠道，请联系老韩人工办理。"
        )
        note_label.setFont(QFont("Microsoft YaHei", 8))
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {t['text_tertiary']}; margin-top: 4px;")
        layout.addWidget(note_label)

    def _apply_style(self) -> None:
        """应用全局样式"""
        t = self._theme
        self.setStyleSheet(
            f"QDialog {{"
            f"  background-color: {t['card_bg']};"
            f"}}"
        )

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题切换时刷新样式。"""
        self._theme = ThemeEngine.get().current_theme
        self._apply_style()
        self.update()

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

        if len(code) not in (16, 18):
            QMessageBox.warning(self, "提示", "激活码格式不正确，请输入16位或18位激活码")
            return

        if verify_activation_code(code, self._machine_code):
            # 从激活码中解析有效期（支持16位旧格式和18位新格式）
            _base_code, validity_days = decode_activation_code(code)
            if save_license(self._machine_code, code, validity_days=validity_days):
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
                "1. 激活码是否输入正确（16位或18位大写字母+数字）\n"
                "2. 激活码是否与当前设备匹配\n"
                "3. 联系管理员【老韩】确认激活码\n"
                "   QQ：223518  微信：tachlaohan"
            )

    @property
    def activated(self) -> bool:
        """激活是否成功"""
        return self._activated

    def _on_later(self) -> None:
        """稍后再说 — 试用模式下允许关闭弹窗返回主窗口"""
        self._activated = False
        self.reject()

    def closeEvent(self, event) -> None:
        """禁止关闭弹窗（试用模式下允许通过「稍后再说」关闭）"""
        if not self._activated and not self._trial_mode:
            event.ignore()
        else:
            event.accept()

    def keyPressEvent(self, event) -> None:
        """禁止ESC键关闭"""
        if event.key() == Qt.Key_Escape and not self._activated:
            event.ignore()
        else:
            super().keyPressEvent(event)


def show_activation_dialog(parent=None, trial_mode: bool = False) -> bool:
    """显示激活弹窗的便捷函数。

    Args:
        parent: 父窗口
        trial_mode: 是否为试用模式（试用模式下显示「稍后再说」按钮允许关闭）

    Returns:
        bool: 是否激活成功
    """
    dialog = ActivationDialog(parent, trial_mode=trial_mode)
    dialog.exec_()
    return dialog.activated


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    result = show_activation_dialog()
    print(f"激活结果: {result}")
    sys.exit(0 if result else 1)
