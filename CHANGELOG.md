# Changelog

所有重要版本变更记录于此，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 格式。

## [V0.3.6] - 2026-05-26

### Added
- 🪟 **Windows 原生标题栏深色模式**：VS Code/Raycast 主题下通过 `DwmSetWindowAttribute` API 自动设置深色标题栏，Business 主题恢复浅色
- 🎨 **输入框边框色优化**：新增 `input_border` 颜色键，QLineEdit/QComboBox 未聚焦边框在深色主题下自动提亮（VS Code `#5A5A62`、Raycast `#6B6B73`，对比度提升 30%）
- 🎯 **默认主题改为 Business**：首次启动默认使用商务沉稳主题，后续启动恢复用户上次选择

### Changed
- 修复导航栏主题切换不刷新问题：导航栏控件（nav_bar/logo_label/account_btn/about_btn）保存为实例变量，`_refresh_nav_style()` 直接引用刷新，消除不可靠的 `find_children` 查找
- 修复配置选择栏背景不刷新问题：`_refresh_config_bar_style()` 新增 `self._config_top_bar` 背景色刷新
- 全局 QSS 中 QLineEdit/QComboBox 边框改用 `input_border`，27 个 UI 文件局部 QSS 同步更新
- 新增规则文件 `.claude/rules/12-qss-theme-signal-spec.md` 坑 5（导航栏控件必须保存实例变量）和坑 6（Windows 标题栏深色模式）

### Packaging
- 用户端 EXE 重新打包（48.7MB）

---

## [V0.3.5] - 2026-05-25

### Added
- 🎨 **三主题切换系统**：
  - 新增 `src/core/theme_engine.py` — 主题引擎（单例模式），管理三套完整配色方案（每套60+颜色变量），支持 `theme_changed` 信号广播、QSS动态生成、配置持久化（`config/theme_config.json`）
  - 新增 `src/ui/theme_switcher_page.py` — 主题切换面板，三个主题预览卡片（QPainter自定义绘制），点击即时切换全局主题
  - 三套主题：**VSCode**（深蓝黑/直角/技术感）、**Raycast**（紫橙渐变/毛玻璃/大圆角）、**Business**（浅灰白/品牌蓝/政企风）
  - 主题配置自动持久化，重启后恢复上次选择

### Changed
- 全局重构：所有UI页面（main_window/login_dialog/activation_dialog/account_manager_dialog/batch_cmd_generator_page）的硬编码QSS色值全部替换为 `ThemeEngine` 动态颜色引用
- `NetworkConfigGenerator.spec` 新增 `theme_engine` / `theme_switcher_page` hiddenimports，输出文件名改为 `NetOps.exe`
- EXE输出文件名从 `NetworkConfigGenerator.exe` 统一改为 `NetOps.exe`

### Packaging
- 用户端EXE重命名为 `dist/NetOps.exe`（48.6MB）

---

## [V0.3.3] - 2026-05-22

### Added
- 🔐 **软件登录认证 + 账户管理**：
  - 程序启动强制弹出登录窗口，身份核验通过方可进入主界面
  - 内置默认账户（admin/admin），首次运行自动生成
  - 密码采用 AES-GCM 加密存储，杜绝明文泄露
  - 密码复杂度校验：≥8位，必须同时包含大写字母、小写字母、阿拉伯数字
  - 导航栏「关于」旁新增「账户管理」入口，支持修改用户名和密码
  - 新增 `src/core/account_manager.py`（账户管理核心逻辑）
  - 新增 `src/ui/login_dialog.py`（登录弹窗）
  - 新增 `src/ui/account_manager_dialog.py`（账户管理弹窗）

### Changed
- `main.py` 启动链：DPI设置 → 激活校验 → **登录认证** → 主窗口
- `NetworkConfigGenerator.spec` 新增 `account_manager` / `login_dialog` / `account_manager_dialog` hiddenimports

### Tests
- 新增 `tests/core/test_account_manager.py`（31个测试用例，全通过）

---

## [2.2.0] - 2026-05-22

