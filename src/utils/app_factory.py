#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序工厂 — 统一 DPI/环境/Qt 初始化

main.py 和 admin_tool_main.py 共用，消除重复代码。
"""

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication


def setup_dpi_environment():
    """统一DPI环境变量注入（QApplication构造前调用）"""
    for key in ("QT_DEVICE_PIXEL_RATIO", "QT_AUTO_SCREEN_SCALE_FACTOR", "QT_SCALE_FACTOR"):
        os.environ.pop(key, None)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"


def create_application(argv=None):
    """创建QApplication并完成三步DPI锁定

    第1步：关闭Qt高DPI缩放属性（构造前）
    第2步：强制进程DPI Unaware（Windows层bitmap拉伸兜底）
    第3步：Fusion样式 + 文本抗锯齿

    Returns:
        QApplication: 已初始化的应用实例
    """
    if argv is None:
        argv = sys.argv

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)  # type: ignore[attr-defined]
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)  # type: ignore[attr-defined]
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # type: ignore[attr-defined]

    app = QApplication(argv)

    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except Exception:
        pass

    app.setStyle("Fusion")
    font = app.font()
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    return app