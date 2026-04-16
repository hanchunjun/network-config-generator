from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.resource_path import resource_path
from ui.config_pages.ruijie.access_switch_config import RuijieAccessSwitchConfig
from ui.config_pages.ruijie.core_switch_config import RuijieCoreSwitchConfig
from ui.config_pages.ruijie.router_config import RuijieRouterConfig
from ui.config_pages.ruijie.ac_config import RuijieACConfig
from ui.config_pages.huawei.access_switch_config import HuaweiAccessSwitchConfig
from ui.config_pages.huawei.core_switch_config import HuaweiCoreSwitchConfig
from ui.config_pages.huawei.router_config import HuaweiRouterConfig
from ui.config_pages.huawei.ac_config import HuaweiACConfig
from ui.config_pages.h3c.access_switch_config import H3CAccessSwitchConfig
from ui.config_pages.h3c.core_switch_config import H3CCoreSwitchConfig
from ui.config_pages.h3c.router_config import H3CRouterConfig
from ui.config_pages.h3c.ac_config import H3CACConfig
from ui.config_pages.cisco.access_switch_config import CiscoAccessSwitchConfig
from ui.config_pages.cisco.core_switch_config import CiscoCoreSwitchConfig
from ui.config_pages.cisco.router_config import CiscoRouterConfig
from ui.config_pages.cisco.ac_config import CiscoACConfig

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('网络设备开局脚本生成工具')
        self.setGeometry(100, 100, 1400, 800)
        
        # 设置全局样式
        self.setup_global_style()
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建顶部选择栏
        self.create_top_selection_bar(main_layout)
        
        # 创建堆叠窗口，用于页面切换
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 配置页面对象字典（创建后不复用，避免删除操作）
        self.config_pages = {}
        
        # 初始化选择状态
        self.selected_vendor = None
        self.selected_device = None
        
        # 创建默认页面（可以是一个提示页面）
        self.create_default_page()
    
    def create_top_selection_bar(self, main_layout):
        """创建顶部选择栏"""
        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_bar.setLayout(top_layout)
        top_bar.setStyleSheet('background-color: white; padding: 10px; border-bottom: 1px solid #E5E6EB;')
        
        # 厂商选择按钮
        vendor_layout = QHBoxLayout()
        vendor_label = QPushButton('厂家选择:')
        vendor_label.setStyleSheet('font-weight: bold; border: none; background: none;')
        vendor_layout.addWidget(vendor_label)
        
        # 厂商按钮
        self.vendor_buttons = {}
        vendors = ['锐捷', '华为', '华三', '思科']
        vendor_ids = ['ruijie', 'huawei', 'h3c', 'cisco']
        
        for name, vendor_id in zip(vendors, vendor_ids):
            button = QPushButton(name)
            button.setFixedSize(100, 40)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #F5F7FA;
                    border: 1px solid #E5E6EB;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border: 1px solid #165DFF;
                }
                QPushButton.selected {
                    background-color: #165DFF;
                    color: white;
                    border: 1px solid #165DFF;
                }
            """)
            button.clicked.connect(lambda checked, vid=vendor_id: self.on_vendor_clicked(vid))
            self.vendor_buttons[vendor_id] = button
            vendor_layout.addWidget(button)
        
        # 设备选择按钮
        device_layout = QHBoxLayout()
        device_label = QPushButton('设备类型:')
        device_label.setStyleSheet('font-weight: bold; border: none; background: none;')
        device_layout.addWidget(device_label)
        
        # 设备按钮
        self.device_buttons = {}
        devices = ['接入交换机', '核心交换机', '路由器', 'AC']
        device_ids = ['access_switch', 'core_switch', 'router', 'ac']
        
        for name, device_id in zip(devices, device_ids):
            button = QPushButton(name)
            button.setFixedSize(120, 40)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #F5F7FA;
                    border: 1px solid #E5E6EB;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border: 1px solid #165DFF;
                }
                QPushButton.selected {
                    background-color: #165DFF;
                    color: white;
                    border: 1px solid #165DFF;
                }
            """)
            button.clicked.connect(lambda checked, did=device_id: self.on_device_clicked(did))
            self.device_buttons[device_id] = button
            device_layout.addWidget(button)
        
        # 添加到顶部布局
        top_layout.addLayout(vendor_layout)
        top_layout.addStretch()
        
        # 关于按钮
        about_button = QPushButton('关于')
        about_button.setFixedSize(80, 40)
        about_button.setStyleSheet("""
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
        about_button.clicked.connect(self.show_about_dialog)
        top_layout.addWidget(about_button)
        
        top_layout.addStretch()
        top_layout.addLayout(device_layout)
        
        main_layout.addWidget(top_bar)
    
    def create_default_page(self):
        """创建默认提示页面"""
        from PyQt5.QtWidgets import QLabel
        default_page = QWidget()
        layout = QVBoxLayout()
        default_page.setLayout(layout)
        
        label = QLabel('请选择厂家和设备类型')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('font-size: 24px; color: #86909C;')
        layout.addWidget(label)
        
        self.stacked_widget.addWidget(default_page)
        self.default_page = default_page
        
    def setup_global_style(self):
        """设置全局样式"""
        # 设置全局字体
        font = QFont("Microsoft YaHei", 9)
        self.setFont(font)
        
        # 设置全局样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }
            QWidget {
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 14px;
                color: #1D2129;
            }
        """)
        
    def on_vendor_clicked(self, vendor):
        """点击厂商按钮"""
        # 更新厂商按钮状态
        for vid, button in self.vendor_buttons.items():
            if vid == vendor:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #165DFF;
                        color: white;
                        border: 1px solid #165DFF;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                """)
            else:
                button.setStyleSheet("""
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
        
        # 更新选择状态
        self.selected_vendor = vendor
        
        # 尝试显示配置页面
        self.try_show_config_page()
    
    def on_device_clicked(self, device_type):
        """点击设备类型按钮"""
        # 更新设备按钮状态
        for did, button in self.device_buttons.items():
            if did == device_type:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #165DFF;
                        color: white;
                        border: 1px solid #165DFF;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                """)
            else:
                button.setStyleSheet("""
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
        
        # 更新选择状态
        self.selected_device = device_type
        
        # 尝试显示配置页面
        self.try_show_config_page()
    
    def try_show_config_page(self):
        """尝试显示配置页面"""
        if self.selected_vendor and self.selected_device:
            self.show_config_page(self.selected_vendor, self.selected_device)
    
    def show_config_page(self, vendor, device_type):
        """显示配置页面"""
        page_key = f"{vendor}_{device_type}"
        
        if page_key in self.config_pages:
            config_page = self.config_pages[page_key]
            self.stacked_widget.setCurrentWidget(config_page)
            return
        
        config_page = None
        
        if vendor == 'ruijie':
            if device_type == 'access_switch':
                config_page = RuijieAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = RuijieCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = RuijieRouterConfig(self)
            elif device_type == 'ac':
                config_page = RuijieACConfig(self)
        elif vendor == 'huawei':
            if device_type == 'access_switch':
                config_page = HuaweiAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = HuaweiCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = HuaweiRouterConfig(self)
            elif device_type == 'ac':
                config_page = HuaweiACConfig(self)
        elif vendor == 'h3c':
            if device_type == 'access_switch':
                config_page = H3CAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = H3CCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = H3CRouterConfig(self)
            elif device_type == 'ac':
                config_page = H3CACConfig(self)
        elif vendor == 'cisco':
            if device_type == 'access_switch':
                config_page = CiscoAccessSwitchConfig(self)
            elif device_type == 'core_switch':
                config_page = CiscoCoreSwitchConfig(self)
            elif device_type == 'router':
                config_page = CiscoRouterConfig(self)
            elif device_type == 'ac':
                config_page = CiscoACConfig(self)
        
        if config_page:
            self.config_pages[page_key] = config_page
            self.stacked_widget.addWidget(config_page)
            self.stacked_widget.setCurrentWidget(config_page)
        
    def show_vendor_selection(self):
        """显示厂商选择页面（兼容旧代码）"""
        pass
    
    def show_device_selection(self, vendor):
        """显示设备选择页面（兼容旧代码）"""
        pass
    
    def show_device_selection_from_config(self, vendor):
        """从配置页返回设备选择页（兼容旧代码）"""
        pass
    
    def show_about_dialog(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle('关于')
        dialog.setFixedSize(400, 220)
        dialog.setWindowModality(Qt.ApplicationModal)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel('网络设备配置脚本生成工具')
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 版本
        version_label = QLabel('V1.0.0 测试版')
        version_label.setAlignment(Qt.AlignLeft)
        version_label.setStyleSheet('font-size: 14px;')
        layout.addWidget(version_label)
        
        # 描述
        desc1 = QLabel('一款面向网络工程师的多厂商设备配置脚本生成工具，支持锐捷、华为、华三、思科等设备命令生成')
        desc1.setAlignment(Qt.AlignLeft)
        desc1.setStyleSheet('font-size: 14px;')
        desc1.setWordWrap(True)
        layout.addWidget(desc1)
        
        desc2 = QLabel('开源项目地址: https://github.com/hanchunjun/network-config-generator')
        desc2.setAlignment(Qt.AlignLeft)
        desc2.setStyleSheet('font-size: 14px;')
        layout.addWidget(desc2)
        
        desc3 = QLabel('Copyright @ 2026 laohan')
        desc3.setAlignment(Qt.AlignLeft)
        desc3.setStyleSheet('font-size: 14px;')
        layout.addWidget(desc3)
        
        desc4 = QLabel('Released under the MIT License')
        desc4.setAlignment(Qt.AlignLeft)
        desc4.setStyleSheet('font-size: 14px;')
        layout.addWidget(desc4)
        
        desc5 = QLabel('本软件为开源免费工具，仅供学习交流与工程实施使用。不代表任何厂商官方立场，无任何官方认证')
        desc5.setAlignment(Qt.AlignLeft)
        desc5.setStyleSheet('font-size: 14px;')
        desc5.setWordWrap(True)
        layout.addWidget(desc5)
        
        # 关闭按钮
        close_button = QPushButton('关闭')
        close_button.setFixedSize(100, 40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        close_button.clicked.connect(dialog.close)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
