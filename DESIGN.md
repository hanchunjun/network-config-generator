# NetOps 界面设计规范（V0.3.7 按钮统一边框版）

> **唯一权威标准**：所有界面代码的生成与修改，必须以本文件为唯一标准，禁止任何脱离规范的主观发挥。

---

## 一、项目整体视觉风格概述

NetOps 支持三套 UI 主题一键切换，每套主题拥有独立的配色体系与界面风格：

| 主题 ID | 名称 | 气质定位 | 默认 |
|---------|------|---------|------|
| `vscode` | VS Code 风格 | 深蓝黑 · 锐利 · 开发者工具感 · 长时间不疲劳 | ✅ |
| `raycast` | Raycast 风格 | 紫橙渐变 · 毛玻璃 · 大圆角 · 新锐科技感 | |
| `business` | 商务沉稳风格 | 浅灰白底 · 品牌蓝 · 政企级 · 专业可信 | |

**实现方式**：`src/core/theme_engine.py` 中 `ThemeEngine` 单例管理三套配色数据，通过 `apply(app, theme_id)` 切换全局 QSS，发射 `theme_changed` 信号通知所有组件动态刷新。

**设计关键词**：科技感 · 专业 · 可切换 · 低视觉疲劳

---

## 二、色彩系统

### 2.1 主色（Primary）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#3B7CFF` | 科技蓝 | 主按钮背景、选中态、焦点边框、进度条填充、导航激活态 |
| `#2962D9` | 科技蓝深 | 主按钮 hover 状态 |
| `#1E4BB8` | 科技蓝更深 | 主按钮 pressed 状态 |
| `#4D90FF` | 高亮蓝 | 链接文字、强调文字、状态栏活跃指示、光晕效果色 |
| `#5C8AFF` | 柔光蓝 | 卡片顶部装饰线、Tab 底部选中条、选中态发光边框 |
| `#1A3A6E` | 深蓝选中底 | 导航激活背景、列表选中背景、AI按钮背景 |
| `#1565C0` | 管理员蓝 | 管理员制码工具专属主色（仅 admin_tool_window 使用） |

### 2.2 强调色（Accent）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#00D4E8` | 冰蓝 | 数据流高亮、实时日志关键字、进度条光晕、动态数据指示 |
| `#0F8B6E` | 深青绿 | 设备在线/Ping成功状态灯、连接成功指示（冷暖双色调） |

### 2.3 功能色（Semantic）

> **按钮用色总纲（§4.1）**：禁止用 success/warning/accent 功能色作为按钮背景区分功能。按钮仅分四类：
> - **主按钮**：`primary` 实色背景 + `primary` 边框（主要操作）
> - **次要按钮**：`transparent`/`page_bg` 背景 + `border` 边框（常规操作）
> - **危险按钮**：`transparent`/`page_bg` 背景 + `danger` 边框（删除等破坏性操作）
> - **AI/精审按钮**：`transparent`/`page_bg` 背景 + `primary`/紫色 边框
>
> 功能色仅用于**文字颜色、状态图标、结果背景、进度条**等非按钮背景场景。

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#3DD66A` | 成功绿 | 成功状态图标、已激活状态指示灯、合规通过判定文字、进度条 chunk |
| `#2BA84E` | 成功绿深 | 成功状态 hover |
| `#43A047` | 激活绿 | 试用模式激活指示灯 |
| `#2E7D32` | 深绿 hover | 激活绿 hover |
| `#1F4A2E` | 成功绿背景 | 合规审计通过结果背景（深色底） |
| `#FFB040` | 警告橙 | 进行中状态指示灯、即将过期提示文字、故障状态图标 |
| `#CC8C30` | 警告橙深 | 警告状态 hover |
| `#FA8C16` | 警告橙文字 | 即将过期按钮文字/border |
| `#2A2210` | 警告背景 | 即将过期提示背景、安全提醒框背景（深色底） |
| `#FAAD14` | 金黄 | 提示性文字、状态图标 |
| `#D48806` | 金黄 hover | 金黄 hover |
| `#FF5C5C` | 危险红 | 危险按钮边框/文字、错误状态图标、未激活提示文字、诊断按钮边框 |
| `#CC3E3E` | 危险红深 | 危险按钮 hover |
| `#FF4D4F` | 亮红 | 状态指示灯 |
| `#FF7875` | 亮红 hover | 亮红 hover |
| `#3A1A1A` | 危险红背景 | 不通过审计结果背景（深色底） |
| `#9B6CEF` | 紫色 | AI精审按钮边框 |
| `#7A4FC7` | 深紫 | AI精审按钮 hover |

