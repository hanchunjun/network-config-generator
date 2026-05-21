# 政企网络自动化运维一体化EXE工具 项目总纲

## 项目开发遵循规则

1. 默认全局遵循：C:\Users\Administrator.claude\CLAUDE.md 通用底层规范。
2. 本项目代码开发，强制遵循：.claude/rules/00-karpathy-guidelines.md 官方编码准则。
3. 工程化规范：强制遵循下方「工程化规范全流程」，每次改动和打包必须按流程执行。

---

## ⭐ 工程化规范全流程（每次改动/打包必做）

### 一、编码规范

- **类型注解**：所有函数签名必须有类型注解，`mypy` 检查无错误
- **便携化路径**：必须用 `get_app_dir()` / `get_config_path()`，禁止硬编码绝对路径
- **安全红线**：自动化仅允许 show/display/ping/traceroute 只读指令，不自动修改设备配置
- **QThread**：必须保存为实例变量（`self._xxx_thread = thread`）
- **日志**：使用 `netops_logger`，禁止 `print()` 调试
- **原子操作**：文件写入用 `.tmp` + `os.replace`
- **外部输入**：IP/设备/项目数据必须经过 `validators` 校验
- **命令执行**：用 `subprocess.run()` 参数列表，禁止 `os.popen()` 拼接字符串

### 二、提交前自检（每次改动必做，1-2分钟）

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

### 三、打包前验证（发布版本必做，按顺序执行，任一失败停止）

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

### 四、复杂度监控基线

- 当前平均复杂度：**D级 (26.63)**
- 新增方法圈复杂度不得超过 **C级 (10)**
- 基线文件：[docs/CODEMAPS/complexity-baseline.md](docs/CODEMAPS/complexity-baseline.md)

### 五、依赖管理

- 运行时依赖：`requirements.txt`（21行直接依赖，版本锁定）
- 开发工具依赖：`requirements-dev.txt`（pytest/mypy/bandit/radon）
- 新增依赖后必须更新对应文件

### 六、版本记录

- 每次重大改动在 `CHANGELOG.md` 对应版本下追加条目
- 格式遵循 Keep a Changelog（Added/Fixed/Changed/Security）

---

## 项目概述

本项目基于原有PyQt5网络设备配置生成器深度扩建，打造政企级全流程闭环网络自动化运维桌面工具。以原有四厂商配置脚本生成为基础，叠加多项目标准化管理、全网批量自动化运维、单点设备专项排查、AI智能故障诊断、配置合规审计五大核心能力；兼容锐捷、华为、H3C、思科全系列网络设备，采用公共脚本复用+多项目物理隔离架构，**免环境安装、双击直跑、整体拷贝即用**，适配政企电子政务、高校校园网、企业园区网开局建站、日常运维、故障排查、等保合规全场景。

**项目状态：V0.3.1 试用模式版已完成（2026年5月21日）· 持续迭代中**

## 基础技术栈

- 开发语言：Python 3.11
- 界面框架：PyQt5
- 设计模式：面向对象 + 工厂模式 + 单例模式
- 加密算法：AES-GCM (V0.2版本)
- 打包部署：PyInstaller 单EXE封装（约47.1MB）
- AI能力：三层架构（嵌入式按钮 → Agent快捷指令 → 自由对话）+ 双层分析（本地预检 + AI精审）

## 顶部固定主菜单（V0.2）

```
📁 新建项目   →   🔧 项目运维   →   🔍 单点运维   →   🤖 专家工作站   →   🖥 设备配置   →   ⚙ 模型设置
   建               管                修                研                配              设
```

| # | 菜单 | 定位 | 核心能力 |
|---|------|------|---------|
| 1 | 📁 新建项目 | 项目总览 | 多项目CRUD + 卡片总览（设备数/备份时间/巡检状态）+ 全局统计 |
| 2 | 🔧 项目运维 | 批量任务中心 | 批量备份/全网巡检/故障核查 + 4Tab文件管理 + AI合规巡检/故障诊断 |
| 3 | 🔍 单点运维 | 单设备全链条 | 5Tab：巡检日志/配置备份/巡检报告/🩺诊断报告/🔍合规审计 + 三件套 |
| 4 | 🤖 专家工作站 | 深度AI分析 | 3Tab：自由对话/合规审计/故障诊断 + Agent快捷指令 + 多文件输入 |
| 5 | 🖥 设备配置 | 配置生成器 | 四厂商四设备类型可视化配置脚本生成 |
| 6 | ⚙ 模型设置 | AI配置管理 | 多模型管理/加密存储/连通性测试/切换自动生效 |

