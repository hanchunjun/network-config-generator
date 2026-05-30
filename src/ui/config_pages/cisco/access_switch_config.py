from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QRadioButton, QButtonGroup, QAbstractItemView)
from PyQt5.QtCore import Qt
from src.ui.config_pages.base_config_page import BaseConfigPage
from src.core.theme_engine import ThemeEngine

class CiscoAccessSwitchConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'cisco', 'access_switch')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
        """初始化所有面板和卡片，使用Tab分组"""
        
        # 创建TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._get_tab_style())
        
        # Tab1：基础配置
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable特权密码', 'enable_password', is_password=True)
        
        # Console 串口登录配置卡片
        card_console = self.create_card('Console 串口登录配置', '🔐', '配置Console串口登录方式和密码')
        
        # 登录方法选择
        login_method_group = QButtonGroup()
        
        # 登录方法选择（标题和选项在同一排）
        login_method_row_layout = QHBoxLayout()
        login_method_row_layout.setSpacing(4)
        
        # 登录方法选择标题
        login_method_title = QLabel('登录方法选择')
        login_method_title.setStyleSheet(self._get_login_title_style())
        login_method_row_layout.addWidget(login_method_title)
        
        # 登录方法选择框架
        login_method_layout = QHBoxLayout()
        login_method_layout.setSpacing(4)
        
        # 仅配置登录密码
        pwd_only_radio = QRadioButton('仅配置登录密码')
        pwd_only_radio.setChecked(True)
        pwd_only_radio.setStyleSheet(self._get_radio_style())
        login_method_layout.addWidget(pwd_only_radio)
        login_method_group.addButton(pwd_only_radio, 0)
        
        # 配置用户名+密码
        user_pwd_radio = QRadioButton('配置用户名+密码')
        user_pwd_radio.setStyleSheet(self._get_radio_style())
        login_method_layout.addWidget(user_pwd_radio)
        login_method_group.addButton(user_pwd_radio, 1)
        
        login_method_row_layout.addLayout(login_method_layout)
        login_method_row_layout.addStretch()
        card_console.layout().addLayout(login_method_row_layout)
        
        # 方法一：密码
        console_method1_layout = QHBoxLayout()
        console_method1_layout.setSpacing(4)
        console_method1_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法一：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        console_method1_layout.addWidget(label)
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        console_method1_layout.addWidget(label)
        
        console_pwd_input = QLineEdit()
        console_pwd_input.setEchoMode(QLineEdit.Password)
        console_pwd_input.setFixedWidth(140)
        console_pwd_input.setPlaceholderText('请输入密码')
        console_pwd_input.setStyleSheet(self._get_input_alt_style())
        console_method1_layout.addWidget(console_pwd_input)
        self.form_fields['console_password'] = console_pwd_input
        
        # 添加拉伸，确保右侧对齐
        console_method1_layout.addStretch()
        card_console.layout().addLayout(console_method1_layout)
        
        # 方法二：用户名和密码（默认显示）
        self.console_method2_widget = QWidget()
        self.console_method2_widget.setStyleSheet('border: none;')
        console_method2_layout = QHBoxLayout(self.console_method2_widget)
        console_method2_layout.setSpacing(4)
        console_method2_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法二：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        console_method2_layout.addWidget(label)
        
        label = QLabel('用户名')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        console_method2_layout.addWidget(label)
        
        username_input = QLineEdit()
        username_input.setFixedWidth(140)
        username_input.setPlaceholderText('请输入用户名')
        username_input.setStyleSheet(self._get_input_alt2_style())
        console_method2_layout.addWidget(username_input)
        self.form_fields['console_username'] = username_input
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        console_method2_layout.addWidget(label)
        
        user_pwd_input = QLineEdit()
        user_pwd_input.setEchoMode(QLineEdit.Password)
        user_pwd_input.setFixedWidth(140)
        user_pwd_input.setPlaceholderText('请输入密码')
        user_pwd_input.setStyleSheet(self._get_input_alt2_style())
        console_method2_layout.addWidget(user_pwd_input)
        self.form_fields['console_user_password'] = user_pwd_input
        
        # 添加拉伸，确保右侧对齐
        console_method2_layout.addStretch()
        card_console.layout().addWidget(self.console_method2_widget)
        
        # 系统时间配置卡片
        card_time = self.create_card('系统时间配置', '🕒', '配置设备系统时间')
        self.add_form_item(card_time, '系统时间', 'system_time')
        
        card2 = self.create_card('VLAN基础配置', '🌐', '批量创建VLAN，支持连续范围如2 to 10')
        # 添加输入提示
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        label = QLabel('批量创建:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText('输入示例：2 to 8，11或2-8，11')
        input_widget.setStyleSheet(self._get_input_style())
        item_layout.addWidget(input_widget)
        self.form_fields['business_vlan'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('输入示例：2 to 8，11或2-8，11')
        hint_label.setStyleSheet(self._get_hint_label_style())
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card2.layout().addLayout(item_layout)
        
        card3 = self.create_card('管理地址与网关配置', '📍', '配置管理VLAN、IP地址、子网掩码和默认网关')
        
        # 管理VLAN ID
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        label = QLabel('管理VLAN ID:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(24)
        input_widget.setFixedWidth(130)
        input_widget.setPlaceholderText('请输入数字，如：100')
        input_widget.setStyleSheet(self._get_input_alt2_style())
        item_layout.addWidget(input_widget)
        self.form_fields['mgmt_vlan'] = input_widget
        
        item_layout.addStretch()
        card3.layout().addLayout(item_layout)
        
        # 管理IP和子网掩码在同一排
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        # 管理IP
        label = QLabel('管理IP:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(24)
        input_widget.setFixedWidth(130)
        input_widget.setPlaceholderText('请输入IP地址，如：192.168.1.1')
        input_widget.setStyleSheet(self._get_input_alt2_style())
        item_layout.addWidget(input_widget)
        self.form_fields['mgmt_ip'] = input_widget
        
        # 子网掩码
        label = QLabel('子网掩码:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(24)
        input_widget.setFixedWidth(130)
        input_widget.setPlaceholderText('请输入子网掩码，如：255.255.255.0')
        input_widget.setStyleSheet(self._get_input_alt2_style())
        item_layout.addWidget(input_widget)
        self.form_fields['subnet_mask'] = input_widget
        
        item_layout.addStretch()
        card3.layout().addLayout(item_layout)
        
        # 默认网关地址输入框
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        label = QLabel('默认网关地址:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setFixedHeight(24)
        input_widget.setFixedWidth(130)
        input_widget.setPlaceholderText('请输入IP地址，如：192.168.1.254')
        input_widget.setStyleSheet(self._get_input_alt2_style())
        item_layout.addWidget(input_widget)
        self.form_fields['gateway'] = input_widget
        
        item_layout.addStretch()
        card3.layout().addLayout(item_layout)
        
        # SSH登录配置卡片
        card_ssh = self.create_card('SSH登录配置', '🔐', '配置SSH登录方式和密码')
        
        # 登录方法选择
        ssh_login_method_group = QButtonGroup()
        
        # 登录方法选择（标题和选项在同一排）
        ssh_login_row_layout = QHBoxLayout()
        ssh_login_row_layout.setSpacing(4)
        
        # 登录方法选择标题
        ssh_login_method_title = QLabel('登录方法选择')
        ssh_login_method_title.setStyleSheet(self._get_login_title_style())
        ssh_login_row_layout.addWidget(ssh_login_method_title)
        
        # 登录方法选择框架
        ssh_login_layout = QHBoxLayout()
        ssh_login_layout.setSpacing(4)
        
        # 仅配置登录密码
        ssh_radio_password = QRadioButton('仅配置登录密码')
        ssh_radio_password.setChecked(True)
        ssh_radio_password.setStyleSheet(self._get_radio_style())
        ssh_login_layout.addWidget(ssh_radio_password)
        ssh_login_method_group.addButton(ssh_radio_password, 0)
        
        # 配置用户名+密码
        ssh_radio_user_pass = QRadioButton('配置用户名+密码')
        ssh_radio_user_pass.setStyleSheet(self._get_radio_style())
        ssh_login_layout.addWidget(ssh_radio_user_pass)
        ssh_login_method_group.addButton(ssh_radio_user_pass, 1)
        
        ssh_login_row_layout.addLayout(ssh_login_layout)
        ssh_login_row_layout.addStretch()
        card_ssh.layout().addLayout(ssh_login_row_layout)
        
        # 方法一：密码
        ssh_method1_layout = QHBoxLayout()
        ssh_method1_layout.setSpacing(4)
        ssh_method1_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法一：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        ssh_method1_layout.addWidget(label)
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        ssh_method1_layout.addWidget(label)
        
        ssh_pwd_input = QLineEdit()
        ssh_pwd_input.setEchoMode(QLineEdit.Password)
        ssh_pwd_input.setFixedWidth(140)
        ssh_pwd_input.setPlaceholderText('请输入密码')
        ssh_pwd_input.setStyleSheet(self._get_input_alt2_style())
        ssh_method1_layout.addWidget(ssh_pwd_input)
        self.form_fields['ssh_pwd'] = ssh_pwd_input
        
        # 添加拉伸，确保右侧对齐
        ssh_method1_layout.addStretch()
        card_ssh.layout().addLayout(ssh_method1_layout)
        
        # 方法二：用户名和密码（默认显示）
        self.ssh_method2_widget = QWidget()
        self.ssh_method2_widget.setStyleSheet('border: none;')
        ssh_method2_layout = QHBoxLayout(self.ssh_method2_widget)
        ssh_method2_layout.setSpacing(4)
        ssh_method2_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法二：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        ssh_method2_layout.addWidget(label)
        
        label = QLabel('用户名')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        ssh_method2_layout.addWidget(label)
        
        self.ssh_user_input = QLineEdit()
        self.ssh_user_input.setFixedWidth(140)
        self.ssh_user_input.setPlaceholderText('请输入用户名')
        self.ssh_user_input.setStyleSheet(self._get_input_alt2_style())
        ssh_method2_layout.addWidget(self.ssh_user_input)
        self.form_fields['ssh_user'] = self.ssh_user_input
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        ssh_method2_layout.addWidget(label)
        
        self.ssh_user_pass_input = QLineEdit()
        self.ssh_user_pass_input.setEchoMode(QLineEdit.Password)
        self.ssh_user_pass_input.setFixedWidth(140)
        self.ssh_user_pass_input.setPlaceholderText('请输入密码')
        self.ssh_user_pass_input.setStyleSheet(self._get_input_alt2_style())
        ssh_method2_layout.addWidget(self.ssh_user_pass_input)
        self.form_fields['ssh_user_password'] = self.ssh_user_pass_input
        
        # 添加拉伸，确保右侧对齐
        ssh_method2_layout.addStretch()
        card_ssh.layout().addWidget(self.ssh_method2_widget)
        
        # 连接信号
        ssh_radio_password.toggled.connect(self.toggle_ssh_user_pass)
        ssh_radio_user_pass.toggled.connect(lambda checked: self.toggle_ssh_user_pass(not checked))
        
        # Telnet登录配置卡片
        card_telnet = self.create_card('Telnet登录配置', '📡', '配置Telnet远程登录方式和密码')
        
        # 登录方法选择
        telnet_login_method_group = QButtonGroup()
        
        # 登录方法选择（标题和选项在同一排）
        telnet_login_row_layout = QHBoxLayout()
        telnet_login_row_layout.setSpacing(4)
        
        # 登录方法选择标题
        telnet_login_method_title = QLabel('登录方法选择')
        telnet_login_method_title.setStyleSheet(self._get_login_title_style())
        telnet_login_row_layout.addWidget(telnet_login_method_title)
        
        # 登录方法选择框架
        telnet_login_layout = QHBoxLayout()
        telnet_login_layout.setSpacing(4)
        
        # 仅配置登录密码
        telnet_radio_password = QRadioButton('仅配置登录密码')
        telnet_radio_password.setChecked(True)
        telnet_radio_password.setStyleSheet(self._get_radio_style())
        telnet_login_layout.addWidget(telnet_radio_password)
        telnet_login_method_group.addButton(telnet_radio_password, 0)
        
        # 配置用户名+密码
        telnet_radio_user_pass = QRadioButton('配置用户名+密码')
        telnet_radio_user_pass.setStyleSheet(self._get_radio_style())
        telnet_login_layout.addWidget(telnet_radio_user_pass)
        telnet_login_method_group.addButton(telnet_radio_user_pass, 1)
        
        telnet_login_row_layout.addLayout(telnet_login_layout)
        telnet_login_row_layout.addStretch()
        card_telnet.layout().addLayout(telnet_login_row_layout)
        
        # 方法一：密码
        telnet_method1_layout = QHBoxLayout()
        telnet_method1_layout.setSpacing(4)
        telnet_method1_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法一：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        telnet_method1_layout.addWidget(label)
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        telnet_method1_layout.addWidget(label)
        
        telnet_pwd_input = QLineEdit()
        telnet_pwd_input.setEchoMode(QLineEdit.Password)
        telnet_pwd_input.setFixedWidth(140)
        telnet_pwd_input.setPlaceholderText('请输入密码')
        telnet_pwd_input.setStyleSheet(self._get_input_alt2_style())
        telnet_method1_layout.addWidget(telnet_pwd_input)
        self.form_fields['telnet_pwd'] = telnet_pwd_input
        
        # 添加拉伸，确保右侧对齐
        telnet_method1_layout.addStretch()
        card_telnet.layout().addLayout(telnet_method1_layout)
        
        # 方法二：用户名和密码（默认显示）
        self.telnet_method2_widget = QWidget()
        self.telnet_method2_widget.setStyleSheet('border: none;')
        telnet_method2_layout = QHBoxLayout(self.telnet_method2_widget)
        telnet_method2_layout.setSpacing(4)
        telnet_method2_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('方法二：')
        label.setStyleSheet(self._get_method_label_style())
        label.setFixedWidth(110)
        telnet_method2_layout.addWidget(label)
        
        label = QLabel('用户名')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        telnet_method2_layout.addWidget(label)
        
        self.telnet_user_input = QLineEdit()
        self.telnet_user_input.setFixedWidth(140)
        self.telnet_user_input.setPlaceholderText('请输入用户名')
        self.telnet_user_input.setStyleSheet(self._get_input_alt2_style())
        telnet_method2_layout.addWidget(self.telnet_user_input)
        self.form_fields['telnet_user'] = self.telnet_user_input
        
        label = QLabel('密 码')
        label.setStyleSheet(self._get_method_field_label_style())
        label.setFixedWidth(110)
        telnet_method2_layout.addWidget(label)
        
        self.telnet_user_pass_input = QLineEdit()
        self.telnet_user_pass_input.setEchoMode(QLineEdit.Password)
        self.telnet_user_pass_input.setFixedWidth(140)
        self.telnet_user_pass_input.setPlaceholderText('请输入密码')
        self.telnet_user_pass_input.setStyleSheet(self._get_input_alt2_style())
        telnet_method2_layout.addWidget(self.telnet_user_pass_input)
        self.form_fields['telnet_user_password'] = self.telnet_user_pass_input
        
        # 添加拉伸，确保右侧对齐
        telnet_method2_layout.addStretch()
        card_telnet.layout().addWidget(self.telnet_method2_widget)
        
        # 连接信号
        telnet_radio_password.toggled.connect(self.toggle_telnet_user_pass)
        telnet_radio_user_pass.toggled.connect(lambda checked: self.toggle_telnet_user_pass(not checked))
        
        tab1.layout().addWidget(card1)  # 设备基础信息卡片
        tab1.layout().addWidget(card2)  # VLAN基础配置卡片
        tab1.layout().addWidget(card3)  # 管理地址与网关配置卡片
        tab1.layout().addWidget(card_time)    # 系统时间配置卡片
        tab1.content_layout.addStretch()
        self.tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：端口与上联配置
        tab2 = self.create_tab_content()
        card5 = self.create_card('下联Access端口配置', '🔌', '批量配置接入端口并划分到指定VLAN')
        
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(6)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet(self._get_label_secondary_style())
        interface_layout.addWidget(interface_label)
        self.access_interface_combo = QComboBox()
        self.access_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.access_interface_combo.setStyleSheet(self._get_combo_style())
        interface_layout.addWidget(self.access_interface_combo)
        config_layout.addLayout(interface_layout)
        
        port_layout = QVBoxLayout()
        port_layout.setSpacing(6)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(6)
        self.access_start_port = QLineEdit()
        self.access_start_port.setPlaceholderText('开始端口')
        self.access_start_port.setFixedWidth(100)
        self.access_start_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(self.access_start_port)
        port_range_layout.addWidget(QLabel('至'))
        self.access_end_port = QLineEdit()
        self.access_end_port.setPlaceholderText('结束端口')
        self.access_end_port.setFixedWidth(100)
        self.access_end_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(self.access_end_port)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(6)
        vlan_label = QLabel('加入VLAN:')
        vlan_label.setStyleSheet(self._get_label_secondary_style())
        vlan_layout.addWidget(vlan_label)
        self.access_vlan_input = QLineEdit()
        self.access_vlan_input.setPlaceholderText('请输入VLAN ID')
        self.access_vlan_input.setFixedWidth(140)
        self.access_vlan_input.setStyleSheet(self._get_input_style())
        vlan_layout.addWidget(self.access_vlan_input)
        config_layout.addLayout(vlan_layout)
        
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet(self._get_primary_button_style())
        
        self.access_table = QTableWidget()
        self.access_table.setColumnCount(5)
        self.access_table.setHorizontalHeaderLabels(['接口', '开始端口', '结束端口', '加入VLAN', '操作'])
        self.access_table.horizontalHeader().setStyleSheet(self._get_table_header_style())
        self.access_table.setStyleSheet(self._get_table_style())
        self.access_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.access_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.access_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.access_table.verticalHeader().setDefaultSectionSize(28)
        self.access_table.setRowCount(0)
        self.access_table.setFixedWidth(780)
        self.access_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_access_port(self.access_interface_combo, self.access_start_port, self.access_end_port, self.access_vlan_input, self.access_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card5.layout().addLayout(config_layout)
        card5.layout().addWidget(self.access_table)
        
        card6 = self.create_card('上联Trunk端口配置', '🌐', '配置上联端口为Trunk模式，调整速率、双工和光电复用')
        
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(6)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet(self._get_label_secondary_style())
        interface_layout.addWidget(interface_label)
        self.trunk_interface_combo = QComboBox()
        self.trunk_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.trunk_interface_combo.setStyleSheet(self._get_combo_style())
        interface_layout.addWidget(self.trunk_interface_combo)
        config_layout.addLayout(interface_layout)
        
        port_layout = QVBoxLayout()
        port_layout.setSpacing(6)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(6)
        self.trunk_start_port = QLineEdit()
        self.trunk_start_port.setPlaceholderText('开始端口')
        self.trunk_start_port.setFixedWidth(100)
        self.trunk_start_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(self.trunk_start_port)
        port_range_layout.addWidget(QLabel('至'))
        self.trunk_end_port = QLineEdit()
        self.trunk_end_port.setPlaceholderText('结束端口')
        self.trunk_end_port.setFixedWidth(100)
        self.trunk_end_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(self.trunk_end_port)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(6)
        vlan_label = QLabel('允许通行:')
        vlan_label.setStyleSheet(self._get_label_secondary_style())
        vlan_layout.addWidget(vlan_label)
        self.trunk_vlan_input = QLineEdit()
        self.trunk_vlan_input.setPlaceholderText('all 或 10-20')
        self.trunk_vlan_input.setFixedWidth(140)
        self.trunk_vlan_input.setStyleSheet(self._get_input_style())
        vlan_layout.addWidget(self.trunk_vlan_input)
        config_layout.addLayout(vlan_layout)
        
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet(self._get_primary_button_style())
        
        self.trunk_table = QTableWidget()
        self.trunk_table.setColumnCount(5)
        self.trunk_table.setHorizontalHeaderLabels(['接口', '开始端口', '结束端口', '允许通行VLAN', '操作'])
        self.trunk_table.horizontalHeader().setStyleSheet(self._get_table_header_style())
        self.trunk_table.setStyleSheet(self._get_table_style())
        self.trunk_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.trunk_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.trunk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trunk_table.verticalHeader().setDefaultSectionSize(28)
        self.trunk_table.setRowCount(0)
        self.trunk_table.setFixedWidth(780)
        self.trunk_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_trunk_port(self.trunk_interface_combo, self.trunk_start_port, self.trunk_end_port, self.trunk_vlan_input, self.trunk_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card6.layout().addLayout(config_layout)
        card6.layout().addWidget(self.trunk_table)
        
        # 链路聚合配置卡片
        card7 = self.create_card('链路聚合 (Port-Channel)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
        # 配置区域
        config_layout = QHBoxLayout()
        config_layout.setSpacing(4)
        
        # 聚合ID
        agg_id_layout = QVBoxLayout()
        agg_id_layout.setSpacing(4)
        agg_id_label = QLabel('聚合ID:')
        agg_id_label.setStyleSheet(self._get_label_secondary_style())
        agg_id_layout.addWidget(agg_id_label)
        self.agg_id_input = QLineEdit()
        self.agg_id_input.setPlaceholderText('1')
        self.agg_id_input.setText('1')
        self.agg_id_input.setFixedWidth(80)
        self.agg_id_input.setStyleSheet(self._get_input_style())
        agg_id_layout.addWidget(self.agg_id_input)
        config_layout.addLayout(agg_id_layout)
        
        # 模式选择
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(4)
        mode_label = QLabel('模式:')
        mode_label.setStyleSheet(self._get_label_secondary_style())
        mode_layout.addWidget(mode_label)
        self.agg_mode_combo = QComboBox()
        self.agg_mode_combo.addItems(['LACP (动态)', 'Manual (静态)'])
        self.agg_mode_combo.setStyleSheet(self._get_combo_style())
        mode_layout.addWidget(self.agg_mode_combo)
        config_layout.addLayout(mode_layout)
        
        # 负载均衡
        lb_layout = QVBoxLayout()
        lb_layout.setSpacing(4)
        lb_label = QLabel('负载均衡:')
        lb_label.setStyleSheet(self._get_label_secondary_style())
        lb_layout.addWidget(lb_label)
        self.agg_lb_combo = QComboBox()
        self.agg_lb_combo.addItems(['src-dst-ip (推荐)', 'src-dst-mac', 'src-dst-port'])
        self.agg_lb_combo.setStyleSheet(self._get_combo_style())
        lb_layout.addWidget(self.agg_lb_combo)
        config_layout.addLayout(lb_layout)
        
        # 成员端口
        member_layout = QVBoxLayout()
        member_layout.setSpacing(4)
        member_label = QLabel('成员端口:')
        member_label.setStyleSheet(self._get_label_secondary_style())
        member_layout.addWidget(member_label)
        member_port_layout = QHBoxLayout()
        member_port_layout.setSpacing(4)
        self.agg_interface_combo = QComboBox()
        self.agg_interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        self.agg_interface_combo.setStyleSheet(self._get_combo_style())
        member_port_layout.addWidget(self.agg_interface_combo)
        self.agg_start_port = QLineEdit()
        self.agg_start_port.setPlaceholderText('开始')
        self.agg_start_port.setFixedWidth(60)
        self.agg_start_port.setStyleSheet(self._get_input_style())
        member_port_layout.addWidget(self.agg_start_port)
        member_port_layout.addWidget(QLabel('至'))
        self.agg_end_port = QLineEdit()
        self.agg_end_port.setPlaceholderText('结束')
        self.agg_end_port.setFixedWidth(60)
        self.agg_end_port.setStyleSheet(self._get_input_style())
        member_port_layout.addWidget(self.agg_end_port)
        member_layout.addLayout(member_port_layout)
        config_layout.addLayout(member_layout)
        
        # 创建聚合组按钮
        create_button = QPushButton('创建聚合组')
        create_button.setFixedSize(120, 40)
        create_button.setStyleSheet(self._get_primary_button_style())
        config_layout.addWidget(create_button)
        
        config_layout.addStretch()
        card7.layout().addLayout(config_layout)
        
        # 聚合组表格
        self.agg_table = QTableWidget()
        self.agg_table.setColumnCount(5)
        self.agg_table.setHorizontalHeaderLabels(['聚合ID', '模式', '均衡方式', '成员', '操作'])
        self.agg_table.horizontalHeader().setStyleSheet(self._get_table_header_style())
        self.agg_table.setStyleSheet(self._get_table_style())
        self.agg_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.agg_table.verticalHeader().setDefaultSectionSize(28)
        self.agg_table.setRowCount(0)
        self.agg_table.setMinimumWidth(600)
        self.agg_table.setFixedHeight(50)
        card7.layout().addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout().addWidget(card5)
        tab2.layout().addWidget(card6)
        tab2.layout().addWidget(card7)
        tab2.content_layout.addStretch()
        self.tab_widget.addTab(tab2.widget, '🔌 端口与上联')
        
        # Tab3：安全与防环配置
        tab3 = self.create_tab_content()
        card8 = self.create_card('DHCP Snooping功能', '📶', '开启DHCP监听，防止伪DHCP服务器，配置信任端口')
        
        # 信任端口范围
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(4)
        
        label = QLabel('信任端口范围:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        port_range_layout.addWidget(label)
        
        # 接口类型下拉框
        interface_combo = QComboBox()
        interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        interface_combo.setStyleSheet(self._get_combo_style())
        interface_combo.setFixedWidth(100)
        port_range_layout.addWidget(interface_combo)
        
        # 开始端口
        start_port = QLineEdit()
        start_port.setPlaceholderText('1')
        start_port.setFixedWidth(80)
        start_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(start_port)
        
        # 至
        port_range_layout.addWidget(QLabel('至'))
        
        # 结束端口
        end_port = QLineEdit()
        end_port.setPlaceholderText('2')
        end_port.setFixedWidth(80)
        end_port.setStyleSheet(self._get_input_style())
        port_range_layout.addWidget(end_port)
        
        # 保存到form_fields
        self.form_fields['dhcp_snooping_interface'] = interface_combo
        self.form_fields['dhcp_snooping_start_port'] = start_port
        self.form_fields['dhcp_snooping_end_port'] = end_port
        
        port_range_layout.addStretch()
        card8.layout().addLayout(port_range_layout)
        
        card9 = self.create_card('接口防环配置', '🛡️', '开启RLDP防环功能，配置环路检测端口')
        
        # 防环端口范围
        loop_port_layout = QHBoxLayout()
        loop_port_layout.setSpacing(4)
        
        label = QLabel('防环端口范围:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        loop_port_layout.addWidget(label)
        
        # 接口类型下拉框
        interface_combo = QComboBox()
        interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        interface_combo.setStyleSheet(self._get_combo_style())
        interface_combo.setFixedWidth(100)
        loop_port_layout.addWidget(interface_combo)
        
        # 开始端口
        start_port = QLineEdit()
        start_port.setPlaceholderText('1')
        start_port.setFixedWidth(80)
        start_port.setStyleSheet(self._get_input_style())
        loop_port_layout.addWidget(start_port)
        
        # 至
        loop_port_layout.addWidget(QLabel('至'))
        
        # 结束端口
        end_port = QLineEdit()
        end_port.setPlaceholderText('2')
        end_port.setFixedWidth(80)
        end_port.setStyleSheet(self._get_input_style())
        loop_port_layout.addWidget(end_port)
        
        # 保存到form_fields
        self.form_fields['loop_interface'] = interface_combo
        self.form_fields['loop_start_port'] = start_port
        self.form_fields['loop_end_port'] = end_port
        
        loop_port_layout.addStretch()
        card9.layout().addLayout(loop_port_layout)
        
        card10 = self.create_card('生成树配置 (STP/RSTP/MSTP)', '🌐', '配置MST多生成树实例，划分VLAN到不同实例')
        
        # STP模式和桥优先级（同一行）
        mode_prio_layout = QHBoxLayout()
        mode_prio_layout.setSpacing(4)
        
        # STP模式
        label = QLabel('STP模式:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        mode_prio_layout.addWidget(label)
        stp_mode_combo = QComboBox()
        stp_mode_combo.addItems(['RSTP', 'STP', 'MSTP'])
        stp_mode_combo.setCurrentText('RSTP')
        stp_mode_combo.setStyleSheet(self._get_combo_style())
        stp_mode_combo.setFixedWidth(100)
        mode_prio_layout.addWidget(stp_mode_combo)
        self.form_fields['stp_mode'] = stp_mode_combo
        
        # 桥优先级
        label = QLabel('桥优先级:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        mode_prio_layout.addWidget(label)
        bridge_prio_combo = QComboBox()
        bridge_prio_combo.addItems(['4096', '8192', '12288', '16384', '20480', '24576', '28672', '32768'])
        bridge_prio_combo.setCurrentText('32768')
        bridge_prio_combo.setStyleSheet(self._get_combo_style())
        bridge_prio_combo.setFixedWidth(100)
        mode_prio_layout.addWidget(bridge_prio_combo)
        self.form_fields['bridge_prio'] = bridge_prio_combo
        
        mode_prio_layout.addStretch()
        card10.layout().addLayout(mode_prio_layout)
        
        # BDPU保护
        bdpu_layout = QHBoxLayout()
        label = QLabel('开启BDPU保护:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        bdpu_layout.addWidget(label)
        bdpu_checkbox = QCheckBox()
        bdpu_checkbox.setStyleSheet(self._get_checkbox_style())
        bdpu_checkbox.setChecked(True)
        bdpu_layout.addWidget(bdpu_checkbox)
        self.form_fields['bdpu_protection'] = bdpu_checkbox
        bdpu_layout.addStretch()
        card10.layout().addLayout(bdpu_layout)
        
        # 应用端口
        port_layout = QHBoxLayout()
        port_layout.setSpacing(4)
        
        label = QLabel('应用端口:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(label)
        
        # 接口类型
        interface_combo = QComboBox()
        interface_combo.addItems(['G 0/', 'G 1/', 'Te 0/', 'Te 1/'])
        interface_combo.setStyleSheet(self._get_combo_style())
        interface_combo.setFixedWidth(100)
        port_layout.addWidget(interface_combo)
        self.form_fields['stp_interface'] = interface_combo
        
        # 开始端口
        start_port = QLineEdit()
        start_port.setPlaceholderText('1')
        start_port.setFixedWidth(80)
        start_port.setStyleSheet(self._get_input_style())
        port_layout.addWidget(start_port)
        self.form_fields['stp_start_port'] = start_port
        
        # 至
        port_layout.addWidget(QLabel('至'))
        
        # 结束端口
        end_port = QLineEdit()
        end_port.setPlaceholderText('2')
        end_port.setFixedWidth(80)
        end_port.setStyleSheet(self._get_input_style())
        port_layout.addWidget(end_port)
        self.form_fields['stp_end_port'] = end_port
        
        port_layout.addStretch()
        card10.layout().addLayout(port_layout)
        
        card11 = self.create_card('ACL访问控制列表', '📜', '配置访问控制列表，限制网络访问')
        acl_config_layout = QVBoxLayout()
        acl_config_layout.setSpacing(4)
        
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(4)
        
        label = QLabel('ACL类型:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row1_layout.addWidget(label)
        acl_type_combo = QComboBox()
        acl_type_combo.addItems(['标准ACL (1-99, 1300-1999)', '扩展ACL (100-199, 2000-2699)', '二层ACL (700-799)'])
        acl_type_combo.setCurrentText('标准ACL (1-99, 1300-1999)')
        acl_type_combo.setFixedWidth(300)
        acl_type_combo.setStyleSheet(self._get_combo_style())
        row1_layout.addWidget(acl_type_combo)
        
        label = QLabel('ACL编号:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row1_layout.addWidget(label)
        acl_number_input = QLineEdit()
        acl_number_input.setText('1')
        acl_number_input.setFixedWidth(100)
        acl_number_input.setStyleSheet(self._get_input_alt2_style())
        row1_layout.addWidget(acl_number_input)
        row1_layout.addStretch()
        acl_config_layout.addLayout(row1_layout)
        
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(4)
        
        label = QLabel('动作:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row2_layout.addWidget(label)
        action_combo = QComboBox()
        action_combo.addItems(['permit', 'deny'])
        action_combo.setFixedWidth(100)
        action_combo.setStyleSheet(self._get_combo_style())
        row2_layout.addWidget(action_combo)
        
        label = QLabel('协议:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row2_layout.addWidget(label)
        protocol_combo = QComboBox()
        protocol_combo.addItems(['ip', 'tcp', 'udp', 'icmp'])
        protocol_combo.setFixedWidth(100)
        protocol_combo.setStyleSheet(self._get_combo_style())
        row2_layout.addWidget(protocol_combo)
        row2_layout.addStretch()
        acl_config_layout.addLayout(row2_layout)
        
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(4)
        
        label = QLabel('源IP/段:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row3_layout.addWidget(label)
        src_ip_input = QLineEdit()
        src_ip_input.setText('any')
        src_ip_input.setFixedWidth(130)
        src_ip_input.setStyleSheet(self._get_input_alt2_style())
        row3_layout.addWidget(src_ip_input)
        
        label = QLabel('目标IP/段:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row3_layout.addWidget(label)
        dst_ip_input = QLineEdit()
        dst_ip_input.setText('any')
        dst_ip_input.setFixedWidth(130)
        dst_ip_input.setStyleSheet(self._get_input_alt2_style())
        row3_layout.addWidget(dst_ip_input)
        row3_layout.addStretch()
        acl_config_layout.addLayout(row3_layout)
        
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(4)
        
        label = QLabel('目标端口:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row4_layout.addWidget(label)
        dst_port_input = QLineEdit()
        dst_port_input.setPlaceholderText('如: 80')
        dst_port_input.setFixedWidth(100)
        dst_port_input.setStyleSheet(self._get_input_alt2_style())
        row4_layout.addWidget(dst_port_input)
        
        add_rule_button = QPushButton('添加规则')
        add_rule_button.setFixedWidth(110)
        add_rule_button.setFixedHeight(24)
        add_rule_button.setStyleSheet(self._get_primary_button_style())
        row4_layout.addWidget(add_rule_button)
        row4_layout.addStretch()
        acl_config_layout.addLayout(row4_layout)
        
        # ACL规则表格
        acl_table = QTableWidget()
        acl_table.setColumnCount(5)
        acl_table.setHorizontalHeaderLabels(['ACL编号', '规则/动作', '协议', '源/目标地址', '操作'])
        acl_table.horizontalHeader().setStretchLastSection(True)
        acl_table.horizontalHeader().setStyleSheet(self._get_table_header_style())
        acl_table.verticalHeader().setVisible(False)
        acl_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        acl_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        acl_table.setFixedHeight(200)
        acl_config_layout.addWidget(acl_table)
        
        # 应用到接口
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(4)
        
        label = QLabel('应用范围:')
        label.setFixedWidth(90)
        label.setStyleSheet(self._get_label_secondary_style())
        row5_layout.addWidget(label)
        interface_combo = QComboBox()
        interface_combo.addItems(['G 0/'])
        interface_combo.setFixedWidth(80)
        interface_combo.setStyleSheet(self._get_combo_style())
        row5_layout.addWidget(interface_combo)
        
        start_port = QLineEdit()
        start_port.setText('1')
        start_port.setFixedWidth(60)
        start_port.setStyleSheet(self._get_input_alt2_style())
        row5_layout.addWidget(start_port)
        
        row5_layout.addWidget(QLabel('至'))
        
        end_port = QLineEdit()
        end_port.setText('2')
        end_port.setFixedWidth(60)
        end_port.setStyleSheet(self._get_input_alt2_style())
        row5_layout.addWidget(end_port)
        
        label = QLabel('方向:')
        label.setFixedWidth(54)
        label.setStyleSheet(self._get_label_secondary_style())
        row5_layout.addWidget(label)
        direction_combo = QComboBox()
        direction_combo.addItems(['inbound', 'outbound'])
        direction_combo.setFixedWidth(100)
        direction_combo.setStyleSheet(self._get_combo_style())
        row5_layout.addWidget(direction_combo)
        
        apply_button = QPushButton('应用到接口')
        apply_button.setFixedWidth(110)
        apply_button.setFixedHeight(24)
        apply_button.setStyleSheet(self._get_primary_button_style())
        row5_layout.addWidget(apply_button)
        row5_layout.addStretch()
        acl_config_layout.addLayout(row5_layout)
        
        card11.layout().addLayout(acl_config_layout)
        
        # 存储ACL相关组件
        self.acl_type_combo = acl_type_combo
        self.acl_number_input = acl_number_input
        self.action_combo = action_combo
        self.protocol_combo = protocol_combo
        self.src_ip_input = src_ip_input
        self.dst_ip_input = dst_ip_input
        self.dst_port_input = dst_port_input
        self.acl_table = acl_table
        self.interface_combo = interface_combo
        self.start_port = start_port
        self.end_port = end_port
        self.direction_combo = direction_combo
        
        # 连接信号
        add_rule_button.clicked.connect(self.add_acl_rule)
        apply_button.clicked.connect(self.apply_acl_to_interface)
        
        tab3.layout().addWidget(card8)
        tab3.layout().addWidget(card9)
        tab3.layout().addWidget(card10)
        tab3.layout().addWidget(card11)
        tab3.content_layout.addStretch()
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
        
        tab4.layout().addWidget(card_console)  # Console 串口登录配置卡片
        tab4.layout().addWidget(card_ssh)      # SSH登录配置卡片
        tab4.layout().addWidget(card_telnet)   # Telnet登录配置卡片
        tab4.layout().addWidget(card12)
        tab4.layout().addWidget(card13)
        tab4.layout().addWidget(card14)
        tab4.layout().addWidget(card15)
        tab4.content_layout.addStretch()
        self.tab_widget.addTab(tab4.widget, '📊 运维与登录')
        
        # 将TabWidget添加到左侧布局
        self.config_layout.addWidget(self.tab_widget)
        # 初始加载时刷新子控件样式
        self._refresh_child_styles()

    def _refresh_child_styles(self) -> None:
        """刷新所有子控件的样式"""
        for child in self.findChildren(QLineEdit):
            child.setStyleSheet(self._get_input_style())
        for child in self.findChildren(QPushButton):
            text = child.text() or ''
            if text in ('返回上一级', '返回首页', '复制脚本', '导出配置', '重置'):
                child.setStyleSheet(self._get_secondary_button_style())
            else:
                child.setStyleSheet(self._get_primary_button_style())
        for child in self.findChildren(QComboBox):
            child.setStyleSheet(self._get_combo_style())


    def create_tab_content(self):
        """创建Tab页内容容器，带滚动区域"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self._get_scroll_area_style())
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setStyleSheet(self._get_container_style())
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop)
        container.setLayout(layout)
        
        scroll_area.setWidget(container)
        
        class TabContent:
            def __init__(self, scroll_area, layout):
                self.widget = scroll_area
                self.content_layout = layout

            def layout(self):
                return self.content_layout
        
        return TabContent(scroll_area, layout)
        
    def create_card(self, title, icon, description=''):
        """创建卡片，带功能描述"""
        card = QWidget()
        # 移除固定宽度，让卡片自适应窗口
        # card.setFixedWidth(800)
        card.setStyleSheet(self._get_card_style())
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        # 卡片标题与勾选框
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
        
        checkbox = QCheckBox()
        checkbox
        title_layout.addWidget(checkbox)
        
        title_label = QLabel(f'{icon} {title}')
        title_label.setStyleSheet(self._get_tab_content_title_style())
        title_layout.addWidget(title_label)
        
        # 功能描述（如果有）
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(self._get_tab_content_desc_style())
            title_layout.addWidget(desc_label)
        
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f'background-color: {self._theme_engine.current_theme["border"]};')
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        card.setLayout(layout)
        card.checkbox = checkbox
        card.title = title
        self.cards.append(card)
        return card
        
    def add_form_item(self, card, label_text, field_name, is_password=False, is_label=False, default_value=''):
        """添加表单项"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        if is_label:
            # 标签模式（不可编辑）
            value_label = QLabel(default_value)
            value_label.setStyleSheet(self._get_label_style())
            item_layout.addWidget(value_label)
        else:
            # 输入框模式
            input_field = QLineEdit()
            input_field.setFixedHeight(24)
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
                input_field.setPlaceholderText('请输入密码')
            else:
                # 根据字段名设置相应的提示信息
                if 'hostname' in field_name:
                    input_field.setPlaceholderText('请输入设备主机名')
                elif 'system_time' in field_name:
                    input_field.setPlaceholderText('格式：YYYY-MM-DD HH:MM:SS')
                elif 'ip' in field_name or 'IP' in label_text:
                    input_field.setPlaceholderText('请输入IP地址')
                elif 'mask' in field_name or '掩码' in label_text:
                    input_field.setPlaceholderText('请输入子网掩码')
                elif 'gateway' in field_name or '网关' in label_text:
                    input_field.setPlaceholderText('请输入默认网关')
                elif 'vlan' in field_name or 'VLAN' in label_text:
                    input_field.setPlaceholderText('请输入VLAN ID')
                elif 'interface' in field_name or '接口' in label_text:
                    input_field.setPlaceholderText('请输入接口名称')
                elif 'description' in field_name or '描述' in label_text:
                    input_field.setPlaceholderText('请输入描述信息')
                elif 'username' in field_name or '用户名' in label_text:
                    input_field.setPlaceholderText('请输入用户名')
                else:
                    input_field.setPlaceholderText(f'请输入{label_text}')
            input_field.setStyleSheet(self._get_input_alt2_style())
            if default_value:
                input_field.setText(default_value)
            item_layout.addWidget(input_field)
            self.form_fields[field_name] = input_field
        
        card.layout().addLayout(item_layout)
        
    def add_combo_item(self, card, label_text, field_name, options):
        """添加下拉选择框"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(4)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setFixedHeight(24)
        combo.setStyleSheet(self._get_combo_style())
        item_layout.addWidget(combo)
        self.form_fields[field_name] = combo
        
        card.layout().addLayout(item_layout)
        
    def generate_config(self):
        """生成配置脚本（覆盖基类方法）"""
        data = self.get_form_data()
        checked_cards = self.get_checked_cards()
        
        config = []
        config_commands = []
        
        if '设备基础信息' in checked_cards:
            if data.get('hostname'):
                config_commands.append(f"hostname {data.get('hostname')}")
            if data.get('enable_password'):
                config_commands.append(f"enable secret {data.get('enable_password')}")
            if data.get('system_time'):
                config_commands.append(f"clock set {data.get('system_time')}")
        
        if 'Console 串口登录配置' in checked_cards:
            if data.get('console_password'):
                config_commands.append(f"line console 0")
                config_commands.append(f"password {data.get('console_password')}")
                config_commands.append(f"login")
                config_commands.append(f"exit")
            elif data.get('console_username') and data.get('console_user_password'):
                config_commands.append(f"username {data.get('console_username')} privilege 15 secret {data.get('console_user_password')}")
                config_commands.append(f"line console 0")
                config_commands.append(f"login local")
                config_commands.append(f"exit")
        
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
                                    config_commands.append("exit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append("exit")
                    elif '-' in item:
                        parts = item.split('-')
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                for vlan_id in range(start, end + 1):
                                    config_commands.append(f"vlan {vlan_id}")
                                    config_commands.append("exit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append("exit")
                    else:
                        # 处理单个VLAN
                        config_commands.append(f"vlan {item}")
                        config_commands.append("exit")
        
        if '管理地址与网关配置' in checked_cards:
            if data.get('mgmt_vlan'):
                config_commands.append(f"vlan {data.get('mgmt_vlan')}")
                config_commands.append(f"name manage")
                config_commands.append(f"exit")
                if data.get('mgmt_ip'):
                    config_commands.append(f"interface vlan {data.get('mgmt_vlan')}")
                    subnet = data.get('subnet_mask', '255.255.255.0')
                    config_commands.append(f"ip address {data.get('mgmt_ip')} {subnet}")
                    config_commands.append(f"exit")
            if data.get('gateway'):
                config_commands.append(f"ip default-gateway {data.get('gateway')}")
        
        if 'SSH登录配置' in checked_cards:
            ssh_pwd = data.get('ssh_pwd')
            ssh_user = data.get('ssh_user')
            ssh_user_pwd = data.get('ssh_user_password')
            if ssh_pwd:
                config_commands.append(f"hostname {data.get('hostname', 'switch')}")
                config_commands.append(f"ip domain-name example.com")
                config_commands.append(f"crypto key generate rsa modulus 1024")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"password {ssh_pwd}")
                config_commands.append(f"login")
                config_commands.append(f"transport input ssh")
                config_commands.append(f"exit")
            if ssh_user and ssh_user_pwd:
                config_commands.append(f"hostname {data.get('hostname', 'switch')}")
                config_commands.append(f"ip domain-name example.com")
                config_commands.append(f"crypto key generate rsa modulus 1024")
                config_commands.append(f"username {ssh_user} privilege 15 secret {ssh_user_pwd}")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"login local")
                config_commands.append(f"transport input ssh")
                config_commands.append(f"exit")
        
        if 'Telnet登录配置' in checked_cards:
            telnet_pwd = data.get('telnet_pwd')
            telnet_user = data.get('telnet_user')
            telnet_user_pwd = data.get('telnet_user_password')
            if telnet_pwd:
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"password {telnet_pwd}")
                config_commands.append(f"login")
                config_commands.append(f"transport input telnet")
                config_commands.append(f"exit")
            if telnet_user and telnet_user_pwd:
                config_commands.append(f"username {telnet_user} privilege 15 secret {telnet_user_pwd}")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"login local")
                config_commands.append(f"transport input telnet")
                config_commands.append(f"exit")
        
        if '下联Access端口配置' in checked_cards:
            if self.access_table and self.access_table.rowCount() > 0:
                for row in range(self.access_table.rowCount()):
                    interface = self.access_table.item(row, 0).text()
                    start_port = self.access_table.item(row, 1).text()
                    end_port = self.access_table.item(row, 2).text()
                    vlan = self.access_table.item(row, 3).text()
                    
                    if interface and start_port and end_port and vlan:
                        if start_port == end_port:
                            config_commands.append(f"interface {interface}{start_port}")
                        else:
                            config_commands.append(f"interface range {interface}{start_port} - {end_port}")
                        config_commands.append(f"switchport mode access")
                        config_commands.append(f"switchport access vlan {vlan}")
                        config_commands.append(f"quit")
        
        if '上联Trunk端口配置' in checked_cards:
            if self.trunk_table and self.trunk_table.rowCount() > 0:
                for row in range(self.trunk_table.rowCount()):
                    interface = self.trunk_table.item(row, 0).text()
                    start_port = self.trunk_table.item(row, 1).text()
                    end_port = self.trunk_table.item(row, 2).text()
                    vlan = self.trunk_table.item(row, 3).text()
                    
                    if interface and start_port and end_port and vlan:
                        if start_port == end_port:
                            config_commands.append(f"interface {interface}{start_port}")
                        else:
                            config_commands.append(f"interface range {interface}{start_port} - {end_port}")
                        config_commands.append(f"switchport mode trunk")
                        config_commands.append(f"switchport trunk encapsulation dot1q")
                        if vlan == 'all':
                            config_commands.append(f"switchport trunk allowed vlan all")
                        else:
                            config_commands.append(f"switchport trunk allowed vlan {vlan}")
                        config_commands.append(f"quit")
        
        if '链路聚合 (Port-Channel)' in checked_cards:
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
                    config_commands.append(f"port-channel load-balance {lb_algorithm}")
                
                for row in range(self.agg_table.rowCount()):
                    # 获取聚合组信息
                    agg_id_item = self.agg_table.item(row, 0)
                    mode_item = self.agg_table.item(row, 1)
                    lb_item = self.agg_table.item(row, 2)
                    member_item = self.agg_table.item(row, 3)
                    
                    if agg_id_item and mode_item and lb_item and member_item:
                        agg_id = agg_id_item.text().split(' ')[-1]  # 提取聚合ID
                        mode = mode_item.text()
                        member = member_item.text()
                        
                        # 解析成员端口范围
                        # 格式：GigabitEthernet 1/0/1 to GigabitEthernet 1/0/4
                        import re
                        match = re.match(r'([A-Za-z\s]+)([\d/]+)\s+to\s+\1([\d/]+)', member)
                        if match:
                            interface_type = match.group(1).strip()
                            start = match.group(2)
                            end = match.group(3)
                            
                            # 构建端口范围字符串
                            port_range = f"{interface_type} {start} to {interface_type} {end}"
                            
                            # 配置聚合端口
                            config_commands.append(f"interface range {port_range}")
                            if mode == 'LACP':
                                config_commands.append(f"channel-protocol lacp")
                                config_commands.append(f"channel-group {agg_id} mode active")
                            else:
                                config_commands.append(f"channel-group {agg_id} mode on")
                            config_commands.append(f"no shutdown")
                            config_commands.append(f"exit")
                            
                            # 配置聚合端口接口
                            config_commands.append(f"interface Port-channel {agg_id}")
                            config_commands.append(f"switchport mode trunk")
                            config_commands.append(f"switchport trunk allowed vlan all")
                            config_commands.append(f"no shutdown")
                            config_commands.append(f"exit")
        
        if 'DHCP Snooping功能' in checked_cards:
            config_commands.append(f"ip dhcp snooping")
            if data.get('dhcp_snooping_interface') and data.get('dhcp_snooping_start_port') and data.get('dhcp_snooping_end_port'):
                interface = data.get('dhcp_snooping_interface').replace(' ', '')
                start_port = data.get('dhcp_snooping_start_port')
                end_port = data.get('dhcp_snooping_end_port')
                config_commands.append(f"interface range {interface}{start_port}-{end_port}")
                config_commands.append(f"ip dhcp snooping trust")
                config_commands.append(f"exit")
        
        if '接口防环配置' in checked_cards:
            config_commands.append("udld enable")
            config_commands.append("errdisable recovery cause udld")
            config_commands.append("errdisable recovery interval 120")
            if data.get('loop_interface') and data.get('loop_start_port') and data.get('loop_end_port'):
                interface = data.get('loop_interface').replace(' ', '')
                start_port = data.get('loop_start_port')
                end_port = data.get('loop_end_port')
                config_commands.append(f"interface range {interface}{start_port}-{end_port}")
                config_commands.append("spanning-tree bpdufilter enable")
                config_commands.append("udld aggressive")
                config_commands.append("exit")
        
        if '生成树配置 (STP/RSTP/MSTP)' in checked_cards:
            # STP模式
            stp_mode = data.get('stp_mode', 'RSTP')
            if stp_mode == 'STP':
                config_commands.append(f"spanning-tree mode pvst")
            elif stp_mode == 'RSTP':
                config_commands.append(f"spanning-tree mode rapid-pvst")
            elif stp_mode == 'MSTP':
                config_commands.append(f"spanning-tree mode mst")
                config_commands.append(f"spanning-tree mst configuration")
                config_commands.append(f"exit")
            
            # 桥优先级
            if data.get('bridge_prio'):
                if stp_mode == 'MSTP':
                    config_commands.append(f"spanning-tree mst 0 priority {data.get('bridge_prio')}")
                else:
                    config_commands.append(f"spanning-tree vlan 1 priority {data.get('bridge_prio')}")
            
            # BDPU保护
            if data.get('bdpu_protection') and data.get('bdpu_protection') is True:
                config_commands.append(f"spanning-tree portfast bpduguard default")
            
            # 边缘端口配置
            if data.get('stp_interface') and data.get('stp_start_port') and data.get('stp_end_port'):
                interface = data.get('stp_interface').replace(' ', '')
                start_port = data.get('stp_start_port')
                end_port = data.get('stp_end_port')
                config_commands.append(f"interface range {interface}{start_port}-{end_port}")
                config_commands.append(f"spanning-tree portfast")
                config_commands.append(f"exit")
        
        if 'ACL访问控制列表' in checked_cards:
            if hasattr(self, 'acl_table') and self.acl_table.rowCount() > 0:
                acl_rules = {}
                for row in range(self.acl_table.rowCount()):
                    acl_number_item = self.acl_table.item(row, 0)
                    action_item = self.acl_table.item(row, 1)
                    protocol_item = self.acl_table.item(row, 2)
                    addr_item = self.acl_table.item(row, 3)
                    
                    if acl_number_item and action_item and protocol_item and addr_item:
                        acl_number = acl_number_item.text()
                        action = action_item.text()
                        protocol = protocol_item.text()
                        addr_desc = addr_item.text()
                        
                        src_dst = addr_desc.split(' → ')
                        src_ip = src_dst[0].strip() if len(src_dst) > 0 else 'any'
                        dst_ip = src_dst[1].strip() if len(src_dst) > 1 else 'any'
                        
                        dst_port = ''
                        if ':' in dst_ip:
                            parts = dst_ip.split(':')
                            dst_ip = parts[0]
                            dst_port = parts[1]
                        
                        if acl_number not in acl_rules:
                            acl_rules[acl_number] = []
                        
                        # 构建ACL规则命令
                        if protocol == 'ip':
                            if src_ip == 'any' and dst_ip == 'any':
                                rule_cmd = f"access-list {acl_number} {action} {protocol}"
                            elif src_ip == 'any':
                                rule_cmd = f"access-list {acl_number} {action} {protocol} any {dst_ip}"
                            elif dst_ip == 'any':
                                rule_cmd = f"access-list {acl_number} {action} {protocol} {src_ip} any"
                            else:
                                rule_cmd = f"access-list {acl_number} {action} {protocol} {src_ip} {dst_ip}"
                        else:
                            if src_ip == 'any' and dst_ip == 'any' and not dst_port:
                                rule_cmd = f"access-list {acl_number} {action} {protocol}"
                            elif src_ip == 'any' and not dst_port:
                                rule_cmd = f"access-list {acl_number} {action} {protocol} any {dst_ip}"
                            elif src_ip == 'any' and dst_port:
                                rule_cmd = f"access-list {acl_number} {action} {protocol} any {dst_ip} eq {dst_port}"
                            elif not dst_port:
                                rule_cmd = f"access-list {acl_number} {action} {protocol} {src_ip} {dst_ip}"
                            else:
                                rule_cmd = f"access-list {acl_number} {action} {protocol} {src_ip} {dst_ip} eq {dst_port}"
                        
                        acl_rules[acl_number].append(rule_cmd)
                
                # 生成ACL配置命令
                for acl_number, rules in acl_rules.items():
                    config_commands.extend(rules)
                
                # 应用ACL到接口
                if hasattr(self, 'interface_combo') and hasattr(self, 'start_port') and hasattr(self, 'end_port') and hasattr(self, 'direction_combo'):
                    interface = self.interface_combo.currentText()
                    start = self.start_port.text()
                    end = self.end_port.text()
                    direction = self.direction_combo.currentText()
                    
                    if interface and start and end:
                        if start == end:
                            config_commands.append(f"interface {interface}{start}")
                        else:
                            config_commands.append(f"interface range {interface}{start} - {end}")
                        
                        # 应用每个ACL到接口
                        for acl_number in acl_rules.keys():
                            config_commands.append(f"ip access-group {acl_number} {direction}")
                        config_commands.append("exit")
        
        if 'NTP时钟同步' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp server {data.get('ntp_server')}")
        
        if 'SNMPv2配置' in checked_cards:
            config_commands.append(f"snmp-server community {data.get('snmp_community', 'public')} RO")
            if data.get('trap_server'):
                config_commands.append(f"snmp-server host {data.get('trap_server')} {data.get('snmp_community', 'public')}")
        
        if '端口镜像配置' in checked_cards:
            if data.get('mirror_src') and data.get('mirror_dst'):
                config_commands.append(f"monitor session 1 source interface {data.get('mirror_src')}")
                config_commands.append(f"monitor session 1 destination interface {data.get('mirror_dst')}")
        
        if 'AAA本地认证配置' in checked_cards:
            if data.get('aaa_user') and data.get('aaa_pwd'):
                config_commands.append(f"username {data.get('aaa_user')} privilege 15 secret {data.get('aaa_pwd')}")
        
        # 生成最终单段配置
        self.preview_text.clear()
        if config_commands:
            config.append("enable")
            config.append("configure terminal")
            config.extend(config_commands)
            config.append("end")
        config.append("write memory")

        self.preview_text.setPlainText('\n'.join(config))
    
    def toggle_ssh_user_pass(self, checked):
        """切换SSH登录方式"""
        self.ssh_method2_widget.show()
    
    def toggle_telnet_user_pass(self, checked):
        """切换Telnet登录方式"""
        self.telnet_method2_widget.show()
    
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
    
    def add_access_port(self, interface_combo, start_port, end_port, vlan_input, table):
        """添加Access端口配置到表格"""
        interface = interface_combo.currentText()
        start = start_port.text()
        end = end_port.text()
        vlan = vlan_input.text()
        
        if not start or not end or not vlan:
            return
        
        row = table.rowCount()
        table.insertRow(row)
        
        table.setItem(row, 0, QTableWidgetItem(interface))
        table.setItem(row, 1, QTableWidgetItem(start))
        table.setItem(row, 2, QTableWidgetItem(end))
        table.setItem(row, 3, QTableWidgetItem(vlan))
        
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet(self._get_danger_button_style())
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)

        row_height = 32
        header_height = table.horizontalHeader().height()
        total_height = header_height + table.rowCount() * row_height + 2
        table.setFixedHeight(total_height)

        if table.parent():
            table_layout = table.parent()
            if table_layout:
                table_layout.update()
                
                card = table_layout.parent()
                if card:
                    card.update()
                    card.adjustSize()
                    
                    container = card.parent()
                    if container:
                        container.update()
                        container.adjustSize()
        
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
        
        row = table.rowCount()
        table.insertRow(row)
        
        table.setItem(row, 0, QTableWidgetItem(interface))
        table.setItem(row, 1, QTableWidgetItem(start))
        table.setItem(row, 2, QTableWidgetItem(end))
        table.setItem(row, 3, QTableWidgetItem(vlan))
        
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet(self._get_danger_button_style())
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)

        row_height = 32
        header_height = table.horizontalHeader().height()
        total_height = header_height + table.rowCount() * row_height + 2
        table.setFixedHeight(total_height)

        if table.parent():
            table_layout = table.parent()
            if table_layout:
                table_layout.update()
                
                card = table_layout.parent()
                if card:
                    card.update()
                    card.adjustSize()
                    
                    container = card.parent()
                    if container:
                        container.update()
                        container.adjustSize()
        
        start_port.clear()
        end_port.clear()
        vlan_input.clear()
    
    def copy_script(self):
        """复制脚本到剪贴板（覆盖基类方法）"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_text.toPlainText())
    
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
                f.write(self.preview_text.toPlainText())
    
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
        table.setItem(row, 0, QTableWidgetItem(f"Port-Channel {agg_id}"))
        # 模式
        table.setItem(row, 1, QTableWidgetItem(agg_mode.split(' ')[0]))
        # 均衡方式
        table.setItem(row, 2, QTableWidgetItem(agg_lb))
        # 成员
        table.setItem(row, 3, QTableWidgetItem(member_ports))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet(self._get_small_delete_btn_style())
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)

        # 计算表格的总高度并设置
        row_height = 32  # 每行的固定高度
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
    
    def add_acl_rule(self):
        """添加ACL规则到表格"""
        acl_number = self.acl_number_input.text()
        action = self.action_combo.currentText()
        protocol = self.protocol_combo.currentText()
        src_ip = self.src_ip_input.text()
        dst_ip = self.dst_ip_input.text()
        dst_port = self.dst_port_input.text()
        
        if not acl_number:
            return
        
        # 构建地址描述
        addr_desc = f"{src_ip} → {dst_ip}"
        if dst_port:
            addr_desc += f":{dst_port}"
        
        # 添加到表格
        row = self.acl_table.rowCount()
        self.acl_table.insertRow(row)
        
        self.acl_table.setItem(row, 0, QTableWidgetItem(acl_number))
        self.acl_table.setItem(row, 1, QTableWidgetItem(action))
        self.acl_table.setItem(row, 2, QTableWidgetItem(protocol))
        self.acl_table.setItem(row, 3, QTableWidgetItem(addr_desc))
        
        # 添加删除按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(60, 24)
        delete_button.setStyleSheet(self._get_danger_button_style())
        delete_button.clicked.connect(lambda _, r=row: self.remove_acl_rule(r))
        self.acl_table.setCellWidget(row, 4, delete_button)
        
        # 调整表格高度
        row_height = 32
        header_height = self.acl_table.horizontalHeader().height()
        total_height = header_height + self.acl_table.rowCount() * row_height + 2
        self.acl_table.setFixedHeight(total_height)
    
    def remove_acl_rule(self, row):
        """从表格中移除ACL规则"""
        self.acl_table.removeRow(row)
        
        # 调整表格高度
        row_height = 32
        header_height = self.acl_table.horizontalHeader().height()
        total_height = header_height + self.acl_table.rowCount() * row_height + 2
        self.acl_table.setFixedHeight(total_height)
    
    def apply_acl_to_interface(self):
        """应用ACL到接口"""
        interface = self.interface_combo.currentText()
        start_port = self.start_port.text()
        end_port = self.end_port.text()
        direction = self.direction_combo.currentText()
        
        if not interface or not start_port or not end_port:
            return
        
        # 这里可以添加应用逻辑，例如更新表格或生成配置
        pass
    
    def reset_form(self):
        """重置表单（覆盖基类方法）"""
        self.reset_all_fields()
        self.preview_text.clear()
        
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
        
        # 重置ACL表格
        if hasattr(self, 'acl_table') and self.acl_table:
            self.acl_table.setRowCount(0)
            self.acl_table.setFixedHeight(200)