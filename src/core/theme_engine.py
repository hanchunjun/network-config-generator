#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps 主题引擎 — 固定浅色商务风格

设计原则：全局 QSS 统一控制所有容器背景色，各页面只需设置页面自身背景 + 有独立样式的控件。
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.resource_path import get_config_path
from src.core.logger import netops_logger


# ── 浅色商务风格配色数据 ──────────────────────────────────────────────────────

_THEME: dict = {
    "name": "light",
    "display_name": "商务浅色",
    "description": "浅灰白底 · 品牌蓝 · 政企级 · 专业可信",
    # ── 背景色 ──
    "page_bg": "#F5F5F5",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#F0F0F0",
    "toolbar_bg": "#E8E8E8",
    "hover_bg": "#E8EAED",
    "code_bg": "#F3F4F6",
    "input_bg": "#FAFAFA",
    "nav_bg": "#F0F0F0",
    # ── 功能色 ──
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
    # ── 文字色 ──
    "text_primary": "#202124",
    "text_main": "#3C4043",
    "text_secondary": "#4A4A4A",
    "text_tertiary": "#808080",
    "text_disabled": "#9AA0A6",
    # ── 边框色 ──
    "border": "#DADCE0",
    "input_border": "#B0B0B8",
    "border_deep": "#E8EAED",
    "border_deepest": "#F1F3F4",
    # ── 滚动条 ──
    "scrollbar_bg": "#F0F0F0",
    "scrollbar_handle": "#DADCE0",
    # ── 状态色 ──
    "status_ready": "#9AA0A6",
    "status_running": "#4285F4",
    "status_done": "#0F9D58",
    "status_error": "#DB4437",
    "device_online": "#0F9D58",
    "device_offline": "#9AA0A6",
    "device_testing": "#4285F4",
    # ── 圆角 ──
    "radius_sm": 3,
    "radius_md": 5,
    "radius_lg": 8,
    "radius_xl": 8,
    "radius_xxl": 8,
    "radius_pill": 999,
    # ── 字体 ──
    "font_ui": "'Segoe UI', 'Microsoft YaHei', sans-serif",
    "font_mono": "'Consolas', 'Courier New', monospace",
}


