#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子网掩码计算器 - 新版布局
支持IP/掩码计算、二进制可视化、子网划分
布局：输入区单行紧凑 + 结果区卡片式网格 + 子网划分表格
"""

import re
from typing import List, Tuple, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QComboBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QApplication, QScrollArea, QGridLayout,
    QSizePolicy, QAbstractItemView, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon


class CardFrame(QFrame):
    def __init__(self, label_text="", value_text="", highlight=False, parent=None):
        super().__init__(parent)
        self.highlight = highlight
        self._setup_ui(label_text, value_text)

    def _setup_ui(self, label_text, value_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 11px; color: #86909C; font-weight: normal;")
        self.value = QLabel(value_text or "--")
        self.value.setTextFormat(Qt.PlainText)

        if self.highlight:
            self.setStyleSheet(
                "CardFrame {"
                "  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "  stop:0 #E8F3FF, stop:1 #F0F7FF);"
                "  border: 1px solid #B3D4FC; border-radius: 6px;"
                "}"
            )
            self.label.setStyleSheet("font-size: 11px; color: #86909C; font-weight: bold;")
            self.value.setStyleSheet(
                "font-size: 14px; color: #165DFF; font-weight: bold; "
                "font-family: Consolas, monospace;"
            )
        else:
            self.setStyleSheet(
                "CardFrame {"
                "  background-color: #F7F8FA; border: 1px solid #E5E6EB; border-radius: 6px;"
                "}"
            )
            self.value.setStyleSheet(
                "font-size: 15px; color: #1D2129; font-weight: bold; "
                "font-family: Consolas, monospace;"
            )

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, text):
        self.value.setText(text)


class SubnetCalculatorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self._binary_expanded = False
        self._setup_ui()
        self._apply_style()
        self._bind_events()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        input_frame = QFrame()
        input_frame.setObjectName("inputArea")
        input_frame.setStyleSheet(
            "#inputArea {"
            "  background-color: #FAFBFC; border: 1px solid #E5E6EB; border-radius: 6px;"
            "}"
        )
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(18, 14, 18, 14)
        input_layout.setSpacing(16)

        ip_label = QLabel("IP 地址:")
        ip_label.setStyleSheet(
            "font-size: 13px; color: #4E5969; font-weight: 600;"
        )
        input_layout.addWidget(ip_label)

        ip_container = QHBoxLayout()
        ip_container.setSpacing(4)
        self.ip_inputs = []
        for i in range(4):
            inp = QLineEdit()
            inp.setPlaceholderText("0~255")
            inp.setAlignment(Qt.AlignCenter)
            inp.setMaxLength(3)
            inp.setMaximumWidth(52)
            inp.setMinimumHeight(30)
            self.ip_inputs.append(inp)
            ip_container.addWidget(inp)
            if i < 3:
                dot = QLabel(".")
                dot.setFont(QFont("Consolas", 14, QFont.Bold))
                dot.setStyleSheet("color: #86909C;")
                ip_container.addWidget(dot)

        input_layout.addLayout(ip_container)

        mask_label = QLabel("掩码位:")
        mask_label.setStyleSheet(
            "font-size: 13px; color: #4E5969; font-weight: 600;"
        )
        input_layout.addWidget(mask_label)

        self.mask_spin = QSpinBox()
        self.mask_spin.setRange(0, 32)
        self.mask_spin.setValue(24)
        self.mask_spin.setMinimumHeight(30)
        self.mask_spin.setMinimumWidth(56)
        input_layout.addWidget(self.mask_spin)

        input_layout.addStretch()

        calc_btn = QPushButton("⚡ 一键计算")
        calc_btn.setObjectName("calcBtn")
        calc_btn.setCursor(Qt.PointingHandCursor)
        calc_btn.setMinimumHeight(30)
        calc_btn.setMinimumWidth(100)
        input_layout.addWidget(calc_btn)

        layout.addWidget(input_frame)

        result_group = QGroupBox()
        result_group.setTitle("")
        result_group.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        result_outer = QVBoxLayout(result_group)
        result_outer.setContentsMargins(0, 0, 0, 0)
        result_outer.setSpacing(0)

        section_title = QLabel("计算结果")
        section_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1D2129; padding-left: 4px;"
            "border-left: 3px solid #165DFF; padding-left: 8px; margin-bottom: 10px;"
        )
        result_outer.addWidget(section_title)

        card_row_1 = QHBoxLayout()
        card_row_1.setSpacing(10)

        self.card_network = CardFrame("网络地址", "")
        card_row_1.addWidget(self.card_network, stretch=1)

        self.card_mask = CardFrame("子网掩码", "")
        card_row_1.addWidget(self.card_mask, stretch=1)

        self.card_broadcast = CardFrame("广播地址", "")
        card_row_1.addWidget(self.card_broadcast, stretch=1)

        self.card_host_count = CardFrame("可用主机数", "")
        card_row_1.addWidget(self.card_host_count, stretch=1)

        result_outer.addLayout(card_row_1)

        card_row_2 = QHBoxLayout()
        card_row_2.setSpacing(10)

        self.card_host_range = CardFrame("🖥️ 主机范围（最常用）", "", highlight=True)
        card_row_2.addWidget(self.card_host_range, stretch=2)

        info_card = CardFrame("📋 其他信息", "", highlight=False)
        self.info_card_widget = info_card
        card_row_2.addWidget(info_card, stretch=1)

        result_outer.addLayout(card_row_2)

        layout.addWidget(result_group)

        binary_group = QGroupBox("二进制位对照")
        binary_group.setStyleSheet(self._group_style())
        binary_layout = QVBoxLayout(binary_group)
        binary_layout.setContentsMargins(14, 8, 14, 8)
        binary_layout.setSpacing(4)

        toggle_btn = QPushButton("▼ 展开二进制详情")
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.setMinimumHeight(26)
        binary_layout.addWidget(toggle_btn)

        self.binary_widget = QWidget()
        self.binary_widget.setVisible(False)
        bl = QGridLayout(self.binary_widget)
        bl.setSpacing(4)

        headers = ["", "第1段", "第2段", "第3段", "第4段"]
        row_names = ["十进制", "主机IP", "子网掩码", "网络地址", "广播地址"]
        self.binary_cells = {}
        for c, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; color: #86909C; font-weight: bold;")
            bl.addWidget(lbl, 0, c)
        for r, name in enumerate(row_names, start=1):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet("font-size: 11px; color: #4E5969; font-weight: bold;")
            bl.addWidget(lbl, r, 0)
            for c in range(4):
                cell = QLabel("")
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont("Consolas", 10))
                cell.setMinimumHeight(22)
                cell.setStyleSheet(
                    "color: #1D2129; background-color: #F2F3F5; "
                    "border: 1px solid #E5E6EB; border-radius: 3px;"
                )
                bl.addWidget(cell, r, c + 1)
                self.binary_cells[(r - 1, c)] = cell

        binary_layout.addWidget(self.binary_widget)
        layout.addWidget(binary_group)

        divide_group = QGroupBox()
        divide_group.setTitle("")
        divide_group.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        divide_outer = QVBoxLayout(divide_group)
        divide_outer.setContentsMargins(0, 0, 0, 0)
        divide_outer.setSpacing(0)

        divide_title = QLabel("子网划分")
        divide_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1D2129; padding-left: 4px;"
            "border-left: 3px solid #165DFF; padding-left: 8px; margin-bottom: 10px;"
        )
        divide_outer.addWidget(divide_title)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        divide_label = QLabel("需要划分数:")
        divide_label.setStyleSheet(
            "font-size: 13px; color: #4E5969; font-weight: 600;"
        )
        top_row.addWidget(divide_label)

        self.divide_spin = QSpinBox()
        self.divide_spin.setRange(1, 4096)
        self.divide_spin.setValue(4)
        self.divide_spin.setMinimumHeight(28)
        self.divide_spin.setMinimumWidth(60)
        top_row.addWidget(self.divide_spin)

        top_row.addStretch()

        divide_calc_btn = QPushButton("⚡ 计算")
        divide_calc_btn.setObjectName("divideBtn")
        divide_calc_btn.setCursor(Qt.PointingHandCursor)
        divide_calc_btn.setMinimumHeight(28)
        divide_calc_btn.setMinimumWidth(70)
        top_row.addWidget(divide_calc_btn)

        copy_all_btn = QPushButton("📋 复制全部")
        copy_all_btn.setObjectName("copyAllBtn")
        copy_all_btn.setCursor(Qt.PointingHandCursor)
        copy_all_btn.setMinimumHeight(28)
        copy_all_btn.setMinimumWidth(80)
        top_row.addWidget(copy_all_btn)

        divide_outer.addLayout(top_row)

        self.divide_table = QTableWidget()
        self.divide_table.setColumnCount(5)
        self.divide_table.setHorizontalHeaderLabels(["#", "网络地址", "主机范围", "可用主机", ""])
        self.divide_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.divide_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.divide_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.divide_table.setColumnWidth(0, 40)
        self.divide_table.setColumnWidth(3, 80)
        self.divide_table.setColumnWidth(4, 40)
        self.divide_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.divide_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.divide_table.verticalHeader().setVisible(False)
        self.divide_table.setAlternatingRowColors(True)
        self.divide_table.setMinimumHeight(120)
        self.divide_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        divide_outer.addWidget(self.divide_table)

        layout.addWidget(divide_group)
        layout.addStretch()

    def _group_style(self):
        return (
            "QGroupBox {"
            "  font-size: 14px; font-weight: bold; color: #1D2129;"
            "  border: 1px solid #E5E6EB; border-radius: 6px;"
            "  margin-top: 8px; padding-top: 8px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin; left: 12px; padding: 0 6px;"
            "}"
        )

    def _apply_style(self):
        self.setStyleSheet(
            "QLineEdit {"
            "  border: 1px solid #C9CDD4; border-radius: 4px; padding: 2px 6px;"
            "  font-size: 13px; background: white;"
            "}"
            "QLineEdit:focus { border-color: #165DFF; }"
            "QSpinBox {"
            "  border: 1px solid #C9CDD4; border-radius: 4px; padding: 2px 6px;"
            "  font-size: 13px; background: white;"
            "}"
            "QSpinBox:focus { border-color: #165DFF; }"
            "QPushButton[objectName=\"calcBtn\"] {"
            "  background-color: #165DFF; color: white; border: none;"
            "  border-radius: 4px; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton[objectName=\"calcBtn\"]:hover { background-color: #0E42D2; }"
            "QPushButton[objectName=\"divideBtn\"] {"
            "  background-color: #43A047; color: white; border: none;"
            "  border-radius: 4px; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton[objectName=\"divideBtn\"]:hover { background-color: #2E7D32; }"
            "QPushButton[objectName=\"copyAllBtn\"] {"
            "  background-color: white; color: #4E5969; border: 1px solid #C9CDD4;"
            "  border-radius: 4px; font-size: 12px;"
            "}"
            "QPushButton[objectName=\"copyAllBtn\"]:hover {"
            "  background-color: #F7F8FA; border-color: #A9AEB8;"
            "}"
            "QTableWidget {"
            "  gridline-color: #E5E6EB; border: 1px solid #E5E6EB; border-radius: 4px;"
            "  font-size: 12px;"
            "}"
            "QTableWidget::item { padding: 4px; }"
            "QHeaderView::section {"
            "  background-color: #F2F3F5; color: #4E5969; font-weight: bold;"
            "  border: none; border-bottom: 1px solid #E5E6EB; padding: 6px;"
            "}"
        )

    def _bind_events(self):
        for inp in self.ip_inputs:
            inp.textChanged.connect(self._on_input_changed)
            inp.returnPressed.connect(self._calculate)
        self.mask_spin.valueChanged.connect(self._on_input_changed)

        children = self.findChildren(QPushButton)
        for btn in children:
            txt = btn.text()
            if txt == "📋":
                btn.clicked.connect(lambda checked, b=btn: self._copy_result(b.property("copy_key")))
            elif txt == "▼ 展开二进制详情":
                btn.clicked.connect(self._toggle_binary)
            elif txt == "⚡ 一键计算":
                btn.clicked.connect(self._calculate)
            elif txt == "⚡ 计算" and btn.objectName() == "divideBtn":
                btn.clicked.connect(self._calculate_division)
            elif txt == "📋 复制全部":
                btn.clicked.connect(self._copy_all_results)

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._calculate)
        timer.start(100)

    def _toggle_binary(self):
        self._binary_expanded = not self._binary_expanded
        self.binary_widget.setVisible(self._binary_expanded)
        btn = self.sender()
        if self._binary_expanded:
            btn.setText("▲ 收起二进制详情")
        else:
            btn.setText("▼ 展开二进制详情")

    def _get_ip_int(self) -> Optional[int]:
        try:
            parts = [int(inp.text() or "0") for inp in self.ip_inputs]
            if not all(0 <= p <= 255 for p in parts):
                return None
            return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
        except ValueError:
            return None

    def _int_to_ip(self, n: int) -> str:
        return f"{(n >> 24) & 0xFF}.{(n >> 16) & 0xFF}.{(n >> 8) & 0xFF}.{n & 0xFF}"

    def _int_to_bin(self, n: int) -> str:
        return f"{n:032b}"

    def _mask_to_int(self, prefix: int) -> int:
        if prefix == 0:
            return 0
        return ((1 << prefix) - 1) << (32 - prefix)

    def _on_input_changed(self):
        pass

    def _calculate(self):
        ip_int = self._get_ip_int()
        if ip_int is None:
            return
        prefix = self.mask_spin.value()
        mask_int = self._mask_to_int(prefix)
        network_int = ip_int & mask_int
        broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)
        wildcard_int = ~mask_int & 0xFFFFFFFF
        host_bits = 32 - prefix
        host_count = max(0, (1 << host_bits) - 2) if host_bits >= 1 else 0
        first_host = network_int + 1 if host_count > 0 else network_int
        last_host = broadcast_int - 1 if host_count > 0 else broadcast_int

        self.card_network.set_value(self._int_to_ip(network_int))
        self.card_mask.set_value(self._int_to_ip(mask_int))
        self.card_broadcast.set_value(self._int_to_ip(broadcast_int))
        self.card_host_count.set_value(str(host_count))

        host_range_str = f"{self._int_to_ip(first_host)} ~ {self._int_to_ip(last_host)}"
        self.card_host_range.set_value(host_range_str)

        first_octet = (ip_int >> 24) & 0xFF
        if 1 <= first_octet <= 126:
            ip_class_info = "A 类"
        elif 128 <= first_octet <= 191:
            ip_class_info = "B 类"
        elif 192 <= first_octet <= 223:
            ip_class_info = "C 类"
        elif 224 <= first_octet <= 239:
            ip_class_info = "D 组播"
        else:
            ip_class_info = "E 保留"

        private_ranges = [
            (10, "10.0.0.0/8"),
            (172, "172.16.0.0/12"),
            (192, "192.168.0.0/16"),
        ]
        is_private = False
        for start, rng in private_ranges:
            if first_octet == start or (first_octet == 172 and 16 <= ((ip_int >> 16) & 0xFF) <= 31) or \
               (first_octet == 192 and (ip_int >> 16) & 0xFF == 168):
                is_private = True
                break
        if is_private:
            ip_class_info += " (私有地址段)"

        info_html = (
            f"<div style='display:flex;flex-direction:column;gap:4px;margin-top:4px;'>"
            f"<div style='font-size:12px;'><b style='color:#86909C;'>反掩码:</b> "
            f"<span style='font-family:Consolas;'>{self._int_to_ip(wildcard_int)}</span></div>"
            f"<div style='font-size:12px;'><b style='color:#86909C;'>前缀法:</b> "
            f"<span style='font-family:Consolas;'>/{prefix}</span></div>"
            f"<div style='font-size:12px;'><b style='color:#86909C;'>IP类别:</b> "
            f"<span>{ip_class_info}</span></div>"
            f"</div>"
        )

        self.info_card_widget.value.setTextFormat(Qt.RichText)
        self.info_card_widget.value.setText(info_html)

        rows_data = [
            (ip_int, "主机IP"),
            (mask_int, "子网掩码"),
            (network_int, "网络地址"),
            (broadcast_int, "广播地址"),
        ]
        for r_idx, (val, _) in enumerate(rows_data):
            bin_str = self._int_to_bin(val)
            for c in range(4):
                segment = bin_str[c * 8:(c + 1) * 8]
                cell = self.binary_cells.get((r_idx, c))
                if cell:
                    cell.setText(segment)
                    if r_idx == 1:
                        ones = segment.count('1')
                        if ones == 8:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #FFFFFF; "
                                f"background-color: #165DFF; border: 1px solid #0E42D2; "
                                "border-radius: 3px;"
                            )
                        elif ones > 0:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #FFFFFF; "
                                f"background-color: #597AE8; border: 1px solid #4566CC; "
                                "border-radius: 3px;"
                            )
                        else:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #F53F3F; "
                                "background-color: #FFECE8; border: 1px solid #FCDCDA; "
                                "border-radius: 3px;"
                            )
                    elif r_idx == 3:
                        zeros = segment.count('0')
                        if zeros == 8:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #FFFFFF; "
                                "background-color: #FAAD14; border: 1px solid #D48806; "
                                "border-radius: 3px;"
                            )
                        elif zeros > 0:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #86909C; "
                                "background-color: #FFF7E6; border: 1px solid #FFD591; "
                                "border-radius: 3px;"
                            )
                        else:
                            cell.setStyleSheet(
                                "font-family: Consolas; font-size: 11px; color: #1D2129; "
                                "background-color: #F2F3F5; border: 1px solid #E5E6EB; "
                                "border-radius: 3px;"
                            )
                    else:
                        cell.setStyleSheet(
                            "font-family: Consolas; font-size: 11px; color: #1D2129; "
                            "background-color: #F2F3F5; border: 1px solid #E5E6EB; "
                            "border-radius: 3px;"
                        )

    def _calculate_division(self):
        ip_int = self._get_ip_int()
        if ip_int is None:
            return
        current_prefix = self.mask_spin.value()
        num_subnets = self.divide_spin.value()
        needed_bits = 0
        temp = 1
        while temp < num_subnets and (current_prefix + needed_bits) < 32:
            needed_bits += 1
            temp *= 2
        new_prefix = current_prefix + needed_bits
        if new_prefix > 32:
            new_prefix = 32
        subnet_bits = 32 - new_prefix
        hosts_per_subnet = max(0, (1 << subnet_bits) - 2) if subnet_bits >= 1 else 0
        mask_int = self._mask_to_int(new_prefix)
        base_network = ip_int & self._mask_to_int(current_prefix)
        actual_subnets = min(num_subnets, 1 << needed_bits) if needed_bits <= (32 - current_prefix) else num_subnets

        self.divide_table.setRowCount(actual_subnets)
        for i in range(actual_subnets):
            subnet_network = base_network + (i << subnet_bits)
            subnet_broadcast = subnet_network | ((1 << subnet_bits) - 1)
            first_h = subnet_network + 1 if hosts_per_subnet > 0 else subnet_network
            last_h = subnet_broadcast - 1 if hosts_per_subnet > 0 else subnet_broadcast

            self.divide_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.divide_table.setItem(i, 1, QTableWidgetItem(f"{self._int_to_ip(subnet_network)}"))
            self.divide_table.setItem(i, 2, QTableWidgetItem(f".{first_h & 0xFF} ~ .{last_h & 0xFF}"))
            self.divide_table.setItem(i, 3, QTableWidgetItem(str(hosts_per_subnet)))

            copy_btn = QPushButton("📋")
            copy_btn.setFixedSize(30, 24)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setToolTip(f"复制第{i+1}个子网信息")
            row_data = f"子网{i+1}: {self._int_to_ip(subnet_network)}/{new_prefix}, 主机范围: {self._int_to_ip(first_h)} ~ {self._int_to_ip(last_h)}, 可用主机: {hosts_per_subnet}"
            copy_btn.clicked.connect(lambda checked, d=row_data: self._copy_text(d))
            self.divide_table.setCellWidget(i, 4, copy_btn)

    def _copy_result(self, key):
        label = self.result_labels.get(key)
        if label:
            text = label.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def _copy_text(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _copy_all_results(self):
        lines = []
        rows = self.divide_table.rowCount()
        for i in range(rows):
            net_item = self.divide_table.item(i, 1)
            range_item = self.divide_table.item(i, 2)
            count_item = self.divide_table.item(i, 3)
            if net_item and range_item and count_item:
                lines.append(f"#{i+1}: {net_item.text()}, 主机: {range_item.text()}, 可用: {count_item.text()}")
        text = "\n".join(lines)
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
