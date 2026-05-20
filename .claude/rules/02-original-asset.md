```
# 核心资产、源码目录、开发打包规范

## 基础技术栈
- 开发语言：Python 3.11
- 图形界面框架：PyQt5，沿用原有QStackedWidget页面切换逻辑
- 核心设计模式：面向对象编程 + 工厂模式，模块化配置生成系统
- 安全加密：cryptography (AES-GCM算法)
- 程序入口：main.py，启动逻辑不变

## 核心功能（完整留存并增强）
1. 四大厂商：锐捷、华为、H3C、思科配置脚本生成
2. 四类设备：接入交换机、核心交换机、路由器、无线AC
3. 顶部厂商+设备类型双维度选择，动态加载配置页面
4. 分厂商独立配置页面，可视化参数填写，自动生成合规命令
5. 配置脚本预览、本地导出自定义保存
6. 语法校验、本地运行、单文件打包全流程
7. 遵循PEP 8规范，类型注解完整
8. **新增：** 密钥管理系统（V2版本）
9. **新增：** 安全确认对话框
10. **新增：** 配置缓存机制

## 优化后源码目录结构
```

NetOps项目规整/

├── src/

│   ├── core/
│   │   ├── config_generator.py      # 配置生成器（已优化）
│   │   ├── crypto_utils.py          # 加密工具（新增）
│   │   ├── device_manager.py        # 设备管理（已优化）
│   │   ├── key_manager.py           # 密钥管理（新增）
│   │   └── logger.py                # 日志系统（新增）

│   ├── ui/
│   │   ├── config_pages/
│   │   │   ├── cisco/               # 思科配置
│   │   │   ├── h3c/                 # H3C配置
│   │   │   ├── huawei/              # 华为配置
│   │   │   └── ruijie/              # 锐捷配置
│   │   ├── device_form_dialog.py    # 设备表单（已优化）
│   │   ├── security_dialogs.py      # 安全对话框（新增）
│   │   └── main_window.py           # 主窗口（已优化）

│   ├── utils/
│   │   ├── file_operators.py        # 文件操作（新增）
│   │   ├── resource_path.py         # 资源路径
│   │   └── validators.py            # 验证器（新增）

├── scripts/
│   ├── backup_all_config.py         # 配置备份脚本
│   ├── network_inspect.py           # 网络巡检脚本
│   └── run_trouble_cmd.py           # 故障核查脚本

├── tests/
│   ├── test_security.py             # 安全测试（新增）
│   └── test_functionality.py        # 功能测试（新增）

├── config/                          # 配置文件目录
│   ├── key_info.json               # 密钥信息（自动生成）
│   └── device_list.txt             # 设备清单

├── logs/                           # 日志目录
│   └── netops_*.log               # 运行日志

├── output/                         # 输出目录
│   ├── single_exception/
│   ├── trouble_check_result/
│   └── manual_high_risk_task.txt

├── report/                         # 报告目录
├── dist/                           # 打包输出
│   └── NetworkConfigGenerator.exe  # 可执行文件

├── main.py                         # 程序入口
├── cleanup_project.py              # 清理脚本
├── generate_manual.py              # 手册生成
├── update_manual.py                # 手册更新
└── README.md

```

## 开发与打包指令
```bash
# 运行程序
python main.py

# 安装依赖
pip install PyQt5 cryptography

# 打包生成EXE
pyinstaller NetworkConfigGenerator.spec

# 清理项目
python cleanup_project.py

# 运行测试
python -m pytest tests/ -v
```

## 扩展规范

1. 新增厂商：src/ui/config_pages/ 新建目录，实现四类设备页面
2. 新增设备类型：补齐页面、更新控件、同步配置生成器
3. 代码规范：4 空格缩进、变量函数小写下划线、类名驼峰、强制类型注解
4. 安全规范：配置脚本不含敏感密钥，生成脚本需设备实测验证
5. **新增：** 所有导出操作需要安全确认
6. **新增：** 配置文件原子操作，防止损坏
7. **新增：** 详细的日志记录和审计

## 核心优化说明

### 安全增强
- 密钥从硬编码升级为动态派生（V2版本）
- 所有导出操作增加安全确认对话框
- 输入参数统一验证和清理
- 文件操作使用原子操作防止损坏

### 性能优化
- 配置生成器添加LRU缓存机制
- 批量VLAN生成优化（范围压缩）
- 字符串处理优化（join替代+=）

### 代码质量
- 模块化重构，独立工具模块
- 统一的异常处理和日志记录
- 完整的类型注解和文档注释

### 测试覆盖
- 安全功能测试（15个用例）
- 功能完整性测试（20个用例）
- 边界条件和异常场景测试
