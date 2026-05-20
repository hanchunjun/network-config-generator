#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提交前自动化检查流水线 — 一键运行全部质量门禁。

用法：
    python scripts/pre_commit_check.py          # 完整检查
    python scripts/pre_commit_check.py --quick   # 仅语法+测试+类型（快速模式）

退出码：
    0 = 全部通过
    1 = 存在失败项
"""
import subprocess
import sys
import os

# 切换到项目根目录
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(step: str, cmd: str) -> bool:
    """执行单步检查，返回是否通过。"""
    print(f"\n{'='*60}")
    print(f"[{step}]")
    print(f"{'='*60}")
    # shell=True 必要：命令为硬编码字符串，含 shell 语法（管道/重定向），无外部输入，无注入风险
    result = subprocess.run(cmd, shell=True)  # nosec B602
    ok = result.returncode == 0
    status = "[PASS]" if ok else "[FAIL]"
    print(f"  -> {status}")
    if not ok:
        print(f"  [!] 关键步骤失败，停止后续检查")
    return ok


def main():
    quick = "--quick" in sys.argv

    print("=" * 60)
    print("  NetOps 提交前自动化检查流水线")
    print("=" * 60)

    steps = []

    # 1. 语法检查（全量核心源文件）
    py_files = [
        "main.py",
        "src/ui/main_window.py",
        "src/ui/ops_toolbox_page.py",
        "src/ui/single_device_page.py",
        "src/ui/ai_analysis_page.py",
        "src/ui/project_manager_page.py",
        "src/ui/system_settings_page.py",
        "src/core/config_generator.py",
        "src/core/crypto_utils.py",
        "src/core/device_manager.py",
        "src/core/key_manager.py",
        "src/core/local_audit_engine.py",
        "src/core/local_diagnostic_engine.py",
        "src/core/secure_config.py",
        "src/core/logger.py",
        "src/utils/resource_path.py",
        "src/utils/file_operators.py",
        "src/utils/validators.py",
    ]
    for f in py_files:
        steps.append(("语法检查", f"python -m py_compile {f}"))

    # 2. 导入链验证（全量核心模块）
    imports = [
        "from src.ui.main_window import MainWindow",
        "from src.core.config_generator import ConfigGenerator",
        "from src.core.crypto_utils import encrypt_password, decrypt_password",
        "from src.core.device_manager import DeviceManager",
        "from src.core.key_manager import KeyManager, EncryptedDataManager",
        "from src.core.local_audit_engine import LocalAuditEngine",
        "from src.core.local_diagnostic_engine import LocalDiagnosticEngine",
        "from src.core.secure_config import SecureConfigFile",
        "from src.core.logger import netops_logger",
        "from src.utils.file_operators import AtomicFileWriter, JSONFileManager, DeviceFileManager",
        "from src.utils.validators import DeviceValidator, ProjectValidator, IPValidator",
    ]
    for imp in imports:
        steps.append(("导入链验证", f'python -c "{imp}; print(\'OK\')"'))

    # 3. 类型检查（全量核心模块）
    steps.append(("类型检查",
                  "py -3.11 -m mypy src/core/ src/utils/"))

    # 4. 单元测试 + 覆盖率
    #    覆盖率统计范围：核心业务逻辑模块（排除UI模板生成器和PyInstaller运行时检测）
    #    阈值 80%：可测试业务逻辑代码的最低覆盖率要求
    #    排除项：
    #       - config_generator.py：四厂商配置模板生成器（纯模板代码，已通过集成测试验证）
    #       - resource_path.py：PyInstaller运行时路径检测（依赖打包环境）
    steps.append(("单元测试", "py -3.11 -m pytest tests/ -v --tb=short "
                  "--cov=src/core "
                  "--cov=src/utils "
                  "--cov-report=term-missing "
                  "--cov-fail-under=80"))

    # 5. 安全扫描
    steps.append(("安全扫描", "py -3.11 -m bandit -r src/ -c bandit.yaml -ll"))

    # 6. 代码复杂度（完整模式）
    if not quick:
        steps.append(("复杂度检查", "py -3.11 -m radon cc src/ -a -nc"))

    # 执行
    passed = 0
    failed = 0
    total = len(steps)

    for i, (name, cmd) in enumerate(steps, 1):
        label = f"{i}/{total} {name}"
        ok = run(label, cmd)
        if ok:
            passed += 1
        else:
            failed += 1
            break

    # 汇总
    print(f"\n{'='*60}")
    print(f"  检查完成：{passed}/{total} 通过，{failed} 失败")
    print(f"{'='*60}")

    if failed > 0:
        print("  [FAIL] 存在失败项，请修复后再提交")
        sys.exit(1)
    else:
        print("  [PASS] 全部通过，可以提交")
        sys.exit(0)


if __name__ == "__main__":
    main()