### 2.4 中性色（Neutral）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#E8ECF1` | 主文字 | 页面标题、表格头部文字、输入框文字、分组框标题 |
| `#B0B8C8` | 正文文字 | 表单标签、副标题、表格内容文字、导航按钮默认文字 |
| `#7A8296` | 辅助文字 | 占位符文字、统计信息、状态栏文字、卡片描述、只读字段 |
| `#4A5266` | 禁用文字 | 禁用状态文字/边框、占位符列表项前景 |
| `#FFFFFF` | 纯白 | 主按钮文字、激活态导航文字、最高层级强调文字 |
| `#2E3648` | 暗边框 | 所有输入框边框、按钮边框、分割线、表格网格线、卡片边框 |
| `#383F50` | 浅暗边框 | 分割线（QFrame HLine）、Tab 未选中边框 |
| `#1A1F2E` | 深空蓝 | 页面背景（QMainWindow）、代码/预览区背景（最深） |
| `#1E2433` | 深蓝灰 | 卡片背景、QGroupBox 背景、内容面板背景、输入框背景 |
| `#242B3D` | 中蓝灰 | 导航栏背景、Tab 栏背景、工具栏背景、表头背景 |
| `#2A3142` | 悬浮蓝灰 | 按钮 hover 背景、列表项 hover 背景、表格交替行背景 |

### 2.5 状态颜色（动态）

| 场景 | 色值 |
|------|------|
| 项目卡片正常 | `#3DD66A` |
| 项目卡片警告（无巡检） | `#FFB040` |
| 项目卡片故障（有故障设备） | `#FF5C5C` |
| 设备在线/成功 | `#0F8B6E` |
| 设备离线/失败 | `#4A5266` |
| 连接测试中 | `#00D4E8` |

---

## 三、字体系统

### 3.1 字体族

| 场景 | 字体 |
|------|------|
| 全局 UI（三主题统一） | `'Segoe UI', 'Microsoft YaHei', sans-serif` |
| 代码/日志/预览/等宽内容 | `'Consolas', 'Courier New', monospace` |

> **V0.3.7 统一**：三套主题 font_ui 统一为 `'Segoe UI', 'Microsoft YaHei', sans-serif`，不再使用 `Inter`/`SF Pro Display`（Windows 不可用）。font_mono 统一为 `'Consolas', 'Courier New', monospace`。

### 3.2 字号层级（4 级，统一使用 pt）

| 层级 | 字号 | 使用场景 |
|------|------|---------|
| **L1 标题** | `14pt` | 页面大标题、导航栏 Logo |
| **L2 分组** | `12pt` | 区块标题、大按钮文字、重要数据 |
| **L3 正文** | `11pt` | 表单标签、正文、输入框、标准按钮、Tab 文字、表格内容、描述文字 |
| **L4 辅助** | `10pt` | 辅助说明、状态栏、表格头部、小按钮、工具栏按钮、提示文字 |

> **V0.3.7 变更**：
> - 全局默认字号从 `10pt` → `11pt`（政企用户可读性优先）
> - 去掉 `9pt` 字号，最小字号为 `10pt`
> - 去掉 `px` 单位混用，全部统一 `pt`
> - 去掉 `15pt` 页面大标题，统一为 `14pt`
> - 关于对话框标题 `18pt` 保持不变

### 3.3 字重

| 场景 | 字重 |
|------|------|
| 页面标题、分组标题、主按钮、导航激活态、表格头部 | `bold`（700） |
| 次级标题、卡片标题 | `500`（Medium） |
| 普通标签、输入框文字、描述文字 | `normal`（400） |

---

## 四、通用组件规范

### 4.1 按钮（QPushButton）

> **V0.3.7 统一规范**：所有按钮使用统一样式——透明背景 + 中性灰边框。禁止在按钮中使用 `primary`、`danger`、`success`、`warning`、`accent` 等功能色作为背景色或边框色。功能色仅用于文字颜色、状态图标、结果背景等非按钮场景。

#### 标准按钮（所有按钮统一）
```css
QPushButton {
    background-color: transparent;
    border: 1px solid #2E3648;
    border-radius: 5px;
    font-size: 11pt;
    color: #B0B8C8;
    padding: 5px 8px;
}
QPushButton:hover {
    background-color: rgba(255,255,255,0.05);
    border-color: #4A5266;
    color: #E8ECF1;
}
QPushButton:pressed {
    background-color: rgba(255,255,255,0.08);
}
QPushButton:disabled {
    border-color: #2E3648;
    color: #4A5266;
}
```
- **尺寸**：固定高度 30px（padding 5+5 + 边框 1×2 + 文字 18px = 30px），宽度自适应或 80~140px
- **场景**：所有按钮（生成、保存、执行、添加、删除、AI分析、复制、导出、刷新、打开等）

#### 工具栏小按钮
```css
QPushButton {
    background-color: transparent;
    border: 1px solid #2E3648;
    border-radius: 3px;
    font-size: 10pt;
    color: #B0B8C8;
    padding: 2px 8px;
}
QPushButton:hover {
    background-color: rgba(255,255,255,0.05);
    border-color: #4A5266;
    color: #E8ECF1;
}
QPushButton:disabled {
    border-color: #2E3648;
    color: #4A5266;
}
```
- **尺寸**：高度 26px（padding 3+3 + 边框 1×2 + 文字 18px = 26px），宽度自适应
- **场景**：文件列表上方的刷新/打开/删除三件套等工具栏区域

