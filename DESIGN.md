# NetOps 界面设计规范（V0.3.5 三主题版）

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

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#3DD66A` | 成功绿 | 保存按钮、测试连接按钮、成功状态图标、已激活状态、合规通过判定 |
| `#2BA84E` | 成功绿深 | 成功按钮 hover |
| `#43A047` | 激活绿 | 试用模式激活按钮、保存模板按钮（batch_cmd_generator） |
| `#2E7D32` | 深绿 hover | 激活绿按钮 hover |
| `#1F4A2E` | 成功绿背景 | 合规审计通过结果背景（深色底） |
| `#FFB040` | 警告橙 | 删除配置按钮、连接测试按钮、故障按钮、进行中状态、即将过期提示 |
| `#CC8C30` | 警告橙深 | 警告按钮 hover |
| `#FA8C16` | 警告橙文字 | 即将过期按钮文字/border |
| `#2A2210` | 警告背景 | 警告按钮背景、即将过期按钮背景、安全提醒框背景（深色底） |
| `#FAAD14` | 金黄 | 复制按钮、重命名模板按钮（batch_cmd_generator） |
| `#D48806` | 金黄 hover | 金黄按钮 hover |
| `#FF5C5C` | 危险红 | 删除按钮、错误状态、诊断按钮、未激活提示文字 |
| `#CC3E3E` | 危险红深 | 删除按钮 hover |
| `#FF4D4F` | 亮红 | 表格行内删除按钮（core/access switch） |
| `#FF7875` | 亮红 hover | 亮红按钮 hover |
| `#3A1A1A` | 危险红背景 | 不通过审计结果背景（深色底） |
| `#9B6CEF` | 紫色 | AI精审按钮背景 |
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
| 全局 UI | `Microsoft YaHei`（系统默认回退） |
| 代码/日志/预览/等宽内容 | `'Consolas', 'Courier New', monospace` |
| HTML 报告渲染 | `'Microsoft YaHei', sans-serif` |

### 3.2 字号层级

| 层级 | 字号 | 使用场景 |
|------|------|---------|
| **L1 页面大标题** | `15pt` | 页面标题（"AI专家工作站"、"项目运维"）、base_config_page 标题 |
| **L2 分组标题** | `12pt` | QGroupBox 标题、预览区标题、卡片标题 |
| **L3 正文/按钮** | `10pt` | 按钮文字、输入框文字、表单标签、Tab 文字、组合框、描述文字 |
| **L4 辅助信息** | `9pt` | 标签文字、输入框标签、辅助信息、表格内容、小按钮、工具栏按钮、状态标签 |
| **L5 细小信息** | `11px` | 路径信息、统计信息、小按钮文字、进度条文字 |
| **Logo** | `14pt` | 导航栏 Logo 标签 |
| **配置默认页提示** | `18pt` | 配置选择栏默认提示标签 |

### 3.3 字重

| 场景 | 字重 |
|------|------|
| 页面标题、分组标题、主按钮、导航激活态、表格头部 | `bold` |
| 普通标签、输入框文字、描述文字 | `normal` |
| 部分强调按钮（AI按钮、进入项目按钮） | `bold` |

---

## 四、通用组件规范

### 4.1 按钮（QPushButton）

> **V0.3.7 按钮透明规范**：所有按钮默认背景透明，仅边框+文字可见；悬停时背景变为浅色，边框/文字变亮。
> 使用 ThemeEngine Token 动态配色，禁止硬编码色值。

#### A — 主按钮（Primary）
```css
/* 使用 Token: primary, selection_bg, primary_hover, border, text_disabled */
QPushButton {
    background-color: transparent;
    color: {primary};
    border: 1px solid {primary};
    border-radius: {radius_md}px;
    font-size: 10pt;
    font-weight: bold;
    padding: 8px 20px;
}
QPushButton:hover {
    background-color: {selection_bg};
    border: 1px solid {primary_hover};
    color: {primary_hover};
}
QPushButton:disabled {
    background-color: transparent;
    border: 1px solid {border};
    color: {text_disabled};
}
```
- **尺寸**：高度 32~40px，宽度根据内容自适应或固定 80~120px
- **场景**：生成配置、保存、执行任务、AI分析等主要操作
- **效果**：默认透明+主题色边框 → 悬停浅色背景+深色边框

