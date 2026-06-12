# 开发实施步骤 & 打包规范（V0.4.2）

## 开发实施步骤

### V0.4.2 Logo 设计与安装包（2026年5月30日）

1. **Logo 设计**：新增 `assets/netops.ico` — 华文行楷 "Net" 字样 + 深海蓝→科技蓝渐变背景 + 四角光点科技装饰
2. **图标生成脚本**：新增 `scripts/generate_icon.py` — 从 TTF 字体渲染多尺寸 ICO（16/32/48/64/128/256），支持 `--preview` 参数生成预览图
3. **安装包构建**：新增 `installer/build_setup.py` — 自解压安装包构建脚本，将 `dist/NetOps/` 打包为带图标的 `NetOps_Setup_0.4.0.exe`
4. **ICO 文件结构**：6帧（16/32/48/64/128用DIB 24bpp，256用PNG压缩），总大小 80.4 KB
5. **打包流程更新**：`pyinstaller NetworkConfigGenerator.spec` → `python installer/build_setup.py` → 生成安装包

### V0.3.6 主题增强（2026年5月26日）

1. **Windows 原生标题栏深色模式**：`main_window.py` 新增 `_update_native_title_bar()`，通过 `DwmSetWindowAttribute(hwnd, 20, ...)` API 设置 VS Code/Raycast 主题为深色标题栏，Business 主题为浅色标题栏
2. **导航栏主题切换刷新修复**：将导航栏控件保存为实例变量（`self._nav_bar`/`self._logo_label`/`self._account_btn`/`self._about_btn`），`_refresh_nav_style()` 直接引用刷新
3. **配置选择栏背景刷新**：`_refresh_config_bar_style()` 新增 `self._config_top_bar` 背景色刷新
4. **输入框边框色优化**：主题引擎新增 `input_border` 颜色键，全局 QSS 和 27 个 UI 文件局部 QSS 中 QLineEdit/QComboBox 边框从 `t['border']` 改为 `t['input_border']`，VS Code 主题对比度提升 30%
5. **默认主题改为 Business**：`theme_engine.py` 中 `Theme.BUSINESS` 作为首次启动默认主题

### V0.3.5 三主题切换系统（2026年5月25日）

1. **主题引擎核心**：新增 `src/core/theme_engine.py` — 单例模式，管理浅色商务风格配色方案，`apply()` 全局QSS设置，配置持久化至 `config/theme_config.json`
2. **全局UI重构**：main_window/login_dialog/activation_dialog/account_manager_dialog/batch_cmd_generator_page 全部硬编码QSS色值替换为 `t['xxx']` 动态引用
3. **spec更新**：新增 `theme_engine` hiddenimports，输出文件名改为 `NetOps.exe`

### V0.3.3 登录认证 + 账户管理（2026年5月22日）

1. **账户管理核心**：新增 `src/core/account_manager.py` — 账户读写/校验/加密/复杂度校验/损坏恢复，复用 AES-256-GCM 加密体系
2. **登录弹窗**：新增 `src/ui/login_dialog.py` — 模态登录窗口，无关闭按钮/禁止ESC，启动链插入激活校验之后
3. **账户管理弹窗**：新增 `src/ui/account_manager_dialog.py` — 修改用户名和密码，密码复杂度校验
4. **导航栏账户管理按钮**：`main_window.py` 新增「账户管理」按钮，位于「关于」左侧
5. **启动链更新**：`main.py` 启动链改为 DPI → 激活校验 → 登录认证 → 主窗口
6. **测试覆盖**：新增 `tests/core/test_account_manager.py`（31个测试用例，全通过）
7. **spec更新**：`NetworkConfigGenerator.spec` 新增 account_manager/login_dialog/account_manager_dialog hiddenimports

### V0.3.2 DPI适配 + 命令生成器重构（2026年5月22日）

