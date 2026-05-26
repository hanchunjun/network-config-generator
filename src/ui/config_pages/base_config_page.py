from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QTextEdit, QScrollArea, QTabWidget, QTableWidget
from PyQt5.QtCore import Qt
from src.core.theme_engine import ThemeEngine


class BaseConfigPage(QWidget):
    def __init__(self, parent, vendor=None, device_type=None):
        super().__init__()
        self.parent = parent
        self.vendor = vendor
        self.device_type = device_type
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

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
        return f"font-size: 15pt; font-weight: bold; color: {t['text_main']};"

    def _get_preview_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 12pt; font-weight: bold; color: {t['text_main']};"

    def _get_desc_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 10pt; color: {t['text_secondary']}; margin-bottom: 10px;"

    def _get_card_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QWidget {{ background-color: {t['card_bg']}; border-radius: 8px; "
            f"padding: 14px; }}"
        )

    def _get_card_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 12pt; font-weight: bold; color: {t['text_main']};"

    def _get_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 10pt; color: {t['text_main']};"

    def _get_label_secondary_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"font-size: 10pt; color: {t['text_secondary']};"

    def _get_input_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['input_border']}; border-radius: 4px;"
            f" padding: 0 12px; font-size: 10pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {t['primary']}; outline: none; }}"
        )

    def _get_primary_button_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: {t['primary']}; color: {t['text_primary']};"
            f" border: none; border-radius: 4px; font-size: 10pt;"
            f"}}"
            f"QPushButton:hover {{ background-color: {t['primary_hover']}; }}"
        )

    def _get_secondary_button_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: {t['card_bg']};"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" font-size: 10pt; color: {t['text_main']};"
            f"}}"
            f"QPushButton:hover {{ border: 1px solid {t['primary']}; }}"
        )

    def _get_preview_text_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QTextEdit {{"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" padding: 10px; font-family: 'Courier New', monospace;"
            f" font-size: 10pt; color: {t['text_main']};"
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
            f" padding: 10px 24px; margin-right: 4px;"
            f" border-top-left-radius: 6px; border-top-right-radius: 6px;"
            f" font-size: 10pt; color: {t['text_secondary']};"
            f"}}"
            f"QTabBar::tab:selected {{"
            f" background-color: {t['primary']}; color: {t['text_primary']};"
            f" font-weight: bold;"
            f"}}"
            f"QTabBar::tab:hover:!selected {{ background-color: {t['hover_bg']}; }}"
        )

    def _get_combo_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QComboBox {{"
            f" border: 1px solid {t['input_border']}; border-radius: 4px;"
            f" padding: 0 12px; font-size: 10pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QComboBox:focus {{ border-color: {t['primary']}; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{"
            f" border: 1px solid {t['input_border']}; selection-background-color: {t['primary']};"
            f"}}"
        )

    def _get_checkbox_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"QCheckBox {{ font-size: 10pt; color: {t['text_main']}; }}"

    def _get_radio_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"QRadioButton {{ font-size: 10pt; color: {t['text_secondary']}; }}"

    def _get_groupbox_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QGroupBox {{"
            f" border: 1px solid {t['border']}; border-radius: 6px;"
            f" margin-top: 12px; padding-top: 12px;"
            f" font-size: 10pt; font-weight: bold; color: {t['text_main']};"
            f"}}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}"
        )

    def _get_table_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QTableWidget {{"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" gridline-color: {t['border']};"
            f" background-color: {t['card_bg']}; color: {t['text_main']};"
            f" font-size: 10pt;"
            f"}}"
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_main']};"
            f" border: 1px solid {t['border']}; padding: 6px;"
            f"}}"
            f"QTableWidget::item {{ padding: 4px; }}"
            f"QTableWidget::item:selected {{ background-color: {t['primary']}; color: {t['text_primary']}; }}"
        )

    def _get_table_header_style(self) -> str:
        t = self._theme_engine.current_theme
        return (
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_secondary']};"
            f" border: none; padding: 8px; font-size: 9pt;"
            f"}}"
        )

    def _get_input_alt_style(self) -> str:
        """替代输入框样式（#CCCCCC 边框 + {t['card_bg']} 背景）"""
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['border_deep']}; padding: 4px 8px;"
            f" font-size: 10pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border: 1px solid {t['primary']}; }}"
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
        return f"font-size: 9pt; color: {t['text_secondary']};"

    def _get_bold_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 10pt; font-weight: bold;"

    def _get_hint_label_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 9pt;"

    def _get_method_label_style(self) -> str:
        """方法标签样式（#E5E5E5 背景 + #CCCCCC 边框）"""
        t = self._theme_engine.current_theme
        return (
            f"color: {t['text_main']}; font-size: 10pt; font-weight: bold;"
            f" background-color: {t['sidebar_bg']};"
            f" border: 1px solid {t['border_deep']}; padding: 4px 8px;"
        )

    def _get_method_field_label_style(self) -> str:
        """方法字段标签样式（#CCCCCC 边框）"""
        t = self._theme_engine.current_theme
        return (
            f"color: {t['text_main']}; font-size: 10pt;"
            f" border: 1px solid {t['border_deep']}; padding: 4px 8px;"
        )

    def _get_login_title_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"color: {t['text_main']}; font-size: 10pt; font-weight: bold;"

    def _get_danger_button_style(self) -> str:
        """危险/删除按钮样式（红色边框+文字，hover 加深）"""
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: transparent;"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" color: {t['text_secondary']}; font-size: 9pt;"
            f"}}"
            f"QPushButton:hover {{"
            f" border: 1px solid {t['danger']}; color: {t['danger']};"
            f"}}"
        )

    def _get_input_alt2_style(self) -> str:
        """替代输入框样式2（#CCCCCC 边框 + card_bg 背景，带 focus 高亮）"""
        t = self._theme_engine.current_theme
        return (
            f"QLineEdit {{"
            f" border: 1px solid {t['border_deep']}; padding: 4px 8px;"
            f" font-size: 10pt; color: {t['text_main']};"
            f" background-color: {t['card_bg']};"
            f"}}"
            f"QLineEdit:focus {{ border: 1px solid {t['primary']}; }}"
        )

    def _get_small_delete_btn_style(self) -> str:
        """小型删除按钮样式（60x24，hover 变红）"""
        t = self._theme_engine.current_theme
        return (
            f"QPushButton {{"
            f" background-color: {t['card_bg']};"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" color: {t['text_secondary']}; font-size: 9pt;"
            f"}}"
            f"QPushButton:hover {{"
            f" border: 1px solid {t['danger']}; color: {t['danger']};"
            f"}}"
        )

    def _get_table_with_selection_style(self) -> str:
        """带动态选中色的表格样式（替代内嵌的 #E6F0FF 选中色）"""
        t = self._theme_engine.current_theme
        return (
            f"QTableWidget {{"
            f" border: 1px solid {t['border']}; border-radius: 4px;"
            f" gridline-color: {t['border']};"
            f" background-color: {t['card_bg']}; color: {t['text_main']};"
            f" font-size: 10pt;"
            f"}}"
            f"QHeaderView::section {{"
            f" background-color: {t['sidebar_bg']}; color: {t['text_main']};"
            f" border: 1px solid {t['border']}; padding: 6px;"
            f"}}"
            f"QTableWidget::item {{ padding: 4px; }}"
            f"QTableWidget::item:selected {{ background-color: {t['primary']}; color: {t['text_primary']}; }}"
        )

    # ------------------------------------------------------------------
    # 原有方法（保持不变）
    # ------------------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        title_layout = QHBoxLayout()
        self.title_label = QLabel('配置页面')
        self.title_label.setStyleSheet(self._get_title_style())
        title_layout.addWidget(self.title_label)

        # 返回按钮
        back_button = QPushButton('返回上一级')
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet(self._get_secondary_button_style())
        back_button.clicked.connect(self.on_back_clicked)
        title_layout.addWidget(back_button)

        # 返回首页按钮
        home_button = QPushButton('返回首页')
        home_button.setFixedSize(100, 40)
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
        self.config_layout.setSpacing(10)
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
        generate_button.setFixedSize(100, 36)
        generate_button.setStyleSheet(self._get_primary_button_style())
        generate_button.clicked.connect(self.generate_config)
        preview_header.addWidget(generate_button)

        copy_button = QPushButton('复制脚本')
        copy_button.setFixedSize(100, 36)
        copy_button.setStyleSheet(self._get_secondary_button_style())
        copy_button.clicked.connect(self.copy_config)
        preview_header.addWidget(copy_button)

        export_button = QPushButton('导出配置')
        export_button.setFixedSize(100, 36)
        export_button.setStyleSheet(self._get_secondary_button_style())
        export_button.clicked.connect(self.export_config)
        preview_header.addWidget(export_button)

        reset_button = QPushButton('重置')
        reset_button.setFixedSize(80, 36)
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
        card_layout.setSpacing(10)

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
        form_layout.setSpacing(10)
        card_layout.addLayout(form_layout)

        card.setLayout(card_layout)
        return card

    def add_form_item(self, card, label_text, field_name, is_password=False, is_label=False, default_value=''):
        """添加表单项"""
        form_layout = card.layout().itemAt(2).layout()

        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(10)

        # 标签
        label = QLabel(label_text)
        label.setFixedWidth(120)
        label.setStyleSheet(self._get_label_style())
        item_layout.addWidget(label)

        # 输入框
        if is_label:
            input_field = QLabel(default_value)
            input_field.setStyleSheet(self._get_label_secondary_style())
        else:
            input_field = QLineEdit()
            input_field.setFixedHeight(32)
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
