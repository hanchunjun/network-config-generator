# 项目扩建底层逻辑 & 目录结构（V2.0）

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

## EXE运行时目录结构（V2.1 三区分离）

```
程序根目录/
├── NetworkConfigGenerator.exe     ← 主程序（唯一顶层文件）
│
├── config/                        ← 🔧 系统配置
│   ├── key_info.json              ← 加密密钥（AES-GCM V2）
│   ├── machine_id.json            ← 机器绑定ID
│   ├── ai_config.json.enc         ← AI模型配置（加密）
│   ├── projects_config.json       ← 项目列表索引
│   └── ai_recent_files.json       ← AI最近文件记录
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

> **三区分离设计**：系统(`config/`)、单点(`single/`)、项目(`projects/`)，三层物理隔离，`single/` 与项目内子目录结构同构，复用同一套脚本逻辑。

## 路径管理API

| 函数 | 用途 | 示例 |
|------|------|------|
| `get_app_dir()` | EXE所在目录根路径 | `D:\工具\` |
| `get_config_dir()` | 系统配置子目录 | `D:\工具\config\` |
| `get_single_dir()` | 单点运维子目录 | `D:\工具\single\` |
| `get_config_path(filename)` | 相对于EXE根目录的路径 | `D:\工具\config\ai_config.json.enc` |
| `resource_path(relative)` | 打包内嵌资源 | `_MEIPASS/scripts/` |

## 旧数据自动迁移

程序启动时 `ensure_dirs()` 检测旧版散落文件（EXE同级的 `ai_config.json.enc`、`projects_config.json`、`single_devices.json.enc`、`config_backup/`、`output/`、`report/` 等），自动迁移至新结构的三区对应位置。