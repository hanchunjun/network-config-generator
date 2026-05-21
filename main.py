#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps网络自动化运维工具主程序入口

V0.3.0 新增：启动时强制激活校验（最高优先级）
- 未激活 → 弹出激活弹窗，激活成功后继续
- 激活失败退出 → 软件不加载任何业务模块
- 方案B：激活成功后静默校验180天黑名单
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


def _check_activation() -> bool:
    """启动时激活校验（最高优先级）。

    流程：
    1. 检查本地激活状态
    2. 未激活 → 弹出激活弹窗
    3. 激活成功后 → 方案B静默黑名单校验
    4. 黑名单命中 → 提示失效并退出

    Returns:
        bool: 是否通过激活校验
    """
    from src.core.activation_engine import check_activation, perform_silent_check
    from src.core.logger import netops_logger

    is_active, status = check_activation()

    if not is_active:
        # 未激活 → 弹出激活弹窗
        from src.ui.activation_dialog import show_activation_dialog
        activated = show_activation_dialog()

        if not activated:
            netops_logger.get_logger().warning("用户未完成激活，程序退出")
            return False

    # 方案B：激活成功后静默校验黑名单（联网失败跳过，不判失效）
    valid, msg = perform_silent_check()
    if not valid:
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtCore import Qt
        msg_box = QMessageBox()
        msg_box.setWindowTitle("软件授权已失效")
        msg_box.setText(
            "当前设备对应的软件使用权限已被管理员收回，无法继续正常使用。\n\n"
            "如需重新开通软件使用权限，请联系管理员【天技老韩】重新审核办理。"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        netops_logger.get_logger().warning("黑名单校验未通过，程序退出")
        return False

    netops_logger.get_logger().info("激活校验通过，启动主程序")
    return True


_setup_crash_logger()
_install_qt_message_handler()

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ★ 最高优先级：激活校验（未激活不加载任何业务模块）
    if not _check_activation():
        sys.exit(1)

    # 激活通过后才加载主窗口
    from src.ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())