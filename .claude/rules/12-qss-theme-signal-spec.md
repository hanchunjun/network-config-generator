# QSS 主题系统与信号联动开发规范（V0.3.5 教训）

> 本文件记录 V0.3.5 主题切换功能开发中暴露的问题及其规范约束，
> 后续涉及 QSS 样式、主题切换、信号联动的新功能开发，必须遵守本文件。

---

## 一、踩坑记录

### 坑 1：自定义 paintEvent 组件不响应主题切换

**现象**：`_PreviewCard` 使用 `paintEvent` 自绘预览图，切换主题后卡片颜色不变。

**根因**：构造时 `self._theme = ThemeEngine.get().get_theme(theme_id)` 保存了配色快照，`paintEvent` 永远使用这份快照数据，不随主题切换更新。

**教训**：
- **自定义绘制组件（paintEvent）必须实时从引擎获取配色数据，禁止构造时快照**
- 或者：组件必须连接 `theme_changed` 信号，在回调中调用 `self.update()` 触发重绘

**正确做法**：
```python
class _PreviewCard(QFrame):
    def __init__(self, theme_id: str, engine: ThemeEngine, parent=None) -> None:
        super().__init__(parent)
        self._theme_id = theme_id
        self._engine = engine  # 持有引擎引用，不持有配色快照
        # 连接主题变化信号
        self._engine.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_id: str) -> None:
        self.update()  # 触发重绘

    def paintEvent(self, event) -> None:
        t = self._engine.get_theme(self._theme_id)  # 实时获取，非快照
        # ... 使用 t 绘制
```

---

### 坑 2：局部 setStyleSheet 覆盖全局 QSS

**现象**：主题切换后，`ThemeSwitcherPage` 内的子控件（QLabel、QPushButton）样式不更新。

**根因**：`_apply_theme_style()` 中执行 `self.setStyleSheet("QWidget { color: ... }")`，设置了 `color` 属性。**QWidget 的局部 setStyleSheet 优先级高于 QApplication 的全局 setStyleSheet**，导致全局 QSS 对子控件的样式设置被覆盖。

**教训**：
- **局部 setStyleSheet 只允许设置页面级属性（背景色、字体），禁止设置 color 属性**
- 如果需要对子控件设置颜色，必须使用具体的选择器（如 `QLabel#title`），不能用 `QWidget` 全局选择器
- 更安全的做法：局部样式表只设置 `background-color` 和 `font-family`，其他全部交给全局 QSS

**正确做法**：
```python
def _apply_theme_style(self) -> None:
    t = self._engine.current_theme
    # ✅ 只设置页面级背景，不碰 color
    self.setStyleSheet(f"""
        ThemeSwitcherPage {{
            background-color: {t['page_bg']};
            font-family: {t['font_ui']};
        }}
    """)
    # ✅ 需要设置特定控件颜色时，用具体选择器
    self._title_label.setStyleSheet(f"color: {t['text_main']};")
```

**错误做法**：
```python
# ❌ QWidget 全局 color 会覆盖所有子控件的文字颜色
self.setStyleSheet(f"""
    QWidget {{
        color: {t['text_main']};  /* 危险！覆盖全局 QSS */
    }}
""")
```

---

### 坑 3：信号链路未全覆盖（V0.3.5 首轮实现）

**现象**：`ThemeSwitcherPage` 连接了 `theme_changed` 信号，但 `_PreviewCard` 没有连接，导致卡片预览不刷新。

**根因**：父组件连接了信号，但子组件未连接，信号链路断裂。

**教训（修正）**：
- 子组件**禁止直接连接** `theme_changed` 信号并调用 `self.update()`，否则会导致事件循环死锁（见坑 4）
- 正确做法：子组件不连接信号，由父组件在 `_on_theme_changed` 中集中调用 `card.update()`

---

### 坑 4：信号嵌套触发事件循环死锁（V0.3.5 致命 Bug）

**现象**：点击主题卡片后程序挂起，日志显示 `主题已切换: VS Code 风格` 后无后续输出。

**根因**：
```
_PreviewCard.mousePressEvent()
  → clicked.emit()
    → ThemeSwitcherPage._switch_theme()
      → ThemeEngine.apply()
        → theme_changed.emit()
          → _PreviewCard._on_theme_changed()
            → self.update()    ← 在 clicked 信号发射过程中调用，触发事件循环嵌套
```
当父组件同时有 `setStyleSheet()` 设置时，`self.update()` 与 `clicked.emit()` 的事件循环嵌套导致 PyQt5 挂起。

**教训**：
- **子组件绝对禁止在 `theme_changed` 回调中调用 `self.update()`**，如果子组件同时通过其他信号（如 `clicked`）触发主题切换
- **集中刷新原则**：所有子组件的刷新由父组件在 `_on_theme_changed` 中统一调用 `card.update()`
- **信号连接审查**：新增信号连接时，必须审查是否存在"信号 A 触发 → 槽内发射信号 B → 信号 B 的槽内调用 UI 方法"的嵌套路径

