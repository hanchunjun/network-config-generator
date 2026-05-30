import os
import sys
import json
import time
import glob as glob_mod
import ssl
import socket
import subprocess
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

import requests
import certifi
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QTextEdit, QMessageBox, QProgressBar,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QDialogButtonBox, QCheckBox, QMenu,
                               QAction, QAbstractItemView, QTabWidget,
                               QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

from src.utils.resource_path import resource_path, get_app_dir, get_config_path, get_single_dir
from src.core.secure_config import SecureConfigFile
from src.core.local_audit_engine import LocalAuditEngine, AuditResult, Severity
from src.core.local_diagnostic_engine import LocalDiagnosticEngine, DiagResult, DiagSeverity
from src.core.theme_engine import ThemeEngine
from src.ui.system_settings_page import get_active_ai_config

SCRIPTS_DIR = resource_path("scripts")
sys.path.insert(0, SCRIPTS_DIR)

AI_CONFIG_PATH = get_config_path("config/ai_config.json")
SINGLE_DEVICES_PATH = os.path.join(get_single_dir(), "single_devices.json")

VENDORS = ["锐捷", "华为", "H3C", "思科"]
DEVICE_TYPES = ["核心交换机", "汇聚交换机", "接入交换机", "路由器", "防火墙", "AC控制器", "AP"]
PROTOCOLS = ["ssh", "telnet"]

DEV_TYPE_MAP = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

TEST_CMD_MAP = {
    "锐捷": ["show version", "show clock"],
    "华为": ["display version", "display clock"],
    "H3C": ["display version", "display clock"],
    "思科": ["show version", "show clock"]
}

INSPECT_EXCEPTION_KEYS = [
    "Down", "Error", "Warning", "CPU", "内存", "过载", "告警", "故障",
    "CRC", "reset", "spanning-tree", "邻居", "会话"
]

INSPECT_TYPE_NORMALIZE = {
    "核心交换机": "交换机", "汇聚交换机": "交换机", "接入交换机": "交换机",
    "交换机": "交换机", "路由器": "路由器", "防火墙": "交换机",
    "AC控制器": "交换机", "AP": "交换机",
}

INSPECT_DEFAULT_CMDS = ["show version", "show ip interface brief", "show cpu", "show memory"]

INSPECT_BASE_CMD_LIB: Dict[str, Dict[str, List[str]]] = {
    "锐捷": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip route", "show cpu", "show memory", "show logging"]
    },
    "华为": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "H3C": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "思科": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip interface brief", "show ip route", "show cpu", "show memory", "show logging"]
    }
}

FULL_CONFIG_CMD_MAP: Dict[str, str] = {
    "锐捷": "show running-config",
    "华为": "display current-configuration",
    "H3C": "display current-configuration",
    "思科": "show running-config"
}

STATUS_ICONS = {"success": "✅", "failed": "❌", "pending": "⚪"}
TAB_LOG = 0
TAB_BACKUP = 1
TAB_REPORT = 2
TAB_DIAGNOSIS = 3
TAB_COMPLIANCE = 4

COMPLIANCE_PROMPT = """{reviewer_rules}

---
设备IP: {device_ip}
配置:
{config_content}
"""

COMPLIANCE_API_TIMEOUT = 120
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 10]
MAX_RULES_LENGTH = 2000

RATE_LIMIT_MAX_RETRIES = 3
RATE_LIMIT_BACKOFF_BASE = 30
PROBE_TIMEOUT = 15


from src.ui.single_device.compliancecheckthread import ComplianceCheckThread
from src.ui.single_device.aidiagnosticthread import AIDiagnosticThread
from src.ui.single_device.singledeviceworker import SingleDeviceWorker
from src.ui.single_device.deviceformdialog import DeviceFormDialog


# ─────────────────────────────────────────────────────────────────────────────
# 公共工具函数（供 SingleDevicePage 内部使用）
# ─────────────────────────────────────────────────────────────────────────────

def _btn_style(t: dict, fg: str = None, bold: bool = False, font_size: int = 10,
               radius_key: str = "radius_md", pad: str = "2px 8px") -> str:
    """通用按钮样式：透明背景 + 边框 + hover 加深边框。"""
    fg = fg or t['text_secondary']
    fw = "bold" if bold else "normal"
    return (f"QPushButton {{ background-color: transparent; color: {fg};"
            f" border: 1px solid {t['border']}; border-radius: {t[radius_key]}px;"
            f" font-size: {font_size}pt; font-weight: {fw}; padding: {pad}; }}"
            f" QPushButton:hover {{ border-color: {t['border_deep']}; }}"
            f" QPushButton:disabled {{ color: {t['text_tertiary']}; }}")

def _ai_btn_style(t: dict) -> str:
    """AI 按钮专用样式（带彩色文字 + bold）。"""
    return _btn_style(t, fg=t['text_secondary'], bold=True, font_size=10, radius_key="radius_md", pad="2px 8px")

def _set_ai_btn_state(btn: QPushButton, text: str, enabled: bool, loading: bool = False):
    """统一设置 AI 按钮状态（加载/完成）。"""
    t = ThemeEngine.get().current_theme
    if loading:
        btn.setText(f"⏳ {text}中...")
        btn.setEnabled(False)
        btn.setStyleSheet(_btn_style(t, fg=t['text_tertiary'], bold=True, font_size=10))
    else:
        btn.setText(text)
        btn.setEnabled(enabled)
        btn.setStyleSheet(_ai_btn_style(t))

def _open_file(list_widget: QListWidget):
    """打开当前选中的文件。"""
    item = list_widget.currentItem()
    if item and item.data(Qt.UserRole):
        fp = item.data(Qt.UserRole)
        if os.path.exists(fp):
            os.startfile(fp)

