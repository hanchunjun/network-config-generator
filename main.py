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
from typing import Optional, Tuple

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


def _check_activation() -> Tuple[bool, Optional[str], Optional[str]]:
    """启动时激活校验（最高优先级）。

    流程：
    1. 采集机器码（仅一次，避免重复 WMIC 调用）
    2. 检查本地激活状态
    3. 已激活 → 方案B静默黑名单校验
    4. 黑名单命中 → 提示失效并退出
    5. 未激活 → 进入试用模式（仅开放锐捷接入交换机配置）

    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (是否允许启动, 机器码, 状态描述)
    """
    from src.core.activation_engine import check_activation, perform_silent_check, get_machine_code
    from src.core.logger import netops_logger

    # 仅采集一次机器码，传递给 check_activation 和 MainWindow，避免重复 WMIC
    machine_code = get_machine_code()
    is_active, status, _info = check_activation(machine_code=machine_code)

    if is_active:
        # 方案B：激活成功后静默校验黑名单（联网失败跳过，不判失效）
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
            return False, machine_code, status

        netops_logger.get_logger().info("激活校验通过，启动主程序")
        return True, machine_code, status

    # 未激活 → 进入试用模式
    netops_logger.get_logger().info("未激活，进入试用模式（仅开放锐捷接入交换机配置）")
    return True, machine_code, status  # 试用模式也允许启动


_setup_crash_logger()
_install_qt_message_handler()

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

if __name__ == '__main__':
    # 强制进程DPI Unaware，让Windows统一做bitmap拉伸
    # 解决125%/150%系统缩放下窗口内容溢出问题
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except Exception:
        pass

    # 不跟随系统DPI缩放，保持100%/125%/150%下布局一致
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    # ★ 最高优先级：激活校验（未激活不加载任何业务模块）
    can_start, machine_code, act_status = _check_activation()
    if not can_start:
        sys.exit(1)

    # ★ 登录认证（激活通过后执行，登录成功才加载主窗口）
    from src.ui.login_dialog import LoginDialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() != QDialog.Accepted:
        sys.exit(0)

    # 激活+登录通过后才加载主窗口（传入机器码避免重复 WMIC）
    from src.ui.main_window import MainWindow
    window = MainWindow(machine_code=machine_code)
    window.show()
    sys.exit(app.exec_())