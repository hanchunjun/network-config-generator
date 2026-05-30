# 核心引擎代码地图

**最后更新：** 2026-05-30
**项目版本：** V0.4.1

---

## 目录

```
src/core/
├── logger.py                    # 日志系统
├── key_manager.py               # 密钥管理（V2）
├── crypto_utils.py              # 加密工具
├── secure_config.py             # 加密配置文件读写
├── config_generator.py          # 配置脚本生成器
├── device_manager.py            # 设备管理
├── local_audit_engine.py        # 本地合规规则引擎
├── local_diagnostic_engine.py   # 本地运行时诊断引擎
├── activation_engine.py         # 激活核心引擎 ⭐V0.3.0新增
├── admin_keygen.py              # 管理员制码核心 ⭐V0.3.0新增
├── account_manager.py           # 账户管理核心 ⭐V0.3.3新增
└── theme_engine.py              # 主题引擎 ⭐V0.3.5新增
```

---

## activation_engine.py — 激活核心引擎（V0.3.0新增）

**职责：** 设备绑定激活的完整生命周期管理：机器码生成、激活码生成/校验、AES-GCM加密授权存储（含有效期）、180天黑名单静默校验、剩余天数计算。

### 核心算法
| 算法 | 说明 |
|------|------|
| 机器码 | CPU序列号 + 硬盘物理序列号 → MD5 → 32位大写 |
| 激活码 | 机器码 + 内置私钥 → MD5 → 前16位大写（旧格式） |
| 激活码（新） | 16位基础码 + 2位hex有效期索引 → 18位（如 `F1637109D2A857DE05`） |
| 授权存储 | AES-GCM加密 → `activation/license.dat` |

### 关键方法
| 方法 | 说明 |
|------|------|
| `get_machine_code()` | 采集硬件信息生成唯一机器码 |
| `generate_activation_code(machine_code)` | 根据机器码生成激活码（管理员端使用） |
| `verify_activation_code(code)` | 校验激活码是否匹配本机 |
| `save_license(machine_code, code, validity_days=0)` | AES-GCM加密存储授权文件，支持有效期（0=永久） |
| `load_license()` | 解密读取授权文件 |
| `check_activation()` | 检查本地激活状态，返回3元组(bool, str, dict)，dict含days_remaining/is_permanent/expire_at等 |
| `check_blacklist(machine_code)` | 联网校验云端黑名单 |
| `perform_silent_check()` | 方案B静默校验（联网失败跳过） |
| `is_due_for_check()` | 判断是否到期需要联网校验 |

### 关键常量
| 常量 | 值 |
|------|------|
| 私钥 | `NetOps::Activation::SecretKey::2026` |
| 授权文件 | `config/license.dat` |
| 黑名单URL | `https://raw.githubusercontent.com/hanchunjun/network-config-generator/main/blacklist.txt` |
| 校验周期 | 180天 |

---

## admin_keygen.py — 管理员制码核心（V0.3.0新增）

**职责：** 管理员制码工具的后端逻辑：激活码生成、台账加密存储、备份恢复、黑名单管理。

### 数据存储
| 文件 | 路径 | 说明 |
|------|------|------|
| 授权台账 | `admin_data/records.dat` | AES-GCM加密，仅管理员工具可解密 |
| 本地黑名单 | `admin_data/blacklist.txt` | 每行一个机器码 |
| 台账备份 | `admin_data/backup/records_YYYYMMDD_HHMMSS.dat` | 带时间戳的加密副本 |

### 有效期选项（10档）
| 索引 | 选项 | 天数 |
|------|------|------|
| 0 | 永久 | 0 |
| 1 | 5年 | 1825 |
| 2 | 10年 | 3650 |
| 3 | 3年 | 1095 |
| 4 | 2年 | 730 |
| 5 | 1年 | 365 |
| 6 | 半年（方案B） | 180 |
| 7 | 季度 | 90 |
| 8 | 月度 | 30 |
| 9 | 周度 | 7 |