#### 导航按钮（Navigation）
```css
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 11pt;
    color: #B0B8C8;
}
QPushButton:hover {
    background-color: #2A3142;
    color: #E8ECF1;
}
QPushButton[active="true"] {
    background-color: #1A3A6E;
    color: #4D90FF;
    font-weight: bold;
}
```
- **尺寸**：高度 28px，宽度自适应

#### 状态指示按钮（Activation Status）

| 状态 | 背景 | 边框 | 文字色 |
|------|------|------|--------|
| 试用/未激活 | `#3A1A1A` | `#FF5C5C` | `#FF5C5C` |
| 即将过期 | `#2A2210` | `#FFB040` | `#FA8C16` |
| 永久/充足 | `#1F4A2E` | `#3DD66A` | `#3DD66A` |

```css
QPushButton {
    border-radius: 5px;
    font-size: 10pt;
    font-weight: bold;
}
```
- **尺寸**：`setFixedSize(90, 28)`

### 4.2 输入框（QLineEdit）

#### 标准输入框
```css
QLineEdit {
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11pt;
    background-color: #1E2433;
    color: #E8ECF1;
    min-height: 26px;
}
QLineEdit:focus {
    border-color: #3B7CFF;
}
```
- **高度**：28px（`setMinimumHeight(28)`）
- **场景**：大部分表单输入
- **V0.3.7**：字号 10pt→11pt，高度 32px→28px

#### 带背景输入框（project_manager / system_settings）
```css
QLineEdit {
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11pt;
    background-color: #1A1F2E;
    color: #E8ECF1;
    min-height: 26px;
}
QLineEdit:focus {
    border-color: #3B7CFF;
    background-color: #1E2433;
}
```
- **V0.3.7**：字号 10pt→11pt，padding 8px→6px，统一 min-height: 28px

#### 只读/机器码输入框
```css
QLineEdit {
    background-color: #1A1F2E;
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 4px 8px;
    color: #4D90FF;
    font-family: Consolas;
    font-size: 11pt;
    min-height: 26px;
}
```
- **V0.3.7**：新增 font-size: 11pt，min-height: 28px

### 4.3 下拉框（QComboBox）

#### 标准下拉框
```css
QComboBox {
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11pt;
    background-color: #1E2433;
    color: #E8ECF1;
    min-height: 26px;
}
QComboBox:hover { border-color: #3B7CFF; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    border: 1px solid #2E3648;
    selection-background-color: #1A3A6E;
    outline: none;
    background-color: #1E2433;
}
```
- **V0.3.7**：字号 10pt→11pt，padding 8px→6px，统一 min-height: 28px

#### 小组合框（工具栏）
```css
QComboBox {
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 4px 10px;
    font-size: 10pt;
    background-color: #242B3D;
    color: #B0B8C8;
    min-height: 26px;
}
QComboBox:focus { border-color: #3B7CFF; }
QComboBox::drop-down { border: none; width: 20px; }
```
- **V0.3.7**：字号 9pt→10pt，padding 5px→4px

### 4.4 表格（QTableWidget）

```css
QTableWidget {
    border: 1px solid #2E3648;
    border-radius: 5px;
    background-color: #1E2433;
    gridline-color: #2A3142;
}
QTableWidget::item { padding: 6px 8px; color: #B0B8C8; }
QTableWidget::item:alternate { background-color: #2A3142; }
QHeaderView::section {
    background-color: #242B3D;
    border: none;
    border-bottom: 1px solid #2E3648;
    padding: 8px;
    font-weight: bold;
    color: #E8ECF1;
    font-size: 10pt;
}
QTableWidget::item:selected { background-color: #1A3A6E; color: #E8ECF1; }
```

- **行高**：36px（`verticalHeader.setDefaultSectionSize(36)`）
- **选择行为**：`SelectRows`，`NoEditTriggers`
- **滚动条**：水平/垂直均 `AlwaysOff`

### 4.5 标签页（QTabWidget）

```css
QTabWidget::pane {
    border: 1px solid #2E3648;
    border-radius: 5px;
    background-color: #1E2433;
}
QTabBar::tab {
    background-color: #242B3D;
    border: 1px solid #2E3648;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 5px 8px;
    font-size: 11pt;
    color: #7A8296;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1E2433;
    color: #4D90FF;
    border-bottom: 2px solid #5C8AFF;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #2A3142;
    color: #B0B8C8;
}
```

### 4.6 分组框（QGroupBox）

```css
QGroupBox {
    font-size: 11pt;
    font-weight: bold;
    color: #E8ECF1;
    border: 1px solid #2E3648;
    border-radius: 8px;
    margin-top: 10px;
    padding: 14px;
    background-color: #1E2433;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
```
- **V0.3.7**：字号 10pt→11pt

### 4.7 列表（QListWidget）

