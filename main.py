#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps网络自动化运维工具主程序入口

V0.3.1 新增：启动闪屏 + 延迟加载非关键页面
- 启动时立即显示闪屏窗口（蓝色背景 + Logo + 版本号）
- 主窗口初始化仅创建首屏（设备配置）页面
- 其他页面在首次切换到该Tab时才创建（懒加载）
- 消除重复的 check_activation() 调用
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
    2. 已激活 → 方案B静默黑名单校验
    3. 黑名单命中 → 提示失效并退出
    4. 未激活 → 进入试用模式（仅开放锐捷接入交换机配置和批量命令生成）

    Returns:
        bool: 是否允许继续启动（激活或试用模式均返回True）
    """
    from src.core.activation_engine import check_activation, perform_silent_check
    from src.core.logger import netops_logger

    is_active, status, _info = check_activation()

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
            return False

        netops_logger.get_logger().info("激活校验通过，启动主程序")
        return True

    # 未激活 → 进入试用模式
    netops_logger.get_logger().info("未激活，进入试用模式（仅开放锐捷接入交换机配置和批量命令生成）")
    return True  # 试用模式也允许启动


def _create_splash_screen(app):
    """创建并显示闪屏窗口。

    使用纯代码绘制，不依赖外部图片资源，确保在任何环境下都能正常显示。

    Returns:
        QSplashScreen: 闪屏窗口实例
    """
    from PyQt5.QtWidgets import QSplashScreen
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter

    pixmap = QPixmap(480, 320)
    pixmap.fill(QColor(22, 93, 255))  # 品牌蓝

    painter = QPainter(pixmap)
    painter.setPen(QColor(255, 255, 255))

    # 主标题
    title_font = QFont("Microsoft YaHei", 24, QFont.Bold)
    painter.setFont(title_font)
    painter.drawText(pixmap.rect().adjusted(0, -60, 0, 0), Qt.AlignCenter, "NetOps")

    # 副标题
    sub_font = QFont("Microsoft YaHei", 11)
    painter.setFont(sub_font)
    painter.drawText(pixmap.rect().adjusted(0, -10, 0, 0), Qt.AlignCenter, "企业网络自动化运维平台")

    # 分隔线
    painter.drawLine(140, 170, 340, 170)

    # 版本号
    ver_font = QFont("Microsoft YaHei", 10)
    painter.setFont(ver_font)
    painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, "V0.3.1")

    # 加载提示
    loading_font = QFont("Microsoft YaHei", 9)
    painter.setFont(loading_font)
    painter.setPen(QColor(200, 210, 240))
    painter.drawText(pixmap.rect().adjusted(0, 90, 0, 0), Qt.AlignCenter, "正在初始化...")

    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    return splash


_setup_crash_logger()
_install_qt_message_handler()

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

if __name__ == '__main__':
    # 启用高DPI缩放，避免字体在125%/150%缩放过过大
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    # ★ 最高优先级：激活校验（未激活不加载任何业务模块）
    if not _check_activation():
        sys.exit(1)

    # 显示闪屏（激活通过后立即显示，给用户即时反馈）
    splash = _create_splash_screen(app)

    # 激活通过后才加载主窗口
    from src.ui.main_window import MainWindow
    window = MainWindow(splash=splash)
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())
