#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps网络自动化运维工具主窗口
"""

import json
import os
import sys
import ctypes
import ctypes.wintypes
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QLabel, QDialog, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

# UI页面导入
from src.ui.system_settings_page import SystemSettingsPage
from src.ui.project_manager_page import ProjectManagerPage
from src.ui.ops_toolbox_page import OpsToolboxPage
from src.ui.single_device_page import SingleDevicePage
from src.ui.ai_analysis_page import AIAnalysisPage
from src.ui.theme_switcher_page import ThemeSwitcherPage

# 配置页面导入（按厂商分组）
from src.ui.config_pages.ruijie import RuijieAccessSwitchConfig, RuijieCoreSwitchConfig, RuijieRouterConfig, RuijieACConfig
from src.ui.config_pages.huawei import HuaweiAccessSwitchConfig, HuaweiCoreSwitchConfig, HuaweiRouterConfig, HuaweiACConfig
from src.ui.config_pages.h3c import H3CAccessSwitchConfig, H3CCoreSwitchConfig, H3CRouterConfig, H3CACConfig
from src.ui.config_pages.cisco import CiscoAccessSwitchConfig, CiscoCoreSwitchConfig, CiscoRouterConfig, CiscoACConfig

from src.utils.resource_path import get_config_path, ensure_dirs
from src.core.logger import netops_logger
from src.core.activation_engine import check_activation
from src.core.theme_engine import ThemeEngine, Theme
from src.utils.validators import ProjectValidator
from src.utils.file_operators import JSONFileManager

# 常量定义
PROJECTS_CONFIG: str = get_config_path("config/projects_config.json")
MODULES: List[Tuple[str, str, str]] = [
    ("config", "设备配置", "🖥"),
    ("project", "新建项目", "📁"),
    ("ops", "项目运维", "🔧"),
    ("single", "单点运维", "🔍"),
    ("ai", "专家工作站", "🤖"),
    ("batchcmd", "命令生成", "📜"),
    ("system", "模型设置", "⚙"),
    ("theme", "主题切换", "🎨"),
]

# 厂商配置映射
VENDOR_CONFIG_MAP: Dict[str, Dict[str, type]] = {
    "锐捷": {
        "接入交换机": RuijieAccessSwitchConfig,
        "核心交换机": RuijieCoreSwitchConfig,
        "路由器": RuijieRouterConfig,
        "AC控制器": RuijieACConfig,
    },
    "华为": {
        "接入交换机": HuaweiAccessSwitchConfig,
        "核心交换机": HuaweiCoreSwitchConfig,
        "路由器": HuaweiRouterConfig,
        "AC控制器": HuaweiACConfig,
    },
    "H3C": {
        "接入交换机": H3CAccessSwitchConfig,
        "核心交换机": H3CCoreSwitchConfig,
        "路由器": H3CRouterConfig,
        "AC控制器": H3CACConfig,
    },
    "思科": {
        "接入交换机": CiscoAccessSwitchConfig,
        "核心交换机": CiscoCoreSwitchConfig,
        "路由器": CiscoRouterConfig,
        "AC控制器": CiscoACConfig,
    },
}


class MainWindow(QMainWindow):
    def __init__(self, is_active: bool = False, act_status: str = "未激活",
                 act_info: Optional[dict] = None):
        super().__init__()
        ensure_dirs()

        # 初始化主题引擎并应用已保存的主题
        self._theme_engine = ThemeEngine.get()
        app = QApplication.instance()
        if app is not None:
            self._theme_engine.apply(app, self._theme_engine.current_theme_id)

        # 直接使用 main.py 传入的激活结果，避免重复 check_activation 调用
        self._trial_mode: bool = not is_active
        self._activation_info: dict = act_info or {}
        if self._trial_mode:
            netops_logger.get_logger().info("试用模式：仅开放锐捷接入交换机配置和批量命令生成")

        self.setWindowTitle('NetOps 企业网络自动化运维平台 V0.3.0' + (' [试用模式]' if self._trial_mode else ''))

        # 初始化窗口尺寸
        screen = QApplication.primaryScreen().availableGeometry()
        self._init_window_geometry(screen)

        # 初始化状态变量
        self.current_project: Optional[Dict[str, Any]] = None
        self.selected_vendor: Optional[str] = None
        self.selected_device: Optional[str] = None
        self.config_pages: Dict[str, QWidget] = {}
        self._config_top_bar: Optional[QWidget] = None
        self._nav_bar: Optional[QWidget] = None
        self._logo_label: Optional[QLabel] = None
        self._account_btn: Optional[QPushButton] = None
        self._about_btn: Optional[QPushButton] = None

        # 创建主布局和导航
        main_widget = self._create_main_layout()
        self.setCentralWidget(main_widget)

        # 创建模块堆栈和配置页面
        self._create_module_stack(main_widget.layout())
        self._init_config_module()

        # 初始化UI状态
        self.module_stack.setCurrentWidget(self.config_container)
        self._update_nav_buttons("config")

        # 创建状态栏
        self._create_status_bar()

        # 加载项目配置（必须在UI创建之后）
        self._load_current_project()

        # 监听主题变化，动态更新硬编码样式的组件
        self._theme_engine.theme_changed.connect(self._on_theme_changed)

    def _init_window_geometry(self, screen):
        """初始化窗口几何尺寸

        Args:
            screen: 屏幕几何信息
        """
        # 多屏幕适配：根据屏幕尺寸分档
        sw, sh = screen.width(), screen.height()
        if sw >= 2560:
            # 2K/4K大屏：固定最大尺寸
            w, h = 1600, 960
        elif sw >= 1920:
            # 1080p：85%屏幕宽度，80%高度
            w = int(sw * 0.85)
            h = int(sh * 0.80)
        elif sw >= 1366:
            # 笔记本常见分辨率
            w = int(sw * 0.90)
            h = int(sh * 0.85)
        else:
            # 小屏/老电脑（1024×768等）：尽量占满
            w = int(sw * 0.95)
            h = int(sh * 0.90)
        # 兜底：不超过屏幕可用区域
        w = min(w, sw - 40)
        h = min(h, sh - 60)
        x = screen.x() + (screen.width() - w) // 2
        y = screen.y() + (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def _show_warning(self, message):
        QMessageBox.warning(self, "提示", message)

    def _show_info(self, message):
        QMessageBox.information(self, "提示", message)

    def _show_critical(self, message):
        QMessageBox.critical(self, "错误", message)

    def _create_main_layout(self) -> QWidget:
        """创建主布局

        Returns:
            主布局组件
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)

        self.create_top_nav_bar(main_layout)

        return main_widget

    def _create_module_stack(self, main_layout: QVBoxLayout):
        """创建模块堆栈

        Args:
            main_layout: 主布局
        """
        self.module_stack = QStackedWidget()
        main_layout.addWidget(self.module_stack)

        # 创建各功能页面
        self.system_page = SystemSettingsPage(self)
        self.project_page = ProjectManagerPage(self)
        self.ops_page = OpsToolboxPage(self)
        self.single_page = SingleDevicePage(self)
        self.ai_page = AIAnalysisPage(self)
        from src.ui.batch_cmd_generator_page import BatchCmdGeneratorPage
        self.batchcmd_page = BatchCmdGeneratorPage(self)
        self.theme_page = ThemeSwitcherPage(self)
        self.config_container = QWidget()

        # 添加到堆栈
        self.module_stack.addWidget(self.system_page)
        self.module_stack.addWidget(self.project_page)
        self.module_stack.addWidget(self.ops_page)
        self.module_stack.addWidget(self.single_page)
        self.module_stack.addWidget(self.ai_page)
        self.module_stack.addWidget(self.batchcmd_page)
        self.module_stack.addWidget(self.theme_page)
        self.module_stack.addWidget(self.config_container)

    def _create_status_bar(self):
        t = self._theme_engine.current_theme
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {t['toolbar_bg']};
                border-top: 1px solid {t['border_deep']};
                font-size: 10pt;
                color: {t['text_tertiary']};
                padding: 2px 12px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 | Ctrl+1~8 切换模块 | Ctrl+1 设备配置 · Ctrl+2 新建项目 · Ctrl+3 运维工具箱 · Ctrl+4 单点巡检 · Ctrl+5 专家工作站 · Ctrl+6 命令生成 · Ctrl+7 模型设置 · Ctrl+8 主题切换")

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            key = event.key()
            shortcuts = {
                Qt.Key_1: "config",
                Qt.Key_2: "project",
                Qt.Key_3: "ops",
                Qt.Key_4: "single",
                Qt.Key_5: "ai",
                Qt.Key_6: "batchcmd",
                Qt.Key_7: "system",
                Qt.Key_8: "theme",
            }
            if key in shortcuts:
                if self._trial_mode and shortcuts[key] not in ("config", "batchcmd"):
                    self._show_trial_prompt()
                    return
                self.switch_module(shortcuts[key])
                module_names = {
                    "system": "模型设置", "project": "新建项目", "ops": "运维工具箱",
                    "single": "单点巡检", "ai": "专家工作站", "config": "设备配置",
                    "batchcmd": "命令生成", "theme": "主题切换",
                }
                self.status_bar.showMessage(f"已切换到：{module_names[shortcuts[key]]} | Ctrl+1~7 切换模块", 3000)
                return
        super().keyPressEvent(event)

    def _load_current_project(self):
        try:
            if not os.path.exists(PROJECTS_CONFIG):
                logger = netops_logger.get_logger()
                logger.info("项目配置文件不存在，等待用户创建项目")
                return

            config = JSONFileManager.load_json(PROJECTS_CONFIG, {"projects": {}, "current": None})

            if not isinstance(config, dict):
                return

            current_name = config.get("current")
            projects = config.get("projects", {})

            if not current_name or not isinstance(projects, dict):
                return

            if current_name not in projects:
                return

            proj_data = projects[current_name]
            if isinstance(proj_data, str):
                self.current_project = {"name": current_name, "path": proj_data}
                self._update_project_status_label(current_name)
                return
            elif isinstance(proj_data, dict):
                project_path = proj_data.get("path")
                if project_path:
                    is_valid, error = ProjectValidator.validate_project_path(project_path)
                    if not is_valid:
                        return
                self.current_project = proj_data
                self._update_project_status_label(current_name)

            logger = netops_logger.get_logger()
            logger.info(f"成功加载项目: {current_name}")

        except json.JSONDecodeError as e:
            self._show_critical(f"项目配置文件格式错误: {str(e)}")
            logger = netops_logger.get_logger()
            logger.error(f"项目配置JSON格式错误: {e}")
        except Exception as e:
            self._show_critical(f"加载项目配置失败: {str(e)}")
            logger = netops_logger.get_logger()
            logger.error(f"加载项目配置失败: {e}")

    def _update_project_status_label(self, project_name=None):
        t = self._theme_engine.current_theme
        if project_name:
            self.project_status_label.setText(f"当前项目：{project_name}")
            self.project_status_label.setStyleSheet(f"font-size: 10pt; color: {t['success']}; padding-right: 12px; font-weight: bold;")
        else:
            self.project_status_label.setText("未选择项目")
            self.project_status_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding-right: 12px;")

    def refresh_project_status(self):
        try:
            if os.path.exists(PROJECTS_CONFIG):
                with open(PROJECTS_CONFIG, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if not isinstance(config, dict):
                    return
                current_name = config.get("current")
                projects = config.get("projects", {})
                if not isinstance(projects, dict):
                    return
                if current_name and current_name in projects:
                    proj_data = projects[current_name]
                    if isinstance(proj_data, str):
                        self.current_project = {"name": current_name, "path": proj_data}
                    else:
                        self.current_project = proj_data
                    self._update_project_status_label(current_name)
                else:
                    self.current_project = None
                    self._update_project_status_label(None)
        except Exception:
            pass

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题切换后更新硬编码样式的组件。"""
        t = self._theme_engine.current_theme
        # 更新状态栏样式
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {t['toolbar_bg']};
                border-top: 1px solid {t['border_deep']};
                font-size: 10pt;
                color: {t['text_tertiary']};
                padding: 2px 12px;
            }}
        """)
        # 刷新导航栏
        self._refresh_nav_style()
        # 刷新配置选择栏
        self._refresh_config_bar_style()
        # 刷新激活按钮
        self._update_activation_btn_style()
        # 刷新项目状态标签
        if self.current_project:
            name = self.current_project.get("name", "")
            self._update_project_status_label(name)
        else:
            self._update_project_status_label(None)
        # 刷新 Windows 原生标题栏颜色
        self._update_native_title_bar()

    def _refresh_nav_style(self) -> None:
        """刷新导航栏按钮样式（主题切换时调用）。"""
        t = self._theme_engine.current_theme
        # 导航栏背景
        if self._nav_bar is not None:
            self._nav_bar.setStyleSheet(f"""
                background-color: {t['nav_bg']};
                border-bottom: 1px solid {t['border']};
            """)
        # Logo
        if self._logo_label is not None:
            self._logo_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {t['primary_light']}; padding-right: 20px;")
        # 导航按钮
        for mid, btn in self.nav_buttons.items():
            is_active = btn.property("active") == "true"
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t['selection_bg']};
                        border: none;
                        border-radius: {t['radius_md']}px;
                        padding: 3px 8px;
                        font-size: 11pt;
                        color: {t['primary_light']};
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        border-radius: {t['radius_md']}px;
                        padding: 3px 8px;
                        font-size: 11pt;
                        color: {t['text_secondary']};
                    }}
                    QPushButton:hover {{
                        background-color: transparent;
                        color: {t['text_main']};
                    }}
                """)
        # 账户管理和关于按钮
        toolbar_btn_qss = self._theme_engine.qss("toolbar_btn")
        if self._account_btn is not None:
            self._account_btn.setStyleSheet(toolbar_btn_qss)
        if self._about_btn is not None:
            self._about_btn.setStyleSheet(toolbar_btn_qss)

    def _refresh_config_bar_style(self) -> None:
        """刷新配置选择栏样式（主题切换时调用）。"""
        t = self._theme_engine.current_theme
        r = t['radius_md']
        # 刷新配置选择栏背景
        if self._config_top_bar is not None:
            self._config_top_bar.setStyleSheet(f'background-color: {t["card_bg"]}; border-bottom: 1px solid {t["border"]};')
        # 刷新厂家选择按钮
        for vid, button in self.vendor_buttons.items():
            if vid == self.selected_vendor:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {t['text_main']};
                        border: 1px solid {t['border_deep']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        font-weight: bold;
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{
                        background-color: transparent;
                        border: 1px solid {t['text_tertiary']};
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {t['border']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        color: {t['text_secondary']};
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{ border: 1px solid {t['border_deep']}; color: {t['text_main']}; }}
                """)
        # 刷新设备类型按钮
        for did, button in self.device_buttons.items():
            if did == self.selected_device:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {t['text_secondary']};
                        border: 1px solid {t['border']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        font-weight: bold;
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{
                        background-color: transparent;
                        border: 1px solid {t['border']};
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {t['border']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        color: {t['text_secondary']};
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{ border: 1px solid {t['border']}; color: {t['text_main']}; }}
                """)
        # 刷新配置选择栏背景
        if self._config_top_bar is not None:
            self._config_top_bar.setStyleSheet(f'background-color: {t["card_bg"]}; padding: 10px; border-bottom: 1px solid {t["border"]};')

    def _update_native_title_bar(self) -> None:
        """更新 Windows 原生标题栏颜色（Windows 10/11）。"""
        if sys.platform != "win32":
            return
        try:
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            # 值 1 = 深色标题栏, 0 = 浅色标题栏
            is_dark = self._theme_engine.current_theme_id in ("vscode", "raycast")
            value = ctypes.c_int(1 if is_dark else 0)
            hwnd = int(self.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
            )
        except Exception:
            pass

    def create_top_nav_bar(self, main_layout):
        t = self._theme_engine.current_theme

        self._nav_bar = QWidget()
        self._nav_bar.setFixedHeight(48)
        self._nav_bar.setStyleSheet(f"""
            background-color: {t['nav_bg']};
            border-bottom: 1px solid {t['border']};
        """)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(16, 0, 16, 0)
        nav_layout.setSpacing(4)
        self._nav_bar.setLayout(nav_layout)

        self._logo_label = QLabel("  NetOps")
        self._logo_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {t['primary_light']}; padding-right: 20px;")
        nav_layout.addWidget(self._logo_label)

        self.nav_buttons = {}
        for module_id, module_name, icon in MODULES:
            btn = QPushButton(f" {icon}  {module_name}")
            btn.setFixedHeight(26)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {t['radius_sm']}px;
                    padding: 3px 8px;
                    font-size: 11pt;
                    color: {t['text_secondary']};
                }}
                QPushButton:hover {{
                    background-color: transparent;
                    color: {t['text_main']};
                }}
                QPushButton[active="true"] {{
                    background-color: {t['selection_bg']};
                    color: {t['primary_light']};
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, mid=module_id: self.switch_module(mid))
            self.nav_buttons[module_id] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        self.project_status_label = QLabel("未选择项目")
        self.project_status_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding-right: 12px;")
        nav_layout.addWidget(self.project_status_label)

        # 保存账户管理和关于按钮引用，主题切换时刷新
        self._account_btn = None
        self._about_btn = None

        # 激活状态按钮
        self._activation_btn = QPushButton()
        self._activation_btn.setFixedSize(90, 26)
        self._activation_btn.setCursor(Qt.PointingHandCursor)
        self._activation_btn.clicked.connect(self._on_activation_btn_clicked)
        self._update_activation_btn_style()
        nav_layout.addWidget(self._activation_btn)

        # 账户管理按钮
        self._account_btn = QPushButton("账户管理")
        self._account_btn.setFixedSize(72, 26)
        self._account_btn.setStyleSheet(self._theme_engine.qss("toolbar_btn"))
        self._account_btn.clicked.connect(self._show_account_dialog)
        nav_layout.addWidget(self._account_btn)

        self._about_btn = QPushButton("关于")
        self._about_btn.setFixedSize(48, 26)
        self._about_btn.setStyleSheet(self._theme_engine.qss("toolbar_btn"))
        self._about_btn.clicked.connect(self.show_about_dialog)
        nav_layout.addWidget(self._about_btn)

        main_layout.addWidget(self._nav_bar)

    def switch_module(self, module_id):
        if self._trial_mode and module_id not in ("config", "batchcmd"):
            self._show_trial_prompt()
            return

        page_map = {
            "system": self.system_page,
            "project": self.project_page,
            "ops": self.ops_page,
            "single": self.single_page,
            "ai": self.ai_page,
            "batchcmd": self.batchcmd_page,
            "theme": self.theme_page,
            "config": self.config_container,
        }
        if module_id in page_map:
            self.module_stack.setCurrentWidget(page_map[module_id])
            self._update_nav_buttons(module_id)
            self.refresh_project_status()
            if module_id == "project":
                self.project_page.refresh_project_list()
            module_names = {
                "system": "模型设置", "project": "新建项目", "ops": "运维工具箱",
                "single": "单点巡检", "ai": "AI分析", "config": "设备配置",
                "batchcmd": "命令生成", "theme": "主题切换",
            }
            self.status_bar.showMessage(f"当前模块：{module_names.get(module_id, '')} | Ctrl+1~8 切换模块")

    def _update_nav_buttons(self, active_id):
        for mid, btn in self.nav_buttons.items():
            if mid == active_id:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _init_config_module(self):
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(0)
        self.config_container.setLayout(config_layout)

        self.create_config_selection_bar(config_layout)

        self.config_stack = QStackedWidget()
        config_layout.addWidget(self.config_stack)

        default_page = QWidget()
        default_layout = QVBoxLayout()
        default_page.setLayout(default_layout)
        label = QLabel('请选择厂家和设备类型')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"font-size: 18pt; color: {self._theme_engine.current_theme['text_tertiary']};")
        default_layout.addWidget(label)
        self.config_stack.addWidget(default_page)

    def create_config_selection_bar(self, parent_layout):
        t = self._theme_engine.current_theme
        top_bar = QWidget()
        self._config_top_bar = top_bar
        top_layout = QHBoxLayout()
        top_bar.setLayout(top_layout)
        top_bar.setStyleSheet(f'background-color: {t["card_bg"]}; border-bottom: 1px solid {t["border"]};')
        top_layout.setContentsMargins(10, 4, 10, 4)
        top_layout.setSpacing(0)

        vendor_layout = QHBoxLayout()
        vendor_layout.setSpacing(4)
        vendor_layout.setContentsMargins(0, 0, 0, 0)
        vendor_label = QPushButton('厂家选择:')
        vendor_label.setStyleSheet(f'font-weight: bold; border: none; background: none; color: {t["text_main"]};')
        vendor_layout.addWidget(vendor_label)

        self.vendor_buttons = {}
        vendors = ['锐捷', '华为', '华三', '思科']
        vendor_ids = ['ruijie', 'huawei', 'h3c', 'cisco']

        for name, vendor_id in zip(vendors, vendor_ids):
            button = QPushButton(name)
            button.setFixedSize(80, 30)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    border-radius: {t['radius_md']}px;
                    font-size: 10pt;
                    color: {t['text_secondary']};
                    padding: 4px 6px;
                }}
                QPushButton:hover {{ border: 1px solid {t['border_deep']}; color: {t['text_main']}; }}
            """)
            button.clicked.connect(lambda checked, vid=vendor_id: self.on_vendor_clicked(vid))
            self.vendor_buttons[vendor_id] = button
            vendor_layout.addWidget(button)

        device_layout = QHBoxLayout()
        device_layout.setSpacing(4)
        device_layout.setContentsMargins(0, 0, 0, 0)
        device_label = QPushButton('设备类型:')
        device_label.setStyleSheet(f'font-weight: bold; border: none; background: none; color: {t["text_main"]};')
        device_layout.addWidget(device_label)

        self.device_buttons = {}
        devices = ['接入交换机', '核心交换机', '路由器', 'AC']
        device_ids = ['access_switch', 'core_switch', 'router', 'ac']

        for name, device_id in zip(devices, device_ids):
            button = QPushButton(name)
            button.setFixedSize(100, 30)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    border-radius: {t['radius_md']}px;
                    font-size: 10pt;
                    color: {t['text_secondary']};
                    padding: 4px 6px;
                }}
                QPushButton:hover {{ border: 1px solid {t['border']}; color: {t['text_main']}; }}
            """)
            button.clicked.connect(lambda checked, did=device_id: self.on_device_clicked(did))
            self.device_buttons[device_id] = button
            device_layout.addWidget(button)

        top_layout.addLayout(vendor_layout)
        top_layout.addStretch()
        top_layout.addLayout(device_layout)

        parent_layout.addWidget(top_bar)

    def on_vendor_clicked(self, vendor):
        if self._trial_mode and vendor != "ruijie":
            self._show_trial_prompt()
            return
        t = self._theme_engine.current_theme
        for vid, button in self.vendor_buttons.items():
            if vid == vendor:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {t['text_secondary']};
                        border: 1px solid {t['border']};
                        border-radius: {t['radius_md']}px;
                        font-size: 10pt;
                        font-weight: bold;
                        padding: 4px 6px;
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {t['border']};
                        border-radius: {t['radius_md']}px;
                        font-size: 10pt;
                        color: {t['text_secondary']};
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{ border: 1px solid {t['border']}; color: {t['text_main']}; }}
                """)
        self.selected_vendor = vendor
        self.try_show_config_page()

    def on_device_clicked(self, device_type):
        if self._trial_mode and device_type != "access_switch":
            self._show_trial_prompt()
            return
        t = self._theme_engine.current_theme
        for did, button in self.device_buttons.items():
            if did == device_type:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {t['text_secondary']};
                        border: 1px solid {t['border']};
                        border-radius: {t['radius_md']}px;
                        font-size: 10pt;
                        font-weight: bold;
                        padding: 4px 6px;
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {t['border']};
                        border-radius: {t['radius_md']}px;
                        font-size: 10pt;
                        color: {t['text_secondary']};
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{ border: 1px solid {t['border_deep']}; color: {t['text_main']}; }}
                """)
        self.selected_device = device_type
        self.try_show_config_page()

    def try_show_config_page(self):
        if self.selected_vendor and self.selected_device:
            self.show_config_page(self.selected_vendor, self.selected_device)

    def show_config_page(self, vendor, device_type):
        # 试用模式：仅允许锐捷接入交换机
        if self._trial_mode:
            if vendor != "ruijie" or device_type != "access_switch":
                self._show_trial_prompt()
                return

        page_key = f"{vendor}_{device_type}"
        config_page = None

        if vendor == 'ruijie':
            if device_type == 'access_switch':
                config_page = RuijieAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = RuijieCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = RuijieRouterConfig(self)
            elif device_type == 'ac':
                config_page = RuijieACConfig(self)
        elif vendor == 'huawei':
            if device_type == 'access_switch':
                config_page = HuaweiAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = HuaweiCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = HuaweiRouterConfig(self)
            elif device_type == 'ac':
                config_page = HuaweiACConfig(self)
        elif vendor == 'h3c':
            if device_type == 'access_switch':
                config_page = H3CAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = H3CCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = H3CRouterConfig(self)
            elif device_type == 'ac':
                config_page = H3CACConfig(self)
        elif vendor == 'cisco':
            if device_type == 'access_switch':
                config_page = CiscoAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = CiscoCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = CiscoRouterConfig(self)
            elif device_type == 'ac':
                config_page = CiscoACConfig(self)

        if config_page:
            if page_key in self.config_pages:
                old_page = self.config_pages[page_key]
                self.config_stack.removeWidget(old_page)
                old_page.deleteLater()

            self.config_pages[page_key] = config_page
            self.config_stack.addWidget(config_page)
            self.config_stack.setCurrentWidget(config_page)

    def _get_activation_display_text(self) -> str:
        """获取激活按钮显示文字。

        Returns:
            str: 按钮文字，如"✅ 已激活"、"✅ 剩365天"、"🔓 未激活"
        """
        if self._trial_mode:
            return "🔓 未激活"

        info = getattr(self, '_activation_info', {})
        if not info:
            return "✅ 已激活"

        is_permanent = info.get("is_permanent", True)
        days_remaining = info.get("days_remaining", -1)

        if is_permanent:
            return "✅ 永久激活"
        elif days_remaining > 0:
            return f"✅ 剩{days_remaining}天"
        else:
            return "✅ 已激活"

    def _update_activation_btn_style(self) -> None:
        """更新导航栏激活状态按钮的样式和文字。"""
        t = self._theme_engine.current_theme
        r = t["radius_md"]

        if self._trial_mode:
            self._activation_btn.setText("🔓 未激活")
            self._activation_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['danger_bg']};
                    border: 1px solid {t['border']};
                    border-radius: {r}px;
                    font-size: 10pt;
                    color: {t['text_secondary']};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {t['danger_bg']};
                    border-color: {t['border']};
                }}
            """)
        else:
            info = getattr(self, '_activation_info', {})
            days_remaining = info.get("days_remaining", -1)
            is_permanent = info.get("is_permanent", True)

            if not is_permanent and days_remaining <= 30 and days_remaining > 0:
                self._activation_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t['warning_bg']};
                        border: 1px solid {t['border']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        color: {t['warning']};
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {t['warning_bg']};
                        border-color: {t['border']};
                    }}
                """)
            else:
                self._activation_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t['success_bg']};
                        border: 1px solid {t['success']};
                        border-radius: {r}px;
                        font-size: 10pt;
                        color: {t['success']};
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {t['success_bg']};
                        border-color: {t['success']};
                    }}
                """)

        self._activation_btn.setText(self._get_activation_display_text())

    def _on_activation_btn_clicked(self) -> None:
        """点击导航栏激活按钮。

        未激活 → 弹出激活弹窗
        已激活 → 弹出激活详情（有效期、剩余天数等）
        """
        if self._trial_mode:
            self._open_activation_dialog()
        else:
            info = getattr(self, '_activation_info', {})
            is_permanent = info.get("is_permanent", True)
            activated_at = info.get("activated_at", "未知")
            expire_at = info.get("expire_at", "")
            days_remaining = info.get("days_remaining", -1)

            msg = "✅ 软件已激活，全部功能正常使用。\n\n"
            msg += f"激活时间：{activated_at[:16] if activated_at else '未知'}\n"

            if is_permanent:
                msg += "授权类型：永久授权\n"
            else:
                msg += f"到期时间：{expire_at if expire_at else '未知'}\n"
                if days_remaining > 0:
                    msg += f"剩余天数：{days_remaining} 天\n"
                    if days_remaining <= 30:
                        msg += "\n⚠️ 授权即将到期，请及时联系管理员续费！"

            QMessageBox.information(self, "激活详情", msg)

    def _show_trial_prompt(self) -> None:
        from src.ui.activation_dialog import show_activation_dialog

        result = show_activation_dialog(self, trial_mode=True)
        if result:
            is_active, act_status, act_info = check_activation()
            self._trial_mode = not is_active
            self._activation_info = act_info
            self.setWindowTitle('NetOps 企业网络自动化运维平台 V0.3.0')
            self._update_activation_btn_style()
            netops_logger.get_logger().info("用户激活成功，退出试用模式")
            activated_at = act_info.get("activated_at", "")[:16]
            self._show_info(f"激活成功！\n激活时间：{activated_at}")

    def show_about_dialog(self):
        t = self._theme_engine.current_theme
        dialog = QDialog(self)
        dialog.setWindowTitle('关于')
        dialog.setFixedSize(500, 340)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setStyleSheet(f"QDialog {{ background-color: {t['card_bg']}; }}")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        version_str = 'V0.3.0' + (' 试用版' if self._trial_mode else '')
        title_label = QLabel(f'NetOps 企业网络自动化运维平台 {version_str}')
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet(f'font-size: 12pt; font-weight: bold; color: {t["text_main"]};')
        layout.addWidget(title_label)

        desc1 = QLabel('面向网络工程师的多厂商网络设备配置脚本生成与自动化运维工具，支持锐捷、华为、华三、思科等设备。\n开源项目地址: https://github.com/hanchunjun/network-config-generator')
        desc1.setAlignment(Qt.AlignLeft)
        desc1.setStyleSheet(f'font-size: 11pt; color: {t["text_secondary"]};')
        desc1.setWordWrap(True)
        layout.addWidget(desc1)

        copyright_label = QLabel('Copyright @ 2026 laohan')
        copyright_label.setAlignment(Qt.AlignLeft)
        copyright_label.setStyleSheet(f'font-size: 11pt; color: {t["text_secondary"]};')
        layout.addWidget(copyright_label)

        license_label = QLabel('Released under the MIT License')
        license_label.setAlignment(Qt.AlignLeft)
        license_label.setStyleSheet(f'font-size: 11pt; color: {t["text_secondary"]};')
        layout.addWidget(license_label)

        disclaimer = QLabel('本软件源码基于 MIT License 开源发布，可自由获取与修改。软件全功能使用需授权激活，不代表任何厂商官方立场，无任何官方认证。')
        disclaimer.setAlignment(Qt.AlignLeft)
        disclaimer.setStyleSheet(f'font-size: 11pt; color: {t["text_secondary"]};')
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        if self._trial_mode:
            activate_btn = QPushButton('🔓 软件激活')
            activate_btn.setFixedSize(120, 30)
            activate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['text_main']};
                    border: 1px solid {t['border']};
                    border-radius: {t['radius_md']}px;
                    font-size: 11pt;
                }}
                QPushButton:hover {{
                    background-color: transparent;
                    border-color: {t['border']};
                    color: {t['text_secondary']};
                }}
            """)
            activate_btn.clicked.connect(lambda: (dialog.close(), self._open_activation_dialog()))
            button_layout.addWidget(activate_btn)

        close_button = QPushButton('关闭')
        close_button.setFixedSize(100, 30)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: transparent;
                border-color: {t['border']};
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
            }}
        """)
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def _open_activation_dialog(self) -> None:
        """打开软件激活弹窗（试用模式下用户主动触发）。"""
        from src.ui.activation_dialog import show_activation_dialog
        result = show_activation_dialog(self, trial_mode=True)
        if result:
            # 激活成功，刷新状态
            is_active, act_status, act_info = check_activation()
            self._trial_mode = not is_active
            self._activation_info = act_info
            self.setWindowTitle('NetOps 企业网络自动化运维平台 V0.3.0')
            self._update_activation_btn_style()
            netops_logger.get_logger().info("用户激活成功，退出试用模式")

            # 显示激活成功详情
            activated_at = act_info.get("activated_at", "")[:16]
            is_permanent = act_info.get("is_permanent", True)
            expire_at = act_info.get("expire_at", "")[:16]
            msg = "软件已成功激活，全部功能已开放！\n\n"
            msg += f"激活时间：{activated_at}\n"
            if is_permanent:
                msg += "授权类型：永久授权"
            else:
                msg += f"到期时间：{expire_at}"
            QMessageBox.information(self, "激活成功", msg)

    def _show_account_dialog(self) -> None:
        """打开账户管理弹窗。"""
        from src.ui.account_manager_dialog import AccountManagerDialog
        dialog = AccountManagerDialog(self)
        dialog.exec_()