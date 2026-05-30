#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetOps 管理员制码工具 — 独立程序入口

仅限管理员【老韩】本地使用，禁止外发。
"""

import os
import sys

from src.utils.app_factory import setup_dpi_environment

setup_dpi_environment()

sys.path.append(os.path.dirname(__file__))

from src.ui.admin_tool_window import run_admin_tool

if __name__ == "__main__":
    run_admin_tool()