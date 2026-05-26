# 版本更新历史（V0.0.9 ~ V0.3.7）

> 本文件收纳 CLAUDE.md 版本更新历史章节。
> 每次重大改动在 `CHANGELOG.md` 对应版本下追加条目，格式遵循 Keep a Changelog。

## V0.3.7 性能优化版（2026-05-26）

- ✅ **QSS 主题缓存**：`theme_engine.py` 全局 QSS 和组件 QSS 分别缓存，主题切换不再重复生成 250 行 f-string
- ✅ **配置生成缓存修复**：修复 `_get_config_cache_key()` 从未定义导致的 `AttributeError`，统一改用 `functools.lru_cache(maxsize=128)`
- ✅ **批量命令生成热循环优化**：进度标签每 100 条更新一次，`str.replace()` 替换为预编译 `re.sub()`，10 万条命令从 ~20s 降至 ~2s
- ✅ **SSH 备份/巡检并发化**：`backup_all_config.py` 和 `network_inspect.py` 改用 `ThreadPoolExecutor`，多设备提速 5~10 倍
- ✅ **启动阶段 WMIC 去重**：`main.py` 和 `main_window.py` 共享 `machine_code`，从 4 次 WMIC 降至 1 次（节省 400~600ms）
- ✅ **死依赖清理**：移除 `bcrypt`，注释 `openpyxl`，PyQt5 子模块排除 14 个，EXE 体积减小 10~15MB
- ✅ 全量 362 个测试用例通过，pre-commit 32/32 全绿

## V0.3.6 主题增强版（2026-05-26）

- ✅ **Windows 原生标题栏深色模式**：通过 `DwmSetWindowAttribute` API 实现 VS Code/Raycast 主题下标题栏自动变深色，Business 主题恢复浅色
- ✅ **导航栏主题切换刷新修复**：将导航栏控件（Logo、按钮、账户管理/关于）保存为实例变量，`_refresh_nav_style()` 直接引用刷新，消除不可靠的 `findChildren` 查找
- ✅ **配置选择栏背景刷新**：`_refresh_config_bar_style()` 新增 `self._config_top_bar` 背景色刷新
- ✅ **输入框边框色优化**：新增 `input_border` 颜色键，VS Code 主题下未聚焦输入框边框从 `#3E3E42` 提升至 `#5A5A62`（对比度 +30%），Raycast 从 `#52525B` 提升至 `#6B6B73`
- ✅ **默认主题改为 Business**：首次启动默认使用商务沉稳主题，后续启动恢复用户上次选择
- ✅ 全局 QSS 输入框边框改用 `input_border`，27 个 UI 文件局部 QSS 同步更新
- ✅ 全量 362 个测试用例通过，EXE 重新打包（48.7MB）

## V0.3.5 三主题版（2026-05-25）

- ✅ **三主题切换系统**：新增 `src/core/theme_engine.py`（主题引擎单例）+ `src/ui/theme_switcher_page.py`（主题切换面板）
- ✅ **三套主题**：VSCode（深蓝黑/直角/技术感）、Raycast（紫橙渐变/毛玻璃/大圆角）、Business（浅灰白/品牌蓝/政企风）
- ✅ **全局动态主题**：所有UI页面硬编码色值全部替换为 ThemeEngine 动态引用，主题切换即时生效
- ✅ **主题配置持久化**：自动保存至 `config/theme_config.json`，重启后恢复
- ✅ **EXE重命名**：输出文件名从 `NetworkConfigGenerator.exe` 改为 `NetOps.exe`
- ✅ 新增 `theme_engine` / `theme_switcher_page` hiddenimports

## V0.3.3 登录认证版（2026-05-22）

- ✅ **软件登录认证**：程序启动强制弹出登录窗口，身份核验通过方可进入主界面，拦截非法访问
- ✅ **内置默认账户**：首次运行自动生成 `config/account.json`，默认账户 admin/admin
- ✅ **密码加密存储**：复用 AES-256-GCM 加密体系，密码密文存储，杜绝明文泄露
- ✅ **密码复杂度校验**：修改密码时强制要求 ≥8位且同时包含大写字母、小写字母、阿拉伯数字
- ✅ **账户管理入口**：导航栏「关于」旁新增「账户管理」按钮，支持修改用户名和密码
- ✅ 新增 `src/core/account_manager.py`（账户管理核心逻辑）
- ✅ 新增 `src/ui/login_dialog.py`（登录弹窗，无关闭按钮/禁止ESC）
- ✅ 新增 `src/ui/account_manager_dialog.py`（账户管理弹窗）
- ✅ 新增 `tests/core/test_account_manager.py`（31个测试用例，全通过）
- ✅ 全量341个测试用例通过，核心模块覆盖率84.10%
- ✅ EXE重新打包：`dist/NetworkConfigGenerator.exe`（48.6MB）

## V0.3.2 DPI适配 + 命令生成器重构（2026-05-22）

