#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps网络自动化运维工具主程序入口
"""

import os
import sys
import traceback
import logging
from datetime import datetime

# 配置Qt环境变量
if "QT_DEVICE_PIXEL_RATIO" in os.environ:
    del os.environ["QT_DEVICE_PIXEL_RATIO"]
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))


def _setup_crash_logger():
    """安装全局异常钩子，将未捕获异常写入崩溃日志"""
    _log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(_log_dir, exist_ok=True)
    _crash_log = os.path.join(_log_dir, "crash.log")

    def _write_crash(exc_type, exc_val, exc_tb):
        try:
            with open(_crash_log, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 未捕获异常\n")
                f.write(f"类型: {exc_type.__name__}\n")
                f.write(f"信息: {exc_val}\n")
                f.write("堆栈:\n")
                traceback.print_exception(exc_type, exc_val, exc_tb, file=f)
        except Exception:
            pass

    _orig_excepthook = sys.excepthook

    def _global_excepthook(exc_type, exc_val, exc_tb):
        _write_crash(exc_type, exc_val, exc_tb)
        _orig_excepthook(exc_type, exc_val, exc_tb)

    sys.excepthook = _global_excepthook


def _install_qt_message_handler():
    """安装Qt消息处理器，捕获Qt内部警告"""
    try:
        from PyQt5.QtCore import qInstallMessageHandler
        def _qt_handler(mode, context, msg):
            pass  # 静默Qt内部消息，避免干扰
        qInstallMessageHandler(_qt_handler)
    except Exception:
        pass


_setup_crash_logger()
_install_qt_message_handler()

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())