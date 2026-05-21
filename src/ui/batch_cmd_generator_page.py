#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量命令生成器
支持模板+参数(%a~%e)→批量生成配置命令
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QGroupBox, QTextEdit, QScrollArea,
    QApplication, QGridLayout, QFileDialog,
    QMessageBox, QWidget as QW
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ParamGroupWidget(QGroupBox):
    def __init__(self, label: str, param_char: str, parent=None):
        super().__init__(f"参数{label}:", parent)
        self.param_char = param_char
        self.setStyleSheet(
            "QGroupBox {"
            "  font-size: 12px; font-weight: bold; color: #1D2129;"
            "  border: 1px solid #C9CDD4; border-radius: 6px;"
            "  margin-top: 8px; padding-top: 10px;"
            "}"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }"
        )
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 8)
        layout.setSpacing(5)

        row = 0
        layout.addWidget(QLabel("基数:"), row, 0)
        self.base_spin = QSpinBox()
        self.base_spin.setRange(0, 99999)
        self.base_spin.setValue(0)
        self.base_spin.setMinimumHeight(24)
        self.base_spin.setMinimumWidth(50)
        layout.addWidget(self.base_spin, row, 1)

        layout.addWidget(QLabel("步长:"), row, 2)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(-99999, 99999)
        self.step_spin.setValue(1)
        self.step_spin.setMinimumHeight(24)
        self.step_spin.setMinimumWidth(50)
        layout.addWidget(self.step_spin, row, 3)

        row = 1
        self.repeat_cb = QCheckBox("重复次数:")
        layout.addWidget(self.repeat_cb, row, 0, 1, 2)
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 9999)
        self.repeat_spin.setValue(8)
        self.repeat_spin.setEnabled(False)
        self.repeat_spin.setMinimumHeight(24)
        self.repeat_spin.setMinimumWidth(48)
        layout.addWidget(self.repeat_spin, row, 2, 1, 2)

        row = 2
        self.loop_cb = QCheckBox("循环个数:")
        layout.addWidget(self.loop_cb, row, 0, 1, 2)
        self.loop_spin = QSpinBox()
        self.loop_spin.setRange(1, 9999)
        self.loop_spin.setValue(24)
        self.loop_spin.setEnabled(False)
        self.loop_spin.setMinimumHeight(24)
        self.loop_spin.setMinimumWidth(48)
        layout.addWidget(self.loop_spin, row, 2, 1, 2)

        self.repeat_cb.toggled.connect(self.repeat_spin.setEnabled)
        self.loop_cb.toggled.connect(self.loop_spin.setEnabled)

    def get_config(self) -> dict:
        return {
            "char": self.param_char,
            "base": self.base_spin.value(),
            "step": self.step_spin.value(),
            "repeat": self.repeat_spin.value() if self.repeat_cb.isChecked() else None,
            "loop": self.loop_spin.value() if self.loop_cb.isChecked() else None,
        }


class BatchCmdGeneratorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self._param_widgets: List[ParamGroupWidget] = []
        self._setup_ui()
        self._apply_style()
        self._bind_events()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 8)
        main_layout.setSpacing(10)

        template_group = QGroupBox("命令模板")
        template_group.setStyleSheet(self._group_style())
        template_layout = QVBoxLayout(template_group)
        template_layout.setContentsMargins(16, 10, 16, 10)
        template_layout.setSpacing(6)

        hint_lbl = QLabel("请输入命令模板，参数格式为：%a ~ %f")
        hint_lbl.setStyleSheet("font-size: 11px; color: #86909C;")
        template_layout.addWidget(hint_lbl)

        self.template_edit = QTextEdit()
        self.template_edit.setPlaceholderText(
            "在此输入命令模板...\n\n示例:\n"
            "vlan %a\n"
            " name AP_%a\n\n"
            "%a=第1个参数, %b=第2个参数, ... %f=第6个参数"
        )
        self.template_edit.setMinimumHeight(110)
        self.template_edit.setFont(QFont("Consolas", 11))
        template_layout.addWidget(self.template_edit)

        main_layout.addWidget(template_group)

        param_group = QGroupBox("参数设置")
        param_group.setStyleSheet(self._group_style())
        param_outer_layout = QVBoxLayout(param_group)
        param_outer_layout.setContentsMargins(8, 8, 8, 6)
        param_outer_layout.setSpacing(6)

        param_container = QW()
        param_container.setLayout(QHBoxLayout())
        param_container.layout().setContentsMargins(0, 0, 0, 0)
        param_container.layout().setSpacing(4)

        for i, char in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
            pw = ParamGroupWidget(label=str(i + 1), param_char=char)
            self._param_widgets.append(pw)
            param_container.layout().addWidget(pw)

        param_scroll = QScrollArea()
        param_scroll.setWidget(param_container)
        param_scroll.setWidgetResizable(True)
        param_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        param_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        param_scroll.setMinimumHeight(145)
        param_scroll.setMaximumHeight(175)
        param_outer_layout.addWidget(param_scroll)

        main_layout.addWidget(param_group)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        action_row.addWidget(QLabel("命令数量:"))
        self.cmd_count_spin = QSpinBox()
        self.cmd_count_spin.setRange(1, 999999)
        self.cmd_count_spin.setValue(48)
        self.cmd_count_spin.setMinimumHeight(30)
        self.cmd_count_spin.setMinimumWidth(75)
        action_row.addWidget(self.cmd_count_spin)

        btn_gen = QPushButton("生成命令")
        btn_gen.setObjectName("genBtn")
        btn_gen.setCursor(Qt.PointingHandCursor)
        btn_gen.setMinimumHeight(32)
        btn_gen.setMinimumWidth(85)
        action_row.addWidget(btn_gen)

        btn_save = QPushButton("保存结果")
        btn_save.setObjectName("saveBtn")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setMinimumHeight(32)
        btn_save.setMinimumWidth(85)
        action_row.addWidget(btn_save)

        btn_copy = QPushButton("复制全部")
        btn_copy.setObjectName("copyBtn")
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setMinimumHeight(32)
        btn_copy.setMinimumWidth(85)
        action_row.addWidget(btn_copy)

        btn_clear = QPushButton("清空")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setMinimumHeight(32)
        btn_clear.setMinimumWidth(65)
        action_row.addWidget(btn_clear)

        action_row.addStretch()
        main_layout.addLayout(action_row)

        self.output_edit = QTextEdit()
        self.output_edit.setFont(QFont("Consolas", 11))
        self.output_edit.setMinimumHeight(220)
        main_layout.addWidget(self.output_edit)

        status_bar = QLabel("  0 %")
        status_bar.setAlignment(Qt.AlignCenter)
        status_bar.setStyleSheet(
            "background-color: #F2F3F5; color: #86909C; font-size: 11px;"
            "border: 1px solid #E5E6EB; padding: 3px;"
        )
        status_bar.setMinimumHeight(24)
        main_layout.addWidget(status_bar)
        self._status_label = status_bar

    def _group_style(self):
        return (
            "QGroupBox {"
            "  font-size: 13px; font-weight: bold; color: #1D2129;"
            "  border: 1px solid #E5E6EB; border-radius: 6px;"
            "  margin-top: 8px; padding-top: 8px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin; left: 12px; padding: 0 6px;"
            "}"
        )

    def _apply_style(self):
        self.setStyleSheet(
            "QTextEdit {"
            "  border: 1px solid #C9CDD4; border-radius: 4px; padding: 6px;"
            "  background: white; font-size: 13px;"
            "}"
            "QTextEdit:focus { border-color: #165DFF; }"
            "QSpinBox {"
            "  border: 1px solid #C9CDD4; border-radius: 4px; padding: 2px 6px;"
            "  background: white;"
            "}"
            "QSpinBox:focus { border-color: #165DFF; }"
            "QPushButton#genBtn {"
            "  background-color: #165DFF; color: white; border: none;"
            "  border-radius: 4px; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton#genBtn:hover { background-color: #0E42D2; }"
            "QPushButton#saveBtn {"
            "  background-color: #43A047; color: white; border: none;"
            "  border-radius: 4px; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton#saveBtn:hover { background-color: #2E7D32; }"
            "QPushButton#copyBtn {"
            "  background-color: #FAAD14; color: white; border: none;"
            "  border-radius: 4px; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton#copyBtn:hover { background-color: #D48806; }"
            "QPushButton:not(#genBtn):not(#saveBtn):not(#copyBtn) {"
            "  background-color: #F2F3F5; color: #4E5969; border: 1px solid #C9CDD4;"
            "  border-radius: 4px; font-size: 13px;"
            "}"
            "QPushButton:not(#genBtn):not(#saveBtn):not(#copyBtn):hover {"
            "  background-color: #E5E6EB; border-color: #86909C;"
            "}"
            "QCheckBox { spacing: 4px; }"
            "QCheckBox::indicator { width: 15px; height: 15px; border-radius: 3px; border: 1px solid #C9CDD4; }"
            "QCheckBox::indicator:checked { background-color: #165DFF; border-color: #165DFF; }"
        )

    def _bind_events(self):
        for btn in self.findChildren(QPushButton):
            txt = btn.text()
            if txt == "生成命令":
                btn.clicked.connect(self._generate)
            elif txt == "保存结果":
                btn.clicked.connect(self._save_result)
            elif txt == "复制全部":
                btn.clicked.connect(self._copy_all)
            elif txt == "清空":
                btn.clicked.connect(self._clear_output)

    def _generate(self):
        template = self.template_edit.toPlainText().strip()
        if not template:
            QMessageBox.information(self, "提示", "请先输入命令模板")
            return

        used_params = sorted(set(re.findall(r'%([a-f])', template)))
        if not used_params:
            count = self.cmd_count_spin.value()
            result_text = "\n".join([template] * count)
            self.output_edit.setPlainText(result_text)
            self._status_label.setText(f"  100 %")
            return

        configs = {}
        for char in used_params:
            idx = ord(char) - ord('a')
            if idx < len(self._param_widgets):
                configs[char] = self._param_widgets[idx].get_config()
            else:
                configs[char] = {"char": char, "base": 0, "step": 1, "repeat": None, "loop": None}

        lines = []
        total_count = [0]
        max_count = self.cmd_count_spin.value()

        def _generate_recursive(param_idx: int, current_values: Dict[str, int]):
            if total_count[0] >= max_count:
                return
            if param_idx >= len(used_params):
                rendered = template
                for char, val in current_values.items():
                    rendered = rendered.replace(f"%{char}", str(val))
                lines.append(rendered)
                total_count[0] += 1
                pct = min(int(total_count[0] / max_count * 100), 100)
                self._status_label.setText(f"  {pct} %")
                QApplication.processEvents()
                return

            char = used_params[param_idx]
            cfg = configs[char]
            base = cfg["base"]
            step = cfg["step"]
            loop = cfg["loop"] or 1
            repeat = cfg["repeat"] or 1

            values = []
            for i in range(loop):
                values.append(base + i * step)

            for val in values:
                new_values = dict(current_values)
                new_values[char] = val
                for _ in range(repeat):
                    if total_count[0] >= max_count:
                        return
                    _generate_recursive(param_idx + 1, new_values)

        _generate_recursive(0, {})
        result_text = "\n".join(lines)
        self.output_edit.setPlainText(result_text)
        self._status_label.setText(f"  100 %")

    def _save_result(self):
        text = self.output_edit.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "提示", "没有可保存的内容，先生成命令")
            return
        default_name = f"batch_cmds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存命令结果", default_name, "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "成功", f"已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存失败: {e}")

    def _copy_all(self):
        text = self.output_edit.toPlainText()
        if text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        else:
            QMessageBox.information(self, "提示", "没有可复制的内容")

    def _clear_output(self):
        self.output_edit.clear()
        self._status_label.setText("  0 %")
