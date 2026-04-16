from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from utils.resource_path import resource_path

class BaseConfigPage(QWidget):
    def __init__(self, parent, vendor, device_type):
        super().__init__()
        self.parent = parent
        self.vendor = vendor
        self.device_type = device_type
        self.vendor_names = {
            'ruijie': '锐捷',
            'huawei': '华为',
            'h3c': 'H3C',
            'cisco': '思科'
        }
        self.device_names = {
            'access_switch': '接入交换机',
            'core_switch': '核心交换机',
            'router': '路由器',
            'ac': '无线控制器'
        }
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏（60px高度）
        title_bar = QWidget()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet('background-color: #FFFFFF; border-bottom: 1px solid #E5E6EB;')
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(24, 0, 24, 0)
        
        # 标题
        vendor_name = self.vendor_names.get(self.vendor, self.vendor)
        device_name = self.device_names.get(self.device_type, self.device_type)
        title = QLabel(f'【{vendor_name}】{device_name}配置')
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: #1D2129;')
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # 返回按钮
        back_prev_button = QPushButton('返回上一级')
        back_prev_button.setFixedSize(96, 36)
        back_prev_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
                color: #165DFF;
            }
        """)
        back_prev_button.clicked.connect(self.go_back)
        title_layout.addWidget(back_prev_button)
        
        title_layout.addSpacing(16)
        
        back_home_button = QPushButton('返回首页')
        back_home_button.setFixedSize(80, 36)
        back_home_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
                color: #165DFF;
            }
        """)
        back_home_button.clicked.connect(self.go_home)
        title_layout.addWidget(back_home_button)
        
        title_bar.setLayout(title_layout)
        layout.addWidget(title_bar)
        
        # 主内容区
        main_content = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 左侧配置区（980px宽度，带滚动条）
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet('border: none; background-color: transparent;')
        
        left_widget = QWidget()
        left_widget.setStyleSheet('background-color: transparent;')
        self.left_layout = QVBoxLayout()
        self.left_layout.setSpacing(16)
        self.left_layout.setAlignment(Qt.AlignTop)
        left_widget.setLayout(self.left_layout)
        
        left_scroll.setWidget(left_widget)
        
        # 中间分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet('background-color: #E5E6EB;')
        
        # 右侧代码区（420px宽度）
        right_widget = QWidget()
        right_widget.setFixedWidth(420)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)
        
        # 右侧按钮置顶
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        generate_btn = QPushButton('生成配置')
        generate_btn.setFixedSize(96, 36)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                border: none;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        generate_btn.clicked.connect(self.generate_config)
        button_layout.addWidget(generate_btn)
        
        copy_btn = QPushButton('复制脚本')
        copy_btn.setFixedSize(88, 36)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
                color: #165DFF;
            }
        """)
        copy_btn.clicked.connect(self.copy_script)
        button_layout.addWidget(copy_btn)
        
        export_btn = QPushButton('导出配置')
        export_btn.setFixedSize(88, 36)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
                color: #165DFF;
            }
        """)
        export_btn.clicked.connect(self.export_config)
        button_layout.addWidget(export_btn)
        
        reset_btn = QPushButton('重置')
        reset_btn.setFixedSize(64, 36)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 1px solid #165DFF;
                color: #165DFF;
            }
        """)
        reset_btn.clicked.connect(self.reset_form)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        right_layout.addLayout(button_layout)
        
        # 代码显示区（带滚动条）
        self.code_editor = QTextEdit()
        self.code_editor.setReadOnly(True)
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: #F7F8FA;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        self.code_editor.setPlaceholderText('配置脚本将在这里显示...')
        right_layout.addWidget(self.code_editor)
        
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(left_scroll, 1)
        main_layout.addWidget(divider)
        main_layout.addWidget(right_widget)
        
        main_content.setLayout(main_layout)
        layout.addWidget(main_content, 1)
        
        # 底部版权栏（40px高度）
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(40)
        bottom_bar.setStyleSheet('background-color: #FFFFFF; border-top: 1px solid #E5E6EB;')
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(24, 0, 24, 0)
        bottom_layout.addStretch()
        
        info_label = QLabel('Copyright @ 2026 laohan  Released under the MIT License  开源地址: https://github.com/hanchunjun/network-config-generator')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('font-size: 12px; color: #86909C;')
        bottom_layout.addWidget(info_label)
        
        bottom_layout.addStretch()
        
        bottom_bar.setLayout(bottom_layout)
        layout.addWidget(bottom_bar)
        
        self.setLayout(layout)
        
    def go_back(self):
        """返回上一级页面"""
        self.parent.show_device_selection_from_config(self.vendor)
        
    def go_home(self):
        """返回首页"""
        self.parent.show_vendor_selection()
        
    def generate_config(self):
        """生成配置脚本"""
        pass
        
    def copy_script(self):
        """复制脚本到剪贴板"""
        pass
        
    def export_config(self):
        """导出配置文件"""
        pass
        
    def reset_form(self):
        """重置表单"""
        pass
