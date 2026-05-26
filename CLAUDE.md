# 政企网络自动化运维一体化EXE工具 项目总纲

## 项目开发遵循规则

1. 默认全局遵循：`C:\Users\Administrator\.claude\CLAUDE.md` 通用底层规范。
2. 本项目代码开发，强制遵循：[.claude/rules/00-karpathy-guidelines.md](.claude/rules/00-karpathy-guidelines.md) 官方编码准则。
3. 工程化规范：强制遵循 [.claude/rules/09-engineering-workflow.md](.claude/rules/09-engineering-workflow.md)，每次改动和打包必须按流程执行。
4. **界面设计规范**：所有界面代码的生成与修改，必须以项目根目录的 [DESIGN.md](DESIGN.md) 为唯一标准，禁止任何脱离规范的主观发挥。包括但不限于：色彩、字体、按钮样式、输入框样式、表格样式、间距、圆角、交互状态，均须严格对照 DESIGN.md 执行。

## 项目概述

基于 PyQt5 网络设备配置生成器深度扩建的政企级全流程闭环网络自动化运维桌面工具。以四厂商配置脚本生成为基础，叠加多项目标准化管理、全网批量自动化运维、单点设备专项排查、AI智能故障诊断、配置合规审计五大核心能力；兼容锐捷、华为、H3C、思科全系列网络设备，采用公共脚本复用+多项目物理隔离架构，**免环境安装、双击直跑、整体拷贝即用**。

**项目状态：V0.3.6 主题增强版（2026年5月26日）· 持续迭代中**

## 基础技术栈

- 开发语言：Python 3.11 · 界面框架：PyQt5 · 设计模式：面向对象 + 工厂模式 + 单例模式
- 加密算法：AES-GCM (V0.2版本) · 打包部署：PyInstaller 单EXE封装（48.6MB）
- AI能力：三层架构（嵌入式按钮 → Agent快捷指令 → 自由对话）+ 双层分析（本地预检 + AI精审）

## 顶部固定主菜单（V0.3.5）

快捷键：`Ctrl+1` ~ `Ctrl+7` 切换对应页面

| # | 菜单 | 定位 | 核心能力 |
|---|------|------|---------|
| 1 | 📁 新建项目 | 项目总览 | 多项目CRUD + 卡片总览 + 全局统计 |
| 2 | 🔧 项目运维 | 批量任务中心 | 批量备份/全网巡检/故障核查 + 4Tab + AI合规/诊断 |
| 3 | 🔍 单点运维 | 单设备全链条 | 5Tab：巡检/备份/报告/诊断/审计 + 三件套 |
| 4 | 🤖 专家工作站 | 深度AI分析 | 3Tab + Agent快捷指令 + 多文件输入 |
| 5 | 🖥 设备配置 | 配置生成器 | 四厂商四设备类型可视化配置脚本生成 |
| 6 | 📜 命令生成 | 批量脚本工具 | 命令模板 + %a~%e参数 + 互斥双模式 + 预置模板 |
| 7 | ⚙ 模型设置 | AI配置管理 | 多模型管理/加密存储/连通性测试 |

## AI能力三层架构

```
第一层：嵌入式AI按钮（单点运维 / 项目运维 — 自动绑定上下文，一键执行）
第二层：Agent快捷指令（专家工作站 — 手动选文件 → 加载Agent → 可编辑Prompt → 发送）
第三层：自由对话（专家工作站 — 完全自定义Prompt + 多轮迭代）
```

详细能力矩阵与Agent文件说明见 [.claude/rules/03-module-spec.md](.claude/rules/03-module-spec.md)。

## 便携化架构

**所有数据跟随EXE，整体拷贝即用。** 详细路径管理API、目录结构、部署方式、五区分离设计见 [.claude/rules/01-architecture-dir.md](.claude/rules/01-architecture-dir.md)。

核心API：`get_app_dir()` / `get_config_dir()` / `get_activation_dir()` / `get_admin_data_dir()` / `get_single_dir()` / `get_config_path()` / `ensure_dirs()`

## 关键技术约束

