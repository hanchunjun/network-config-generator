# NetOps V0.4.2 — 项目总纲

## 开发规则

1. 代码遵循 `.claude/rules/00-karpathy-guidelines.md`
2. 工程化遵循 `.claude/rules/09-engineering-workflow.md`（每次改动+打包按流程执行）
3. **界面遵循根目录 `DESIGN.md`**，禁止主观发挥（色彩/字体/按钮/间距/圆角/交互）
4. `C:\Users\Administrator\.claude\CLAUDE.md` 为全局底层规范

## 项目

政企级全流程闭环网络自动化运维桌面工具。PyQt5 + Python 3.11，四厂商（锐捷/华为/H3C/思科）全系列设备。PyInstaller 单EXE打包 + Inno Setup/自解压安装包。

## 技术栈

Python 3.11 · PyQt5 · AES-GCM加密 · PyInstaller打包 · DPI三层控制(96dpi固定) · Inno Setup安装包

## 七大模块

| # | 模块 | 核心 |
|---|------|------|
| 1 | 新建项目 | 项目CRUD + 卡片总览 |
| 2 | 项目运维 | 批量备份/巡检/故障核查 + AI合规诊断 |
| 3 | 单点运维 | 5Tab全链条（巡检/备份/报告/诊断/审计）|
| 4 | 专家工作站 | 3Tab AI分析 + Agent快捷指令 |
| 5 | 设备配置 | 四厂商四设备配置脚本生成 |
| 6 | 命令生成 | 命令模板 + %a~%f参数 |
| 7 | 模型设置 | AI多模型管理 + 加密存储 |

## 关键约束

1. DPI：`app_factory.py` 统一入口，96dpi固定渲染
2. QThread：必须存为实例变量 `self._xxx_thread`
3. AI配置：用 `get_active_ai_config()`，不直接读文件
4. 路径：用 `get_app_dir()` / `get_config_path()` / `ensure_dirs()`，禁止硬编码
5. 主题：`ThemeEngine.get().current_theme`，禁止硬编码色值，按钮统一调用 `ThemeEngine.qss()`
6. 危险操作：必须确认对话框
7. 文件写入：`.tmp` + `os.replace` 原子操作
8. 日志：`logger`，禁止 `print()`
9. 试用模式：未激活仅开放锐捷接入交换机和命令生成

## Logo 与图标（V0.4.2）

| 项目 | 内容 |
|------|------|
| 文字 | "Net"（华文行楷 STXINGKA.TTF） |
| 背景 | 深海蓝 → 科技蓝 竖向渐变 |
| ICO | `assets/netops.ico`（6帧：16/32/48/64/128/256） |
| 预览 | `assets/netops_preview.png` |
| 生成脚本 | `scripts/generate_icon.py`（可复用，支持 `--preview`） |

## 按钮规范（V0.4.2）

> 详见 DESIGN.md §4.1

**统一灰色边框风格**：所有按钮默认灰色边框+灰色文字，hover 时才显示对应颜色。

| 级别 | 方法 | 默认边框 | hover 边框 | 用途 |
|------|------|---------|-----------|------|
| `btn_primary` | 灰色边框+灰色文字 | `border_deep` | `primary`（蓝） | 主操作（生成/保存/创建）|
| `btn_default` | 灰色边框+灰色文字 | `border_deep` | `text_secondary` | 辅助（清空/刷新/导出）|
| `btn_danger` | 灰色边框+灰色文字 | `border_deep` | `danger`（红） | 破坏性（删除/移除）|

**使用方式**：
```python
t = ThemeEngine.get().current_theme
btn.setStyleSheet(t['qss']('btn_primary'))
```

**注意**：禁止在页面级 setStyleSheet 中覆盖 QPushButton 默认样式，应使用 ThemeEngine.qss() 或针对单个按钮设置。

## 目录结构

```
NetOps/
├── main.py              # 主入口
├── admin_tool_main.py   # 管理员制码入口
├── DESIGN.md            # 界面规范（唯一标准）
├── NetworkConfigGenerator.spec  # 打包配置
├── src/
│   ├── core/            # 引擎层（激活/加密/主题/审计/诊断）
│   ├── ui/              # 界面层（7大页面 + 弹窗 + 16配置页）
│   └── utils/           # 工具层（路径/文件/验证/DPI工厂）
├── assets/              # 图标与图片资源
│   ├── netops.ico       # 程序图标（6帧，行书"Net"）
│   └── netops_preview.png
├── agents/              # AI Agent提示词
├── scripts/             # 运维脚本 + 打包/检查/图标生成
├── installer/           # 安装包构建
│   ├── NetOps_Setup.iss # Inno Setup 脚本
│   ├── build_setup.py   # 自解压安装包构建脚本
│   ├── install.py       # Python GUI 安装程序
│   └── NetOps_Setup_0.4.0.exe  # 安装包输出
├── tests/               # 单元测试
└── dist/                # 打包输出
```

## 交付物

| EXE | 路径 | 说明 |
|-----|------|------|
| NetOps.exe | `dist/NetOps.exe` | 用户端主程序 |
| NetOps_Setup_0.4.0.exe | `installer/NetOps_Setup_0.4.0.exe` | 安装包（双击安装） |
| AdminKeyGenTool.exe | `dist/AdminKeyGenTool.exe` | 管理员制码（不外发）|