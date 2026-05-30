# 数据流代码地图

**最后更新：** 2026-05-30
**项目版本：** V0.4.2

---

## 五区分离架构

```
EXE所在目录/
│
├── config/           ← 🔧 系统配置区（全局共享）
│   ├── key_info.json              # 加密密钥
│   ├── machine_id.json            # 机器ID
│   ├── ai_config.json.enc         # AI配置（加密）
│   ├── projects_config.json       # 项目列表索引
│   ├── ai_recent_files.json       # AI最近文件记录
│   ├── account.json               # 账户信息（用户名明文+密码AES-GCM密文）★V0.3.3新增
│   └── theme_config.json          # 主题配置（theme_id持久化）★V0.3.5新增
│
├── activation/       ← 🔐 用户端激活体系
│   ├── license.dat                # 激活授权文件（AES-GCM加密）
│   └── bl_check.dat               # 黑名单校验时间记录
│
├── admin_data/       ← 🛡 管理员数据（独立隔离）
│   ├── records.dat                # 授权台账（AES-GCM加密）
│   ├── blacklist.txt              # 本地黑名单
│   └── backup/                    # 台账备份目录
│       └── records_YYYYMMDD_HHMMSS.dat
│
├── single/           ← 🔍 单点运维区（独立隔离）
│   ├── single_devices.json.enc    # 单点设备清单（加密）
│   ├── config_backup/             # 单点配置备份
│   ├── output/single_exception/   # 单点巡检异常
│   └── report/
│       ├── single_inspect/        # 单点巡检报告
│       ├── compliance/            # 单点AI合规审计
│       └── diagnosis/             # 单点AI诊断+精审
│
├── projects/         ← 📁 项目数据区（多项目物理隔离）
│   └── 01_项目名称/
│       ├── config/device_list.txt # 设备清单
│       ├── config_backup/         # 项目配置备份
│       ├── output/                # 批量运维输出
│       │   ├── all_device_full.md
│       │   ├── single_exception/
│       │   ├── trouble_check_result/
│       │   └── manual_high_risk_task.txt
│       └── report/
│           ├── single_inspect/    # 项目巡检报告
│           ├── compliance/        # 项目AI合规审计
│           └── diagnosis/         # 项目AI诊断+精审
│
└── logs/             ← 📝 日志区
    ├── netops_YYYYMMDD.log        # 主运行日志
    └── crash.log                  # 崩溃日志
```

---

## 数据流转路径

### 批量备份流程
```
用户点击[💾批量配置备份]
  → 读取 projects/项目名/config/device_list.txt
  → 逐台SSH连接设备
  → 执行 show running-config（只读）
  → 保存到 projects/项目名/config_backup/
  → 更新UI文件列表
```

### 批量巡检流程
```
用户点击[🔍全网自动化巡检]
  → 读取 device_list.txt
  → 逐台SSH连接设备
  → 执行CPU/内存/接口/日志检查命令（只读）
  → 生成巡检报告 → projects/项目名/report/single_inspect/
  → 生成汇总报告 → projects/项目名/output/all_device_full.md
  → 更新UI文件列表
```

### AI诊断流程
```
用户点击[🩺AI故障诊断]
  → 读取选中的巡检报告/日志内容
  → Layer1: 本地诊断引擎提取异常
  → 生成精简摘要 + 精准上下文
  → Layer2: 发送AI API请求
  → 接收AI返回结果
  → 拼接双层报告
  → 保存到 report/diagnosis/（单点）或 report/diagnosis/（项目）
  → 更新UI显示
```

### AI合规审计流程
```
用户点击[🔍AI合规巡检]
  → 读取选中的备份配置文件
  → Layer1: 本地合规引擎检查
  → 生成精简问题列表 + 精准配置上下文
  → Layer2: 发送AI API请求
  → 接收AI返回结果
  → 拼接双层报告
  → 保存到 report/compliance/
  → 更新UI显示
```

---

## 设备清单格式

**文件：** `projects/项目名/config/device_list.txt`
**格式：** `IP，厂商，设备类型，用户名，密码，协议，特权密码`

示例：
```
192.168.1.1，锐捷，核心交换机，admin，password123，ssh，enable123
192.168.1.2，华为，接入交换机，admin，password456，ssh，enable456
```

---

## 加密存储说明

| 数据 | 存储位置 | 加密方式 |
|------|---------|---------|
| AI模型配置 | `config/ai_config.json.enc` | AES-GCM，密钥绑定机器ID |
| 单点设备清单 | `single/single_devices.json.enc` | AES-GCM |
| 设备密码 | `projects/项目名/config/device_list.txt` | 明文（⚠️ 安全提示：导出文件包含明文密码） |
| 密钥文件 | `config/key_info.json` | 动态派生（V0.2版本） |
| 机器ID | `config/machine_id.json` | 明文 |
| 激活授权 | `activation/license.dat` | AES-GCM（V0.3.0新增） |
| 账户密码 | `config/account.json` | AES-GCM，`ENC:`前缀密文（V0.3.3新增） |
| 主题配置 | `config/theme_config.json` | 明文JSON，`{"theme_id": "vscode"}`（V0.3.5新增） |

---

## 激活数据流（V0.3.0新增）

### 用户端启动流程（V0.3.3）
```
启动 → SetProcessDpiAwareness(0) [DPI适配]
  → _check_activation() [激活校验]
      → 未激活 → 弹出激活弹窗
          → 用户复制机器码 → 发送给管理员
          → 填入激活码 → verify_activation_code()
          → 校验通过 → save_license() → 进入登录
          → 校验失败 → 提示错误，留在弹窗
      → 已激活 → perform_silent_check()（方案B黑名单校验）
          → 联网失败 → 跳过（不判失效）
          → 黑名单命中 → 弹出失效窗口 → 退出
          → 正常 → 进入登录
  → LoginDialog [登录认证，V0.3.3新增]
      → 验证用户名密码 → account.json
      → 成功 → 启动主程序
      → 失败 → 提示错误，留在登录窗口
  → ThemeEngine.get() [主题引擎初始化，V0.3.5新增]
      → 加载 config/theme_config.json → 应用上次主题
      → 主窗口所有组件连接 theme_changed 信号
```

### 管理员制码流程
```
管理员工具 → 粘贴用户机器码
  → generate_code_for_machine() → 生成16位激活码
  → save_record() → 写入 config/admin_records.json
  → 下发激活码给用户
  → 如需封禁 → add_to_blacklist() → config/blacklist_local.txt
  → export_blacklist_for_upload() → 导出上传云端
```

---

## 高危操作人工清单

以下操作**禁止自动化**，仅生成人工执行清单：
- 接口启停
- 路由变更
- 设备重启
- 配置保存

**输出文件：** `projects/项目名/output/manual_high_risk_task.txt`
