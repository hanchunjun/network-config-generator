# NetOps 界面设计规范（V0.3.3）

> **唯一权威标准**：所有界面代码的生成与修改，必须以本文件为唯一标准，禁止任何脱离规范的主观发挥。

---

## 一、项目整体视觉风格概述

**企业级浅灰底桌面运维工具风格**：以白色内容区 + 浅灰页面背景为基础，品牌蓝 `#165DFF` 作为全局主色，配合语义化功能色（红/橙/绿/紫）区分操作等级。整体追求信息密度高、层次清晰、交互反馈明确的政企级专业界面。

**设计关键词**：简洁 · 专业 · 信息密度高 · 低学习成本

---

## 二、色彩系统

### 2.1 主色（Primary）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#165DFF` | 品牌蓝 | 主按钮背景、选中态、焦点边框、链接文字、进度条填充、导航激活态 |
| `#0E42D2` | 深蓝 | 主按钮 hover 状态 |
| `#0A3680` | 更深蓝 | 主按钮 pressed 状态（登录/激活对话框） |
| `#1565C0` | 管理员蓝 | 管理员制码工具专属主色（仅 admin_tool_window 使用） |
| `#E8F3FF` | 浅蓝 | AI按钮背景、导航激活背景、列表选中背景、Tab hover 背景 |
| `#D6E8FF` | 浅蓝 hover | AI按钮 hover 背景 |

### 2.2 功能色（Semantic）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#00B42A` | 成功绿 | 保存按钮、测试连接按钮、成功状态图标、已激活状态、合规通过判定 |
| `#009A29` | 深绿 | 成功按钮 hover |
| `#43A047` | 激活绿 | 试用模式激活按钮、保存模板按钮（batch_cmd_generator） |
| `#2E7D32` | 深绿 hover | 激活绿按钮 hover |
| `#E8FFEA` | 浅绿背景 | 合规审计通过结果背景 |
| `#FF7D00` | 警告橙 | 删除配置按钮、连接测试按钮、故障按钮、进行中状态、即将过期提示 |
| `#FA8C16` | 警告橙文字 | 即将过期按钮文字/border |
| `#FFF7E6` | 浅橙背景 | 警告按钮背景、即将过期按钮背景、安全提醒框背景 |
| `#FFE7BA` | 浅橙 hover | 警告按钮 hover 背景 |
| `#FFF7E8` | 浅橙背景2 | 取消按钮背景、危险小按钮背景 |
| `#FAAD14` | 金黄 | 复制按钮、重命名模板按钮（batch_cmd_generator） |
| `#D48806` | 金黄 hover | 金黄按钮 hover |
| `#F53F3F` | 危险红 | 删除按钮、错误状态、诊断按钮、未激活提示文字 |
| `#CB2634` | 深红 | 诊断按钮 hover |
| `#D9363E` | 深红 hover | 删除按钮 hover（DeleteDeviceDialog） |
| `#FF4D4F` | 亮红 | 表格行内删除按钮（core/access switch） |
| `#FF7875` | 亮红 hover | 亮红按钮 hover |
| `#FFECE8` | 浅红背景 | 不通过审计结果背景 |
| `#722ED1` | 紫色 | AI精审按钮背景 |
| `#531DAB` | 深紫 | AI精审按钮 hover |

### 2.3 中性色（Neutral）

| 色值 | 名称 | 使用场景 |
|------|------|---------|
| `#1D2129` | 标题黑 | 页面标题、表格头部文字、输入框文字、分组框标题 |
| `#4E5969` | 正文灰 | 表单标签、副标题、表格内容文字、导航按钮默认文字 |
| `#86909C` | 辅助灰 | 占位符文字、统计信息、状态栏文字、卡片描述、只读字段 |
| `#C9CDD4` | 禁用灰 | 禁用状态文字/边框、占位符列表项前景 |
| `#E5E6EB` | 边框灰 | 所有输入框边框、按钮边框、分割线、表格网格线、卡片边框 |
| `#F2F3F5` | 浅灰背景 | 页面背景（QMainWindow）、表格网格线（部分）、列表项分割线、默认按钮背景 |
| `#F5F7FA` | 更浅灰背景 | 输入框背景（部分页面）、次要按钮背景、进度条背景 |
| `#F7F8FA` | 表格头背景 | QHeaderView 背景、日志编辑区背景、预览区背景 |
| `#FAFAFA` | 窗口背景 | 管理员工具窗口背景（admin_tool_window） |
| `#FAFBFC` | 表单背景 | DeviceFormDialog QGroupBox 背景、文本编辑区背景 |
| `#FFFFFF` | 纯白 | 页面内容区背景、卡片背景、输入框背景、导航栏背景 |