#### B — 次要边框按钮（Secondary）
```css
/* 使用 Token: text_secondary, border, selection_bg, primary, text_disabled */
QPushButton {
    background-color: transparent;
    color: {text_secondary};
    border: 1px solid {border};
    border-radius: {radius_md}px;
    font-size: 10pt;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: {selection_bg};
    border: 1px solid {primary};
    color: {primary};
}
QPushButton:disabled {
    background-color: transparent;
    border: 1px solid {border};
    color: {text_disabled};
}
```
- **尺寸**：高度 32~40px，宽度 80~120px
- **场景**：取消、刷新、编辑、导入、导出等非破坏性操作
- **效果**：默认透明+灰色边框 → 悬停浅色背景+主题色边框

#### C — 语义按钮（Semantic）
```css
/* Danger — 使用 Token: danger, danger_bg, danger_hover */
QPushButton {
    background-color: transparent;
    color: {danger};
    border: 1px solid {danger};
    border-radius: {radius_md}px;
    font-size: 9pt;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: {danger_bg};
    border: 1px solid {danger_hover};
    color: {danger_hover};
}

/* Success — 使用 Token: success, success_bg, success_hover */
QPushButton {
    background-color: transparent;
    color: {success};
    border: 1px solid {success};
    border-radius: {radius_md}px;
    font-size: 10pt;
    padding: 8px 20px;
}
QPushButton:hover {
    background-color: {success_bg};
    border: 1px solid {success_hover};
    color: {success_hover};
}

/* Warning — 使用 Token: warning, warning_bg, warning_hover */
QPushButton {
    background-color: transparent;
    color: {warning};
    border: 1px solid {warning};
    border-radius: {radius_md}px;
    font-size: 9pt;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: {warning_bg};
    border: 1px solid {warning_hover};
    color: {warning_hover};
}
```
- **尺寸**：高度 24~36px，宽度 60~100px
- **场景**：删除(红)、测试连接(绿)、取消(黄)等语义操作
- **关键**：使用 `*_bg` Token 替代手动透明度，三主题自适应

#### D — AI 按钮
```css
/* 使用 Token: ai_text, ai_border, selection_bg, text_disabled */
QPushButton {
    background-color: transparent;
    color: {ai_text};
    border: 1px solid {ai_border};
    border-radius: {radius_md}px;
    font-size: 10pt;
    font-weight: bold;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: {selection_bg};
    border-color: {ai_text};
    color: {ai_text};
}
QPushButton:disabled {
    background-color: transparent;
    color: {text_disabled};
    border-color: {border};
}
```
- **场景**：所有 AI 分析按钮（AI合规巡检、AI故障诊断、AI精审）

#### E — 工具栏小按钮（Toolbar Small）
```css
/* 使用 Token: text_secondary, border, selection_bg, primary */
QPushButton {
    background-color: transparent;
    border: 1px solid {border};
    border-radius: {radius_sm}px;
    font-size: 11px;
    color: {text_secondary};
    padding: 2px 8px;
}
QPushButton:hover {
    background-color: {selection_bg};
    border-color: {primary};
    color: {primary};
}
```
- **尺寸**：高度 22~26px，宽度 60~70px
- **场景**：文件列表上方的刷新/打开/删除三件套

#### F — 导航按钮（Navigation）
```css
/* 无边框设计，保持透明背景 */
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: {radius_lg}px;
    padding: 6px 16px;
    font-size: 10pt;
    color: {text_secondary};
}
QPushButton:hover {
    background-color: {hover_bg};
    color: {text_main};
}
QPushButton[active="true"] {
    background-color: {selection_bg};
    color: {primary_light};
    font-weight: bold;
}
```
- **尺寸**：高度 40px，宽度自适应

