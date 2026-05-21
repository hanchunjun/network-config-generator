# 开发实施步骤 & 打包规范（V0.2.0）

## 开发实施步骤

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
- **规格文件：** NetworkConfigGenerator.spec
- **优化参数：** 包含所有依赖，单文件输出

## 打包包含

- **原有源码：** 全量源文件
- **新增模块：** 日志系统、验证器、密钥管理、文件操作、本地审计引擎
- **公共脚本：** backup_all_config.py, network_inspect.py, run_trouble_cmd.py
- **AI Agent：** agents/network-config-reviewer.md, agents/network-troubleshooter.md
- **第三方依赖：** PyQt5, cryptography, Netmiko, Paramiko, requests 等

## 输出产物

- **位置：** `dist/NetworkConfigGenerator.exe`
- **格式：** 单文件绿色EXE
- **大小：** 约48.7MB

## 运行环境

- **操作系统：** Windows 10/11
- **Python：** 3.11（已打包）
- **依赖：** 全部内嵌，无需额外安装
- **启动时间：** 3-5秒

## 数据存储

- **系统配置：** config/ 目录（含 projects_config.json、key_info.json、ai_config.json.enc、ai_recent_files.json）
- **设备清单：** projects/目录内各项目的 config/device_list.txt
- **日志文件：** logs/netops_*.log
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

# 全量导入链验证
python -c "from src.ui.main_window import MainWindow; print('OK')"

# 打包生成EXE
pyinstaller NetworkConfigGenerator.spec --noconfirm
```

## 版本信息

- **版本：** NetOps V0.2.0（架构升级版）
- **日期：** 2026年5月19日
- **升级：** 三页面重构 + AI三层架构 + 命名体系统一 + 文件管理标准化
- **状态：** 已完成，可商用交付