### 2.4 状态颜色（动态）

| 场景 | 色值 |
|------|------|
| 项目卡片正常 | `#00B42A` |
| 项目卡片警告（无巡检） | `#FF7D00` |
| 项目卡片故障（有故障设备） | `#F53F3F` |
| 设备状态成功 | `#00B42A` |
| 设备状态失败 | `#F53F3F` |

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

#### 主按钮（Primary Action）
```css
QPushButton {
    background-color: #165DFF;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 10pt;
}
QPushButton:hover { background-color: #0E42D2; }
QPushButton:pressed { background-color: #0A3680; }
QPushButton:disabled { background-color: #C9CDD4; }
```
- **尺寸**：高度 32~40px，宽度根据内容自适应或固定 80~120px
- **场景**：生成配置、保存、关闭、执行任务等主要操作

#### 次要按钮（Secondary Action）
```css
QPushButton {
    background-color: #F5F7FA;
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    font-size: 10pt;
}
QPushButton:hover { border: 1px solid #165DFF; }
```
- **尺寸**：高度 32~40px，宽度 80~120px
- **场景**：取消、返回、复制、导出、重置等非破坏性操作

#### AI 按钮
```css
QPushButton {
    background-color: #E8F3FF;
    color: #165DFF;
    border: 1px solid #165DFF;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: bold;
    padding: 8px 16px;
}
QPushButton:hover { background-color: #D6E8FF; }
QPushButton:disabled {
    background-color: #F2F3F5;
    color: #C9CDD4;
    border-color: #E5E6EB;
}
```
- **场景**：所有 AI 分析按钮（AI合规巡检、AI故障诊断、AI精审）

#### 危险按钮（Danger Action）
```css
QPushButton {
    background-color: #F53F3F;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 9pt;
}
QPushButton:hover { background-color: #D9363E; }
QPushButton:disabled { background-color: #C9CDD4; }
```
- **尺寸**：高度 24~36px，宽度 60~100px
- **场景**：删除设备、删除配置等破坏性操作

#### 诊断按钮（Diagnose）
```css
QPushButton {
    background-color: #F53F3F;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 9pt;
    font-weight: bold;
}
QPushButton:hover { background-color: #CB2634; }
```

#### AI 精审按钮（Compliance）
```css
QPushButton {
    background-color: #722ED1;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 9pt;
    font-weight: bold;
}
QPushButton:hover { background-color: #531DAB; }
```

#### 工具栏小按钮（Toolbar Small）
```css
QPushButton {
    background-color: #F5F7FA;
    border: 1px solid #E5E6EB;
    border-radius: 3px;
    font-size: 11px;
    color: #4E5969;
    padding: 2px 8px;
}
QPushButton:hover { border-color: #165DFF; color: #165DFF; }
```
- **尺寸**：高度 22~26px，宽度 60~70px
- **场景**：文件列表上方的刷新/打开/删除三件套

#### 导航按钮（Navigation）
```css
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
    color: #4E5969;
}
QPushButton:hover {
    background-color: #F2F3F5;
    color: #1D2129;
}
QPushButton[active="true"] {
    background-color: #E8F3FF;
    color: #165DFF;
    font-weight: bold;
}
```
- **尺寸**：高度 40px，宽度自适应

#### 状态指示按钮（Activation Status）

