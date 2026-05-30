# 构建与部署代码地图

**最后更新：** 2026-05-30
**项目版本：** V0.4.2 Logo 设计与安装包版

---

## 开发环境

| 项目 | 要求 |
|------|------|
| Python | 3.11+ |
| 操作系统 | Windows 10/11 |
| 关键依赖 | PyQt5, cryptography, netmiko, paramiko, requests, certifi |

---

## 开发命令

```bash
# 运行程序
python main.py

# 安装依赖
pip install PyQt5 cryptography netmiko paramiko requests certifi

# 运行测试（V0.2.1已废弃，待重建）
python -m pytest tests/ -v
```

---

## 打包前验证（必须全部通过）

```bash
# 1. 语法检查
python -m py_compile main.py
python -m py_compile src/ui/main_window.py
python -m py_compile src/ui/ops_toolbox_page.py
python -m py_compile src/ui/single_device_page.py
python -m py_compile src/ui/ai_analysis_page.py
python -m py_compile src/ui/project_manager_page.py
python -m py_compile src/ui/subnet_calculator_page.py
python -m py_compile src/ui/batch_cmd_generator_page.py
python -m py_compile src/ui/system_settings_page.py
python -m py_compile src/ui/login_dialog.py
python -m py_compile src/ui/account_manager_dialog.py
python -m py_compile src/core/local_audit_engine.py
python -m py_compile src/core/local_diagnostic_engine.py
python -m py_compile src/core/account_manager.py
python -m py_compile src/utils/resource_path.py

# 2. 导入链验证
python -c "from src.ui.main_window import MainWindow; print('OK')"
python -c "from src.core.local_audit_engine import LocalAuditEngine; print('OK')"
python -c "from src.core.local_diagnostic_engine import LocalDiagnosticEngine; print('OK')"
python -c "from src.ui.subnet_calculator_page import SubnetCalculatorPage; print('OK')"
python -c "from src.ui.batch_cmd_generator_page import BatchCmdGeneratorPage; print('OK')"
python -c "from src.core.account_manager import AccountManager; print('OK')"
python -c "from src.ui.login_dialog import LoginDialog; print('OK')"
python -c "from src.ui.account_manager_dialog import AccountManagerDialog; print('OK')"

# 3. 类型检查
py -3.11 -m mypy src/utils/ src/core/key_manager.py src/core/secure_config.py src/core/logger.py

# 4. 单元测试
py -3.11 -m pytest tests/ -v

# 5. 安全扫描（排除模板代码固有误报）
py -3.11 -m bandit -r src/ -c bandit.yaml -ll

# 6. 代码复杂度检查（新增方法不超过C级）
py -3.11 -m radon cc src/ -a -nc
```

---

## 打包命令

```bash
# 1. 生成 Logo 图标（首次或修改后执行）
python scripts/generate_icon.py --preview

# 2. 删除旧EXE（如果被占用需先关闭运行的实例）
del dist\NetOps.exe
del dist\AdminKeyGenTool.exe

# 3. 清理构建缓存
rmdir /s /q build\

# 4. 打包用户端EXE
pyinstaller NetworkConfigGenerator.spec --noconfirm

# 5. 打包管理员制码工具EXE
pyinstaller admin_tool.spec --noconfirm

# 6. 构建安装包（自解压 EXE）
python installer/build_setup.py
```

---

## 打包配置

### 用户端（NetworkConfigGenerator.spec）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 入口文件 | `main.py` | 程序入口 |
| 输出文件 | `dist/NetOps.exe` | 单文件EXE |
| 大小 | ~47MB | PyInstaller单文件封装 |
| 控制台 | `console=False` | 无命令行窗口 |
| 数据文件 | `scripts/`, `agents/` | 打包内嵌 |
| **DPI清单** | `manifest='app.manifest'` | ★V0.3.2新增，内嵌EXE |

### DPI缩放适配（V0.3.2）

```
三层控制体系（优先级从高到低）：

1. app.manifest → dpiAwareness: unaware（最高优先级，内嵌EXE）
2. main.py → SetProcessDpiAwareness(0)（进程级API调用）
3. main.py → QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

效果：Windows 全窗口 bitmap 拉伸，100%/125%/150% 缩放下布局完全一致。
125%: 完美锐利 / 150%: 轻微柔化但无溢出
```

### 管理员工具（admin_tool.spec）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 入口文件 | `admin_tool_main.py` | 管理员工具入口 |
| 输出文件 | `dist/AdminKeyGenTool.exe` | 单文件EXE |
| 大小 | ~41MB | PyInstaller单文件封装 |
| 控制台 | `console=False` | 无命令行窗口 |