### 台账记录字段
| 字段 | 说明 |
|------|------|
| `name` | 用户姓名/标识 |
| `machine_code` | 32位机器码 |
| `activation_code` | 16位或18位激活码（18位含有效期编码） |
| `note` | 备注信息 |
| `created_at` | 授权时间（格式：YYYY-MM-DD HH:MM:SS） |
| `validity_days` | 有效期天数，0=永久 |
| `expire_at` | 到期时间（格式：YYYY-MM-DD HH:MM:SS），永久为空 |

### 关键方法
| 方法 | 说明 |
|------|------|
| `generate_code_for_machine(machine_code, validity_days=0)` | 为指定机器码生成18位激活码（含有效期编码） |
| `save_record(name, mc, code, note, validity_days)` | 保存台账记录（加密追加，含有效期，validity_days=0永久） |
| `load_records()` | 加载所有台账记录（自动解密） |
| `format_record_time(iso_str)` | 格式化时间字符串为友好显示 |
| `get_record_expire_status(rec)` | 获取记录有效期状态描述 |
| `delete_record(index)` | 删除指定记录 |
| `backup_records()` | 创建台账备份（带时间戳） |
| `list_backups()` | 列出所有备份文件 |
| `restore_backup(filename)` | 从备份恢复（自动创建安全备份） |
| `export_records_to_json(path)` | 导出台账为明文JSON |
| `import_records_from_json(path, merge)` | 从JSON导入台账（合并/覆盖） |
| `add_to_blacklist(machine_code)` | 添加机器码到黑名单 |
| `remove_from_blacklist(machine_code)` | 从黑名单移除 |
| `load_blacklist()` | 加载本地黑名单 |
| `export_blacklist_for_upload()` | 导出黑名单（用于上传云端） |

---

## local_diagnostic_engine.py — 本地运行时诊断引擎

**职责：** 从巡检报告/日志/配置中提取结构化异常，生成精简摘要 + 精准上下文，供AI精审使用。

### 核心数据结构
```python
DiagSeverity: CRITICAL | HIGH | MEDIUM | LOW
DiagFinding: id, severity, category, title, issue, evidence, layer, suggestion
DiagResult: findings[], source_type, parse_time_ms
```

### 关键方法
| 方法 | 行号 | 说明 |
|------|------|------|
| `diagnose(content, source_type)` | ~520 | 主入口：CPU→内存→接口→日志检查→去重 |
| `to_ai_prompt_context()` | ~80 | 生成AI可用的精简异常摘要 |
| `extract_relevant_context(content, ctx_lines, max_lines)` | ~97 | 精准提取异常周边上下文（替代全文发送） |
| `to_summary_text()` | ~199 | 生成人类可读的摘要 |

### 诊断规则
| 检查项 | 分类 | 阈值 |
|--------|------|------|
| CPU利用率 | cpu | >80%告警 |
| 内存利用率 | memory | >85%告警 |
| 接口状态 | interface | down/error检测 |
| 日志告警 | log | 关键词匹配 |

### 精准上下文提取策略
1. **策略1**：用证据文本整行做精确子串匹配，每证据最多3行
2. **策略2**：精确匹配失败时，取证据中20字符子串匹配，每证据最多2行
3. **降级**：总匹配行数 > 200时，降级为证据摘要

---

## local_audit_engine.py — 本地合规规则引擎

**职责：** 对设备配置进行确定性规则预检，提取合规问题，供AI精审使用。

### 核心数据结构
```python
Severity: CRITICAL | HIGH | MEDIUM | LOW
AuditFinding: id, severity, category, title, issue, matched_line, line_number, suggestion
AuditResult: findings[], audit_time_ms
```

### 关键方法
| 方法 | 行号 | 说明 |
|------|------|------|
| `audit(content, project_name, device_ip)` | — | 主入口：执行所有合规规则检查 |
| `to_ai_prompt_context()` | ~70 | 生成AI可用的精简问题列表 |
| `extract_relevant_context(content, ctx_lines, max_lines)` | ~117 | 精准提取问题配置行周边上下文 |