```css
QListWidget {
    border: 1px solid #2E3648;
    border-radius: 5px;
    background-color: #1E2433;
    font-size: 11pt;
    outline: none;
    color: #B0B8C8;
}
QListWidget::item { padding: 5px 8px; }
QListWidget::item:selected { background-color: #1A3A6E; color: #E8ECF1; }
QListWidget::item:hover { background-color: #2A3142; }
```
- **V0.3.7**：字号 10pt→11pt

### 4.8 文本编辑区（QTextEdit）

#### 代码/预览区
```css
QTextEdit {
    border: 1px solid #2E3648;
    border-radius: 5px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11pt;
    background-color: #1A1F2E;
    color: #B0B8C8;
}
```

#### Prompt 编辑区
```css
QTextEdit {
    border: 1px solid #3B7CFF;
    border-radius: 5px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11pt;
    background-color: #1A1F2E;
    color: #E8ECF1;
}
```
- **V0.3.7**：字号 10pt→11pt

### 4.9 进度条（QProgressBar）

```css
QProgressBar {
    border: 1px solid #2E3648;
    border-radius: 5px;
    text-align: center;
    background-color: #2A3142;
    font-size: 10pt;
    color: #B0B8C8;
}
```
- **V0.3.7**：字号 10px→10pt
QProgressBar::chunk {
    background-color: #3B7CFF;
    border-radius: 3px;
}
```

### 4.10 复选框（QCheckBox）

```css
QCheckBox { font-size: 11pt; color: #B0B8C8; }
- **V0.3.7**：字号 10pt→11pt
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #2E3648;
}
QCheckBox::indicator:checked {
    background-color: #3B7CFF;
    border-color: #3B7CFF;
}
```

### 4.11 卡片（Card）

```css
QWidget {
    background-color: #1E2433;
    border-radius: 8px;
    padding: 14px;
    border: 1px solid #2E3648;
}
```

- **内部间距**：`spacing: 10`
- **标题**：`font-size: 12pt; font-weight: bold; color: #E8ECF1;`
- **描述**：`font-size: 11pt; color: #7A8296; margin-bottom: 10px;`
- **V0.3.7**：描述字号 10pt→11pt

### 4.12 分割线（QFrame HLine）

```css
QFrame { color: #383F50; max-height: 1px; }
```

### 4.13 对话框（QDialog）

- **全局背景**：`#1E2433`
- **标准尺寸**：
  - 登录对话框：`400×320`
  - 激活对话框：`580×560`（三重锁定）
  - 账户管理对话框：`420×340`
  - 关于对话框：`500×340`
  - 管理员工具窗口：最小 `900×650`，启动时 80% 屏幕居中

---

## 五、布局与间距标准

### 5.1 统一单位

- **边距单位**：px（像素）
- **圆角单位**：px
- **字号单位**：pt

### 5.2 间距系统

#### 间距 Token

| Token | 值 | 使用场景 |
|-------|----|---------|
| `xs` | `2px` | 分割线上下间距、极紧凑元素间距 |
| `sm` | `6px` | 工具栏按钮间距、同行小间距 |
| `md` | `12px` | 表单行间距、卡片内部间距、Tab 间距 |
| `lg` | `16px` | 页面级 ContentsMargins、GroupBox 内部 padding |
| `xl` | `16px` | 大区域留白（与 lg 同级） |

#### 页面级边距与间距

| 页面/区域 | ContentsMargins | Spacing |
|-----------|----------------|---------|
| 主窗口主布局 | `(0, 0, 0, 0)` | `0` |
| 导航栏布局 | `(lg, 0, lg, 0)` 即 `(16, 0, 16, 0)` | `4` |
| 配置页面根布局 | `(lg, lg, lg, lg)` 即 `(16, 16, 16, 16)` | `md` |
| 项目运维主布局 | `(lg, md, lg, md)` 即 `(16, 12, 16, 12)` | `sm` |
| 单点运维主布局 | `(md, sm, md, sm)` 即 `(12, 6, 12, 6)` | `sm` |
| AI分析主布局 | `(lg, lg, lg, lg)` 即 `(16, 16, 16, 16)` | `md` |
| 状态栏 | `padding: xs md` 即 `padding: 2px 12px` | - |

> **V0.3.7**：引入五级间距 Token（xs/sm/md/lg/xl），统一页面边距与间距标准。

### 5.3 圆角规范

| Token | 值 | 适用组件 |
|-------|----|---------|
| `sm` | `3px` | 小按钮、工具栏按钮、复选框 indicator、进度条 chunk |
| `md` | `5px` | 标准按钮、输入框、下拉框、文本框、Spinbox、导航按钮 |
| `lg` | `8px` | GroupBox、卡片、配置选择栏按钮、Tab 页签 |

> **V0.3.7**：圆角精简为三级（3/5/8px），原 4px 统一升为 5px，原 6px 统一降为 5px，消除冗余中间值。

### 5.4 边框规范

