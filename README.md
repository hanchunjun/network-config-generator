# 网络设备配置脚本生成工具

## 项目简介

网络设备配置脚本生成工具是一款面向网络工程师的多厂商设备配置脚本生成工具，支持锐捷、华为、华三、思科等设备命令生成。

## 功能特点

- 支持多厂商设备配置：锐捷、华为、华三、思科
- 支持多种设备类型：接入交换机、核心交换机、路由器、AC
- 可视化配置界面，操作简单直观
- 自动生成配置脚本，提高工作效率
- 支持常见网络配置场景：VLAN、端口聚合、路由配置等

## 技术栈

- Python 3.11+
- PyQt5：用于创建图形用户界面
- PyInstaller：用于打包成可执行文件

## 安装说明

### 方法一：直接使用可执行文件

1. 从 `dist` 目录下载 `NetworkConfigTool.exe`
2. 双击运行即可，无需安装Python环境

### 方法二：从源码运行

1. 克隆仓库：
   ```bash
   git clone https://github.com/hanchunjun/network-config-generator.git
   cd network-config-generator
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行程序：
   ```bash
   python main.py
   ```

## 使用指南

1. 运行程序后，在顶部选择栏选择厂商和设备类型
2. 在配置页面中填写相关配置信息
3. 点击"生成配置"按钮，生成配置脚本
4. 点击"复制到剪贴板"按钮，将配置脚本复制到剪贴板
5. 将配置脚本粘贴到设备命令行中执行

## 项目结构

```
network-config-generator/
├── src/             # 源代码目录
│   ├── core/        # 核心功能模块
│   ├── ui/          # 界面模块
│   └── utils/       # 工具类
├── assets/          # 资源文件
├── docs/            # 文档
├── dist/            # 打包输出目录
├── README.md        # 项目说明
├── LICENSE          # 许可证
├── .gitignore       # Git忽略文件
├── DEV.md           # 开发文档
├── CHANGELOG.md     # 版本记录
├── main.py          # 入口文件
├── requirements.txt # 依赖管理
└── NetworkConfigTool.spec # 打包配置
```

## 贡献指南

欢迎贡献代码和提出问题！请按照以下步骤：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 免责声明

本软件为开源免费工具，仅供学习交流与工程实施使用。
不代表任何厂商官方立场，无任何官方认证。

## 联系方式

- 开源项目地址：[https://github.com/hanchunjun/network-config-generator](https://github.com/hanchunjun/network-config-generator)
- 作者：laohan