### 合规检查维度
| 维度 | 说明 |
|------|------|
| 密码策略 | 密码复杂度、加密方式 |
| 远程管理 | SSH/Telnet配置安全性 |
| SNMP | 社区字符串安全性 |
| 日志 | 日志开启状态 |
| 接口 | 未使用接口shutdown |
| ACL | 访问控制列表配置 |
| NTP | 时间同步配置 |

### 精准上下文提取策略
1. **优先**：用 `line_number` 字段精确定位
2. **其次**：用 `matched_line` 文本精确匹配，每问题最多2行
3. **降级**：总匹配行数 > 150时，降级为摘要

---

## key_manager.py — 密钥管理系统（V0.2）

**职责：** AES-GCM密钥的生成、存储、派生和迁移。

### 关键方法
| 方法 | 说明 |
|------|------|
| `get_key()` | 获取当前密钥（自动创建/迁移） |
| `derive_key_from_machine_id()` | 从机器ID派生密钥 |
| `migrate_v1_to_v2()` | V0.1.0→V0.2格式自动迁移 |

### 密钥文件
| 文件 | 用途 |
|------|------|
| `config/key_info.json` | 加密密钥（AES-GCM V0.2） |
| `config/machine_id.json` | 机器绑定ID |

---

## secure_config.py — 加密配置文件读写

**职责：** 使用AES-GCM算法加密存储敏感配置（AI模型配置等）。

### 关键方法
| 方法 | 说明 |
|------|------|
| `load()` | 解密读取配置 |
| `save(config)` | 加密写入配置 |
| `get_instance()` | 获取单例实例 |

### 加密文件
| 文件 | 内容 |
|------|------|
| `config/ai_config.json.enc` | AI模型配置（加密） |

---

## config_generator.py — 配置脚本生成器

**职责：** 为四厂商四类型设备生成开局配置脚本。

### 支持的厂商和类型
| 厂商 | 接入交换机 | 核心交换机 | 路由器 | AC控制器 |
|------|:---:|:---:|:---:|:---:|
| 锐捷 | ✅ | ✅ | ✅ | ✅ |
| 华为 | ✅ | ✅ | ✅ | ✅ |
| H3C | ✅ | ✅ | ✅ | ✅ |
| 思科 | ✅ | ✅ | ✅ | ✅ |

### 关键方法
| 方法 | 说明 |
|------|------|
| `generate(vendor, device_type, params)` | 生成配置脚本 |
| `validate_params(params)` | 参数验证 |
| `preview()` | 预览配置 |

---

## device_manager.py — 设备管理

**职责：** 设备清单的CRUD操作、数据加密存储。

### 关键方法
| 方法 | 说明 |
|------|------|
| `load_devices(project_path)` | 加载设备清单 |
| `save_devices(project_path, devices)` | 保存设备清单 |
| `add_device(project_path, device)` | 添加设备 |
| `remove_device(project_path, ip)` | 删除设备 |
| `encrypt_device_data(data)` | 加密设备数据 |
| `decrypt_device_data(data)` | 解密设备数据 |

---

## account_manager.py — 账户管理核心（V0.3.3新增）

**职责：** 账户数据的读写、密码加密/验证、复杂度校验、首次初始化、损坏恢复。

### 数据存储
| 文件 | 路径 | 说明 |
|------|------|------|
| 账户文件 | `config/account.json` | 用户名明文 + 密码AES-GCM密文（`ENC:`前缀） |

### 关键方法
| 方法 | 说明 |
|------|------|
| `verify_login(username, password)` | 验证用户名和密码，返回bool |
| `verify_password(input_pwd)` | 仅验证密码（用于修改密码时校验旧密码） |
| `change_account(new_username, new_pwd)` | 修改用户名和密码，返回(bool, str) |
| `validate_password_complexity(pwd)` | 静态方法，校验密码复杂度（≥8位，大写+小写+数字） |
| `_load_account()` | 读取账户配置（损坏时自动重置为默认） |
| `_write_account_file(username, encrypted_pwd)` | 原子写入账户文件 |
| `_init_default_account()` | 首次运行初始化默认账户 admin/admin |

