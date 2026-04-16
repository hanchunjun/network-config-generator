import sys
import os


def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和打包后的EXE环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包后的EXE，使用脚本所在目录的父目录（项目根目录）
        # 获取当前文件所在目录（utils）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（utils的父目录）
        base_path = os.path.dirname(current_dir)
    
    # 构建完整路径
    full_path = os.path.join(base_path, relative_path)
    print(f"Resource path: {full_path}")  # 调试信息
    print(f"Path exists: {os.path.exists(full_path)}")  # 调试信息
    
    return full_path