1. **DPI全方案修复**：`main.py` 新增 `SetProcessDpiAwareness(0)` + 新建 `app.manifest`（dpiAwareness:unaware）+ `spec` manifest参数内嵌，三层控制确保100%/125%/150%布局稳定
2. **批量命令生成器重构**：互斥双模式（固定重复/差异化生成），`loop_count` 统一驱动，双向联动 CheckBox，模式提示标签
3. **模板管理按钮改造**：下拉菜单→4个彩色平铺按钮（新增蓝/重命名橙/保存绿/删除灰黑）
4. **激活弹窗文案优化**：去掉硬编码 `\n` 换行

### V0.3.1 工具增强（2026年5月22日）

1. **批量命令生成器新增**：`src/ui/batch_cmd_generator_page.py` — 命令模板 + %a~%e参数 + 批量生成 + 预置模板
2. **导航栏扩展至7模块**：Ctrl+1~7
3. **项目管理页UI优化**：合并项目切换/信息框，压缩高度
4. **chardet降级修复**：7.4.3→4.0.0，修复ACCESS VIOLATION崩溃

### V0.3.0 激活体系（2026年5月21日）

1. **激活核心引擎**：`src/core/activation_engine.py` — 机器码生成、激活码生成/校验、AES-GCM加密授权存储、180天黑名单静默校验
2. **管理员制码核心**：`src/core/admin_keygen.py` — 激活码生成、台账记录、黑名单管理
3. **用户激活弹窗**：`src/ui/activation_dialog.py` — 无关闭/无跳过/无试用，严格按定稿文案
4. **管理员制码工具UI**：`src/ui/admin_tool_window.py` — 独立窗口，台账+黑名单快捷管理
5. **管理员工具入口**：`admin_tool_main.py` + `admin_tool.spec` — 独立EXE打包
6. **启动强制校验**：修改 `main.py`，激活校验最高优先级，未激活不加载业务模块
7. **测试覆盖**：`tests/core/test_activation_engine.py` — 36个用例，全部通过

### V0.2.0 架构升级（2026年5月19日）

1. **运维工具箱重构**：3面板→公共项目选择器+3任务卡片+4Tab(备份/报告/诊断/合规)+左右分栏+AI按钮
2. **AI分析页重定义**：旧双面板→左文件管理+右3Tab(自由对话/合规审计/故障诊断)+Agent快捷指令
3. **新建项目页升级**：新增项目总览区(卡片网格+状态灯🟢🟡🔴+全局统计)
4. **导航改名**：运维工具箱→项目运维 / 单点巡检→单点运维 / AI分析→专家工作站
5. **文件管理统一**：所有文件列表统一 [🔄刷新][📂打开][🗑删除] 三件套标准
6. **AI三层架构落地**：嵌入式→Agent快捷指令→自由对话，全量覆盖

### V0.1.0 已完成优化（2026年5月17-18日）

1. **主窗口框架**：顶部菜单框架按固定顺序布局搭建
2. **新建项目模块**：目录生成、项目切换、设备清单编辑
3. **设备配置模块**：保留原有逻辑，添加配置缓存和验证
4. **单点运维模块**：独立UI与业务逻辑，5Tab全链条
5. **AI智能分析**：规则加载、模型调用、报告生成落地
6. **系统设置模块**：AI配置界面、读写持久化、连通测试
7. **全局数据隔离**：项目绑定、路径读写、禁止跨项目操作
8. **全流程联调**：异常捕获、归档校验、日志记录
9. **整体封装**：所有依赖封装，输出单EXE

### 安全特性

1. **密钥管理系统**：V0.2版本，动态派生，支持自动迁移
2. **加密工具增强**：AES-GCM算法，多版本兼容
3. **输入验证器**：IP、设备、项目统一验证
4. **安全确认对话框**：导出、删除、查看密码确认
5. **原子文件操作**：防止数据损坏
6. **日志系统**：详细的操作审计记录
7. **激活体系安全**：设备绑定+启动强制校验+加密授权存储+权限隔离

### 性能优化

1. **配置缓存机制**：LRU缓存，128条目
2. **批量VLAN优化**：范围压缩，减少循环
3. **字符串处理优化**：join替代+=，减少内存分配
4. **表格操作优化**：减少UI组件访问

