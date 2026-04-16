from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class H3CAccessSwitchConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'h3c', 'access_switch')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
        """初始化所有面板和卡片，使用Tab分组"""
        
        # 创建TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #F2F3F5;
            }
            QTabBar::tab {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-bottom: none;
                padding: 10px 24px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
                color: #4E5969;
            }
            QTabBar::tab:selected {
                background-color: #165DFF;
                color: #FFFFFF;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #F7F8FA;
            }
        """)
        
        # Tab1：基础配置
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码、Console密码和系统时间')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable特权密码', 'enable_password', is_password=True)
        self.add_form_item(card1, 'Console登录密码', 'console_password', is_password=True)
        self.add_form_item(card1, '系统时间', 'system_time')
        self.add_form_item(card1, '时区', 'timezone', is_label=True, default_value='北京时区 +8')
        
        card2 = self.create_card('VLAN基础配置', '🌐', '批量创建VLAN，支持连续范围如2 to 10')
        # 添加输入提示
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('批量创建:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        item_layout.addWidget(input_widget)
        self.form_fields['business_vlan'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('输入示例：2 to 8，11或2-8，11')
        hint_label.setStyleSheet('color: #000000; font-size: 12px;')
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card2.layout.addLayout(item_layout)
        
        card3 = self.create_card('管理地址与网关配置', '📍', '配置管理VLAN、IP地址、子网掩码和默认网关')
        self.add_form_item(card3, '管理VLAN ID', 'mgmt_vlan')
        
        # 管理IP输入框带提示
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('管理IP:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(32)
        input_widget.setFixedWidth(200)
        input_widget.setStyleSheet("""
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
        item_layout.addWidget(input_widget)
        self.form_fields['mgmt_ip'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('输入示例：192.168.0.2')
        hint_label.setStyleSheet('color: #000000; font-size: 12px;')
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card3.layout.addLayout(item_layout)
        
        # 子网掩码输入框带提示
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('子网掩码:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(32)
        input_widget.setFixedWidth(200)
        input_widget.setStyleSheet("""
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
        item_layout.addWidget(input_widget)
        self.form_fields['subnet_mask'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('输入示例：255.255.255.0')
        hint_label.setStyleSheet('color: #000000; font-size: 12px;')
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card3.layout.addLayout(item_layout)
        
        # 默认网关地址输入框带提示
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('默认网关地址:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(32)
        input_widget.setFixedWidth(200)
        input_widget.setStyleSheet("""
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
        item_layout.addWidget(input_widget)
        self.form_fields['gateway'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('输入示例：192.168.0.1')
        hint_label.setStyleSheet('color: #000000; font-size: 12px;')
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card3.layout.addLayout(item_layout)
        
        card4 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录方式及用户名密码')
        self.add_form_item(card4, 'SSH用户名', 'ssh_user')
        self.add_form_item(card4, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card4, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addWidget(card4)
        tab1.layout.addStretch()
        self.tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：端口与上联配置
        tab2 = self.create_tab_content()
        card5 = self.create_card('下联Access端口配置', '🔌', '批量配置接入端口并划分到指定VLAN')
        
        # 配置区域
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        # 接口类型
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(12)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        interface_layout.addWidget(interface_label)
        self.access_interface_combo = QComboBox()
        self.access_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.access_interface_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        interface_layout.addWidget(self.access_interface_combo)
        config_layout.addLayout(interface_layout)
        
        # 端口范围
        port_layout = QVBoxLayout()
        port_layout.setSpacing(12)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(12)
        self.access_start_port = QLineEdit()
        self.access_start_port.setPlaceholderText('开始端口')
        self.access_start_port.setFixedWidth(100)
        self.access_start_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        port_range_layout.addWidget(self.access_start_port)
        
        port_dash_label = QLabel('—')
        port_dash_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        port_range_layout.addWidget(port_dash_label)
        
        self.access_end_port = QLineEdit()
        self.access_end_port.setPlaceholderText('结束端口')
        self.access_end_port.setFixedWidth(100)
        self.access_end_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        port_range_layout.addWidget(self.access_end_port)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        # 加入VLAN
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(12)
        vlan_label = QLabel('加入VLAN:')
        vlan_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        vlan_layout.addWidget(vlan_label)
        self.access_vlan_input = QLineEdit()
        self.access_vlan_input.setPlaceholderText('VLAN ID')
        self.access_vlan_input.setFixedWidth(140)
        self.access_vlan_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        vlan_layout.addWidget(self.access_vlan_input)
        config_layout.addLayout(vlan_layout)
        
        # 新增按钮
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                border: none;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        # 表格区域
        self.access_table = QTableWidget()
        self.access_table.setColumnCount(5)
        self.access_table.setHorizontalHeaderLabels(['接口', '开始端口', '结束端口', '加入VLAN', '操作'])
        self.access_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F2F3F5;
                border: none;
                padding: 8px;
                font-size: 12px;
                color: #4E5969;
            }
        """)
        self.access_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 14px;
            }
        """)
        # 禁用水平滚动条，禁用垂直滚动条
        self.access_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.access_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 自动调整列宽
        self.access_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格行高
        self.access_table.verticalHeader().setDefaultSectionSize(36)
        # 初始化表格行数
        self.access_table.setRowCount(0)
        # 固定表格宽度
        self.access_table.setFixedWidth(780)
        # 初始设置表格高度
        self.access_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_access_port(self.access_interface_combo, self.access_start_port, self.access_end_port, self.access_vlan_input, self.access_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card5.layout.addLayout(config_layout)
        card5.layout.addWidget(self.access_table)
        
        card6 = self.create_card('上联Trunk端口配置', '🌐', '配置上联端口为Trunk模式，调整速率、双工和光电复用')
        
        # 配置区域
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        # 接口类型
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(12)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        interface_layout.addWidget(interface_label)
        self.trunk_interface_combo = QComboBox()
        self.trunk_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.trunk_interface_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        interface_layout.addWidget(self.trunk_interface_combo)
        config_layout.addLayout(interface_layout)
        
        # 端口范围
        port_layout = QVBoxLayout()
        port_layout.setSpacing(12)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(12)
        self.trunk_start_port = QLineEdit()
        self.trunk_start_port.setPlaceholderText('开始端口')
        self.trunk_start_port.setFixedWidth(100)
        self.trunk_start_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        port_range_layout.addWidget(self.trunk_start_port)
        
        port_dash_label = QLabel('—')
        port_dash_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        port_range_layout.addWidget(port_dash_label)
        
        self.trunk_end_port = QLineEdit()
        self.trunk_end_port.setPlaceholderText('结束端口')
        self.trunk_end_port.setFixedWidth(100)
        self.trunk_end_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        port_range_layout.addWidget(self.trunk_end_port)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        # 允许通行VLAN
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(12)
        vlan_label = QLabel('允许通行VLAN:')
        vlan_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        vlan_layout.addWidget(vlan_label)
        self.trunk_vlan_input = QLineEdit()
        self.trunk_vlan_input.setPlaceholderText('VLAN ID')
        self.trunk_vlan_input.setFixedWidth(140)
        self.trunk_vlan_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #165DFF;
            }
        """)
        vlan_layout.addWidget(self.trunk_vlan_input)
        config_layout.addLayout(vlan_layout)
        
        # 新增按钮
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                border: none;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        # 表格区域
        self.trunk_table = QTableWidget()
        self.trunk_table.setColumnCount(5)
        self.trunk_table.setHorizontalHeaderLabels(['接口', '开始端口', '结束端口', '允许通行VLAN', '操作'])
        self.trunk_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F2F3F5;
                border: none;
                padding: 8px;
                font-size: 12px;
                color: #4E5969;
            }
        """)
        self.trunk_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 14px;
            }
        """)
        # 禁用水平滚动条，禁用垂直滚动条
        self.trunk_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.trunk_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 自动调整列宽
        self.trunk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格行高
        self.trunk_table.verticalHeader().setDefaultSectionSize(36)
        # 初始化表格行数
        self.trunk_table.setRowCount(0)
        # 固定表格宽度
        self.trunk_table.setFixedWidth(780)
        # 初始设置表格高度
        self.trunk_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_trunk_port(self.trunk_interface_combo, self.trunk_start_port, self.trunk_end_port, self.trunk_vlan_input, self.trunk_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card6.layout.addLayout(config_layout)
        card6.layout.addWidget(self.trunk_table)
        
        card7 = self.create_card('链路聚合 (Bridge-Aggregation)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
        # 配置区域
        config_layout = QHBoxLayout()
        config_layout.setSpacing(16)
        
        # 聚合ID
        agg_id_layout = QVBoxLayout()
        agg_id_layout.setSpacing(8)
        agg_id_label = QLabel('聚合ID:')
        agg_id_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        agg_id_layout.addWidget(agg_id_label)
        self.agg_id_input = QLineEdit()
        self.agg_id_input.setPlaceholderText('1')
        self.agg_id_input.setText('1')
        self.agg_id_input.setFixedWidth(80)
        self.agg_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        agg_id_layout.addWidget(self.agg_id_input)
        config_layout.addLayout(agg_id_layout)
        
        # 模式选择
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(8)
        mode_label = QLabel('模式:')
        mode_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        mode_layout.addWidget(mode_label)
        self.agg_mode_combo = QComboBox()
        self.agg_mode_combo.addItems(['LACP (动态)', 'Manual (静态)'])
        self.agg_mode_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        mode_layout.addWidget(self.agg_mode_combo)
        config_layout.addLayout(mode_layout)
        
        # 负载均衡
        lb_layout = QVBoxLayout()
        lb_layout.setSpacing(8)
        lb_label = QLabel('负载均衡:')
        lb_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        lb_layout.addWidget(lb_label)
        self.agg_lb_combo = QComboBox()
        self.agg_lb_combo.addItems(['src-dst-ip (推荐)', 'src-dst-mac', 'src-dst-port'])
        self.agg_lb_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        lb_layout.addWidget(self.agg_lb_combo)
        config_layout.addLayout(lb_layout)
        
        # 成员端口
        member_layout = QVBoxLayout()
        member_layout.setSpacing(8)
        member_label = QLabel('成员端口:')
        member_label.setStyleSheet('color: #4E5969; font-size: 14px;')
        member_layout.addWidget(member_label)
        member_port_layout = QHBoxLayout()
        member_port_layout.setSpacing(8)
        self.agg_interface_combo = QComboBox()
        self.agg_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.agg_interface_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        member_port_layout.addWidget(self.agg_interface_combo)
        self.agg_start_port = QLineEdit()
        self.agg_start_port.setPlaceholderText('开始')
        self.agg_start_port.setFixedWidth(60)
        self.agg_start_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        member_port_layout.addWidget(self.agg_start_port)
        member_port_layout.addWidget(QLabel('至'))
        self.agg_end_port = QLineEdit()
        self.agg_end_port.setPlaceholderText('结束')
        self.agg_end_port.setFixedWidth(60)
        self.agg_end_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
        """)
        member_port_layout.addWidget(self.agg_end_port)
        member_layout.addLayout(member_port_layout)
        config_layout.addLayout(member_layout)
        
        # 创建聚合组按钮
        create_button = QPushButton('创建聚合组')
        create_button.setFixedSize(120, 40)
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #165DFF;
                border: none;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0E42D2;
            }
        """)
        config_layout.addWidget(create_button)
        
        config_layout.addStretch()
        card7.layout.addLayout(config_layout)
        
        # 聚合组表格
        self.agg_table = QTableWidget()
        self.agg_table.setColumnCount(5)
        self.agg_table.setHorizontalHeaderLabels(['聚合ID', '模式', '均衡方式', '成员', '操作'])
        self.agg_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F2F3F5;
                border: none;
                padding: 8px;
                font-size: 12px;
                color: #4E5969;
            }
        """)
        self.agg_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.agg_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.agg_table.verticalHeader().setDefaultSectionSize(36)
        self.agg_table.setRowCount(0)
        self.agg_table.setMinimumWidth(600)
        self.agg_table.setFixedHeight(50)
        card7.layout.addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addWidget(card7)
        tab2.layout.addStretch()
        self.tab_widget.addTab(tab2.widget, '🔌 端口与上联')
        
        # Tab3：安全与防环配置
        tab3 = self.create_tab_content()
        card8 = self.create_card('DHCP Snooping功能', '📶', '开启DHCP监听，防止伪DHCP服务器，配置信任端口')
        self.add_form_item(card8, '信任端口号', 'trust_port')
        
        card9 = self.create_card('接口防环配置', '🛡️', '开启RLDP防环功能，配置环路检测端口')
        self.add_form_item(card9, '防环端口范围', 'loop_port')
        
        card10 = self.create_card('生成树MSTP配置', '🌐', '配置MST多生成树实例，划分VLAN到不同实例')
        self.add_form_item(card10, 'MST实例1 VLAN', 'mst_vlan1')
        self.add_form_item(card10, 'MST实例2 VLAN', 'mst_vlan2')
        self.add_form_item(card10, '优先级', 'mst_prio')
        
        card11 = self.create_card('ACL访问控制列表', '📜', '配置访问控制列表，限制访问管理VLAN的来源')
        self.add_form_item(card11, '允许管理网段', 'allow_segment')
        self.add_form_item(card11, '允许主机', 'allow_host')
        self.add_form_item(card11, '拒绝网段1', 'deny_segment1')
        self.add_form_item(card11, '拒绝网段2', 'deny_segment2')
        self.add_form_item(card11, '管理VLAN', 'mgmt_vlan_acl')
        
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addWidget(card10)
        tab3.layout.addWidget(card11)
        tab3.layout.addStretch()
        self.tab_widget.addTab(tab3.widget, '🔒 安全与防环')
        
        # Tab4：运维与调试功能
        tab4 = self.create_tab_content()
        card12 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器，自动同步设备时钟')
        self.add_form_item(card12, 'NTP服务器地址', 'ntp_server')
        
        card13 = self.create_card('SNMPv2配置', '📈', '开启SNMP功能，配置团体名和Trap告警服务器')
        self.add_form_item(card13, 'SNMP只读团体名', 'snmp_community')
        self.add_form_item(card13, 'Trap服务器地址', 'trap_server')
        
        card14 = self.create_card('端口镜像配置', '📋', '配置端口镜像，将流量复制到监控端口')
        self.add_form_item(card14, '镜像源端口', 'mirror_src')
        self.add_combo_item(card14, '流量方向', 'mirror_dir', ['rx', 'tx', 'both'])
        self.add_form_item(card14, '镜像目的端口', 'mirror_dst')
        
        card15 = self.create_card('AAA本地认证配置', '🔐', '配置AAA本地认证，统一管理登录用户')
        self.add_form_item(card15, 'AAA用户名', 'aaa_user')
        self.add_form_item(card15, 'AAA密码', 'aaa_pwd', is_password=True)
        
        tab4.layout.addWidget(card12)
        tab4.layout.addWidget(card13)
        tab4.layout.addWidget(card14)
        tab4.layout.addWidget(card15)
        tab4.layout.addStretch()
        self.tab_widget.addTab(tab4.widget, '📊 运维与调试')
        
        # 将TabWidget添加到左侧布局
        self.left_layout.addWidget(self.tab_widget)
        
    def create_tab_content(self):
        """创建Tab页内容容器，带滚动区域"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('border: none; background-color: #F2F3F5;')
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setStyleSheet('background-color: #F2F3F5;')
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop)
        container.setLayout(layout)
        
        scroll_area.setWidget(container)
        
        class TabContent:
            def __init__(self, scroll_area, layout):
                self.widget = scroll_area
                self.layout = layout
        
        return TabContent(scroll_area, layout)
        
    def create_card(self, title, icon, description=''):
        """创建卡片，带功能描述"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 卡片标题与勾选框
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        checkbox = QCheckBox()
        checkbox.setStyleSheet('QCheckBox::indicator { width: 18px; height: 18px; }')
        title_layout.addWidget(checkbox)
        
        title_label = QLabel(f'{icon} {title}')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #1D2129;')
        title_layout.addWidget(title_label)
        
        # 功能描述（如果有）
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet('font-size: 12px; color: #86909C;')
            title_layout.addWidget(desc_label)
        
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet('background-color: #E5E6EB;')
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        card.setLayout(layout)
        card.layout = layout
        card.checkbox = checkbox
        card.title = title
        self.cards.append(card)
        return card
        
    def add_form_item(self, card, label_text, field_name, is_password=False, is_label=False, default_value=''):
        """添加表单项"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        if is_label:
            # 标签模式（不可编辑）
            value_label = QLabel(default_value)
            value_label.setStyleSheet('color: #1D2129; font-size: 14px;')
            item_layout.addWidget(value_label)
        else:
            # 输入框模式
            input_field = QLineEdit()
            input_field.setFixedHeight(32)
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
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
            if default_value:
                input_field.setText(default_value)
            item_layout.addWidget(input_field)
            self.form_fields[field_name] = input_field
        
        card.layout.addLayout(item_layout)
        
    def add_combo_item(self, card, label_text, field_name, options):
        """添加下拉选择框"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setFixedHeight(32)
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
                color: #1D2129;
            }
            QComboBox:focus {
                border-color: #165DFF;
                outline: none;
            }
        """)
        item_layout.addWidget(combo)
        self.form_fields[field_name] = combo
        
        card.layout.addLayout(item_layout)
        
    def generate_config(self):
        """生成配置脚本（覆盖基类方法）"""
        data = self.get_form_data()
        checked_cards = self.get_checked_cards()
        
        config = []
        config_commands = []
        
        if '设备基础信息' in checked_cards:
            if data.get('hostname'):
                config_commands.append(f"sysname {data.get('hostname')}")
            if data.get('enable_password'):
                config_commands.append(f"super password level 3 hash {data.get('enable_password')}")
            if data.get('console_password'):
                config_commands.append(f"line console 0")
                config_commands.append(f"password {data.get('console_password')}")
                config_commands.append(f"login")
                config_commands.append(f"quit")
            if data.get('system_time'):
                config_commands.append(f"clock datetime {data.get('system_time')}")
                config_commands.append(f"clock timezone beijing 8")
        
        if 'VLAN基础配置' in checked_cards:
            if data.get('business_vlan'):
                vlan_input = data.get('business_vlan').strip()
                # 替换中文逗号为英文逗号，支持中英文逗号输入
                vlan_input = vlan_input.replace('，', ',')
                # 处理逗号分隔的多个项
                items = [item.strip() for item in vlan_input.split(',') if item.strip()]
                for item in items:
                    # 处理连续范围格式，如 "2 to 4" 或 "2-4"
                    if ' to ' in item:
                        parts = item.split(' to ')
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                for vlan_id in range(start, end + 1):
                                    config_commands.append(f"vlan {vlan_id}")
                                    config_commands.append("quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append("quit")
                    elif '-' in item:
                        parts = item.split('-')
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                for vlan_id in range(start, end + 1):
                                    config_commands.append(f"vlan {vlan_id}")
                                    config_commands.append("quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append("quit")
                    else:
                        # 处理单个VLAN
                        config_commands.append(f"vlan {item}")
                        config_commands.append("quit")
        
        if '管理地址与网关配置' in checked_cards:
            if data.get('mgmt_vlan'):
                config_commands.append(f"vlan {data.get('mgmt_vlan')}")
                config_commands.append(f"name manage")
                config_commands.append(f"quit")
                if data.get('mgmt_ip'):
                    config_commands.append(f"interface vlan-interface {data.get('mgmt_vlan')}")
                    subnet = data.get('subnet_mask', '255.255.255.0')
                    config_commands.append(f"ip address {data.get('mgmt_ip')} {subnet}")
                    config_commands.append(f"quit")
            if data.get('gateway'):
                config_commands.append(f"ip route-static 0.0.0.0 0 {data.get('gateway')}")
        
        if '远程登录配置' in checked_cards:
            if data.get('ssh_user') and data.get('ssh_pwd'):
                config_commands.append(f"ssh server enable")
                config_commands.append(f"local-user {data.get('ssh_user')}")
                config_commands.append(f"password simple {data.get('ssh_pwd')}")
                config_commands.append(f"service-type ssh")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"authentication-mode scheme")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
            if data.get('telnet_pwd'):
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"password {data.get('telnet_pwd')}")
                config_commands.append(f"login")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
        
        if '下联Access端口配置' in checked_cards:
            # 从表格中读取Access端口配置
            for row in range(self.access_table.rowCount()):
                interface = self.access_table.item(row, 0).text()
                start_port = self.access_table.item(row, 1).text()
                end_port = self.access_table.item(row, 2).text()
                vlan = self.access_table.item(row, 3).text()
                
                if start_port and end_port and vlan:
                    if start_port == end_port:
                        config_commands.append(f"interface {interface}{start_port}")
                    else:
                        config_commands.append(f"interface range {interface}{start_port} to {interface}{end_port}")
                    config_commands.append(f"port link-type access")
                    config_commands.append(f"port access vlan {vlan}")
                    config_commands.append(f"quit")
        
        if '上联Trunk端口配置' in checked_cards:
            # 从表格中读取Trunk端口配置
            for row in range(self.trunk_table.rowCount()):
                interface = self.trunk_table.item(row, 0).text()
                start_port = self.trunk_table.item(row, 1).text()
                end_port = self.trunk_table.item(row, 2).text()
                vlan = self.trunk_table.item(row, 3).text()
                
                if start_port and end_port and vlan:
                    if start_port == end_port:
                        config_commands.append(f"interface {interface}{start_port}")
                    else:
                        config_commands.append(f"interface range {interface}{start_port} to {interface}{end_port}")
                    config_commands.append(f"port link-type trunk")
                    if vlan == 'all':
                        config_commands.append(f"port trunk permit vlan all")
                    else:
                        config_commands.append(f"port trunk permit vlan {vlan}")
                    config_commands.append(f"quit")
        
        if '链路聚合 (Bridge-Aggregation)' in checked_cards:
            # 处理表格中的链路聚合配置
            if hasattr(self, 'agg_table') and self.agg_table.rowCount() > 0:
                # 全局配置负载均衡算法（只配置一次）
                # 获取第一个聚合组的负载均衡配置
                first_lb_item = self.agg_table.item(0, 2)
                if first_lb_item:
                    lb = first_lb_item.text()
                    # 提取负载均衡算法
                    if 'src-dst-port' in lb:
                        lb_algorithm = 'src-dst-port'
                    elif 'src-dst-mac' in lb:
                        lb_algorithm = 'src-dst-mac'
                    else:
                        lb_algorithm = 'src-dst-ip'
                    config_commands.append(f"link-aggregation load-sharing mode {lb_algorithm}")
                
                for row in range(self.agg_table.rowCount()):
                    # 获取聚合组信息
                    agg_id_item = self.agg_table.item(row, 0)
                    mode_item = self.agg_table.item(row, 1)
                    lb_item = self.agg_table.item(row, 2)
                    member_item = self.agg_table.item(row, 3)
                    
                    if agg_id_item and mode_item and lb_item and member_item:
                        agg_id = agg_id_item.text().split(' ')[-1]  # 提取聚合ID
                        mode = mode_item.text()
                        lb = lb_item.text()
                        member = member_item.text()
                        
                        # 解析成员端口范围
                        # 格式：G 0/1 to G 0/4 或 Te 0/1 to Te 0/4
                        import re
                        match = re.match(r'([A-Za-z\s]+)(\d+/)(\d+)\s+to\s+\1\2(\d+)', member)
                        if match:
                            interface_type = match.group(1).strip()
                            interface_num = match.group(2)
                            start = match.group(3)
                            end = match.group(4)
                            
                            # 构建完整接口类型
                            full_interface_type = 'GigabitEthernet'
                            if interface_type == 'Te':
                                full_interface_type = 'Ten-GigabitEthernet'
                            
                            # 构建端口范围字符串
                            port_range = f"{interface_num}{start} to {interface_num}{end}"
                            
                            # 配置聚合端口
                            config_commands.append(f"interface Bridge-Aggregation {agg_id}")
                            config_commands.append(f"port link-type trunk")
                            config_commands.append(f"port trunk permit vlan all")
                            if mode == 'LACP':
                                config_commands.append(f"link-aggregation mode dynamic")
                            else:
                                config_commands.append(f"link-aggregation mode manual")
                            config_commands.append(f"quit")
                            
                            # 配置成员端口
                            config_commands.append(f"interface range {full_interface_type} {port_range}")
                            config_commands.append(f"port link-aggregation group {agg_id}")
                            config_commands.append(f"quit")
        
        if 'DHCP Snooping功能' in checked_cards:
            if data.get('trust_port'):
                config_commands.append(f"dhcp-snooping enable")
                config_commands.append(f"interface GigabitEthernet {data.get('trust_port')}")
                config_commands.append(f"dhcp-snooping trust")
                config_commands.append(f"quit")
        
        if '接口防环配置' in checked_cards:
            if data.get('loop_port'):
                config_commands.append(f"stp enable")
                config_commands.append(f"interface range GigabitEthernet {data.get('loop_port')}")
                config_commands.append(f"stp edged-port enable")
                config_commands.append(f"quit")
        
        if '生成树MSTP配置' in checked_cards:
            config_commands.append(f"stp mode mstp")
            config_commands.append(f"stp region-configuration")
            if data.get('mst_vlan1'):
                config_commands.append(f"instance 1 vlan {data.get('mst_vlan1')}")
            if data.get('mst_vlan2'):
                config_commands.append(f"instance 2 vlan {data.get('mst_vlan2')}")
            if data.get('mst_prio'):
                config_commands.append(f"stp instance 1 priority {data.get('mst_prio')}")
            config_commands.append(f"active region-configuration")
        
        if 'ACL访问控制列表' in checked_cards:
            if data.get('allow_segment'):
                config_commands.append(f"acl number 2000")
                config_commands.append(f"rule permit source {data.get('allow_segment')} 0.0.0.255")
                config_commands.append(f"quit")
                if data.get('mgmt_vlan_acl'):
                    config_commands.append(f"interface vlan-interface {data.get('mgmt_vlan_acl')}")
                    config_commands.append(f"packet-filter 2000 inbound")
                    config_commands.append(f"quit")
        
        if 'NTP时钟同步' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp-service unicast-server {data.get('ntp_server')}")
        
        if 'SNMPv2配置' in checked_cards:
            config_commands.append(f"snmp-agent")
            if data.get('snmp_community'):
                config_commands.append(f"snmp-agent community read {data.get('snmp_community')}")
            if data.get('trap_server'):
                config_commands.append(f"snmp-agent target-host trap address udp-domain {data.get('trap_server')} params securityname {data.get('snmp_community', 'public')}")
        
        if '端口镜像配置' in checked_cards:
            if data.get('mirror_src') and data.get('mirror_dst'):
                config_commands.append(f"mirroring-group 1 local")
                config_commands.append(f"mirroring-group 1 mirror-port GigabitEthernet {data.get('mirror_src')}")
                config_commands.append(f"mirroring-group 1 monitor-port GigabitEthernet {data.get('mirror_dst')}")
        
        if 'AAA本地认证配置' in checked_cards:
            if data.get('aaa_user') and data.get('aaa_pwd'):
                config_commands.append(f"local-user {data.get('aaa_user')}")
                config_commands.append(f"password simple {data.get('aaa_pwd')}")
                config_commands.append(f"service-type terminal ssh telnet")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
        
        # 生成最终配置
        if config_commands:
            config.extend(config_commands)
            config.append("save force")
        
        self.code_editor.setPlainText('\n'.join(config))
    
    def get_form_data(self):
        """获取表单数据"""
        data = {}
        for field_name, widget in self.form_fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
        return data
    
    def get_checked_cards(self):
        """获取勾选的卡片标题列表"""
        checked = []
        for card in self.cards:
            if card.checkbox.isChecked():
                checked.append(card.title)
        return checked
    
    def reset_all_fields(self):
        """重置所有表单"""
        for widget in self.form_fields.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        for card in self.cards:
            card.checkbox.setChecked(False)
    
    def copy_script(self):
        """复制脚本到剪贴板（覆盖基类方法）"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_editor.toPlainText())
    
    def export_config(self):
        """导出配置文件（覆盖基类方法）"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            '导出配置文件', 
            '', 
            '配置文件 (*.txt);;所有文件 (*.*)'
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
    
    def add_access_port(self, interface_combo, start_port, end_port, vlan_input, table):
        """添加Access端口配置到表格"""
        interface = interface_combo.currentText()
        start = start_port.text()
        end = end_port.text()
        vlan = vlan_input.text()
        
        if not start or not end or not vlan:
            return
        
        # 添加到表格
        row = table.rowCount()
        table.insertRow(row)
        
        # 接口
        table.setItem(row, 0, QTableWidgetItem(interface))
        # 开始端口
        table.setItem(row, 1, QTableWidgetItem(start))
        # 结束端口
        table.setItem(row, 2, QTableWidgetItem(end))
        # 加入VLAN
        table.setItem(row, 3, QTableWidgetItem(vlan))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 12px;
            }
            QPushButton:hover {
                border: 1px solid #F5222D;
                color: #F5222D;
            }
        """)
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)
        
        # 计算表格的总高度并设置
        row_height = 36  # 每行的固定高度
        header_height = table.horizontalHeader().height()
        total_height = header_height + table.rowCount() * row_height + 2
        table.setFixedHeight(total_height)
        
        # 布局更新逻辑：表格 → 卡片 → 容器
        if table.parent():
            # 1. 调整表格所在的布局
            table_layout = table.parent()
            if table_layout:
                table_layout.update()
                
                # 2. 调整卡片大小
                card = table_layout.parent()
                if card:
                    card.update()
                    card.adjustSize()
                    
                    # 3. 找到卡片所在的容器（Tab页面的垂直布局）
                    container = card.parent()
                    if container:
                        # 确保容器布局正确更新
                        container.update()
                        container.adjustSize()
        
        # 清空输入
        start_port.clear()
        end_port.clear()
        vlan_input.clear()
    
    def add_trunk_port(self, interface_combo, start_port, end_port, vlan_input, table):
        """添加Trunk端口配置到表格"""
        interface = interface_combo.currentText()
        start = start_port.text()
        end = end_port.text()
        vlan = vlan_input.text()
        
        if not start or not end or not vlan:
            return
        
        # 添加到表格
        row = table.rowCount()
        table.insertRow(row)
        
        # 接口
        table.setItem(row, 0, QTableWidgetItem(interface))
        # 开始端口
        table.setItem(row, 1, QTableWidgetItem(start))
        # 结束端口
        table.setItem(row, 2, QTableWidgetItem(end))
        # 允许通行VLAN
        table.setItem(row, 3, QTableWidgetItem(vlan))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 12px;
            }
            QPushButton:hover {
                border: 1px solid #F5222D;
                color: #F5222D;
            }
        """)
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)
        
        # 计算表格的总高度并设置
        row_height = 36  # 每行的固定高度
        header_height = table.horizontalHeader().height()
        total_height = header_height + table.rowCount() * row_height + 2
        table.setFixedHeight(total_height)
        
        # 布局更新逻辑：表格 → 卡片 → 容器
        if table.parent():
            # 1. 调整表格所在的布局
            table_layout = table.parent()
            if table_layout:
                table_layout.update()
                
                # 2. 调整卡片大小
                card = table_layout.parent()
                if card:
                    card.update()
                    card.adjustSize()
                    
                    # 3. 找到卡片所在的容器（Tab页面的垂直布局）
                    container = card.parent()
                    if container:
                        # 确保容器布局正确更新
                        container.update()
                        container.adjustSize()
        
        # 清空输入
        start_port.clear()
        end_port.clear()
        vlan_input.clear()
    
    def add_agg_port(self, agg_id_input, agg_mode_combo, agg_lb_combo, agg_interface_combo, agg_start_port, agg_end_port, table):
        """添加链路聚合配置到表格"""
        agg_id = agg_id_input.text()
        agg_mode = agg_mode_combo.currentText()
        agg_lb = agg_lb_combo.currentText()
        interface = agg_interface_combo.currentText()
        start = agg_start_port.text()
        end = agg_end_port.text()
        
        if not agg_id or not start or not end:
            return
        
        # 构建成员端口字符串
        member_ports = f"{interface}{start} to {interface}{end}"
        
        # 添加到表格
        row = table.rowCount()
        table.insertRow(row)
        
        # 聚合ID
        table.setItem(row, 0, QTableWidgetItem(f"Bridge-Aggregation {agg_id}"))
        # 模式
        table.setItem(row, 1, QTableWidgetItem(agg_mode.split(' ')[0]))
        # 均衡方式
        table.setItem(row, 2, QTableWidgetItem(agg_lb))
        # 成员
        table.setItem(row, 3, QTableWidgetItem(member_ports))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                color: #4E5969;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)
        
        # 计算表格的总高度并设置
        row_height = 36  # 每行的固定高度
        header_height = table.horizontalHeader().height()
        total_height = header_height + table.rowCount() * row_height + 2
        table.setFixedHeight(total_height)
        
        # 布局更新逻辑：表格 → 卡片 → 容器
        if table.parent():
            # 1. 调整表格所在的布局
            table_layout = table.parent()
            if table_layout:
                table_layout.update()
                
                # 2. 调整卡片大小
                card = table_layout.parent()
                if card:
                    card.update()
                    card.adjustSize()
                    
                    # 3. 找到卡片所在的容器（Tab页面的垂直布局）
                    container = card.parent()
                    if container:
                        # 确保容器布局正确更新
                        container.update()
                        container.adjustSize()
        
        # 清空输入
        agg_id_input.clear()
        agg_start_port.clear()
        agg_end_port.clear()
    
    def reset_form(self):
        """重置表单（覆盖基类方法）"""
        self.reset_all_fields()
        self.code_editor.clear()
        
        # 重置链路聚合表格
        if hasattr(self, 'agg_table') and self.agg_table:
            self.agg_table.setRowCount(0)
        
        # 重置链路聚合输入控件
        if hasattr(self, 'agg_id_input'):
            self.agg_id_input.setText('1')
        if hasattr(self, 'agg_start_port'):
            self.agg_start_port.clear()
        if hasattr(self, 'agg_end_port'):
            self.agg_end_port.clear()