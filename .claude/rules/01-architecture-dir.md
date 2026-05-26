# 项目扩建底层逻辑 & 目录结构（V0.3.5）

## 项目扩建底层逻辑

全程基于原有项目做增量功能开发，不修改原有代码、不调整原有目录、不破坏原有功能，新增模块与原有模块完全解耦，可独立启用/关闭，保证原有配置生成功能稳定运行。

## 公共脚本库（全项目复用，不随项目复制）

```
scripts/
├── backup_all_config.py   # 全厂商设备基线配置批量备份脚本
├── network_inspect.py     # 全网设备自动化健康巡检脚本
└── run_trouble_cmd.py     # 故障设备二次只读核查脚本
```

核心规则：脚本存放于程序根目录，所有新建项目共用，无需每个项目单独复制，统一维护、统一更新。

## AI Agent 目录

```
agents/
├── network-config-reviewer.md    # 配置合规审计系统提示词
└── network-troubleshooter.md     # OSI分层故障诊断系统提示词
```

Agent文件由所有AI按钮统一调用（单点运维、项目运维、专家工作站）。

## 项目标准目录结构

```
project_root/
├── config/
│   └── device_list.txt            # 格式：IP,厂商,设备类型,用户名,密码,协议,特权密码
├── output/
│   ├── single_exception/          # 单点异常输出
│   └── trouble_check_result/     # 故障核查结果
├── report/
│   ├── diagnosis/                 # AI诊断报告归档
│   ├── compliance/                # AI合规审计报告归档
│   └── single_inspect/            # 单点巡检报告
└── config_backup/                 # 配置备份归档
```

核心规则：项目间数据完全物理隔离，禁止跨项目读取、写入、操作，所有运维操作仅绑定当前选中项目。

## EXE运行时目录结构（V0.3.3 五区分离）

```
程序根目录/
├── NetworkConfigGenerator.exe     ← 主程序（唯一顶层文件）
│
├── config/                        ← 🔧 系统配置
│   ├── key_info.json              ← 加密密钥（AES-GCM V0.2）
│   ├── machine_id.json            ← 机器绑定ID
│   ├── ai_config.json.enc         ← AI模型配置（加密）
│   ├── projects_config.json       ← 项目列表索引
│   ├── ai_recent_files.json       ← AI最近文件记录
│   └── account.json               ← 账户信息（用户名明文+密码AES-GCM密文）★V0.3.3新增
│
├── activation/                    ← 🔐 用户端激活体系
│   ├── license.dat                ← 激活授权文件（AES-GCM加密）
│   └── bl_check.dat               ← 黑名单校验时间记录
│
├── admin_data/                    ← 🛡 管理员数据（独立隔离）
│   ├── records.dat                ← 授权台账（AES-GCM加密）
│   ├── blacklist.txt              ← 本地黑名单
│   └── backup/                    ← 台账备份目录
│       └── records_YYYYMMDD_HHMMSS.dat
│
├── logs/                          ← 📝 运行日志
│
├── single/                        ← 🔍 单点运维全量隔离
│   ├── single_devices.json.enc    ← 单点设备清单（加密）
│   ├── config_backup/             ← 单点配置备份
│   ├── output/single_exception/   ← 单点巡检异常
│   └── report/
│       ├── single_inspect/        ← 单点巡检报告
│       ├── compliance/            ← 单点AI合规审计
│       └── diagnosis/             ← 单点AI诊断+精审
│
└── projects/                      ← 📁 项目数据
    └── 01_项目名称/
        ├── config/device_list.txt
        ├── config_backup/
        ├── output/
        │   ├── all_device_full.md
        │   ├── single_exception/
        │   ├── trouble_check_result/
        │   └── manual_high_risk_task.txt
        └── report/
            ├── single_inspect/
            ├── compliance/
            └── diagnosis/
```

> **五区分离设计**：系统配置(`config/`) + 用户端激活(`activation/`) + 管理员数据(`admin_data/`) + 单点数据(`single/`) + 项目数据(`projects/`)，五层物理隔离。管理员数据与用户端激活完全独立，台账加密存储，支持备份恢复。

## 路径管理API

| 函数 | 用途 | 示例 |
|------|------|------|
| `get_app_dir()` | EXE所在目录根路径 | `D:\工具\` |
| `get_config_dir()` | 系统配置子目录 | `D:\工具\config\` |
| `get_activation_dir()` | 激活体系子目录 | `D:\工具\activation\` |
| `get_single_dir()` | 单点运维子目录 | `D:\工具\single\` |
| `get_config_path(filename)` | 相对于EXE根目录的路径 | `D:\工具\config\ai_config.json.enc` |
| `resource_path(relative)` | 打包内嵌资源 | `_MEIPASS/scripts/` |

## 旧数据自动迁移

程序启动时 `ensure_dirs()` 检测旧版散落文件（EXE同级的 `ai_config.json.enc`、`projects_config.json`、`single_devices.json.enc`、`config_backup/`、`output/`、`report/` 等），自动迁移至新结构的三区对应位置。