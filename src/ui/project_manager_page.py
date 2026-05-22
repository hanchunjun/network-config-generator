import os
import json
import subprocess
import platform
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QTextEdit, QMessageBox, QFileDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QAbstractItemView,
                               QMenu, QAction, QCheckBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QKeySequence

from src.utils.resource_path import get_config_path, get_app_dir
from src.core.device_manager import DeviceManager, VENDORS, DEVICE_TYPES, PROTOCOLS, DEVICE_HEADERS, DEVICE_TEMPLATES
from src.ui.device_form_dialog import DeviceFormDialog
from src.ui.device_discovery_dialog import DeviceDiscoveryDialog
from src.ui.device_template_dialog import DeviceTemplateDialog
from src.ui.history_dialog import HistoryDialog
from src.core.logger import netops_logger
from src.utils.validators import ProjectValidator, DeviceValidator
from src.utils.file_operators import JSONFileManager

PROJECTS_DIR = os.path.join(get_app_dir(), "projects")
PROJECTS_CONFIG = get_config_path("config/projects_config.json")

PROJECT_SUBDIRS = ["config", "output", "output/single_exception", "output/trouble_check_result",
                   "report", "report/single_inspect", "report/diagnosis", "report/compliance",
                   "config_backup"]


class ConnectionTestWorker(QThread):
    result_ready = pyqtSignal(str, str, bool, str)

    def __init__(self, ip, protocol, username, password):
        super().__init__()
        self.ip = ip
        self.protocol = protocol
        self.username = username
        self.password = password

    def run(self):
        ping_ok = self._test_ping()
        if not ping_ok:
            self.result_ready.emit(self.ip, "ping", False, "无法Ping通")
            self.result_ready.emit(self.ip, "ssh", False, "Ping失败，跳过SSH测试")
            return

        self.result_ready.emit(self.ip, "ping", True, "Ping成功")

        if self.protocol == "ssh":
            try:
                from netmiko import ConnectHandler
                device = {
                    "device_type": "cisco_ios" if self.protocol == "ssh" else "cisco_ios_telnet",
                    "host": self.ip,
                    "username": self.username,
                    "password": self.password,
                    "timeout": 10,
                }
                conn = ConnectHandler(**device)
                conn.disconnect()
                self.result_ready.emit(self.ip, "ssh", True, "SSH连接成功")
            except Exception as e:
                self.result_ready.emit(self.ip, "ssh", False, f"SSH失败: {str(e)[:80]}")
        else:
            try:
                from netmiko import ConnectHandler
                device = {
                    "device_type": "cisco_ios_telnet",
                    "host": self.ip,
                    "username": self.username,
                    "password": self.password,
                    "timeout": 10,
                }
                conn = ConnectHandler(**device)
                conn.disconnect()
                self.result_ready.emit(self.ip, "telnet", True, "Telnet连接成功")
            except Exception as e:
                self.result_ready.emit(self.ip, "telnet", False, f"Telnet失败: {str(e)[:80]}")

    def _test_ping(self):
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
            cmd = ["ping", param, "1", timeout_param, "2", self.ip]
            startupinfo = None
            if platform.system().lower() == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    startupinfo=startupinfo, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


class ProjectManagerPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_project = None
        self.device_manager = DeviceManager()
        self._show_passwords = False
        self._group_filter = "全部"
        self.init_ui()
        self.refresh_project_list()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        workspace_group = QGroupBox("项目工作区")
        workspace_group.setStyleSheet(self._group_style())
        workspace_layout = QVBoxLayout()
        workspace_layout.setContentsMargins(14, 6, 14, 10)
        workspace_layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        create_section = QVBoxLayout()
        create_section.setSpacing(4)
        create_header = QLabel("新建项目")
        create_header.setStyleSheet("font-size: 10pt; font-weight: bold; color: #1D2129;")
        create_section.addWidget(create_header)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        name_label = QLabel("项目名称")
        name_label.setFixedWidth(60)
        name_label.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
        input_layout.addWidget(name_label)
        self.project_name_input = QLineEdit()
        self.project_name_input.setFixedWidth(240)
        self.project_name_input.setFixedHeight(28)
        self.project_name_input.setPlaceholderText("请输入项目名称，如：栖霞区电子政务外网项目")
        self.project_name_input.setStyleSheet(self._input_style())
        input_layout.addWidget(self.project_name_input)

        self.create_btn = QPushButton("创建项目")
        self.create_btn.setFixedSize(88, 28)
        self.create_btn.setStyleSheet(self._primary_btn_style())
        self.create_btn.clicked.connect(self.create_project)
        input_layout.addWidget(self.create_btn)
        input_layout.addStretch()
        create_section.addLayout(input_layout)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(6)
        path_label = QLabel("存储路径")
        path_label.setFixedWidth(60)
        path_label.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
        path_layout.addWidget(path_label)
        self.path_label = QLabel(PROJECTS_DIR)
        self.path_label.setStyleSheet("font-size: 11px; color: #86909C;")
        path_layout.addWidget(self.path_label)
        path_layout.addStretch()
        create_section.addLayout(path_layout)

        top_row.addLayout(create_section, stretch=2)

        overview_section = QVBoxLayout()
        overview_section.setSpacing(4)
        overview_header_row = QHBoxLayout()
        overview_header_row.setSpacing(12)
        overview_header = QLabel("项目总览")
        overview_header.setStyleSheet("font-size: 10pt; font-weight: bold; color: #1D2129;")
        overview_header_row.addWidget(overview_header)
        self.overview_stats_label = QLabel("")
        self.overview_stats_label.setStyleSheet("font-size: 11px; color: #86909C; font-weight: normal;")
        overview_header_row.addWidget(self.overview_stats_label)
        overview_header_row.addStretch()
        overview_section.addLayout(overview_header_row)

        self.overview_cards_layout = QHBoxLayout()
        self.overview_cards_layout.setSpacing(6)
        overview_section.addLayout(self.overview_cards_layout)
        overview_section.addStretch()

        top_row.addLayout(overview_section, stretch=3)
        workspace_layout.addLayout(top_row)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { color: #E5E6EB; max-height: 1px; }")
        workspace_layout.addWidget(separator)

        console_layout = QHBoxLayout()
        console_layout.setSpacing(8)

        switch_label = QLabel("当前项目")
        switch_label.setFixedWidth(60)
        switch_label.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
        console_layout.addWidget(switch_label)
        self.project_combo = QComboBox()
        self.project_combo.setFixedWidth(280)
        self.project_combo.setFixedHeight(28)
        self.project_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 2px 10px;
                font-size: 9pt;
                background-color: #F5F7FA;
            }
            QComboBox:hover { border: 1px solid #165DFF; }
            QComboBox::drop-down { border: none; }
        """)
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        console_layout.addWidget(self.project_combo)

        self.switch_btn = QPushButton("切换")
        self.switch_btn.setFixedSize(56, 28)
        self.switch_btn.setStyleSheet(self._primary_btn_style())
        self.switch_btn.clicked.connect(self.switch_project)
        console_layout.addWidget(self.switch_btn)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedSize(56, 28)
        self.refresh_btn.setStyleSheet(self._secondary_btn_style())
        self.refresh_btn.clicked.connect(self.refresh_project_list)
        console_layout.addWidget(self.refresh_btn)

        self.edit_project_btn = QPushButton("编辑")
        self.edit_project_btn.setFixedSize(56, 28)
        self.edit_project_btn.setStyleSheet(self._secondary_btn_style())
        self.edit_project_btn.clicked.connect(self.edit_project)
        console_layout.addWidget(self.edit_project_btn)

        self.delete_project_btn = QPushButton("删除")
        self.delete_project_btn.setFixedSize(56, 28)
        self.delete_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF2F0; border: 1px solid #F53F3F;
                border-radius: 4px; font-size: 9pt; color: #F53F3F;
            }
            QPushButton:hover { background-color: #FFECE8; }
        """)
        self.delete_project_btn.clicked.connect(self.delete_project)
        console_layout.addWidget(self.delete_project_btn)

        self.info_path = QLabel("项目路径：未选择")
        self.info_path.setStyleSheet("font-size: 11px; color: #86909C; font-weight: normal;")
        console_layout.addWidget(self.info_path)
        self.info_devices = QLabel("设备数量：0")
        self.info_devices.setStyleSheet("font-size: 11px; color: #86909C; font-weight: normal;")
        console_layout.addWidget(self.info_devices)
        self.info_logs = QLabel("运维日志：0")
        self.info_logs.setStyleSheet("font-size: 11px; color: #86909C; font-weight: normal;")
        console_layout.addWidget(self.info_logs)

        console_layout.addStretch()
        workspace_layout.addLayout(console_layout)

        workspace_group.setLayout(workspace_layout)
        layout.addWidget(workspace_group)

        device_group = QGroupBox("设备清单管理")
        device_group.setStyleSheet(self._group_style())
        device_layout = QVBoxLayout()
        device_layout.setSpacing(6)

        table_btn_layout = QHBoxLayout()
        table_btn_layout.setSpacing(8)

        self.add_row_btn = QPushButton("新增设备")
        self.add_row_btn.setFixedSize(90, 36)
        self.add_row_btn.setStyleSheet(self._primary_btn_style())
        self.add_row_btn.clicked.connect(self.add_device_dialog)
        table_btn_layout.addWidget(self.add_row_btn)

        self.edit_btn = QPushButton("编辑设备")
        self.edit_btn.setFixedSize(90, 36)
        self.edit_btn.setStyleSheet(self._secondary_btn_style())
        self.edit_btn.clicked.connect(self.edit_device_dialog)
        table_btn_layout.addWidget(self.edit_btn)

        self.del_row_btn = QPushButton("删除选中")
        self.del_row_btn.setFixedSize(90, 36)
        self.del_row_btn.setStyleSheet(self._secondary_btn_style())
        self.del_row_btn.clicked.connect(self.delete_device_row)
        table_btn_layout.addWidget(self.del_row_btn)

        self.save_device_btn = QPushButton("保存清单")
        self.save_device_btn.setFixedSize(90, 36)
        self.save_device_btn.setStyleSheet(self._primary_btn_style())
        self.save_device_btn.clicked.connect(self.save_device_list)
        table_btn_layout.addWidget(self.save_device_btn)

        self.import_btn = QPushButton("导入")
        self.import_btn.setFixedSize(70, 36)
        self.import_btn.setStyleSheet(self._secondary_btn_style())
        self.import_btn.clicked.connect(self.import_device_list)
        table_btn_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("导出")
        self.export_btn.setFixedSize(70, 36)
        self.export_btn.setStyleSheet(self._secondary_btn_style())
        self.export_btn.clicked.connect(self.export_device_list)
        table_btn_layout.addWidget(self.export_btn)

        self.template_btn = QPushButton("下载模板")
        self.template_btn.setFixedSize(90, 36)
        self.template_btn.setStyleSheet(self._secondary_btn_style())
        self.template_btn.clicked.connect(self.download_template)
        table_btn_layout.addWidget(self.template_btn)

        self.template_lib_btn = QPushButton("模板库")
        self.template_lib_btn.setFixedSize(80, 36)
        self.template_lib_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0F5FF; border: 1px solid #165DFF;
                border-radius: 4px; font-size: 10pt; color: #165DFF;
            }
            QPushButton:hover { background-color: #E0EAFF; }
        """)
        self.template_lib_btn.clicked.connect(self.open_template_library)
        table_btn_layout.addWidget(self.template_lib_btn)

        self.discover_btn = QPushButton("批量发现")
        self.discover_btn.setFixedSize(90, 36)
        self.discover_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8FFEA; border: 1px solid #00B42A;
                border-radius: 4px; font-size: 10pt; color: #00B42A;
            }
            QPushButton:hover { background-color: #D0F5D3; }
        """)
        self.discover_btn.clicked.connect(self.open_discovery)
        table_btn_layout.addWidget(self.discover_btn)

        self.test_conn_btn = QPushButton("连接测试")
        self.test_conn_btn.setFixedSize(90, 36)
        self.test_conn_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF7E6; border: 1px solid #FF7D00;
                border-radius: 4px; font-size: 10pt; color: #FF7D00;
            }
            QPushButton:hover { background-color: #FFECD2; }
        """)
        self.test_conn_btn.clicked.connect(self.test_connection)
        table_btn_layout.addWidget(self.test_conn_btn)

        self.history_btn = QPushButton("变更历史")
        self.history_btn.setFixedSize(90, 36)
        self.history_btn.setStyleSheet(self._secondary_btn_style())
        self.history_btn.clicked.connect(self.show_history)
        table_btn_layout.addWidget(self.history_btn)

        table_btn_layout.addStretch()
        device_layout.addLayout(table_btn_layout)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        filter_layout.addWidget(QLabel("分组筛选："))
        self.group_filter_combo = QComboBox()
        self.group_filter_combo.setFixedWidth(180)
        self.group_filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB; border-radius: 4px;
                padding: 6px 10px; font-size: 10pt; background-color: #FFFFFF;
            }
            QComboBox:hover { border: 1px solid #165DFF; }
            QComboBox::drop-down { border: none; }
        """)
        self.group_filter_combo.currentTextChanged.connect(self._on_group_filter_changed)
        filter_layout.addWidget(self.group_filter_combo)

        self.show_pwd_cb = QCheckBox("显示密码")
        self.show_pwd_cb.setStyleSheet("font-size: 10pt;")
        self.show_pwd_cb.stateChanged.connect(self._toggle_password_display)
        filter_layout.addWidget(self.show_pwd_cb)
        filter_layout.addStretch()

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 10pt; color: #86909C;")
        filter_layout.addWidget(self.stats_label)
        device_layout.addLayout(filter_layout)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(9)
        self.device_table.setHorizontalHeaderLabels(DEVICE_HEADERS)
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.device_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.device_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.device_table.customContextMenuRequested.connect(self._show_context_menu)
        self.device_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                background-color: #FFFFFF;
                gridline-color: #F2F3F5;
            }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background-color: #F7F8FA;
                border: none;
                border-bottom: 1px solid #E5E6EB;
                padding: 8px;
                font-weight: bold;
                color: #1D2129;
            }
        """)
        device_layout.addWidget(self.device_table)

        device_group.setLayout(device_layout)
        layout.addWidget(device_group, stretch=1)

        self.setLayout(layout)

    def _group_style(self):
        return """
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #1D2129;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                margin-top: 10px;
                padding: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """

    def _input_style(self):
        return """
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: #F5F7FA;
            }
            QLineEdit:focus { border: 1px solid #165DFF; }
        """

    def _primary_btn_style(self):
        return """
            QPushButton {
                background-color: #165DFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #0E42D2; }
        """

    def _secondary_btn_style(self):
        return """
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover { border: 1px solid #165DFF; }
        """

    def _get_projects_config(self):
        if os.path.exists(PROJECTS_CONFIG):
            with open(PROJECTS_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"projects": {}, "current": None}

    def _save_projects_config(self, config):
        with open(PROJECTS_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def refresh_project_list(self):
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("-- 请选择项目 --")

        config = self._get_projects_config()
        projects = config.get("projects", {})

        if not projects and os.path.exists(PROJECTS_DIR):
            for item in os.listdir(PROJECTS_DIR):
                item_path = os.path.join(PROJECTS_DIR, item)
                if os.path.isdir(item_path):
                    projects[item] = item_path
            config["projects"] = projects
            self._save_projects_config(config)

        for name in projects:
            path = projects[name]
            if os.path.exists(path):
                self.project_combo.addItem(name)

        current = config.get("current")
        if current and current in projects:
            idx = self.project_combo.findText(current)
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
                self.current_project = projects[current]
                self._update_project_info()

        self.project_combo.blockSignals(False)
        self._refresh_overview()

    def on_project_changed(self, index):
        pass

    def switch_project(self):
        name = self.project_combo.currentText()
        if name == "-- 请选择项目--":
            QMessageBox.warning(self, "提示", "请先选择一个项目")
            return

        config = self._get_projects_config()
        projects = config.get("projects", {})
        if name in projects:
            config["current"] = name
            self._save_projects_config(config)
            self.current_project = projects[name]
            self._update_project_info()
            if hasattr(self.parent, 'current_project'):
                self.parent.current_project = self.current_project
            if hasattr(self.parent, 'refresh_project_status'):
                self.parent.refresh_project_status()
            QMessageBox.information(self, "切换成功", f"已切换到项目：{name}")

    def edit_project(self):
        name = self.project_combo.currentText()
        if name == "-- 请选择项目--":
            QMessageBox.warning(self, "提示", "请先选择一个项目")
            return

        config = self._get_projects_config()
        projects = config.get("projects", {})
        if name not in projects:
            QMessageBox.warning(self, "提示", "项目不存在")
            return

        from PyQt5.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "编辑项目", "请输入新的项目名称：", text=name)
        if not ok or not new_name.strip() or new_name.strip() == name:
            return

        new_name = new_name.strip()
        if new_name in projects:
            QMessageBox.warning(self, "提示", f"项目名称 '{new_name}' 已存在")
            return

        old_path = projects[name]
        parent_dir = os.path.dirname(old_path)
        new_path = os.path.join(parent_dir, new_name)

        try:
            os.rename(old_path, new_path)
            del projects[name]
            projects[new_name] = new_path
            if config.get("current") == name:
                config["current"] = new_name
            self._save_projects_config(config)
            self.current_project = new_path
            if hasattr(self.parent, 'current_project'):
                self.parent.current_project = self.current_project
            self.refresh_project_list()
            self._update_project_info()
            QMessageBox.information(self, "编辑成功", f"项目已重命名为：{new_name}")
        except Exception as e:
            QMessageBox.critical(self, "编辑失败", f"重命名失败：{str(e)}")

    def delete_project(self):
        name = self.project_combo.currentText()
        if name == "-- 请选择项目--":
            QMessageBox.warning(self, "提示", "请先选择一个项目")
            return

        config = self._get_projects_config()
        projects = config.get("projects", {})
        if name not in projects:
            QMessageBox.warning(self, "提示", "项目不存在")
            return

        project_path = projects[name]
        reply = QMessageBox.warning(self, "确认删除",
            f"确定要删除项目 '{name}' 吗？\n\n"
            f"项目路径：{project_path}\n"
            f"此操作将删除项目目录下的所有文件，不可恢复！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply != QMessageBox.Yes:
            return

        reply2 = QMessageBox.warning(self, "再次确认",
            f"请再次确认：真的要删除项目 '{name}' 吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply2 != QMessageBox.Yes:
            return

        try:
            import shutil
            shutil.rmtree(project_path)
            del projects[name]
            if config.get("current") == name:
                config["current"] = None
            self._save_projects_config(config)
            self.current_project = None
            if hasattr(self.parent, 'current_project'):
                self.parent.current_project = None
            if hasattr(self.parent, 'refresh_project_status'):
                self.parent.refresh_project_status()
            self.refresh_project_list()
            self._update_project_info()
            QMessageBox.information(self, "删除成功", f"项目 '{name}' 已删除")
        except Exception as e:
            QMessageBox.critical(self, "删除失败", f"删除项目失败：{str(e)}")

    def create_project(self):
        name = self.project_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入项目名称")
            return

        existing = self._get_projects_config().get("projects", {})
        existing_names = list(existing.keys())
        prefix = f"{len(existing_names) + 1:02d}_"
        full_name = prefix + name

        project_path = os.path.join(PROJECTS_DIR, full_name)
        if os.path.exists(project_path):
            QMessageBox.warning(self, "提示", f"项目目录已存在：{full_name}")
            return

        try:
            os.makedirs(project_path, exist_ok=True)
            for subdir in PROJECT_SUBDIRS:
                os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

            device_list_path = os.path.join(project_path, "config", "device_list.txt")
            with open(device_list_path, "w", encoding="utf-8") as f:
                f.write("# 格式：IP,厂商,设备类型,用户名,密码,协议,特权密码,分组,标签\n")
                f.write(f"# 项目：{name}\n")

            config = self._get_projects_config()
            config["projects"][full_name] = project_path
            config["current"] = full_name
            self._save_projects_config(config)

            self.current_project = project_path
            if hasattr(self.parent, 'current_project'):
                self.parent.current_project = self.current_project
            if hasattr(self.parent, 'refresh_project_status'):
                self.parent.refresh_project_status()

            self.project_name_input.clear()
            self.refresh_project_list()
            self._update_project_info()
            QMessageBox.information(self, "创建成功", f"项目 '{full_name}' 创建成功！\n路径：{project_path}")
        except Exception as e:
            QMessageBox.critical(self, "创建失败", f"项目创建失败：{str(e)}")

    def _update_project_info(self):
        if not self.current_project:
            self.info_path.setText("项目路径：未选择")
            self.info_devices.setText("设备数量：0")
            self.info_logs.setText("运维日志：0")
            self._clear_device_table()
            self.stats_label.setText("")
            return

        self.info_path.setText(f"项目路径：{self.current_project}")
        self.device_manager.set_project(self.current_project)
        self.device_manager.load_devices()

        device_count = self.device_manager.get_device_count()
        self.info_devices.setText(f"设备数量：{device_count}")

        log_count = 0
        exception_dir = os.path.join(self.current_project, "output", "single_exception")
        if os.path.exists(exception_dir):
            log_count += len(os.listdir(exception_dir))
        check_dir = os.path.join(self.current_project, "output", "trouble_check_result")
        if os.path.exists(check_dir):
            log_count += len(os.listdir(check_dir))
        self.info_logs.setText(f"运维日志：{log_count}")

        self._refresh_group_filter()
        self._load_device_table()
        self._update_stats()

    def _refresh_group_filter(self):
        self.group_filter_combo.blockSignals(True)
        self.group_filter_combo.clear()
        self.group_filter_combo.addItem("全部")
        for g in self.device_manager.get_groups():
            self.group_filter_combo.addItem(g)
        idx = self.group_filter_combo.findText(self._group_filter)
        if idx >= 0:
            self.group_filter_combo.setCurrentIndex(idx)
        self.group_filter_combo.blockSignals(False)

    def _on_group_filter_changed(self, text):
        self._group_filter = text
        self._load_device_table()

    def _toggle_password_display(self, state):
        self._show_passwords = (state == Qt.Checked)
        self._load_device_table()

    def _update_stats(self):
        stats = self.device_manager.get_stats()
        parts = []
        if stats["by_vendor"]:
            vendor_str = " | ".join(f"{k}:{v}" for k, v in stats["by_vendor"].items())
            parts.append(f"厂商: {vendor_str}")
        if stats["by_group"]:
            group_str = " | ".join(f"{k}:{v}" for k, v in stats["by_group"].items())
            parts.append(f"分组: {group_str}")
        self.stats_label.setText("  |  ".join(parts))

    def _clear_device_table(self):
        self.device_table.setRowCount(0)

    def _load_device_table(self):
        self._clear_device_table()
        if not self.current_project:
            return

        devices = self.device_manager.devices
        if self._group_filter != "全部":
            devices = [d for d in devices if d.get("group", "") == self._group_filter]

        for row, d in enumerate(devices):
            self.device_table.insertRow(row)
            self.device_table.setItem(row, 0, QTableWidgetItem(d["ip"]))
            self.device_table.setItem(row, 1, QTableWidgetItem(d["vendor"]))
            self.device_table.setItem(row, 2, QTableWidgetItem(d["device_type"]))
            self.device_table.setItem(row, 3, QTableWidgetItem(d["username"]))

            pwd_item = QTableWidgetItem(d["password"] if self._show_passwords else "••••••••")
            pwd_item.setData(Qt.UserRole, d["password"])
            self.device_table.setItem(row, 4, pwd_item)

            self.device_table.setItem(row, 5, QTableWidgetItem(d["protocol"]))

            enable_item = QTableWidgetItem(d["enable_password"] if self._show_passwords else ("••••••••" if d["enable_password"] else ""))
            enable_item.setData(Qt.UserRole, d["enable_password"])
            self.device_table.setItem(row, 6, enable_item)

            self.device_table.setItem(row, 7, QTableWidgetItem(d.get("group", "")))
            self.device_table.setItem(row, 8, QTableWidgetItem(d.get("tags", "")))

    def _get_existing_ips(self, exclude_ip=None):
        ips = set()
        for d in self.device_manager.devices:
            if d["ip"] != exclude_ip:
                ips.add(d["ip"])
        return ips

    def add_device_dialog(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        existing_ips = self._get_existing_ips()
        dialog = DeviceFormDialog(self, existing_ips=existing_ips)
        if dialog.exec_() == DeviceFormDialog.Accepted:
            device = dialog.get_device_data()
            self.device_manager.devices.append(device)
            self.device_manager.save_devices()
            self.device_manager.record_history("add", f"新增设备 {device['ip']} ({device['vendor']} {device['device_type']})", 1)
            self._update_project_info()

    def edit_device_dialog(self):
        current_row = self.device_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选中要编辑的设备")
            return

        ip = self.device_table.item(current_row, 0).text()
        device = None
        for d in self.device_manager.devices:
            if d["ip"] == ip:
                device = d
                break

        if not device:
            return

        existing_ips = self._get_existing_ips(exclude_ip=ip)
        dialog = DeviceFormDialog(self, device=device, existing_ips=existing_ips)
        if dialog.exec_() == DeviceFormDialog.Accepted:
            new_data = dialog.get_device_data()
            for key, val in new_data.items():
                device[key] = val
            self.device_manager.save_devices()
            self.device_manager.record_history("modify", f"修改设备 {device['ip']} ({device['vendor']} {device['device_type']})", 1)
            self._update_project_info()

    def delete_device_row(self):
        current_row = self.device_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选中要删除的设备行")
            return

        ip = self.device_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "确认删除", f"确定要删除设备 {ip} 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.device_manager.devices = [d for d in self.device_manager.devices if d["ip"] != ip]
        self.device_manager.save_devices()
        self.device_manager.record_history("delete", f"删除设备 {ip}", 1)
        self._update_project_info()

    def save_device_list(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        devices = []
        for row in range(self.device_table.rowCount()):
            ip = self.device_table.item(row, 0).text().strip() if self.device_table.item(row, 0) else ""
            if not ip:
                continue
            device = {
                "ip": ip,
                "vendor": self.device_table.item(row, 1).text().strip() if self.device_table.item(row, 1) else "",
                "device_type": self.device_table.item(row, 2).text().strip() if self.device_table.item(row, 2) else "",
                "username": self.device_table.item(row, 3).text().strip() if self.device_table.item(row, 3) else "",
                "password": self.device_table.item(row, 4).data(Qt.UserRole) if self.device_table.item(row, 4) else "",
                "protocol": self.device_table.item(row, 5).text().strip() if self.device_table.item(row, 5) else "",
                "enable_password": self.device_table.item(row, 6).data(Qt.UserRole) if self.device_table.item(row, 6) else "",
                "group": self.device_table.item(row, 7).text().strip() if self.device_table.item(row, 7) else "",
                "tags": self.device_table.item(row, 8).text().strip() if self.device_table.item(row, 8) else "",
            }
            devices.append(device)

        self.device_manager.save_devices(devices)
        self.device_manager.record_history("save", f"保存设备清单", len(devices))
        self._update_project_info()
        QMessageBox.information(self, "保存成功", f"设备清单已保存，共 {len(devices)} 台设备")

    def import_device_list(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入设备清单", "",
            "所有支持格式 (*.txt *.csv *.xlsx);;文本文件 (*.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx)")
        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".csv":
                devices = self.device_manager.import_csv(file_path)
            elif ext in (".xlsx", ".xls"):
                devices = self.device_manager.import_excel(file_path)
                if devices is None:
                    QMessageBox.critical(self, "导入失败", "导入Excel需要pandas和openpyxl库，请先安装。\n已自动切换到文本模式导入。")
                    devices = self.device_manager.import_txt(file_path)
            else:
                devices = self.device_manager.import_txt(file_path)

            if not devices:
                QMessageBox.warning(self, "导入失败", "未能从文件中解析到有效设备数据")
                return

            reply = QMessageBox.question(self, "导入确认",
                f"解析到 {len(devices)} 台设备。\n\n替换现有清单？\n（选'否'将追加到现有清单）",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.device_manager.devices = devices
            else:
                existing_ips = {d["ip"] for d in self.device_manager.devices}
                for d in devices:
                    if d["ip"] not in existing_ips:
                        self.device_manager.devices.append(d)

            self.device_manager.save_devices()
            self.device_manager.record_history("import", f"导入设备清单 ({ext})", len(devices))
            self._update_project_info()
            QMessageBox.information(self, "导入成功", f"已导入 {len(devices)} 台设备")
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def export_device_list(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        if not self.device_manager.devices:
            QMessageBox.warning(self, "提示", "设备清单为空，无法导出")
            return

        menu = QMenu(self)
        txt_action = menu.addAction("导出为文本文件 (.txt)")
        csv_action = menu.addAction("导出为CSV文件 (.csv)")
        xlsx_action = menu.addAction("导出为Excel文件 (.xlsx)")
        action = menu.exec_(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))

        if not action:
            return

        if action == txt_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出设备清单", "device_list.txt", "文本文件 (*.txt)")
            if file_path:
                self.device_manager.export_txt(file_path)
        elif action == csv_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出设备清单", "device_list.csv", "CSV文件 (*.csv)")
            if file_path:
                self.device_manager.export_csv(file_path)
        elif action == xlsx_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出设备清单", "device_list.xlsx", "Excel文件 (*.xlsx)")
            if file_path:
                ok = self.device_manager.export_excel(file_path)
                if not ok:
                    QMessageBox.critical(self, "导出失败", "导出Excel需要pandas和openpyxl库，请先安装。")
                    return

        if file_path:
            self.device_manager.record_history("export", f"导出设备清单到 {os.path.basename(file_path)}",
                                               self.device_manager.get_device_count())
            QMessageBox.information(self, "导出成功", f"设备清单已导出到：\n{file_path}")

    def download_template(self):
        menu = QMenu(self)
        csv_action = menu.addAction("下载CSV模板 (.csv)")
        txt_action = menu.addAction("下载文本模板 (.txt)")
        xlsx_action = menu.addAction("下载Excel模板 (.xlsx)")
        action = menu.exec_(self.template_btn.mapToGlobal(self.template_btn.rect().bottomLeft()))

        if not action:
            return

        if action == csv_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "下载模板", "设备清单模板.csv", "CSV文件 (*.csv)")
            if file_path:
                self.device_manager.generate_template(file_path, "csv")
        elif action == txt_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "下载模板", "设备清单模板.txt", "文本文件 (*.txt)")
            if file_path:
                self.device_manager.generate_template(file_path, "txt")
        elif action == xlsx_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "下载模板", "设备清单模板.xlsx", "Excel文件 (*.xlsx)")
            if file_path:
                ok = self.device_manager.generate_template(file_path, "xlsx")
                if not ok:
                    QMessageBox.critical(self, "下载失败", "生成Excel模板需要pandas和openpyxl库。")
                    return

        if file_path:
            QMessageBox.information(self, "下载成功",
                f"模板已保存到：\n{file_path}\n\n模板包含3条示例数据，请按格式填写后导入。")

    def open_template_library(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        dialog = DeviceTemplateDialog(self)
        if dialog.exec_() == DeviceTemplateDialog.Accepted:
            templates = dialog.get_selected_templates()
            if templates:
                existing_ips = self._get_existing_ips()
                added = 0
                for name in templates:
                    info = DEVICE_TEMPLATES.get(name, {})
                    if info:
                        device = {
                            "ip": "",
                            "vendor": info.get("厂商", ""),
                            "device_type": info.get("设备类型", ""),
                            "username": "",
                            "password": "",
                            "protocol": info.get("协议", "ssh"),
                            "enable_password": "",
                            "group": "",
                            "tags": "",
                        }
                        self.device_manager.devices.append(device)
                        added += 1

                self.device_manager.save_devices()
                self.device_manager.record_history("template", f"应用模板添加 {added} 台设备", added)
                self._update_project_info()
                QMessageBox.information(self, "模板应用成功",
                    f"已添加 {added} 台设备模板，请补充IP地址和登录凭据后保存。")

    def open_discovery(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        dialog = DeviceDiscoveryDialog(self)
        if dialog.exec_() == DeviceDiscoveryDialog.Accepted:
            ips = dialog.get_selected_ips()
            if ips:
                existing_ips = self._get_existing_ips()
                added = 0
                for ip in ips:
                    if ip not in existing_ips:
                        self.device_manager.devices.append({
                            "ip": ip, "vendor": "", "device_type": "",
                            "username": "", "password": "", "protocol": "ssh",
                            "enable_password": "", "group": "", "tags": "",
                        })
                        added += 1

                if added > 0:
                    self.device_manager.save_devices()
                    self.device_manager.record_history("discover", f"批量发现添加 {added} 台设备", added)
                    self._update_project_info()
                    QMessageBox.information(self, "添加成功",
                        f"已添加 {added} 台新发现的设备，请补充设备信息后保存。")
                else:
                    QMessageBox.information(self, "提示", "所选IP已全部存在于设备清单中。")

    def test_connection(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        selected_rows = set()
        for item in self.device_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选中要测试的设备（可多选）")
            return

        devices_to_test = []
        for row in selected_rows:
            ip = self.device_table.item(row, 0).text().strip() if self.device_table.item(row, 0) else ""
            protocol = self.device_table.item(row, 5).text().strip() if self.device_table.item(row, 5) else "ssh"
            username = self.device_table.item(row, 3).text().strip() if self.device_table.item(row, 3) else ""
            password = self.device_table.item(row, 4).data(Qt.UserRole) if self.device_table.item(row, 4) else ""
            if ip:
                devices_to_test.append((ip, protocol, username, password))

        if not devices_to_test:
            return

        results = []
        self.test_conn_btn.setEnabled(False)
        self.test_conn_btn.setText("测试中...")

        for ip, protocol, username, password in devices_to_test:
            worker = ConnectionTestWorker(ip, protocol, username, password)
            worker.run()

            ping_ok = worker._test_ping()
            if ping_ok:
                results.append(f"✅ {ip} - Ping成功")
                if protocol == "ssh":
                    try:
                        from netmiko import ConnectHandler
                        device = {
                            "device_type": "cisco_ios",
                            "host": ip, "username": username, "password": password,
                            "timeout": 10,
                        }
                        conn = ConnectHandler(**device)
                        conn.disconnect()
                        results.append(f"✅ {ip} - SSH连接成功")
                    except Exception as e:
                        results.append(f"❌ {ip} - SSH失败: {str(e)[:60]}")
                else:
                    try:
                        from netmiko import ConnectHandler
                        device = {
                            "device_type": "cisco_ios_telnet",
                            "host": ip, "username": username, "password": password,
                            "timeout": 10,
                        }
                        conn = ConnectHandler(**device)
                        conn.disconnect()
                        results.append(f"✅ {ip} - Telnet连接成功")
                    except Exception as e:
                        results.append(f"❌ {ip} - Telnet失败: {str(e)[:60]}")
            else:
                results.append(f"❌ {ip} - Ping失败")

        self.test_conn_btn.setEnabled(True)
        self.test_conn_btn.setText("连接测试")

        QMessageBox.information(self, "连接测试结果", "\n".join(results))

    def show_history(self):
        if not self.current_project:
            QMessageBox.warning(self, "提示", "请先选择或创建项目")
            return

        history = self.device_manager.get_history()
        dialog = HistoryDialog(self, history=history)
        dialog.exec_()

    def _refresh_overview(self):
        for i in reversed(range(self.overview_cards_layout.count())):
            widget = self.overview_cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        config = self._get_projects_config()
        projects = config.get("projects", {})
        total_devices = 0
        latest_inspect = "--"

        for name, path in projects.items():
            if not os.path.exists(path):
                continue

            device_file = os.path.join(path, "config", "device_list.txt")
            device_count = 0
            if os.path.exists(device_file):
                with open(device_file, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            device_count += 1
            total_devices += device_count

            last_backup = "--"
            backup_dir = os.path.join(path, "config_backup")
            if os.path.exists(backup_dir):
                backups = sorted([f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))])
                if backups:
                    mtime = os.path.getmtime(os.path.join(backup_dir, backups[-1]))
                    last_backup = datetime.fromtimestamp(mtime).strftime('%m/%d')

            last_inspect = "--"
            report_dir = os.path.join(path, "report")
            if os.path.exists(report_dir):
                reports = sorted([f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f)) and f.endswith(('.txt', '.md'))])
                if reports:
                    mtime = os.path.getmtime(os.path.join(report_dir, reports[-1]))
                    last_inspect = datetime.fromtimestamp(mtime).strftime('%m/%d')
                    if latest_inspect == "--" or last_inspect > latest_inspect:
                        latest_inspect = last_inspect

            fault_count = 0
            exception_dir = os.path.join(path, "output", "single_exception")
            if os.path.exists(exception_dir):
                fault_count += len([f for f in os.listdir(exception_dir) if os.path.isfile(os.path.join(exception_dir, f))])
            check_dir = os.path.join(path, "output", "trouble_check_result")
            if os.path.exists(check_dir):
                fault_count += len([f for f in os.listdir(check_dir) if os.path.isfile(os.path.join(check_dir, f))])

            if fault_count > 0:
                status_color = "#F53F3F"
                status_icon = "🔴"
            elif last_inspect == "--":
                status_color = "#FF7D00"
                status_icon = "🟡"
            else:
                status_color = "#00B42A"
                status_icon = "🟢"

            card = QGroupBox(f"{status_icon} {name}")
            card.setStyleSheet("""
                QGroupBox {
                    font-size: 10pt;
                    font-weight: bold;
                    color: #1D2129;
                    border: 1px solid #E5E6EB;
                    border-radius: 8px;
                    margin-top: 8px;
                    padding: 12px 10px 8px 10px;
                    background-color: #FFFFFF;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 4px;
                }
                QGroupBox:hover { border: 1px solid #165DFF; }
            """)
            card.setFixedWidth(210)
            card_layout = QVBoxLayout()
            card_layout.setSpacing(3)
            card_layout.setContentsMargins(6, 14, 6, 6)

            info_dev = QLabel(f"设备: {device_count}台")
            info_dev.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
            card_layout.addWidget(info_dev)
            info_bkp = QLabel(f"备份: {last_backup}")
            info_bkp.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
            card_layout.addWidget(info_bkp)
            info_ins = QLabel(f"巡检: {last_inspect}")
            info_ins.setStyleSheet("font-size: 9pt; color: #4E5969; font-weight: normal;")
            card_layout.addWidget(info_ins)
            info_fault = QLabel(f"故障: {fault_count}台")
            info_fault.setStyleSheet(f"font-size: 9pt; color: {status_color}; font-weight: normal;")
            card_layout.addWidget(info_fault)

            enter_btn = QPushButton("进入项目")
            enter_btn.setFixedHeight(28)
            enter_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E8F3FF;
                    color: #165DFF;
                    border: 1px solid #165DFF;
                    border-radius: 4px;
                    font-size: 9pt;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #D6E8FF; }
            """)
            enter_btn.clicked.connect(lambda checked, n=name: self._enter_project_from_card(n))
            card_layout.addWidget(enter_btn)
            card.setLayout(card_layout)
            self.overview_cards_layout.addWidget(card)

        self.overview_cards_layout.addStretch()
        self.overview_stats_label.setText(
            f"共{len(projects)}个项目 | {total_devices}台设备 | 最近一次全量巡检: {latest_inspect}")

    def _enter_project_from_card(self, name):
        config = self._get_projects_config()
        projects = config.get("projects", {})
        if name in projects:
            config["current"] = name
            self._save_projects_config(config)
            self.current_project = projects[name]
            if hasattr(self.parent, 'current_project'):
                self.parent.current_project = self.current_project
            if hasattr(self.parent, 'refresh_project_status'):
                self.parent.refresh_project_status()
            self.refresh_project_list()
            self._update_project_info()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        edit_action = menu.addAction("编辑设备")
        delete_action = menu.addAction("删除设备")
        test_action = menu.addAction("连接测试")
        menu.addSeparator()
        copy_ip_action = menu.addAction("复制IP")

        action = menu.exec_(self.device_table.mapToGlobal(pos))

        if action == edit_action:
            self.edit_device_dialog()
        elif action == delete_action:
            self.delete_device_row()
        elif action == test_action:
            self.test_connection()
        elif action == copy_ip_action:
            row = self.device_table.currentRow()
            if row >= 0:
                ip = self.device_table.item(row, 0).text()
                from PyQt5.QtWidgets import QApplication
                QApplication.clipboard().setText(ip)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            self._handle_paste()
        else:
            super().keyPressEvent(event)

    def _handle_paste(self):
        if not self.current_project:
            return

        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text or "\t" not in text and "," not in text:
            return

        lines = text.strip().split("\n")
        if len(lines) < 1:
            return

        devices = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "\t" in line:
                parts = [p.strip() for p in line.split("\t")]
            else:
                parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 7:
                devices.append({
                    "ip": parts[0], "vendor": parts[1], "device_type": parts[2],
                    "username": parts[3], "password": parts[4], "protocol": parts[5],
                    "enable_password": parts[6],
                    "group": parts[7] if len(parts) > 7 else "",
                    "tags": parts[8] if len(parts) > 8 else "",
                })

        if not devices:
            return

        reply = QMessageBox.question(self, "批量粘贴",
            f"从剪贴板解析到 {len(devices)} 台设备。\n\n替换现有清单？\n（选'否'将追加到现有清单）",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            return
        elif reply == QMessageBox.Yes:
            self.device_manager.devices = devices
        else:
            existing_ips = {d["ip"] for d in self.device_manager.devices}
            for d in devices:
                if d["ip"] not in existing_ips:
                    self.device_manager.devices.append(d)

        self.device_manager.save_devices()
        self.device_manager.record_history("batch_paste", f"批量粘贴 {len(devices)} 台设备", len(devices))
        self._update_project_info()
        QMessageBox.information(self, "粘贴成功", f"已添加 {len(devices)} 台设备")