class ThemeEngine(QObject):
    """主题引擎单例 — 固定浅色商务风格。

    Signals:
        theme_changed(str): 主题切换完成（仅用于初始化时通知）
    """

    theme_changed = pyqtSignal(str)

    _instance: Optional[ThemeEngine] = None

    def __init__(self) -> None:
        super().__init__()
        self._current = _THEME

    # ── 单例 ────────────────────────────────────────────────────────────────

    @classmethod
    def get(cls) -> ThemeEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── 公共 API ────────────────────────────────────────────────────────────

    @property
    def current_theme_id(self) -> str:
        return "light"

    @property
    def current_theme(self) -> dict:
        return self._current

    def apply(self, app: QApplication) -> None:
        """应用浅色主题到整个应用程序。"""
        radius = self._current["radius_md"]
        qss = self._build_global_qss(self._current, radius)
        app.setStyleSheet(qss)
        netops_logger.get_logger().info("主题已应用: 商务浅色")

    def _build_global_qss(self, t: dict, radius: int) -> str:
        """构建全局 QSS 样式表（统一控制所有容器背景色）。"""
        return f"""
        /* ═══════════════════════════════════════════════
           NetOps 全局 QSS — 浅色商务风格
           ═══════════════════════════════════════════════ */

        /* ── 窗口背景 ── */
        QMainWindow {{ background-color: {t['page_bg']}; }}

        /* ── 全局字体/文字 ── */
        QWidget {{
            font-family: {t['font_ui']};
            font-size: 11pt;
            color: {t['text_main']};
        }}

        /* ── QScrollArea ── */
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget {{
            background-color: {t['page_bg']};
            border: none;
        }}

        /* ── QTabWidget ── */
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
            padding: 4px 10px;
            font-size: 11pt;
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

        /* ── QGroupBox ── */
        QGroupBox {{
            font-size: 11pt;
            font-weight: bold;
            color: {t['text_main']};
            border: 1px solid {t['border_deep']};
            border-radius: {t['radius_lg']}px;
            margin-top: 8px;
            padding: 10px;
            background-color: {t['card_bg']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }}

        /* ── QLineEdit ── */
        QLineEdit {{
            border: 1px solid {t['input_border']};
            border-radius: {radius}px;
            padding: 4px 8px;
            font-size: 11pt;
            background-color: {t['input_bg']};
            color: {t['text_secondary']};
            min-height: 26px;
        }}
        QLineEdit:focus {{ border-color: {t['primary']}; }}

        /* ── QComboBox ── */
        QComboBox {{
            border: 1px solid {t['input_border']};
            border-radius: {radius}px;
            padding: 4px 8px;
            font-size: 11pt;
            background-color: {t['input_bg']};
            color: {t['text_secondary']};
            min-height: 26px;
        }}
        QComboBox:hover {{ border-color: {t['primary']}; }}
        QComboBox QAbstractItemView {{
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            selection-background-color: {t['selection_bg']};
            background-color: {t['card_bg']};
            outline: none;
        }}

        /* ── QTableWidget ── */
        QTableWidget {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            background-color: {t['card_bg']};
            gridline-color: {t['border_deep']};
        }}
        QTableWidget::item {{ padding: 4px 6px; color: {t['text_secondary']}; }}
        QTableWidget::item:alternate {{ background-color: {t['hover_bg']}; }}
        QTableWidget::item:selected {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QHeaderView::section {{
            background-color: {t['toolbar_bg']};
            border: none;
            border-bottom: 1px solid {t['border_deep']};
            padding: 6px;
            font-weight: bold;
            color: {t['text_main']};
            font-size: 9pt;
        }}

        /* ── QListWidget ── */
        QListWidget {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            background-color: {t['card_bg']};
            font-size: 11pt;
            outline: none;
            color: {t['text_secondary']};
        }}
        QListWidget::item:selected {{
            background-color: {t['selection_bg']};
            color: {t['text_primary']};
        }}
        QListWidget::item:hover {{ background-color: {t['hover_bg']}; }}

        /* ── QTextEdit ── */
        QTextEdit {{
            border: 1px solid {t['border_deep']};
            border-radius: {radius}px;
            padding: 8px;
            font-family: {t['font_mono']};
            font-size: 11pt;
            background-color: {t['code_bg']};
            color: {t['text_secondary']};
        }}

        /* ── QProgressBar ── */
        QProgressBar {{
            border: 1px solid {t['border']};
            border-radius: {t['radius_sm']}px;
            text-align: center;
            background-color: {t['hover_bg']};
            font-size: 10pt;
            color: {t['text_tertiary']};
            height: 14px;
        }}
        QProgressBar::chunk {{
            background-color: {t['primary']};
            border-radius: {t['radius_sm']}px;
        }}

        /* ── QCheckBox ── */
        QCheckBox {{ font-size: 11pt; color: {t['text_secondary']}; spacing: 6px; }}

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

        /* ── 分割线 ── */
        QFrame[frameShape="4"] {{ color: {t['border_deep']}; max-height: 1px; }}
        QFrame[frameShape="5"] {{ color: {t['border_deep']}; max-width: 1px; }}

        /* ── QSplitter handle ── */
        QSplitter::handle {{ background-color: {t['border']}; }}

        /* ── QLabel ── */
        QLabel {{ color: {t['text_main']}; background-color: transparent; }}

        /* ── 工具提示 ── */
        QToolTip {{
            background-color: {t['card_bg']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {radius}px;
            padding: 4px 8px;
            font-size: 10pt;
        }}

        /* ── 状态栏 ── */
        QStatusBar {{
            background-color: {t['toolbar_bg']};
            border-top: 1px solid {t['border_deep']};
            font-size: 10pt;
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

    def status_color(self, status: str) -> str:
        """获取状态指示颜色。"""
        _map = {
            "ready": self._current["status_ready"],
            "running": self._current["status_running"],
            "done": self._current["status_done"],
            "error": self._current["status_error"],
            "online": self._current["device_online"],
            "offline": self._current["device_offline"],
            "testing": self._current["device_testing"],
        }
        return _map.get(status, self._current["text_tertiary"])