**正确做法**：
```python
# 子组件：不连接 theme_changed 信号
class _PreviewCard(QFrame):
    def __init__(self, theme_id, engine, parent=None):
        super().__init__(parent)
        self._theme_id = theme_id
        self._engine = engine
        # 不连接 theme_changed，避免死锁

# 父组件：集中刷新所有子组件
class ThemeSwitcherPage(QWidget):
    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()
        self._update_card_selection()
        # 集中刷新所有预览卡片
        for card in self._cards.values():
            card.update()
```

**错误做法**：
```python
# ❌ 子组件连接 theme_changed 并在回调中调用 self.update()
class _PreviewCard(QFrame):
    def __init__(self, theme_id, engine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self._engine.theme_changed.connect(self._on_theme_changed)  # 危险！

    def _on_theme_changed(self, theme_id: str) -> None:
        self.update()  # 与 clicked.emit() 嵌套时导致死锁
```

---

## 二、强制规范

### 规范 1：自定义绘制组件必须实时获取主题数据

| 项目 | 要求 |
|------|------|
| 适用场景 | 任何使用 `paintEvent` 自绘的组件 |
| 强制规则 | 禁止在 `__init__` 中保存配色快照；`paintEvent` 内必须实时从 `ThemeEngine` 获取数据 |
| 信号要求 | 必须连接 `theme_changed` 信号，在回调中调用 `self.update()` |

### 规范 2：局部 setStyleSheet 禁止设置 color 属性

| 项目 | 要求 |
|------|------|
| 适用场景 | 任何页面的 `_apply_theme_style` 或类似方法 |
| 强制规则 | 局部 `setStyleSheet` 只能设置 `background-color`、`font-family`、`border` 等几何/背景属性 |
| 禁止规则 | 禁止在局部样式表中使用 `QWidget { color: ... }` 全局选择器覆盖文字颜色 |
| 例外 | 可以使用具体选择器（如 `QLabel#xxx`、`QPushButton.yyy_class`）设置特定控件颜色 |

### 规范 3：信号连接必须审查嵌套路径

| 项目 | 要求 |
|------|------|
| 适用场景 | 任何组件连接 `theme_changed` 或其他全局信号 |
| 强制规则 | 子组件禁止连接 `theme_changed` 并在回调中调用 `self.update()`，如果该子组件同时通过其他信号触发主题切换 |
| 正确做法 | 父组件在 `_on_theme_changed` 中集中调用 `card.update()` 刷新所有子组件 |
| 审查要点 | 检查是否存在"信号 A → 槽内发射信号 B → 信号 B 的槽内调用 UI 方法"的嵌套路径 |

### 规范 4：新模块集成必须全链路验证

| 项目 | 要求 |
|------|------|
| 适用场景 | 新增页面/模块集成到主窗口导航 |
| 检查项 | 1. `MODULES` 列表 2. `_create_module_stack` 3. `page_map` 4. `keyPressEvent` 快捷键 5. 状态栏文案 |
| 验证要求 | 代码审查时必须逐项勾选，缺一不可 |

### 规范 4：功能上线前必须端到端验证

| 项目 | 要求 |
|------|------|
| 适用场景 | 任何涉及 UI 交互的新功能 |
| 最低验证 | 1. 代码审查通过 2. 单元测试通过 3. **实际运行程序手动操作一遍完整流程** |
| 禁止行为 | 仅凭"代码逻辑正确"就打包发布，不进行实际操作验证 |

---

## 三、V0.3.5 主题切换功能测试清单

打包前，必须手动操作验证以下场景，全部通过方可发布：

- [ ] 启动程序，导航栏显示「🎨 主题切换」按钮
- [ ] 点击「🎨 主题切换」按钮，页面切换到主题切换面板
- [ ] Ctrl+8 快捷键可切换到主题切换面板
- [ ] 主题切换面板显示三张预览卡片（Raycast / VS Code / Business）
- [ ] 当前激活的卡片有选中高亮边框
- [ ] 点击 Raycast 卡片 → 全局界面切换为紫橙渐变风格
- [ ] 点击 VS Code 卡片 → 全局界面切换为深蓝黑风格
- [ ] 点击 Business 卡片 → 全局界面切换为浅灰白风格，文字清晰可读
- [ ] 切换主题后，预览卡片的选中高亮跟随变化
- [ ] 关闭程序重启后，主题设置自动恢复
- [ ] Business 主题下所有页面文字对比度足够（无"白底灰字"现象）

---

## 四、版本信息

- **版本**：NetOps V0.3.5 补丁
- **日期**：2026年5月25日
- **触发事件**：用户报告"主题切换无效"和"有的地方白有的地方黑"
- **根因**：paintEvent 快照不更新 + 局部 setStyleSheet 覆盖全局 QSS + 信号链路断裂
