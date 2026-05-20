# AI Agent 代码地图

**最后更新：** 2026-05-20

---

## AI能力三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  第一层：嵌入式AI按钮（单点运维 / 项目运维）                    │
│  自动绑定上下文 → 一键执行 → 不可编辑Prompt                    │
│  线程：AIDiagnosticThread / OpsDiagnosticThread              │
├─────────────────────────────────────────────────────────────┤
│  第二层：Agent快捷指令（专家工作站专属）                        │
│  手动选文件 → 加载Agent → 可编辑Prompt → 手动发送             │
│  线程：ExpertAnalysisThread                                  │
├─────────────────────────────────────────────────────────────┤
│  第三层：自由对话（专家工作站专属）                             │
│  完全自定义Prompt + 多文件输入 + 多轮迭代                      │
│  线程：ExpertAnalysisThread（tab_key="free"）                │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent 文件

| 文件 | 用途 | 大小 | 调用方 |
|------|------|------|--------|
| `agents/network-config-reviewer.md` | 配置合规审计系统提示词 | ~1.9KB | 所有AI合规巡检 |
| `agents/network-troubleshooter.md` | OSI分层故障诊断提示词 | ~2.3KB | 所有AI故障诊断 |

### reviewer Agent（合规审计）
**定位：** `agents/network-config-reviewer.md`
**职责：** 对设备配置进行等保合规审计
**审计维度：** 密码策略、远程管理、SNMP、日志、接口、ACL、NTP
**输出格式：** 全中文报告 + 分级整改建议

### troubleshooter Agent（故障诊断）
**定位：** `agents/network-troubleshooter.md`
**职责：** OSI分层网络故障诊断
**诊断流程：** 物理层 → 数据链路层 → 网络层 → 传输层 → 应用层
**输出格式：** 根因分析 + 排查命令 + 后续步骤

---

## AI按钮一览

### 单点运维页面
| 按钮 | Tab | Agent | 线程 |
|------|-----|-------|------|
| `[🔍AI合规巡检]` | 配置备份 | reviewer | 内置双层分析 |
| `[🩺AI故障诊断]` | 巡检报告 | troubleshooter | `AIDiagnosticThread` |
| `[🩺AI故障诊断]` | 诊断报告 | troubleshooter | `AIDiagnosticThread` |
| `[🩺AI精审]` | 合规审计 | reviewer（双层） | 内置双层分析 |

### 项目运维页面
| 按钮 | Tab | Agent | 线程 |
|------|-----|-------|------|
| `[🔍AI合规巡检]` | 备份文件 | reviewer | `OpsComplianceThread` |
| `[🩺AI故障诊断]` | 巡检报告 | troubleshooter | `OpsDiagnosticThread` |
| `[🩺AI故障诊断]` | 诊断报告 | troubleshooter | `OpsDiagnosticThread` |
| `[🩺AI精审]` | 合规审计 | reviewer（双层） | `OpsComplianceThread` |

### 专家工作站页面
| 按钮 | Tab | Agent | 线程 |
|------|-----|-------|------|
| `[🔍一键合规巡检]` | 合规审计 | reviewer | `ExpertAnalysisThread` |
| `[🩺一键故障诊断]` | 故障诊断 | troubleshooter | `ExpertAnalysisThread` |
| `💬自由对话` | 自由对话 | 自定义 | `ExpertAnalysisThread` |

---

## 双层AI分析流程

```
用户点击AI按钮
      │
      ▼
Layer 1：本地规则引擎（确定性规则，毫秒级）
  ├─ LocalDiagnosticEngine.diagnose()  [故障诊断]
  │    → CPU/内存/接口/日志检查
  │    → 生成 DiagResult（结构化异常列表）
  │
  ├─ LocalAuditEngine.audit()  [合规审计]
  │    → 密码/SNMP/日志/接口/ACL/NTP检查
  │    → 生成 AuditResult（结构化问题列表）
  │
  ├─ to_ai_prompt_context()  → 精简异常摘要
  └─ extract_relevant_context()  → 精准上下文片段
      │
      ▼
Layer 2：AI大模型（语义分析，深度推理）
  ├─ 仅接收精简摘要 + 异常周边上下文（非全文）
  ├─ 深度根因分析
  ├─ 补充遗漏问题
  └─ OSI分层排查命令
      │
      ▼
输出：双层诊断报告（本地结果 + AI精审）
```

### Token优化效果
| 场景 | 优化前 | 优化后 | 压缩率 |
|------|--------|--------|--------|
| 合规审计 | 18.4KB | 5.0KB | -73% |
| 故障诊断 | 151.6KB | 5.5KB | -96% |

---

## AI配置获取链路

```
模型设置页 → 用户选择模型 → 写入 active_profile
                    ↓
        get_active_ai_config()  ← 单点运维页（3个AI按钮）
                                ← 项目运维页（4个AI按钮）
                                ← 专家工作站（2个Agent按钮 + 自由对话）
```

**注意：** AI配置存储在 `config/ai_config.json.enc`（AES-GCM加密），密钥绑定机器ID。