### Added
- 🌐 **子网掩码计算器** `src/ui/subnet_calculator_page.py`：IP/掩码实时计算 + 二进制位对照 + 子网划分详情表
- 📜 **批量命令生成器** `src/ui/batch_cmd_generator_page.py`：命令模板 + %a~%e多参数占位 + 循环/步进/重复模式 + 预置模板
- 导航栏扩展至8个模块：Ctrl+1~Ctrl+8，新增子网计算、命令生成（试用模式下也开放使用）

### Changed
- 项目管理页UI布局压缩：合并项目切换/信息框，压缩上部组件高度，最大化设备清单区域
- 主窗口默认几何调整：1200×780
- 激活弹窗「稍后再说」按钮视觉醒目化（蓝色底色）
- 试用模式提示文案优化：明确告知仅「锐捷接入交换机」可免激活使用
- 激活弹窗窗口尺寸三重锁定，防止移动时高度变化

### Fixed
- 🐛 EXE 启动崩溃：`chardet` 从 7.4.3 降级至 4.0.0（纯Python，去除 mypyc .pyd），修复 ACCESS VIOLATION
- 🐛 `subnet_calculator_page.py` 遗漏 `QAbstractItemView` 导入导致运行时 NameError

### Packaging
- `NetworkConfigGenerator.spec` 扩展排除列表，移除 tensorflow/torch/pandas 等非必要依赖

---

## [2.1.0] - 2026-05-20

### Added
- 双层AI分析架构：本地规则引擎预检 → 精简摘要 + 精准上下文 → AI精审
- 精准上下文提取 `extract_relevant_context()`：根据异常位置提取周边上下文，替代全文发送
- 全局异常钩子 `sys.excepthook` + `logs/crash.log`：未捕获异常自动写入崩溃日志
- Qt消息处理器：捕获Qt内部警告输出
- 代码地图体系：`docs/CODEMAPS/` 8个索引文件
- 依赖版本锁定：`requirements.txt` 完整冻结

### Fixed
- `glob` 模块未定义（NameError）：`import glob as glob_mod` 但调用处仍用 `glob.glob()`，导致AI诊断完成后回调崩溃
- `_on_diagnose_finished` 单try块连锁崩溃：每个UI操作步骤独立try/except保护
- AI返回HTTP 200但JSON结构异常时线程崩溃：改为降级输出本地诊断结果
- Qt消息处理器签名错误：5参数修正为3参数

### Changed
- Agent文件精简：reviewer 11.7KB→1.9KB（-84%），troubleshooter 14.2KB→2.3KB（-84%）
- Token消耗大幅降低：合规审计 -73%，故障诊断 -96%

### Security
- 加固所有AI回调异常处理，防止崩溃导致UI状态不一致

---

## [2.0.0] - 2026-05-19

### Added
- 运维工具箱重构为「项目运维」：3任务卡片 + 4Tab + AI嵌入 + 文件三件套
- AI分析页重定义为「专家工作站」：3Tab + Agent快捷指令 + 可编辑Prompt + 多文件
- 新建项目页升级「项目总览」：卡片网格 + 状态灯🟢🟡🔴 + 全局统计
- AI能力三层架构：嵌入式按钮 → Agent快捷指令 → 自由对话
- 双层审计架构（本地预检 + AI精审）
- 文件管理三件套统一标准（🔄刷新/📂打开/🗑删除）

### Changed
- 导航改名：运维工具箱→项目运维 / 单点巡检→单点运维 / AI分析→专家工作站
- 三区分离架构：`config/`（系统配置）+ `single/`（单点运维）+ `projects/`（项目数据）

---

## [1.0.0] - 2026-05-18

### Added
- 全面路径便携化改造，所有数据跟随EXE
- AI模型多配置管理（新增/删除/重命名/切换/加密）
- AI配置加密存储（SecureConfigFile + AES-GCM）
- 单点设备测试连接按钮（Ping + SSH/Telnet 双验证）
- 日志系统跟随EXE

### Fixed
- 巡检设备类型映射
- 单点巡检报告保存路径
- `key_manager.py` Path导入缺失

---

## [0.9.0] - 2026-05-17

### Added
- 基础六菜单框架
- 四厂商四类设备可视化配置脚本生成
- AES-GCM加密体系
- 安全加固9项 + 性能优化4项
- 测试框架35个用例（已随架构升级废弃）