| 属性 | 标准值 | 说明 |
|------|----|------|
| 宽度 | `1px` | 所有边框统一 1px，禁止 2px 及以上 |
| 样式 | `solid` | 仅使用实线，禁止 dashed/dotted |
| 颜色 | 主题动态色 | 使用 `t['border']` 或 `t['input_border']`，禁止硬编码色值 |

**各控件边框颜色**：

| 控件 | 边框颜色 Key |
|------|-------------|
| 输入框（QLineEdit） | `input_border`（未聚焦）、`primary`（聚焦） |
| 下拉框（QComboBox） | `input_border` |
| 文本框（QTextEdit） | `input_border` |
| 表格（QTableWidget） | `border` |
| 按钮 | 各按钮类型自定义（透明边框+主题色） |
| GroupBox | `border` |
| 卡片 | `border` |
| Tab 页签 | `border` |
| 进度条 | `border` |
| 列表（QListWidget） | `border` |

> **V0.3.7**：边框统一为 `1px solid`，颜色全部引用主题动态色，禁止硬编码。

### 5.5 布局比例

| 区域 | 比例 |
|------|------|
| 左侧配置区 : 右侧预览区 | `7 : 3` |
| AI分析左侧面板 : 右侧面板 | 最大宽 320px : 自适应，分割比例 `1:4` |

### 5.6 标准控件高度

| 控件 | 高度 | 说明 |
|------|------|------|
| 导航栏 | 48px | 顶部主导航区域 |
| 导航按钮 | 24px | 与导航栏同高，紧凑排列 |
| 输入框（QLineEdit） | 26px | padding 4+4 + 边框 1×2 = 26px |
| 下拉框（QComboBox） | 26px | 与输入框对齐 |
| 文本框（QTextEdit） | 自适应 | 不固定高度 |
| 主按钮 | 30px | padding 5+5 + 边框 1×2 + 文字18px = 30px |
| 标准按钮 | 30px | 同行与输入框视觉居中对齐 |
| 小按钮/工具栏按钮 | 26px | padding 3+3 + 边框 1×2 + 文字18px = 26px |
| 设备状态/激活按钮 | 26px | 与工具栏同档 |
| 账户/关于按钮 | 26px | 与导航按钮同档 |
| 表格行 | 32px | 紧凑行高，提升信息密度 |
| 表格内图标按钮 | 22px | 行内操作按钮 |
| 进度条 | 16px | 细长进度指示 |
| 复选框 indicator | 16px | 方形 indicator |

> **V0.3.7 统一**：控件高度由 padding + 边框 + 文字高度精确计算，不凭感觉设定。11pt 中文字体渲染高度约 18px，按钮统一 `padding: 5px 8px`，固定高度 30px（5+5+2+18=30）。输入框 padding `4px 8px`，固定高度 26px。导航栏压缩至 48px，表格行压缩至 32px，整体更紧凑精致。

---

## 六、交互行为规范

### 6.1 按钮状态

| 状态 | 视觉反馈 |
|------|---------|
| **默认** | 各按钮各自的基础色 |
| **hover** | 背景色变深或边框变蓝（`#165DFF`） |
| **pressed** | 背景色更深（仅部分按钮定义） |
| **disabled** | 背景 `#C9CDD4`，文字变灰 |
| **active**（自定义属性） | 蓝色背景 + 白色文字 + 加粗 |

### 6.2 输入框状态

| 状态 | 视觉反馈 |
|------|---------|
| **默认** | 灰色边框 `#E5E6EB`，深黑文字 `#1D2129` |
| **focus** | 边框变蓝 `#165DFF` |
| **只读** | 灰色背景 `#F5F5F5`，Consolas 字体 |

### 6.3 表格交互

- **选中行**：`SelectRows` 行为
- **编辑**：`NoEditTriggers`（禁止直接编辑）
- **交替行**：`#F7F8FA` 交替背景
- **滚动条**：始终关闭（`AlwaysOff`）

### 6.4 弹窗行为

- **危险操作**：必须有确认对话框
- **激活/登录弹窗**：无关闭按钮、禁止 ESC
- **关于对话框**：试用模式下可主动激活

### 6.5 提示信息样式

| 类型 | 样式 |
|------|------|
| 就绪状态 | `font-size: 10pt; color: #7A8296;` |
| 运行中 | `font-size: 10pt; color: #00D4E8; font-weight: normal;` |
| 完成 | `font-size: 10pt; color: #3DD66A; font-weight: normal;` |
| 错误 | `font-size: 10pt; color: #FF5C5C; font-weight: normal;` |

> **V0.3.7**：9pt→10pt

### 6.6 加载效果

- 进度条：`QProgressBar`，高度 14~22px，蓝色 chunk `#3B7CFF`
- 按钮加载中：背景 `#FFB040`，`disabled` 状态

---

## 七、推荐行为与禁止行为清单

### ✅ 推荐行为