- ✅ **DPI全方案修复**：`main.py` 新增 `SetProcessDpiAwareness(0)` + 新建 `app.manifest`（dpiAwareness:unaware）+ `spec` manifest参数内嵌，三层控制确保100%/125%/150%布局稳定
- ✅ **批量命令生成器重构**：互斥双模式（固定重复/差异化生成），`loop_count` 统一驱动，双向联动 CheckBox，模式提示标签
- ✅ **模板管理按钮改造**：下拉菜单→4个彩色平铺按钮（新增蓝/重命名橙/保存绿/删除灰黑）
- ✅ **激活弹窗文案优化**：去掉硬编码 `\n` 换行

## V0.3.1 工具增强版（2026-05-22）

- ✅ 新增 📜 **批量命令生成器** `src/ui/batch_cmd_generator_page.py`（命令模板 + %a~%e多参数占位 + 循环/步进/重复 + 预置模板）
- ✅ 导航栏扩展至7个模块：`Ctrl+1`~`Ctrl+7`（命令生成在试用模式下也开放）
- ✅ 主窗口快捷键更新，`main_window.py` MODULES 列表扩展
- ✅ 项目管理页UI布局优化：合并项目切换/信息框，压缩高度，最大化设备清单区域
- ✅ 激活弹窗窗口尺寸三重锁定（`setFixedSize` + `Minimum/MaximumSize` + `MSWindowsFixedSizeDialogHint`），防止移动时高度变化
- ✅ 「稍后再说」按钮视觉醒目化（蓝色底色突出显示）
- ✅ 试用模式提示文案更新：明确告知仅「锐捷接入交换机」可免激活使用
- ✅ 主窗口默认几何调整为 **1200×780**，改善窗口比例
- 🐛 修复 EXE 崩溃：`chardet` 7.4.3（含 mypyc .pyd 文件）降级至 4.0.0（纯 Python），修复启动时 ACCESS VIOLATION
- 📦 `NetworkConfigGenerator.spec` 扩展排除列表，移除 tensorflow/torch/pandas 等非必要依赖

## V0.3.0 激活体系版（2026-05-21）

- ✅ 新增软件激活三套方案完整体系（方案A纯离线/方案B 180天黑名单/方案C管理员制码工具）
- ✅ 新增激活核心引擎 `src/core/activation_engine.py`（机器码/激活码/授权存储/黑名单校验）
- ✅ 新增用户激活弹窗 `src/ui/activation_dialog.py`（无跳过/无试用入口，试用模式下可「稍后再说」关闭）
- ✅ 新增管理员制码工具 `src/ui/admin_tool_window.py` + `src/core/admin_keygen.py`
- ✅ 新增管理员工具独立入口 `admin_tool_main.py` + 打包规格 `admin_tool.spec`
- ✅ 新增管理员工具打包脚本 `scripts/build_admin_tool.py`
- ✅ 修改 `main.py` 启动强制校验 + `main_window.py` 版本号
- ✅ 新增规则文件 `.claude/rules/08-activation-plan.md`
- ✅ 新增测试文件 `tests/core/test_activation_engine.py`（36个测试用例）
- ✅ 全量305个测试用例通过，核心模块覆盖率83.43%
- ✅ 用户端EXE打包：`dist/NetworkConfigGenerator.exe`（47.1MB）
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.2MB）

## V0.3.0 试用模式版（2026-05-21）

- ✅ **试用模式**：未激活用户进入主窗口，仅开放「锐捷接入交换机配置」功能
- ✅ 修改 `main.py`：未激活不退出，改为进入试用模式
- ✅ 修改 `main_window.py`：添加 `_trial_mode` 状态检测 + 导航拦截 + 配置页限制
- ✅ 新增 `_show_trial_prompt()` 弹窗：提示联系老韩（QQ:223518 / WeChat:tachlaohan）
- ✅ 新增 `_open_activation_dialog()`：关于对话框中试用模式可主动激活
- ✅ 窗口标题显示「[试用模式]」标识
- ✅ 关于对话框版本号动态显示「V0.3.0 试用版」
- ✅ 全量305个测试用例通过
- ✅ 用户端EXE打包：`dist/NetworkConfigGenerator.exe`（47.1MB）
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.3MB）

## V0.3.0 激活增强版（2026-05-21）

- ✅ **有效期扩展**：管理员工具有效期选项扩展为10档（永久/5年/10年/3年/2年/1年/半年/季度/月度/周度）
- ✅ **剩余天数显示**：`check_activation()` 返回3元组，含 `days_remaining`/`is_permanent`/`expire_at`
- ✅ **导航栏激活按钮**：实时显示剩余天数（✅永久激活/✅剩XXX天/🔓未激活），颜色编码（绿/橙/红）
- ✅ **授权详情弹窗**：点击已激活按钮弹出详细信息（激活时间、到期时间、剩余天数、到期预警）
- ✅ **管理员工具窗口自适应**：启动时自动设为屏幕可用区域80%宽高并居中显示
- ✅ 修改 `activation_engine.py`：`save_license()` 支持 `validity_days`，`check_activation()` 返回详细授权信息
- ✅ 修改 `admin_tool_window.py`：有效期10档 + 窗口80%屏幕居中
- ✅ 修改 `main_window.py`：激活按钮显示剩余天数 + 颜色编码 + 详情弹窗
- ✅ 全量306个测试用例通过
- ✅ 管理员工具EXE打包：`dist/AdminKeyGenTool.exe`（41.3MB）

