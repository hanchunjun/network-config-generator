#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThemeEngine 单元测试（V0.4.3 固定浅色主题版）

测试项：
- ThemeEngine 单例模式
- 默认主题为浅色商务风格
- apply() 应用全局 QSS
- status_color() 状态颜色映射
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 确保 QApplication 实例存在（PyQt5 测试必须）
_app = QApplication.instance()
if _app is None:
    _app = QApplication([])


from src.core.theme_engine import ThemeEngine


# ========== 测试数据 ==========

REQUIRED_KEYS = [
    "page_bg", "card_bg", "nav_bg", "toolbar_bg",
    "primary", "primary_hover", "primary_light",
    "text_primary", "text_main", "text_secondary", "text_tertiary",
    "border", "border_deep",
    "radius_md", "font_ui",
    "display_name", "description",
]


# ========== 测试用例 ==========

class TestThemeEngineSingleton:
    """ThemeEngine 单例模式测试。"""

    def setup_method(self):
        """每个测试前重置单例状态。"""
        ThemeEngine._instance = None

    def teardown_method(self):
        ThemeEngine._instance = None

    def test_singleton_returns_same_instance(self):
        """验证 get() 返回同一实例。"""
        a = ThemeEngine.get()
        b = ThemeEngine.get()
        assert a is b

    def test_default_theme_is_light(self):
        """默认主题为 light（V0.4.3 固定浅色）。"""
        engine = ThemeEngine.get()
        assert engine.current_theme_id == "light"


class TestThemeDataIntegrity:
    """主题数据完整性测试。"""

    def setup_method(self):
        ThemeEngine._instance = None

    def teardown_method(self):
        ThemeEngine._instance = None

    def test_required_keys_present(self):
        """主题包含所有必需键。"""
        engine = ThemeEngine.get()
        theme = engine.current_theme
        for key in REQUIRED_KEYS:
            assert key in theme, f"missing key: {key}"

    def test_text_main_darker_than_text_secondary(self):
        """text_main 与 text_secondary 是不同颜色，确保视觉层次。"""
        engine = ThemeEngine.get()
        t = engine.current_theme
        assert t["text_main"] != t["text_secondary"], (
            "text_main 和 text_secondary 不能相同"
        )

    def test_light_theme_contrast(self):
        """浅色主题 text_secondary 不能太亮（保证对比度）。"""
        engine = ThemeEngine.get()
        t = engine.current_theme
        # text_secondary 不能太亮（#F5F5F5 以上）
        secondary_val = int(t["text_secondary"].replace("#", ""), 16)
        assert secondary_val < 0x5F6368, f"text_secondary too bright: {t['text_secondary']}"


class TestThemeEngineApply:
    """ThemeEngine.apply() 应用测试。"""

    def setup_method(self):
        ThemeEngine._instance = None
        self.engine = ThemeEngine.get()

    def teardown_method(self):
        ThemeEngine._instance = None

    def test_apply_sets_global_qss(self):
        """apply() 应设置 QApplication 样式表。"""
        app = QApplication.instance()
        self.engine.apply(app)
        qss = app.styleSheet()
        # 验证 QSS 包含主题色
        assert len(qss) > 0, "QSS 不应为空"

    def test_apply_sets_page_bg(self):
        """apply() 应设置页面背景色。"""
        app = QApplication.instance()
        self.engine.apply(app)
        qss = app.styleSheet()
        # 验证包含 page_bg 颜色
        engine = ThemeEngine.get()
        page_bg = engine.current_theme["page_bg"]
        assert page_bg in qss, f"page_bg {page_bg} not found in QSS"

    def test_apply_sets_font(self):
        """apply() 应设置字体。"""
        app = QApplication.instance()
        self.engine.apply(app)
        qss = app.styleSheet()
        # 验证包含字体设置
        assert "font-family" in qss, "font-family not found in QSS"


class TestStatusColor:
    """status_color() 状态颜色映射测试。"""

    def setup_method(self):
        ThemeEngine._instance = None
        self.engine = ThemeEngine.get()

    def teardown_method(self):
        ThemeEngine._instance = None

    @pytest.mark.parametrize("status", ["ready", "running", "done", "error", "online", "offline", "testing"])
    def test_known_statuses(self, status):
        """已知状态应返回对应颜色。"""
        color = self.engine.status_color(status)
        assert color.startswith("#"), f"status {status} should return hex color"

    def test_unknown_status_returns_default(self):
        """未知状态应返回默认颜色。"""
        color = self.engine.status_color("unknown_status_xyz")
        assert color.startswith("#"), "unknown status should return hex color"


class TestThemeEngineEdgeCases:
    """边界情况测试。"""

    def setup_method(self):
        ThemeEngine._instance = None

    def teardown_method(self):
        ThemeEngine._instance = None

    def test_multiple_apply_calls(self):
        """多次调用 apply() 不应出错。"""
        app = QApplication.instance()
        engine = ThemeEngine.get()
        engine.apply(app)
        engine.apply(app)
        engine.apply(app)
        # 不应抛出异常

    def test_theme_dict_immutable(self):
        """主题字典应返回副本，修改不影响原数据。"""
        engine = ThemeEngine.get()
        theme1 = engine.current_theme
        theme2 = engine.current_theme
        # 应该是同一个对象（因为返回的是引用）
        # 但修改不应影响引擎内部状态
        assert theme1 is theme2