1. **颜色**：新增颜色必须从本规范色盘中选取，如需新色须先更新本文件
2. **按钮**：所有按钮统一使用 `transparent` 背景 + `border` 中性灰边框，hover 时边框加深为 `border_deep`；禁止在按钮中使用 `primary`、`danger`、`success`、`warning`、`accent` 等功能色作为背景色或边框色
3. **输入框**：统一高度 32px，focus 时边框变蓝
4. **表格**：统一行高 36px，交替行背景，禁止直接编辑
5. **间距**：页面级边距 12~16px，组件间距 4~12px
6. **圆角**：按钮/输入框 4px，GroupBox/卡片 8px
7. **交互反馈**：所有可交互组件必须定义 hover 和 focus 状态
8. **禁用状态**：统一使用 `#C9CDD4` 背景色
9. **代码区域**：统一使用 Consolas 等宽字体
10. **危险操作**：必须有二次确认对话框

### ❌ 禁止行为

1. **禁止**：使用规范外的颜色值（除非先更新本文件）
2. **禁止**：按钮无 hover/focus 状态
3. **禁止**：输入框无 focus 反馈
4. **禁止**：硬编码绝对路径（必须使用 `get_app_dir()` 等 API）
5. **禁止**：在界面代码中直接拼接命令字符串（防注入）
6. **禁止**：删除/导出等危险操作无确认对话框
7. **禁止**：QThread 保存为局部变量（必须保存为实例变量）
8. **禁止**：使用 `print()` 调试（必须使用 `netops_logger`）
9. **禁止**：文件写入非原子操作（必须 `.tmp` + `os.replace`）
10. **禁止**：脱离本规范自创界面风格

---

## 八、界面开发指令模板

### 8.1 新增界面模板

后续新增界面时，直接套用以下指令：

> 「请根据项目根目录的 `DESIGN.md` 规范，开发 **[功能名称]** 界面。要求：
> 1. 组件样式（按钮、输入框、表格、分组框、标签等）必须严格遵循 DESIGN.md 中的 QSS 样式模板
> 2. 色彩必须从 DESIGN.md 色盘中选取，禁止自创颜色；**按钮用色统一规范**：所有按钮 `transparent` 背景 + `border` 中性灰边框，hover 边框加深；**禁止在按钮中使用 primary/danger/success/warning/accent 等功能色作为背景色或边框色**
> 3. 字体层级遵循 L1~L4 字号规范
> 4. 间距与边距遵循布局标准（页面边距 12~16px，组件间距 4~12px）
> 5. 圆角规范：按钮/输入框 5px（md），小按钮/工具栏 3px（sm），GroupBox/卡片 8px（lg）
> 6. 所有可交互组件必须定义 hover 和 focus 状态
> 7. 危险操作必须有二次确认对话框
> 8. 整体风格与现有项目页面保持完全一致。」

### 8.2 修改现有界面模板

> 「请根据项目根目录的 `DESIGN.md` 规范，对 **[页面名称]** 界面进行标准化整改。要求：
> 1. 逐项比对 DESIGN.md 中的样式规范
> 2. 修正所有不符合规范的色值、字号、间距、圆角
> 3. 修正所有按钮样式：背景必须为 transparent，边框必须为 border 中性灰，禁止 primary/danger 等功能色
> 4. 补齐缺失的 hover/focus/disabled 状态
> 5. 整改完成后列出修改项清单。」

## 八之三、V0.3.7 控件紧凑化变更记录

> 本次调整目标：消除"偏大、不紧凑、不精致"感，所有控件高度由 padding + 边框精确计算。

### 按钮内部留白（文字 ↔ 按钮边框）

| 方向 | 值 | 说明 |
|------|----|------|
| 顶部内边距 | `5px` | 统一所有按钮 |
| 底部内边距 | `5px` | 统一所有按钮 |
| 左侧内边距 | `8px` | 统一所有按钮 |
| 右侧内边距 | `8px` | 统一所有按钮 |
| 固定总高度 | `28px` | padding 5+5 + 边框 1×2 = 28px |

### 按钮之间间距（按钮 ↔ 相邻按钮）

| 关系 | 值 |
|------|----|
| 横向并排按钮间距 | `5px` |
| 竖向堆叠按钮间距 | `5px` |

### 按钮与外部元素间距

| 关系 | 值 |
|------|----|
| 按钮 → 所属窗口/面板内壁 | `10px` |
| 按钮 → 旁边输入框/下拉框 | `5px` |
| 按钮组 → 上方/下方标题/分割线 | `10px` |

### 控件高度调整

| 控件 | 旧值 | 新值 | 计算依据 |
|------|------|------|---------|
| 导航栏 | 56px | 48px | 压缩留白 |
| 导航按钮 | 28px | 26px | padding 3+3 + 边框 1×2 + 文字18px = 26px |
| 输入框 | 28px | 26px | padding 4+4 + 边框 1×2 = 26px |
| 下拉框 | 28px | 26px | 与输入框对齐 |
| 主按钮 | 30px | 30px | padding 5+5 + 边框 1×2 + 文字18px = 30px |
| 标准按钮 | 28px | 30px | 修复文字裁剪：11pt中文字高18px，28px不够 |
| 小按钮/工具栏 | 24px | 26px | padding 3+3 + 边框 1×2 + 文字18px = 26px |
| 账户/关于按钮 | 28px | 26px | 与导航按钮同档 |
| 设备状态/激活按钮 | 28px | 26px | 与工具栏同档 |
| 表格行 | 36px | 32px | 提升信息密度 |
| 进度条 | 自适应 | 16px | 固定细长高度 |
| 复选框 indicator | 15px | 16px | 标准方形尺寸 |