def _delete_file(list_widget: QListWidget, refresh_fn: Callable, title: str = "文件"):
    """删除当前选中的文件并刷新列表。"""
    item = list_widget.currentItem()
    if not item or not item.data(Qt.UserRole):
        QMessageBox.warning(list_widget.parent(), "提示", f"请先选择要删除的{title}")
        return
    fp = item.data(Qt.UserRole)
    reply = QMessageBox.question(
        list_widget.parent(), "确认删除",
        f"确定要删除该{title}吗？\n{os.path.basename(fp)}",
        QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        try:
            os.remove(fp)
            refresh_fn()
        except Exception as e:
            QMessageBox.warning(list_widget.parent(), "删除失败", str(e))

def _refresh_file_list(list_widget: QListWidget, dir_path: str,
                       filter_combo: QComboBox = None, placeholder: str = "暂无文件"):
    """刷新文件列表（支持按 IP 筛选）。"""
    list_widget.blockSignals(True)
    list_widget.clear()
    if not os.path.isdir(dir_path):
        list_widget.addItem(_make_placeholder(placeholder))
        list_widget.blockSignals(False)
        return
    files = sorted(glob_mod.glob(os.path.join(dir_path, "*.*")),
                   key=os.path.getmtime, reverse=True)
    filter_ip = ""
    if filter_combo:
        filter_ip = filter_combo.currentText()
        if filter_ip and filter_ip != "全部设备":
            files = [f for f in files if filter_ip in os.path.basename(f)]
    if not files:
        list_widget.addItem(_make_placeholder(f"暂无匹配{placeholder}" if filter_ip and filter_ip != "全部设备" else placeholder))
        list_widget.blockSignals(False)
        return
    for fp in files:
        name = os.path.basename(fp)
        size_kb = os.path.getsize(fp) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%m-%d %H:%M")
        item = QListWidgetItem(f"{name}\n  ({size_kb:.1f}KB · {mtime})")
        item.setToolTip(fp)
        item.setData(Qt.UserRole, fp)
        list_widget.addItem(item)
    list_widget.blockSignals(False)
    if list_widget.count() > 0:
        list_widget.setCurrentRow(0)

def _make_placeholder(text: str) -> QListWidgetItem:
    """创建不可选的占位 QListWidgetItem。"""
    t = ThemeEngine.get().current_theme
    item = QListWidgetItem(text)
    item.setForeground(QColor(t['text_tertiary']))
    item.setFlags(Qt.NoItemFlags)
    return item


class SingleDevicePage(QWidget):
    COL_CHECK = 0
    COL_IP = 1
    COL_VENDOR = 2
    COL_TYPE = 3
    COL_PROTO = 4
    COL_USER = 5
    COL_STATUS = 6
    COL_TIME = 7
    COL_DATA = 8

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.worker = None
        self.devices: List[Dict] = []
        self._secure_cfg = SecureConfigFile.instance()
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._load_devices()
        self.refresh_backup_list()
        self.refresh_report_list()
        self.refresh_compliance_list()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

    # ─────────────────────────────────────────────────────────────────────────
    # UI 初始化
    # ─────────────────────────────────────────────────────────────────────────

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(4)

        # ── 设备清单 ──
        table_group = QGroupBox("设备清单")
        table_group.setStyleSheet(self._group_style())
        table_layout = QVBoxLayout()
        table_layout.setSpacing(4)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        t = self._theme_engine.current_theme

        self.add_btn = self._mk_btn("+ 添加设备", 100, _btn_style(t, fg=t['text_secondary']))
        self.add_btn.clicked.connect(self.on_add_device)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = self._mk_btn("✏️ 编辑", 72, _btn_style(t, fg=t['text_secondary']))
        self.edit_btn.clicked.connect(self.on_edit_device)
        toolbar.addWidget(self.edit_btn)

        self.del_btn = self._mk_btn("🗑️ 删除", 72, _btn_style(t))
        self.del_btn.clicked.connect(self.on_delete_device)
        toolbar.addWidget(self.del_btn)

        self.clear_btn = self._mk_btn("清空列表", 72, _btn_style(t, fg=t['text_tertiary']))
        self.clear_btn.clicked.connect(self.on_clear_all)
        toolbar.addWidget(self.clear_btn)

        self.select_count_lbl = QLabel("")
        self.select_count_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        toolbar.addWidget(self.select_count_lbl)
        toolbar.addStretch()
        table_layout.addLayout(toolbar)

        # 表格
        t = self._theme_engine.current_theme
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["", "IP地址", "厂商", "设备类型", "协议", "用户名", "状态", "最后执行", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for col, w in [(0, 32), (2, 56), (3, 96), (4, 52), (5, 76), (6, 46), (7, 140), (8, 0)]:
            self.table.setColumnWidth(col, w)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(80)
        self.table.setStyleSheet(self._table_style())
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.doubleClicked.connect(self.on_table_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # ── 操作按钮行 ──
        action_row = QHBoxLayout()
        action_row.setSpacing(6)

        self.inspect_btn = self._mk_btn("▶ 批量巡检", 96, self._primary_btn_style())
        self.inspect_btn.clicked.connect(self.run_batch_inspect)
        action_row.addWidget(self.inspect_btn)

        self.backup_btn = self._mk_btn("💾 批量备份", 96, self._secondary_btn_style())
        self.backup_btn.clicked.connect(self.run_batch_backup)
        action_row.addWidget(self.backup_btn)

        self.test_btn = self._mk_btn("🔗 测试连接", 88, self._secondary_btn_style())
        self.test_btn.clicked.connect(self.run_batch_test)
        action_row.addWidget(self.test_btn)

        self.cancel_btn = self._mk_btn("取消", 60, _btn_style(t))
        self.cancel_btn.clicked.connect(self.on_cancel_task)
        self.cancel_btn.setVisible(False)
        action_row.addWidget(self.cancel_btn)

        t = self._theme_engine.current_theme
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m")
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setStyleSheet(self._progress_style())
        action_row.addWidget(self.progress_bar, 1)
        layout.addLayout(action_row)

        self.status_label = QLabel("就绪，等待操作...")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding-left: 4px;")
        layout.addWidget(self.status_label)

        # ── 结果 Tab ──
        self.result_tabs = QTabWidget()
        self.result_tabs.setDocumentMode(True)
        self.result_tabs.setTabPosition(QTabWidget.North)
        self.result_tabs.setStyleSheet(self._result_tabs_style())

        self.result_tabs.addTab(self._create_log_tab(), "📋 执行日志")
        self.result_tabs.addTab(self._create_backup_tab(), "💾 备份配置")
        self.result_tabs.addTab(self._create_report_tab(), "📄 巡检报告")
        self.result_tabs.addTab(self._create_diagnosis_tab(), "🩺 诊断报告")
        self.result_tabs.addTab(self._create_compliance_tab(), "🔍 合规审计")

        layout.addWidget(self.result_tabs, 1)

        t = self._theme_engine.current_theme
        desc_label = QLabel("管理常用设备清单，支持批量巡检/备份/连接测试/AI分析。数据加密存储，跟随EXE便携使用。")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding: 4px 0;")
        layout.addWidget(desc_label)

        self.setLayout(layout)
        self._update_select_count()

    @staticmethod
    def _mk_btn(text: str, width: int, style: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(width, 30)
        btn.setStyleSheet(style)
        return btn

    # ─────────────────────────────────────────────────────────────────────────
    # 样式方法
    # ─────────────────────────────────────────────────────────────────────────

    def _text_edit_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QTextEdit {{ border: none; border-radius: {t['radius_md']}px; padding: 10px;"
                f" font-family: 'Consolas', 'Courier New', monospace; font-size: 10pt;"
                f" background-color: {t['input_bg']}; color: {t['text_secondary']};"
                f" selection-background-color: {t['selection_bg']}; selection-color: {t['text_main']}; }}")

    def _list_widget_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QListWidget {{ border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
                f" background-color: {t['input_bg']}; font-size: 10pt; outline: none; }}"
                f" QListWidget::item {{ padding: 4px 8px; border-bottom: 1px solid {t['border_deep']}; }}"
                f" QListWidget::item:hover {{ background-color: {t['selection_bg']}; }}"
                f" QListWidget::item:selected {{ background-color: {t['page_bg']}; color: {t['text_primary']}; }}")

    def _combo_small_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QComboBox {{ border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
                f" padding: 4px 8px; font-size: 11pt; background-color: {t['page_bg']}; }}"
                f" QComboBox:focus {{ border-color: {t['border']}; }}"
                f" QComboBox::drop-down {{ border: none; width: 20px; }}"
                f" QComboBox QAbstractItemView {{ border: 1px solid {t['border']};"
                f" background-color: {t['card_bg']}; selection-background-color: {t['selection_bg']}; outline: none; }}")

    def _group_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QGroupBox {{ font-size: 11pt; font-weight: bold; color: {t['text_main']};"
                f" border: 1px solid {t['border']}; border-radius: {t['radius_lg']}px;"
                f" margin-top: 4px; padding: 4px 10px; background-color: {t['card_bg']}; }}"
                f" QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}")

    def _primary_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QPushButton {{ background-color: transparent; border: 1px solid {t['border']};"
                f" border-radius: {t['radius_md']}px; font-size: 11pt; color: {t['text_secondary']}; padding: 5px 8px; }}"
                f" QPushButton:hover {{ border-color: {t['border_deep']}; }}"
                f" QPushButton:disabled {{ color: {t['text_tertiary']}; }}")

    def _secondary_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QPushButton {{ background-color: transparent; border: 1px solid {t['border']};"
                f" border-radius: {t['radius_md']}px; font-size: 11pt; }}"
                f" QPushButton:hover {{ border-color: {t['border_deep']}; }}")

    def _table_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QTableWidget {{ border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
                f" gridline-color: {t['border_deep']}; background-color: {t['card_bg']}; font-size: 10pt; }}"
                f" QTableWidget::item {{ padding: 2px 4px; }}"
                f" QTableWidget::item:alternate {{ background-color: {t['hover_bg']}; }}"
                f" QHeaderView::section {{ background-color: {t['toolbar_bg']}; border: none;"
                f" border-bottom: 1px solid {t['border']}; padding: 2px 6px;"
                f" font-size: 10pt; font-weight: bold; color: {t['text_secondary']}; }}")

    def _result_tabs_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QTabWidget::pane {{ border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
                f" background-color: {t['card_bg']}; top: -1px; }}"
                f" QTabBar::tab {{ background-color: {t['page_bg']}; border: 1px solid {t['border']};"
                f" border-bottom: none; border-top-left-radius: {t['radius_lg']}px;"
                f" border-top-right-radius: {t['radius_lg']}px; padding: 5px 8px;"
                f" font-size: 11pt; color: {t['text_secondary']}; margin-right: 2px; }}"
                f" QTabBar::tab:selected {{ background-color: {t['card_bg']}; color: {t['text_secondary']};"
                f" border-bottom: 2px solid {t['primary']}; font-weight: bold; }}"
                f" QTabBar::tab:hover:!selected {{ background-color: {t['selection_bg']}; color: {t['text_secondary']}; }}")

    def _progress_style(self) -> str:
        t = self._theme_engine.current_theme
        return (f"QProgressBar {{ border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
                f" text-align: center; height: 20px; background-color: {t['page_bg']}; font-size: 10pt; }}"
                f" QProgressBar::chunk {{ background-color: {t['page_bg']}; border-radius: {t['radius_sm']}px; }}")

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 创建
    # ─────────────────────────────────────────────────────────────────────────

    def _create_log_tab(self) -> QWidget:
        t = self._theme_engine.current_theme
        w = QWidget()
        l = QVBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(4)

        bar = QHBoxLayout()
        self.log_clear_btn = self._mk_btn("清空日志", 70, _btn_style(t, fg=t['text_tertiary']))
        self.log_clear_btn.clicked.connect(lambda: self.log_text.clear())
        bar.addWidget(self.log_clear_btn)
        bar.addStretch()

        self.log_diagnose_btn = self._mk_btn("🩺 AI故障诊断", 100, _ai_btn_style(t))
        self.log_diagnose_btn.clicked.connect(lambda: self.run_ai_diagnose("log"))
        bar.addWidget(self.log_diagnose_btn)

        self.log_info_lbl = QLabel("")
        self.log_info_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        bar.addWidget(self.log_info_lbl)
        l.addLayout(bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(self._text_edit_style())
        l.addWidget(self.log_text)
        w.setLayout(l)
        return w

    def _create_backup_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(8)

        # 左侧面板
        left = QVBoxLayout()
        left.setSpacing(4)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("设备筛选："))
        self.backup_filter_combo = QComboBox()
        self.backup_filter_combo.setMinimumWidth(140)
        self.backup_filter_combo.setStyleSheet(self._combo_small_style())
        self.backup_filter_combo.addItem("全部设备")
        self.backup_filter_combo.currentTextChanged.connect(self.on_backup_filter_changed)
        filter_row.addWidget(self.backup_filter_combo)
        left.addLayout(filter_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        for text, slot in [("🔄 刷新", self.refresh_backup_list),
                            ("📂 打开", self.on_open_backup_file),
                            ("🗑 删除", self.on_delete_backup_file)]:
            btn = self._mk_btn(text, 60, _btn_style(self._theme_engine.current_theme))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        self.backup_file_list = QListWidget()
        self.backup_file_list.setMinimumWidth(200)
        self.backup_file_list.setMaximumWidth(280)
        self.backup_file_list.setStyleSheet(self._list_widget_style())
        self.backup_file_list.currentItemChanged.connect(self.on_backup_file_selected)
        left.addWidget(self.backup_file_list, 1)
        l.addLayout(left, 0)

        # 右侧面板
        right = QVBoxLayout()
        right.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.backup_file_name_lbl = QLabel("未选择文件")
        self.backup_file_name_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.backup_file_name_lbl)
        info_bar.addStretch()

        self.ai_inspect_btn = self._mk_btn("🔍 AI合规巡检", 100, _ai_btn_style(t))
        self.ai_inspect_btn.clicked.connect(self.run_ai_inspect)
        info_bar.addWidget(self.ai_inspect_btn)
        right.addLayout(info_bar)

        self.backup_content = QTextEdit()
        self.backup_content.setReadOnly(True)
        self.backup_content.setStyleSheet(self._text_edit_style())
        self.backup_content.setPlaceholderText("选择左侧文件查看备份内容...")
        right.addWidget(self.backup_content, 1)
        l.addLayout(right, 1)

        w.setLayout(l)
        return w

    def _create_report_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(4)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("设备筛选："))
        self.report_filter_combo = QComboBox()
        self.report_filter_combo.setMinimumWidth(140)
        self.report_filter_combo.setStyleSheet(self._combo_small_style())
        self.report_filter_combo.addItem("全部设备")
        self.report_filter_combo.currentTextChanged.connect(self.on_report_filter_changed)
        filter_row.addWidget(self.report_filter_combo)
        left.addLayout(filter_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        for text, slot in [("🔄 刷新", self.refresh_report_list),
                            ("📂 打开", self.on_open_report_file),
                            ("🗑 删除", self.on_delete_report_file)]:
            btn = self._mk_btn(text, 60, _btn_style(self._theme_engine.current_theme))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        self.report_file_list = QListWidget()
        self.report_file_list.setMinimumWidth(200)
        self.report_file_list.setMaximumWidth(280)
        self.report_file_list.setStyleSheet(self._list_widget_style())
        self.report_file_list.currentItemChanged.connect(self.on_report_file_selected)
        left.addWidget(self.report_file_list, 1)
        l.addLayout(left, 0)

        right = QVBoxLayout()
        right.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.report_title_lbl = QLabel("未选择报告")
        self.report_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.report_title_lbl)
        info_bar.addStretch()

        self.report_ai_btn = self._mk_btn("🩺 AI故障诊断", 100, _ai_btn_style(t))
        self.report_ai_btn.clicked.connect(lambda: self.run_ai_diagnose("report"))
        self.report_ai_btn.setEnabled(False)
        info_bar.addWidget(self.report_ai_btn)
        right.addLayout(info_bar)

        self.report_content = QTextEdit()
        self.report_content.setReadOnly(True)
        self.report_content.setStyleSheet(self._text_edit_style())
        self.report_content.setPlaceholderText("选择左侧报告查看详情...")
        right.addWidget(self.report_content, 1)
        l.addLayout(right, 1)

        w.setLayout(l)
        return w

    def _create_diagnosis_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(6)

        left = QVBoxLayout()
        left.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        for text, slot in [("🔄 刷新", self.refresh_diagnosis_list),
                            ("📂 打开", self.on_open_diagnosis_file),
                            ("🗑 删除", self.on_delete_diagnosis_file)]:
            btn = self._mk_btn(text, 60, _btn_style(self._theme_engine.current_theme))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        self.diagnosis_file_list = QListWidget()
        self.diagnosis_file_list.setMinimumWidth(200)
        self.diagnosis_file_list.setMaximumWidth(280)
        self.diagnosis_file_list.setStyleSheet(self._list_widget_style())
        self.diagnosis_file_list.currentItemChanged.connect(self.on_diagnosis_file_selected)
        left.addWidget(self.diagnosis_file_list, 1)
        l.addLayout(left, 0)

        right = QVBoxLayout()
        right.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.diagnosis_title_lbl = QLabel("未选择报告")
        self.diagnosis_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.diagnosis_title_lbl)
        info_bar.addStretch()
        right.addLayout(info_bar)

        self.diagnosis_content = QTextEdit()
        self.diagnosis_content.setReadOnly(True)
        self.diagnosis_content.setStyleSheet(self._text_edit_style())
        self.diagnosis_content.setPlaceholderText("选择左侧诊断报告查看内容，或通过其他Tab的[🩺AI故障诊断]按钮生成新报告。")
        right.addWidget(self.diagnosis_content, 1)
        l.addLayout(right, 1)

        w.setLayout(l)
        return w

    def _create_compliance_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(6)

        left = QVBoxLayout()
        left.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        for text, slot in [("🔄 刷新", self.refresh_compliance_list),
                            ("📂 打开", self.on_open_compliance_file),
                            ("🗑 删除", self.on_delete_compliance_file)]:
            btn = self._mk_btn(text, 60, _btn_style(self._theme_engine.current_theme))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        self.compliance_file_list = QListWidget()
        self.compliance_file_list.setMinimumWidth(200)
        self.compliance_file_list.setMaximumWidth(280)
        self.compliance_file_list.setStyleSheet(self._list_widget_style())
        self.compliance_file_list.currentItemChanged.connect(self.on_compliance_file_selected)
        left.addWidget(self.compliance_file_list, 1)
        l.addLayout(left, 0)

        right = QVBoxLayout()
        right.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.compliance_title_lbl = QLabel("未选择报告")
        self.compliance_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.compliance_title_lbl)
        info_bar.addStretch()

        self.compliance_refine_btn = self._mk_btn("🩺 AI精审", 80, _ai_btn_style(t))
        self.compliance_refine_btn.clicked.connect(lambda: self.run_ai_diagnose("compliance"))
        self.compliance_refine_btn.setEnabled(False)
        info_bar.addWidget(self.compliance_refine_btn)
        right.addLayout(info_bar)

        self.compliance_content = QTextEdit()
        self.compliance_content.setReadOnly(True)
        self.compliance_content.setStyleSheet(self._text_edit_style())
        self.compliance_content.setPlaceholderText("选择左侧审计报告查看内容，或在【备份配置】Tab选中配置文件后点击[🔍AI合规巡检]生成新报告。")
        right.addWidget(self.compliance_content, 1)
        l.addLayout(right, 1)

        w.setLayout(l)
        return w

    # ─────────────────────────────────────────────────────────────────────────
    # 主题切换
    # ─────────────────────────────────────────────────────────────────────────

    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()

    def _apply_theme_style(self) -> None:
        if self._theme_engine is None:
            return
        t = self._theme_engine.current_theme
        self.setStyleSheet(f"SingleDevicePage {{ background-color: {t['page_bg']}; font-family: {t['font_ui']}; }}")
        if hasattr(self, 'table_group'):
            self.table_group.setStyleSheet(self._group_style())
        if hasattr(self, 'table'):
            self.table.setStyleSheet(self._table_style())
        if hasattr(self, 'result_tabs'):
            self.result_tabs.setStyleSheet(self._result_tabs_style())
        for attr, style_fn in [
            ('add_btn', lambda: _btn_style(t, fg=t['text_secondary'])),
            ('edit_btn', lambda: _btn_style(t, fg=t['text_secondary'])),
            ('del_btn', lambda: _btn_style(t)),
            ('clear_btn', lambda: _btn_style(t, fg=t['text_tertiary'])),
        ]:
            btn = getattr(self, attr, None)
            if btn is not None:
                btn.setStyleSheet(style_fn())
        for attr, fn in [('inspect_btn', self._primary_btn_style), ('backup_btn', self._secondary_btn_style),
                          ('test_btn', self._secondary_btn_style), ('cancel_btn', lambda: _btn_style(t))]:
            btn = getattr(self, attr, None)
            if btn is not None:
                btn.setStyleSheet(fn())
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setStyleSheet(self._progress_style())
        for attr in ('status_label', 'select_count_lbl'):
            lbl = getattr(self, attr, None)
            if lbl is not None:
                lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        if hasattr(self, 'desc_label'):
            self.desc_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding: 4px 0;")
        self._refresh_all_tabs()

    def _refresh_all_tabs(self) -> None:
        """刷新所有结果 Tab 的内部控件样式"""
        t = self._theme_engine.current_theme
        for i in range(self.result_tabs.count()):
            page = self.result_tabs.widget(i)
            if page is None:
                continue
            for lst in page.findChildren(QListWidget):
                lst.setStyleSheet(self._list_widget_style())
            for te in page.findChildren(QTextEdit):
                te.setStyleSheet(self._text_edit_style())
            for cb in page.findChildren(QComboBox):
                cb.setStyleSheet(self._combo_small_style())
            _page_del_btns = [getattr(page, a, None) for a in
                              ('backup_del_btn', 'report_del_btn', 'diagnosis_del_btn', 'compliance_del_btn')]
            for btn in page.findChildren(QPushButton):
                obj_name = btn.objectName()
                if 'del' in obj_name or btn in _page_del_btns:
                    btn.setStyleSheet(_btn_style(t))
                elif any(kw in obj_name for kw in ('ai_', 'inspect', 'diagnose', 'refine')):
                    btn.setStyleSheet(_ai_btn_style(t))
                else:
                    btn.setStyleSheet(_btn_style(t))
            for lbl in page.findChildren(QLabel):
                obj_name = lbl.objectName()
                if any(kw in obj_name for kw in ('_title_lbl', '_name_lbl')):
                    lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
                else:
                    lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")

    # ─────────────────────────────────────────────────────────────────────────
    # 设备表格操作
    # ─────────────────────────────────────────────────────────────────────────

    def _get_selected_devices(self) -> tuple:
        rows, devs = [], []
        for row in range(self.table.rowCount()):
            item = self.table.cellWidget(row, self.COL_CHECK)
            if item and isinstance(item, QCheckBox) and item.isChecked():
                data_item = self.table.item(row, self.COL_DATA)
                if data_item:
                    devs.append(data_item.data(Qt.UserRole))
                    rows.append(row)
        return rows, devs

    def _refresh_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.devices))
        for row, dev in enumerate(self.devices):
            chk = QCheckBox()
            chk.setStyleSheet("margin-left: 6px;")
            self.table.setCellWidget(row, self.COL_CHECK, chk)
            for col, key in [(self.COL_IP, "ip"), (self.COL_VENDOR, "vendor"),
                             (self.COL_TYPE, "device_type"), (self.COL_PROTO, "protocol"),
                             (self.COL_USER, "username"), (self.COL_STATUS, "last_status"),
                             (self.COL_TIME, "last_time")]:
                item = QTableWidgetItem(str(dev.get(key, "")))
                item.setTextAlignment(Qt.AlignCenter)
                if col == self.COL_STATUS:
                    icon = STATUS_ICONS.get(dev.get("status", ""), "")
                    if icon:
                        item.setText(icon)
                if col == self.COL_IP:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)
            data_item = QTableWidgetItem()
            data_item.setData(Qt.UserRole, dev)
            self.table.setItem(row, self.COL_DATA, data_item)
        self.table.blockSignals(False)
        self._update_select_count()
        self._refresh_device_filters()

    def _update_select_count(self):
        count = sum(1 for r in range(self.table.rowCount())
                     if self.table.cellWidget(r, self.COL_CHECK)
                     and isinstance(self.table.cellWidget(r, self.COL_CHECK), QCheckBox)
                     and self.table.cellWidget(r, self.COL_CHECK).isChecked())
        total = self.table.rowCount()
        self.select_count_lbl.setText(f"共 {total} 台 | 已选 {count} 台")
        line_count = self.log_text.document().blockCount() if hasattr(self, 'log_text') else 0
        if hasattr(self, 'log_info_lbl'):
            self.log_info_lbl.setText(f"{line_count} 行")

    def on_item_changed(self, item):
        if item.column() == self.COL_CHECK:
            self._update_select_count()

    def on_add_device(self):
        dialog = DeviceFormDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                self.devices.append(data)
                self._refresh_table()
                self._save_devices()
                self.log_append(f"✅ 已添加设备：{data['ip']} ({data['vendor']} {data['device_type']})")

    def on_edit_device(self):
        rows, _ = self._get_selected_devices()
        if not rows:
            if self.table.currentRow() >= 0:
                rows = [self.table.currentRow()]
            else:
                QMessageBox.information(self, "提示", "请先选择要编辑的设备行")
                return
        row = rows[0]
        data_item = self.table.item(row, self.COL_DATA)
        if not data_item:
            return
        dev = data_item.data(Qt.UserRole)
        dialog = DeviceFormDialog(self, dev)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data:
                new_data["last_status"] = dev.get("last_status", "")
                new_data["last_time"] = dev.get("last_time", "")
                self.devices[row] = new_data
                self._refresh_table()
                self._save_devices()
                self.log_append(f"✏️ 已更新设备：{new_data['ip']}")

    def on_delete_device(self):
        rows, _ = self._get_selected_devices()
        if not rows:
            QMessageBox.information(self, "提示", "请先勾选要删除的设备")
            return
        reply = QMessageBox.question(self, "确认删除",
                                     f'确定要删除选中的 {len(rows)} 台设备吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        for row in sorted(rows, reverse=True):
            del self.devices[row]
        self._refresh_table()
        self._save_devices()
        self.log_append(f"🗑️ 已删除 {len(rows)} 台设备")

    def on_clear_all(self):
        if not self.devices:
            return
        reply = QMessageBox.question(self, "确认清空",
                                     f'确定要清空全部 {len(self.devices)} 台设备吗？此操作不可恢复。',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.devices.clear()
        self._refresh_table()
        self._save_devices()
        self.log_append("🗑️ 已清空全部设备列表")

    def on_table_double_click(self, index):
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if col == self.COL_STATUS:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                ip = dev.get("ip", "")
                status = dev.get("last_status", "")
                if status == "success":
                    self.result_tabs.setCurrentIndex(TAB_BACKUP)
                    self._select_backup_by_ip(ip)
                elif status == "failed":
                    self.result_tabs.setCurrentIndex(TAB_LOG)
                return
        if col != self.COL_CHECK:
            self.edit_btn.click()

    def on_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu(self)
        edit_act = menu.addAction("✏️ 编辑此设备")
        del_act = menu.addAction("🗑️ 删除此设备")
        sel_act = menu.addAction("☑️ 选中此设备")
        view_bk = menu.addAction("💾 查看备份")
        view_rp = menu.addAction("📄 查看巡检报告")
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == edit_act:
            self.table.selectRow(row)
            self.on_edit_device()
        elif action == del_act:
            self.table.selectRow(row)
            rows, _ = self._get_selected_devices()
            if row not in rows:
                chk = self.table.cellWidget(row, self.COL_CHECK)
                if isinstance(chk, QCheckBox):
                    chk.setChecked(True)
            self.on_delete_device()
        elif action == sel_act:
            chk = self.table.cellWidget(row, self.COL_CHECK)
            if isinstance(chk, QCheckBox):
                chk.setChecked(not chk.isChecked())
        elif action == view_bk:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                self.result_tabs.setCurrentIndex(TAB_BACKUP)
                self._select_backup_by_ip(dev.get("ip", ""))
        elif action == view_rp:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                self.result_tabs.setCurrentIndex(TAB_REPORT)
                self._select_report_by_ip(dev.get("ip", ""))

    def _load_devices(self):
        raw = self._secure_cfg.load(SINGLE_DEVICES_PATH)
        if raw and isinstance(raw, dict):
            self.devices = raw.get("devices", [])
        self._refresh_table()

    def _save_devices(self):
        data = {"devices": self.devices, "updated": datetime.now().isoformat()}
        self._secure_cfg.save(SINGLE_DEVICES_PATH, data)

    # ─────────────────────────────────────────────────────────────────────────
    # 批量任务
    # ─────────────────────────────────────────────────────────────────────────

    def _set_buttons_enabled(self, enabled: bool):
        for attr in ('inspect_btn', 'backup_btn', 'test_btn', 'add_btn', 'edit_btn', 'del_btn'):
            btn = getattr(self, attr, None)
            if btn:
                btn.setEnabled(enabled)
        self.cancel_btn.setVisible(not enabled)

    def log_append(self, msg: str):
        ts = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.append(f"{ts} {msg}")
        self._update_select_count()

    def run_batch_inspect(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要巡检的设备")
            return
        self._start_batch_task("inspect", devs, rows, "批量巡检")

    def run_batch_backup(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要备份的设备")
            return
        self._start_batch_task("backup", devs, rows, "批量备份")

    def run_batch_test(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要测试的设备")
            return
        self._start_batch_task("test_connect", devs, rows, "批量测试连接")

    def _start_batch_task(self, task_type: str, devs: List[Dict], rows: List[int], label: str):
        self._set_buttons_enabled(False)
        self.log_text.clear()
        self.progress_bar.setMaximum(len(devs))
        self.progress_bar.setValue(0)
        self.status_label.setText(f"正在{label}... 共 {len(devs)} 台")
        self.result_tabs.setCurrentIndex(TAB_LOG)
        self.worker = SingleDeviceWorker(task_type, devs, rows)
        self.worker.progress_signal.connect(self.on_progress)
        self.worker.finished_signal.connect(self.on_task_finished)
        self.worker.error_signal.connect(self.on_task_error)
        self.worker.batch_progress.connect(self.on_batch_progress)
        self.worker.start()

    def on_progress(self, msg: str):
        self.log_append(msg)

    def _update_device_status(self, row_idx: int, success: bool):
        t = self._theme_engine.current_theme
        if row_idx >= len(self.devices):
            return
        self.devices[row_idx]["last_status"] = "success" if success else "failed"
        self.devices[row_idx]["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        status_item = self.table.item(row_idx, self.COL_STATUS)
        time_item = self.table.item(row_idx, self.COL_TIME)
        if status_item:
            status_item.setText("✅" if success else "❌")
            status_item.setForeground(QColor(t['success'] if success else t['danger']))
        if time_item:
            time_item.setText(self.devices[row_idx]["last_time"])

    def on_task_finished(self, row_idx: int, result: str, hint: str):
        self.log_append(result)
        self._update_device_status(row_idx, True)

    def on_task_error(self, row_idx: int, err_msg: str):
        self.log_append(f"❌ 错误：{err_msg}")
        self._update_device_status(row_idx, False)

    def on_batch_progress(self, current: int, total: int):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"执行中... {current}/{total}")
        if current >= total:
            self._on_batch_complete(total)

    def _on_batch_complete(self, total: int):
        self._set_buttons_enabled(True)
        self._save_devices()
        self.status_label.setText(f"✅ 全部完成！共处理 {total} 台设备")
        self.log_append(f"\n{'='*50}")
        self.log_append(f"✅ 批量任务完成！共 {total} 台设备处理完毕")
        self.log_append(f"{'='*50}")
        self.refresh_backup_list()
        self.refresh_report_list()

    def on_cancel_task(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.log_append("⚠️ 用户取消任务，等待当前设备完成...")

    # ─────────────────────────────────────────────────────────────────────────
    # AI 合规巡检
    # ─────────────────────────────────────────────────────────────────────────

    def run_ai_inspect(self):
        try:
            t = self._theme_engine.current_theme
            _set_ai_btn_state(self.ai_inspect_btn, "分析", enabled=False, loading=True)
            self.result_tabs.setCurrentIndex(TAB_LOG)
            self.log_append("=" * 60)
            self.log_append("🔍 AI合规巡检 — 启动中...")
            ai_config = get_active_ai_config()
            if not ai_config or not ai_config.get("base_url") or not ai_config.get("api_key"):
                self.log_append("⚠️ AI模型未配置，请在【⚙ 模型设置】中配置")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "请先在【⚙ 模型设置】中配置AI模型后再使用AI合规巡检功能。")
                return
            item = self.backup_file_list.currentItem()
            if not item:
                self.log_append("⚠️ 未选择备份文件")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "请先在左侧【备份配置】列表中选择一个配置文件。")
                return
            fp = item.data(Qt.UserRole)
            if not fp:
                self.log_append("⚠️ 备份文件路径无效")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "所选文件路径无效，请重新选择。")
                return
            self.log_append(f"📄 配置文件: {os.path.basename(fp)}")
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                self.log_append(f"❌ 读取文件失败: {str(e)}")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "读取失败", f"无法读取配置文件:\n{str(e)}")
                return
            if not content or len(content.strip()) < 50:
                self.log_append("⚠️ 配置文件内容为空或过短")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "配置文件内容为空或过短，无法进行合规审计。")
                return
            self.log_append(f"✅ 配置已加载 ({len(content):,} 字符)，启动AI分析...")
            self._start_ai_inspect(content, os.path.basename(fp), ai_config)
        except Exception as e:
            self.log_append(f"❌ 合规巡检启动异常: {type(e).__name__}: {str(e)}")
            self._restore_inspect_btn()
            QMessageBox.critical(self, "错误", f"合规巡检启动失败:\n{type(e).__name__}: {str(e)}")

    def _restore_inspect_btn(self):
        _set_ai_btn_state(self.ai_inspect_btn, "🔍 AI合规巡检", enabled=True)

    def _start_ai_inspect(self, config_content: str, filename: str, ai_config: Dict[str, Any]):
        self.log_append("🔍 AI合规巡检已启动，正在进行双层审计（本地预检 + AI精审）...")
        device_ip = ""
        item = self.backup_file_list.currentItem()
        if item:
            text = item.text()
            for d in self.devices:
                if d.get("ip", "") in text:
                    device_ip = d["ip"]
                    break
        thread = ComplianceCheckThread(config_content, device_ip, ai_config)
        self._ai_inspect_thread = thread
        thread.progress_signal.connect(self.log_append)
        thread.finished_signal.connect(self.on_ai_inspect_finished)
        thread.error_signal.connect(lambda msg: (
            self.log_append(f"❌ {msg}"),
            self._restore_inspect_btn()
        ))
        thread.local_result_signal.connect(self._show_local_audit_result)
        thread.start()

    def _show_local_audit_result(self, result_text: str):
        self.result_tabs.setCurrentIndex(TAB_BACKUP)
        self.backup_content.setPlainText(result_text)
        self.backup_file_name_lbl.setText("📋 本地预检结果")

    def on_ai_inspect_finished(self, report: str):
        self._restore_inspect_btn()
        comp_dir = os.path.join(get_single_dir(), "report", "compliance")
        os.makedirs(comp_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"compliance_{ts}.md"
        try:
            with open(os.path.join(comp_dir, fname), "w", encoding="utf-8") as f:
                f.write(report)
        except Exception:
            pass
        self.refresh_compliance_list()
        self.compliance_content.setPlainText(report)
        self.compliance_title_lbl.setText(f"📄 {fname}")
        self.result_tabs.setCurrentIndex(TAB_COMPLIANCE)
        self.log_append("✅ AI合规巡检完成")

    # ─────────────────────────────────────────────────────────────────────────
    # AI 故障诊断
    # ─────────────────────────────────────────────────────────────────────────

    def run_ai_diagnose(self, source_type: str):
        try:
            btn_map = {"report": self.report_ai_btn, "compliance": self.compliance_refine_btn, "log": self.log_diagnose_btn}
            active_btn = btn_map.get(source_type)
            if active_btn:
                _set_ai_btn_state(active_btn, "诊断", enabled=False, loading=True)
            self.result_tabs.setCurrentIndex(TAB_LOG)
            self.log_append("=" * 60)
            self.log_append("🩺 AI故障诊断 — 启动中...")
            ai_config = get_active_ai_config()
            if not ai_config or not ai_config.get("base_url") or not ai_config.get("api_key"):
                self.log_append("⚠️ AI模型未配置，请在【⚙ 模型设置】中配置")
                self._restore_diagnose_btn(source_type)
                QMessageBox.warning(self, "提示", "请先在【⚙ 模型设置】中配置AI模型后再使用AI故障诊断功能。")
                return
            content_map = {
                "backup": self.backup_content.toPlainText(),
                "report": self.report_content.toPlainText(),
                "compliance": self.compliance_content.toPlainText(),
                "log": self.log_text.toPlainText(),
            }
            content = content_map.get(source_type, "")
            if not content.strip():
                hints = {"backup": "请先选择一个备份配置文件", "report": "请先选择一份巡检报告",
                         "compliance": "请先选择一份审计报告", "log": "执行日志为空，请先执行操作"}
                self.log_append(f"⚠️ {hints.get(source_type, '没有可分析的内容')}")
                self._restore_diagnose_btn(source_type)
                QMessageBox.warning(self, "提示", hints.get(source_type, "没有可分析的内容"))
                return
            self.log_append(f"📄 数据来源: {source_type} ({len(content):,} 字符)")
            self.log_append("✅ 数据已加载，启动AI诊断引擎...")
            thread = AIDiagnosticThread(content, source_type, ai_config)
            self._ai_diagnose_thread = thread
            thread.progress_signal.connect(self.log_append)
            thread.finished_signal.connect(lambda r: self._on_diagnose_finished(r, source_type))
            thread.error_signal.connect(lambda msg: self._on_diagnose_error(msg, source_type))
            thread.start()
        except Exception as e:
            self.log_append(f"❌ 故障诊断启动异常: {type(e).__name__}: {str(e)}")
            self._restore_diagnose_btn(source_type)
            QMessageBox.critical(self, "错误", f"故障诊断启动失败:\n{type(e).__name__}: {str(e)}")

    def _restore_diagnose_btn(self, source_type: str):
        text_map = {"report": "🩺 AI故障诊断", "compliance": "🩺 AI精审", "log": "🩺 AI故障诊断"}
        btn_map = {"report": self.report_ai_btn, "compliance": self.compliance_refine_btn, "log": self.log_diagnose_btn}
        btn = btn_map.get(source_type)
        if btn:
            _set_ai_btn_state(btn, text_map.get(source_type, "🩺 AI故障诊断"), enabled=True)

    def _on_diagnose_error(self, msg: str, source_type: str):
        try:
            self.log_append(f"❌ {msg}")
        except Exception:
            pass
        try:
            self._restore_diagnose_btn(source_type)
        except Exception as e:
            logger.warning(f"恢复诊断按钮异常: {e}")
        QMessageBox.warning(self, "AI诊断失败", f"故障诊断过程中出现错误：\n\n{msg}")

    def _on_diagnose_finished(self, report: str, source_type: str):
        _dbg_fp = os.path.join(get_app_dir(), "logs", "diagnosis_debug.log")
        def _cb_log(msg):
            try:
                os.makedirs(os.path.dirname(_dbg_fp), exist_ok=True)
                with open(_dbg_fp, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [CB] {msg}\n")
            except Exception:
                pass
        try:
            _cb_log("_on_diagnose_finished START")
            try:
                diag_dir = os.path.join(get_single_dir(), "report", "diagnosis")
                os.makedirs(diag_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"diagnosis_{ts}.md"
                with open(os.path.join(diag_dir, fname), "w", encoding="utf-8") as f:
                    f.write(report)
                _cb_log(f"report saved: {fname}")
            except Exception as write_err:
                _cb_log(f"write file error: {write_err}")
                fname = "诊断报告"
            try:
                _cb_log("refreshing diagnosis list...")
                self.refresh_diagnosis_list()
            except Exception as refresh_err:
                _cb_log(f"refresh list error: {type(refresh_err).__name__}: {refresh_err}")
            try:
                _cb_log("setting content to diagnosis widget...")
                self.diagnosis_content.setPlainText(report)
                self.diagnosis_title_lbl.setText(f"📄 {fname}")
            except Exception as content_err:
                _cb_log(f"set content error: {type(content_err).__name__}: {content_err}")
            try:
                _cb_log("switching to diagnosis tab...")
                self.result_tabs.setCurrentIndex(TAB_DIAGNOSIS)
            except Exception as tab_err:
                _cb_log(f"switch tab error: {type(tab_err).__name__}: {tab_err}")
            try:
                _cb_log("restoring button state...")
                self._restore_diagnose_btn(source_type)
            except Exception as btn_err:
                _cb_log(f"restore btn error: {type(btn_err).__name__}: {btn_err}")
            try:
                self.log_append("✅ AI故障诊断完成")
            except Exception:
                pass
            _cb_log("_on_diagnose_finished END OK")
        except Exception as e:
            _cb_log(f"_on_diagnose_finished CRASH: {type(e).__name__}: {str(e)[:500]}")
            import traceback
            _cb_log(traceback.format_exc())
            logger.error(f"诊断完成回调崩溃: {type(e).__name__}: {str(e)}")
            try:
                self._restore_diagnose_btn(source_type)
            except Exception:
                pass
            try:
                self.log_append(f"⚠️ 诊断报告已生成但显示异常: {type(e).__name__}")
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # 设备筛选
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh_device_filters(self):
        ips = sorted(set(d.get("ip", "") for d in self.devices if d.get("ip")))
        for combo in [self.backup_filter_combo, self.report_filter_combo]:
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("全部设备")
            combo.addItems(ips)
            if current and (current in ips or current == "全部设备"):
                combo.setCurrentText(current)
            combo.blockSignals(False)

    # ─────────────────────────────────────────────────────────────────────────
    # 备份配置 Tab
    # ─────────────────────────────────────────────────────────────────────────

    def _get_backup_dir(self) -> str:
        return os.path.join(get_single_dir(), "config_backup")

    def refresh_backup_list(self):
        _refresh_file_list(self.backup_file_list, self._get_backup_dir(),
                           self.backup_filter_combo, "暂无备份文件")

    def on_backup_filter_changed(self, _text: str):
        self.refresh_backup_list()

    def on_backup_file_selected(self, item: QListWidgetItem):
        if not item or not item.data(Qt.UserRole):
            self.backup_content.clear()
            self.backup_file_name_lbl.setText("未选择文件")
            self.ai_inspect_btn.setEnabled(False)
            return
        fp = item.data(Qt.UserRole)
        self.backup_file_name_lbl.setText(f"📄 {os.path.basename(fp)}")
        self.ai_inspect_btn.setEnabled(True)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if len(content) > 500000:
                self.backup_content.setPlainText(content[:500000] + f"\n\n... 文件过大，已截断显示（共 {len(content):,} 字符）")
            else:
                self.backup_content.setPlainText(content)
        except Exception as e:
            self.backup_content.setPlainText(f"读取失败：{str(e)}")

    def _select_backup_by_ip(self, ip: str):
        idx = self.backup_filter_combo.findText(ip)
        if idx >= 0:
            self.backup_filter_combo.setCurrentIndex(idx)
        self.refresh_backup_list()
        if self.backup_file_list.count() > 0:
            self.backup_file_list.setCurrentRow(0)

    def on_open_backup_file(self):
        _open_file(self.backup_file_list)

    def on_delete_backup_file(self):
        _delete_file(self.backup_file_list, self.refresh_backup_list, "备份文件")

    # ─────────────────────────────────────────────────────────────────────────
    # 巡检报告 Tab
    # ─────────────────────────────────────────────────────────────────────────

    def _get_report_dir(self) -> str:
        return os.path.join(get_single_dir(), "report", "single_inspect")

    def refresh_report_list(self):
        _refresh_file_list(self.report_file_list, self._get_report_dir(),
                           self.report_filter_combo, "暂无巡检报告")

    def on_report_filter_changed(self, _text: str):
        self.refresh_report_list()

    def on_report_file_selected(self, item: QListWidgetItem):
        if not item or not item.data(Qt.UserRole):
            self.report_content.clear()
            self.report_title_lbl.setText("未选择报告")
            self.report_ai_btn.setEnabled(False)
            return
        fp = item.data(Qt.UserRole)
        self.report_title_lbl.setText(f"📄 {os.path.basename(fp)}")
        self.report_ai_btn.setEnabled(True)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.report_content.setPlainText(content)
        except Exception as e:
            self.report_content.setPlainText(f"读取失败：{str(e)}")

    def _select_report_by_ip(self, ip: str):
        idx = self.report_filter_combo.findText(ip)
        if idx >= 0:
            self.report_filter_combo.setCurrentIndex(idx)
        self.refresh_report_list()
        if self.report_file_list.count() > 0:
            self.report_file_list.setCurrentRow(0)

    def on_open_report_file(self):
        _open_file(self.report_file_list)

    def on_delete_report_file(self):
        _delete_file(self.report_file_list, self.refresh_report_list, "报告文件")

    def on_open_report_dir(self):
        rdir = self._get_report_dir()
        os.makedirs(rdir, exist_ok=True)
        os.startfile(rdir)

    # ─────────────────────────────────────────────────────────────────────────
    # 诊断报告 Tab
    # ─────────────────────────────────────────────────────────────────────────

    def refresh_diagnosis_list(self):
        _refresh_file_list(self.diagnosis_file_list,
                           os.path.join(get_single_dir(), "report", "diagnosis"),
                           placeholder="暂无诊断报告")

    def on_diagnosis_file_selected(self, current, previous):
        if not current or not current.data(Qt.UserRole):
            self.diagnosis_title_lbl.setText("未选择报告")
            return
        fp = current.data(Qt.UserRole)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.diagnosis_title_lbl.setText(f"📄 {os.path.basename(fp)}")
            self.diagnosis_content.setPlainText(content)
        except Exception as e:
            self.diagnosis_content.setPlainText(f"读取诊断报告失败：{str(e)}")

    def on_open_diagnosis_file(self):
        _open_file(self.diagnosis_file_list)

    def on_delete_diagnosis_file(self):
        _delete_file(self.diagnosis_file_list, self.refresh_diagnosis_list, "诊断报告")

    # ─────────────────────────────────────────────────────────────────────────
    # 合规审计 Tab
    # ─────────────────────────────────────────────────────────────────────────

    def refresh_compliance_list(self):
        _refresh_file_list(self.compliance_file_list,
                           os.path.join(get_single_dir(), "report", "compliance"),
                           placeholder="暂无审计报告")

    def on_compliance_file_selected(self, current, previous):
        if not current or not current.data(Qt.UserRole):
            self.compliance_refine_btn.setEnabled(False)
            return
        self.compliance_refine_btn.setEnabled(True)
        fp = current.data(Qt.UserRole)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                report = f.read()
            styled = self._style_compliance_report(report)
            self.compliance_title_lbl.setText(f"📄 {os.path.basename(fp)}")
            self.compliance_content.setHtml(styled)
        except Exception as e:
            self.compliance_content.setPlainText(f"读取审计报告失败：{str(e)}")

    def on_open_compliance_file(self):
        _open_file(self.compliance_file_list)

    def on_open_compliance_dir(self):
        comp_dir = os.path.join(get_single_dir(), "report", "compliance")
        os.makedirs(comp_dir, exist_ok=True)
        os.startfile(comp_dir)

    def on_delete_compliance_file(self):
        item = self.compliance_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        name = os.path.basename(fp)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除审计报告「{name}」吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(fp)
            self.refresh_compliance_list()
            self.compliance_title_lbl.setText("未选择文件")
            self.compliance_content.clear()
            self.log_text.append(f"🗑 已删除审计报告：{name}")
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"无法删除文件：{str(e)}")

    # ─────────────────────────────────────────────────────────────────────────
    # 合规报告 HTML 样式
    # ─────────────────────────────────────────────────────────────────────────

    def _style_compliance_report(self, report: str) -> str:
        t = self._theme_engine.current_theme
        html = "<div style='font-family: Microsoft YaHei, sans-serif; line-height: 1.7;'>"
        for line in report.split("\n"):
            stripped = line.strip()
            if stripped.startswith("### CRITICAL") or "[CRITICAL-" in stripped:
                html += f"<p style='color: {t['text_secondary']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### HIGH") or "[HIGH-" in stripped:
                html += f"<p style='color: {t['warning']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### MEDIUM") or "[MEDIUM-" in stripped:
                html += f"<p style='color: {t['warning']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### LOW") or "[LOW-" in stripped:
                html += f"<p style='color: {t['text_tertiary']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif "Verdict:" in stripped or "判定:" in stripped:
                if "PASS" in stripped or "通过" in stripped:
                    html += f"<p style='color: {t['success']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['success_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                elif "BLOCK" in stripped or "阻止" in stripped:
                    html += f"<p style='color: {t['text_secondary']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['danger_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                elif "WARNING" in stripped or "警告" in stripped:
                    html += f"<p style='color: {t['warning']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['warning_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                else:
                    html += f"<p style='margin: 4px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("#"):
                html += f"<p style='color: {t['text_secondary']}; font-weight: bold; font-size: 11pt; margin-top: 10px;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("|"):
                html += f"<p style='color: {t['text_secondary']}; margin: 2px 0; font-family: Consolas, monospace;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("---"):
                html += f"<hr style='border: none; border-top: 1px solid {t['border']}; margin: 8px 0;'/>"
            else:
                html += f"<p style='margin: 2px 0; color: {t['text_main']};'>{self._escape_html(line)}</p>"
        html += "</div>"
        return html

    @staticmethod
    def _escape_html(text: str) -> str:
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;").replace(" ", "&nbsp;"))