### 密码复杂度规则
- 长度 ≥ 8 位
- 必须同时包含大写字母、小写字母、阿拉伯数字
- 仅修改新密码时校验，默认初始密码 admin 不受限制

### 损坏恢复
- JSON解析失败 → 自动重置为默认账户 admin/admin
- 非字典JSON → 自动重置为默认账户 admin/admin

---

## theme_engine.py — 主题引擎（V0.3.5新增，V0.3.6增强，V0.3.7缓存优化）

**职责：** 管理三套完整配色方案，提供全局QSS动态生成、信号广播、配置持久化。

### 核心数据结构
```python
Theme: Dict[str, str]  # 60+颜色变量，如 primary, nav_bg, text_main 等
ThemeEngine: 单例类，_theme_id + _current_theme + _THEMES + theme_changed信号
```

### 三套主题（每套60+颜色变量）
| 主题ID | 名称 | 风格特征 |
|--------|------|---------|
| `vscode` | VSCode Dark | 深蓝黑底，直角，技术感，`#1E1E1E`/`#007ACC` |
| `raycast` | Raycast | 紫橙渐变，毛玻璃，大圆角，`#1A1025`/`#FF6363` |
| `business` | Business | 浅灰白底，品牌蓝，政企风，`#F5F6FA`/`#1565C0` |

### 关键方法
| 方法 | 说明 |
|------|------|
| `get()` | 获取单例实例（自动初始化默认主题） |
| `apply(app, theme_id)` | 应用全局QSS样式表 |
| `qss(component)` | 返回指定组件类型的QSS片段 |
| `status_color(status)` | 返回状态灯颜色（success/warning/danger） |

### 颜色变量体系（部分）
| 变量类别 | 示例变量 |
|---------|---------|
| 品牌色 | `primary`, `primary_light`, `primary_hover`, `primary_pressed` |
| 背景色 | `bg_main`, `card_bg`, `nav_bg`, `input_bg`, `code_bg`, `hover_bg` |
| 文字色 | `text_main`, `text_primary`, `text_secondary`, `text_tertiary` |
| 边框/分割 | `border`, `input_border`（V0.3.6新增，输入框专用，比普通border更亮）, `border_deep`, `border_deepest` |
| 状态色 | `success`, `warning`, `danger`, `info` + 各状态 bg/hover 变体 |
| 圆角 | `radius_sm`, `radius_md`, `radius_lg` |

### 配置持久化
- 存储路径：`config/theme_config.json`
- 格式：`{"theme_id": "business"}`（V0.3.6起默认主题为 business）
- 切换主题时自动保存，启动时自动加载

### V0.3.6 新增颜色变量
| 变量 | 说明 | VS Code | Raycast | Business |
|------|------|---------|---------|----------|
| `input_border` | QLineEdit/QComboBox 未聚焦边框 | `#5A5A62` | `#6B6B73` | `#B0B0B8` |

### V0.3.7 缓存优化
- `_global_qss_cache: Dict[str, str]` — 全局 QSS 缓存，键为 `theme_id`
- `_component_qss_cache: Dict[str, str]` — 组件 QSS 缓存，键为 `component@theme_id`
- `apply()` 切换主题时自动清空缓存，避免旧样式残留

---

## logger.py — 日志系统

**职责：** 统一日志管理，写入EXE同级 `logs/` 目录。

### 关键方法
| 方法 | 说明 |
|------|------|
| `get_logger(name)` | 获取命名日志器 |
| `set_level(level)` | 设置日志级别 |

### 日志文件
| 文件 | 用途 |
|------|------|
| `logs/netops_YYYYMMDD.log` | 主运行日志（按日期分割） |
| `logs/crash.log` | 未捕获异常崩溃日志 |
