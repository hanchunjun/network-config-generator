from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from src.ui.config_pages.base_config_page import BaseConfigPage
from src.core.theme_engine import ThemeEngine

class RuijieCoreSwitchConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'ruijie', 'core_switch')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
        """初始化所有面板和卡片，使用Tab分组"""
        
        # 创建TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._get_tab_style())
        
        # Tab1：基础管理配置
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码和系统时间')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable加密密码', 'enable_secret', is_password=True)
        self.add_form_item(card1, '系统时间', 'system_time')
        
        # Console 串口登录配置卡片
        card_console = self.create_card('Console 串口登录配置', '🔐', '配置Console串口登录方式和密码')
        
        # 登录方式选择
        login_mode_layout = QHBoxLayout()
        login_mode_layout.setSpacing(16)
        
        label = QLabel('登录方式:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        login_mode_layout.addWidget(label)
        
        # 仅配置密码登录
        pwd_only_radio = QRadioButton('仅配置密码登录')
        pwd_only_radio.setChecked(True)
        pwd_only_radio.setStyleSheet(self._get_radio_style())
        login_mode_layout.addWidget(pwd_only_radio)
        
        # 配置用户名+密码
        user_pwd_radio = QRadioButton('配置用户名+密码')
        user_pwd_radio.setStyleSheet(self._get_radio_style())
        login_mode_layout.addWidget(user_pwd_radio)
        
        login_mode_layout.addStretch()
        card_console.layout().addLayout(login_mode_layout)
        
        # console密码输入
        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(16)
        
        label = QLabel('console密码:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        pwd_layout.addWidget(label)
        
        console_pwd_input = QLineEdit()
        console_pwd_input.setEchoMode(QLineEdit.Password)
        console_pwd_input.setPlaceholderText('请输入密码')
        console_pwd_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['primary']};
            }
        """)
        pwd_layout.addWidget(console_pwd_input)
        self.form_fields['console_password'] = console_pwd_input
        
        pwd_layout.addStretch()
        card_console.layout().addLayout(pwd_layout)
        
        # 用户名和密码输入
        user_pwd_layout = QHBoxLayout()
        user_pwd_layout.setSpacing(16)
        
        label = QLabel('用户名:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        user_pwd_layout.addWidget(label)
        
        user_input = QLineEdit()
        user_input.setPlaceholderText('请输入用户名')
        user_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['primary']};
            }
        """)
        user_pwd_layout.addWidget(user_input)
        self.form_fields['console_username'] = user_input
        
        label = QLabel('密码:')
        label.setFixedWidth(80)
        label.setStyleSheet(self._get_label_secondary_style())
        user_pwd_layout.addWidget(label)
        
        user_pwd_input = QLineEdit()
        user_pwd_input.setEchoMode(QLineEdit.Password)
        user_pwd_input.setPlaceholderText('请输入密码')
        user_pwd_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['primary']};
            }
        """)
        user_pwd_layout.addWidget(user_pwd_input)
        self.form_fields['console_user_password'] = user_pwd_input
        
        user_pwd_layout.addStretch()
        card_console.layout().addLayout(user_pwd_layout)
        
        # 系统时间配置卡片
        card_time = self.create_card('系统时间配置', '🕒', '配置设备系统时间')
        self.add_form_item(card_time, '系统时间', 'system_time')
        
        # VLAN基础配置卡片
        card2 = self.create_card('VLAN基础配置', '🌐', '批量创建VLAN，支持连续范围如2 to 10')
        # 批量创建VLAN输入框
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('批量创建:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText('输入示例：2 to 8，11或2-8，11')
        input_widget.setStyleSheet(self._get_input_style())
        item_layout.addWidget(input_widget)
        self.form_fields['vlan_basic'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('批量创建vlan，用逗号隔开，连续的用to或者-，例如：2 to 8，11或2-8，11')
        hint_label.setStyleSheet(f"color: {self._theme_engine.current_theme['primary']}; font-size: 9pt;")
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card2.layout().addLayout(item_layout)
        
        card3 = self.create_card('管理VLAN配置', '🌐', '创建管理VLAN并配置管理IP地址')
        self.add_form_item(card3, '管理VLAN ID', 'mgmt_vlan')
        self.add_form_item(card3, '管理VLAN名称', 'mgmt_vlan_name')
        self.add_form_item(card3, '管理IP地址', 'mgmt_ip')
        self.add_form_item(card3, '子网掩码', 'mgmt_mask')
        
        # SSH登录配置卡片
        card_ssh = self.create_card('SSH登录配置', '🔐', '配置SSH登录方式和密码')
        
        # SSH登录方式选择
        ssh_login_layout = QHBoxLayout()
        ssh_login_label = QLabel('登录方式:')
        ssh_login_label.setStyleSheet(self._get_label_secondary_style())
        ssh_login_layout.addWidget(ssh_login_label)
        
        self.ssh_login_type = QButtonGroup()
        ssh_radio_password = QRadioButton('仅配置密码登录')
        ssh_radio_user_pass = QRadioButton('配置用户名+密码')
        ssh_radio_password.setChecked(True)
        
        self.ssh_login_type.addButton(ssh_radio_password, 1)
        self.ssh_login_type.addButton(ssh_radio_user_pass, 2)
        
        ssh_login_layout.addWidget(ssh_radio_password)
        ssh_login_layout.addWidget(ssh_radio_user_pass)
        ssh_login_layout.addStretch()
        card_ssh.layout().addLayout(ssh_login_layout)
        
        # SSH密码
        self.add_form_item(card_ssh, 'SSH密码', 'ssh_password', is_password=True)
        
        # SSH用户名和密码（仅当选择配置用户名+密码时显示）
        self.ssh_user_layout = QHBoxLayout()
        ssh_user_label = QLabel('用户名:')
        ssh_user_label.setStyleSheet(self._get_label_secondary_style())
        self.ssh_user_input = QLineEdit()
        self.ssh_user_input.setPlaceholderText('请输入SSH用户名')
        self.ssh_user_input.setStyleSheet(self.get_input_style())
        
        ssh_pass_label = QLabel('密码:')
        ssh_pass_label.setStyleSheet(self._get_label_secondary_style())
        self.ssh_user_pass_input = QLineEdit()
        self.ssh_user_pass_input.setPlaceholderText('请输入SSH密码')
        self.ssh_user_pass_input.setEchoMode(QLineEdit.Password)
        self.ssh_user_pass_input.setStyleSheet(self.get_input_style())
        
        self.ssh_user_layout.addWidget(ssh_user_label)
        self.ssh_user_layout.addWidget(self.ssh_user_input)
        self.ssh_user_layout.addWidget(ssh_pass_label)
        self.ssh_user_layout.addWidget(self.ssh_user_pass_input)
        card_ssh.layout().addLayout(self.ssh_user_layout)
        
        # 默认隐藏用户名密码输入
        self.ssh_user_input.hide()
        self.ssh_user_pass_input.hide()
        ssh_user_label.hide()
        ssh_pass_label.hide()
        
        # 连接信号
        ssh_radio_password.toggled.connect(lambda checked: self.toggle_ssh_user_pass(checked))
        ssh_radio_user_pass.toggled.connect(lambda checked: self.toggle_ssh_user_pass(not checked))
        
        # 将用户名和密码输入框添加到form_fields字典中
        self.form_fields['ssh_user'] = self.ssh_user_input
        self.form_fields['ssh_user_password'] = self.ssh_user_pass_input
        
        # Telnet登录配置卡片
        card_telnet = self.create_card('Telnet登录配置', '📡', '配置Telnet远程登录方式和密码')
        
        # Telnet登录方式选择
        telnet_login_layout = QHBoxLayout()
        telnet_login_label = QLabel('登录方式:')
        telnet_login_label.setStyleSheet(self._get_label_secondary_style())
        telnet_login_layout.addWidget(telnet_login_label)
        
        self.telnet_login_type = QButtonGroup()
        telnet_radio_password = QRadioButton('仅配置密码登录')
        telnet_radio_user_pass = QRadioButton('配置用户名+密码')
        telnet_radio_password.setChecked(True)
        
        self.telnet_login_type.addButton(telnet_radio_password, 1)
        self.telnet_login_type.addButton(telnet_radio_user_pass, 2)
        
        telnet_login_layout.addWidget(telnet_radio_password)
        telnet_login_layout.addWidget(telnet_radio_user_pass)
        telnet_login_layout.addStretch()
        card_telnet.layout().addLayout(telnet_login_layout)
        
        # Telnet密码
        self.add_form_item(card_telnet, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        # Telnet用户名和密码（仅当选择配置用户名+密码时显示）
        self.telnet_user_layout = QHBoxLayout()
        telnet_user_label = QLabel('用户名:')
        telnet_user_label.setStyleSheet(self._get_label_secondary_style())
        self.telnet_user_input = QLineEdit()
        self.telnet_user_input.setPlaceholderText('请输入Telnet用户名')
        self.telnet_user_input.setStyleSheet(self.get_input_style())
        
        telnet_pass_label = QLabel('密码:')
        telnet_pass_label.setStyleSheet(self._get_label_secondary_style())
        self.telnet_user_pass_input = QLineEdit()
        self.telnet_user_pass_input.setPlaceholderText('请输入Telnet密码')
        self.telnet_user_pass_input.setEchoMode(QLineEdit.Password)
        self.telnet_user_pass_input.setStyleSheet(self.get_input_style())
        
        self.telnet_user_layout.addWidget(telnet_user_label)
        self.telnet_user_layout.addWidget(self.telnet_user_input)
        self.telnet_user_layout.addWidget(telnet_pass_label)
        self.telnet_user_layout.addWidget(self.telnet_user_pass_input)
        card_telnet.layout().addLayout(self.telnet_user_layout)
        
        # 默认隐藏用户名密码输入
        self.telnet_user_input.hide()
        self.telnet_user_pass_input.hide()
        telnet_user_label.hide()
        telnet_pass_label.hide()
        
        # 连接信号
        telnet_radio_password.toggled.connect(lambda checked: self.toggle_telnet_user_pass(checked))
        telnet_radio_user_pass.toggled.connect(lambda checked: self.toggle_telnet_user_pass(not checked))
        
        # 将用户名和密码输入框添加到form_fields字典中
        self.form_fields['telnet_user'] = self.telnet_user_input
        self.form_fields['telnet_user_password'] = self.telnet_user_pass_input
        
        tab1.layout().addWidget(card1)
        tab1.layout().addWidget(card_console)  # Console 串口登录配置卡片
        tab1.layout().addWidget(card_time)    # 系统时间配置卡片
        tab1.layout().addWidget(card2)  # VLAN基础配置卡片
        tab1.layout().addWidget(card3)
        tab1.layout().addWidget(card_ssh)  # SSH登录配置卡片
        tab1.layout().addWidget(card_telnet)  # Telnet登录配置卡片
        tab1.content_layout.addStretch()
        self.tab_widget.addTab(tab1.widget, '⚙️ 基础管理')
        
        # Tab2：端口与上联配置
        tab2 = self.create_tab_content()
        
        card7 = self.create_card('下联Access端口配置', '🔌', '配置下联端口为Access模式')
        
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(12)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet(self._get_label_secondary_style())
        interface_layout.addWidget(interface_label)
        self.access_interface_combo = QComboBox()
        self.access_interface_combo.addItems(['GigabitEthernet 0/', 'GigabitEthernet 1/', 'TenGigabitEthernet 0/'])
        self.access_interface_combo.setStyleSheet(self._get_combo_style())
        interface_layout.addWidget(self.access_interface_combo)
        config_layout.addLayout(interface_layout)
        
        port_layout = QVBoxLayout()
        port_layout.setSpacing(12)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(12)
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
        vlan_layout.setSpacing(12)
        vlan_label = QLabel('加入VLAN:')
        vlan_label.setStyleSheet(self._get_label_secondary_style())
        vlan_layout.addWidget(vlan_label)
        self.access_vlan_input = QLineEdit()
        self.access_vlan_input.setPlaceholderText('请输入VLAN ID')
        self.access_vlan_input.setFixedWidth(140)
        self.access_vlan_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
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
        self.access_table.verticalHeader().setDefaultSectionSize(36)
        self.access_table.setRowCount(0)
        self.access_table.setFixedWidth(780)
        self.access_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_access_port(self.access_interface_combo, self.access_start_port, self.access_end_port, self.access_vlan_input, self.access_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card7.layout().addLayout(config_layout)
        card7.layout().addWidget(self.access_table)
        
        card5 = self.create_card('上联Trunk端口配置', '🔌', '配置上联端口为Trunk模式')
        
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(12)
        interface_label = QLabel('接口类型:')
        interface_label.setStyleSheet(self._get_label_secondary_style())
        interface_layout.addWidget(interface_label)
        self.trunk_interface_combo = QComboBox()
        self.trunk_interface_combo.addItems(['GigabitEthernet 0/', 'GigabitEthernet 1/', 'TenGigabitEthernet 0/'])
        self.trunk_interface_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        interface_layout.addWidget(self.trunk_interface_combo)
        config_layout.addLayout(interface_layout)
        
        port_layout = QVBoxLayout()
        port_layout.setSpacing(12)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(12)
        self.trunk_start_port = QLineEdit()
        self.trunk_start_port.setPlaceholderText('开始端口')
        self.trunk_start_port.setFixedWidth(100)
        self.trunk_start_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        port_range_layout.addWidget(self.trunk_start_port)
        port_range_layout.addWidget(QLabel('至'))
        self.trunk_end_port = QLineEdit()
        self.trunk_end_port.setPlaceholderText('结束端口')
        self.trunk_end_port.setFixedWidth(100)
        self.trunk_end_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        port_range_layout.addWidget(self.trunk_end_port)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(12)
        vlan_label = QLabel('允许通行:')
        vlan_label.setStyleSheet(self._get_label_secondary_style())
        vlan_layout.addWidget(vlan_label)
        self.trunk_vlan_input = QLineEdit()
        self.trunk_vlan_input.setPlaceholderText('all 或 10-20')
        self.trunk_vlan_input.setFixedWidth(140)
        self.trunk_vlan_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        vlan_layout.addWidget(self.trunk_vlan_input)
        config_layout.addLayout(vlan_layout)
        
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet(self._get_primary_button_style())
        
        self.trunk_table = QTableWidget()
        self.trunk_table.setColumnCount(5)
        self.trunk_table.setHorizontalHeaderLabels(['接口', '开始端口', '结束端口', '允许通行VLAN', '操作'])
        self.trunk_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: {t['hover_bg']};
                border: none;
                padding: 8px;
                font-size: 9pt;
                color: {t['text_secondary']};
            }
        """)
        self.trunk_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid {t['border']};
                border-radius: 4px;
                background-color: {t['card_bg']};
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 10pt;
            }
        """)
        self.trunk_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.trunk_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.trunk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trunk_table.verticalHeader().setDefaultSectionSize(36)
        self.trunk_table.setRowCount(0)
        self.trunk_table.setFixedWidth(780)
        self.trunk_table.setFixedHeight(50)
        
        add_button.clicked.connect(lambda: self.add_trunk_port(self.trunk_interface_combo, self.trunk_start_port, self.trunk_end_port, self.trunk_vlan_input, self.trunk_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card5.layout().addLayout(config_layout)
        card5.layout().addWidget(self.trunk_table)
        
        card6 = self.create_card('链路聚合 (AggregatePort)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
        # 配置区域
        config_layout = QHBoxLayout()
        config_layout.setSpacing(16)
        
        # 聚合ID
        agg_id_layout = QVBoxLayout()
        agg_id_layout.setSpacing(8)
        agg_id_label = QLabel('聚合ID:')
        agg_id_label.setStyleSheet(self._get_label_secondary_style())
        agg_id_layout.addWidget(agg_id_label)
        self.agg_id_input = QLineEdit()
        self.agg_id_input.setPlaceholderText('1')
        self.agg_id_input.setText('1')
        self.agg_id_input.setFixedWidth(80)
        self.agg_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        agg_id_layout.addWidget(self.agg_id_input)
        config_layout.addLayout(agg_id_layout)
        
        # 模式选择
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(8)
        mode_label = QLabel('模式:')
        mode_label.setStyleSheet(self._get_label_secondary_style())
        mode_layout.addWidget(mode_label)
        self.agg_mode_combo = QComboBox()
        self.agg_mode_combo.addItems(['LACP (动态)', 'Static (静态)'])
        self.agg_mode_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        mode_layout.addWidget(self.agg_mode_combo)
        config_layout.addLayout(mode_layout)
        
        # 负载均衡
        lb_layout = QVBoxLayout()
        lb_layout.setSpacing(8)
        lb_label = QLabel('负载均衡:')
        lb_label.setStyleSheet(self._get_label_secondary_style())
        lb_layout.addWidget(lb_label)
        self.agg_lb_combo = QComboBox()
        self.agg_lb_combo.addItems(['src-dst-ip (推荐)', 'src-dst-mac', 'src-dst-ip+port'])
        self.agg_lb_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        lb_layout.addWidget(self.agg_lb_combo)
        config_layout.addLayout(lb_layout)
        
        # 成员端口
        member_layout = QVBoxLayout()
        member_layout.setSpacing(8)
        member_label = QLabel('成员端口:')
        member_label.setStyleSheet(self._get_label_secondary_style())
        member_layout.addWidget(member_label)
        member_port_layout = QHBoxLayout()
        member_port_layout.setSpacing(8)
        self.agg_interface_combo = QComboBox()
        # 核心交换机以万兆口为主
        self.agg_interface_combo.addItems(['Te 0/', 'Te 1/', 'Te 2/', 'Te 3/', 'G 0/', 'G 1/'])
        self.agg_interface_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        member_port_layout.addWidget(self.agg_interface_combo)
        self.agg_start_port = QLineEdit()
        self.agg_start_port.setPlaceholderText('开始')
        self.agg_start_port.setFixedWidth(60)
        self.agg_start_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        member_port_layout.addWidget(self.agg_start_port)
        member_port_layout.addWidget(QLabel('至'))
        self.agg_end_port = QLineEdit()
        self.agg_end_port.setPlaceholderText('结束')
        self.agg_end_port.setFixedWidth(60)
        self.agg_end_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        member_port_layout.addWidget(self.agg_end_port)
        member_layout.addLayout(member_port_layout)
        config_layout.addLayout(member_layout)
        
        # 创建聚合组按钮
        create_button = QPushButton('创建聚合组')
        create_button.setFixedSize(120, 40)
        create_button.setStyleSheet(self._get_primary_button_style())
        config_layout.addWidget(create_button)
        
        config_layout.addStretch()
        card6.layout().addLayout(config_layout)
        
        # 聚合组表格
        self.agg_table = QTableWidget()
        self.agg_table.setColumnCount(5)
        self.agg_table.setHorizontalHeaderLabels(['聚合ID', '模式', '均衡方式', '成员', '操作'])
        self.agg_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: {t['hover_bg']};
                border: none;
                padding: 8px;
                font-size: 9pt;
                color: {t['text_secondary']};
            }
        """)
        self.agg_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid {t['border']};
                border-radius: 4px;
                background-color: {t['card_bg']};
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 10pt;
            }
        """)
        self.agg_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.agg_table.verticalHeader().setDefaultSectionSize(36)
        self.agg_table.setRowCount(0)
        self.agg_table.setMinimumWidth(600)
        self.agg_table.setFixedHeight(50)
        card6.layout().addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout().addWidget(card7)
        tab2.layout().addWidget(card5)
        tab2.layout().addWidget(card6)
        tab2.content_layout.addStretch()
        self.tab_widget.addTab(tab2.widget, '🔌 端口与上联')
        
        # Tab3：三层网关与路由配置
        tab3 = self.create_tab_content()
        card8 = self.create_card('业务VLANIF三层网关配置', '🌐', '配置用户网段和服务器网段的三层网关')
        self.add_form_item(card8, '用户网关IP地址', 'user_gw')
        self.add_form_item(card8, '用户网段子网掩码', 'user_mask')
        self.add_form_item(card8, '服务器网关IP地址', 'server_gw')
        self.add_form_item(card8, '服务器网段子网掩码', 'server_mask')
        
        card9 = self.create_card('静态路由配置', '🛣️', '配置静态路由条目')
        self.add_form_item(card9, '目的网段1', 'dst_net1')
        self.add_form_item(card9, '子网掩码1', 'dst_mask1')
        self.add_form_item(card9, '下一跳1', 'nh1')
        self.add_form_item(card9, '目的网段2', 'dst_net2')
        self.add_form_item(card9, '子网掩码2', 'dst_mask2')
        self.add_form_item(card9, '下一跳2', 'nh2')
        self.add_form_item(card9, '目的网段3', 'dst_net3')
        self.add_form_item(card9, '子网掩码3', 'dst_mask3')
        self.add_form_item(card9, '下一跳3', 'nh3')
        
        card10 = self.create_card('OSPF动态路由配置', '🔄', '配置OSPF动态路由协议')
        self.add_form_item(card10, 'OSPF进程号', 'ospf_proc')
        self.add_form_item(card10, 'OSPF路由器ID', 'ospf_rid')
        self.add_form_item(card10, '管理网段', 'mgmt_net')
        self.add_form_item(card10, '管理网段反掩码', 'mgmt_wild')
        self.add_form_item(card10, '用户网段', 'user_net')
        self.add_form_item(card10, '用户网段反掩码', 'user_wild')
        self.add_form_item(card10, '服务器网段', 'server_net')
        self.add_form_item(card10, '服务器网段反掩码', 'server_wild')
        self.add_form_item(card10, 'OSPF区域号', 'area_id')
        
        tab3.layout().addWidget(card8)
        tab3.layout().addWidget(card9)
        tab3.layout().addWidget(card10)
        tab3.content_layout.addStretch()
        self.tab_widget.addTab(tab3.widget, '🌐 三层网关与路由')
        
        # Tab4：DHCP服务 & 安全防环配置
        tab4 = self.create_tab_content()
        card11 = self.create_card('DHCP Server全局配置', '📶', '开启DHCP服务并配置地址池')
        self.add_form_item(card11, '用户网段排除起始IP', 'user_ex_start')
        self.add_form_item(card11, '用户网段排除结束IP', 'user_ex_end')
        self.add_form_item(card11, '服务器网段排除起始IP', 'server_ex_start')
        self.add_form_item(card11, '服务器网段排除结束IP', 'server_ex_end')
        self.add_form_item(card11, '用户地址池名称', 'user_pool')
        self.add_form_item(card11, '用户网段', 'user_pool_net')
        self.add_form_item(card11, '用户网段子网掩码', 'user_pool_mask')
        self.add_form_item(card11, '用户网关', 'user_pool_gw')
        self.add_form_item(card11, '主DNS', 'dns1')
        self.add_form_item(card11, '备DNS', 'dns2')
        self.add_form_item(card11, '服务器地址池名称', 'server_pool')
        self.add_form_item(card11, '服务器网段', 'server_pool_net')
        self.add_form_item(card11, '服务器网段子网掩码', 'server_pool_mask')
        self.add_form_item(card11, '服务器网关', 'server_pool_gw')
        
        card12 = self.create_card('DHCP Snooping安全配置', '🛡️', '开启DHCP监听防止伪DHCP服务器')
        self.add_form_item(card12, '信任上联端口', 'trust_port')
        self.add_form_item(card12, '监听VLAN列表', 'snooping_vlan')
        
        card13 = self.create_card('MSTP生成树防环配置', '🔄', '配置MSTP多生成树防止环路')
        self.add_form_item(card13, 'MST域名', 'mst_name')
        self.add_form_item(card13, '修订号', 'revision')
        self.add_form_item(card13, '实例1 VLAN列表', 'ins1_vlan')
        self.add_form_item(card13, '实例2 VLAN列表', 'ins2_vlan')
        self.add_form_item(card13, '生成树优先级', 'mst_prio')
        
        card14 = self.create_card('ACL访问控制配置', '📜', '配置访问控制列表限制访问权限')
        self.add_form_item(card14, '允许管理IP网段', 'manage_net')
        self.add_form_item(card14, '允许管理网段反掩码', 'manage_wild')
        self.add_form_item(card14, '用户网段', 'user_acl_net')
        self.add_form_item(card14, '用户网段反掩码', 'user_acl_wild')
        self.add_form_item(card14, '服务器网段', 'server_acl_net')
        self.add_form_item(card14, '服务器网段反掩码', 'server_acl_wild')
        
        tab4.layout().addWidget(card11)
        tab4.layout().addWidget(card12)
        tab4.layout().addWidget(card13)
        tab4.layout().addWidget(card14)
        tab4.content_layout.addStretch()
        self.tab_widget.addTab(tab4.widget, '🔒 DHCP & 安全防环')
        
        # Tab5：运维监控配置
        tab5 = self.create_tab_content()
        card15 = self.create_card('NTP时钟同步配置', '⏰', '配置NTP服务器自动同步设备时钟')
        self.add_form_item(card15, 'NTP服务器IP地址', 'ntp_server')
        
        card16 = self.create_card('SNMPv2c配置', '📈', '开启SNMP功能配置团体名和Trap告警')
        self.add_form_item(card16, 'SNMP只读团体名', 'snmp_ro_community')
        self.add_form_item(card16, 'Trap服务器IP', 'trap_server')
        self.add_form_item(card16, 'Trap团体名', 'trap_community')
        
        card17 = self.create_card('端口镜像配置', '📋', '配置端口镜像将流量复制到监控端口')
        self.add_form_item(card17, '镜像源端口', 'mirror_src')
        self.add_form_item(card17, '镜像目的端口', 'mirror_dst')
        
        tab5.layout().addWidget(card15)
        tab5.layout().addWidget(card16)
        tab5.layout().addWidget(card17)
        tab5.content_layout.addStretch()
        self.tab_widget.addTab(tab5.widget, '📊 运维监控')
        
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 卡片标题与勾选框
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        checkbox = QCheckBox()
        checkbox.setStyleSheet('QCheckBox::indicator { width: 18px; height: 18px; }')
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
        
        # 移除固定宽度，让卡片自适应窗口
        # card.setFixedWidth(800)
        card.setLayout(layout)
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
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        if is_label:
            value_label = QLabel(default_value)
            value_label.setStyleSheet(self._get_label_secondary_style())
            item_layout.addWidget(value_label)
        else:
            input_widget = QLineEdit()
            if is_password:
                input_widget.setEchoMode(QLineEdit.Password)
                input_widget.setPlaceholderText('请输入密码')
            else:
                # 根据字段名设置相应的提示信息
                if 'hostname' in field_name:
                    input_widget.setPlaceholderText('请输入设备主机名')
                elif 'system_time' in field_name:
                    input_widget.setPlaceholderText('格式：YYYY-MM-DD HH:MM:SS')
                elif 'ip' in field_name or 'IP' in label_text:
                    input_widget.setPlaceholderText('请输入IP地址')
                elif 'mask' in field_name or '掩码' in label_text:
                    input_widget.setPlaceholderText('请输入子网掩码')
                elif 'gateway' in field_name or '网关' in label_text:
                    input_widget.setPlaceholderText('请输入默认网关')
                elif 'vlan' in field_name or 'VLAN' in label_text:
                    input_widget.setPlaceholderText('请输入VLAN ID')
                elif 'interface' in field_name or '接口' in label_text:
                    input_widget.setPlaceholderText('请输入接口名称')
                elif 'description' in field_name or '描述' in label_text:
                    input_widget.setPlaceholderText('请输入描述信息')
                elif 'username' in field_name or '用户名' in label_text:
                    input_widget.setPlaceholderText('请输入用户名')
                else:
                    input_widget.setPlaceholderText(f'请输入{label_text}')
            input_widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid {t['input_border']};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 10pt;
                    background-color: {t['card_bg']};
                }
                QLineEdit:focus {
                    border: 1px solid {t['primary']};
                }
            """)
            item_layout.addWidget(input_widget)
            self.form_fields[field_name] = input_widget
        
        item_layout.addStretch()
        card.layout().addLayout(item_layout)
        
    def add_combo_item(self, card, label_text, field_name, options):
        """添加下拉选择项"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
                min-width: 200px;
            }
            QComboBox:focus {
                border: 1px solid {t['primary']};
            }
        """)
        item_layout.addWidget(combo)
        self.form_fields[field_name] = combo
        
        item_layout.addStretch()
        card.layout().addLayout(item_layout)
        
    def toggle_ssh_user_pass(self, checked):
        """切换SSH登录方式"""
        for widget in self.ssh_user_layout.children():
            if isinstance(widget, (QLabel, QLineEdit)):
                widget.setVisible(not checked)
    
    def toggle_telnet_user_pass(self, checked):
        """切换Telnet登录方式"""
        for widget in self.telnet_user_layout.children():
            if isinstance(widget, (QLabel, QLineEdit)):
                widget.setVisible(not checked)
    
    def get_form_data(self):
        """获取表单数据"""
        data = {}
        for field_name, widget in self.form_fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
        
        # SSH登录方式
        data['ssh_login_type'] = 'password' if self.ssh_login_type.checkedId() == 1 else 'local'
        data['ssh_username'] = self.ssh_user_input.text()
        data['ssh_user_password'] = self.ssh_user_pass_input.text()
        
        # Telnet登录方式
        data['telnet_login_type'] = 'password' if self.telnet_login_type.checkedId() == 1 else 'local'
        data['telnet_username'] = self.telnet_user_input.text()
        data['telnet_user_password'] = self.telnet_user_pass_input.text()
        
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
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: {t['danger']};
                color: {t['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['danger_hover']};
            }
        """)
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)
        
        row_height = 36
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
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: {t['danger']};
                color: {t['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['danger_hover']};
            }
        """)
        delete_button.clicked.connect(lambda _, r=row: table.removeRow(r))
        table.setCellWidget(row, 4, delete_button)
        
        row_height = 36
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
        table.setItem(row, 0, QTableWidgetItem(f"AggregatePort {agg_id}"))
        # 模式
        table.setItem(row, 1, QTableWidgetItem(agg_mode.split(' ')[0]))
        # 均衡方式
        table.setItem(row, 2, QTableWidgetItem(agg_lb))
        # 成员
        table.setItem(row, 3, QTableWidgetItem(member_ports))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: {t['danger']};
                color: {t['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['danger_hover']};
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
    
    def generate_config(self):
        """生成配置脚本（覆盖基类方法）"""
        data = self.get_form_data()
        checked_cards = self.get_checked_cards()
        
        config = []
        
        if '设备基础信息' in checked_cards:
            if data.get('hostname'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"hostname {data.get('hostname')}")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('enable_secret'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"enable secret {data.get('enable_secret')}")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('system_time'):
                config.append("enable")
                config.append(f"clock set {data.get('system_time')}")
                config.append("configure terminal")
                config.append("clock timezone BJ add 08:00")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'Console 串口登录配置' in checked_cards:
            if data.get('console_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line console 0")
                config.append(f" password {data.get('console_password')}")
                config.append(" login")
                config.append(" exec-timeout 10 0")
                config.append(" logging synchronous")
                config.append("exit")
                config.append("write")
                config.append("")
            elif data.get('console_username') and data.get('console_user_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"username {data.get('console_username')} password {data.get('console_user_password')}")
                config.append("line console 0")
                config.append(" login local")
                config.append(" exec-timeout 10 0")
                config.append(" logging synchronous")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '管理VLAN配置' in checked_cards:
            if data.get('mgmt_vlan'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"vlan {data.get('mgmt_vlan')}")
                if data.get('mgmt_vlan_name'):
                    config.append(f" name {data.get('mgmt_vlan_name')}")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('mgmt_ip') and data.get('mgmt_mask'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface Vlan {data.get('mgmt_vlan')}")
                config.append(f" ip address {data.get('mgmt_ip')} {data.get('mgmt_mask')}")
                config.append(" no shutdown")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'SSH登录配置' in checked_cards:
            if data.get('ssh_username') and data.get('ssh_user_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append("enable service ssh-server")
                config.append("ip ssh version 2")
                config.append("line vty 0 15")
                config.append(" login local")
                config.append(" transport input ssh")
                config.append(" exec-timeout 15 0")
                config.append("exit")
                config.append(f"username {data.get('ssh_username')} privilege 15 password {data.get('ssh_user_password')}")
                config.append("crypto key generate rsa")
                config.append("exit")
                config.append("write")
                config.append("")
            elif data.get('ssh_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append("enable service ssh-server")
                config.append("ip ssh version 2")
                config.append("line vty 0 15")
                config.append(f" password {data.get('ssh_password')}")
                config.append(" login")
                config.append(" transport input ssh")
                config.append(" exec-timeout 15 0")
                config.append("exit")
                config.append("crypto key generate rsa")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'Telnet登录配置' in checked_cards:
            if data.get('telnet_username') and data.get('telnet_user_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line vty 0 4")
                config.append(" login local")
                config.append(" exec-timeout 10 0")
                config.append("exit")
                config.append(f"username {data.get('telnet_username')} privilege 15 password {data.get('telnet_user_password')}")
                config.append("exit")
                config.append("write")
                config.append("")
            elif data.get('telnet_pwd'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line vty 0 4")
                config.append(f" password {data.get('telnet_pwd')}")
                config.append(" login")
                config.append(" exec-timeout 10 0")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'VLAN基础配置' in checked_cards:
            if data.get('vlan_basic'):
                vlan_input = data.get('vlan_basic').strip()
                # 替换中文逗号为英文逗号，支持中英文逗号输入
                vlan_input = vlan_input.replace('，', ',')
                # 处理逗号分隔的多个项
                items = [item.strip() for item in vlan_input.split(',') if item.strip()]
                if items:
                    config.append("enable")
                    config.append("configure terminal")
                    for item in items:
                        # 处理连续范围格式，如 "2 to 4" 或 "2-4"
                        if ' to ' in item:
                            parts = item.split(' to ')
                            if len(parts) == 2:
                                try:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    for vlan_id in range(start, end + 1):
                                        config.append(f"vlan {vlan_id}")
                                        config.append("exit")
                                except ValueError:
                                    # 如果不是有效的数字范围，当作单个VLAN处理
                                    config.append(f"vlan {item}")
                                    config.append("exit")
                        elif '-' in item:
                            parts = item.split('-')
                            if len(parts) == 2:
                                try:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    for vlan_id in range(start, end + 1):
                                        config.append(f"vlan {vlan_id}")
                                        config.append("exit")
                                except ValueError:
                                    # 如果不是有效的数字范围，当作单个VLAN处理
                                    config.append(f"vlan {item}")
                                    config.append("exit")
                        else:
                            # 处理单个VLAN
                            config.append(f"vlan {item}")
                            config.append("exit")
                    config.append("exit")
                    config.append("write")
                    config.append("")
        
        if '业务VLAN创建' in checked_cards:
            if data.get('business_vlan'):
                vlan_input = data.get('business_vlan').strip()
                # 替换中文逗号为英文逗号，支持中英文逗号输入
                vlan_input = vlan_input.replace('，', ',')
                # 处理逗号分隔的多个项
                items = [item.strip() for item in vlan_input.split(',') if item.strip()]
                if items:
                    config.append("enable")
                    config.append("configure terminal")
                    for item in items:
                        # 处理连续范围格式，如 "2 to 4" 或 "2-4"
                        if ' to ' in item:
                            parts = item.split(' to ')
                            if len(parts) == 2:
                                try:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    for vlan_id in range(start, end + 1):
                                        config.append(f"vlan {vlan_id}")
                                        config.append("exit")
                                except ValueError:
                                    # 如果不是有效的数字范围，当作单个VLAN处理
                                    config.append(f"vlan {item}")
                                    config.append("exit")
                        elif '-' in item:
                            parts = item.split('-')
                            if len(parts) == 2:
                                try:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    for vlan_id in range(start, end + 1):
                                        config.append(f"vlan {vlan_id}")
                                        config.append("exit")
                                except ValueError:
                                    # 如果不是有效的数字范围，当作单个VLAN处理
                                    config.append(f"vlan {item}")
                                    config.append("exit")
                        else:
                            # 处理单个VLAN
                            config.append(f"vlan {item}")
                            config.append("exit")
                    config.append("exit")
                    config.append("write")
                    config.append("")
        
        # 检查是否有端口配置需要执行
        has_port_config = False
        if hasattr(self, 'access_table') and self.access_table.rowCount() > 0:
            has_port_config = True
        if hasattr(self, 'trunk_table') and self.trunk_table.rowCount() > 0:
            has_port_config = True
        
        if has_port_config:
            config.append("enable")
            config.append("configure terminal")
            
            # 配置下联Access端口
            if '下联Access端口配置' in checked_cards:
                if hasattr(self, 'access_table') and self.access_table.rowCount() > 0:
                    for row in range(self.access_table.rowCount()):
                        interface = self.access_table.item(row, 0).text()
                        start_port = self.access_table.item(row, 1).text()
                        end_port = self.access_table.item(row, 2).text()
                        vlan = self.access_table.item(row, 3).text()
                        
                        if start_port == end_port:
                            config.append(f"interface {interface}{start_port}")
                        else:
                            config.append(f"interface range {interface}{start_port} to {interface}{end_port}")
                        config.append(" switchport mode access")
                        config.append(f" switchport access vlan {vlan}")
                        config.append(" no shutdown")
                        config.append("exit")
            
            # 配置上联Trunk端口
            if '上联Trunk端口配置' in checked_cards:
                if hasattr(self, 'trunk_table') and self.trunk_table.rowCount() > 0:
                    for row in range(self.trunk_table.rowCount()):
                        interface = self.trunk_table.item(row, 0).text()
                        start_port = self.trunk_table.item(row, 1).text()
                        end_port = self.trunk_table.item(row, 2).text()
                        vlan = self.trunk_table.item(row, 3).text()
                        
                        if start_port == end_port:
                            config.append(f"interface {interface}{start_port}")
                        else:
                            config.append(f"interface range {interface}{start_port} to {interface}{end_port}")
                        config.append(" switchport mode trunk")
                        config.append(f" switchport trunk allowed vlan {vlan}")
                        config.append(" no shutdown")
                        config.append("exit")
            
            config.append("exit")
            config.append("write")
            config.append("")

        if '链路聚合 (AggregatePort)' in checked_cards:
            # 处理表格中的链路聚合配置
            if hasattr(self, 'agg_table') and self.agg_table.rowCount() > 0:
                # 全局配置负载均衡算法和所有聚合组配置在同一个会话中
                config.append("enable")
                config.append("configure terminal")
                
                # 全局配置负载均衡算法（只配置一次）
                # 获取第一个聚合组的负载均衡配置
                first_lb_item = self.agg_table.item(0, 2)
                if first_lb_item:
                    lb = first_lb_item.text()
                    # 提取负载均衡算法
                    if 'src-dst-ip+port' in lb:
                        lb_algorithm = 'src-dst-ip-port'
                    elif 'src-dst-mac' in lb:
                        lb_algorithm = 'src-dst-mac'
                    else:
                        lb_algorithm = 'src-dst-ip'
                    config.append(f"aggregateport load-balance {lb_algorithm}")
                
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
                        # 格式：Te 0/1 to Te 0/4
                        import re
                        match = re.match(r'([A-Za-z\s]+)(\d+/)(\d+)\s+to\s+\1\2(\d+)', member)
                        if match:
                            interface_type = match.group(1)
                            interface_num = match.group(2)
                            start = match.group(3)
                            end = match.group(4)
                            
                            # 构建端口范围字符串
                            port_range = f"{interface_type}{interface_num}{start} - {end}"
                            
                            # 配置聚合端口
                            config.append(f"interface AggregatePort {agg_id}")
                            config.append(" switchport mode trunk")
                            config.append(" switchport trunk allowed vlan all")
                            if mode == 'LACP':
                                config.append(" lacp mode active")
                            config.append(" no shutdown")
                            config.append("exit")
                            
                            # 配置成员端口
                            if mode == 'LACP':
                                config.append(f"interface range {port_range}")
                                config.append(f" port-group {agg_id} mode active")
                            else:  # Static
                                config.append(f"interface range {port_range}")
                                config.append(f" port-group {agg_id} mode on")
                            config.append(" no shutdown")
                            config.append("exit")
                
                # 所有配置完成后统一退出和保存
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '业务VLANIF三层网关配置' in checked_cards:
            if data.get('user_gw') and data.get('user_mask'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface Vlan {data.get('user_vlan')}")
                config.append(f" ip address {data.get('user_gw')} {data.get('user_mask')}")
                config.append(" no shutdown")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('server_gw') and data.get('server_mask'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface Vlan {data.get('server_vlan')}")
                config.append(f" ip address {data.get('server_gw')} {data.get('server_mask')}")
                config.append(" no shutdown")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '静态路由配置' in checked_cards:
            routes = []
            if data.get('dst_net1') and data.get('dst_mask1') and data.get('nh1'):
                routes.append(f"ip route {data.get('dst_net1')} {data.get('dst_mask1')} {data.get('nh1')}")
            if data.get('dst_net2') and data.get('dst_mask2') and data.get('nh2'):
                routes.append(f"ip route {data.get('dst_net2')} {data.get('dst_mask2')} {data.get('nh2')}")
            if data.get('dst_net3') and data.get('dst_mask3') and data.get('nh3'):
                routes.append(f"ip route {data.get('dst_net3')} {data.get('dst_mask3')} {data.get('nh3')}")
            if routes:
                config.append("enable")
                config.append("configure terminal")
                config.extend(routes)
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'OSPF动态路由配置' in checked_cards:
            if data.get('ospf_proc') and data.get('ospf_rid'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"router ospf {data.get('ospf_proc')}")
                config.append(f" router-id {data.get('ospf_rid')}")
                if data.get('mgmt_net') and data.get('mgmt_wild') and data.get('area_id'):
                    config.append(f" network {data.get('mgmt_net')} {data.get('mgmt_wild')} area {data.get('area_id')}")
                if data.get('user_net') and data.get('user_wild') and data.get('area_id'):
                    config.append(f" network {data.get('user_net')} {data.get('user_wild')} area {data.get('area_id')}")
                if data.get('server_net') and data.get('server_wild') and data.get('area_id'):
                    config.append(f" network {data.get('server_net')} {data.get('server_wild')} area {data.get('area_id')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'DHCP Server全局配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("service dhcp")
            config.append("ip dhcp relay information option")
            config.append("exit")
            config.append("write")
            config.append("")
            
            if data.get('user_ex_start') and data.get('user_ex_end'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip dhcp excluded-address {data.get('user_ex_start')} {data.get('user_ex_end')}")
                if data.get('server_ex_start') and data.get('server_ex_end'):
                    config.append(f"ip dhcp excluded-address {data.get('server_ex_start')} {data.get('server_ex_end')}")
                config.append("exit")
                config.append("write")
                config.append("")
            
            if data.get('user_pool') and data.get('user_pool_net'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip dhcp pool {data.get('user_pool')}")
                config.append(f" network {data.get('user_pool_net')} {data.get('user_pool_mask')}")
                if data.get('user_pool_gw'):
                    config.append(f" default-router {data.get('user_pool_gw')}")
                if data.get('dns1'):
                    dns_cmd = f" dns-server {data.get('dns1')}"
                    if data.get('dns2'):
                        dns_cmd += f" {data.get('dns2')}"
                    config.append(dns_cmd)
                config.append(" lease 7 0 0")
                config.append("exit")
                config.append("write")
                config.append("")
            
            if data.get('server_pool') and data.get('server_pool_net'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip dhcp pool {data.get('server_pool')}")
                config.append(f" network {data.get('server_pool_net')} {data.get('server_pool_mask')}")
                if data.get('server_pool_gw'):
                    config.append(f" default-router {data.get('server_pool_gw')}")
                if data.get('dns1'):
                    dns_cmd = f" dns-server {data.get('dns1')}"
                    if data.get('dns2'):
                        dns_cmd += f" {data.get('dns2')}"
                    config.append(dns_cmd)
                config.append(" lease 30 0 0")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'DHCP Snooping安全配置' in checked_cards:
            if data.get('trust_port'):
                config.append("enable")
                config.append("configure terminal")
                config.append("ip dhcp snooping enable")
                if data.get('snooping_vlan'):
                    config.append(f"ip dhcp snooping vlan {data.get('snooping_vlan')}")
                config.append("ip dhcp snooping verify mac-address")
                config.append(f"interface {data.get('trust_port')}")
                config.append(" ip dhcp snooping trust")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'MSTP生成树防环配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("spanning-tree mode mstp")
            config.append("spanning-tree mst configuration")
            if data.get('mst_name'):
                config.append(f" name {data.get('mst_name')}")
            if data.get('revision'):
                config.append(f" revision {data.get('revision')}")
            if data.get('ins1_vlan'):
                config.append(f" instance 1 vlan {data.get('ins1_vlan')}")
            if data.get('ins2_vlan'):
                config.append(f" instance 2 vlan {data.get('ins2_vlan')}")
            config.append(" active region-configuration")
            config.append("exit")
            if data.get('mst_prio'):
                config.append(f"spanning-tree mst 1 priority {data.get('mst_prio')}")
            config.append("spanning-tree enable")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if 'ACL访问控制配置' in checked_cards:
            if data.get('manage_net') and data.get('manage_wild'):
                config.append("enable")
                config.append("configure terminal")
                config.append("ip access-list standard 10")
                config.append(f" permit {data.get('manage_net')} {data.get('manage_wild')}")
                config.append(" deny any")
                config.append("exit")
                config.append("line vty 0 15")
                config.append(" access-class 10 in")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('user_acl_net') and data.get('server_acl_net'):
                config.append("enable")
                config.append("configure terminal")
                config.append("ip access-list extended 100")
                config.append(f" permit ip {data.get('user_acl_net')} {data.get('user_acl_wild')} {data.get('server_acl_net')} {data.get('server_acl_wild')}")
                config.append(" deny ip any any")
                config.append("exit")
                config.append(f"interface Vlan {data.get('user_vlan')}")
                config.append(" ip access-group 100 in")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'NTP时钟同步配置' in checked_cards:
            if data.get('ntp_server'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ntp server {data.get('ntp_server')}")
                config.append("ntp update-calendar")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'SNMPv2c配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('snmp_ro_community'):
                config.append(f"snmp-server community {data.get('snmp_ro_community')} ro")
            if data.get('trap_server') and data.get('trap_community'):
                config.append(f"snmp-server host {data.get('trap_server')} traps {data.get('trap_community')} version 2c")
            config.append("snmp-server enable traps")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '端口镜像配置' in checked_cards:
            if data.get('mirror_src') and data.get('mirror_dst'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"monitor session 1 source interface {data.get('mirror_src')} both")
                config.append(f"monitor session 1 destination interface {data.get('mirror_dst')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        self.preview_text.setPlainText('\n'.join(config))
    
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
