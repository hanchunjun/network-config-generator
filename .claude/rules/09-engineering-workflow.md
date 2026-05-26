# 工程化规范全流程（V0.3.5）

> 本文件收纳 CLAUDE.md 工程化规范章节，每次改动和打包必须按流程执行。

## 一、编码规范

- **类型注解**：所有函数签名必须有类型注解，`mypy` 检查无错误
- **便携化路径**：必须用 `get_app_dir()` / `get_config_path()`，禁止硬编码绝对路径
- **安全红线**：自动化仅允许 show/display/ping/traceroute 只读指令，不自动修改设备配置
- **QThread**：必须保存为实例变量（`self._xxx_thread = thread`）
- **日志**：使用 `netops_logger`，禁止 `print()` 调试
- **原子操作**：文件写入用 `.tmp` + `os.replace`
- **外部输入**：IP/设备/项目数据必须经过 `validators` 校验
- **命令执行**：用 `subprocess.run()` 参数列表，禁止 `os.popen()` 拼接字符串

## 二、提交前自检（每次改动必做，1-2分钟）

**方式一：自动化脚本（推荐，约15秒）**

```bash
python scripts/pre_commit_check.py --quick
```

**方式二：手动分步**

```bash
# 1. 语法检查（改动的文件）
python -m py_compile <改动文件>

# 2. 类型检查
py -3.11 -m mypy src/utils/ src/core/key_manager.py src/core/secure_config.py src/core/logger.py

# 3. 单元测试 + 覆盖率（全部通过，核心模块≥80%）
py -3.11 -m pytest tests/ -v --cov=src/core --cov=src/utils --cov-report=term-missing --cov-fail-under=80

# 4. 安全扫描（无新增 High/Medium）
py -3.11 -m bandit -r src/ -c bandit.yaml -ll
```

详细清单见：[docs/CODEMAPS/review-checklist.md](docs/CODEMAPS/review-checklist.md)

## 三、打包前验证（发布版本必做，按顺序执行，任一失败停止）

**方式一：自动化脚本（推荐）**

```bash
# 完整检查（17项，含radon复杂度）
python scripts/pre_commit_check.py
```

**方式二：手动分步（调试时使用）**

```bash
# 1. 全量语法检查
python -m py_compile main.py
python -m py_compile src/ui/main_window.py
python -m py_compile src/ui/ops_toolbox_page.py
python -m py_compile src/ui/single_device_page.py
python -m py_compile src/ui/ai_analysis_page.py
python -m py_compile src/ui/project_manager_page.py
python -m py_compile src/ui/system_settings_page.py
python -m py_compile src/core/local_audit_engine.py
python -m py_compile src/core/local_diagnostic_engine.py
python -m py_compile src/utils/resource_path.py

# 2. 导入链验证
python -c "from src.ui.main_window import MainWindow; print('OK')"
python -c "from src.core.local_audit_engine import LocalAuditEngine; print('OK')"
python -c "from src.core.local_diagnostic_engine import LocalDiagnosticEngine; print('OK')"

# 3. 类型检查
py -3.11 -m mypy src/utils/ src/core/key_manager.py src/core/secure_config.py src/core/logger.py

# 4. 单元测试 + 覆盖率（核心模块≥80%）
py -3.11 -m pytest tests/ -v --cov=src/core --cov=src/utils --cov-report=term-missing --cov-fail-under=80

# 5. 安全扫描
py -3.11 -m bandit -r src/ -c bandit.yaml -ll

# 6. 代码复杂度（新增方法不超过C级）
py -3.11 -m radon cc src/ -a -nc

# 7. 打包
del dist\NetworkConfigGenerator.exe
pyinstaller NetworkConfigGenerator.spec --noconfirm
```

## 四、复杂度监控基线

- 当前平均复杂度：**D级 (26.63)**
- 新增方法圈复杂度不得超过 **C级 (10)**
- 基线文件：[docs/CODEMAPS/complexity-baseline.md](docs/CODEMAPS/complexity-baseline.md)

## 五、依赖管理

- 运行时依赖：`requirements.txt`（21行直接依赖，版本锁定）
- 开发工具依赖：`requirements-dev.txt`（pytest/mypy/bandit/radon）
- 新增依赖后必须更新对应文件

## 六、版本记录

- 每次重大改动在 `CHANGELOG.md` 对应版本下追加条目
- 格式遵循 Keep a Changelog（Added/Fixed/Changed/Security）
