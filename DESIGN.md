# NetOps 界面设计规范（V0.4.1）

> **唯一权威标准**。所有界面代码的生成与修改，必须以本文件为唯一标准，禁止脱离规范的主观发挥。

---

## 一、主题体系

| ID | 名称 | 定位 | 默认 |
|----|------|------|------|
| `vscode` | VS Code 风格 | 深蓝黑 · 锐利 · 开发者工具感 | ✅ |
| `raycast` | Raycast 风格 | 紫橙渐变 · 毛玻璃 · 大圆角 | |
| `business` | 商务沉稳风格 | 浅灰白底 · 品牌蓝 · 政企级 | |

**引擎**：`src/core/theme_engine.py` — `ThemeEngine.get()` 单例，`apply(app, theme_id)` 切换，发射 `theme_changed` 信号。

---

## 二、色彩 Token

### 主色

| Key | 色值 | 用途 |
|-----|------|------|
| `primary` | `#3B7CFF` | 主按钮边框、焦点、进度条填充 |
| `primary_hover` | `#2962D9` | hover 态 |
| `primary_pressed` | `#1E4BB8` | pressed 态 |
| `primary_light` | `#5C8AFF` | 描边按钮文字/边框、链接、选中条 |

### 功能色

| Key | 色值 | 用途 |
|-----|------|------|
| `success` / `success_hover` | `#3DD66A` / `#2BA84E` | 成功状态、通过指示 |
| `warning` / `warning_hover` | `#FFB040` / `#CC8C30` | 进行中、警告提示 |
| `danger` / `danger_hover` | `#FF5C5C` / `#CC3E3E` | 危险操作、错误状态 |
| `accent` | `#00D4E8` | 数据流高亮、实时指示 |

### 中性色

| Key | 用途 |
|-----|------|
| `text_main` | 标题、表格头、输入框文字 |
| `text_secondary` | 正文、标签、导航默认 |
| `text_tertiary` | 占位符、禁用状态 |
| `border` / `border_deep` | 边框（浅/深两档） |
| `page_bg` | 页面背景 |
| `card_bg` | 卡片/面板背景 |
| `input_bg` | 输入框背景 |
| `toolbar_bg` | 工具栏/表头背景 |
| `hover_bg` | hover 背景 |
| `sidebar_bg` | 侧栏背景 |

---

## 三、字体

| 属性 | 值 |
|------|-----|
| UI 字体 | `'Segoe UI', 'Microsoft YaHei', sans-serif` |
| 等宽字体 | `'Consolas', 'Courier New', monospace` |

### 字号层级

| 层级 | 字号 | 场景 |
|------|------|------|
| L1 标题 | **14pt** | 页面大标题、Logo |
| L2 分组 | **12pt** | 区块标题、卡片标题 |
| L3 正文 | **11pt** | 表单、输入框、表格内容、标准按钮 |
| L4 辅助 | **10pt** | 提示、状态栏、hint 文字 |
| L5 紧凑 | **9pt** | 表格头部、工具栏按钮、hint_label（仅非正文场景） |

字重：标题/主按钮/表头 → `bold`；次级 → `500`；普通 → `normal`

> **V0.3.8 变更**：新增 L5(9pt) 紧凑层级，仅用于表格头部、工具栏按钮和 hint_label，正文保持 11pt 不变。

---

## 四、组件规范

### 4.1 按钮（核心 · 三级分类）

> **唯一来源**：所有按钮样式由 `ThemeEngine.qss('btn_xxx')` 统一输出。禁止各页面自行内联 QSS 或定义 `_xxx_btn_style()` 方法。

#### 一级 · 主操作按钮 `btn_primary`

透明底 + **蓝色描边 + 蓝色文字** + bold。用于核心动作。

| 状态 | 背景 | 边框 | 文字 |
|------|------|------|------|
| default | transparent | `primary_light` | `primary_light` |
| hover | `sidebar_bg` | `primary` | `primary` |
| pressed | `hover_bg` | `primary_hover` | `primary_hover` |
| disabled | transparent | `border` | `text_tertiary` |

**适用场景**：生成命令、保存结果、创建项目、提交、复制全部、新增模板等**主要正向操作**。

#### 二级 · 常规按钮 `btn_default`

透明底 + **中性深边框 + 主文字色**。用于辅助/中性动作。

| 状态 | 背景 | 边框 | 文字 |
|------|------|------|------|
| default | transparent | `border_deep` | `text_main` |
| hover | `hover_bg` | `text_secondary` | `text_secondary` |
| pressed | `page_bg` | `text_main` | `text_main` |
| disabled | transparent | `border` | `text_tertiary` |

