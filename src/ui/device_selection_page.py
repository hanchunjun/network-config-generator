from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from utils.resource_path import resource_path

class DeviceSelectionPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_vendor = ''
        self.vendor_names = {
            'ruijie': '锐捷',
            'huawei': '华为',
            'h3c': 'H3C',
            'cisco': '思科'
        }
        self.init_ui()
        
    def set_vendor(self, vendor):
        """设置当前厂商，并更新标题"""
        self.current_vendor = vendor
        vendor_name = self.vendor_names.get(vendor, vendor)
        self.title_label.setText(f'【{vendor_name}】设备类型选择')
        
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
        self.title_label = QLabel('【厂商】设备类型选择')
        self.title_label.setStyleSheet('font-size: 20px; color: #1D2129;')
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 返回首页按钮
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
        back_home_button.clicked.connect(self.on_back_home_clicked)
        title_layout.addWidget(back_home_button)
        
        title_bar.setLayout(title_layout)
        layout.addWidget(title_bar)
        
        # 上方伸缩项
        layout.addStretch()
        
        # 设备按钮布局
        device_layout = QHBoxLayout()
        device_layout.setAlignment(Qt.AlignCenter)
        device_layout.setSpacing(60)
        
        # 接入交换机
        access_widget, access_button = self.create_device_button('接入交换机')
        access_button.clicked.connect(lambda: self.on_device_clicked('access_switch'))
        device_layout.addWidget(access_widget)
        
        # 核心交换机
        core_widget, core_button = self.create_device_button('核心交换机')
        core_button.clicked.connect(lambda: self.on_device_clicked('core_switch'))
        device_layout.addWidget(core_widget)
        
        # 路由器
        router_widget, router_button = self.create_device_button('路由器')
        router_button.clicked.connect(lambda: self.on_device_clicked('router'))
        device_layout.addWidget(router_widget)
        
        # 无线控制器
        ac_widget, ac_button = self.create_device_button('无线控制器')
        ac_button.clicked.connect(lambda: self.on_device_clicked('ac'))
        device_layout.addWidget(ac_widget)
        
        layout.addLayout(device_layout)
        
        # 说明文字
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(0, 40, 0, 0)
        
        info_texts = [
            '请选择需要生成配置脚本的设备类型',
            '内置厂商标准模板，命令规范、开局即用',
            '支持配置预览、一键复制与导出',
            '-Ver 1.0.0｜开发：天技老韩'
        ]
        
        for text in info_texts:
            info_label = QLabel(text)
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet('font-size: 20px; font-weight: 500; color: #86909C;')
            info_layout.addWidget(info_label)
        
        layout.addLayout(info_layout)
        
        # 下方伸缩项
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_device_button(self, name):
        """创建设备按钮，返回widget和button两个对象"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        # 按钮
        button = QPushButton(name)
        button.setFixedSize(160, 116)
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover {
                border: 2px solid #165DFF;
                background-color: #F5F7FA;
            }
        """)
        layout.addWidget(button)
        
        widget.setLayout(layout)
        return widget, button
        
    def on_device_clicked(self, device_type):
        """点击设备按钮（跳转到三级配置页）"""
        self.parent.show_config_page(self.current_vendor, device_type)
        
    def on_back_home_clicked(self):
        """点击返回首页按钮"""
        self.parent.show_vendor_selection()
