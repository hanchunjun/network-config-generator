#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps 主题引擎（ThemeEngine）

支持三套 UI 主题一键切换：
  - raycast  : Raycast 风格（紫橙渐变、毛玻璃、大圆角）
  - vscode   : VS Code 风格（深蓝黑、锐利、开发者工具感）
  - business : 商务沉稳风格（浅灰白底、品牌蓝、政企级）

用法：
    from src.core.theme_engine import ThemeEngine, Theme
    theme = ThemeEngine.get()
    theme.apply(app, Theme.VSCODE)
    qss = theme.qss("primary_btn")
"""

from __future__ import annotations

import json
import os
from enum import Enum
from typing import Dict, Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.resource_path import get_config_path
from src.core.logger import netops_logger


class Theme(str, Enum):
    """主题枚举。"""
    RAYCAST = "raycast"
    VSCODE = "vscode"
    BUSINESS = "business"


# ── 三套主题完整配色数据 ──────────────────────────────────────────────────────

_THEMES: Dict[str, dict] = {
    # ── Raycast 风格 ──────────────────────────────────────────────────────────
    "raycast": {
        "name": "Raycast",
        "display_name": "Raycast 风格",
        "description": "紫橙渐变 · 毛玻璃 · 大圆角 · 新锐科技感",
        "page_bg": "#1C1C1E",
        "card_bg": "#2C2C2E",
        "sidebar_bg": "#38383A",
        "hover_bg": "#48484A",
        "code_bg": "#252528",
        "input_bg": "#2C2C2E",
        "nav_bg": "#38383A",
        "toolbar_bg": "#38383A",
        "primary": "#A855F7",
        "primary_hover": "#9333EA",
        "primary_pressed": "#7E22CE",
        "primary_light": "#C084FC",
        "accent": "#F97316",
        "accent_hover": "#EA580C",
        "accent_light": "#FB923C",
        "selection_bg": "rgba(168,85,247,0.15)",
        "ai_bg": "rgba(249,115,22,0.15)",
        "ai_border": "#F97316",
        "ai_text": "#FB923C",
        "success": "#34D399",
        "success_hover": "#059669",
        "success_bg": "rgba(52,211,153,0.12)",
        "warning": "#FBBF24",
        "warning_hover": "#D97706",
        "warning_bg": "rgba(251,191,36,0.12)",
        "danger": "#F87171",
        "danger_hover": "#DC2626",
        "danger_bg": "rgba(248,113,113,0.12)",
        "info": "#60A5FA",
        "info_hover": "#3B82F6",
        "text_primary": "#FFFFFF",
        "text_main": "#E4E4E7",
        "text_secondary": "#A1A1AA",
        "text_tertiary": "#71717A",
        "text_disabled": "#71717A",
        "border": "#52525B",
        "input_border": "#6B6B73",
        "border_deep": "#3F3F46",
        "border_deepest": "#27272A",
        "border_glass": "rgba(255,255,255,0.08)",
        "scrollbar_bg": "#2C2C2E",
        "scrollbar_handle": "#52525B",
        "status_ready": "#71717A",
        "status_running": "#60A5FA",
        "status_done": "#34D399",
        "status_error": "#F87171",
        "device_online": "#34D399",
        "device_offline": "#52525B",
        "device_testing": "#60A5FA",
        "radius_sm": 4,
        "radius_md": 8,
        "radius_lg": 10,
        "radius_xl": 12,
        "radius_xxl": 16,
        "radius_pill": 999,
        "font_ui": "'Inter', 'SF Pro Display', 'Microsoft YaHei', sans-serif",
        "font_mono": "'JetBrains Mono', 'Consolas', 'Courier New', monospace",
        "gradient_primary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A855F7, stop:1 #F97316)",
        "gradient_primary_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9333EA, stop:1 #EA580C)",
    },

    # ── VS Code 风格 ──────────────────────────────────────────────────────────
    "vscode": {
        "name": "VS Code",
        "display_name": "VS Code 风格",
        "description": "深蓝黑 · 锐利 · 开发者工具感 · 长时间不疲劳",
        "page_bg": "#1E1E1E",
        "card_bg": "#2D2D2D",
        "sidebar_bg": "#252526",
        "hover_bg": "#2A2D2E",
        "code_bg": "#1E1E1E",
        "input_bg": "#3C3C3C",
        "nav_bg": "#252526",
        "toolbar_bg": "#2D2D30",
        "primary": "#007ACC",
        "primary_hover": "#0062A3",
        "primary_pressed": "#004F86",
        "primary_light": "#3794FF",
        "accent": "#4EC9B0",
        "accent_hover": "#3DA28F",
        "accent_light": "#4EC9B0",
        "selection_bg": "rgba(0,122,204,0.12)",
        "ai_bg": "rgba(0,122,204,0.12)",
        "ai_border": "#007ACC",
        "ai_text": "#3794FF",
        "success": "#4EC9B0",
        "success_hover": "#3DA28F",
        "success_bg": "rgba(78,201,176,0.12)",
        "warning": "#DCDCAA",
        "warning_hover": "#B8A030",
        "warning_bg": "rgba(220,220,170,0.10)",
        "danger": "#F44747",
        "danger_hover": "#CC3E3E",
        "danger_bg": "rgba(244,71,71,0.12)",
        "info": "#569CD6",
        "info_hover": "#3794FF",
        "text_primary": "#FFFFFF",
        "text_main": "#CCCCCC",
        "text_secondary": "#D4D4D4",
        "text_tertiary": "#9D9D9D",
        "text_disabled": "#808080",
        "border": "#3E3E42",
        "input_border": "#5A5A62",
        "border_deep": "#333337",
        "border_deepest": "#2D2D30",
        "border_glass": "rgba(255,255,255,0.06)",
        "scrollbar_bg": "#1E1E1E",
        "scrollbar_handle": "#424242",
        "status_ready": "#808080",
        "status_running": "#569CD6",
        "status_done": "#4EC9B0",
        "status_error": "#F44747",
        "device_online": "#4EC9B0",
        "device_offline": "#808080",
        "device_testing": "#569CD6",
        "radius_sm": 2,
        "radius_md": 3,
        "radius_lg": 4,
        "radius_xl": 4,
        "radius_xxl": 6,
        "radius_pill": 999,
        "font_ui": "'Segoe UI', 'Microsoft YaHei', sans-serif",
        "font_mono": "'Cascadia Code', 'Consolas', 'Courier New', monospace",
        "gradient_primary": None,
        "gradient_primary_hover": None,
    },

    # ── 商务沉稳风格 ──────────────────────────────────────────────────────────
    "business": {
        "name": "Business",
        "display_name": "商务沉稳风格",
        "description": "浅灰白底 · 品牌蓝 · 政企级 · 专业可信",
        "page_bg": "#F5F5F5",
        "card_bg": "#FFFFFF",
        "sidebar_bg": "#F0F0F0",
        "hover_bg": "#E8EAED",
        "code_bg": "#F3F4F6",
        "input_bg": "#FAFAFA",
        "nav_bg": "#F0F0F0",
        "toolbar_bg": "#E8E8E8",
        "primary": "#1A73E8",
        "primary_hover": "#1557B0",
        "primary_pressed": "#0D47A1",
        "primary_light": "#4285F4",
        "accent": "#5F6368",
        "accent_hover": "#3C4043",
        "accent_light": "#9AA0A6",
        "selection_bg": "rgba(26,115,232,0.08)",
        "ai_bg": "rgba(26,115,232,0.08)",
        "ai_border": "#4285F4",
        "ai_text": "#1A73E8",
        "success": "#0F9D58",
        "success_hover": "#0B8043",
        "success_bg": "rgba(15,157,88,0.08)",
        "warning": "#F4B400",
        "warning_hover": "#F09300",
        "warning_bg": "rgba(244,180,0,0.08)",
        "danger": "#DB4437",
        "danger_hover": "#C5221F",
        "danger_bg": "rgba(219,68,55,0.08)",
        "info": "#4285F4",
        "info_hover": "#1A73E8",
        "text_primary": "#202124",
        "text_main": "#3C4043",
        "text_secondary": "#4A4A4A",
        "text_tertiary": "#808080",
        "text_disabled": "#9AA0A6",
        "border": "#DADCE0",
        "input_border": "#B0B0B8",
        "border_deep": "#E8EAED",
        "border_deepest": "#F1F3F4",
        "border_glass": "rgba(0,0,0,0.06)",
        "scrollbar_bg": "#F0F0F0",
        "scrollbar_handle": "#DADCE0",
        "status_ready": "#9AA0A6",
        "status_running": "#4285F4",
        "status_done": "#0F9D58",
        "status_error": "#DB4437",
        "device_online": "#0F9D58",
        "device_offline": "#9AA0A6",
        "device_testing": "#4285F4",
        "radius_sm": 3,
        "radius_md": 4,
        "radius_lg": 6,
        "radius_xl": 8,
        "radius_xxl": 8,
        "radius_pill": 999,
        "font_ui": "'Segoe UI', 'Microsoft YaHei', sans-serif",
        "font_mono": "'Consolas', 'Courier New', monospace",
        "gradient_primary": None,
        "gradient_primary_hover": None,
    },
}


class ThemeEngine(QObject):
    """主题引擎单例。

    管理三套 UI 主题的加载、切换、持久化。
    切换主题时发射 theme_changed 信号，通知所有监听者更新样式。

    Signals:
        theme_changed(str): 主题切换完成，参数为主题 ID
    """

    theme_changed = pyqtSignal(str)

    _instance: Optional[ThemeEngine] = None
    _config_path: str = get_config_path("config/theme_config.json")
    _global_qss_cache: Dict[str, str] = {}       # 全局 QSS 缓存（键: theme_id）
    _component_qss_cache: Dict[str, str] = {}    # 组件 QSS 缓存（键: component@theme_id）

    def __init__(self) -> None:
        super().__init__()
        self._current: str = Theme.BUSINESS
        self._load_config()

    # ── 单例 ────────────────────────────────────────────────────────────────

    @classmethod
    def get(cls) -> ThemeEngine:
        """获取主题引擎单例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── 配置持久化 ──────────────────────────────────────────────────────────

    def _load_config(self) -> None:
        """从配置文件加载当前主题。"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                theme_id = cfg.get("theme", Theme.BUSINESS)
                if theme_id in _THEMES:
                    self._current = theme_id
        except Exception as e:
            netops_logger.get_logger().warning(f"主题配置加载失败: {e}")

    def _save_config(self) -> None:
        """保存当前主题到配置文件。"""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump({"theme": self._current}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            netops_logger.get_logger().warning(f"主题配置保存失败: {e}")

    # ── 公共 API ────────────────────────────────────────────────────────────

    @property
    def current_theme_id(self) -> str:
        """当前主题 ID。"""
        return self._current

    @property
    def current_theme(self) -> dict:
        """当前主题配色数据。"""
        return _THEMES[self._current]

    @property
    def available_themes(self) -> Dict[str, str]:
        """可用主题列表 {theme_id: display_name}。"""
        return {tid: data["display_name"] for tid, data in _THEMES.items()}

    def get_theme(self, theme_id: str) -> dict:
        """获取指定主题的配色数据。"""
        if theme_id not in _THEMES:
            raise ValueError(f"未知主题: {theme_id}，可用: {list(_THEMES.keys())}")
        return _THEMES[theme_id]

    def apply(self, app: QApplication, theme_id: str) -> None:
        """切换主题并应用到整个应用程序。

        Args:
            app: QApplication 实例
            theme_id: 主题 ID（Theme.RAYCAST / Theme.VSCODE / Theme.BUSINESS）
        """
        if theme_id not in _THEMES:
            raise ValueError(f"未知主题: {theme_id}")

        self._current = theme_id
        self._save_config()

        # 主题切换时清除 QSS 缓存
        ThemeEngine._global_qss_cache.clear()
        ThemeEngine._component_qss_cache.clear()

        t = _THEMES[theme_id]
        radius = t["radius_md"]

        # ── 构建全局 QSS ──────────────────────────────────────────────────
        qss = self._build_global_qss(theme_id, t, radius)
        app.setStyleSheet(qss)

        self.theme_changed.emit(theme_id)
        netops_logger.get_logger().info(f"主题已切换: {t['display_name']}")

    def _build_global_qss(self, theme_id: str, t: dict, radius: int) -> str:
        """构建全局 QSS 样式表（带缓存）。"""
        if theme_id in ThemeEngine._global_qss_cache:
            return ThemeEngine._global_qss_cache[theme_id]
        # 主按钮样式（Raycast 用渐变，其他用纯色）
        if t.get("gradient_primary"):
            primary_btn = f"""
            QPushButton {{
                background: {t['gradient_primary']};
                color: {t['text_primary']};
                border: none;
                border-radius: {t['radius_md']}px;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background: {t['gradient_primary_hover']};
            }}
            QPushButton:pressed {{
                background: {t['primary_pressed']};
            }}
            QPushButton:disabled {{
                background: {t['border_deep']};
                color: {t['text_disabled']};
            }}"""
        else:
            primary_btn = f"""
            QPushButton {{
                background-color: {t['primary']};
                color: {t['text_primary']};
                border: none;
                border-radius: {radius}px;
                font-size: 10pt;
                padding: 8px 18px;
            }}
            QPushButton:hover {{ background-color: {t['primary_hover']}; }}
            QPushButton:pressed {{ background-color: {t['primary_pressed']}; }}
            QPushButton:disabled {{
                background-color: {t['border']};
                color: {t['text_disabled']};
            }}"""

        qss = f"""
        /* ── 全局基础 ── */
        QMainWindow {{ background-color: {t['page_bg']}; }}
        QWidget {{
            font-family: {t['font_ui']};
            font-size: 10pt;
            color: {t['text_main']};
        }}

        /* ── 主按钮 ── */
        {primary_btn}

        /* ── 次要按钮 ── */
        QPushButton.secondary {{
            background-color: {t['hover_bg']};
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            font-size: 10pt;
            color: {t['text_secondary']};
            padding: 8px 16px;
        }}
        QPushButton.secondary:hover {{
            border-color: {t['primary']};
            color: {t['text_main']};
        }}

        /* ── 输入框 ── */
        QLineEdit {{
            border: 1px solid {t['input_border']};
            border-radius: {radius}px;
            padding: 8px 12px;
            font-size: 10pt;
            background-color: {t['input_bg']};
            color: {t['text_secondary']};
        }}
        QLineEdit:focus {{ border-color: {t['primary']}; }}
        QLineEdit:disabled {{
            background-color: {t['border_deepest']};
            color: {t['text_disabled']};
        }}

        /* ── 下拉框 ── */
        QComboBox {{
            border: 1px solid {t['input_border']};
            border-radius: {radius}px;
            padding: 8px 12px;
            font-size: 10pt;
            background-color: {t['input_bg']};
            color: {t['text_secondary']};
        }}
        QComboBox:hover {{ border-color: {t['primary']}; }}
        QComboBox::drop-down {{ border: none; width: 28px; }}
        QComboBox QAbstractItemView {{
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            selection-background-color: {t['selection_bg']};
            background-color: {t['card_bg']};
            outline: none;
        }}

        /* ── 表格 ── */
        QTableWidget {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            background-color: {t['card_bg']};
            gridline-color: {t['border_deep']};
        }}
        QTableWidget::item {{ padding: 6px 8px; color: {t['text_secondary']}; }}
        QTableWidget::item:alternate {{ background-color: {t['hover_bg']}; }}
        QTableWidget::item:selected {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QHeaderView::section {{
            background-color: {t['toolbar_bg']};
            border: none;
            border-bottom: 1px solid {t['border_deep']};
            padding: 8px;
            font-weight: bold;
            color: {t['text_main']};
            font-size: 9pt;
        }}

        /* ── 标签页 ── */
        QTabWidget::pane {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            background-color: {t['card_bg']};
        }}
        QTabBar::tab {{
            background-color: {t['toolbar_bg']};
            border: 1px solid {t['border_deep']};
            border-bottom: none;
            border-top-left-radius: {radius}px;
            border-top-right-radius: {radius}px;
            padding: 6px 14px;
            font-size: 10pt;
            color: {t['text_tertiary']};
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {t['card_bg']};
            color: {t['primary_light']};
            border-bottom: 2px solid {t['primary']};
            font-weight: bold;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {t['hover_bg']};
            color: {t['text_secondary']};
        }}

        /* ── 分组框 ── */
        QGroupBox {{
            font-size: 10pt;
            font-weight: bold;
            color: {t['text_main']};
            border: 1px solid {t['border_deep']};
            border-radius: {t['radius_lg']}px;
            margin-top: 10px;
            padding: 14px;
            background-color: {t['card_bg']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }}

        /* ── 列表 ── */
        QListWidget {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            background-color: {t['card_bg']};
            font-size: 10pt;
            outline: none;
            color: {t['text_secondary']};
        }}
        QListWidget::item {{ padding: 5px 8px; }}
        QListWidget::item:selected {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QListWidget::item:hover {{ background-color: {t['hover_bg']}; }}

        /* ── 文本编辑区 ── */
        QTextEdit {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            padding: 10px;
            font-family: {t['font_mono']};
            font-size: 10pt;
            background-color: {t['code_bg']};
            color: {t['text_secondary']};
        }}

        /* ── 进度条 ── */
        QProgressBar {{
            border: 1px solid {t['border']};
            border-radius: {t['radius_sm']}px;
            text-align: center;
            background-color: {t['hover_bg']};
            font-size: 10px;
            color: {t['text_tertiary']};
        }}
        QProgressBar::chunk {{
            background-color: {t['primary']};
            border-radius: {t['radius_sm']}px;
        }}

        /* ── 复选框 ── */
        QCheckBox {{ font-size: 10pt; color: {t['text_secondary']}; }}
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border-radius: {t['radius_sm']}px;
            border: 1px solid {t['border']};
            background-color: {t['input_bg']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {t['primary']};
            border-color: {t['primary']};
        }}

        /* ── 滚动条 ── */
        QScrollBar:vertical {{
            background-color: {t['scrollbar_bg']};
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {t['scrollbar_handle']};
            border-radius: {t['radius_sm']}px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{
            background-color: {t['scrollbar_bg']};
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {t['scrollbar_handle']};
            border-radius: {t['radius_sm']}px;
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

        /* ── 分割线 ── */
        QFrame[frameShape="4"] {{ color: {t['border_deep']}; max-height: 1px; }}
        QFrame[frameShape="5"] {{ color: {t['border_deep']}; max-width: 1px; }}

        /* ── 工具提示 ── */
        QToolTip {{
            background-color: {t['card_bg']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            padding: 4px 8px;
            font-size: 9pt;
        }}

        /* ── 状态栏 ── */
        QStatusBar {{
            background-color: {t['toolbar_bg']};
            border-top: 1px solid {t['border_deep']};
            font-size: 9pt;
            color: {t['text_tertiary']};
            padding: 2px 12px;
        }}

        /* ── 菜单 ── */
        QMenu {{
            background-color: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            color: {t['text_secondary']};
        }}
        QMenu::item {{ padding: 6px 20px; }}
        QMenu::item:selected {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}

        /* ── 对话框 ── */
        QDialog {{
            background-color: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_xl']}px;
        }}
        """

        ThemeEngine._global_qss_cache[theme_id] = qss
        return qss

    # ── 便捷方法 ──────────────────────────────────────────────────────────

    def qss(self, component: str) -> str:
        """获取指定组件的 QSS 片段（用于局部控件样式覆盖，带缓存）。

        Args:
            component: 组件名称，如 "primary_btn", "ai_btn", "danger_btn",
                       "input", "table", "tab", "groupbox", "list",
                       "textedit", "progressbar", "checkbox", "nav_btn",
                       "toolbar_btn", "status_btn_trial", "status_btn_expiring",
                       "status_btn_active"

        Returns:
            QSS 字符串
        """
        cache_key = f"{component}@{self._current}"
        if cache_key in ThemeEngine._component_qss_cache:
            return ThemeEngine._component_qss_cache[cache_key]

        t = self.current_theme
        r = t["radius_md"]

        _qss_map = {
            "primary_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['primary']};
                    border: 1px solid {t['primary']};
                    border-radius: {r}px;
                    font-size: 10pt;
                    font-weight: bold;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: {t['selection_bg']};
                    border: 1px solid {t['primary_hover']};
                    color: {t['primary_hover']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "ai_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['ai_text']};
                    border: 1px solid {t['ai_border']};
                    border-radius: {r}px;
                    font-size: 10pt;
                    font-weight: bold;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {t['selection_bg']};
                    border-color: {t['ai_text']};
                    color: {t['ai_text']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    color: {t['text_disabled']};
                    border-color: {t['border']};
                }}
            """,
            "danger_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['danger']};
                    border: 1px solid {t['danger']};
                    border-radius: {r}px;
                    font-size: 9pt;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {t['danger_bg']};
                    border: 1px solid {t['danger_hover']};
                    color: {t['danger_hover']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "success_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['success']};
                    border: 1px solid {t['success']};
                    border-radius: {r}px;
                    font-size: 10pt;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: {t['success_bg']};
                    border: 1px solid {t['success_hover']};
                    color: {t['success_hover']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "warning_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['warning']};
                    border: 1px solid {t['warning']};
                    border-radius: {r}px;
                    font-size: 9pt;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {t['warning_bg']};
                    border: 1px solid {t['warning_hover']};
                    color: {t['warning_hover']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "secondary_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    border-radius: {r}px;
                    font-size: 10pt;
                    color: {t['text_secondary']};
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {t['selection_bg']};
                    border-color: {t['primary']};
                    color: {t['primary']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border-color: {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "nav_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {t['radius_xxl']}px;
                    padding: 8px 14px;
                    font-size: 10pt;
                    color: {t['text_secondary']};
                }}
                QPushButton:hover {{
                    background-color: {t['hover_bg']};
                    color: {t['text_main']};
                }}
                QPushButton[active="true"] {{
                    background-color: {t['selection_bg']};
                    color: {t['primary_light']};
                    font-weight: bold;
                }}
            """,
            "toolbar_btn": f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {t['border']};
                    border-radius: {t['radius_sm']}px;
                    font-size: 11px;
                    color: {t['text_secondary']};
                    padding: 2px 8px;
                }}
                QPushButton:hover {{
                    background-color: {t['selection_bg']};
                    border-color: {t['primary']};
                    color: {t['primary']};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    border-color: {t['border']};
                    color: {t['text_disabled']};
                }}
            """,
            "status_btn_trial": f"""
                QPushButton {{
                    background-color: {t['danger_bg']};
                    border: 1px solid {t['danger']};
                    border-radius: {r}px;
                    font-size: 9pt;
                    color: {t['danger']};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {t['danger_bg']};
                }}
            """,
            "status_btn_expiring": f"""
                QPushButton {{
                    background-color: {t['warning_bg']};
                    border: 1px solid {t['warning']};
                    border-radius: {r}px;
                    font-size: 9pt;
                    color: {t['warning']};
                    font-weight: bold;
                }}
            """,
            "status_btn_active": f"""
                QPushButton {{
                    background-color: {t['success_bg']};
                    border: 1px solid {t['success']};
                    border-radius: {r}px;
                    font-size: 9pt;
                    color: {t['success']};
                    font-weight: bold;
                }}
            """,
        }

        if component not in _qss_map:
            raise ValueError(f"未知组件: {component}，可用: {list(_qss_map.keys())}")
        result = _qss_map[component]
        ThemeEngine._component_qss_cache[cache_key] = result
        return result

    def status_color(self, status: str) -> str:
        """获取状态指示颜色。

        Args:
            status: 状态名称 - "ready", "running", "done", "error",
                    "online", "offline", "testing"
        """
        t = self.current_theme
        _map = {
            "ready": t["status_ready"],
            "running": t["status_running"],
            "done": t["status_done"],
            "error": t["status_error"],
            "online": t["device_online"],
            "offline": t["device_offline"],
            "testing": t["device_testing"],
        }
        return _map.get(status, t["text_tertiary"])  # type: ignore[no-any-return]
