# 架构代码地图

**最后更新：** 2026-05-30
**项目版本：** V0.4.1

---

## 分层架构

项目采用**三层单向依赖**架构，严格禁止反向依赖：

```
第三层：UI页面层（src/ui/）
         │
         ▼ 依赖
第二层：业务逻辑层（src/core/）
         │
         ▼ 依赖
第一层：工具层（src/utils/）
         │
         ▼ 依赖
标准库 + 第三方库
```

---

## 模块依赖关系

### 工具层（src/utils/）— 无内部依赖

| 模块 | 职责 | 被谁依赖 |
|------|------|---------|
| `resource_path.py` | EXE路径管理、目录创建、旧数据迁移 | **所有模块**（最底层基础） |
| `validators.py` | IP/设备/项目数据验证 | `device_manager`, `project_manager_page`, `ops_toolbox_page` |
| `file_operators.py` | JSON文件读写、设备列表解析 | `device_manager`, `project_manager_page`, `ops_toolbox_page` |

### 业务逻辑层（src/core/）— 仅依赖 utils/

| 模块 | 职责 | 被谁依赖 |
|------|------|---------|
| `logger.py` | 日志系统（写入EXE同级logs/） | `crypto_utils`, `config_generator`, `device_manager` |
| `key_manager.py` | AES-GCM密钥管理（V2版本，机器ID绑定） | `crypto_utils`, `secure_config` |
| `crypto_utils.py` | 加密/解密工具 | `device_manager` |
| `secure_config.py` | 加密配置文件读写（单例） | `system_settings_page`, `single_device_page` |
| `config_generator.py` | 四厂商配置脚本生成器 | `config_pages/*/`（16个配置页面） |
| `device_manager.py` | 设备CRUD、清单管理 | `project_manager_page`, `device_form_dialog` |
| `local_audit_engine.py` | 本地合规规则引擎（双层审计预检层） | `ops_toolbox_page`, `single_device_page`, `ai_analysis_page` |
| `local_diagnostic_engine.py` | 本地运行时诊断引擎（异常提取+精准上下文） | `ops_toolbox_page`, `single_device_page`, `ai_analysis_page` |
| `account_manager.py` | 账户管理核心（读写/校验/加密/复杂度校验） ★V0.3.3新增 | `login_dialog`, `account_manager_dialog` |
| `theme_engine.py` | 主题引擎（单例/三主题/60+色彩/QSS/持久化） ★V0.3.5新增 | `main_window`, `login_dialog`, `activation_dialog`, `account_manager_dialog`, `batch_cmd_generator_page` |

### UI页面层（src/ui/）— 依赖 core/ 和 utils/

| 模块 | 职责 | 导航名称 |
|------|------|---------|
| `main_window.py` | 主窗口、导航栏、7页面切换、账户管理按钮 | — |
| `project_manager_page.py` | 项目CRUD + 卡片总览 + 全局统计 | 📁 新建项目 |
| `ops_toolbox_page.py` | 3任务卡片 + 4Tab + AI嵌入 | 🔧 项目运维 |
| `single_device_page.py` | 5Tab全链条 + 测试连接 + AI分析 | 🔍 单点运维 |
| `ai_analysis_page.py` | 3Tab + Agent快捷指令 + 多文件 | 🤖 专家工作站 |
| `system_settings_page.py` | AI模型多配置管理 + 加密存储 | ⚙ 模型设置 |
| `config_pages/*/` | 四厂商四设备类型配置生成 | 🖥 设备配置 |
| `device_form_dialog.py` | 设备表单弹窗 | 对话框 |
| `device_discovery_dialog.py` | 设备发现弹窗 | 对话框 |
| `device_template_dialog.py` | 设备模板弹窗 | 对话框 |
| `history_dialog.py` | 历史记录弹窗 | 对话框 |
| `security_dialogs.py` | 安全确认弹窗（导出/删除/查看密码） | 对话框 |
| `login_dialog.py` | 登录弹窗（无关闭按钮/禁止ESC） ★V0.3.3新增 | 对话框 |
| `account_manager_dialog.py` | 账户管理弹窗（修改用户名/密码） ★V0.3.3新增 | 对话框 |
| `subnet_calculator_page.py` | 子网掩码计算器 ★V0.3.1新增 | 🔢 子网计算（试用模式开放） |
| `batch_cmd_generator_page.py` | 批量命令生成器 ★V0.3.1新增 | 📜 命令生成（试用模式开放） |
| `theme_switcher_page.py` | 主题切换面板（QPainter预览卡片） ★V0.3.5新增 | 🎨 主题切换 |

