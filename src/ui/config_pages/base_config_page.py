from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QTextEdit, QScrollArea, QTabWidget, QTableWidget,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from src.core.theme_engine import ThemeEngine

_CLI_TEMPLATE_MAP = {
    'ruijie': 'src.ui.config_pages.templates.ruijie_cli.RuijieCLITemplate',
    'huawei': 'src.ui.config_pages.templates.huawei_cli.HuaweiCLITemplate',
    'h3c': 'src.ui.config_pages.templates.h3c_cli.H3CCLITemplate',
    'cisco': 'src.ui.config_pages.templates.cisco_cli.CiscoCLITemplate',
}


class BatchImportDialog(QDialog):
    """批量导入对话框，一次性收集所有必填和选填字段。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('批量导入设备')
        self.setMinimumWidth(420)
        self._fields: dict[str, QLineEdit] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(4)

        # 必填字段
        self._add_form_field(form, 'hostname', '设备主机名 *', '请输入设备主机名')
        self._add_form_field(form, 'ip_address', 'IP 地址 *', '请输入IP地址')

        # 选填字段
        self._add_form_field(form, 'subnet_mask', '子网掩码', '例如 255.255.255.0')
        self._add_form_field(form, 'gateway', '默认网关', '请输入默认网关')
        self._add_form_field(form, 'vlan_id', 'VLAN ID', '1-4094')
        self._add_form_field(form, 'port', '端口号', '1-65535')

        layout.addLayout(form)

        # 按钮框
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 设置 Tab 顺序：按添加顺序自然排列
        self._fields['hostname'].setFocus()

    def _add_form_field(self, form: QFormLayout, field_name: str, label: str, placeholder: str) -> None:
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setMinimumWidth(260)
        self._fields[field_name] = edit
        form.addRow(QLabel(label), edit)

    def _on_accept(self) -> None:
        """验证必填字段，通过则 accept()"""
        hostname = self._fields['hostname'].text().strip()
        ip_address = self._fields['ip_address'].text().strip()

        if not hostname:
            QMessageBox.warning(self, '输入错误', '设备主机名为必填项')
            self._fields['hostname'].setFocus()
            return
        if not ip_address:
            QMessageBox.warning(self, '输入错误', 'IP 地址为必填项')
            self._fields['ip_address'].setFocus()
            return

        # 验证选填字段格式（如果有填写）
        vlan_str = self._fields['vlan_id'].text().strip()
        if vlan_str:
            try:
                vlan_id = int(vlan_str)
                if not 1 <= vlan_id <= 4094:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, '输入错误', 'VLAN ID 必须是 1-4094 的整数')
                self._fields['vlan_id'].setFocus()
                return

        port_str = self._fields['port'].text().strip()
        if port_str:
            try:
                port = int(port_str)
                if not 1 <= port <= 65535:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, '输入错误', '端口号必须是 1-65535 的整数')
                self._fields['port'].setFocus()
                return

        self.accept()

    def get_data(self) -> dict[str, str]:
        """返回用户填写的数据字典"""
        return {
            'hostname': self._fields['hostname'].text().strip(),
            'ip_address': self._fields['ip_address'].text().strip(),
            'subnet_mask': self._fields['subnet_mask'].text().strip(),
            'gateway': self._fields['gateway'].text().strip(),
            'vlan_id': self._fields['vlan_id'].text().strip(),
            'port': self._fields['port'].text().strip(),
        }


class BaseConfigPage(QWidget):
    def __init__(self, parent, vendor=None, device_type=None):
        super().__init__()
        self.parent = parent
        self.vendor = vendor
        self.device_type = device_type
        self._theme_engine = ThemeEngine.get()
        self.cli = self._load_cli_template()
        self.cards = []
        self.form_fields = {}
        self.init_ui()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

    def _load_cli_template(self):
        if self.vendor and self.vendor in _CLI_TEMPLATE_MAP:
            mod_path, cls_name = _CLI_TEMPLATE_MAP[self.vendor].rsplit('.', 1)
            import importlib
            mod = importlib.import_module(mod_path.replace('/', '.'))
            return getattr(mod, cls_name)()
        return None

    # ------------------------------------------------------------------
    # 主题联动
    # ------------------------------------------------------------------
    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()
        self._refresh_child_styles()

    def _refresh_child_styles(self) -> None:
        """刷新所有子控件的样式，子类可覆写此方法"""
        t = self._theme_engine.current_theme
        # 刷新所有 QTabWidget
        for tab in self.findChildren(QTabWidget):
            tab.setStyleSheet(self._get_tab_style())
        # 刷新所有 QTableWidget
        for table in self.findChildren(QTableWidget):
            table.setStyleSheet(self._get_table_style())
            table.horizontalHeader().setStyleSheet(self._get_table_header_style())

    def _apply_theme_style(self) -> None:
        t = self._theme_engine.current_theme
        self.setStyleSheet(f"background-color: {t['page_bg']};")

    # ------------------------------------------------------------------
    # 动态样式生成器
    # ------------------------------------------------------------------
    def _get_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 14pt; font-weight: bold; color: {t['text_main']};"

    def _get_preview_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 12pt; font-weight: bold; color: {t['text_main']};"

    def _get_desc_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 11pt; color: {t['text_secondary']}; margin-bottom: 10px;"

    def _get_card_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QWidget {{ background-color: {t['card_bg']}; border-radius: {t['radius_lg']}px;"
            f"padding: 6px; }}"
        )

    def _get_card_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 12pt; font-weight: bold; color: {t['text_main']};"

    def _get_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 11pt; color: {t['text_main']};"

    def _get_label_secondary_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 11pt; color: {t['text_secondary']};"

    def _get_input_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['input_border']}; border-radius: {t['radius_md']}px;"
            f" padding: 3px 6px; font-size: 11pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {t['border']}; outline: none; }}"
        )

    def _get_primary_button_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: transparent;"
            f" color: {t['text_main']};"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px; font-size: 11pt;"
            f"}}"
            f"QPushButton:hover {{"
            f" background-color: transparent;"
            f" border-color: {t['border']};"
            f" color: {t['text_secondary']};"
            f"}}"
            f"QPushButton:disabled {{"
            f" background-color: transparent;"
            f" border-color: {t['border']};"
            f" color: {t['text_tertiary']};"
            f"}}"
        )

    def _get_secondary_button_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: transparent;"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" font-size: 11pt; color: {t['text_main']};"
            f"}}"
            f"QPushButton:hover {{ border: 1px solid {t['border']}; }}"
        )

    def _get_preview_text_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QTextEdit {{"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" padding: 6px; font-family: 'Courier New', monospace;"
            f" font-size: 11pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
        )

    def _get_tab_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QTabWidget::pane {{ border: none; background-color: {t['sidebar_bg']}; }}"
            f"QTabBar::tab {{"
            f" background-color: {t['card_bg']};"
            f" border: 1px solid {t['border']}; border-bottom: none;"
            f" padding: 6px 24px; margin-right: 4px;"
            f" border-top-left-radius: 6px; border-top-right-radius: 6px;"
            f" font-size: 11pt; color: {t['text_secondary']};"
            f"}}"
            f"QTabBar::tab:selected {{"
            f" background-color: {t['page_bg']}; color: {t['text_primary']};"
            f" font-weight: bold;"
            f"}}"
            f"QTabBar::tab:hover:!selected {{ background-color: {t['hover_bg']}; }}"
        )

    def _get_combo_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QComboBox {{"
            f" border: 1px solid {t['input_border']}; border-radius: {t['radius_md']}px;"
            f" padding: 3px 6px; font-size: 11pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QComboBox:focus {{ border-color: {t['border']}; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{"
            f" border: 1px solid {t['input_border']}; selection-background-color: {t['page_bg']};"
            f"}}"
        )

    def _get_checkbox_style(self) -> str:
        """仅设置文字样式，indicator 由 ThemeEngine 全局 QSS 统一控制。"""
        t = self._theme_engine.current_theme
        return f"QCheckBox {{ font-size: 11pt; color: {t['text_main']}; }}"

    def _get_radio_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"QRadioButton {{ font-size: 11pt; color: {t['text_secondary']}; }}"

    def _get_groupbox_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QGroupBox {{"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" margin-top: 12px; padding-top: 12px;"
            f" font-size: 11pt; font-weight: bold; color: {t['text_main']};"
            f"}}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}"
        )

    def _get_table_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QTableWidget {{"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" gridline-color: {t['border']};"
            f" background-color: {t['card_bg']}; color: {t['text_main']};"
            f" font-size: 11pt;"
            f"}}"
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_main']};"
            f" border: 1px solid {t['border']}; padding: 6px;"
            f"}}"
            f"QTableWidget::item {{ padding: 4px; }}"
            f"QTableWidget::item:selected {{ background-color: {t['page_bg']}; color: {t['text_primary']}; }}"
        )

    def _get_table_header_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_secondary']};"
            f" border: none; padding: 6px; font-size: 10pt;"
            f"}}"
        )

    def _get_input_alt_style(self) -> str:
        """替代输入框样式（#CCCCCC 边框 + {t['card_bg']} 背景）"""
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['border_deep']}; padding: 3px 6px;"
            f" font-size: 11pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border: 1px solid {t['border']}; }}"
        )

    def _get_scroll_area_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"border: none; background-color: {t['sidebar_bg']};"

    def _get_container_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"background-color: {t['sidebar_bg']};"

    def _get_divider_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"background-color: {t['border']};"

    def _get_tab_content_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 12pt; font-weight: bold; color: {t['text_main']};"

    def _get_tab_content_desc_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 10pt; color: {t['text_secondary']};"

    def _get_bold_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 11pt; font-weight: bold;"

    def _get_hint_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 10pt;"

    def _get_method_label_style(self) -> str:
        """方法标签样式（#E5E5E5 背景 + #CCCCCC 边框）"""
        t = self._theme_engine.current_theme
        return (
            f"color: {t['text_main']}; font-size: 11pt; font-weight: bold;"
            f" background-color: {t['sidebar_bg']};"
            f" border: 1px solid {t['border_deep']}; padding: 3px 6px;"
        )

    def _get_method_field_label_style(self) -> str:
        """方法字段标签样式（#CCCCCC 边框）"""
        t = self._theme_engine.current_theme
        return (
            f"color: {t['text_main']}; font-size: 11pt;"
            f" border: 1px solid {t['border_deep']}; padding: 3px 6px;"
        )

    def _get_login_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 11pt; font-weight: bold;"

    def _get_danger_button_style(self) -> str:
        """危险/删除按钮样式（红色边框+文字，hover 加深）"""
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: transparent;"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" color: {t['text_secondary']}; font-size: 10pt;"
            f"}}"
            f"QPushButton:hover {{"
            f" border: 1px solid {t['border']}; color: {t['text_secondary']};"
            f"}}"
        )

    def _get_input_alt2_style(self) -> str:
        """替代输入框样式2（#CCCCCC 边框 + card_bg 背景，带 focus 高亮）"""
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['border_deep']}; padding: 3px 6px;"
            f" font-size: 11pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border: 1px solid {t['border']}; }}"
        )

    def _get_small_delete_btn_style(self) -> str:
        """小型删除按钮样式（60x24，hover 变红）"""
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: transparent;"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" color: {t['text_secondary']}; font-size: 10pt;"
            f"}}"
            f"QPushButton:hover {{"
            f" border: 1px solid {t['border']}; color: {t['text_secondary']};"
            f"}}"
        )

    def _get_table_with_selection_style(self) -> str:
        """带动态选中色的表格样式（替代内嵌的 #E6F0FF 选中色）"""
        t = self._theme_engine.current_theme
        return (
            f"QTableWidget {{"
            f" border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;"
            f" gridline-color: {t['border']};"
            f" background-color: {t['card_bg']}; color: {t['text_main']};"
            f" font-size: 11pt;"
            f"}}"
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_main']};"
            f" border: 1px solid {t['border']}; padding: 6px;"
            f"}}"
            f"QTableWidget::item {{ padding: 4px; }}"
            f"QTableWidget::item:selected {{ background-color: {t['page_bg']}; color: {t['text_primary']}; }}"
        )

    # ------------------------------------------------------------------
    # 原有方法（保持不变）
    # ------------------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # 标题
        title_layout = QHBoxLayout()
        self.title_label = QLabel('配置页面')
        self.title_label.setStyleSheet(self._get_title_style())
        title_layout.addWidget(self.title_label)

        # 返回按钮
        back_button = QPushButton('返回上一级')
        back_button.setFixedSize(90, 26)
        back_button.setStyleSheet(self._get_secondary_button_style())
        back_button.clicked.connect(self.on_back_clicked)
        title_layout.addWidget(back_button)

        # 返回首页按钮
        home_button = QPushButton('返回首页')
        home_button.setFixedSize(90, 26)
        home_button.setStyleSheet(self._get_secondary_button_style())
        home_button.clicked.connect(self.on_home_clicked)
        title_layout.addWidget(home_button)

        layout.addLayout(title_layout)

        # 内容区域
        content_layout = QHBoxLayout()

        # 左侧配置区域
        self.config_area = QScrollArea()
        self.config_area.setWidgetResizable(True)
        self.config_widget = QWidget()
        self.config_layout = QVBoxLayout()
        self.config_layout.setContentsMargins(0, 0, 0, 0)
        self.config_layout.setSpacing(4)
        self.config_widget.setLayout(self.config_layout)
        self.config_area.setWidget(self.config_widget)
        content_layout.addWidget(self.config_area, 7)

        # 右侧预览区域
        preview_layout = QVBoxLayout()

        preview_header = QHBoxLayout()
        preview_label = QLabel('配置脚本预览')
        preview_label.setStyleSheet(self._get_preview_label_style())
        preview_header.addWidget(preview_label)
        preview_header.addStretch()

        generate_button = QPushButton('生成配置')
        generate_button.setFixedSize(90, 26)
        generate_button.setStyleSheet(self._get_primary_button_style())
        generate_button.clicked.connect(self.generate_config)
        preview_header.addWidget(generate_button)

        copy_button = QPushButton('复制脚本')
        copy_button.setFixedSize(90, 26)
        copy_button.setStyleSheet(self._get_secondary_button_style())
        copy_button.clicked.connect(self.copy_config)
        preview_header.addWidget(copy_button)

        export_button = QPushButton('导出配置')
        export_button.setFixedSize(90, 26)
        export_button.setStyleSheet(self._get_secondary_button_style())
        export_button.clicked.connect(self.export_config)
        preview_header.addWidget(export_button)

        reset_button = QPushButton('重置')
        reset_button.setFixedSize(72, 24)
        reset_button.setStyleSheet(self._get_secondary_button_style())
        reset_button.clicked.connect(self.reset_config)
        preview_header.addWidget(reset_button)

        preview_layout.addLayout(preview_header)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(self._get_preview_text_style())
        preview_layout.addWidget(self.preview_text, 1)

        content_layout.addLayout(preview_layout, 3)

        layout.addLayout(content_layout)

        self.setLayout(layout)

    def on_back_clicked(self):
        """返回上一级"""
        pass

    def on_home_clicked(self):
        """返回首页"""
        pass

    def generate_config(self):
        """生成配置"""
        pass

    def copy_config(self):
        """复制配置"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_text.toPlainText())

    def export_config(self):
        """导出配置"""
        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "导出配置", "", "配置文件 (*.txt);;所有文件 (*.*)", options=options)
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.preview_text.toPlainText())

    def reset_config(self):
        """重置配置"""
        if hasattr(self, 'reset_form'):
            self.reset_form()
        elif hasattr(self, 'reset_all_fields'):
            self.reset_all_fields()
        self.preview_text.clear()

    def create_card(self, title, icon, description):
        """创建配置卡片"""
        card = QWidget()
        card.setStyleSheet(self._get_card_style())
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(4)

        # 卡片标题
        title_layout = QHBoxLayout()
        title_label = QLabel(f'{icon} {title}')
        title_label.setStyleSheet(self._get_card_title_style())
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)

        # 卡片描述
        desc_label = QLabel(description)
        desc_label.setStyleSheet(self._get_desc_label_style())
        card_layout.addWidget(desc_label)

        # 表单区域
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        card_layout.addLayout(form_layout)

        card.setLayout(card_layout)
        return card

    def add_form_item(self, card, label_text, field_name, is_password=False, is_label=False, default_value=''):
        """添加表单项"""
        form_layout = card.layout().itemAt(2).layout()

        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(4)

        # 标签
        label = QLabel(label_text)
        label.setFixedWidth(110)
        label.setStyleSheet(self._get_label_style())
        item_layout.addWidget(label)

        # 输入框
        if is_label:
            input_field = QLabel(default_value)
            input_field.setStyleSheet(self._get_label_secondary_style())
        else:
            input_field = QLineEdit()
            input_field.setFixedHeight(24)
            input_field.setText(default_value)
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
                input_field.setPlaceholderText('请输入密码')
            else:
                # 根据字段名设置相应的提示信息
                if 'hostname' in field_name:
                    input_field.setPlaceholderText('请输入设备主机名')
                elif 'ip' in field_name or 'address' in field_name:
                    input_field.setPlaceholderText('请输入IP地址')
                elif 'mask' in field_name:
                    input_field.setPlaceholderText('请输入子网掩码')
                elif 'gateway' in field_name:
                    input_field.setPlaceholderText('请输入默认网关')
                elif 'vlan' in field_name:
                    input_field.setPlaceholderText('请输入VLAN ID')
                elif 'interface' in field_name:
                    input_field.setPlaceholderText('请输入接口名称')
                elif 'description' in field_name:
                    input_field.setPlaceholderText('请输入描述信息')
                elif 'username' in field_name:
                    input_field.setPlaceholderText('请输入用户名')
                else:
                    input_field.setPlaceholderText(f'请输入{label_text}')

            # 设置样式
            input_field.setStyleSheet(self._get_input_style())

        item_layout.addWidget(input_field, 1)
        form_layout.addLayout(item_layout)

        return input_field

    # ------------------------------------------------------------------
    # 共享数据解析（消除全部16个config页的重复逻辑）
    # ------------------------------------------------------------------
    @staticmethod
    def parse_vlan_input(vlan_str: str) -> List[int]:
        """解析用户输入的VLAN字符串，返回 VLAN ID 列表。
        支持格式：单个'100'，逗号'100,200'，范围'2 to 4'/'2-4'，混合'100,200-205'
        原重复位置：全部16个config页 + config_generator.py ×16
        """
        if not vlan_str:
            return []
        result = []
        items = [s.strip() for s in vlan_str.replace('，', ',').split(',') if s.strip()]
        for item in items:
            if ' to ' in item:
                parts = item.split(' to ')
                try:
                    result.extend(range(int(parts[0]), int(parts[1]) + 1))
                except ValueError:
                    pass
            elif '-' in item:
                parts = item.split('-')
                try:
                    result.extend(range(int(parts[0]), int(parts[1]) + 1))
                except ValueError:
                    pass
            else:
                try:
                    result.append(int(item))
                except ValueError:
                    pass
        return result

    @staticmethod
    def parse_acl_address(addr_desc: str) -> tuple:
        """解析ACL源/目标地址描述，返回 (src_ip, dst_ip, dst_port)"""
        src_ip = 'any'
        dst_ip = 'any'
        dst_port = ''
        if '→' in addr_desc:
            parts = addr_desc.split('→')
            src_ip = parts[0].strip() or 'any'
            dst_part = parts[1].strip() if len(parts) > 1 else 'any'
            if ':' in dst_part:
                host, port = dst_part.rsplit(':', 1)
                dst_ip = host.strip()
                dst_port = port.strip()
            else:
                dst_ip = dst_part
        return src_ip, dst_ip, dst_port

    @staticmethod
    def parse_interface_abbrev(iface_str: str) -> tuple:
        """解析接口缩写，返回 (类型, 编号)。如 'G 1/0' → ('GigabitEthernet', '1/0')"""
        mapping = {
            'G': 'GigabitEthernet', 'Te': 'TenGigabitEthernet',
            'F': 'FastEthernet', 'E': 'Ethernet', 'XG': 'XGigabitEthernet',
        }
        parts = iface_str.strip().split()
        if len(parts) >= 2:
            kind = mapping.get(parts[0], parts[0])
            num = parts[1]
            return kind, num
        return iface_str, ''

    def get_cards(self) -> List[QWidget]:
        """获取所有卡片"""
        return self.cards

    def get_checked_cards(self) -> List[str]:
        """获取所有选中的卡片名称"""
        checked = []
        for card in self.cards:
            for child in card.findChildren(QCheckBox):
                if child.isChecked():
                    checked.append(child.text())
        return checked

    def get_form_data(self) -> dict:
        """获取表单数据字典"""
        data = {}
        for field_name, widget in self.form_fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                data[field_name] = widget.isChecked()
            elif isinstance(widget, QLabel):
                data[field_name] = widget.text()
        return data

    def _get_cli_list(self) -> list:
        """创建空的命令列表"""
        return []

    def _emit_config(self, cmds):
        """将命令列表写入预览窗口"""
        self.preview_text.setText('\n'.join(cmds))

    def batch_import(self) -> None:
        """批量导入设备配置，使用自定义对话框收集所有字段。"""
        dialog = BatchImportDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        data = dialog.get_data()
        cmds = self._get_cli_list()

        # 生成主机名配置
        cmds.append(f"hostname {data['hostname']}")

        # 生成接口配置
        cmds.append(f"interface {data.get('interface', 'GigabitEthernet0/0')}")
        cmds.append(f" ip address {data['ip_address']} {data['subnet_mask']}")
        cmds.append(" no shutdown")

        # 生成VLAN配置（如果有）
        vlan_id = data['vlan_id']
        if vlan_id:
            cmds.append(f"vlan {vlan_id}")
            cmds.append(f" name VLAN_{vlan_id}")

        # 生成网关配置（如果有）
        gateway = data['gateway']
        if gateway:
            cmds.append(f"ip route 0.0.0.0 0.0.0.0 {gateway}")

        # 生成端口配置（如果有）
        port = data['port']
        if port:
            cmds.append(f"line vty 0 {port}")
            cmds.append(" login local")

        self._emit_config(cmds)