| 状态 | 背景 | 边框 | 文字色 |
|------|------|------|--------|
| 试用/未激活 | `#3A1A1A` | `#FF5C5C` | `#FF5C5C` |
| 即将过期 | `#2A2210` | `#FFB040` | `#FA8C16` |
| 永久/充足 | `#1F4A2E` | `#3DD66A` | `#3DD66A` |

```css
QPushButton {
    border-radius: 4px;
    font-size: 9pt;
    font-weight: bold;
}
/* hover 对应加深背景/边框 */
```
- **尺寸**：`setFixedSize(90, 32)`

### 4.2 输入框（QLineEdit）

#### 标准输入框
```css
QLineEdit {
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #1E2433;
    color: #E8ECF1;
}
QLineEdit:focus {
    border-color: #3B7CFF;
}
```
- **高度**：32px（`setFixedHeight(32)`）
- **场景**：大部分表单输入

#### 带背景输入框（project_manager / system_settings）
```css
QLineEdit {
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #1A1F2E;
    color: #E8ECF1;
}
QLineEdit:focus {
    border-color: #3B7CFF;
    background-color: #1E2433;
}
```

#### 只读/机器码输入框
```css
QLineEdit {
    background-color: #1A1F2E;
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 4px 8px;
    color: #4D90FF;
    font-family: Consolas;
}
```

### 4.3 下拉框（QComboBox）

