#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量命令生成器
支持模板+参数(%a~%f)→批量生成配置命令
支持预置模板（四厂商VLAN/接口VLAN）+ 用户自定义模板管理
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QGroupBox, QTextEdit, QScrollArea,
    QApplication, QGridLayout, QFileDialog,
    QMessageBox, QWidget as QW, QComboBox, QInputDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from src.utils.resource_path import get_config_path
from src.utils.file_operators import JSONFileManager
from src.core.theme_engine import ThemeEngine


# ─────────────────────────────────────────────
# 预置模板数据
# ─────────────────────────────────────────────
def _build_preset_templates() -> List[dict]:
    """构建12个预置模板数据列表（四厂商 × VLAN + 接口VLAN + DHCP）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    presets: List[dict] = [
        # ── 锐捷 ──
        {
            "id": "preset_ruijie_vlan",
            "name": "锐捷-VLAN批量创建",
            "category": "preset",
            "vendor": "锐捷",
            "type": "vlan",
            "content": "vlan %a\n name VLAN_%a\nexit\n",
            "params": ["a"],
            "description": "锐捷交换机批量创建VLAN并命名（%a=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_ruijie_interface_vlan",
            "name": "锐捷-接口划分VLAN",
            "category": "preset",
            "vendor": "锐捷",
            "type": "interface_vlan",
            "content": "interface GigabitEthernet 0/%a\n switchport mode access\n switchport access vlan %b\nexit\n",
            "params": ["a", "b"],
            "description": "锐捷交换机接口划入VLAN（%a=接口编号 %b=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_ruijie_dhcp",
            "name": "锐捷-DHCP地址池",
            "category": "preset",
            "vendor": "锐捷",
            "type": "dhcp",
            "content": "ip dhcp pool VLAN_%a\n network 192.168.%b.0 255.255.255.0\n default-router 192.168.%b.254\n dns-server 61.147.37.1 218.2.135.1\nexit\n",
            "params": ["a", "b"],
            "description": "锐捷交换机DHCP地址池（%a=VLAN号 %b=网段第三段）",
            "created_at": now,
        },
        # ── 华为 ──
        {
            "id": "preset_huawei_vlan",
            "name": "华为-VLAN批量创建",
            "category": "preset",
            "vendor": "华为",
            "type": "vlan",
            "content": "vlan batch %a to %b\n",
            "params": ["a", "b"],
            "description": "华为交换机批量创建VLAN（%a=起始VLAN %b=结束VLAN）",
            "created_at": now,
        },
        {
            "id": "preset_huawei_interface_vlan",
            "name": "华为-接口划分VLAN",
            "category": "preset",
            "vendor": "华为",
            "type": "interface_vlan",
            "content": "interface GigabitEthernet 0/%a\n port link-type access\n port default vlan %b\nquit\n",
            "params": ["a", "b"],
            "description": "华为交换机接口划入VLAN（%a=接口编号 %b=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_huawei_dhcp",
            "name": "华为-DHCP地址池",
            "category": "preset",
            "vendor": "华为",
            "type": "dhcp",
            "content": "ip pool VLAN_%a\n gateway-list 192.168.%b.254\n network 192.168.%b.0 mask 255.255.255.0\n dns-list 61.147.37.1 218.2.135.1\nquit\ndhcp enable\n",
            "params": ["a", "b"],
            "description": "华为交换机DHCP地址池（%a=VLAN号 %b=网段第三段）",
            "created_at": now,
        },
        # ── H3C ──
        {
            "id": "preset_h3c_vlan",
            "name": "H3C-VLAN批量创建",
            "category": "preset",
            "vendor": "H3C",
            "type": "vlan",
            "content": "vlan %a\n name VLAN_%a\nquit\n",
            "params": ["a"],
            "description": "H3C交换机创建VLAN并命名（%a=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_h3c_interface_vlan",
            "name": "H3C-接口划分VLAN",
            "category": "preset",
            "vendor": "H3C",
            "type": "interface_vlan",
            "content": "interface GigabitEthernet 0/%a\n port access vlan %b\nquit\n",
            "params": ["a", "b"],
            "description": "H3C交换机接口划入VLAN（%a=接口编号 %b=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_h3c_dhcp",
            "name": "H3C-DHCP地址池",
            "category": "preset",
            "vendor": "H3C",
            "type": "dhcp",
            "content": "dhcp server ip-pool VLAN_%a\n gateway-list 192.168.%b.254\n network 192.168.%b.0 mask 255.255.255.0\n dns-list 61.147.37.1 218.2.135.1\nquit\ndhcp enable\n",
            "params": ["a", "b"],
            "description": "H3C交换机DHCP地址池（%a=VLAN号 %b=网段第三段）",
            "created_at": now,
        },
        # ── 思科 ──
        {
            "id": "preset_cisco_vlan",
            "name": "思科-VLAN批量创建",
            "category": "preset",
            "vendor": "思科",
            "type": "vlan",
            "content": "vlan %a\n name VLAN_%a\nexit\n",
            "params": ["a"],
            "description": "Cisco交换机创建VLAN并命名（%a=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_cisco_interface_vlan",
            "name": "思科-接口划分VLAN",
            "category": "preset",
            "vendor": "思科",
            "type": "interface_vlan",
            "content": "interface GigabitEthernet 0/%a\n switchport mode access\n switchport access vlan %b\nexit\n",
            "params": ["a", "b"],
            "description": "Cisco交换机接口划入VLAN（%a=接口编号 %b=VLAN号）",
            "created_at": now,
        },
        {
            "id": "preset_cisco_dhcp",
            "name": "思科-DHCP地址池",
            "category": "preset",
            "vendor": "思科",
            "type": "dhcp",
            "content": "ip dhcp pool VLAN_%a\n network 192.168.%b.0 255.255.255.0\n default-router 192.168.%b.254\n dns-server 61.147.37.1 218.2.135.1\nexit\n",
            "params": ["a", "b"],
            "description": "Cisco交换机DHCP地址池（%a=VLAN号 %b=网段第三段）",
            "created_at": now,
        },
    ]
    return presets


# ─────────────────────────────────────────────
# 参数组控件
# ─────────────────────────────────────────────
class ParamGroupWidget(QGroupBox):
    loop_toggled = pyqtSignal(str, bool)

    def __init__(self, label: str, param_char: str, parent=None):
        super().__init__(f"参数{label}:", parent)
        self.param_char = param_char
        self._theme = ThemeEngine.get().current_theme
        t = self._theme
        self.setStyleSheet(
            f"QGroupBox {{"
            f"  font-size: 10pt; font-weight: bold; color: {t['text_main']};"
            f"  border: 1px solid {t['border']}; border-radius: {t['radius_lg']}px;"
            f"  margin-top: 8px; padding-top: 10px;"
            f"}}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}"
        )
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 8)
        layout.setSpacing(5)

        row = 0
        layout.addWidget(QLabel("基数:"), row, 0)
        self.base_spin = QSpinBox()
        self.base_spin.setRange(0, 99999)
        self.base_spin.setValue(1)
        self.base_spin.setMinimumHeight(22)
        self.base_spin.setMinimumWidth(50)
        layout.addWidget(self.base_spin, row, 1)

        layout.addWidget(QLabel("步长:"), row, 2)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(-99999, 99999)
        self.step_spin.setValue(1)
        self.step_spin.setMinimumHeight(22)
        self.step_spin.setMinimumWidth(50)
        layout.addWidget(self.step_spin, row, 3)

        row = 1
        self.repeat_cb = QCheckBox("重复次数:")
        layout.addWidget(self.repeat_cb, row, 0, 1, 2)
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 9999)
        self.repeat_spin.setValue(1)
        self.repeat_spin.setEnabled(False)
        self.repeat_spin.setMinimumHeight(22)
        self.repeat_spin.setMinimumWidth(48)
        layout.addWidget(self.repeat_spin, row, 2, 1, 2)

        row = 2
        self.loop_cb = QCheckBox("循环个数:")
        layout.addWidget(self.loop_cb, row, 0, 1, 2)
        self.loop_spin = QSpinBox()
        self.loop_spin.setRange(1, 9999)
        self.loop_spin.setValue(12)
        self.loop_spin.setEnabled(False)
        self.loop_spin.setMinimumHeight(22)
        self.loop_spin.setMinimumWidth(48)
        layout.addWidget(self.loop_spin, row, 2, 1, 2)

        self.repeat_cb.toggled.connect(self.repeat_spin.setEnabled)
        self.loop_cb.toggled.connect(self._on_loop_toggled)
        self.loop_cb.toggled.connect(self.loop_spin.setEnabled)

    def _on_loop_toggled(self, checked: bool) -> None:
        self.loop_toggled.emit(self.param_char, checked)

    def set_loop_enabled(self, enabled: bool) -> None:
        if not enabled:
            self.loop_cb.setChecked(False)
        self.loop_spin.setEnabled(self.loop_cb.isChecked())

    def get_config(self) -> dict:
        return {
            "char": self.param_char,
            "base": self.base_spin.value(),
            "step": self.step_spin.value(),
            "repeat": self.repeat_spin.value() if self.repeat_cb.isChecked() else None,
            "loop": self.loop_spin.value() if self.loop_cb.isChecked() else None,
        }


# ─────────────────────────────────────────────
# 批量命令生成器主页面
# ─────────────────────────────────────────────
class BatchCmdGeneratorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self._param_widgets: List[ParamGroupWidget] = []
        self._theme = ThemeEngine.get().current_theme

        # 模板数据
        self._template_file: str = get_config_path("config/cmd_templates.json")
        self._templates: List[dict] = []
        self._preset_templates: List[dict] = []
        self._user_templates: List[dict] = []

        self._setup_ui()
        self._apply_style()
        self._init_template_data()
        self._refresh_template_combo()
        self._bind_events()

        ThemeEngine.get().theme_changed.connect(self._on_theme_changed)

    # ─── 模板数据管理 ───

    def _init_template_data(self) -> None:
        """加载模板数据，不存在则从预置创建"""
        from src.utils.resource_path import ensure_dirs
        ensure_dirs()
        if self._template_file and self._template_file.endswith(".json"):
            data = JSONFileManager.load_json(self._template_file, default=None)
            if data and "templates" in data:
                self._templates = data["templates"]
                self._preset_templates = [t for t in self._templates if t.get("category") == "preset"]
                self._user_templates = [t for t in self._templates if t.get("category") == "user"]
                return
        # 首次运行：生成预置模板并保存
        self._preset_templates = _build_preset_templates()
        self._user_templates = []
        self._templates = self._preset_templates + self._user_templates
        self._save_templates()

    def _save_templates(self) -> bool:
        """原子保存模板数据到JSON文件"""
        data = {
            "version": "1.0",
            "templates": self._preset_templates + self._user_templates,
        }
        return JSONFileManager.save_json(self._template_file, data)

    def _refresh_template_combo(self) -> None:
        """刷新模板下拉框"""
        self.template_combo.clear()
        self.template_combo.addItem("请选择模板...")

        # 预置模板
        if self._preset_templates:
            self.template_combo.insertSeparator(self.template_combo.count())
            for t in self._preset_templates:
                idx = self.template_combo.count()
                self.template_combo.addItem(t["name"])
                self.template_combo.setItemData(idx, t)
                self.template_combo.setItemData(
                    idx, QColor(self._theme["text_tertiary"]), Qt.ForegroundRole
                )

        # 用户模板
        if self._user_templates:
            self.template_combo.insertSeparator(self.template_combo.count())
            for t in self._user_templates:
                idx = self.template_combo.count()
                self.template_combo.addItem(t["name"])
                self.template_combo.setItemData(idx, t)

        self._update_template_buttons()

    def _get_template_by_index(self, index: int) -> Optional[dict]:
        """根据combo索引获取模板数据"""
        if index <= 0:
            return None
        data = self.template_combo.itemData(index)
        return data if isinstance(data, dict) else None

    def _get_current_template(self) -> Optional[dict]:
        """获取当前选中的模板数据"""
        return self._get_template_by_index(self.template_combo.currentIndex())

    # ─── 模板操作 ───

    def _on_template_selected(self, index: int) -> None:
        """下拉框选中模板→填入编辑区"""
        self._update_template_buttons()
        template = self._get_template_by_index(index)
        if template is None:
            return

        # 编辑区有内容时确认覆盖
        current_text = self.template_edit.toPlainText().strip()
        if current_text:
            reply = QMessageBox.question(
                self, "确认覆盖",
                f"当前编辑区已有内容，是否用模板「{template['name']}」覆盖？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                # 恢复之前的选择
                self.template_combo.blockSignals(True)
                self.template_combo.setCurrentIndex(0)
                self.template_combo.blockSignals(False)
                self._update_template_buttons()
                return

        self.template_edit.setPlainText(template.get("content", ""))

    def _update_template_buttons(self) -> None:
        current = self._get_current_template()
        is_user = current is not None and current.get("category") == "user"
        self.btn_rename_template.setEnabled(is_user)
        self.btn_delete_template.setEnabled(is_user)

    def _on_add_template(self) -> None:
        """新增用户模板"""
        name, ok = QInputDialog.getText(self, "新增模板", "请输入模板名称:")
        if not ok or not name.strip():
            return
        name = name.strip()

        # 检查名称重复
        all_names = {t["name"] for t in self._preset_templates + self._user_templates}
        if name in all_names:
            QMessageBox.warning(self, "名称重复", f"模板名称「{name}」已存在，请换一个名称")
            return

        content = self.template_edit.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "提示", "编辑区为空，请先输入模板内容")
            return

        params = sorted(set(re.findall(r'%([a-f])', content)))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_template = {
            "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "category": "user",
            "vendor": "",
            "type": "",
            "content": content,
            "params": params,
            "description": "",
            "created_at": now,
        }
        self._user_templates.append(new_template)
        self._save_templates()
        self._refresh_template_combo()

        # 选中新添加的模板
        for i in range(self.template_combo.count()):
            if self.template_combo.itemText(i) == name:
                self.template_combo.setCurrentIndex(i)
                break

    def _on_rename_template(self) -> None:
        """重命名用户模板"""
        current = self._get_current_template()
        if current is None or current.get("category") != "user":
            QMessageBox.information(self, "提示", "请先选择一个用户模板")
            return

        new_name, ok = QInputDialog.getText(
            self, "重命名模板", "请输入新名称:", QLineEdit.Normal, current["name"]
        )
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()

        all_names = {t["name"] for t in self._preset_templates + self._user_templates}
        if new_name in all_names and new_name != current["name"]:
            QMessageBox.warning(self, "名称重复", f"模板名称「{new_name}」已存在")
            return

        for t in self._user_templates:
            if t["id"] == current["id"]:
                t["name"] = new_name
                break
        self._save_templates()
        self._refresh_template_combo()

    def _on_delete_template(self) -> None:
        """删除用户模板"""
        current = self._get_current_template()
        if current is None or current.get("category") != "user":
            QMessageBox.information(self, "提示", "请先选择一个用户模板")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模板「{current['name']}」吗？此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._user_templates = [t for t in self._user_templates if t["id"] != current["id"]]
        self._save_templates()
        self._refresh_template_combo()
        self.template_combo.setCurrentIndex(0)

    def _on_save_current_as_template(self) -> None:
        """将当前编辑区内容保存为新用户模板"""
        content = self.template_edit.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "提示", "编辑区为空，请先输入模板内容")
            return

        name, ok = QInputDialog.getText(self, "保存为模板", "请输入模板名称:")
        if not ok or not name.strip():
            return
        name = name.strip()

        all_names = {t["name"] for t in self._preset_templates + self._user_templates}
        if name in all_names:
            QMessageBox.warning(self, "名称重复", f"模板名称「{name}」已存在，请换一个名称")
            return

        params = sorted(set(re.findall(r'%([a-f])', content)))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_template = {
            "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "category": "user",
            "vendor": "",
            "type": "",
            "content": content,
            "params": params,
            "description": "",
            "created_at": now,
        }
        self._user_templates.append(new_template)
        self._save_templates()
        self._refresh_template_combo()

        # 选中新添加的模板
        for i in range(self.template_combo.count()):
            if self.template_combo.itemText(i) == name:
                self.template_combo.setCurrentIndex(i)
                break

    # ─── UI搭建 ───

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 6)
        main_layout.setSpacing(6)

        # 命令模板区
        template_group = QGroupBox("命令模板")
        template_group.setStyleSheet(self._group_style())
        template_layout = QVBoxLayout(template_group)
        template_layout.setContentsMargins(12, 8, 12, 8)
        template_layout.setSpacing(4)

        # 模板选择工具栏
        template_bar = QHBoxLayout()
        template_bar.setSpacing(4)
        template_bar.addWidget(QLabel("模板:"))

        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(260)
        t = self._theme
        r = t["radius_md"]
        self.template_combo.setStyleSheet(
            f"QComboBox {{"
            f"  border: 1px solid {t['input_border']}; border-radius: {r}px;"
            f"  padding: 4px 8px; font-size: 10pt; background: {t['input_bg']};"
            f"  color: {t['text_main']};"
            "}}"
            f"QComboBox:hover {{ border-color: {t['border']}; }}"
            "QComboBox::drop-down { border: none; width: 24px; }"
        )
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        template_bar.addWidget(self.template_combo)

        self.btn_add_template = QPushButton("+ 新增")
        self.btn_add_template.setObjectName("tplAddBtn")
        self.btn_add_template.setCursor(Qt.PointingHandCursor)
        self.btn_add_template.setMinimumHeight(22)
        self.btn_add_template.setMinimumWidth(52)
        template_bar.addWidget(self.btn_add_template)

        self.btn_rename_template = QPushButton("重命名")
        self.btn_rename_template.setObjectName("tplRenameBtn")
        self.btn_rename_template.setCursor(Qt.PointingHandCursor)
        self.btn_rename_template.setMinimumHeight(22)
        self.btn_rename_template.setMinimumWidth(52)
        template_bar.addWidget(self.btn_rename_template)

        self.btn_save_template = QPushButton("保存")
        self.btn_save_template.setObjectName("tplSaveBtn")
        self.btn_save_template.setCursor(Qt.PointingHandCursor)
        self.btn_save_template.setMinimumHeight(22)
        self.btn_save_template.setMinimumWidth(40)
        template_bar.addWidget(self.btn_save_template)

        self.btn_delete_template = QPushButton("删除")
        self.btn_delete_template.setObjectName("tplDeleteBtn")
        self.btn_delete_template.setCursor(Qt.PointingHandCursor)
        self.btn_delete_template.setMinimumHeight(22)
        self.btn_delete_template.setMinimumWidth(40)
        template_bar.addWidget(self.btn_delete_template)

        template_bar.addStretch()
        template_layout.addLayout(template_bar)

        hint_lbl = QLabel("请输入命令模板，参数格式为：%a ~ %f")
        hint_lbl.setStyleSheet(f"font-size: 10pt; color: {self._theme['text_tertiary']};")
        template_layout.addWidget(hint_lbl)

        self.template_edit = QTextEdit()
        self.template_edit.setPlaceholderText(
            "在此输入命令模板，或从上方下拉框选择预置模板...\n\n"
            "参数格式: %a=第1个参数, %b=第2个参数, ... %f=第6个参数\n"
            "两种模式：\n"
            "  ① 固定重复：勾选下方「重复次数」，输出N条相同命令（适合无参/纯文本）\n"
            "  ② 差异化生成：勾选参数的「循环个数」，按基数+步长自动递增生成不同命令\n\n"
            "示例（锐捷接口划分VLAN）:\n"
            "interface GigabitEthernet 0/%a\n"
            " switchport mode access\n"
            " switchport access vlan %b\n"
            "exit\n\n"
            "%a=接口编号(如1~24), %b=VLAN号(如100~200)"
        )
        self.template_edit.setMinimumHeight(90)
        self.template_edit.setFont(QFont("Consolas", 11))
        template_layout.addWidget(self.template_edit)

        main_layout.addWidget(template_group)

        # 参数设置区
        param_group = QGroupBox("参数设置  （勾选「循环个数」→ 差异化批量生成模式）")
        param_group.setStyleSheet(self._group_style())
        param_outer_layout = QVBoxLayout(param_group)
        param_outer_layout.setContentsMargins(6, 6, 6, 4)
        param_outer_layout.setSpacing(4)

        param_container = QW()
        param_container.setLayout(QHBoxLayout())
        param_container.layout().setContentsMargins(0, 0, 0, 0)
        param_container.layout().setSpacing(4)

        for i, char in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
            pw = ParamGroupWidget(label=str(i + 1), param_char=char)
            self._param_widgets.append(pw)
            param_container.layout().addWidget(pw)

        param_scroll = QScrollArea()
        param_scroll.setWidget(param_container)
        param_scroll.setWidgetResizable(True)
        param_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        param_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        param_scroll.setMinimumHeight(120)
        param_scroll.setMaximumHeight(175)
        param_outer_layout.addWidget(param_scroll)

        main_layout.addWidget(param_group)

        # 操作按钮行
        action_row = QHBoxLayout()
        action_row.setSpacing(6)

        self.cmd_count_cb = QCheckBox()
        self.cmd_count_cb.setChecked(True)
        self.cmd_count_cb.setCursor(Qt.PointingHandCursor)
        self.cmd_count_cb.setToolTip("勾选：重复输出相同命令（适用于无参数/纯文本模板）")
        action_row.addWidget(self.cmd_count_cb)

        action_row.addWidget(QLabel("重复次数:"))
        self.cmd_count_spin = QSpinBox()
        self.cmd_count_spin.setRange(1, 999999)
        self.cmd_count_spin.setValue(12)
        self.cmd_count_spin.setMinimumHeight(26)
        self.cmd_count_spin.setMinimumWidth(75)
        self.cmd_count_spin.setToolTip("输出多少条相同的命令\n取消勾选后由下方「循环个数」控制差异化条数")
        action_row.addWidget(self.cmd_count_spin)

        self.mode_hint_label = QLabel()
        self.mode_hint_label.setStyleSheet(
            f"color: {self._theme['text_tertiary']}; font-size: 10pt; padding: 0 4px;"
        )
        self.mode_hint_label.setText("📌 当前模式：固定重复")
        action_row.addWidget(self.mode_hint_label)

        btn_gen = QPushButton("生成命令")
        btn_gen.setObjectName("genBtn")
        btn_gen.setCursor(Qt.PointingHandCursor)
        btn_gen.setMinimumHeight(26)
        btn_gen.setMinimumWidth(85)
        action_row.addWidget(btn_gen)

        btn_save = QPushButton("保存结果")
        btn_save.setObjectName("saveBtn")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setMinimumHeight(26)
        btn_save.setMinimumWidth(85)
        action_row.addWidget(btn_save)

        btn_copy = QPushButton("复制全部")
        btn_copy.setObjectName("copyBtn")
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setMinimumHeight(26)
        btn_copy.setMinimumWidth(85)
        action_row.addWidget(btn_copy)

        btn_clear = QPushButton("清空")
        btn_clear.setObjectName("clearBtn")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setMinimumHeight(22)
        btn_clear.setMinimumWidth(65)
        action_row.addWidget(btn_clear)

        action_row.addStretch()
        main_layout.addLayout(action_row)

        # 输出区
        self.output_edit = QTextEdit()
        self.output_edit.setFont(QFont("Consolas", 11))
        self.output_edit.setMinimumHeight(180)
        main_layout.addWidget(self.output_edit)

        # 状态栏
        t = self._theme
        status_bar = QLabel("  0 %")
        status_bar.setAlignment(Qt.AlignCenter)
        status_bar.setStyleSheet(
            f"background-color: {t['hover_bg']}; color: {t['text_tertiary']}; font-size: 10pt;"
            f"border: 1px solid {t['border']}; padding: 3px;"
        )
        status_bar.setMinimumHeight(20)
        main_layout.addWidget(status_bar)
        self._status_label = status_bar

    def _group_style(self) -> str:
        t = self._theme
        return (
            "QGroupBox {"
            f"  font-size: 11pt; font-weight: bold; color: {t['text_main']};"
            f"  border: 1px solid {t['border']}; border-radius: {t['radius_lg']}px;"
            "  margin-top: 8px; padding-top: 8px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin; left: 12px; padding: 0 6px;"
            "}"
        )

    def _apply_style(self) -> None:
        t = self._theme
        r = t["radius_md"]
        te = ThemeEngine.get()
        ss = (
            "QTextEdit {"
            f"  border: 1px solid {t['border']}; border-radius: {r}px; padding: 6px;"
            f"  background: {t['input_bg']}; font-size: 11pt; color: {t['text_main']};"
            "}"
            f"QTextEdit:focus {{ border-color: {t['border']}; }}"
            "QSpinBox {"
            f"  border: 1px solid {t['border']}; border-radius: {r}px; padding: 2px 6px;"
            f"  background: {t['input_bg']}; color: {t['text_main']};"
            "}"
            f"QSpinBox:focus {{ border-color: {t['border']}; }}"
        )
        _primary = te.qss("btn_primary")
        _default = te.qss("btn_default")
        _danger = te.qss("btn_danger")
        # 主操作：生成、保存、复制、新增模板
        for name in ("genBtn", "saveBtn", "copyBtn", "tplAddBtn"):
            ss += f"QPushButton#{name} {{{_primary}}}\n"
        # 辅助操作：重命名、清空
        for name in ("tplRenameBtn", "clearBtn"):
            ss += f"QPushButton#{name} {{{_default}}}\n"
        # 危险操作：删除
        ss += f"QPushButton#tplDeleteBtn {{{_danger}}}\n"
        self.setStyleSheet(ss)

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题切换时刷新样式。"""
        self._theme = ThemeEngine.get().current_theme
        self._apply_style()
        # 刷新 ParamGroupWidget 样式
        for pw in self._param_widgets:
            pw.setStyleSheet(
                f"QGroupBox {{"
                f"  font-size: 10pt; font-weight: bold; color: {self._theme['text_main']};"
                f"  border: 1px solid {self._theme['border']}; border-radius: {self._theme['radius_lg']}px;"
                f"  margin-top: 8px; padding-top: 10px;"
                f"}}"
                f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}"
            )
        # 刷新模板选择栏和状态栏
        hint_color = self._theme['text_tertiary']
        for lbl in self.findChildren(QLabel):
            if lbl.text() and "%a" in lbl.text():
                lbl.setStyleSheet(f"font-size: 10pt; color: {hint_color};")
        if hasattr(self, '_status_label') and self._status_label:
            t = self._theme
            self._status_label.setStyleSheet(
                f"background-color: {t['hover_bg']}; color: {t['text_tertiary']};"
                f"font-size: 10pt; border: 1px solid {t['border']}; padding: 3px;"
            )
        self.update()

    def _bind_events(self) -> None:
        for btn in self.findChildren(QPushButton):
            txt = btn.text()
            if txt == "生成命令":
                btn.clicked.connect(self._generate)
            elif txt == "保存结果":
                btn.clicked.connect(self._save_result)
            elif txt == "复制全部":
                btn.clicked.connect(self._copy_all)
            elif txt == "清空":
                btn.clicked.connect(self._clear_output)

        for pw in self._param_widgets:
            pw.loop_toggled.connect(self._on_param_loop_toggled)
        self.cmd_count_cb.toggled.connect(self._on_cmd_count_toggled)

        self.btn_add_template.clicked.connect(self._on_add_template)
        self.btn_rename_template.clicked.connect(self._on_rename_template)
        self.btn_delete_template.clicked.connect(self._on_delete_template)
        self.btn_save_template.clicked.connect(self._on_save_current_as_template)

        self._init_mutual_exclusion()

    def _init_mutual_exclusion(self) -> None:
        self._sync_ui_from_cmd_count_mode()

    def _on_param_loop_toggled(self, char: str, checked: bool) -> None:
        if checked:
            self.cmd_count_cb.blockSignals(True)
            self.cmd_count_cb.setChecked(False)
            self.cmd_count_cb.blockSignals(False)
            self._update_mode_hint()
        else:
            any_still_checked = any(pw.loop_cb.isChecked() for pw in self._param_widgets)
            if not any_still_checked:
                self.cmd_count_cb.blockSignals(True)
                self.cmd_count_cb.setChecked(True)
                self.cmd_count_cb.blockSignals(False)
                self._update_mode_hint()

    def _on_cmd_count_toggled(self, checked: bool) -> None:
        if checked:
            for pw in self._param_widgets:
                pw.set_loop_enabled(False)
        self._update_mode_hint()

    def _sync_ui_from_cmd_count_mode(self) -> None:
        for pw in self._param_widgets:
            pw.set_loop_enabled(False)
        self.cmd_count_cb.setChecked(True)
        self._update_mode_hint()

    def _update_mode_hint(self) -> None:
        if self.cmd_count_cb.isChecked():
            self.mode_hint_label.setText("📌 当前模式：固定重复")
        else:
            loop_vals = [
                pw.loop_spin.value()
                for pw in self._param_widgets
                if pw.loop_cb.isChecked()
            ]
            max_v = max(loop_vals) if loop_vals else 0
            self.mode_hint_label.setText(f"📌 当前模式：差异化生成（{max_v}条）")

    # ─── 生成逻辑 ───

    def _generate(self) -> None:
        template = self.template_edit.toPlainText().strip()
        if not template:
            QMessageBox.information(self, "提示", "请先输入命令模板")
            return

        used_params = sorted(set(re.findall(r'%([a-f])', template)))
        if not used_params:
            count = self.cmd_count_spin.value()
            result_text = "\n".join([template] * count)
            self.output_edit.setPlainText(result_text)
            self._status_label.setText("  100 %")
            return

        configs: Dict[str, dict] = {}
        for char in used_params:
            idx = ord(char) - ord('a')
            if idx < len(self._param_widgets):
                configs[char] = self._param_widgets[idx].get_config()
            else:
                configs[char] = {"char": char, "base": 0, "step": 1, "repeat": None, "loop": None}

        # 确定循环次数
        if self.cmd_count_cb.isChecked():
            loop_count = self.cmd_count_spin.value()
        else:
            loop_values = [
                self._param_widgets[ord(c) - ord('a')].loop_spin.value()
                for c in used_params
                if ord(c) - ord('a') < len(self._param_widgets)
                and self._param_widgets[ord(c) - ord('a')].loop_cb.isChecked()
            ]
            loop_count = max(loop_values) if loop_values else self.cmd_count_spin.value()

        # 为每个使用的参数生成值列表
        param_values: Dict[str, List[int]] = {}
        for char in used_params:
            cfg = configs[char]
            base = cfg["base"]
            step = cfg["step"]
            loop = cfg["loop"]
            repeat = cfg["repeat"] or 1
            if self.cmd_count_cb.isChecked():
                values = [base + i * step for i in range(loop_count)]
            elif loop is not None:
                values = [base + i * step for i in range(loop)]
            else:
                values = [base]
            expanded = []
            for v in values:
                expanded.extend([v] * repeat)
            param_values[char] = expanded

        # 优化：使用 re.sub 一次性替换所有占位符，每 100 次迭代更新一次 UI
        _pattern = re.compile(r'%([a-f])')
        lines: List[str] = []
        for i in range(loop_count):
            current_values: Dict[str, int] = {}
            for char in used_params:
                vals = param_values[char]
                current_values[char] = vals[i % len(vals)] if vals else 0
            rendered = _pattern.sub(lambda m: str(current_values.get(m.group(1), 0)), template)
            lines.append(rendered)
            if i % 100 == 0:
                pct = min(int((i + 1) / loop_count * 100), 100)
                self._status_label.setText(f"  {pct} %")
                QApplication.processEvents()
        result_text = "\n".join(lines)
        self.output_edit.setPlainText(result_text)
        self._status_label.setText("  100 %")

    def _save_result(self) -> None:
        text = self.output_edit.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "提示", "没有可保存的内容，先生成命令")
            return
        default_name = f"batch_cmds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存命令结果", default_name, "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "成功", f"已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存失败: {e}")

    def _copy_all(self) -> None:
        text = self.output_edit.toPlainText()
        if text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        else:
            QMessageBox.information(self, "提示", "没有可复制的内容")

    def _clear_output(self) -> None:
        self.output_edit.clear()
        self._status_label.setText("  0 %")