### QThread关键约束

```python
# ✅ 正确：QThread必须保存为实例变量，防止GC回收
self._ai_inspect_thread = thread
self._ai_diagnose_thread = thread
self._ai_compliance_thread = thread

# ❌ 错误：局部变量会被GC回收，导致运行中线程崩溃
thread = SomeThread(...)
thread.start()
```

---

# 打包规范

## 打包工具

- **工具：** PyInstaller 6.0.0
- **用户端规格文件：** `NetworkConfigGenerator.spec`（输出名 `NetOps.exe`）
- **管理员工具规格文件：** `admin_tool.spec`
- **优化参数：** 包含所有依赖，单文件输出

## 打包包含

- **原有源码：** 全量源文件
- **新增模块：** 日志系统、验证器、密钥管理、文件操作、本地审计引擎
- **激活体系（V0.3.0新增）：** activation_engine, admin_keygen, activation_dialog, admin_tool_window
- **DPI适配（V0.3.2新增）：** app.manifest（dpiAwareness:unaware，通过 spec 内嵌EXE）
- **公共脚本：** backup_all_config.py, network_inspect.py, run_trouble_cmd.py, build_admin_tool.py
- **AI Agent：** agents/network-config-reviewer.md, agents/network-troubleshooter.md
- **第三方依赖：** PyQt5, cryptography, Netmiko, Paramiko, requests 等

## 输出产物（两个独立EXE）

| EXE | 位置 | 大小 | 用途 |
|-----|------|------|------|
| 用户端主程序 | `dist/NetOps.exe` | 48.6MB | 用户日常使用，含激活校验+登录认证+三主题 |
| 管理员制码工具 | `dist/AdminKeyGenTool.exe` | 41.2MB | 管理员专用，生成激活码/管理黑名单 |

## 运行环境

- **操作系统：** Windows 10/11
- **Python：** 3.11（已打包）
- **依赖：** 全部内嵌，无需额外安装
- **启动时间：** 3-5秒

## 数据存储

- **系统配置：** config/ 目录（含 projects_config.json、key_info.json、ai_config.json.enc、ai_recent_files.json）
- **用户端激活：** activation/ 目录（含 license.dat、bl_check.dat）
- **管理员数据：** admin_data/ 目录（含 records.dat 加密台账、blacklist.txt、backup/ 备份目录）
- **设备清单：** projects/目录内各项目的 config/device_list.txt
- **日志文件：** logs/netops_*.log + logs/crash.log
- **单点输出：** single/config_backup/、single/output/single_exception/、single/report/
- **项目输出：** projects/项目名/output/、projects/项目名/report/、projects/项目名/config_backup/

## 开发与打包命令

```bash
# 运行程序
python main.py

# 安装依赖
pip install PyQt5 cryptography

# 打包前验证（必须通过全部）
python -m py_compile src/ui/ops_toolbox_page.py
python -m py_compile src/ui/ai_analysis_page.py
python -m py_compile src/ui/project_manager_page.py
python -m py_compile src/ui/main_window.py
python -m py_compile src/ui/single_device_page.py
python -m py_compile src/ui/system_settings_page.py
python -m py_compile src/ui/batch_cmd_generator_page.py
python -m py_compile src/core/activation_engine.py
python -m py_compile src/core/admin_keygen.py

# 全量导入链验证
python -c "from src.ui.main_window import MainWindow; print('OK')"
python -c "from src.core.activation_engine import check_activation; print('OK')"

# 打包用户端EXE
pyinstaller NetworkConfigGenerator.spec --noconfirm

# 打包管理员制码工具EXE
pyinstaller admin_tool.spec --noconfirm
```

## 版本信息

- **版本：** NetOps V0.4.2（Logo 设计版）
- **日期：** 2026年5月30日
- **升级：** 华文行楷 Logo + 安装包构建脚本 + ICO 6帧 + 自解压安装包
- **状态：** 已完成，可商用交付
