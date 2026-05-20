# Changelog

所有重要版本变更记录于此，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 格式。

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