## V0.3.0 Bug修复版（2026-05-21）

- ✅ **激活码升级为18位**：16位基础码 + 2位hex有效期索引（如 `F1637109D2A857DE05`，`05`=1年），彻底修复有期限激活显示"永久激活"的bug
- ✅ **激活弹窗支持18位输入**：`maxLength` 从16改为18，校验支持16位（旧格式/永久）和18位（含有效期）
- ✅ **修复 `admin_tool_window.py` 导入错误**：`encode_activation_code` 从 `activation_engine` 导入，消除 `ImportError`
- ✅ **消除双重编码**：`_on_generate()` 直接传 `validity_days` 给 `generate_code_for_machine()`，不再手动编码
- ✅ **试用模式激活弹窗可关闭**：增加「稍后再说」按钮，允许用户关闭弹窗返回试用主窗口
- ✅ **激活弹窗窗口尺寸三重锁定**：`setFixedSize` + `setMinimumSize/setMaximumSize` + `setSizePolicy(Fixed)`，防止移动时高度变化
- ✅ **统一文案**：所有文件中「天技老韩」改为「老韩」（共17处）
- ✅ 全量310个测试用例通过，核心模块覆盖率≥80%
- ✅ 两个EXE重新打包：用户端47.1MB + 管理员工具41.3MB

## V0.2.1 AI精审优化版（2026-05-20）

- ✅ **双层AI分析架构**：本地规则引擎预检 → 精简摘要 + 精准上下文 → AI精审
- ✅ **精准上下文提取**：`extract_relevant_context()` 精确子串匹配 + 行数上限保护
- ✅ **Agent文件精简**：reviewer 11.7KB→1.9KB，troubleshooter 14.2KB→2.3KB
- ✅ **Token消耗大幅降低**：合规审计 -73%，故障诊断 -96%
- ✅ **关键词匹配修复**：从模糊拆词匹配改为精确行匹配，避免大文件全文发送
- ✅ **spec文件补全**：新增 `local_diagnostic_engine` hiddenimport

## V0.2.1 目录架构优化版（2026-05-19）

- ✅ 三区分离架构：系统配置(`config/`) + 单点数据(`single/`) + 项目数据(`projects/`)，顶层仅保留EXE
- ✅ 单点运维数据全量归入 `single/` 子目录，与项目内部结构复用同一套脚本逻辑
- ✅ 系统配置文件（加密配置/项目索引/最近文件）统一归入 `config/` 子目录
- ✅ 修复 `_get_single_report_dir()` 和 `save_err_log()` Frozen模式忽略项目上下文BUG
- ✅ 补齐项目创建 `PROJECT_SUBDIRS`（含 report/single_inspect、diagnosis、compliance）
- ✅ 单点端报告命名统一（compliance_{ts}.md / diagnosis_{ts}.md）
- ✅ 旧数据自动迁移：首次启动自动将散落文件迁移至新结构
- ✅ 新增 `get_single_dir()` / `get_config_dir()` API

## V0.2.0 架构升级版（2026-05-19）

- ✅ 运维工具箱重构为「项目运维」任务中心（3任务卡片 + 4Tab + AI嵌入 + 文件三件套）
- ✅ AI分析页重定义为「专家工作站」（3Tab + Agent快捷指令 + 可编辑Prompt + 多文件）
- ✅ 新建项目页升级「项目总览」（卡片网格 + 状态灯🟢🟡🔴 + 全局统计）
- ✅ 导航改名：「运维工具箱→项目运维」「单点巡检→单点运维」「AI分析→专家工作站」
- ✅ AI能力三层架构正式落地（嵌入式按钮 → Agent快捷指令 → 自由对话）
- ✅ 文件管理三件套统一标准（🔄刷新/📂打开/🗑删除）
- ✅ 双层审计架构（本地预检 + AI精审）
- ✅ 合规审计报告全中文化

## V0.1.0 便携化版（2026-05-18）

- 全面路径便携化改造，所有数据跟随EXE
- AI模型多配置管理（新增/删除/重命名/切换/加密）
- 单点设备增强（测试连接按钮 + 备份修复）
- 巡检功能修复（设备类型映射 + 报告保存）
- 日志系统跟随EXE
- 修复 key_manager.py Path 导入缺失问题

## V0.0.9 初始版（2026-05-17）

- 基础六菜单框架搭建
- 四厂商配置脚本集成
- AES-GCM加密体系搭建
- 安全加固9项 + 性能优化4项
- 测试框架232个用例
