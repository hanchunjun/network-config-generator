#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps网络自动化运维工具主程序入口

V0.4.0 重构：DPI工厂化 + 独一入口
"""

import os
import sys
import traceback
import logging
from datetime import datetime
from typing import Optional, Tuple

from src.utils.app_factory import setup_dpi_environment

setup_dpi_environment()

sys.path.append(os.path.dirname(__file__))


def _setup_crash_logger():
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
    try:
        from PyQt5.QtCore import qInstallMessageHandler
        def _qt_handler(mode, context, msg):
            pass
        qInstallMessageHandler(_qt_handler)
    except Exception:
        pass


def _check_activation() -> Tuple[bool, str, str, dict]:
    from src.core.activation_engine import check_activation, perform_silent_check, get_machine_code
    from src.core.logger import netops_logger

    machine_code = get_machine_code()
    is_active, act_status, act_info = check_activation(machine_code=machine_code)

    if is_active:
        valid, msg = perform_silent_check()
        if not valid:
            from PyQt5.QtWidgets import QMessageBox
            msg_box = QMessageBox()
            msg_box.setWindowTitle("软件授权已失效")
            msg_box.setText(
                "当前设备对应的软件使用权限已被管理员收回，无法继续正常使用。\n\n"
                "如需重新开通软件使用权限，请联系管理员【老韩】重新审核办理。"
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            netops_logger.get_logger().warning("黑名单校验未通过，程序退出")
            return False, machine_code, act_status, act_info

        netops_logger.get_logger().info("激活校验通过，启动主程序")
        return True, machine_code, act_status, act_info

    netops_logger.get_logger().info("未激活，进入试用模式（仅开放锐捷接入交换机配置）")
    return True, machine_code, act_status, act_info


_setup_crash_logger()
_install_qt_message_handler()

from PyQt5.QtWidgets import QDialog

if __name__ == '__main__':
    from src.utils.app_factory import create_application

    app = create_application()

    can_start, machine_code, act_status, act_info = _check_activation()
    if not can_start:
        sys.exit(1)

    from src.ui.login_dialog import LoginDialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() != QDialog.Accepted:
        sys.exit(0)

    from src.ui.main_window import MainWindow
    is_active = act_status != "未激活"
    window = MainWindow(is_active=is_active, act_status=act_status, act_info=act_info)
    window.show()
    sys.exit(app.exec_())