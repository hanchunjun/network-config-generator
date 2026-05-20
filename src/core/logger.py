import logging
import os
from datetime import datetime
from typing import Optional
from src.utils.resource_path import get_app_dir

class NetOpsLogger:
    """NetOps日志系统 — 按日期分割日志文件。

    日志文件位置：{EXE目录}/logs/netops_YYYYMMDD.log
    同时输出到文件（DEBUG级别）和控制台（INFO级别）。
    """

    LOG_DIR = os.path.join(get_app_dir(), "logs")
    LOG_FILE = f"{LOG_DIR}/netops_{datetime.now().strftime('%Y%m%d')}.log"

    def __init__(self):
        self._setup_logger()

    def _setup_logger(self):
        """配置日志系统（文件 + 控制台双输出）。"""
        os.makedirs(self.LOG_DIR, exist_ok=True)

        self.logger = logging.getLogger("NetOps")
        self.logger.setLevel(logging.DEBUG)

        # 防止重复添加处理器
        if self.logger.handlers:
            return

        # 文件处理器
        file_handler = logging.FileHandler(
            self.LOG_FILE,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """获取NetOps日志器实例。

        Returns:
            logging.Logger: 配置好的日志器，支持 debug/info/warning/error/critical
        """
        return self.logger

# 全局日志实例
netops_logger = NetOpsLogger()