| 状态 | 背景 | 边框 | 文字色 |
|------|------|------|--------|
| 试用/未激活 | `#FFF2F0` | `#FF7875` | `#F5222D` |
| 即将过期 | `#FFF7E6` | `#FFA940` | `#FA8C16` |
| 永久/充足 | `#F6FFED` | `#73D13D` | `#52C41A` |

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
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #FFFFFF;
    color: #1D2129;
}
QLineEdit:focus {
    border-color: #165DFF;
}
```
- **高度**：32px（`setFixedHeight(32)`）
- **场景**：大部分表单输入

#### 带背景输入框（project_manager / system_settings）
```css
QLineEdit {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #F5F7FA;
}
QLineEdit:focus {
    border-color: #165DFF;
    background-color: #FFFFFF;
}
```

#### 只读/机器码输入框
```css
QLineEdit {
    background-color: #F5F5F5;
    border: 1px solid #BDBDBD;
    border-radius: 4px;
    padding: 4px 8px;
    color: #212121;
    font-family: Consolas;
}
```

### 4.3 下拉框（QComboBox）

#### 标准下拉框
```css
QComboBox {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 10pt;
    background-color: #FFFFFF;
}
QComboBox:hover { border-color: #165DFF; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    border: 1px solid #E5E6EB;
    selection-background-color: #E8F3FF;
    outline: none;
}
```

#### 小组合框（工具栏）
```css
QComboBox {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 9pt;
    background-color: #F5F7FA;
}
QComboBox:focus { border-color: #165DFF; }
QComboBox::drop-down { border: none; width: 20px; }
```

### 4.4 表格（QTableWidget）

```css
QTableWidget {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    background-color: #FFFFFF;
    gridline-color: #F2F3F5;
}
QTableWidget::item { padding: 6px 8px; }
QTableWidget::item:alternate { background-color: #F7F8FA; }
QHeaderView::section {
    background-color: #F7F8FA;
    border: none;
    border-bottom: 1px solid #E5E6EB;
    padding: 8px;
    font-weight: bold;
    color: #1D2129;
    font-size: 9pt;
}
```

- **行高**：36px（`verticalHeader.setDefaultSectionSize(36)`）
- **选择行为**：`SelectRows`，`NoEditTriggers`
- **滚动条**：水平/垂直均 `AlwaysOff`

### 4.5 标签页（QTabWidget）

```css
QTabWidget::pane {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QTabBar::tab {
    background-color: #F5F7FA;
    border: 1px solid #E5E6EB;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
    color: #4E5969;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #165DFF;
    border-bottom: 2px solid #165DFF;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #E8F3FF;
    color: #165DFF;
}
```

### 4.6 分组框（QGroupBox）

```css
QGroupBox {
    font-size: 10pt;
    font-weight: bold;
    color: #1D2129;
    border: 1px solid #E5E6EB;
    border-radius: 8px;
    margin-top: 10px;
    padding: 14px;
    background-color: #FFFFFF;
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
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    background-color: #FFFFFF;
    font-size: 10pt;
    outline: none;
}
QListWidget::item { padding: 5px 8px; }
QListWidget::item:selected { background-color: #E8F3FF; color: #1D2129; }
QListWidget::item:hover { background-color: #F5F7FA; }
```

### 4.8 文本编辑区（QTextEdit）

#### 代码/预览区
```css
QTextEdit {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    background-color: #F7F8FA;
    color: #4E5969;
}
```

#### Prompt 编辑区
```css
QTextEdit {
    border: 1px solid #165DFF;
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    background-color: #F7F8FA;
}
```

### 4.9 进度条（QProgressBar）

```css
QProgressBar {
    border: 1px solid #E5E6EB;
    border-radius: 4px;
    text-align: center;
    background-color: #F5F7FA;
    font-size: 10px;
}
QProgressBar::chunk {
    background-color: #165DFF;
    border-radius: 3px;
}
```

### 4.10 复选框（QCheckBox）

```css
QCheckBox { font-size: 10pt; }
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #C9CDD4;
}
QCheckBox::indicator:checked {
    background-color: #165DFF;
    border-color: #165DFF;
}
```

### 4.11 卡片（Card）

```css
QWidget {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
```

- **内部间距**：`spacing: 10`
- **标题**：`font-size: 12pt; font-weight: bold;`
- **描述**：`font-size: 10pt; color: #86909C; margin-bottom: 10px;`

### 4.12 分割线（QFrame HLine）

```css
QFrame { color: #E5E6EB; max-height: 1px; }
```

### 4.13 对话框（QDialog）

- **全局背景**：`#FFFFFF`
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
| 就绪状态 | `font-size: 9pt; color: #86909C;` |
| 运行中 | `font-size: 9pt; color: #165DFF; font-weight: normal;` |
| 完成 | `font-size: 9pt; color: #00B42A; font-weight: normal;` |
| 错误 | `font-size: 9pt; color: #F53F3F; font-weight: normal;` |

### 6.6 加载效果

- 进度条：`QProgressBar`，高度 14~22px，蓝色 chunk `#165DFF`
- 按钮加载中：背景 `#FF7D00`，`disabled` 状态

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
- **版本**：V0.3.3
- **更新日期**：2026年5月24日
- **维护规则**：每次新增/修改界面样式后，必须同步更新本文件对应章节
