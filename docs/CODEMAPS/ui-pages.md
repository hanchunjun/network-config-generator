# UI页面代码地图

**最后更新：** 2026-05-22

---

## 主窗口导航结构

```
顶部固定主菜单（从左到右）：

📁 新建项目  →  🔧 项目运维  →  🔍 单点运维  →  🤖 专家工作站  →  🖥 设备配置  →  🌐 子网计算  →  📜 命令生成  →  ⚙ 模型设置
    建              管                修                研                配              算              写              设
```

快捷键：`Ctrl+1` ~ `Ctrl+8` 切换对应页面

---

## 页面1：📁 新建项目（project_manager_page.py）

**文件：** `src/ui/project_manager_page.py`
**对应规则：** `.claude/rules/03-module-spec.md §模块1`

### 功能清单
| 功能 | 说明 |
|------|------|
| 项目列表 | 卡片网格展示所有项目 |
| 项目总览卡片 | 状态灯🟢🟡🔴 + 设备数 + 最近备份/巡检时间 + 故障设备数 |
| 全局统计栏 | 项目数/设备总数/最近全量巡检时间 |
| 新建/重命名/删除项目 | CRUD操作，删除有确认对话框 |
| 编辑设备清单 | 可视化编辑 device_list.txt |
| 打开项目目录 | 用文件管理器打开 |

### 关键方法
| 方法 | 行号 | 说明 |
|------|------|------|
| `refresh_project_list()` | — | 刷新项目卡片网格 |
| `_create_project()` | — | 创建新项目 + 标准化目录 |
| `_delete_project()` | — | 删除项目（有确认） |
| `_open_device_list_editor()` | — | 打开设备清单编辑器 |

### AI能力
- 无直接AI按钮（项目总览页）

---

## 页面2：🔧 项目运维（ops_toolbox_page.py）

**文件：** `src/ui/ops_toolbox_page.py`
**对应规则：** `.claude/rules/03-module-spec.md §模块2`

### 功能清单
| 功能 | 说明 |
|------|------|
| 项目选择器 | 顶部下拉框，所有任务共用 |
| 💾 批量配置备份 | SSH批量抓取所有设备配置 |
| 🔍 全网自动化巡检 | CPU/内存/接口/日志只读巡检 |
| 🛠 故障设备二次核查 | 自动识别故障IP、只读指令深挖 |
| 结果Tab × 4 | 备份文件/巡检报告/诊断报告/合规审计 |
| 文件管理三件套 | 🔄刷新/📂打开/🗑删除 |

### Tab结构
```
Tab 0: 💾 备份文件 → [🔍AI合规巡检]按钮
Tab 1: 📊 巡检报告 → [🩺AI故障诊断]按钮
Tab 2: 🩺 诊断报告 → [🩺AI故障诊断]按钮
Tab 3: 🔍 合规审计 → [🩺AI精审]按钮
```

### 关键线程
| 线程类 | 行号 | 说明 |
|--------|------|------|
| `OpsBackupThread` | — | 批量备份线程 |
| `OpsInspectThread` | — | 批量巡检线程 |
| `OpsTroubleThread` | — | 故障核查线程 |
| `OpsDiagnosticThread` | ~350 | AI诊断线程（双层分析） |
| `OpsComplianceThread` | — | AI合规审计线程（双层） |

### AI按钮
| 按钮 | Agent | 触发线程 |
|------|-------|---------|
| `[🔍AI合规巡检]` | reviewer | `OpsComplianceThread` |
| `[🩺AI故障诊断]` | troubleshooter | `OpsDiagnosticThread` |
| `[🩺AI精审]` | reviewer（双层） | `OpsComplianceThread` |

---

## 页面3：🔍 单点运维（single_device_page.py）

**文件：** `src/ui/single_device_page.py`
**对应规则：** `.claude/rules/03-module-spec.md §模块3`

### 功能清单
| 功能 | 说明 |
|------|------|
| 设备录入 | IP/厂商/类型/账号密码，支持粘贴导入 |
| 🧪 测试连接 | Ping + SSH/Telnet 双协议验证 |
| ▶ 批量巡检 | 只读指令巡检 |
| 💾 批量备份 | SSH配置备份 |
| 结果Tab × 5 | 巡检日志/配置备份/巡检报告/诊断报告/合规审计 |
| 文件管理三件套 | 🔄刷新/📂打开/🗑删除 |

### Tab结构
```
Tab 0: 巡检日志（实时输出）
Tab 1: 配置备份 → [🔍AI合规巡检]按钮
Tab 2: 巡检报告 → [🩺AI故障诊断]按钮
Tab 3: 🩺诊断报告 → [🩺AI故障诊断]按钮
Tab 4: 🔍合规审计 → [🩺AI精审]按钮 + 本地预检摘要
```

