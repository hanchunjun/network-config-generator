#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps 管理员制码工具 — 独立程序入口

仅限管理员【老韩】本地使用，禁止外发。
"""

import os
import sys

# 配置Qt环境变量
if "QT_DEVICE_PIXEL_RATIO" in os.environ:
    del os.environ["QT_DEVICE_PIXEL_RATIO"]
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from src.ui.admin_tool_window import run_admin_tool

if __name__ == "__main__":
    run_admin_tool()