### 圆角 Token 更新

| Token | 旧值 | 新值 |
|-------|------|------|
| radius_sm | 各主题不一 | 3/2/3 |
| radius_md | 各主题不一 | 5/3/5 |
| radius_lg | 各主题不一 | 8/5/8 |

### 影响文件

- `src/core/theme_engine.py` — 圆角 Token、全局 QSS 控件高度/圆角/padding
- `src/ui/main_window.py` — 导航栏高度、导航按钮/账户/关于按钮尺寸
- `src/ui/ai_analysis_page.py` — 按钮 padding
- `src/ui/ops_toolbox_page.py` — 按钮 padding、主布局边距
- `src/ui/single_device_page.py` — 按钮 padding、主布局边距、表格行高
- `src/ui/batch_cmd_generator_page.py` — 按钮 padding
- `src/ui/system_settings_page.py` — 按钮 padding
- `src/ui/device_discovery_dialog.py` — 输入框 padding/高度
- `src/ui/device_form_dialog.py` — 输入框 padding/高度
- `src/ui/config_pages/` — 全部 16 个配置页表格行高 36→32

---

## 九、文件与维护

- **本文件位置**：项目根目录 `DESIGN.md`，与 `CLAUDE.md` 同级
- **版本**：V0.3.7
- **更新日期**：2026年5月26日
- **维护规则**：每次新增/修改界面样式后，必须同步更新本文件对应章节

## 十一、PyQt5 渲染与 DPI 专项规范

> **本章节为渲染底层规范，优先级高于配色与样式章节。所有涉及 DPI、渲染管线、字体绘制的代码，必须以本章节为唯一标准。**

### 11.1 适用范围

仅约束 PyQt5 项目底层渲染、DPI 缩放、文本绘制逻辑，不改动配色、界面样式、业务代码。

### 11.2 核心目标

1. 程序固定以 **96DPI（系统 100% 缩放基准）** 渲染，不受 Windows 系统缩放（100%/125%/150% 等）影响
2. 字体、控件尺寸全程保持固定，杜绝发虚、重影、锯齿，提升文字清晰度
3. 兼容窗口最大化、手动调整窗口大小功能，切换状态后显示无异常

### 11.3 强制开发规则

| 序号 | 规则 | 实现方式 |
|------|------|---------|
| R1 | 关闭高 DPI 自适应 | `Qt.AA_EnableHighDpiScaling = False` + `Qt.AA_DisableHighDpiScaling = True`，必须在 `QApplication` 构造前调用 |
| R2 | 禁止 Qt 自动屏幕缩放 | 删除 `QT_AUTO_SCREEN_SCALE_FACTOR` 环境变量，设置 `QT_ENABLE_HIGHDPI_SCALING=0` |
| R3 | 屏蔽系统原生主题差异 | `QApplication.setStyle("Fusion")`，全局启用 Fusion 样式 |
| R4 | 全局文本抗锯齿 | `QFont.setStyleStrategy(QFont.PreferAntialias)` 应用到全局字体 |
| R5 | 固定像素尺寸 | 所有控件尺寸、字号使用绝对像素/pt 单位，禁止使用动态适配、相对尺寸单位（em、百分比等） |
| R6 | 进程 DPI Unaware 兜底 | `SetProcessDpiAwareness(0)` + `app.manifest` 声明 `dpiAwareness:unaware`，三层控制确保布局稳定 |

### 11.4 main.py DPI 初始化代码模板

```python
# ── 第1步：环境变量（QApplication 构造前）──
if "QT_DEVICE_PIXEL_RATIO" in os.environ:
    del os.environ["QT_DEVICE_PIXEL_RATIO"]
if "QT_AUTO_SCREEN_SCALE_FACTOR" in os.environ:
    del os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"]
if "QT_SCALE_FACTOR" in os.environ:
    del os.environ["QT_SCALE_FACTOR"]
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

# ── 第2步：Qt 属性（QApplication 构造前）──
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)

# ── 第3步：进程 DPI Unaware（Windows API 兜底）──
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
except Exception:
    pass

# ── 第4步：Fusion 样式 + 全局抗锯齿 ──
app.setStyle("Fusion")
font = app.font()
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
```

### 11.5 效果说明

- 系统缩放仅作用于系统桌面，本程序界面大小、字体大小不会跟随改变
- 文字边缘锐利清晰，解决缩放引发的模糊问题
- 高分屏环境下字体不会自动放大，可通过调整基准字号平衡视觉大小与可读性
- 窗口常规尺寸、最大化状态互相切换，渲染效果、字体清晰度保持一致