**适用场景**：清空、重置、刷新、编辑、导出、重命名、保存（非提交类）、查看详情等**辅助操作**。

#### 三级 · 危险按钮 `btn_danger`

透明底 + **红色描边 + 红色文字**。用于破坏性操作。

| 状态 | 背景 | 边框 | 文字 |
|------|------|------|------|
| default | transparent | `danger` | `danger` |
| hover | transparent | `danger_hover` | `danger_hover` |
| disabled | transparent | `border` | `text_tertiary` |

**适用场景**：删除、移除、清除数据等**不可逆操作**。

#### 选中状态（selected）

适用于导航按钮、厂家/设备选择按钮、标签页等需要保持高亮态的场景。

| 按钮类型 | 选中态样式 |
|---------|-----------|
| 导航按钮 | `selection_bg` 背景 + `primary_light` 文字 + bold |
| 厂家/设备选择按钮 | `transparent` 背景 + `border_deep` 边框 + bold |
| 标签页选中 | `card_bg` 底 + `primary_light` 文字 + 底部 `primary_light` 条 |

**交互规则**：
- 选中态互斥：同一组内仅一个按钮可处于选中态
- 点击已选中按钮不取消选中（保持高亮）
- 选中态优先级高于 hover（hover 不覆盖选中态颜色）

#### 公共尺寸

| 档位 | 高度 | padding | 字号 | 圆角 | 场景 |
|------|------|---------|------|------|------|
| 标准 | **28px** | `4px 10px` | 11pt bold | 5px | 页面主体按钮 |
| 小 | **24px** | `2px 6px` | 9pt | 3px | 工具栏、文件三件套、表格行内 |
| 导航 | **24px** | `2px 6px` | 11pt | 5px | 顶部导航栏 |

按钮间距：横向并排 `4px`，纵向堆叠 `4px`。

> **V0.3.8 变更**：按钮整体压缩 2px，标准 30→28px，小按钮 26→24px，导航 28→24px。配合 L5(9pt) 字号确保文字不裁剪。

#### 使用方式

```python
t = ThemeEngine.get().current_theme
btn.setStyleSheet(t['qss']('btn_primary'))   # 主操作
btn.setStyleSheet(t['qss']('btn_default'))   # 常规
btn.setStyleSheet(t['qss']('btn_danger'))    # 危险
```

#### 特殊按钮

| 类型 | 规则 |
|------|------|
| 导航按钮 | 无边框，hover 底色加深，active 用 `selection_bg` + `primary_light` 文字 |
| AI 按钮 | 同 `btn_primary`，可加紫色变体（`accent` 色） |
| 状态指示按钮 | 实心小方块（90×28），用功能色填充（成功绿/警告橙/危险红） |

### 4.2 输入框

- 高度 **26px**，padding `4px 8px`，圆角 `5px`
- 边框：默认 `input_border`，focus 变 `primary`
- 背景：`input_bg`，文字 `text_main`
- 只读：背景 `page_bg`，文字 `primary_light`，字体 Consolas

### 4.3 下拉框

- 高度 **26px**，圆角 `5px`
- 边框 `input_border`，hover/focus → `primary`
- 下拉列表：`selection_background_color: selection_bg`

### 4.4 表格

- 行高 **28px**，`SelectRows`，`NoEditTriggers`
- 交替行：`alternate → hover_bg`
- 选中行：`selection_bg` + `text_main`
- 表头：`toolbar_bg` 底 + `text_secondary` 加粗，字号 **9pt**（L5）
- item padding：`4px 6px`

### 4.5 标签页

- Tab 未选：`toolbar_bg` 底 + `text_tertiary` 文字
- Tab 选中：`card_bg` 底 + `primary_light` 文字 + 底部 `primary_light` 条
- 圆角：上左/上右 `8px`

### 4.6 分组框

- 圆角 `8px`，padding `14px`，标题加粗 `text_main`
- 边框 `border`，背景 `card_bg`

### 4.7 其他组件

| 组件 | 关键参数 |
|------|---------|
| 复选框 | indicator 16×16，圆角 3px，选中 `primary` 填充 |
| 进度条 | 高 16px，chunk `primary`，圆角 3px |
| 卡片 | 圆角 8px，padding 14px，`card_bg` + `border` |
| 分割线 | `border_deep` 色，高度 1px |
| 对话框 | 背景 `card_bg`，登录 400×320，激活 580×560 |

---

## 五、布局 Token

### 间距

| Token | 值 | 场景 |
|-------|----|------|
| xs | 2px | 极紧凑 |
| sm | 4px | 行内间距、工具栏、文件三件套 |
| md | 8px | 表单行距、卡片内部 |
| lg | 12px | 页面边距、区块间距 |

