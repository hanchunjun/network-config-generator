# Changelog

所有重要版本变更记录于此，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 格式。

## [0.3.1] - 2026-05-22

### Added
- 📜 **批量命令生成器** `src/ui/batch_cmd_generator_page.py`：命令模板 + %a~%e多参数占位 + zip同步循环 + 模板管理（12预置+用户模板）
- 导航栏扩展至7个模块：Ctrl+1~Ctrl+7，新增命令生成（试用模式下也开放使用）
- 高DPI缩放支持：`Qt.AA_EnableHighDpiScaling` + `AA_UseHighDpiPixmaps`
- 多屏幕自适应窗口：4档分辨率断点（≥2560/≥1920/≥1366/<1366）

### Changed
- 全部22个UI文件 `font-size` 从 `px` 转换为 `pt` 单位，适配DPI缩放
- 试用模式文案更新：开放「锐捷接入交换机配置」+「批量命令生成」两个基础功能
- 激活弹窗文案更新：补充批量命令生成功能说明
- 批量命令生成器模板路径迁移至 `config/cmd_templates.json`
- 批量命令生成器默认值调整：base=1, loop=4, repeat=1, cmd_count=12

### Fixed
- 🐛 批量命令生成器参数循环bug：从笛卡尔积改为zip同步循环模式
- 🐛 EXE 启动崩溃：`chardet` 从 7.4.3 降级至 4.0.0（纯Python），修复 ACCESS VIOLATION
- 🐛 预置模板内容修正：接口模板补全完整接口名（如 `GigabitEthernet 0/%a`）
- 🐛 预置模板DHCP：使用正确的DNS服务器地址

### Packaging
- `NetworkConfigGenerator.spec` 扩展排除列表，移除 tensorflow/torch/pandas 等非必要依赖
- 用户端EXE重新打包：48.5MB

---

## [0.2.1] - 2026-05-20

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

## [0.2.0] - 2026-05-19

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

## [0.1.0] - 2026-05-18

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

## [0.0.9] - 2026-05-17

### Added
- 基础六菜单框架
- 四厂商四类设备可视化配置脚本生成
- AES-GCM加密体系
- 安全加固9项 + 性能优化4项
- 测试框架35个用例（已随架构升级废弃）
