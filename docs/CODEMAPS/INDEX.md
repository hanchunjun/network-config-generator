# NetOps 代码地图索引

**最后更新：** 2026-05-20
**项目版本：** V0.2.1 AI精审优化版
**技术栈：** Python 3.11 + PyQt5 + AES-GCM

---

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (入口)                         │
│              sys.exit(app.exec_())                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              src/ui/main_window.py (主窗口)               │
│         QStackedWidget + 顶部导航栏 + 6页面切换            │
└───┬──────────┬──────────┬──────────┬──────────┬─────────┘
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────────┐
│ 新建  │ │ 项目  │ │ 单点  │ │ 专家  │ │   设备    │
│ 项目  │ │ 运维  │ │ 运维  │ │ 工作站 │ │   配置    │
│ Page  │ │ Page  │ │ Page  │ │ Page  │ │  Pages×16 │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └─────┬─────┘
    │         │         │         │            │
    └─────────┴─────────┴─────────┴────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    src/core/ (业务逻辑层)                  │
│  local_audit_engine │ local_diagnostic_engine │ key_mgr  │
│  secure_config │ crypto_utils │ device_manager │ logger   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    src/utils/ (工具层)                     │
│       resource_path │ validators │ file_operators         │
└─────────────────────────────────────────────────────────┘
```

---

## 代码地图文件清单

| 文件 | 内容 | 适用场景 |
|------|------|---------|
| [INDEX.md](INDEX.md) | 总索引 + 架构总览 | 快速了解项目全貌 |
| [architecture.md](architecture.md) | 三层架构 + 模块依赖关系 | 理解代码分层和调用链 |
| [ui-pages.md](ui-pages.md) | 6大UI页面 + 16个配置页面 | 定位UI相关代码 |
| [core-engines.md](core-engines.md) | AI双引擎 + 安全 + 设备管理 | 定位业务逻辑代码 |
| [utils.md](utils.md) | 路径管理 + 验证器 + 文件操作 | 定位工具函数代码 |
| [ai-agents.md](ai-agents.md) | Agent提示词 + AI三层架构 | 定位AI相关代码 |
| [data-flow.md](data-flow.md) | 数据流向 + 文件目录结构 | 理解数据存储和流转 |
| [build-deploy.md](build-deploy.md) | 开发命令 + 打包规范 + 部署 | 构建和发布 |

---

## 快速导航

### 按功能查找

| 我要做什么 | 看哪个文件 |
|-----------|-----------|
| 新增一个UI页面 | [ui-pages.md](ui-pages.md) |
| 新增一个AI分析能力 | [ai-agents.md](ai-agents.md) |
| 新增一个配置生成厂商 | [ui-pages.md §配置页面](ui-pages.md) |
| 修改安全加密逻辑 | [core-engines.md §安全](core-engines.md) |
| 修改路径管理 | [utils.md §resource_path](utils.md) |
| 打包发布 | [build-deploy.md](build-deploy.md) |
| 理解整体架构 | [architecture.md](architecture.md) |

### 按角色查找

| 角色 | 先看 |
|------|------|
| 新接手开发者 | INDEX.md → architecture.md → data-flow.md |
| 前端/UI开发者 | ui-pages.md |
| AI功能开发者 | ai-agents.md → core-engines.md |
| 打包/运维 | build-deploy.md |

---

## 关键约定

1. **三层单向依赖**：`utils/` → `core/` → `ui/`，禁止反向依赖
2. **路径管理**：所有文件路径必须通过 `src/utils/resource_path.py` 获取，禁止硬编码
3. **QThread约束**：所有QThread子类必须保存为实例变量（`self._xxx_thread = thread`）
4. **项目隔离**：多项目数据物理隔离，禁止跨项目操作
5. **安全红线**：自动化仅允许只读指令，绝不修改设备配置
