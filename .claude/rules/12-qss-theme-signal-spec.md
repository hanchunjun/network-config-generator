# QSS 全局样式规范（V0.4.3）

> 本文件记录 V0.4.3 主题系统简化后的开发规范。
> 主题切换已取消，固定使用浅色商务风格。全局 QSS 统一控制所有容器背景色。

---

## 一、核心设计

### 1.1 固定浅色主题

- 主题引擎只保留 `Theme.LIGHT`（商务浅灰白风格）
- `ThemeEngine.apply(app)` 签名只接受 `app` 参数
- 全局 QSS 使用 `!important` 标记强制覆盖局部样式

### 1.2 全局 QSS 统一控制容器背景色

全局 QSS 中定义了以下容器的背景色（使用 `!important`）：

| 容器 | 背景色 | 说明 |
|------|--------|------|
| `QMainWindow` | `page_bg` | 窗口底色 |
| `QScrollArea` 及其子控件 | `page_bg` | 解决 viewport 默认白色 |
| `QTabWidget::pane` | `card_bg` | 标签页内容区 |
| `QTabBar::tab` | `toolbar_bg` | 标签栏 |
| `QGroupBox` | `card_bg` | 分组框 |
| `QLineEdit` | `input_bg` | 输入框 |
| `QComboBox` | `input_bg` | 下拉框 |
| `QTableWidget` | `card_bg` | 表格 |
| `QListWidget` | `card_bg` | 列表 |
| `QTextEdit` | `code_bg` | 文本编辑区 |
| `QProgressBar` | `hover_bg` | 进度条 |
| `QStatusBar` | `toolbar_bg` | 状态栏 |
| `QMenu` | `card_bg` | 菜单 |
| `QDialog` | `card_bg` | 对话框 |
| `QSplitter::handle` | `border` | 分割线 |
| `QLabel` | transparent | 标签背景透明 |

### 1.3 各页面职责

- **只需设置页面自身背景色**：`self.setStyleSheet(f"PageName {{ background-color: {t['page_bg']}; }}")`
- **只需刷新按钮样式**：遍历按钮，调用 `btn.setStyleSheet(...)`
- **禁止 `findChildren` 遍历容器控件**：容器样式由全局 QSS 控制
- **禁止在局部 `setStyleSheet` 中设置 `color` 属性**：文字颜色由全局 QSS 控制

---

## 二、踩坑记录

### 坑 1：局部 setStyleSheet 覆盖全局 QSS

**现象**：某些控件样式不更新。

**根因**：局部 `setStyleSheet` 优先级高于全局 QSS。

**教训**：
- **全局 QSS 使用 `!important` 标记**
- **各页面不在局部设置容器背景色**

### 坑 2：setStyleSheet 替换所有样式

**现象**：调用 `self.setStyleSheet(...)` 后，之前设置的样式全部丢失。

**教训**：
- **合并所有样式到一次 `setStyleSheet` 调用**
- **避免多次调用 `setStyleSheet`**

### 坑 3：简化时遗漏方法

**现象**：简化 `_apply_theme_style` 时去掉了 `_secondary_btn_style` 等方法，但调用处未同步修改。

**教训**：
- **简化时必须检查所有引用**
- **添加 `hasattr` 类型检查**

---

## 三、强制规范

### 规范 1：全局 QSS 使用 `!important`

| 项目 | 要求 |
|------|------|
| 适用场景 | 全局 QSS 中所有背景色属性 |
| 强制规则 | 所有容器背景色必须使用 `!important` 标记 |

### 规范 2：各页面只设置页面背景 + 按钮样式

| 项目 | 要求 |
|------|------|
| 适用场景 | 所有页面的 `_on_theme_changed` / `_apply_theme_style` |
| 强制规则 | 只设置页面自身背景色和按钮样式 |
| 禁止规则 | 禁止 `findChildren(QGroupBox)` 等遍历容器控件 |

### 规范 3：局部 setStyleSheet 禁止设置 color 属性

| 项目 | 要求 |
|------|------|
| 适用场景 | 任何页面的 `_apply_theme_style` |
| 强制规则 | 只能设置 `background-color`、`font-family`、`border` 等几何/背景属性 |
| 禁止规则 | 禁止使用 `QWidget { color: ... }` 全局选择器 |

---

## 四、版本信息

- **版本**：NetOps V0.4.3 固定浅色主题版
- **日期**：2026年6月4日
- **变更**：取消主题切换，固定浅色商务风格
