from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt

class BaseConfigPage(QWidget):
    def __init__(self, parent, vendor=None, device_type=None):
        super().__init__()
        self.parent = parent
        self.vendor = vendor
        self.device_type = device_type
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title_layout = QHBoxLayout()
        self.title_label = QLabel('配置页面')
        self.title_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        title_layout.addWidget(self.title_label)
        
        # 返回按钮
        back_button = QPushButton('返回上一级')
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
            }
        """)
        back_button.clicked.connect(self.on_back_clicked)
        title_layout.addWidget(back_button)
        
        # 返回首页按钮
        home_button = QPushButton('返回首页')
        home_button.setFixedSize(100, 40)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
            }
        """)
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
        preview_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        preview_header.addWidget(preview_label)
        preview_header.addStretch()
        
        generate_button = QPushButton('生成配置')
        generate_button.setFixedSize(100, 36)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        generate_button.clicked.connect(self.generate_config)
        preview_header.addWidget(generate_button)
        
        copy_button = QPushButton('复制脚本')
        copy_button.setFixedSize(100, 36)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
            }
        """)
        copy_button.clicked.connect(self.copy_config)
        preview_header.addWidget(copy_button)
        
        export_button = QPushButton('导出配置')
        export_button.setFixedSize(100, 36)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
            }
        """)
        export_button.clicked.connect(self.export_config)
        preview_header.addWidget(export_button)
        
        reset_button = QPushButton('重置')
        reset_button.setFixedSize(80, 36)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
            }
        """)
        reset_button.clicked.connect(self.reset_config)
        preview_header.addWidget(reset_button)
        
        preview_layout.addLayout(preview_header)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
        """)
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
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 14px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(10)
        
        # 卡片标题
        title_layout = QHBoxLayout()
        title_label = QLabel(f'{icon} {title}')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        
        # 卡片描述
        desc_label = QLabel(description)
        desc_label.setStyleSheet('font-size: 14px; color: #86909C; margin-bottom: 10px;')
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
        label.setStyleSheet('font-size: 14px;')
        item_layout.addWidget(label)
        
        # 输入框
        if is_label:
            input_field = QLabel(default_value)
            input_field.setStyleSheet('font-size: 14px; color: #86909C;')
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
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #E5E6EB;
                    border-radius: 4px;
                    padding: 0 12px;
                    font-size: 14px;
                    color: #1D2129;
                }
                QLineEdit:focus {
                    border-color: #165DFF;
                    outline: none;
                }
            """)
        
        item_layout.addWidget(input_field, 1)
        form_layout.addLayout(item_layout)

        return input_field

    def get_input_style(self):
        """获取输入框统一样式"""
        return """
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
                color: #1D2129;
            }
            QLineEdit:focus {
                border-color: #165DFF;
                outline: none;
            }
        """