0. **试用模式**：未激活用户可进入主窗口，仅开放「锐捷接入交换机配置」和「命令生成」功能，其他导航项弹出激活提示（联系老韩 QQ:223518 / WeChat:tachlaohan）
1. **DPI缩放适配**：`main.py` 调用 `SetProcessDpiAwareness(0)` + `app.manifest` 声明 `dpiAwareness:unaware`，三层控制确保 100%/125%/150% 布局稳定
2. **QThread必须保存为实例变量**：`self._xxx_thread = thread`，否则GC回收导致崩溃
3. **AI配置获取用 `get_active_ai_config()`**：不要直接读文件或 `SecureConfigFile`
4. **所有路径跟随EXE**：用 `get_app_dir()` / `get_config_path()` / `ensure_dirs()`
5. **Agent文件用相对路径读取**：基于 `get_app_dir()` 定位 `agents/` 目录
6. **文件操作前确认对话框**：删除/导出等危险操作需确认
7. **原子文件操作**：防止数据损坏
8. **操作日志**：所有关键操作写入 `logs/netops_YYYYMMDD.log`
9. **登录认证**：程序启动在激活校验通过后执行登录认证，登录成功才加载主窗口；账户数据存储于 `config/account.json`（用户名明文+密码AES-GCM密文）
10. **主题引擎**：所有UI页面初始化时捕获 `ThemeEngine.get().current_theme`，连接 `theme_changed` 信号动态刷新样式；新增UI组件必须使用 `t['xxx']` 动态颜色，禁止硬编码色值

## 关键源码文件速查

| 模块 | 文件 | 职责 |
|------|------|------|
| 激活体系 | [src/core/activation_engine.py](src/core/activation_engine.py) | 激活引擎（机器码/激活码/授权存储/黑名单校验） |
| 管理员制码 | [src/core/admin_keygen.py](src/core/admin_keygen.py) | 制码核心（加密台账/备份恢复/黑名单管理） |
| 登录认证 | [src/core/account_manager.py](src/core/account_manager.py) | 账户管理（读写/校验/加密/复杂度校验） |
| 激活弹窗 | [src/ui/activation_dialog.py](src/ui/activation_dialog.py) | 用户端激活弹窗UI |
| 管理员工具 | [src/ui/admin_tool_window.py](src/ui/admin_tool_window.py) | 管理员制码工具UI |
| 登录弹窗 | [src/ui/login_dialog.py](src/ui/login_dialog.py) | 登录弹窗（无关闭按钮/禁止ESC） |
| 账户管理弹窗 | [src/ui/account_manager_dialog.py](src/ui/account_manager_dialog.py) | 账户管理弹窗 |
| 路径管理 | [src/utils/resource_path.py](src/utils/resource_path.py) | get_app_dir / get_single_dir / get_config_path / ensure_dirs |
| 密钥管理 | [src/core/key_manager.py](src/core/key_manager.py) | AES-GCM 密钥管理（V0.2版本） |
| 加密配置 | [src/core/secure_config.py](src/core/secure_config.py) | 加密配置文件读写（单例） |
| 日志系统 | [src/core/logger.py](src/core/logger.py) | 日志系统（EXE同级logs/） |
| 本地审计引擎 | [src/core/local_audit_engine.py](src/core/local_audit_engine.py) | 本地合规规则引擎（双层审计预检层） |
| 本地诊断引擎 | [src/core/local_diagnostic_engine.py](src/core/local_diagnostic_engine.py) | 本地运行时诊断引擎（异常提取 + 精准上下文） |
| 主窗口 | [src/ui/main_window.py](src/ui/main_window.py) | 主窗口 + 导航栏 + 页面切换 |
| 新建项目页 | [src/ui/project_manager_page.py](src/ui/project_manager_page.py) | 项目CRUD + 卡片总览 + 状态灯 + 全局统计 |
| 项目运维页 | [src/ui/ops_toolbox_page.py](src/ui/ops_toolbox_page.py) | 3任务卡片 + 4Tab文件管理 + AI合规/诊断 |
| 单点运维页 | [src/ui/single_device_page.py](src/ui/single_device_page.py) | 5Tab全链条 + 测试连接 + 文件三件套 |
| 专家工作站 | [src/ui/ai_analysis_page.py](src/ui/ai_analysis_page.py) | 3Tab + Agent快捷指令 + 可编辑Prompt + 多文件 |
| 命令生成页 | [src/ui/batch_cmd_generator_page.py](src/ui/batch_cmd_generator_page.py) | 命令模板 + %a~%e参数 + 批量生成 |
| 模型设置页 | [src/ui/system_settings_page.py](src/ui/system_settings_page.py) | AI模型多配置管理 + 加密存储 + 自动匹配 |
| 巡检脚本 | [scripts/network_inspect.py](scripts/network_inspect.py) | 巡检引擎 + 设备类型映射 |
| 备份脚本 | [scripts/backup_all_config.py](scripts/backup_all_config.py) | 批量/单点配置备份 |
| 故障核查脚本 | [scripts/run_trouble_cmd.py](scripts/run_trouble_cmd.py) | 故障设备二次核查 |
| 合规审计Agent | [agents/network-config-reviewer.md](agents/network-config-reviewer.md) | 配置合规审计系统提示词 |
| 故障诊断Agent | [agents/network-troubleshooter.md](agents/network-troubleshooter.md) | OSI分层故障诊断系统提示词 |
| 打包辅助 | [app.manifest](app.manifest) | DPI清单（dpiAwareness:unaware） + [NetworkConfigGenerator.spec](NetworkConfigGenerator.spec) |
| 主题引擎 | [src/core/theme_engine.py](src/core/theme_engine.py) | 三主题引擎（单例/信号/60+色彩/QSS生成/配置持久化） |
| 主题切换页 | [src/ui/theme_switcher_page.py](src/ui/theme_switcher_page.py) | 主题切换面板（预览卡片/QPainter绘制/即时切换） |