### 关键线程
| 线程类 | 行号 | 说明 |
|--------|------|------|
| `SingleDeviceWorker` | ~852 | 巡检/备份工作线程 |
| `AIDiagnosticThread` | ~585 | AI故障诊断线程（双层分析） |

### AI按钮
| 按钮 | Agent | 触发线程 |
|------|-------|---------|
| `[🔍AI合规巡检]` | reviewer | 内置双层分析 |
| `[🩺AI故障诊断]` | troubleshooter | `AIDiagnosticThread` |
| `[🩺AI精审]` | reviewer（双层） | 内置双层分析 |

### 关键回调
| 方法 | 行号 | 说明 |
|------|------|------|
| `_on_diagnose_finished()` | ~2503 | AI诊断完成回调（保存+刷新+切换Tab） |
| `_on_diagnose_error()` | ~2491 | AI诊断错误回调（日志+弹窗） |
| `_restore_diagnose_btn()` | ~2454 | 恢复按钮状态 |
| `refresh_diagnosis_list()` | ~2749 | 刷新诊断报告列表 |

---

## 页面4：🤖 专家工作站（ai_analysis_page.py）

**文件：** `src/ui/ai_analysis_page.py`
**对应规则：** `.claude/rules/03-module-spec.md §模块4`

### 功能清单
| 功能 | 说明 |
|------|------|
| 左侧面板 | 文件选择/最近文件/历史报告 |
| 💬 自由对话 | 完全自定义Prompt + 多轮迭代 |
| 📋 合规审计 | reviewer Agent + 可编辑Prompt + 多文件 |
| 🩺 故障诊断 | troubleshooter Agent + 可编辑Prompt + 多文件 |
| Agent快捷指令 | `[🔍一键合规巡检]` / `[🩺一键故障诊断]` |
| 结果输出 | Markdown渲染 + 保存/导出 |

### Tab结构
```
Tab 0: 💬 自由对话（完全自定义）
Tab 1: 📋 合规审计（reviewer Agent）
Tab 2: 🩺 故障诊断（troubleshooter Agent）
```

### 关键线程
| 线程类 | 行号 | 说明 |
|--------|------|------|
| `ExpertAnalysisThread` | ~110 | 专家分析线程（统一处理3种Tab） |

### AI三层架构
```
第一层：嵌入式按钮（单点运维/项目运维）→ 自动执行
第二层：Agent快捷指令（专家工作站）→ 可编辑Prompt → 手动发送
第三层：自由对话（专家工作站）→ 完全自定义
```

---

## 页面5：🖥 设备配置（config_pages/）

**文件目录：** `src/ui/config_pages/`
**对应规则：** `.claude/rules/03-module-spec.md §模块5`

### 文件结构
```
config_pages/
├── base_config_page.py          # 基类（所有配置页面继承）
├── ruijie/                      # 锐捷（4个设备类型）
│   ├── access_switch_config.py  # 接入交换机
│   ├── core_switch_config.py    # 核心交换机
│   ├── router_config.py         # 路由器
│   └── ac_config.py             # AC控制器
├── huawei/                      # 华为（4个设备类型）
│   ├── access_switch_config.py
│   ├── core_switch_config.py
│   ├── router_config.py
│   └── ac_config.py
├── h3c/                         # H3C（4个设备类型）
│   ├── access_switch_config.py
│   ├── core_switch_config.py
│   ├── router_config.py
│   └── ac_config.py
└── cisco/                       # 思科（4个设备类型）
    ├── access_switch_config.py
    ├── core_switch_config.py
    ├── router_config.py
    └── ac_config.py
```

### 扩展方式
新增厂商：在 `config_pages/` 下新建目录，继承 `BaseConfigPage`，实现4个设备类型页面。

---

## 页面6：⚙ 模型设置（system_settings_page.py）

**文件：** `src/ui/system_settings_page.py`
**对应规则：** `.claude/rules/03-module-spec.md §模块6`

### 功能清单
| 功能 | 说明 |
|------|------|
| 多模型管理 | 新增/删除/重命名/切换 |
| 加密存储 | SecureConfigFile + AES-GCM |
| 连通性测试 | 验证API可用性 |
| 自动匹配 | 所有AI按钮自动读取激活模型 |

### 关键API
| 函数 | 说明 |
|------|------|
| `get_active_ai_config()` | 获取当前激活的AI配置（被3个页面调用） |
| `save_ai_config()` | 保存AI配置（加密） |
| `test_connection()` | 测试API连通性 |

---

## 页面7：🌐 子网计算（subnet_calculator_page.py）★V0.3.1新增

**文件：** `src/ui/subnet_calculator_page.py`