---

## ⭐ AI能力三层架构（核心创新）

```
第一层：嵌入式AI按钮（单点运维 / 项目运维 — 自动绑定上下文，一键执行）
第二层：Agent快捷指令（专家工作站 — 手动选文件 → 加载Agent → 可编辑Prompt → 发送）
第三层：自由对话（专家工作站 — 完全自定义Prompt + 多轮迭代）
```

### AI能力归属矩阵

| 能力 | 单点运维 | 项目运维 | 专家工作站 |
|------|:---:|:---:|:---:|
| 🔍 一键合规巡检（单文件/自动） | ✅ 嵌入按钮 | ✅ 嵌入按钮 | — |
| 🔍 一键合规巡检（多文件/手动） | — | — | ✅ Agent按钮 |
| 🩺 一键故障诊断（单文件/自动） | ✅ 嵌入按钮 | ✅ 嵌入按钮 | — |
| 🩺 一键故障诊断（多文件/手动） | — | — | ✅ Agent按钮 |
| 🩺 AI精审（双层审计） | ✅ 合规审计Tab | ✅ 合规审计Tab | ✅ Agent按钮 |
| 💬 自由对话/多轮迭代 | — | — | ✅ 专属 |
| 📝 自定义提示词模板 | — | — | ✅ 专属 |

### Agent文件

| 文件 | 用途 | 调用方 |
|------|------|--------|
| [agents/network-config-reviewer.md](agents/network-config-reviewer.md) | 合规审计系统提示词 | 所有AI合规巡检按钮 |
| [agents/network-troubleshooter.md](agents/network-troubleshooter.md) | OSI分层故障诊断提示词 | 所有AI故障诊断按钮 |

---

## ⭐ 文件管理统一标准

所有文件列表统一使用三件套按钮，放置于列表上方：

```
[🔄 刷新列表]  [📂 打开文件]  [🗑 删除文件]
```

适用位置：单点运维5个Tab、项目运维4个Tab、专家工作站历史报告区。

---

## ⭐ 便携化架构（核心设计）

### 设计原则

**所有数据跟随EXE，整体拷贝即用。** 不依赖固定路径，不依赖环境变量，不依赖注册表。

### 路径管理API

| 函数 | 用途 | 示例 |
|------|------|------|
| `get_app_dir()` | EXE所在目录根路径 | `D:\工具\` |
| `get_config_dir()` | 系统配置子目录 | `D:\工具\config\` |
| `get_activation_dir()` | 用户端激活体系子目录 | `D:\工具\activation\` |
| `get_admin_data_dir()` | 管理员数据子目录 | `D:\工具\admin_data\` |
| `get_single_dir()` | 单点运维数据子目录 | `D:\工具\single\` |
| `get_config_path(filename)` | 相对于EXE根目录的路径 | `D:\工具\config\ai_config.json.enc` |
| `resource_path(relative)` | 打包内嵌资源（仅开发时） | `_MEIPASS/scripts/` |
| **禁止使用** | 绝对硬编码路径 | ❌ `C:\Network-Config\...` |

### 代码规范

```python
# ✅ 正确：使用 get_app_dir()
from src.utils.resource_path import get_app_dir, get_config_path, get_single_dir

PROJECTS_DIR = os.path.join(get_app_dir(), "projects")
SINGLE_DIR = get_single_dir()
AI_CONFIG_PATH = get_config_path("config/ai_config.json")
LOG_DIR = os.path.join(get_app_dir(), "logs")