### 关键隐藏导入（V0.3.3更新）
```
src.core.activation_engine       # 激活核心引擎
src.core.admin_keygen            # 管理员制码核心
src.ui.activation_dialog         # 用户激活弹窗
src.core.local_audit_engine      # 本地合规规则引擎
src.core.local_diagnostic_engine # 本地运行时诊断引擎
src.core.account_manager         # 账户管理核心 ★V0.3.3新增
src.ui.login_dialog              # 登录弹窗 ★V0.3.3新增
src.ui.account_manager_dialog    # 账户管理弹窗 ★V0.3.3新增
src.core.theme_engine            # 主题引擎 ★V0.3.5新增
src.ui.theme_switcher_page       # 主题切换面板 ★V0.3.5新增
cryptography.hazmat.primitives.ciphers.aead
cryptography.hazmat.primitives.kdf.pbkdf2
certifi
```

### 排除列表（V0.3.1扩展）
```
# 排除大型非必要模块以减小EXE体积
excludes=['tensorflow', 'torch', 'pandas', 'scipy',
          'matplotlib', 'PIL', 'cv2', 'nltk', 'spacy',
          'sklearn', 'sqlalchemy', 'jupyter', 'django',
          'flask', 'fastapi', 'plotly', 'sympy', 'seaborn',
          'pygame', 'kivy', 'dash', 'bokeh', 'pyspark']
```

---

## 输出产物（三个独立 EXE + 安装包）

| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| `NetOps.exe` | `dist/NetOps/` | ~48MB | 用户端主程序（含三主题） |
| `AdminKeyGenTool.exe` | `dist/` | ~41MB | 管理员制码工具 |
| `NetOps_Setup_0.4.0.exe` | `installer/` | ~62MB | 安装包（双击安装，含新 Logo） |
| 构建日志 | `build/` | — | 分产品目录存储 |
| 警告日志 | `build/*/warn-*.txt` | — | — |
| 交叉引用 | `build/*/xref-*.html` | — | — |

---

## 部署方式

### 方式1：安装包安装（推荐）
```
双击 installer/NetOps_Setup_0.4.0.exe → 自动安装到 Program Files\NetOps
→ 创建桌面快捷方式 + 开始菜单快捷方式
→ 安装包含行书 "Net" Logo 图标
```

### 方式2：便携运行（免安装）
```
双击 dist/NetOps/NetOps.exe 直接运行
数据跟随 EXE 所在目录（config/projects/single/activation）
```

### 方式3：U盘携带
整个 dist/NetOps/ 文件夹复制到U盘，插上即用

---

## 运行时自动创建的文件

首次启动时 `ensure_dirs()` 自动创建：
```
EXE所在目录/
├── config/              # 系统配置（加密存储）
├── logs/                # 运行日志
├── single/              # 单点运维数据
│   ├── config_backup/
│   ├── output/
│   └── report/
└── projects/            # 项目数据
```

---

## 版本信息

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| V0.4.2 Logo 设计版 | 2026-05-30 | 华文行楷 "Net" Logo + 安装包构建脚本 + ICO 6帧 + 自解压安装包 |
| V0.3.7 性能优化版 | 2026-05-26 | 6项Python针对性优化：WMIC去重 + 配置缓存修复 + 批量命令生成优化 + 死依赖清理 + SSH并发化 + QSS缓存 |
| V0.3.6 主题增强版 | 2026-05-26 | Windows标题栏深色模式 + 导航栏刷新修复 + input_border输入框边框 + 默认主题Business |
| V0.3.5 三主题版 | 2026-05-25 | 三主题切换系统 + ThemeEngine + 全局动态QSS + EXE重命名 NetOps.exe |
| V0.3.3 登录认证版 | 2026-05-22 | 软件登录认证 + 账户管理 + AES-GCM密码加密 + 341测试用例 |
| V0.3.2 DPI适配版 | 2026-05-22 | DPI全方案修复 + 批量命令生成器重构 + 模板管理4按钮 + 激活弹窗文案优化 |
| V0.3.1 工具增强版 | 2026-05-22 | 子网计算器 + 批量命令生成器 + 7模块导航 + chardet修复 |
| V0.3.0 激活体系版 | 2026-05-21 | 三套激活方案 + 双EXE + 启动强制校验 + 180天黑名单 |
| V0.2.1 AI精审优化版 | 2026-05-20 | 双层AI分析 + 精准上下文提取 + Agent文件精简 + Token压缩 |
| V0.2.0 架构升级版 | 2026-05-19 | 三页面重构 + AI三层架构 + 命名体系统一 |
| V0.1.0 便携化版 | 2026-05-18 | 路径便携化 + AI多配置管理 |
| V0.0.9 初始版 | 2026-05-17 | 基础六菜单框架 |