#### 标准下拉框
```css
QComboBox {
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #1E2433;
    color: #E8ECF1;
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

#### 小组合框（工具栏）
```css
QComboBox {
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 9pt;
    background-color: #242B3D;
    color: #B0B8C8;
}
QComboBox:focus { border-color: #3B7CFF; }
QComboBox::drop-down { border: none; width: 20px; }
```

### 4.4 表格（QTableWidget）

```css
QTableWidget {
    border: 1px solid #2E3648;
    border-radius: 4px;
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
    font-size: 9pt;
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
    border-radius: 4px;
    background-color: #1E2433;
}
QTabBar::tab {
    background-color: #242B3D;
    border: 1px solid #2E3648;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
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
    font-size: 10pt;
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

### 4.7 列表（QListWidget）

```css
QListWidget {
    border: 1px solid #2E3648;
    border-radius: 4px;
    background-color: #1E2433;
    font-size: 10pt;
    outline: none;
    color: #B0B8C8;
}
QListWidget::item { padding: 5px 8px; }
QListWidget::item:selected { background-color: #1A3A6E; color: #E8ECF1; }
QListWidget::item:hover { background-color: #2A3142; }
```

### 4.8 文本编辑区（QTextEdit）

#### 代码/预览区
```css
QTextEdit {
    border: 1px solid #2E3648;
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    background-color: #1A1F2E;
    color: #B0B8C8;
}
```

#### Prompt 编辑区
```css
QTextEdit {
    border: 1px solid #3B7CFF;
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    background-color: #1A1F2E;
    color: #E8ECF1;
}
```

### 4.9 进度条（QProgressBar）

```css
QProgressBar {
    border: 1px solid #2E3648;
    border-radius: 4px;
    text-align: center;
    background-color: #2A3142;
    font-size: 10px;
    color: #B0B8C8;
}
QProgressBar::chunk {
    background-color: #3B7CFF;
    border-radius: 3px;
}
```

### 4.10 复选框（QCheckBox）

```css
QCheckBox { font-size: 10pt; color: #B0B8C8; }
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
- **描述**：`font-size: 10pt; color: #7A8296; margin-bottom: 10px;`

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

### 5.2 页面级边距与间距

| 页面/区域 | ContentsMargins | Spacing |
|-----------|----------------|---------|
| 主窗口主布局 | `(0, 0, 0, 0)` | `0` |
| 导航栏布局 | `(16, 0, 16, 0)` | `4` |
| 配置页面根布局 | `(16, 16, 16, 16)` | `12` |
| 项目运维主布局 | `(16, 14, 16, 14)` | `8` |
| 单点运维主布局 | `(12, 8, 12, 8)` | `6` |
| AI分析主布局 | `(16, 16, 16, 16)` | `10` |
| 状态栏 | `padding: 2px 12px` | - |

### 5.3 圆角规范

| 圆角值 | 适用组件 |
|--------|---------|
| `3px` | 小按钮、复选框 indicator |
| `4px` | 标准按钮、输入框、下拉框、文本框、Spinbox、进度条 chunk |
| `6px` | 导航按钮、部分 GroupBox |
| `8px` | GroupBox、卡片、配置选择栏按钮 |

### 5.4 布局比例

| 区域 | 比例 |
|------|------|
| 左侧配置区 : 右侧预览区 | `7 : 3` |
| AI分析左侧面板 : 右侧面板 | 最大宽 320px : 自适应，分割比例 `1:4` |

### 5.5 标准控件高度

| 控件 | 高度 |
|------|------|
| 导航栏 | 56px |
| 导航按钮 | 40px |
| 输入框（QLineEdit） | 32px |
| 主按钮 | 36~40px |
| 小按钮 | 22~26px |
| 设备状态/激活按钮 | 32px |
| 账户/关于按钮 | 32px |
| 表格行 | 36px |

---

## 六、交互行为规范

### 6.1 按钮状态

| 状态 | 视觉反馈 | Token 参考 |
|------|---------|-----------|
| **默认** | 实心按钮：背景色 + 同色系深色边框；次要按钮：card_bg + 灰色边框 | `primary`+`primary_hover` / `card_bg`+`border` |
| **hover** | 实心按钮：背景变深 + 边框变亮；次要/语义按钮：边框变为主题色 + 文字变主题色 | `primary_hover`+`primary_light` / `selection_bg`+`primary` |
| **pressed** | 背景色更深（仅部分按钮定义） | `primary_pressed` |
| **disabled** | 背景 `border_deep`，边框 `border`，文字 `text_disabled` | 三主题自适应 |
| **active**（自定义属性） | 选中态：`selection_bg` 背景 + `primary_light` 文字 + 加粗 | 导航按钮专用 |

### 6.2 按钮边框规范（V0.3.7）

| 按钮类型 | 默认背景 | 默认边框 | 悬停背景 | 悬停边框 | 文字默认 | 文字悬停 |
|---------|---------|---------|---------|---------|---------|---------|
| A 主按钮 | `transparent` | `1px solid {primary}` | `{selection_bg}` | `1px solid {primary_hover}` | `{primary}` | `{primary_hover}` |
| B 次要按钮 | `transparent` | `1px solid {border}` | `{selection_bg}` | `1px solid {primary}` | `{text_secondary}` | `{primary}` |
| C 语义按钮 | `transparent` | `1px solid {语义色}` | `{语义色_bg}` | `1px solid {语义色_hover}` | 语义色本身 | 语义色_hover |
| D 工具栏小按钮 | `transparent` | `1px solid {border}` | `{selection_bg}` | `1px solid {primary}` | `{text_secondary}` | `{primary}` |
| E AI 按钮 | `transparent` | `1px solid {ai_border}` | `{selection_bg}` | `1px solid {ai_text}` | `{ai_text}` | `{ai_text}` |
| F 导航按钮 | `transparent` | 无边框 | `{hover_bg}` | 无边框 | `{text_secondary}` | `{text_main}` |

**核心原则**：
- 所有按钮默认背景透明（导航按钮除外），仅边框+文字可见
- 悬停时背景变为浅色（`selection_bg` 或 `*_bg`），边框/文字变亮
- 使用 `*_bg` Token 替代手动透明度（如 `{danger}22`），确保三主题自适应
- 禁止在按钮样式中使用 `border: none`（导航按钮除外）

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
| 就绪状态 | `font-size: 9pt; color: #7A8296;` |
| 运行中 | `font-size: 9pt; color: #00D4E8; font-weight: normal;` |
| 完成 | `font-size: 9pt; color: #3DD66A; font-weight: normal;` |
| 错误 | `font-size: 9pt; color: #FF5C5C; font-weight: normal;` |

### 6.6 加载效果

- 进度条：`QProgressBar`，高度 14~22px，蓝色 chunk `#3B7CFF`
- 按钮加载中：背景 `#FFB040`，`disabled` 状态

---

## 七、推荐行为与禁止行为清单

### ✅ 推荐行为

1. **颜色**：新增颜色必须从本规范色盘中选取，如需新色须先更新本文件
2. **按钮**：区分主次操作，主按钮用品牌蓝，次要按钮用浅灰底+灰边框
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
> 2. 色彩必须从 DESIGN.md 色盘中选取，禁止自创颜色
> 3. 字体层级遵循 L1~L5 字号规范
> 4. 间距与边距遵循布局标准（页面边距 12~16px，组件间距 4~12px）
> 5. 圆角规范：按钮/输入框 4px，GroupBox/卡片 8px
> 6. 所有可交互组件必须定义 hover 和 focus 状态
> 7. 危险操作必须有二次确认对话框
> 8. 整体风格与现有项目页面保持完全一致。」

### 8.2 修改现有界面模板

> 「请根据项目根目录的 `DESIGN.md` 规范，对 **[页面名称]** 界面进行标准化整改。要求：
> 1. 逐项比对 DESIGN.md 中的样式规范
> 2. 修正所有不符合规范的色值、字号、间距、圆角
> 3. 补齐缺失的 hover/focus/disabled 状态
> 4. 整改完成后列出修改项清单。」

## 九、文件与维护

- **本文件位置**：项目根目录 `DESIGN.md`，与 `CLAUDE.md` 同级
- **版本**：V0.3.5
- **更新日期**：2026年5月25日
- **维护规则**：每次新增/修改界面样式后，必须同步更新本文件对应章节

## 十、变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-05-24 | 初版创建，从30+ UI文件提取完整设计规范 |
| 2026-05-25 | 修正复选框指示器边框色 `#C9CDD4`→`#E5E6EB`（§4.10）；同步修正代码中10处正常态组件边框色不一致 |
| 2026-05-25 | **V0.3.4 暗蓝科技感升级**：整体配色从浅灰底迁移为深空蓝 `#1A1F2E` 暗色系；主色从 `#165DFF` 升级为 `#3B7CFF` 科技蓝；新增冰蓝 `#00D4E8`、深青绿 `#0F8B6E`、柔光蓝 `#5C8AFF` 三强调色；所有功能色适配暗色背景（提亮15-20%）；更新主窗口、登录/激活/账户管理对话框共5个文件 |
| 2026-05-25 | **V0.3.5 三主题切换体系**：新增 `src/core/theme_engine.py`（ThemeEngine 单例 + 三套完整配色数据 + 全局QSS生成 + 组件QSS片段 + 配置持久化）；新增 `src/ui/theme_switcher_page.py`（主题切换面板 + 预览卡片 + 一键切换）；重构 `main_window.py`（移除硬编码QSS，集成ThemeEngine，导航栏/状态栏/配置栏/激活按钮/关于对话框全部动态适配）；重构 `login_dialog.py`、`activation_dialog.py`、`account_manager_dialog.py`（硬编码颜色→ThemeEngine动态颜色 + theme_changed监听）；重构 `batch_cmd_generator_page.py`（ParamGroupWidget + 模板按钮 + 状态栏全部动态适配）；更新 DESIGN.md 为三主题规范 |
