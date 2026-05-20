#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备发现对话框
提供网络设备自动发现功能
"""

import ipaddress
import platform
import subprocess
from typing import List, Optional

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QProgressBar, QCheckBox,
                               QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.core.device_manager import VENDORS, DEVICE_TYPES, PROTOCOLS


class PingWorker(QThread):
    """Ping工作线程，用于扫描网络设备"""
    progress = pyqtSignal(int, int)
    found = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, ip_list: List[str]):
        """初始化Ping工作线程

        Args:
            ip_list: IP地址列表
        """
        super().__init__()
        self.ip_list = ip_list
        self._is_running = True

    def stop(self):
        """停止扫描"""
        self._is_running = False

    def run(self):
        """执行Ping扫描"""
        results: List[str] = []
        total = len(self.ip_list)

        # 根据平台设置ping参数
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"

        for i, ip in enumerate(self.ip_list):
            if not self._is_running:
                break

            try:
                # 验证IP地址
                ipaddress.ip_address(ip)

                # 构建ping命令
                cmd = ["ping", param, "1", timeout_param, "1", ip]

                # Windows平台隐藏窗口
                startupinfo = None
                if platform.system().lower() == "windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                # 执行ping
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    startupinfo=startupinfo,
                    timeout=3
                )

                if result.returncode == 0:
                    results.append(ip)
                    self.found.emit(ip)

            except ValueError:
                # IP地址格式无效
                continue
            except subprocess.TimeoutExpired:
                # Ping超时
                pass
            except Exception:
                # 其他异常
                pass

            self.progress.emit(i + 1, total)

        self.finished.emit(results)

        self.finished.emit(results)


class DeviceDiscoveryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量设备发现")
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)
        self.discovered_ips = []
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("批量设备发现")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1D2129;")
        layout.addWidget(title)

        scan_group = QGroupBox("扫描设置")
        scan_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #1D2129;
                border: 1px solid #E5E6EB; border-radius: 6px;
                margin-top: 8px; padding: 16px; background-color: #FAFBFC;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }
        """)
        scan_layout = QVBoxLayout()
        scan_layout.setSpacing(12)

        input_style = """
            QLineEdit, QComboBox {
                border: 1px solid #E5E6EB; border-radius: 4px;
                padding: 8px 12px; font-size: 14px; background-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #165DFF; }
        """

        ip_layout = QHBoxLayout()
        ip_layout.setSpacing(8)
        ip_layout.addWidget(QLabel("起始IP："))
        self.start_ip = QLineEdit("192.168.1.1")
        self.start_ip.setStyleSheet(input_style)
        ip_layout.addWidget(self.start_ip)
        ip_layout.addWidget(QLabel("结束IP："))
        self.end_ip = QLineEdit("192.168.1.254")
        self.end_ip.setStyleSheet(input_style)
        ip_layout.addWidget(self.end_ip)
        scan_layout.addLayout(ip_layout)

        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        preset_layout.addWidget(QLabel("快速选择："))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "-- 自定义IP范围 --",
            "192.168.0.0/24 (192.168.0.1 - 192.168.0.254)",
            "192.168.1.0/24 (192.168.1.1 - 192.168.1.254)",
            "10.0.0.0/24 (10.0.0.1 - 10.0.0.254)",
            "172.16.0.0/24 (172.16.0.1 - 172.16.0.254)",
        ])
        self.preset_combo.setStyleSheet(input_style)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        scan_layout.addLayout(preset_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.setFixedSize(120, 38)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #165DFF; color: white; border: none;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { background-color: #0E42D2; }
            QPushButton:disabled { background-color: #C9CDD4; }
        """)
        self.scan_btn.clicked.connect(self._start_scan)
        btn_layout.addWidget(self.scan_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedSize(80, 38)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F53F3F; color: white; border: none;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { background-color: #CB272D; }
            QPushButton:disabled { background-color: #C9CDD4; }
        """)
        self.stop_btn.clicked.connect(self._stop_scan)
        btn_layout.addWidget(self.stop_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E6EB; border-radius: 4px;
                text-align: center; height: 22px; background-color: #F5F7FA;
            }
            QProgressBar::chunk {
                background-color: #165DFF; border-radius: 3px;
            }
        """)
        btn_layout.addWidget(self.progress_bar)
        btn_layout.addStretch()
        scan_layout.addLayout(btn_layout)

        self.status_label = QLabel("就绪，请设置IP范围后点击扫描")
        self.status_label.setStyleSheet("font-size: 13px; color: #86909C;")
        scan_layout.addWidget(self.status_label)

        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        result_group = QGroupBox("发现结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #1D2129;
                border: 1px solid #E5E6EB; border-radius: 6px;
                margin-top: 8px; padding: 16px; background-color: #FAFBFC;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }
        """)
        result_layout = QVBoxLayout()
        result_layout.setSpacing(12)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["选择", "IP地址", "状态"])
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB; border-radius: 4px;
                background-color: #FFFFFF; gridline-color: #F2F3F5;
            }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section {
                background-color: #F7F8FA; border: none;
                border-bottom: 1px solid #E5E6EB; padding: 6px;
                font-weight: bold; color: #1D2129;
            }
        """)
        result_layout.addWidget(self.result_table)

        add_layout = QHBoxLayout()
        add_layout.setSpacing(12)

        self.select_all_cb = QCheckBox("全选")
        self.select_all_cb.setStyleSheet("font-size: 13px;")
        self.select_all_cb.stateChanged.connect(self._toggle_select_all)
        add_layout.addWidget(self.select_all_cb)

        add_layout.addStretch()

        self.add_selected_btn = QPushButton("添加选中设备到清单")
        self.add_selected_btn.setFixedSize(180, 38)
        self.add_selected_btn.setEnabled(False)
        self.add_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B42A; color: white; border: none;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { background-color: #009A29; }
            QPushButton:disabled { background-color: #C9CDD4; }
        """)
        self.add_selected_btn.clicked.connect(self._add_selected)
        add_layout.addWidget(self.add_selected_btn)

        result_layout.addLayout(add_layout)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 38)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA; border: 1px solid #E5E6EB;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { border: 1px solid #165DFF; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def _on_preset_changed(self, idx):
        if idx == 0:
            return
        presets = {
            1: ("192.168.0.1", "192.168.0.254"),
            2: ("192.168.1.1", "192.168.1.254"),
            3: ("10.0.0.1", "10.0.0.254"),
            4: ("172.16.0.1", "172.16.0.254"),
        }
        if idx in presets:
            self.start_ip.setText(presets[idx][0])
            self.end_ip.setText(presets[idx][1])

    def _start_scan(self):
        try:
            start = ipaddress.IPv4Address(self.start_ip.text().strip())
            end = ipaddress.IPv4Address(self.end_ip.text().strip())
        except Exception:
            QMessageBox.warning(self, "错误", "IP地址格式不正确")
            return

        if start > end:
            QMessageBox.warning(self, "错误", "起始IP不能大于结束IP")
            return

        ip_list = []
        current = start
        while current <= end:
            ip_list.append(str(current))
            current += 1

        if len(ip_list) > 1024:
            reply = QMessageBox.question(self, "确认",
                f"将扫描 {len(ip_list)} 个IP地址，可能需要较长时间，确定继续吗？",
                QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        self.result_table.setRowCount(0)
        self.discovered_ips = []
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.add_selected_btn.setEnabled(False)
        self.select_all_cb.setChecked(False)
        self.progress_bar.setMaximum(len(ip_list))
        self.progress_bar.setValue(0)
        self.status_label.setText(f"正在扫描 {len(ip_list)} 个IP地址...")

        self.worker = PingWorker(ip_list)
        self.worker.progress.connect(self._on_progress)
        self.worker.found.connect(self._on_found)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _stop_scan(self):
        if self.worker:
            self.worker.stop()
        self.status_label.setText("扫描已停止")
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_progress(self, current, total):
        self.progress_bar.setValue(current)

    def _on_found(self, ip):
        self.discovered_ips.append(ip)
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)

        cb = QCheckBox()
        cb.setChecked(True)
        self.result_table.setCellWidget(row, 0, cb)

        self.result_table.setItem(row, 1, QTableWidgetItem(ip))
        self.result_table.setItem(row, 2, QTableWidgetItem("在线"))

        self.add_selected_btn.setEnabled(True)

    def _on_finished(self, results):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"扫描完成，发现 {len(results)} 台在线设备")

    def _toggle_select_all(self, state):
        for row in range(self.result_table.rowCount()):
            widget = self.result_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(state == Qt.Checked)

    def _add_selected(self):
        selected = []
        for row in range(self.result_table.rowCount()):
            widget = self.result_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                ip_item = self.result_table.item(row, 1)
                if ip_item:
                    selected.append(ip_item.text())

        if not selected:
            QMessageBox.warning(self, "提示", "请至少选择一个设备")
            return

        self.discovered_ips = selected
        self.accept()

    def get_selected_ips(self):
        return self.discovered_ips