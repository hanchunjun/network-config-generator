import os
import json
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Union, Optional, List, Any

_logger = logging.getLogger("NetOps.FileOperators")

class AtomicFileWriter:
    """原子文件写入器，防止写入过程中文件损坏"""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.temp_path: Optional[Path] = None

    def __enter__(self):
        """创建临时文件"""
        temp_dir = self.file_path.parent
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(
            dir=temp_dir,
            prefix=f".{self.file_path.name}.tmp.",
            suffix=None
        )
        self.temp_path = Path(temp_path)
        os.close(fd)

        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时原子替换文件"""
        if self.temp_path is None:
            return False

        if exc_type is not None:
            # 发生异常，删除临时文件
            try:
                self.temp_path.unlink(missing_ok=True)
            except Exception:
                pass
            return False

        try:
            # 确保临时文件已完全写入磁盘
            # Windows 不支持 POSIX 权限模型，跳过 chmod
            if os.name != "nt":
                self.temp_path.chmod(0o644)

            # 原子替换原文件
            self.temp_path.replace(self.file_path)
        except Exception:
            # 替换失败，清理临时文件
            try:
                self.temp_path.unlink(missing_ok=True)
            except Exception:
                pass
            raise

        return False


class JSONFileManager:
    """JSON文件管理器，支持原子操作"""

    @staticmethod
    def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
        """
        安全加载JSON文件

        Args:
            file_path: 文件路径
            default: 文件不存在时的默认值

        Returns:
            JSON数据或默认值
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {e}")
        except Exception as e:
            raise IOError(f"读取文件失败: {e}")

    @staticmethod
    def save_json(file_path: Union[str, Path], data: Any, indent: int = 2) -> bool:
        """
        原子保存JSON文件

        Args:
            file_path: 文件路径
            data: 要保存的数据
            indent: 缩进空格数

        Returns:
            是否成功
        """
        try:
            with AtomicFileWriter(file_path) as temp_file:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            _logger.error(f"保存JSON文件失败: {e}")
            return False


class DeviceFileManager:
    """设备文件管理器"""

    @staticmethod
    def load_device_list(file_path: Union[str, Path]) -> List[str]:
        """
        加载设备列表文件内容

        Args:
            file_path: 文件路径

        Returns:
            文件行列表
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            raise IOError(f"读取设备列表失败: {e}")

    @staticmethod
    def save_device_list(file_path: Union[str, Path], lines: List[str]) -> bool:
        """
        原子保存设备列表

        Args:
            file_path: 文件路径
            lines: 要保存的行列表

        Returns:
            是否成功
        """
        try:
            with AtomicFileWriter(file_path) as temp_file:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            return True
        except Exception as e:
            _logger.error(f"保存设备列表失败: {e}")
            return False