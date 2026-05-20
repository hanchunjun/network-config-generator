# 代码审查自检清单

> 每次提交前必须逐项确认，打包前必须全部通过。

---

## 一、提交前自检（每次改动必做）

### 基础检查
- [ ] 全量语法检查通过（`py_compile` 所有改动的文件）
- [ ] 导入链验证通过（`from src.xxx import Xxx` 无报错）
- [ ] 类型检查通过（`mypy` 无新增错误）
- [ ] 单元测试通过（`pytest tests/ -v` 全部绿色）
- [ ] 安全扫描通过（`bandit` 无新增 High/Medium）

### 代码质量
- [ ] 无新增绝对硬编码路径（必须用 `get_app_dir()` / `get_config_path()`）
- [ ] 无硬编码密钥/密码/令牌
- [ ] QThread保存为实例变量（`self._xxx_thread = thread`）
- [ ] 无 `print()` 调试语句（使用 `netops_logger`）
- [ ] 危险操作有确认对话框（删除/导出/查看密码）
- [ ] 文件操作使用原子操作（写 `.tmp` 再 `os.replace`）
- [ ] 新增函数有docstring和类型注解

### 安全红线
- [ ] 自动化仅允许 show/display/ping/traceroute 只读指令
- [ ] 不自动修改设备配置（接口启停/路由变更/设备重启/配置保存）
- [ ] 外部输入经过验证（IP格式、设备数据、项目名称）
- [ ] 命令参数使用列表传递，不拼接shell字符串

---

## 二、打包前验证（发布版本必做）

按顺序执行，任一失败停止：

```bash
# 1. 语法检查
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

# 4. 单元测试
py -3.11 -m pytest tests/ -v

# 5. 安全扫描
py -3.11 -m bandit -r src/ -c bandit.yaml -ll

# 6. 打包
del dist\NetworkConfigGenerator.exe
pyinstaller NetworkConfigGenerator.spec --noconfirm
```

---

## 三、新功能开发流程

```
研究与重用 → 规划(TDD) → 编码 → 代码审查 → 打包验证 → 发布
     ↓           ↓                    ↓
  GitHub搜索   planner代理       review-checklist
  库文档       tdd-guide代理      全部通过才打包
```

---

## 四、严重级别判定

| 级别 | 含义 | 处理 |
|------|------|------|
| CRITICAL | 安全漏洞/数据丢失/程序崩溃 | **阻止** — 必须修复 |
| HIGH | Bug或重大质量问题 | **警告** — 应修复 |
| MEDIUM | 可维护性问题 | **信息** — 考虑修复 |
| LOW | 风格或次要建议 | **注意** — 可选 |
