"""全局测试配置。"""
import os
import sys

# 将项目根目录加入 sys.path，确保 from src.xxx 可导入
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