### 11.6 验收标准

| 编号 | 验收项 | 方法 |
|------|--------|------|
| A1 | 切换系统不同缩放比例（100%/125%/150%），程序字体、控件、布局尺寸无变化 | 实机切换对比 |
| A2 | 字体显示清晰，无模糊、锯齿、重影现象 | 与系统记事本文字对比 |
| A3 | 窗口最大化/还原、拖拽调整窗口大小，界面显示正常 | 手动操作验证 |

---

## 十、变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-05-24 | 初版创建，从30+ UI文件提取完整设计规范 |
| 2026-05-25 | 修正复选框指示器边框色 `#C9CDD4`→`#E5E6EB`（§4.10）；同步修正代码中10处正常态组件边框色不一致 |
| 2026-05-25 | **V0.3.4 暗蓝科技感升级**：整体配色从浅灰底迁移为深空蓝 `#1A1F2E` 暗色系；主色从 `#165DFF` 升级为 `#3B7CFF` 科技蓝；新增冰蓝 `#00D4E8`、深青绿 `#0F8B6E`、柔光蓝 `#5C8AFF` 三强调色；所有功能色适配暗色背景（提亮15-20%）；更新主窗口、登录/激活/账户管理对话框共5个文件 |
| 2026-05-25 | **V0.3.5 三主题切换体系**：新增 `src/core/theme_engine.py`（ThemeEngine 单例 + 三套完整配色数据 + 全局QSS生成 + 组件QSS片段 + 配置持久化）；新增 `src/ui/theme_switcher_page.py`（主题切换面板 + 预览卡片 + 一键切换）；重构 `main_window.py`（移除硬编码QSS，集成ThemeEngine，导航栏/状态栏/配置栏/激活按钮/关于对话框全部动态适配）；重构 `login_dialog.py`、`activation_dialog.py`、`account_manager_dialog.py`（硬编码颜色→ThemeEngine动态颜色 + theme_changed监听）；重构 `batch_cmd_generator_page.py`（ParamGroupWidget + 模板按钮 + 状态栏全部动态适配）；更新 DESIGN.md 为三主题规范 |
| 2026-05-26 | **DPI 渲染专项规范**：新增第十一章「PyQt5 渲染与 DPI 专项规范」；修改 `main.py` DPI 初始化逻辑：移除冲突的 `QT_AUTO_SCREEN_SCALE_FACTOR`，关闭 `AA_EnableHighDpiScaling`，全局启用 Fusion 样式 + `QFont.PreferAntialias` 文本抗锯齿，设置 `QT_ENABLE_HIGHDPI_SCALING=0` 兜底 |
| 2026-05-26 | **商务主题黑色残留修复**：`theme_engine.py` 商务主题 `text_primary` 从 `#202124` 改为 `#FFFFFF`（彩色按钮文字统一白色）；`selection_bg` 从 `rgba(26,115,232,0.08)` 改为 `#BBDEFB`（选中项背景加深确保白字可读）；`single_device_page.py` 占位符文字从 `border_deep` 改为 `text_tertiary`（极浅灰→可见灰色） |
| 2026-05-26 | **V0.3.7 字号与按钮尺寸全局规范化**：① 字号体系从 6 级（15/12/10/9/8 + 游离）精简为 4 级（14/12/11/10），去掉 9pt 和 15pt；② 全局默认 10pt→11pt；③ 页面大标题 15pt→14pt；④ 配置输出框 10pt→11pt monospace；⑤ 按钮三档高度统一为 30/26/26px（留白 5~6px），字号对应 12/11/10pt；⑥ 输入框统一 26px 高度；⑦ 所有 px 字号单位改为 pt；⑧ 涉及 theme_engine.py + 18 个 UI 文件全面整改 |
| 2026-05-27 | **V0.3.7 按钮文字裁剪修复**：实测发现 11pt 中文字体渲染高度约 18px，28px 按钮高度（padding 5+5 + border 2 + 文字 18 = 30px 需求）导致文字被上下裁剪 1px。将所有 `setFixedSize(..., 28)` 的按钮统一改为 30px，共涉及 11 个文件 40+ 处。厂商选择按钮（锐捷/华为/H3C/思科）和设备类型按钮（接入交换机/核心交换机/路由器/AC）文字现已完整显示 |
| 2026-05-27 | **V0.3.7 按钮用色规范统一**：彻底清除所有 success/warning/accent 功能色作为按钮背景的违规用法。修复 `single_device_page.py`（添加设备/测试连接/删除/取消按钮）、`batch_cmd_generator_page.py`（删除模板按钮）共 6 处。同步修订 DESIGN.md：§2.3 功能色表删除按钮相关描述并增加总纲引用、§4.1 总纲明确四类按钮规范并删除矛盾表述、§7 推荐行为更新按钮描述、§8.1 开发模板增加按钮用色约束。**根本原因**：DESIGN.md 色值表与按钮规范存在矛盾，导致多次修复不彻底 |