# ❌ 错误：硬编码绝对路径
PROJECTS_DIR = r"C:\Network-Config\projects"
```

### 启动自动创建目录

程序启动时调用 `ensure_dirs()` 自动创建以下目录结构（同时自动迁移旧版散落文件）：

```
📂 EXE所在目录/
├── 📄 NetworkConfigGenerator.exe          ← 主程序（唯一顶层文件）
│
├── 📂 config/                             ← 🔧 系统配置
│   ├── key_info.json                      ← 加密密钥（AES-GCM V0.2）
│   ├── machine_id.json                    ← 机器绑定ID
│   ├── ai_config.json.enc                 ← AI模型配置（加密存储）
│   ├── projects_config.json               ← 项目列表索引
│   └── ai_recent_files.json               ← AI最近文件记录
│
├── 📂 activation/                         ← 🔐 用户端激活体系
│   ├── license.dat                        ← 激活授权文件（AES-GCM加密）
│   └── bl_check.dat                       ← 黑名单校验时间记录
│
├── 📂 admin_data/                         ← 🛡 管理员数据（独立隔离）
│   ├── records.dat                        ← 授权台账（AES-GCM加密）
│   ├── blacklist.txt                      ← 本地黑名单
│   └── backup/                            ← 台账备份目录
│       └── records_YYYYMMDD_HHMMSS.dat    ← 带时间戳的备份
│
├── 📂 logs/                               ← 📝 运行日志
│   ├── netops_YYYYMMDD.log                ← 按日期分割
│   └── backup_error.log                   ← 备份错误日志
│
├── 📂 single/                             ← 🔍 单点运维全量隔离
│   ├── 📄 single_devices.json.enc         ← 单点设备清单（加密）
│   ├── 📂 config_backup/                  ← 单点配置备份
│   ├── 📂 output/single_exception/        ← 单点巡检异常输出
│   └── 📂 report/
│       ├── single_inspect/                ← 单点巡检报告
│       ├── compliance/                    ← 单点AI合规审计
│       └── diagnosis/                     ← 单点AI诊断+精审
│
└── 📂 projects/                           ← 📁 项目数据
    └── 📂 01_项目名称/
        ├── 📂 config/device_list.txt      ← 设备清单
        ├── 📂 config_backup/              ← 项目配置备份
        ├── 📂 output/                     ← 批量运维输出
        │   ├── all_device_full.md         ← 全网巡检汇总报告
        │   ├── single_exception/          ← 巡检异常输出
        │   ├── trouble_check_result/      ← 故障核查结果
        │   └── manual_high_risk_task.txt  ← 高危操作人工清单
        └── 📂 report/                     ← 报告目录
            ├── single_inspect/            ← 项目巡检报告
            ├── compliance/                ← 项目AI合规审计
            └── diagnosis/                 ← 项目AI诊断+精审
```

> **三区分离设计**：系统配置(`config/`) + 单点数据(`single/`) + 项目数据(`projects/`) + 日志(`logs/`)，顶层仅保留1个EXE。

### 部署方式

```powershell
# 方式1：直接运行
dist\NetworkConfigGenerator.exe

# 方式2：拷贝到任意位置后运行
xcopy dist\ D:\网络工具\ /E /I /H
D:\网络工具\NetworkConfigGenerator.exe