### 功能清单
| 功能 | 说明 |
|------|------|
| IP地址输入 | 支持点分十进制IP（如 192.168.1.0） |
| 子网掩码选择 | 支持 CIDR（/0~/32）和点分十进制两种模式 |
| 实时计算 | 网络地址、广播地址、可用IP范围、总IP数 |
| 二进制位对照表 | 每字节8位，直观展示IP与掩码AND运算 |
| 子网划分详情表 | 完整的网络属性表格（网络号、掩码、可用地址等） |

### 关键方法
| 方法 | 说明 |
|------|------|
| `_ip_changed()` | IP输入变化时实时计算 |
| `_mask_changed()` | 掩码模式/值变化时实时计算 |
| `_calculate()` | 核心计算逻辑（IP转二进制、AND运算） |
| `_display_result()` | 填充结果表格和二进制位对照 |

### 设计约束
- 试用模式下开放使用（无需激活）
- 实时计算，无需点击按钮
- 子网划分表使用 QTableWidget，只读不可编辑

---

## 页面8：📜 命令生成（batch_cmd_generator_page.py）★V0.3.1新增

**文件：** `src/ui/batch_cmd_generator_page.py`

### 功能清单
| 功能 | 说明 |
|------|------|
| 命令模板编辑 | 支持多行命令输入，`%a`~`%e` 参数占位 |
| 参数配置 | 5组参数，每组支持范围（起止/步长）、列表、单个值 |
| 循环模式 | 遍历所有参数组合（笛卡尔积） |
| 步进模式 | 参数同步递增（各参数索引对齐） |
| 重复模式 | 每个命令重复N次 |
| 预置模板 | 内置常用命令模板（VLAN批量、接口配置等） |
| 命令预览 | 实时生成预览，展示最终命令序列 |
| 导出 | 复制全部命令到剪贴板 |

### 参数模式
```
范围模式：5-10/1 → 生成 5,6,7,8,9,10
列表模式：1,3,5,7 → 生成 1,3,5,7
单值模式：100    → 固定值 100
```

### 占位符映射
| 占位符 | 用途示例 |
|--------|----------|
| `%a` | VLAN ID |
| `%b` | 端口号 |
| `%c` | IP第三段 |
| `%d` | IP第四段 |
| `%e` | 描述/备注 |

### 关键方法
| 方法 | 说明 |
|------|------|
| `_generate_commands()` | 根据模式和参数生成命令序列 |
| `_preview_commands()` | 在预览区展示生成的命令 |
| `_copy_commands()` | 复制全部命令到剪贴板 |
| `_load_template()` | 加载预置模板 |

### 设计约束
- 试用模式下开放使用（无需激活）
- 命令生成逻辑在后台线程执行，不阻塞UI
- 参数解析失败时给出明确错误提示

---

## 对话框组件

| 文件 | 用途 |
|------|------|
| `device_form_dialog.py` | 设备信息录入/编辑 |
| `device_discovery_dialog.py` | 设备自动发现 |
| `device_template_dialog.py` | 设备模板管理 |
| `history_dialog.py` | 历史记录查看 |
| `security_dialogs.py` | 安全确认（导出/删除/查看密码） |
| `activation_dialog.py` | 用户激活弹窗 ★V0.3.0新增 |

---

## 激活弹窗（activation_dialog.py）— V0.3.0新增

**文件：** `src/ui/activation_dialog.py`
**对应规则：** `.claude/rules/08-activation-plan.md §4`

### 设计约束
- 模态对话框，无关闭按钮、无跳过按钮、无试用入口
- 机器码只读展示 + 一键复制
- 激活码输入框 + 立即激活按钮
- 严格按定稿文案实现

### 关键方法
| 方法 | 说明 |
|------|------|
| `show_activation_dialog()` | 显示激活弹窗，返回是否激活成功 |

---

## 管理员制码工具（admin_tool_window.py）— V0.3.0新增

**文件：** `src/ui/admin_tool_window.py`
**独立入口：** `admin_tool_main.py`
**对应规则：** `.claude/rules/08-activation-plan.md §方案C`

### 设计约束
- 独立EXE，不与用户端合并
- 仅限管理员本地使用，严禁外发
- 窗口标题：`NetOps 管理员制码工具 V0.3.0 — 老韩专用`

### 功能清单
| 功能 | 说明 |
|------|------|
| 机器码粘贴输入 | 接收用户发来的32位机器码 |
| 一键生成激活码 | 调用 `admin_keygen.generate_code_for_machine()` |
| 一键复制激活码 | 复制到剪贴板 |
| 用户信息备注 | 姓名/用途/备注 |
| 台账自动保存 | 写入 `admin_data/records.dat`（AES-GCM加密） |
| 黑名单快捷添加 | 一键将机器码加入黑名单 |
| 黑名单导出 | 导出为可上传云端的TXT格式 |
