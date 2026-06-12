# NetOps 界面设计规范（V0.4.3）

> **唯一权威标准**。所有界面代码的生成与修改，必须以本文件为唯一标准，禁止脱离规范的主观发挥。

---

## 一、主题体系

**固定使用浅色商务风格**，主题切换功能已取消。

**引擎**：`src/core/theme_engine.py` — `ThemeEngine.get()` 单例，`apply(app)` 初始化全局 QSS。全局 QSS 统一控制所有容器背景色（使用 `!important` 标记），各页面只需设置页面自身背景 + 刷新按钮样式。

### 设计风格

| 属性 | 值 |
|------|-----|
| 风格 | Minimalism & Swiss Style（极简与瑞士风格） |
| 主色 | `#1A73E8`（品牌蓝） |
| 背景 | `#F5F5F5`（浅灰白） |
| 卡片 | `#FFFFFF`（纯白） |
| 字体 | Microsoft YaHei / Segoe UI |
| 代码字体 | Consolas / Courier New |
| 圆角 | 按钮 5px，卡片 8px，输入框 5px |
| 间距 | 基础单位 4px |

---

## 二、色彩 Token

### 主色

| Key | 色值 | 用途 |
|-----|------|------|
| `primary` | `#1A73E8` | 主按钮边框、焦点、进度条填充 |
| `primary_hover` | `#1557B0` | hover 态 |
| `primary_pressed` | `#0D47A1` | pressed 态 |
| `primary_light` | `#4285F4` | 描边按钮文字/边框、链接、选中条 |

### 功能色

| Key | 色值 | 用途 |
|-----|------|------|
| `success` / `success_hover` | `#0F9D58` / `#0B8043` | 成功状态、通过指示 |
| `warning` / `warning_hover` | `#F4B400` / `#F09300` | 进行中、警告提示 |
| `danger` / `danger_hover` | `#DB4437` / `#C5221F` | 危险操作、错误状态 |
| `info` | `#4285F4` | 信息提示 |

### 中性色

| Key | 色值 | 用途 |
|-----|------|------|
| `page_bg` | `#F5F5F5` | 页面背景 |
| `card_bg` | `#FFFFFF` | 卡片/面板背景 |
| `sidebar_bg` | `#F0F0F0` | 侧栏背景 |
| `toolbar_bg` | `#E8E8E8` | 工具栏/表头背景 |
| `hover_bg` | `#E8EAED` | hover 背景 |
| `code_bg` | `#F3F4F6` | 代码区背景 |
| `input_bg` | `#FAFAFA` | 输入框背景 |
| `nav_bg` | `#F0F0F0` | 导航栏背景 |
| `border` | `#DADCE0` | 边框 |
| `input_border` | `#B0B0B8` | 输入框边框 |
| `border_deep` | `#E8EAED` | 深色边框 |
| `text_primary` | `#202124` | 主要文字 |
| `text_main` | `#3C4043` | 正文文字 |
| `text_secondary` | `#4A4A4A` | 次要文字 |
| `text_tertiary` | `#808080` | 三级文字 |
| `text_disabled` | `#9AA0A6` | 禁用文字 |

---

## 三、组件规范

### 3.1 按钮（核心 · 三级分类）

**唯一来源**：全局 QSS 统一控制，各页面只需刷新按钮样式。

| 级别 | 默认边框 | hover 边框 | 用途 |
|------|---------|-----------|------|
| 主按钮 | `border_deep`（灰） | `primary`（蓝） | 主操作（生成/保存/创建）|
| 辅助按钮 | `border_deep`（灰） | `text_secondary` | 辅助（清空/刷新/导出）|
| 危险按钮 | `border_deep`（灰） | `danger`（红） | 破坏性（删除/移除）|

**使用方式**：
```python
t = ThemeEngine.get().current_theme
btn.setStyleSheet(f"QPushButton {{ background-color: transparent; border: 1px solid {t['border']}; ...")
```

### 3.2 输入框

| 属性 | 值 |
|------|-----|
| 背景 | `input_bg`（`#FAFAFA`） |
| 边框 | `input_border`（`#B0B0B8`） |
| 圆角 | 5px |
| 字体 | Microsoft YaHei |

### 3.3 卡片

| 属性 | 值 |
|------|-----|
| 背景 | `card_bg`（`#FFFFFF`） |
| 边框 | `border_deep`（`#E8EAED`） |
| 圆角 | 8px |
| 内边距 | 10px |

### 3.4 表格

| 属性 | 值 |
|------|-----|
| 背景 | `card_bg`（`#FFFFFF`） |
| 网格线 | `border_deep`（`#E8EAED`） |
| 表头背景 | `toolbar_bg`（`#E8E8E8`） |
| 选中行 | `selection_bg`（`rgba(26,115,232,0.08)`） |

---

## 四、间距规范

| 属性 | 值 |
|------|-----|
| 页面边距 | 12-16px |
| 组件间距 | 4-8px |
| 卡片内边距 | 10px |
| 按钮内边距 | 5px 8px |

---

## 五、各页面职责

1. **全局 QSS 统一控制容器背景色**（QScrollArea、QTabWidget::pane、QGroupBox、QLineEdit、QComboBox、QTableWidget、QTextEdit、QListWidget 等）
2. **各页面只需设置页面自身背景色**：`self.setStyleSheet(f"PageName {{ background-color: {t['page_bg']}; }}")`
3. **各页面只需刷新按钮样式**：遍历按钮，调用 `btn.setStyleSheet(...)`
4. **禁止 `findChildren` 遍历容器控件**：容器样式由全局 QSS 控制
5. **禁止在局部 `setStyleSheet` 中设置容器背景色**：由全局 QSS `!important` 控制

---

## 六、版本信息

- **版本**：NetOps V0.4.3 固定浅色主题版
- **日期**：2026年6月4日
- **设计风格**：Minimalism & Swiss Style（极简与瑞士风格）
- **目标平台**：PyQt5 桌面应用（Windows 10/11）