# 方式3：U盘携带
# 整个文件夹复制到U盘，插上即用
```

---

## 目录规范说明

- 根目录：CLAUDE.md 项目总纲
- .claude/rules/：按领域拆分标准规则集
- docs/CODEMAPS/：代码地图（架构、模块、数据流、AI Agent、构建部署等索引）
- docs/archive/：归档旧版文档
- 所有业务细则、架构规范、编码规则、模块说明、流程规范、安全约束均收纳在 rules 独立文件中

## 代码地图索引

`docs/CODEMAPS/` — 快速定位代码，按需查阅：

| 文件 | 内容 | 适用场景 |
|------|------|---------|
| [INDEX.md](docs/CODEMAPS/INDEX.md) | 总索引 + 架构总览 + 快速导航 | 了解项目全貌 |
| [architecture.md](docs/CODEMAPS/architecture.md) | 三层架构 + 模块依赖关系 + 关键路径 | 理解代码分层和调用链 |
| [ui-pages.md](docs/CODEMAPS/ui-pages.md) | 6大UI页面 + 16个配置页面 + AI按钮 | 定位UI相关代码 |
| [core-engines.md](docs/CODEMAPS/core-engines.md) | AI双引擎 + 安全加密 + 设备管理 | 定位业务逻辑代码 |
| [utils.md](docs/CODEMAPS/utils.md) | 路径管理 + 验证器 + 文件操作 | 定位工具函数代码 |
| [ai-agents.md](docs/CODEMAPS/ai-agents.md) | Agent提示词 + AI三层架构 + 双层分析 | 定位AI相关代码 |
| [data-flow.md](docs/CODEMAPS/data-flow.md) | 三区分离 + 数据流转 + 加密存储 | 理解数据存储和流转 |
| [build-deploy.md](docs/CODEMAPS/build-deploy.md) | 开发命令 + 打包规范 + 部署方式 | 构建和发布 |
| [review-checklist.md](docs/CODEMAPS/review-checklist.md) | 提交前自检 + 打包前验证 + 审查清单 | 代码审查和发布 |
| [complexity-baseline.md](docs/CODEMAPS/complexity-baseline.md) | 复杂度基线 + 高复杂度方法清单 + 监控规则 | 代码质量监控 |

## 规则文件索引

`.claude/rules/`

- 01-architecture-dir.md   整体架构 + 全量目录结构规范
- 02-original-asset.md     原有源码资产、目录、开发打包指令与扩展规范
- 03-module-spec.md       六大菜单模块极致细化功能说明
- 04-user-workflow.md      全流程用户操作步骤
- 05-dev-build-rule.md    开发实施步骤 + 打包发布规范
- 06-safety-rule.md       安全执行铁律 + 成品核心能力总结
- 07-v2-architecture-plan.md  V0.2架构升级方案（已实施完成）
- 08-activation-plan.md      软件激活三套方案完整技术规范（V0.3.0已完成）

---

## 核心优化成果

### 安全加固（9项改进）

- ✅ 密钥管理系统升级（V0.2版本，支持自动迁移）
- ✅ 加密工具增强（AES-GCM算法，多版本兼容）
- ✅ 输入验证器（IP、设备、项目验证）
- ✅ 安全确认对话框（导出、删除、查看密码）
- ✅ 命令注入防护（特殊字符过滤）
- ✅ 原子文件操作（防止数据损坏）
- ✅ 详细的日志记录（操作审计）
- ✅ 异常处理增强（细粒度错误处理）
- ✅ 资源释放保障（上下文管理器）

### 性能优化（4项改进）

- ✅ 配置缓存机制（LRU缓存，128条目）
- ✅ 批量VLAN生成（范围压缩优化）
- ✅ 字符串处理优化（join替代+=）
- ✅ 表格操作优化（减少UI访问）

### 代码质量（3项改进）

- ✅ 模块化重构（独立工具模块）
- ✅ 类型注解完善
- ✅ 文档和注释增强

### 测试框架

- ✅ **V0.2.1 测试体系已重建**：232 个单元测试用例，覆盖 `src/core/` 和 `src/utils/` 全部核心模块
- ✅ 核心模块覆盖率 **80.71%**（阈值 ≥80%，`.coveragerc` 排除 UI 模板和 PyInstaller 运行时检测）
- ✅ 自动化流水线：`scripts/pre_commit_check.py` 17 项质量门禁（语法/导入/类型/测试+覆盖率/安全/复杂度）
- ⚪ V0.0.9 时期测试用例（test_security.py 等，共 35 个用例）已随架构升级废弃，由新测试体系替代
- ⚪ UI 层集成测试和 E2E 测试待后续补充

### V0.3.0 激活体系（2026-05-21 新增）
- ✅ **三套激活方案**：方案A纯离线永久激活 / 方案B 180天黑名单可控激活 / 方案C管理员独立制码工具
- ✅ **机器码绑定**：CPU序列号+硬盘物理序列号→MD5→32位大写唯一机器码
- ✅ **激活码算法**：机器码+内置私钥→16位大写激活码，一机一码
- ✅ **启动激活校验**：未激活进入试用模式（仅开放锐捷接入交换机配置），激活后全功能开放
- ✅ **180天静默校验**：方案B后台联网校验云端黑名单，支持远程封禁/解绑
- ✅ **管理员制码工具**：独立EXE，唯一出码渠道，台账自动记录
- ✅ **有效期支持**：10档有效期（永久/5年/10年/3年/2年/1年/半年/季度/月度/周度）
- ✅ **剩余天数显示**：导航栏激活按钮实时显示剩余天数，颜色编码（绿/橙/红）
- ✅ **授权详情弹窗**：点击已激活按钮查看激活时间、到期时间、剩余天数

### V0.2.0 架构升级（2026-05-19 更新）

- ✅ 运维工具箱 → 重构为「项目运维」任务中心（3任务卡片 + 4Tab + AI嵌入）
- ✅ AI分析页 → 重定义为「专家工作站」（3Tab + Agent快捷指令 + 自由对话）
- ✅ 新建项目页 → 升级「项目总览」（卡片网格 + 状态灯 + 全局统计）
- ✅ 导航改名：「运维工具箱→项目运维」「单点巡检→单点运维」「AI分析→专家工作站」
- ✅ AI能力三层架构落地（嵌入式按钮 → Agent快捷指令 → 自由对话）
- ✅ 文件管理三件套统一标准（🔄刷新/📂打开/🗑删除）
- ✅ 全量40个源文件编译通过，14模块导入链验证通过

### 功能增强（2026-05-18 更新）

- ✅ AI模型多配置管理（新增/删除/重命名/切换）
- ✅ AI配置加密存储（SecureConfigFile + AES-GCM）
- ✅ 配置名称可编辑（QInputDialog 重命名）
- ✅ 切换配置实时状态显示（模型名/API地址）
- ✅ 单点设备"测试连接"按钮（Ping + SSH/Telnet 双验证）
- ✅ 单点设备备份修复（路径跟随EXE）
- ✅ 巡检设备类型映射修复（UI类型→命令库类型）
- ✅ 单点巡检报告保存（report/single_inspect/）
- ✅ 全面便携化改造（所有路径跟随EXE）

---

## 关键技术约束

0. **试用模式**：未激活用户可进入主窗口，仅开放「锐捷接入交换机配置」功能，其他导航项和配置选项弹出激活提示（联系老韩 QQ:223518 / WeChat:tachlaohan）；激活成功后全部功能开放
1. **QThread必须保存为实例变量**：`self._xxx_thread = thread`，否则GC回收导致崩溃
2. **AI配置获取用 `get_active_ai_config()`**：不要直接读文件或 `SecureConfigFile`
3. **所有路径跟随EXE**：用 `get_app_dir()` / `get_config_path()` / `ensure_dirs()`
4. **Agent文件用相对路径读取**：基于 `get_app_dir()` 定位 `agents/` 目录
5. **文件操作前确认对话框**：删除/导出等危险操作需确认
6. **原子文件操作**：防止数据损坏
7. **操作日志**：所有关键操作写入 `logs/netops_YYYYMMDD.log`

---

## 关键源码文件速查

### 激活体系（V0.3.0 新增）

| 文件 | 职责 |
|------|------|
| [src/core/activation_engine.py](src/core/activation_engine.py) | 用户端激活引擎（机器码/激活码/授权存储/黑名单校验） |
| [src/core/admin_keygen.py](src/core/admin_keygen.py) | 管理员制码核心（加密台账/备份恢复/黑名单管理） |
| [src/ui/activation_dialog.py](src/ui/activation_dialog.py) | 用户端激活弹窗UI |
| [src/ui/admin_tool_window.py](src/ui/admin_tool_window.py) | 管理员制码工具UI（台账/备份/导出/导入） |

### 路径管理核心

| 文件 | 职责 |
|------|------|
| [src/utils/resource_path.py](src/utils/resource_path.py) | get_app_dir() / get_single_dir() / get_config_path() / ensure_dirs() + 旧数据迁移 |
| [src/core/key_manager.py](src/core/key_manager.py) | AES-GCM 密钥管理（V0.2版本） |
| [src/core/secure_config.py](src/core/secure_config.py) | 加密配置文件读写（单例） |
| [src/core/logger.py](src/core/logger.py) | 日志系统（EXE同级logs/） |
| [src/core/local_audit_engine.py](src/core/local_audit_engine.py) | 本地合规规则引擎（双层审计预检层） |
| [src/core/local_diagnostic_engine.py](src/core/local_diagnostic_engine.py) | 本地运行时诊断引擎（异常提取 + 精准上下文） |

### UI页面（V0.2架构）

| 文件 | 导航名称 | 职责 |
|------|---------|------|
| [src/ui/main_window.py](src/ui/main_window.py) | — | 主窗口 + 导航栏 + 页面切换 |
| [src/ui/project_manager_page.py](src/ui/project_manager_page.py) | 📁 新建项目 | 项目CRUD + 卡片总览 + 状态灯 + 全局统计 |
| [src/ui/ops_toolbox_page.py](src/ui/ops_toolbox_page.py) | 🔧 项目运维 | 3任务卡片 + 4Tab文件管理 + AI合规/诊断 |
| [src/ui/single_device_page.py](src/ui/single_device_page.py) | 🔍 单点运维 | 5Tab全链条 + 测试连接 + 文件三件套 |
| [src/ui/ai_analysis_page.py](src/ui/ai_analysis_page.py) | 🤖 专家工作站 | 3Tab + Agent快捷指令 + 可编辑Prompt + 多文件 |
| [src/ui/system_settings_page.py](src/ui/system_settings_page.py) | ⚙ 模型设置 | AI模型多配置管理 + 加密存储 + 自动匹配 |

### 业务脚本

| 文件 | 职责 |
|------|------|
| [scripts/network_inspect.py](scripts/network_inspect.py) | 巡检引擎 + 设备类型映射 |
| [scripts/backup_all_config.py](scripts/backup_all_config.py) | 批量/单点配置备份 |
| [scripts/run_trouble_cmd.py](scripts/run_trouble_cmd.py) | 故障设备二次核查 |

### AI Agent

| 文件 | 职责 |
|------|------|
| [agents/network-config-reviewer.md](agents/network-config-reviewer.md) | 配置合规审计系统提示词 |
| [agents/network-troubleshooter.md](agents/network-troubleshooter.md) | OSI分层故障诊断系统提示词 |

---

## 项目交付物

### 可执行文件（两个独立EXE）

| EXE | 位置 | 大小 | 用途 |
|-----|------|------|------|
| 用户端主程序 | `dist/NetworkConfigGenerator.exe` | 47.1MB | 用户日常使用，含激活校验 |
| 管理员制码工具 | `dist/AdminKeyGenTool.exe` | 41.3MB | 管理员专用，生成激活码/管理黑名单 |

> **重要：** 两个EXE独立打包、独立运行。管理员制码工具严禁外发给用户。

### 源代码结构

- **核心模块：** src/core/ (7文件：含activation_engine.py、admin_keygen.py), src/ui/ (8文件：含activation_dialog.py、admin_tool_window.py), src/utils/ (3文件)
- **业务脚本：** scripts/ (4文件：含build_admin_tool.py)
- **AI Agent：** agents/ (2个系统提示词)
- **测试用例：** tests/ (305个单元测试，核心模块覆盖率≥83%)

### 文档

- **技术总纲：** CLAUDE.md （本文件）
- **规则集：** .claude/rules/ (7个领域规则文件)
- **架构方案：** .claude/rules/07-v2-architecture-plan.md
- **使用说明书：** 使用说明书.md

---

## 使用建议

### 首次使用

1. 双击 `NetworkConfigGenerator.exe` 启动（首次会自动创建所有目录）
2. **试用模式**：未激活可直接使用「锐捷接入交换机配置」功能，其他功能受限
3. **激活软件**：点击右上角「关于」→「软件激活」→ 复制机器码 → 发送给管理员【老韩】（QQ:223518 / WeChat:tachlaohan）→ 填入激活码 → 点击激活
4. 激活后进入「📁 新建项目」→ 创建项目 → 添加设备清单
5. 进入「⚙ 模型设置」→ 配置AI模型 → 测试连通性 → 保存
6. 进入「🔍 单点运维」→ 添加设备 → 测试连接 → 执行巡检/备份
7. 进入「🔧 项目运维」→ 选择项目 → 执行批量任务 → 查看结果Tab

### AI使用路径

- **快速分析：** 单点运维页 → 选中文件 → 点 `[🔍AI合规巡检]` 或 `[🩺AI故障诊断]`
- **深度分析：** 专家工作站 → 选文件 → 点Agent快捷指令 → 编辑Prompt → 发送
- **自由对话：** 专家工作站 → 💬自由对话Tab → 输入任意问题 → 发送

### 数据安全

- AI配置自动加密存储为 `.enc` 文件
- 密钥绑定机器ID，拷贝到其他电脑需重新配置
- 所有操作写入日志文件 `logs/netops_YYYYMMDD.log`
- 删除/导出等危险操作有确认对话框

### 性能预期

- 启动时间：3-5秒
- 配置生成：首次较慢（缓存生效后快速）
- 内存占用：150-200MB
- 文件保存：原子操作，防止损坏
- EXE大小：47.1MB（PyInstaller打包）

### AI请求优化（V0.2.1）

- **双层分析**：本地规则引擎预检 + AI精审，减少AI无效推理
- **精准上下文提取**：`extract_relevant_context()` 根据异常位置提取周边上下文，替代全文截断
- **Token压缩**：合规审计从 18.4KB → 5.0KB（-73%），故障诊断从 151.6KB → 5.5KB（-96%）
- **Agent文件精简**：reviewer 84%缩减，troubleshooter 84%缩减

### 故障排查

- **启动崩溃**：检查 `logs/` 目录下最新日志 + `logs/crash.log`
- **试用模式**：未激活用户进入主窗口后仅可使用「锐捷接入交换机配置」，点击其他功能弹出激活提示，属正常设计
- **激活弹窗无法关闭**：正常设计，试用模式下用户主动触发激活弹窗后，必须完成激活或点击关闭才能返回
- **提示"授权已失效"**：设备被列入黑名单，联系管理员【老韩】重新审核
- **AI按钮报"未配置模型"**：进入模型设置确认已保存配置并设为激活
- **配置丢失**：检查 config/ai_config.json.enc 是否存在
- **项目找不到**：检查 config/projects_config.json 和 projects/ 目录
- **AI分析崩溃**：确保 agents/ 目录下两个 Agent 文件存在

---

## 版本更新历史

### V0.3.0 激活体系版（2026-05-21）

- ✅ 新增软件激活三套方案完整体系（方案A纯离线/方案B 180天黑名单/方案C管理员制码工具）
- ✅ 新增激活核心引擎 `src/core/activation_engine.py`（机器码/激活码/授权存储/黑名单校验）
- ✅ 新增用户激活弹窗 `src/ui/activation_dialog.py`（无关闭/无跳过/无试用）
- ✅ 新增管理员制码工具 `src/ui/admin_tool_window.py` + `src/core/admin_keygen.py`
- ✅ 新增管理员工具独立入口 `admin_tool_main.py` + 打包规格 `admin_tool.spec`
- ✅ 新增管理员工具打包脚本 `scripts/build_admin_tool.py`
- ✅ 修改 `main.py` 启动强制校验 + `main_window.py` 版本号
- ✅ 新增规则文件 `.claude/rules/08-activation-plan.md`
- ✅ 新增测试文件 `tests/core/test_activation_engine.py`（36个测试用例）
- ✅ 全量305个测试用例通过，核心模块覆盖率83.43%
- ✅ 用户端EXE打包：`dist/NetworkConfigGenerator.exe`（47.1MB）
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.2MB）

### V0.3.1 试用模式版（2026-05-21）

- ✅ **试用模式**：未激活用户进入主窗口，仅开放「锐捷接入交换机配置」功能
- ✅ 修改 `main.py`：未激活不退出，改为进入试用模式
- ✅ 修改 `main_window.py`：添加 `_trial_mode` 状态检测 + 导航拦截 + 配置页限制
- ✅ 新增 `_show_trial_prompt()` 弹窗：提示联系老韩（QQ:223518 / WeChat:tachlaohan）
- ✅ 新增 `_open_activation_dialog()`：关于对话框中试用模式可主动激活
- ✅ 窗口标题显示「[试用模式]」标识
- ✅ 关于对话框版本号动态显示「V0.3.0 试用版」
- ✅ 全量305个测试用例通过
- ✅ 用户端EXE打包：`dist/NetworkConfigGenerator.exe`（47.1MB）
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.3MB）

### V0.3.1 激活增强版（2026-05-21）

- ✅ **有效期扩展**：管理员工具有效期选项扩展为10档（永久/5年/10年/3年/2年/1年/半年/季度/月度/周度）
- ✅ **剩余天数显示**：`check_activation()` 返回3元组，含 `days_remaining`/`is_permanent`/`expire_at`
- ✅ **导航栏激活按钮**：实时显示剩余天数（✅永久激活/✅剩XXX天/🔓未激活），颜色编码（绿/橙/红）
- ✅ **授权详情弹窗**：点击已激活按钮弹出详细信息（激活时间、到期时间、剩余天数、到期预警）
- ✅ **管理员工具窗口自适应**：启动时自动设为屏幕可用区域80%宽高并居中显示
- ✅ 修改 `activation_engine.py`：`save_license()` 支持 `validity_days`，`check_activation()` 返回详细授权信息
- ✅ 修改 `admin_tool_window.py`：有效期10档 + 窗口80%屏幕居中
- ✅ 修改 `main_window.py`：激活按钮显示剩余天数 + 颜色编码 + 详情弹窗
- ✅ 全量306个测试用例通过
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.3MB）

### V0.2.1 目录架构优化版（2026-05-19）

- ✅ 三区分离架构：系统配置(`config/`) + 单点数据(`single/`) + 项目数据(`projects/`)，顶层仅保留EXE
- ✅ 单点运维数据全量归入 `single/` 子目录，与项目内部结构复用同一套脚本逻辑
- ✅ 系统配置文件（加密配置/项目索引/最近文件）统一归入 `config/` 子目录
- ✅ 修复 `_get_single_report_dir()` 和 `save_err_log()` Frozen模式忽略项目上下文BUG
- ✅ 补齐项目创建 `PROJECT_SUBDIRS`（含 report/single_inspect、diagnosis、compliance）
- ✅ 单点端报告命名统一（compliance_{ts}.md / diagnosis_{ts}.md）
- ✅ 旧数据自动迁移：首次启动自动将散落文件迁移至新结构
- ✅ 新增 `get_single_dir()` / `get_config_dir()` API

### V0.2.0 架构升级版（2026-05-19）

- 运维工具箱重构为「项目运维」任务中心（3任务卡片 + 4Tab + AI嵌入 + 文件三件套）
- AI分析页重定义为「专家工作站」（3Tab + Agent快捷指令 + 可编辑Prompt + 多文件）
- 新建项目页升级「项目总览」（卡片网格 + 状态灯🟢🟡🔴 + 全局统计）
- 导航改名：「运维工具箱→项目运维」「单点巡检→单点运维」「AI分析→专家工作站」
- AI能力三层架构正式落地
- 文件管理三件套统一标准，覆盖全页面
- 双层审计架构（本地预检 + AI精审）
- 合规审计报告全中文化

### V0.2.1 AI精审优化版（2026-05-20）

- ✅ **双层AI分析架构**：本地规则引擎预检 → 精简摘要 + 精准上下文 → AI精审
- ✅ **精准上下文提取**：`extract_relevant_context()` 精确子串匹配 + 行数上限保护
- ✅ **Agent文件精简**：reviewer 11.7KB→1.9KB，troubleshooter 14.2KB→2.3KB
- ✅ **Token消耗大幅降低**：合规审计 -73%，故障诊断 -96%
- ✅ **关键词匹配修复**：从模糊拆词匹配改为精确行匹配，避免大文件全文发送
- ✅ **spec文件补全**：新增 `local_diagnostic_engine` hiddenimport

### V0.1.0 便携化版（2026-05-18）

- 全面路径便携化改造，所有数据跟随EXE
- AI模型多配置管理（新增/删除/重命名/切换/加密）
- 单点设备增强（测试连接按钮 + 备份修复）
- 巡检功能修复（设备类型映射 + 报告保存）
- 日志系统跟随EXE
- 修复 key_manager.py Path 导入缺失问题

### V0.0.9 初始版（2026-05-17）

- 基础六菜单框架搭建
- 四厂商配置脚本集成
- AES-GCM加密体系搭建
- 安全加固9项 + 性能优化4项
- 测试框架232个用例

---

## 技术支持与扩展

如需功能扩展或问题排查，请参考：

- **规则文件：** `.claude/rules/` 目录下对应领域文档
- **测试用例：** `tests/` 目录
- **运行日志：** `logs/netops_YYYYMMDD.log`
- **关键入口：** `main.py` → `src/ui/main_window.py`
- **使用说明书：** `使用说明书.md`