### 业务脚本层（scripts/）— 相对独立

| 模块 | 职责 |
|------|------|
| `backup_all_config.py` | SSH批量配置备份 |
| `network_inspect.py` | 全网自动化巡检 |
| `run_trouble_cmd.py` | 故障设备二次核查 |

### AI Agent层（agents/）

| 模块 | 职责 | 调用方 |
|------|------|--------|
| `network-config-reviewer.md` | 配置合规审计系统提示词 | 所有AI合规巡检按钮 |
| `network-troubleshooter.md` | OSI分层故障诊断提示词 | 所有AI故障诊断按钮 |

### 打包配置层

| 模块 | 职责 |
|------|------|
| `app.manifest` | Windows DPI清单（dpiAwareness:unaware），通过 spec 内嵌EXE |
| `NetworkConfigGenerator.spec` | 用户端PyInstaller打包规格（输出 `NetOps.exe`） |
| `admin_tool.spec` | 管理员工具PyInstaller打包规格 |

---

## 关键依赖路径

### 启动链路
```
main.py → SetProcessDpiAwareness(0) [DPI Unaware声明]
  → QApplication.setAttribute(AA_UseHighDpiPixmaps)
  → _check_activation() [激活校验]
  → LoginDialog [登录认证，V0.3.3新增]
  → QApplication → ThemeEngine.get() [主题引擎初始化，V0.3.5新增]
  → MainWindow.__init__()
  → ensure_dirs() [创建目录结构]
  → _load_current_project() [加载当前项目]
  → 初始化7个UI页面
```

### AI诊断链路（单点运维）
```
用户点击[🩺AI故障诊断]
  → single_device_page._run_ai_diagnostic()
    → 读取文件内容
    → 获取AI配置 get_active_ai_config()
    → 创建 AIDiagnosticThread
      → Layer1: LocalDiagnosticEngine.diagnose() [本地预检]
      → Layer2: HTTP POST → AI API [AI精审]
    → finished_signal → _on_diagnose_finished()
      → 保存报告 → 刷新列表 → 切换Tab → 恢复按钮
    → error_signal → _on_diagnose_error()
      → 日志 + 恢复按钮 + 弹窗提示
```

### AI诊断链路（项目运维）
```
用户点击[🩺AI故障诊断]
  → ops_toolbox_page.FileResultTab._run_diagnose()
    → 读取文件内容
    → 获取AI配置
    → 创建 OpsDiagnosticThread
      → Layer1: LocalDiagnosticEngine.diagnose()
      → Layer2: HTTP POST → AI API
    → finished_signal → _on_diagnose_done()
    → error_signal → _on_diagnose_error()
```

### AI诊断链路（专家工作站）
```
用户点击[🩺一键故障诊断] 或 [💬自由对话]
  → ai_analysis_page._run_expert_analysis()
    → 收集文件内容
    → 获取AI配置
    → 创建 ExpertAnalysisThread
      → Layer1: _run_local_pre_check() [本地预检]
      → Layer2: HTTP POST → AI API（携带精简摘要+精准上下文）
    → finished_signal → _on_expert_finished()
    → error_signal → _on_expert_error()
```

---

## 跨模块共享依赖

以下模块被多个页面共同依赖，修改时需注意影响范围：

| 共享模块 | 被哪些页面使用 | 影响范围 |
|----------|--------------|---------|
| `system_settings_page.get_active_ai_config()` | ops_toolbox_page, single_device_page, ai_analysis_page | ⚠️ 高 |
| `resource_path.get_app_dir()` | 几乎所有模块 | ⚠️ 高 |
| `resource_path.get_single_dir()` | single_device_page, ai_analysis_page | 中 |
| `local_audit_engine` | ops_toolbox_page, single_device_page, ai_analysis_page | ⚠️ 高 |
| `local_diagnostic_engine` | ops_toolbox_page, single_device_page, ai_analysis_page | ⚠️ 高 |
| `theme_engine` | main_window, login_dialog, activation_dialog, account_manager_dialog, batch_cmd_generator_page | ⚠️ 高 |
