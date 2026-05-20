# 代码复杂度基线

> 首次扫描时间：2026-05-20
> 工具：radon `cc -a -nc`
> 平均复杂度：**D (26.63)**

---

## 当前高复杂度方法（D级及以上）

### E级（需关注）

| 文件 | 方法 | 行号 | 说明 |
|------|------|------|------|
| `local_diagnostic_engine.py` | `DiagResult.extract_relevant_context` | 97 | 精准上下文提取，多策略匹配逻辑 |
| `local_audit_engine.py` | `AuditResult.extract_relevant_context` | 117 | 同上，审计版本 |
| `ai_analysis_page.py` | `ExpertAnalysisThread.run` | 157 | AI分析线程，多Tab多Agent调度 |
| `local_diagnostic_engine.py` | `_check_threshold_rules` | 455 | 通用阈值规则检查，多规则循环 |

### D级（可接受，暂不重构）

| 文件 | 方法 | 行号 | 说明 |
|------|------|------|------|
| `single_device_page.py` | `AIDiagnosticThread.run` | 626 | AI诊断线程 |
| `single_device_page.py` | `SingleDeviceWorker._do_inspect` | 1012 | 巡检执行 |
| `single_device_page.py` | `ComplianceCheckThread._classify_error` | 314 | 合规错误分类 |
| `single_device_page.py` | `ComplianceCheckThread.run` | 353 | 合规检查线程 |
| `single_device_page.py` | `SingleDeviceWorker._do_backup` | 919 | 备份执行 |
| `single_device_page.py` | `SingleDeviceWorker._do_test_connection` | 1144 | 连接测试 |
| `single_device_page.py` | `SingleDevicePage._style_compliance_report` | 2845 | 合规报告样式 |
| `main_window.py` | `MainWindow.show_config_page` | 536 | 配置页面切换 |
| `project_manager_page.py` | `ProjectManagerPage._refresh_overview` | 1095 | 项目总览刷新 |
| `project_manager_page.py` | `ProjectManagerPage._handle_paste` | 1258 | 粘贴导入处理 |

### F级（配置生成器模板，不重构）

| 文件 | 方法 | 行号 | 说明 |
|------|------|------|------|
| `cisco/access_switch_config.py` | `generate_config` | 1928 | Cisco接入交换机配置生成 |
| `h3c/access_switch_config.py` | `generate_config` | 1943 | H3C接入交换机配置生成 |
| `huawei/access_switch_config.py` | `generate_config` | 1913 | 华为接入交换机配置生成 |
| `ruijie/access_switch_config.py` | `generate_config` | 1980 | 锐捷接入交换机配置生成 |

> **说明**：F级方法为四厂商配置脚本生成器，本质是模板字符串逐行拼接，逻辑上无法拆分。属于项目固有特征。

---

## 监控规则

- 新增方法圈复杂度不得超过 **10**
- 重构目标：E级方法在功能稳定后逐步拆分
- 每次重大改动后重新扫描，对比基线

## 扫描命令

```bash
# 查看C级及以上
py -3.11 -m radon cc src/ -a -nc

# 查看平均复杂度
py -3.11 -m radon cc src/ -a
```
