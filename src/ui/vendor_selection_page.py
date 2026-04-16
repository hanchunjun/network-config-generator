from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from utils.resource_path import resource_path

class VendorSelectionPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 设置背景为白色
        self.setStyleSheet('background-color: white;')
        
        # 标题
        title = QLabel('网络设备调试辅助工具')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 36px; font-weight: bold; letter-spacing: 5px; padding-top: 40px; margin-bottom: 60px; font-family: "SimSun", "宋体", serif;')
        layout.addWidget(title)
        
        # 上方伸缩项
        layout.addStretch()
        
        # 厂商按钮布局
        vendor_layout = QHBoxLayout()
        vendor_layout.setAlignment(Qt.AlignCenter)
        vendor_layout.setSpacing(60)
        
        # 锐捷
        ruijie_widget, ruijie_button = self.create_vendor_button('锐捷')
        ruijie_button.clicked.connect(lambda: self.on_vendor_clicked('ruijie'))
        vendor_layout.addWidget(ruijie_widget)
        
        # 华为
        huawei_widget, huawei_button = self.create_vendor_button('华为')
        huawei_button.clicked.connect(lambda: self.on_vendor_clicked('huawei'))
        vendor_layout.addWidget(huawei_widget)
        
        # 华三
        h3c_widget, h3c_button = self.create_vendor_button('H3C')
        h3c_button.clicked.connect(lambda: self.on_vendor_clicked('h3c'))
        vendor_layout.addWidget(h3c_widget)
        
        # 思科
        cisco_widget, cisco_button = self.create_vendor_button('思科')
        cisco_button.clicked.connect(lambda: self.on_vendor_clicked('cisco'))
        vendor_layout.addWidget(cisco_widget)
        
        layout.addLayout(vendor_layout)
        
        # 说明文字
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(0, 40, 0, 0)
        
        info_texts = [
            '本工具专门为网络工程师项目开局与调试维护打造',
            '支持锐捷、华为、华三、思科多厂商设备开局配置',
            '可视化填写参数，一键生成可直接上线的命令脚本',
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
        
    def create_vendor_button(self, name):
        """创建厂商按钮，返回widget和button两个对象"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        # 按钮
        button = QPushButton(name)
        button.setFixedSize(200, 120)
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                font-size: 60px;
                color: black;
            }
            QPushButton:hover {
                border: 2px solid #165DFF;
                background-color: #F5F7FA;
            }
        """)
        layout.addWidget(button)
        
        widget.setLayout(layout)
        return widget, button
        
    def on_vendor_clicked(self, vendor):
        """点击厂商按钮"""
        self.parent.show_device_selection(vendor)
