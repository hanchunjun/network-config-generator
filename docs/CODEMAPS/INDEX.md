# NetOps 代码地图索引

**最后更新：** 2026-05-30
**项目版本：** V0.4.3 Logo 设计与安装包版
**技术栈：** Python 3.11 + PyQt5 + AES-GCM

---

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (入口)                         │
│    SetProcessDpiAwareness(0) → app.manifest unaware     │
│    → _check_activation() [激活校验]                       │
│    → LoginDialog [登录认证]                               │
│              sys.exit(app.exec_())                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              src/ui/main_window.py (主窗口)               │
│         QStackedWidget + 顶部导航栏 + 7页面切换            │
└───┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┘
    │      │      │      │      │      │      │
    ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌──────────┐
│ 新建  ││ 项目  ││ 单点  ││ 专家  ││  设备  ││ 命令  ││   模型   │
│ 项目  ││ 运维  ││ 运维  ││ 工作站 ││  配置  ││ 生成  ││   设置   │
│ Page  ││ Page  ││ Page  ││ Page  ││Pages×16││ Page  ││   Page   │
└───┬───┘└───┬───┘└───┬───┘└───┬───┘└───┬───┘└───┬───┘└────┬────┘
    │        │        │        │        │       │        │
    └────────┴────────┴────────┴────────┴───────┴────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    src/core/ (业务逻辑层)                  │
│  local_audit_engine │ local_diagnostic_engine │ activation_engine │
│  admin_keygen │ account_manager │ key_mgr │ secure_config │ crypto_utils │ device_manager │ logger │ theme_engine │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    src/utils/ (工具层)                     │
│       resource_path │ validators │ file_operators │ theme_engine │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              打包配置 & 平台适配                          │
│  app.manifest (DPI unaware) │ NetworkConfigGenerator.spec → NetOps.exe │
└─────────────────────────────────────────────────────────┘
```

---

## 代码地图文件清单

| 文件 | 内容 | 适用场景 |
|------|------|---------|
| [INDEX.md](INDEX.md) | 总索引 + 架构总览 | 快速了解项目全貌 |
| [architecture.md](architecture.md) | 三层架构 + 模块依赖关系 | 理解代码分层和调用链 |
| [ui-pages.md](ui-pages.md) | 7大UI页面 + 16个配置页面 + 登录/激活/管理员工具页面 | 定位UI相关代码 |
| [core-engines.md](core-engines.md) | AI双引擎 + 安全加密 + 设备管理 + 账户管理 | 定位业务逻辑代码 |
| [utils.md](utils.md) | 路径管理 + 验证器 + 文件操作 | 定位工具函数代码 |
| [ai-agents.md](ai-agents.md) | Agent提示词 + AI三层架构 | 定位AI相关代码 |
| [data-flow.md](data-flow.md) | 五区分离 + 数据流转 + 加密存储 | 理解数据存储和流转 |
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

0. **启动链**：DPI设置 → 激活校验 → 登录认证 → 主窗口，四步顺序执行，任一失败不进入下一步
1. **三层单向依赖**：`utils/` → `core/` → `ui/`，禁止反向依赖
2. **路径管理**：所有文件路径必须通过 `src/utils/resource_path.py` 获取，禁止硬编码
3. **QThread约束**：所有QThread子类必须保存为实例变量（`self._xxx_thread = thread`）
4. **项目隔离**：多项目数据物理隔离，禁止跨项目操作
5. **安全红线**：自动化仅允许只读指令，绝不修改设备配置
6. **双EXE隔离**：用户端与管理员工具独立打包，管理员工具严禁外发
7. **登录认证**：V0.3.3新增，程序启动在激活校验通过后执行登录认证，登录成功才加载主窗口；账户数据存于 `config/account.json`（用户名明文+密码AES-GCM密文）
8. **三主题系统**：V0.3.5新增，ThemeEngine单例引擎管理三套配色（VSCode/Raycast/Business），所有UI页面动态引用 `t['xxx']` 色值，主题切换即时生效并持久化至 `config/theme_config.json`
9. **Windows标题栏深色模式**：V0.3.6新增，通过 `DwmSetWindowAttribute(hwnd, 20, ...)` API 实现 VS Code/Raycast 主题下标题栏自动变深色
10. **输入框边框色**：V0.3.6新增 `input_border` 颜色键，QLineEdit/QComboBox 未聚焦边框使用 `t['input_border']`（比普通 `border` 更亮，深色主题对比度 +30%）
11. **导航栏主题刷新**：V0.3.6修复，导航栏控件必须保存为实例变量（`self._nav_bar`/`self._logo_label` 等），禁止在 `_refresh_xxx_style()` 中使用 `findChildren` 查找
