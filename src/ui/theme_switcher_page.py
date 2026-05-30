#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题切换面板

提供三套 UI 主题（Raycast / VS Code / 商务沉稳）的一键切换功能，
带实时预览卡片和即时生效。
"""

import sys
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QPainterPath, QColor, QLinearGradient
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy,
)

from src.core.theme_engine import ThemeEngine, Theme


class _PreviewCard(QWidget):
    """主题预览卡片 — 绘制小型主题预览图。

    设计约定（防死锁）：
    - 不连接 theme_changed 信号，避免与 clicked 信号嵌套导致事件循环死锁
    - paintEvent 内实时从引擎获取配色数据，不使用构造时快照
    - 卡片刷新由父组件 ThemeSwitcherPage._on_theme_changed 集中调用 card.update()

    注意：继承 QWidget 而非 QFrame，因为 QFrame 默认不处理鼠标事件，
    导致 mousePressEvent 不会被调用，clicked 信号无法发射。
    """

    clicked = pyqtSignal()

    def __init__(self, theme_id: str, engine: ThemeEngine, parent=None) -> None:
        super().__init__(parent)
        self._theme_id = theme_id
        self._engine = engine
        self._selected = False
        self.setFixedSize(220, 160)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.update()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # 实时从引擎获取最新主题数据，不使用快照
        t = self._engine.get_theme(self._theme_id)
        r = 10

        # 外框（选中时高亮）
        if self._selected:
            p.setPen(QColor(t["primary"]))
            p.setBrush(QColor(t["page_bg"]))
            p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), r, r)
        else:
            p.setPen(QColor(t["border"]))
            p.setBrush(QColor(t["page_bg"]))
            p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), r, r)

        # 内部预览区域
        inner = self.rect().adjusted(12, 12, -12, -36)

        # 导航栏
        nav_h = 22
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(t["nav_bg"]))
        p.drawRoundedRect(inner.x(), inner.y(), inner.width(), nav_h, 4, 4)

        # 导航按钮点
        dot_colors = [QColor(t["primary_light"]), QColor(t["text_tertiary"]),
                       QColor(t["text_tertiary"]), QColor(t["text_tertiary"])]
        for i, dc in enumerate(dot_colors):
            p.setBrush(dc)
            p.drawEllipse(inner.x() + 8 + i * 22, inner.y() + 7, 8, 8)

        # 内容区
        content_y = inner.y() + nav_h + 6
        content_h = inner.height() - nav_h - 6
        p.setBrush(QColor(t["card_bg"]))
        p.setPen(QColor(t["border"]))
        p.drawRoundedRect(inner.x(), content_y, inner.width(), content_h, 6, 6)

        # 模拟内容块
        bar_w = int(inner.width() * 0.6)
        bar_h = 8
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(t["text_main"]))
        p.drawRoundedRect(inner.x() + 10, content_y + 12, bar_w, bar_h, 3, 3)
        p.setBrush(QColor(t["text_tertiary"]))
        p.drawRoundedRect(inner.x() + 10, content_y + 28, int(bar_w * 0.7), bar_h, 3, 3)

        # 模拟按钮
        btn_w = 50
        btn_h = 16
        btn_x = inner.x() + inner.width() - btn_w - 10
        btn_y = content_y + content_h - btn_h - 10
        if t.get("gradient_primary") and self._theme_id == "raycast":
            grad = QLinearGradient(btn_x, btn_y, btn_x + btn_w, btn_y + btn_h)
            grad.setColorAt(0, QColor(t["primary"]))
            grad.setColorAt(1, QColor(t["accent"]))
            p.setBrush(grad)
        else:
            p.setBrush(QColor(t["primary"]))
        p.drawRoundedRect(btn_x, btn_y, btn_w, btn_h, 4, 4)

        p.end()


class ThemeSwitcherPage(QWidget):
    """主题切换面板页面。

    显示三套主题的预览卡片，点击即可即时切换全局主题。

    Signals:
        theme_switched(str): 主题已切换，参数为主题 ID
    """

    theme_switched = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._engine = ThemeEngine.get()
        self._cards: dict = {}
        self._setup_ui()

        # 连接 theme_changed 信号，集中刷新页面样式和卡片选中状态。
        # 注意：槽函数内只操作本页面控件和卡片，不调用 app.setStyleSheet()
        # （全局 QSS 由 ThemeEngine.apply() 负责），避免事件循环嵌套死锁。
        self._engine.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(10)

        # ── 标题 ──
        title = QLabel("🎨  主题切换")
        title.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("选择界面主题，即时生效")
        desc.setFont(QFont("Microsoft YaHei", 10))
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        layout.addWidget(line)

        # ── 主题卡片区域 ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)
        cards_row.setAlignment(Qt.AlignCenter)

        theme_ids = [Theme.RAYCAST, Theme.VSCODE, Theme.BUSINESS]
        for tid in theme_ids:
            card_container = QVBoxLayout()
            card_container.setSpacing(8)

            card = _PreviewCard(tid, self._engine)
            card.clicked.connect(lambda t=tid: self._switch_theme(t))
            self._cards[tid] = card
            card_container.addWidget(card, alignment=Qt.AlignCenter)

            # 主题名称
            name = QLabel(self._engine.get_theme(tid)["display_name"])
            name.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
            name.setAlignment(Qt.AlignCenter)
            card_container.addWidget(name)

            # 主题描述
            desc_lbl = QLabel(self._engine.get_theme(tid)["description"])
            desc_lbl.setFont(QFont("Microsoft YaHei", 8))
            desc_lbl.setAlignment(Qt.AlignCenter)
            desc_lbl.setWordWrap(True)
            desc_lbl.setFixedWidth(220)
            card_container.addWidget(desc_lbl)

            cards_row.addLayout(card_container)

        layout.addLayout(cards_row)

        # ── 当前主题指示 ──
        self._current_label = QLabel()
        self._current_label.setFont(QFont("Microsoft YaHei", 10))
        self._current_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._current_label)

        layout.addStretch()

        # ── 底部提示 ──
        tip = QLabel("提示：主题切换即时生效，无需重启程序")
        tip.setFont(QFont("Microsoft YaHei", 8))
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)

        # 初始化选中状态
        self._update_card_selection()

    def _switch_theme(self, theme_id: str) -> None:
        """切换主题。"""
        app = QApplication.instance()
        if app is None:
            return
        self._engine.apply(app, theme_id)
        self.theme_switched.emit(theme_id)

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题变化后集中刷新页面样式和卡片状态。

        设计约定（防死锁）：
        - 不调用 app.setStyleSheet()（全局样式由 engine.apply() 负责）
        - 直接操作本页面控件和卡片，调用 card.update() 触发重绘
        - 子组件 _PreviewCard 不连接 theme_changed 信号
        """
        self._apply_theme_style()
        self._update_card_selection()
        # 集中刷新所有预览卡片（paintEvent 实时获取配色）
        for card in self._cards.values():
            card.update()

    def _update_card_selection(self) -> None:
        """更新卡片选中状态和当前主题标签。"""
        current = self._engine.current_theme_id
        for tid, card in self._cards.items():
            card.set_selected(tid == current)
        t = self._engine.current_theme
        self._current_label.setText(f"当前主题：{t['display_name']}")

    def _apply_theme_style(self) -> None:
        """根据当前主题更新页面样式。

        注意：只设置页面级背景色和字体，不覆盖 color 属性，
        避免局部 setStyleSheet 的全局 QWidget color 规则覆盖
        QApplication 级别的主题 QSS 对子控件的影响。
        """
        t = self._engine.current_theme
        self.setStyleSheet(f"""
            ThemeSwitcherPage {{
                background-color: {t['page_bg']};
                font-family: {t['font_ui']};
            }}
        """)
        # 更新标题颜色（直接针对具体 QLabel，不用全局规则）
        for child in self.findChildren(QLabel):
            if child.text().startswith("🎨"):
                child.setStyleSheet(f"color: {t['text_main']}; background: transparent;")
                break


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    # 初始化默认主题
    ThemeEngine.get().apply(app, Theme.VSCODE)
    page = ThemeSwitcherPage()
    page.setWindowTitle("主题切换")
    page.resize(800, 500)
    page.show()
    sys.exit(app.exec_())
