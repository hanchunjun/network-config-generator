# 工程化规范全流程（V0.4.1）

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

## 六、版本号管理规范（V0.4.1 教训）

**每次版本升级，必须全量检查以下所有位置的版本号，确保一致：**

### 必须同步的位置

| # | 文件 | 位置 | 示例 |
|---|------|------|------|
| 1 | `CLAUDE.md` | 第 1 行标题 | `# NetOps V0.4.1 — 项目总纲` |
| 2 | `main.py` | 文件头注释 | `V0.4.1 Logo设计 + 安装包` |
| 3 | `src/ui/main_window.py` | 窗口标题（3处） | `'NetOps 企业网络自动化运维平台 V0.4.1'` |
| 4 | `src/ui/main_window.py` | 关于对话框版本号 | `version_str = 'V0.4.1' + (' 试用版' if ...)` |
| 5 | `src/ui/admin_tool_window.py` | 窗口标题 | `"NetOps 管理员制码工具 V0.4.1 — 老韩专用"` |
| 6 | `DESIGN.md` | 标题 + 维护信息 | `V0.4.1` / `2026-05-30` |
| 7 | `.claude/rules/05-dev-build-rule.md` | 标题 | `V0.4.1` |
| 8 | `.claude/rules/10-version-history.md` | 标题 + 新增条目 | `V0.4.1 Logo 设计版` |
| 9 | `.claude/rules/03-module-spec.md` | 标题 | `V0.4.1` |
| 10 | `.claude/rules/04-user-workflow.md` | 标题 | `V0.4.1` |
| 11 | `.claude/rules/06-safety-rule.md` | 标题 + 底部版本信息 | `V0.4.1` |
| 12 | `.claude/rules/01-architecture-dir.md` | 标题 | `V0.4.1` |
| 13 | `.claude/rules/08-activation-plan.md` | 标题 | `V0.4.1` |
| 14 | `.claude/rules/09-engineering-workflow.md` | 标题 | `V0.4.1` |
| 15 | `.claude/rules/11-user-guide.md` | 标题 | `V0.4.1` |
| 16 | `.claude/rules/12-qss-theme-signal-spec.md` | 标题 + 底部版本 | `V0.4.1` |
| 17 | `.claude/rules/07-v2-architecture-plan.md` | 状态注释 | `V0.4.1` |
| 18 | `docs/CODEMAPS/INDEX.md` | 版本 + 日期 | `V0.4.1` / `2026-05-30` |
| 19 | `docs/CODEMAPS/build-deploy.md` | 版本 + 日期 + 版本表 | `V0.4.1` |
| 20 | `docs/CODEMAPS/architecture.md` | 版本 + 日期 | `V0.4.1` |
| 21 | `docs/CODEMAPS/ui-pages.md` | 版本 + 日期 | `V0.4.1` |
| 22 | `docs/CODEMAPS/core-engines.md` | 版本 + 日期 | `V0.4.1` |
| 23 | `docs/CODEMAPS/data-flow.md` | 版本 + 日期 | `V0.4.1` |
| 24 | `docs/CODEMAPS/ai-agents.md` | 版本 + 日期 | `V0.4.1` |
| 25 | `docs/CODEMAPS/utils.md` | 版本 + 日期 | `V0.4.1` |
| 26 | `installer/build_setup.py` | 版本号 + 输出文件名 | `V0.4.1` / `NetOps_Setup_0.4.1.exe` |
| 27 | `installer/NetOps_Setup.iss` | `AppVersion` + `OutputBaseFilename` | `0.4.1` |
| 28 | `~/.claude/projects/.../memory/project.md` | 版本字段 | `V0.4.1` |

### 检查命令

```bash
# 快速扫描所有硬编码版本号
grep -rn "V0\.[0-9]\+\.[0-9]\+\|版本.*V0\.\|version.*0\." \
  CLAUDE.md main.py src/ui/main_window.py src/ui/admin_tool_window.py \
  DESIGN.md .claude/rules/ docs/CODEMAPS/ installer/ \
  --include="*.md" --include="*.py" --include="*.iss"
```

### 教训

> V0.4.1 发布时，因版本号未全量同步，导致安装包内关于对话框仍显示 V0.3.0，
> 窗口标题也未更新。事后不得不单独提交修复。
> **版本升级必须一次性同步所有位置，不得遗漏。**

## 七、版本记录

- 每次重大改动在 `CHANGELOG.md` 对应版本下追加条目
- 格式遵循 Keep a Changelog（Added/Fixed/Changed/Security）

## 八、改动后自动流程（每次代码修改后必须执行，无需用户提醒）

每次完成代码修改后，按顺序自动执行以下步骤：

### 1. 代码审查
- 检查修改文件是否有语法错误、逻辑错误
- 检查是否有死代码、未使用的导入
- 检查是否符合 DESIGN.md 规范

### 2. 测试
- 运行 `python -m py_compile <修改文件>` 确认语法正确
- 运行 `python -m pytest tests/ -v` 确认测试通过

### 3. 打包
- 清理 `build/` 目录
- 运行 `pyinstaller NetworkConfigGenerator.spec --noconfirm`
- 运行 `python installer/build_setup.py`
- 验证 `dist/NetOps/` 和 `installer/NetOps_Setup_0.4.0.exe` 生成成功

### 4. 更新相关文件
- 检查 CLAUDE.md、DESIGN.md、rules/ 是否需要同步更新
- 检查版本号是否需要更新（遵循第六章规范）
- 检查 codemap 是否需要更新

### 5. Git 提交
- 使用 conventional commits 格式
- 详细描述修改内容
- 不遗漏任何修改文件

### 教训

> V0.4.1 多次出现"改了代码忘了打包"、"改了规范忘了更新代码"、"版本号漏更新"等问题。
> **每次改动后必须自动走完整个流程，不需要用户提醒。**