> **V0.3.8 变更**：间距整体压缩一级（sm 6→4, md 12→8, lg 16→12），参考 Linear(4px base) 和 Raycast(8px base) 的高密度桌面工具标准。

### 圆角

| Token | 值 | 适用 |
|-------|----|------|
| sm | 3px | 小按钮、复选框、进度条 |
| md | 5px | 按钮、输入框、下拉框 |
| lg | 8px | GroupBox、卡片、Tab |

### 边框

统一 **1px solid**，颜色引用主题 Token，禁止硬编码。

### 页面边距参考

| 区域 | margin | spacing |
|------|--------|---------|
| 配置页根布局 | `(lg, md, lg, md)` 即 `(12,8,12,8)` | `md`(8) |
| 运维页主布局 | `(lg, md, lg, md)` 即 `(12,8,12,8)` | `sm`(4) |
| 单点运维 | `(md, sm, md, sm)` 即 `(8,4,8,4)` | `sm`(4) |
| AI 分析 | `(lg, md, lg, md)` 即 `(12,8,12,8)` | `md`(8) |

---

## 六、交互规范

| 规则 | 说明 |
|------|------|
| 危险操作 | 必须有确认对话框 |
| 激活/登录弹窗 | 无关闭按钮，禁止 ESC |
| 所有交互件 | 必须定义 hover / focus / disabled 三态 |
| 日志 | 禁止 `print()`，使用 `netops_logger` |
| QThread | 必须存为实例变量 `self._xxx_thread` |
| 文件操作 | 必须 `.tmp` + `os.replace` 原子写入 |
| 路径 | 禁止硬编码绝对路径，使用 `get_app_dir()` 等 API |

### 交互状态汇总

| 组件 | 状态 | 样式规则 |
|------|------|---------|
| 按钮 | default / hover / pressed / disabled / selected | 见 4.1 |
| 输入框 | default / focus / disabled / readonly | 见 4.2 |
| 下拉框 | default / hover / focus / expanded | expanded 时边框变 `primary` |
| 复选框 | unchecked / checked / indeterminate | checked 用 `primary` 填充，indeterminate 用 `primary_light` |
| 表格行 | default / alternate / selected | selected 用 `selection_bg` + `text_main` |
| 标签页 | unselected / selected | 见 4.5 |
| 进度条 | running / done / error | running 用 `primary` chunk，done 用 `success`，error 用 `danger` |
| 导航按钮 | default / hover / active | active 用 `selection_bg` + `primary_light` |
| 对话框 | open / close | 打开时背景 `card_bg`，无动画（即时显示） |

### 状态提示

| 类型 | 样式 |
|------|------|
| 就绪 | `10pt` + `text_tertiary` |
| 运行中 | `10pt` + `accent` |
| 完成 | `10pt` + `success` |
| 错误 | `10pt` + `danger` |

---

## 七、禁止行为

1. 禁止使用规范外颜色值（先更新本文件）
2. 禁止脱离本规范自创界面风格
3. 禁止在页面代码中内联按钮 QSS（必须调用 `ThemeEngine.qss()`）
4. 禁止定义 `_xxx_btn_style()` 私有方法（已废弃）
5. 禁止硬编码颜色/字号/间距
6. 禁止危险操作无确认对话框
7. 禁止 QThread 存为局部变量
8. 禁止 `print()` 调试输出
9. 禁止非原子文件写入
10. 禁止硬编码路径

---

## 八、DPI 渲染规范

固定 **96DPI（100%）** 渲染，不受系统缩放影响。

| 规则 | 实现 |
|------|------|
| 关闭 Qt DPI 缩放 | `AA_EnableHighDpiScaling=False`, `AA_DisableHighDpiScaling=True` |
| 屏蔽环境变量 | 删除 `QT_AUTO_SCREEN_SCALE_FACTOR` 等，设 `QT_ENABLE_HIGHDPI_SCALING=0` |
| Fusion 样式 | `app.setStyle("Fusion")` |
| 进程 Unaware | `SetProcessDpiAwareness(0)` + `app.manifest` |
| 抗锯齿 | `QFont.PreferAntialias` 全局字体策略 |
| 固定尺寸 | 所有控件用绝对 pt/px，禁止 em/% |

入口统一使用 `src/utils/app_factory.py` 的 `create_application()`。

---

## 维护信息

| 项目 | 值 |
|------|-----|
| 版本 | V0.4.1 |
| 更新日期 | 2026年5月30日 |
| 规则 | 每次修改界面后同步更新本文件 |
