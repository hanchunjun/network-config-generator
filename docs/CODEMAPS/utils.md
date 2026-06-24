# 工具层代码地图

**最后更新：** 2026-05-30
**项目版本：** V0.4.3

---

```
src/utils/
├── resource_path.py     # 路径管理（最核心，被所有模块依赖）
├── validators.py        # 数据验证器
└── file_operators.py    # 文件操作
```

---

## resource_path.py — 路径管理（⚠️ 最核心）

**职责：** 管理EXE运行时所有路径。**所有文件操作必须通过此模块获取路径，禁止硬编码。**

### 核心API

| 函数 | 返回值 | 说明 |
|------|--------|------|
| `get_app_dir()` | EXE所在目录 | 如 `D:\工具\` |
| `get_config_dir()` | `{app}/config/` | 系统配置目录 |
| `get_single_dir()` | `{app}/single/` | 单点运维数据目录 |
| `get_config_path(filename)` | `{app}/{filename}` | 相对于EXE根的路径 |
| `resource_path(relative)` | 打包内嵌资源路径 | 开发时用 `_MEIPASS` |
| `ensure_dirs()` | None | 启动时创建所有必要目录 + 旧数据迁移 |

### 目录结构（ensure_dirs 创建）
```
EXE所在目录/
├── config/                          ← get_config_dir()
│   ├── key_info.json
│   ├── machine_id.json
│   ├── ai_config.json.enc
│   ├── projects_config.json
│   └── ai_recent_files.json
├── logs/
├── single/                          ← get_single_dir()
│   ├── single_devices.json.enc
│   ├── config_backup/
│   ├── output/single_exception/
│   └── report/
│       ├── single_inspect/
│       ├── compliance/
│       └── diagnosis/
└── projects/
    └── 01_项目名称/
        ├── config/device_list.txt
        ├── config_backup/
        ├── output/
        └── report/
```

### 旧数据迁移
首次启动时自动将散落在EXE根目录的旧文件迁移到新结构：
- `ai_config.json.enc` → `config/`
- `projects_config.json` → `config/`
- `single_devices.json.enc` → `single/`
- `config_backup/` → `single/`
- `output/` → `single/`
- `report/` → `single/`

---

## validators.py — 数据验证器

**职责：** 统一的数据合法性验证。

### 验证函数
| 函数 | 验证内容 |
|------|---------|
| `validate_ip(ip)` | IP地址格式、范围、保留地址 |
| `validate_device(device)` | 厂商、类型、参数合法性 |
| `validate_project_name(name)` | 项目名称格式 |
| `sanitize_command(cmd)` | 命令注入防护（特殊字符过滤） |

---

## file_operators.py — 文件操作

**职责：** 安全的文件读写操作（原子操作防损坏）。

### 核心类
| 类 | 说明 |
|------|------|
| `AtomicFileWriter` | 原子文件写入（`.tmp` + `os.replace`，防损坏） |
| `JSONFileManager` | JSON文件读写（原子操作） |
| `DeviceListParser` | 设备列表文件解析 |
| `DeviceFileManager` | 设备文件管理（device_list.txt读写） |

### 关键方法
| 方法 | 说明 |
|------|------|
| `AtomicFileWriter(path)` | 上下文管理器，原子写入任意文本文件 |
| `JSONFileManager.load_json(path, default)` | 安全读取JSON |
| `JSONFileManager.save_json(path, data)` | 原子写入JSON |
| `DeviceListParser.parse(path)` | 解析device_list.txt |
| `DeviceFileManager.load(project_path)` | 加载设备清单 |
| `DeviceFileManager.save(project_path, devices)` | 保存设备清单 |
