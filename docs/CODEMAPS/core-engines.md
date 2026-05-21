# 核心引擎代码地图

**最后更新：** 2026-05-21

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
└── admin_keygen.py              # 管理员制码核心 ⭐V0.3.0新增
```

---

## activation_engine.py — 激活核心引擎（V0.3.0新增）

**职责：** 设备绑定激活的完整生命周期管理：机器码生成、激活码生成/校验、AES-GCM加密授权存储、180天黑名单静默校验。

### 核心算法
| 算法 | 说明 |
|------|------|
| 机器码 | CPU序列号 + 硬盘物理序列号 → MD5 → 32位大写 |
| 激活码 | 机器码 + 内置私钥 → MD5 → 前16位大写 |
| 授权存储 | AES-GCM加密 → `config/license.dat` |

### 关键方法
| 方法 | 说明 |
|------|------|
| `get_machine_code()` | 采集硬件信息生成唯一机器码 |
| `generate_activation_code(machine_code)` | 根据机器码生成激活码（管理员端使用） |
| `verify_activation_code(code)` | 校验激活码是否匹配本机 |
| `save_license(machine_code)` | AES-GCM加密存储授权文件 |
| `load_license()` | 解密读取授权文件 |
| `check_activation()` | 检查本地激活状态 |
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

**职责：** 管理员制码工具的后端逻辑：激活码生成、台账记录、黑名单管理。

### 关键方法
| 方法 | 说明 |
|------|------|
| `generate_code_for_machine(machine_code)` | 为指定机器码生成激活码 |
| `save_record(machine_code, activation_code, note)` | 保存授权台账记录 |
| `load_records()` | 加载所有台账记录 |
| `add_to_blacklist(machine_code, reason)` | 添加机器码到黑名单 |
| `remove_from_blacklist(machine_code)` | 从黑名单移除 |
| `load_blacklist()` | 加载本地黑名单 |
| `export_blacklist_for_upload()` | 导出黑名单（用于上传云端） |

### 数据文件
| 文件 | 用途 |
|------|------|
| `config/admin_records.json` | 授权台账记录 |
| `config/blacklist_local.txt` | 本地黑名单 |

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