## 项目交付物

| EXE | 位置 | 大小 | 用途 |
|-----|------|------|------|
| 用户端主程序 | `dist/NetOps.exe` | 48.7MB | 用户日常使用，含激活校验+登录认证+三主题+标题栏深色模式 |
| 管理员制码工具 | `dist/AdminKeyGenTool.exe` | 41.3MB | 管理员专用，生成激活码/管理黑名单 |

> **重要：** 两个EXE独立打包、独立运行。管理员制码工具严禁外发给用户。

## 规则文件索引

| 文件 | 内容 |
|------|------|
| [.claude/rules/00-karpathy-guidelines.md](.claude/rules/00-karpathy-guidelines.md) | 十二项专业行为规则套装 |
| [.claude/rules/01-architecture-dir.md](.claude/rules/01-architecture-dir.md) | 整体架构 + 全量目录结构 + 便携化路径API |
| [.claude/rules/02-original-asset.md](.claude/rules/02-original-asset.md) | 原有源码资产、目录、开发打包指令与扩展规范 |
| [.claude/rules/03-module-spec.md](.claude/rules/03-module-spec.md) | 七大菜单模块极致细化功能说明 + AI能力矩阵 |
| [.claude/rules/04-user-workflow.md](.claude/rules/04-user-workflow.md) | 全流程用户操作步骤 + 命令生成器使用步骤 |
| [.claude/rules/05-dev-build-rule.md](.claude/rules/05-dev-build-rule.md) | 开发实施步骤 + 打包发布规范 |
| [.claude/rules/06-safety-rule.md](.claude/rules/06-safety-rule.md) | 安全执行铁律 + 成品核心能力总结 |
| [.claude/rules/07-v2-architecture-plan.md](.claude/rules/07-v2-architecture-plan.md) | V0.2架构升级方案 `[归档]` |
| [.claude/rules/08-activation-plan.md](.claude/rules/08-activation-plan.md) | 软件激活三套方案完整技术规范（V0.3.0） |
| [.claude/rules/09-engineering-workflow.md](.claude/rules/09-engineering-workflow.md) | 工程化规范全流程（编码/提交/打包/复杂度/依赖） |
| [.claude/rules/10-version-history.md](.claude/rules/10-version-history.md) | 版本更新历史（V0.0.9 ~ V0.3.5） |
| [.claude/rules/11-user-guide.md](.claude/rules/11-user-guide.md) | 使用建议 & 故障排查 |
| [.claude/rules/12-qss-theme-signal-spec.md](.claude/rules/12-qss-theme-signal-spec.md) | QSS主题系统 + 信号联动开发规范（V0.3.5教训） |

## 代码地图索引

`docs/CODEMAPS/` — 快速定位代码，按需查阅：

| 文件 | 定位 |
|------|------|
| [INDEX.md](docs/CODEMAPS/INDEX.md) | 总索引 + 快速导航 |
| [architecture.md](docs/CODEMAPS/architecture.md) | 模块依赖 + 关键路径 |
| [ui-pages.md](docs/CODEMAPS/ui-pages.md) | 7大UI页面 + 16个配置页 |
| [core-engines.md](docs/CODEMAPS/core-engines.md) | AI双引擎 + 安全加密 |
| [utils.md](docs/CODEMAPS/utils.md) | 路径/验证器/文件操作 |
| [ai-agents.md](docs/CODEMAPS/ai-agents.md) | Agent调用链 + 双层分析流程 |
| [data-flow.md](docs/CODEMAPS/data-flow.md) | 数据流转 + 加密存储 |
| [build-deploy.md](docs/CODEMAPS/build-deploy.md) | 开发命令 + 打包规范 |
| [review-checklist.md](docs/CODEMAPS/review-checklist.md) | 提交/打包审查清单 |
| [complexity-baseline.md](docs/CODEMAPS/complexity-baseline.md) | 复杂度基线 |

## 相关文档

- **使用说明书：** [使用说明书.md](使用说明书.md)
- **版本记录：** [CHANGELOG.md](CHANGELOG.md)
- **技术支持：** `.claude/rules/` 目录下对应领域文档 · 测试用例 `tests/` · 运行日志 `logs/netops_YYYYMMDD.log` · 关键入口 `main.py` → `src/ui/main_window.py`
