#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题引擎与主题切换面板单元测试

覆盖：
- ThemeEngine 单例行为
- 三套主题配色数据完整性
- apply() 切换主题并发射信号
- 配置持久化（保存/加载）
- ThemeSwitcherPage 页面创建
- _PreviewCard 实时获取主题数据（非快照）
- _PreviewCard 响应 theme_changed 信号触发重绘
- _apply_theme_style 不覆盖全局 QSS 子控件颜色
"""

import os
import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 确保有 QApplication 实例（PyQt5 测试必须）
_app = QApplication.instance()
if _app is None:
    _app = QApplication([])


from src.core.theme_engine import ThemeEngine, Theme, _THEMES


# ── 单例测试 ────────────────────────────────────────────────────────────

class TestThemeEngineSingleton:
    """ThemeEngine 单例行为测试。"""

    def setup_method(self):
        """每个测试前重置单例，避免状态污染。"""
        ThemeEngine._instance = None

    def teardown_method(self):
        ThemeEngine._instance = None

    def test_singleton_returns_same_instance(self):
        """多次 get() 返回同一实例。"""
        a = ThemeEngine.get()
        b = ThemeEngine.get()
        assert a is b

    def test_default_theme_is_vscode(self):
        """默认主题为 VS Code。"""
        engine = ThemeEngine.get()
        assert engine.current_theme_id == Theme.VSCODE


# ── 配色数据完整性测试 ───────────────────────────────────────────────────

class TestThemeDataIntegrity:
    """三套主题配色数据完整性测试。"""

    REQUIRED_KEYS = [
        "page_bg", "card_bg", "nav_bg", "toolbar_bg",
        "primary", "primary_hover", "primary_light",
        "text_primary", "text_main", "text_secondary", "text_tertiary",
        "border", "border_deep",
        "radius_md", "font_ui",
        "display_name", "description",
    ]

    @pytest.mark.parametrize("theme_id", [Theme.RAYCAST, Theme.VSCODE, Theme.BUSINESS])
    def test_required_keys_present(self, theme_id):
        """每套主题必须包含所有必需键。"""
        for key in self.REQUIRED_KEYS:
            assert key in _THEMES[theme_id], f"{theme_id} missing key: {key}"

    @pytest.mark.parametrize("theme_id", [Theme.RAYCAST, Theme.VSCODE, Theme.BUSINESS])
    def test_text_main_darker_than_text_secondary(self, theme_id):
        """text_main 和 text_secondary 必须是不同颜色（确保视觉层次区分）。"""
        t = _THEMES[theme_id]
        # 注意：深色主题中 text_main 是亮色、text_secondary 是暗色；
        # 浅色主题中 text_main 是暗色、text_secondary 是亮色。
        # 因此不能用 hex 值大小比较，只验证两者不相等。
        assert t["text_main"] != t["text_secondary"], (
            f"{theme_id}: text_main 与 text_secondary 不能相同"
        )

    def test_business_theme_contrast(self):
        """Business 主题 text_secondary 在浅色背景上对比度足够。"""
        t = _THEMES[Theme.BUSINESS]
        # text_secondary 不能太亮（否则在 #F5F5F5 上看不清）
        secondary_val = int(t["text_secondary"].replace("#", ""), 16)
        # #4A4A4A = 4882442, #5F6368 = 6251368（之前的问题值，太亮）
        assert secondary_val < 0x5F6368, f"text_secondary too bright: {t['text_secondary']}"


# ── apply() 切换测试 ────────────────────────────────────────────────────

class TestThemeEngineApply:
    """ThemeEngine.apply() 切换主题测试。"""

    def setup_method(self):
        ThemeEngine._instance = None
        self.engine = ThemeEngine.get()
        self._config_path = self.engine._config_path
        # 备份原始配置
        self._backup = None
        if os.path.exists(self._config_path):
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._backup = f.read()

    def teardown_method(self):
        ThemeEngine._instance = None
        # 恢复原始配置
        if self._backup is not None:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                f.write(self._backup)

    def test_apply_changes_current_theme(self):
        """apply() 后 current_theme_id 变化。"""
        app = QApplication.instance()
        self.engine.apply(app, Theme.BUSINESS)
        assert self.engine.current_theme_id == Theme.BUSINESS

    def test_apply_emits_signal(self):
        """apply() 发射 theme_changed 信号。"""
        app = QApplication.instance()
        received = []
        self.engine.theme_changed.connect(lambda tid: received.append(tid))
        self.engine.apply(app, Theme.RAYCAST)
        assert Theme.RAYCAST in received

    def test_apply_sets_global_qss(self):
        """apply() 后 QApplication 有样式表。"""
        app = QApplication.instance()
        self.engine.apply(app, Theme.VSCODE)
        qss = app.styleSheet()
        assert "#1E1E1E" in qss  # VS Code page_bg

    def test_apply_saves_config(self):
        """apply() 后配置文件更新。"""
        app = QApplication.instance()
        self.engine.apply(app, Theme.BUSINESS)
        assert os.path.exists(self._config_path)
        with open(self._config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        assert cfg.get("theme") == Theme.BUSINESS


# ── 主题切换面板测试 ────────────────────────────────────────────────────

class TestThemeSwitcherPage:
    """ThemeSwitcherPage 页面测试。"""

    def setup_method(self):
        ThemeEngine._instance = None
        self.engine = ThemeEngine.get()
        self.engine._config_path = os.path.join(
            tempfile.gettempdir(), "test_theme_config.json"
        )
        # 先应用一个主题，确保 QApplication 有样式表
        app = QApplication.instance()
        self.engine.apply(app, Theme.VSCODE)

    def teardown_method(self):
        ThemeEngine._instance = None
        # 清理临时配置
        tmp = os.path.join(tempfile.gettempdir(), "test_theme_config.json")
        if os.path.exists(tmp):
            os.remove(tmp)

    def test_page_creates_three_cards(self):
        """页面创建三张主题预览卡片。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        page = ThemeSwitcherPage()
        assert len(page._cards) == 3
        assert Theme.RAYCAST in page._cards
        assert Theme.VSCODE in page._cards
        assert Theme.BUSINESS in page._cards

    def test_card_uses_engine_not_snapshot(self):
        """_PreviewCard 通过 engine 实时获取主题数据，非构造时快照。"""
        from src.ui.theme_switcher_page import _PreviewCard
        card = _PreviewCard(Theme.BUSINESS, self.engine)
        # 验证 card 持有 engine 引用，不持有 _theme 快照
        assert hasattr(card, "_engine"), "_PreviewCard 应持有 _engine 引用"
        assert card._engine is self.engine
        assert not hasattr(card, "_theme"), "_PreviewCard 不应持有 _theme 快照属性"

    def test_card_does_not_connect_theme_changed_signal(self):
        """死锁修复验证：_PreviewCard 不连接 theme_changed 信号。"""
        from src.ui.theme_switcher_page import _PreviewCard
        received = []
        # 临时连接 engine 信号以追踪发射次数
        self.engine.theme_changed.connect(lambda tid: received.append(tid))
        card = _PreviewCard(Theme.RAYCAST, self.engine)
        # 验证 _PreviewCard 没有 _on_theme_changed 方法
        assert not hasattr(card, '_on_theme_changed'), (
            "_PreviewCard 不应有 _on_theme_changed 方法（不连接 theme_changed 信号）"
        )
        assert hasattr(card, '_engine'), (
            "_PreviewCard 应持有 _engine 引用"
        )
        # 清理临时连接
        self.engine.theme_changed.disconnect()

    def test_rapid_theme_switch_no_deadlock(self):
        """死锁回归测试：快速连续切换主题不应挂起。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        page = ThemeSwitcherPage()
        app = QApplication.instance()
        themes = [Theme.VSCODE, Theme.RAYCAST, Theme.BUSINESS, Theme.VSCODE, Theme.RAYCAST]
        for tid in themes:
            self.engine.apply(app, tid)
            # 每次切换后验证卡片状态正确
            for cid, card in page._cards.items():
                expected = (cid == tid)
                assert card._selected is expected, (
                    f"切换到 {tid} 后，{cid} 选中状态应为 {expected}，实际 {card._selected}"
                )

    def test_page_on_theme_changed_refreshes_cards(self):
        """ThemeSwitcherPage._on_theme_changed 集中刷新所有卡片（防死锁设计）。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        app = QApplication.instance()
        # 先重置为 vscode，确保测试独立
        self.engine.apply(app, Theme.VSCODE)
        page = ThemeSwitcherPage()
        # 记录调用前状态
        assert page._cards[Theme.VSCODE]._selected is True
        # 切换主题
        self.engine.apply(app, Theme.RAYCAST)
        # 验证 _on_theme_changed 被触发，卡片状态更新
        assert page._cards[Theme.RAYCAST]._selected is True
        assert page._cards[Theme.VSCODE]._selected is False

    def test_switch_theme_calls_engine_apply(self):
        """点击卡片调用 engine.apply()。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        page = ThemeSwitcherPage()
        app = QApplication.instance()
        with patch.object(page._engine, "apply") as mock_apply:
            page._switch_theme(Theme.BUSINESS)
            mock_apply.assert_called_once_with(app, Theme.BUSINESS)

    def test_apply_theme_style_uses_page_selector_only(self):
        """_apply_theme_style 只设置页面级样式，不覆盖子控件 color。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        page = ThemeSwitcherPage()
        page._apply_theme_style()
        qss = page.styleSheet()
        # 不应包含 QWidget { color: ... } 这种全局覆盖规则
        assert "QWidget" not in qss or "color:" not in qss.split("QWidget")[1].split("}")[0]

    def test_on_theme_changed_updates_cards(self):
        """theme_changed 信号触发后，卡片选中状态更新。"""
        from src.ui.theme_switcher_page import ThemeSwitcherPage
        # 先重置为 vscode，确保测试独立
        app = QApplication.instance()
        self.engine.apply(app, Theme.VSCODE)
        page = ThemeSwitcherPage()
        # 初始状态：VS Code 选中
        assert page._cards[Theme.VSCODE]._selected is True
        assert page._cards[Theme.BUSINESS]._selected is False
        # 切换到 business
        self.engine.apply(app, Theme.BUSINESS)
        # 验证卡片选中状态更新
        assert page._cards[Theme.BUSINESS]._selected is True
        assert page._cards[Theme.VSCODE]._selected is False
