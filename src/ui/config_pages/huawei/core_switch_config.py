from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from src.ui.config_pages.base_config_page import BaseConfigPage
from src.core.theme_engine import ThemeEngine

class HuaweiCoreSwitchConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'huawei', 'core_switch')
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
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable加密密码', 'enable_secret', is_password=True)
        
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
        console_pwd_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        pwd_layout.addWidget(console_pwd_input)
        self.form_fields['console_pwd'] = console_pwd_input
        
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
        user_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
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
        user_pwd_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        user_pwd_layout.addWidget(user_pwd_input)
        self.form_fields['console_user_password'] = user_pwd_input
        
        user_pwd_layout.addStretch()
        card_console.layout().addLayout(user_pwd_layout)
        
        # 系统时间配置卡片
        card_time = self.create_card('系统时间配置', '🕒', '配置设备系统时间')
        self.add_form_item(card_time, '系统时间', 'system_time')
        
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
        
        # VLAN基础配置卡片
        card4_vlan = self.create_card('VLAN基础配置', '🌐', '批量创建VLAN，支持连续范围如2 to 10')
        # 批量创建VLAN输入框
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('批量创建:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setStyleSheet(self._get_input_style())
        item_layout.addWidget(input_widget)
        self.form_fields['vlan_basic'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('批量创建vlan，用逗号隔开，连续的用to或者-，例如：2 to 8，11或2-8，11')
        hint_label.setStyleSheet(f"color: {self._theme_engine.current_theme['primary']}; font-size: 9pt;")
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card4_vlan.layout().addLayout(item_layout)
        
        tab1.layout().addWidget(card1)
        tab1.layout().addWidget(card4_vlan)  # VLAN基础配置（移至第二位）
        tab1.layout().addWidget(card_console)  # Console 串口登录配置卡片
        tab1.layout().addWidget(card_time)    # 系统时间配置卡片
        tab1.layout().addWidget(card_ssh)  # SSH登录配置卡片
        tab1.layout().addWidget(card_telnet)  # Telnet登录配置卡片
        tab1.content_layout.addStretch()
        self.tab_widget.addTab(tab1.widget, '⚙️ 基础管理')
        
        # Tab2：端口与链路配置
        tab2 = self.create_tab_content()
        
        # 下联Access端口配置卡片
        card9 = self.create_card('下联Access端口配置', '🔌', '配置下联端口为Access模式')
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        
        interface_layout = QVBoxLayout()
        interface_layout.setSpacing(12)
        interface_label = QLabel('端口类型:')
        interface_label.setStyleSheet(self._get_label_secondary_style())
        interface_layout.addWidget(interface_label)
        interface_combo = QComboBox()
        interface_combo.addItems(['G0/', 'G1/', 'T0/'])
        interface_combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QComboBox:focus {
                border: 1px solid {t['border']};
            }
        """)
        interface_layout.addWidget(interface_combo)
        config_layout.addLayout(interface_layout)
        
        port_layout = QVBoxLayout()
        port_layout.setSpacing(12)
        port_label = QLabel('端口范围:')
        port_label.setStyleSheet(self._get_label_secondary_style())
        port_layout.addWidget(port_label)
        port_range_layout = QHBoxLayout()
        port_range_layout.setSpacing(12)
        start_input = QLineEdit()
        start_input.setPlaceholderText('开始端口')
        start_input.setFixedWidth(100)
        start_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        port_range_layout.addWidget(start_input)
        port_range_layout.addWidget(QLabel('至'))
        end_input = QLineEdit()
        end_input.setPlaceholderText('结束端口')
        end_input.setFixedWidth(100)
        end_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        port_range_layout.addWidget(end_input)
        port_layout.addLayout(port_range_layout)
        config_layout.addLayout(port_layout)
        
        vlan_layout = QVBoxLayout()
        vlan_layout.setSpacing(12)
        vlan_label = QLabel('加入VLAN:')
        vlan_label.setStyleSheet(self._get_label_secondary_style())
        vlan_layout.addWidget(vlan_label)
        vlan_input = QLineEdit()
        vlan_input.setPlaceholderText('请输入VLAN ID')
        vlan_input.setFixedWidth(140)
        vlan_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        vlan_layout.addWidget(vlan_input)
        config_layout.addLayout(vlan_layout)
        
        add_button = QPushButton('点击增加')
        add_button.setFixedSize(120, 40)
        add_button.setStyleSheet(self._get_primary_button_style())
        add_button.clicked.connect(lambda: self.add_access_port(interface_combo, start_input, end_input, vlan_input, access_table))
        config_layout.addWidget(add_button)
        
        config_layout.addStretch()
        card9.layout().addLayout(config_layout)
        
        # Access端口表格
        access_table = QTableWidget(0, 5)
        access_table.setHorizontalHeaderLabels(['端口', '开始端口', '结束端口', '加入VLAN', '操作'])
        access_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        access_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        access_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: {t['hover_bg']};
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
            }
        """)
        access_table.setColumnWidth(0, 120)
        access_table.setColumnWidth(1, 100)
        access_table.setColumnWidth(2, 100)
        access_table.setColumnWidth(3, 100)
        access_table.setColumnWidth(4, 80)
        access_table.setStyleSheet(self._get_table_with_selection_style())
        access_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        access_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        access_table.setMinimumHeight(100)
        card9.layout().addWidget(access_table)
        self.access_table = access_table
        
        # 上联Trunk端口配置卡片
        card10 = self.create_card('上联Trunk端口配置', '🔌', '配置上联端口为Trunk模式')
        trunk_config_layout = QHBoxLayout()
        trunk_config_layout.setSpacing(24)
        
        trunk_interface_layout = QVBoxLayout()
        trunk_interface_layout.setSpacing(12)
        trunk_interface_label = QLabel('端口类型:')
        trunk_interface_label.setStyleSheet(self._get_label_secondary_style())
        trunk_interface_layout.addWidget(trunk_interface_label)
        trunk_interface_combo = QComboBox()
        trunk_interface_combo.addItems(['G0/', 'G1/', 'T0/'])
        trunk_interface_combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QComboBox:focus {
                border: 1px solid {t['border']};
            }
        """)
        trunk_interface_layout.addWidget(trunk_interface_combo)
        trunk_config_layout.addLayout(trunk_interface_layout)
        
        trunk_port_layout = QVBoxLayout()
        trunk_port_layout.setSpacing(12)
        trunk_port_label = QLabel('端口范围:')
        trunk_port_label.setStyleSheet(self._get_label_secondary_style())
        trunk_port_layout.addWidget(trunk_port_label)
        trunk_port_range_layout = QHBoxLayout()
        trunk_port_range_layout.setSpacing(12)
        trunk_start_input = QLineEdit()
        trunk_start_input.setPlaceholderText('开始端口')
        trunk_start_input.setFixedWidth(100)
        trunk_start_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        trunk_port_range_layout.addWidget(trunk_start_input)
        trunk_port_range_layout.addWidget(QLabel('至'))
        trunk_end_input = QLineEdit()
        trunk_end_input.setPlaceholderText('结束端口')
        trunk_end_input.setFixedWidth(100)
        trunk_end_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        trunk_port_range_layout.addWidget(trunk_end_input)
        trunk_port_layout.addLayout(trunk_port_range_layout)
        trunk_config_layout.addLayout(trunk_port_layout)
        
        trunk_vlan_layout = QVBoxLayout()
        trunk_vlan_layout.setSpacing(12)
        trunk_vlan_label = QLabel('允许VLAN:')
        trunk_vlan_label.setStyleSheet(self._get_label_secondary_style())
        trunk_vlan_layout.addWidget(trunk_vlan_label)
        trunk_vlan_input = QLineEdit()
        trunk_vlan_input.setPlaceholderText('请输入VLAN列表')
        trunk_vlan_input.setFixedWidth(140)
        trunk_vlan_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
            QLineEdit:focus {
                border: 1px solid {t['border']};
            }
        """)
        trunk_vlan_layout.addWidget(trunk_vlan_input)
        trunk_config_layout.addLayout(trunk_vlan_layout)
        
        trunk_add_button = QPushButton('点击增加')
        trunk_add_button.setFixedSize(120, 40)
        trunk_add_button.setStyleSheet(self._get_primary_button_style())
        trunk_add_button.clicked.connect(lambda: self.add_trunk_port(trunk_interface_combo, trunk_start_input, trunk_end_input, trunk_vlan_input, trunk_table))
        trunk_config_layout.addWidget(trunk_add_button)
        
        trunk_config_layout.addStretch()
        card10.layout().addLayout(trunk_config_layout)
        
        # Trunk端口表格
        trunk_table = QTableWidget(0, 5)
        trunk_table.setHorizontalHeaderLabels(['端口', '开始端口', '结束端口', '允许VLAN', '操作'])
        trunk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        trunk_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        trunk_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: {t['hover_bg']};
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
            }
        """)
        trunk_table.setColumnWidth(0, 120)
        trunk_table.setColumnWidth(1, 100)
        trunk_table.setColumnWidth(2, 100)
        trunk_table.setColumnWidth(3, 100)
        trunk_table.setColumnWidth(4, 80)
        trunk_table.setStyleSheet(self._get_table_with_selection_style())
        trunk_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        trunk_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        trunk_table.setMinimumHeight(100)
        card10.layout().addWidget(trunk_table)
        self.trunk_table = trunk_table
        
        # 链路聚合配置卡片
        card11 = self.create_card('链路聚合 (Eth-Trunk)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
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
        self.agg_id_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
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
        self.agg_mode_combo.addItems(['LACP (动态)', 'Manual (静态)'])
        self.agg_mode_combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
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
        self.agg_lb_combo.addItems(['src-dst-ip (推荐)', 'src-dst-mac', 'src-dst-port'])
        self.agg_lb_combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
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
        self.agg_interface_combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: {t['card_bg']};
            }
        """)
        member_port_layout.addWidget(self.agg_interface_combo)
        self.agg_start_port = QLineEdit()
        self.agg_start_port.setPlaceholderText('开始')
        self.agg_start_port.setFixedWidth(60)
        self.agg_start_port.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
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
        self.agg_end_port.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
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
        card11.layout().addLayout(config_layout)
        
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
        self.agg_table.setStyleSheet(f"""
            QTableWidget {
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px;
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
        self.agg_table.verticalHeader().setDefaultSectionSize(32)
        self.agg_table.setRowCount(0)
        self.agg_table.setMinimumWidth(600)
        self.agg_table.setFixedHeight(50)
        card11.layout().addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout().addWidget(card9)  # 下联Access端口配置（上）
        tab2.layout().addWidget(card10)  # 上联Trunk端口配置（下）
        tab2.layout().addWidget(card11)
        tab2.content_layout.addStretch()
        self.tab_widget.addTab(tab2.widget, '🔌 端口与上联')
        
        # Tab3：VLAN与路由配置
        tab3 = self.create_tab_content()
        card4 = self.create_card('业务VLAN创建', '🌐', '批量创建VLAN，支持连续范围如2 to 10')
        # 批量创建VLAN输入框
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel('批量创建:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        input_widget = QLineEdit()
        input_widget.setStyleSheet(self._get_input_style())
        item_layout.addWidget(input_widget)
        self.form_fields['business_vlan'] = input_widget
        
        # 添加小字提示
        hint_label = QLabel('批量创建vlan，用逗号隔开，连续的用to或者-，例如：2 to 8，11或2-8，11')
        hint_label.setStyleSheet(f"color: {self._theme_engine.current_theme['primary']}; font-size: 9pt;")
        item_layout.addWidget(hint_label)
        
        item_layout.addStretch()
        card4.layout().addLayout(item_layout)
        
        # 业务VLAN名称和管理VLAN ID
        self.add_form_item(card4, '业务VLAN名称', 'business_vlan_name')
        self.add_form_item(card4, '管理VLAN ID', 'mgmt_vlan')
        
        card5 = self.create_card('管理地址配置', '📍', '配置管理VLAN接口IP地址')
        self.add_form_item(card5, '管理IP地址', 'mgmt_ip')
        self.add_form_item(card5, '子网掩码', 'subnet_mask')
        self.add_form_item(card5, '默认网关', 'gateway')
        
        card6 = self.create_card('OSPF路由配置', '🌐', '配置OSPF动态路由')
        self.add_form_item(card6, 'OSPF进程号', 'ospf_process')
        self.add_form_item(card6, '区域ID', 'area_id')
        self.add_form_item(card6, '网络地址', 'network_addr')
        self.add_form_item(card6, '反掩码', 'wildcard_mask')
        
        card7 = self.create_card('静态路由配置', '🛣️', '配置静态路由')
        self.add_form_item(card7, '目标网段', 'static_dest')
        self.add_form_item(card7, '子网掩码', 'static_mask')
        self.add_form_item(card7, '下一跳地址', 'next_hop')
        
        tab3.layout().addWidget(card4)
        tab3.layout().addWidget(card5)
        tab3.layout().addWidget(card6)
        tab3.layout().addWidget(card7)
        tab3.content_layout.addStretch()
        self.tab_widget.addTab(tab3.widget, '🌐 VLAN与路由')
        

        
        # Tab4：DHCP & 安全防环
        tab4 = self.create_tab_content()
        card11 = self.create_card('DHCP服务配置', '📶', '配置DHCP地址池和排除地址')
        self.add_form_item(card11, 'DHCP池名称', 'dhcp_pool')
        self.add_form_item(card11, '网络地址', 'network')
        self.add_form_item(card11, '子网掩码', 'mask')
        self.add_form_item(card11, '网关地址', 'pool_gw')
        self.add_form_item(card11, '地址池起始IP', 'pool_start')
        self.add_form_item(card11, '地址池结束IP', 'pool_end')
        self.add_form_item(card11, '排除地址开始', 'exclude_start')
        self.add_form_item(card11, '排除地址结束', 'exclude_end')
        self.add_form_item(card11, '主DNS', 'dns1')
        self.add_form_item(card11, '备DNS', 'dns2')
        
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
        
    def add_access_port(self, interface_combo, start_input, end_input, vlan_input, table):
        """添加Access端口配置到表格"""
        interface = interface_combo.currentText()
        start_port = start_input.text().strip()
        end_port = end_input.text().strip()
        vlan = vlan_input.text().strip()
        
        if not start_port or not end_port or not vlan:
            return
        
        # 添加新行
        row = table.rowCount()
        table.insertRow(row)
        
        # 设置表格数据
        table.setItem(row, 0, QTableWidgetItem(interface))
        table.setItem(row, 1, QTableWidgetItem(start_port))
        table.setItem(row, 2, QTableWidgetItem(end_port))
        table.setItem(row, 3, QTableWidgetItem(vlan))
        
        # 添加删除按钮
        delete_button = QPushButton('删除')
        delete_button.setStyleSheet(f"""
            QPushButton {
                background-color: {t['page_bg']};
                color: {t['text_primary']};
                border: none;
                border-radius: {t['radius_md']}px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['hover_bg']};
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_port(table, row))
        table.setCellWidget(row, 4, delete_button)
        
        # 调整表格高度
        self.adjust_table_height(table)
        
        # 清空输入框
        start_input.clear()
        end_input.clear()
        vlan_input.clear()
    
    def add_trunk_port(self, interface_combo, start_input, end_input, vlan_input, table):
        """添加Trunk端口配置到表格"""
        interface = interface_combo.currentText()
        start_port = start_input.text().strip()
        end_port = end_input.text().strip()
        vlan = vlan_input.text().strip()
        
        if not start_port or not end_port or not vlan:
            return
        
        # 添加新行
        row = table.rowCount()
        table.insertRow(row)
        
        # 设置表格数据
        table.setItem(row, 0, QTableWidgetItem(interface))
        table.setItem(row, 1, QTableWidgetItem(start_port))
        table.setItem(row, 2, QTableWidgetItem(end_port))
        table.setItem(row, 3, QTableWidgetItem(vlan))
        
        # 添加删除按钮
        delete_button = QPushButton('删除')
        delete_button.setStyleSheet(f"""
            QPushButton {
                background-color: {t['page_bg']};
                color: {t['text_primary']};
                border: none;
                border-radius: {t['radius_md']}px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['hover_bg']};
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_port(table, row))
        table.setCellWidget(row, 4, delete_button)
        
        # 调整表格高度
        self.adjust_table_height(table)
        
        # 清空输入框
        start_input.clear()
        end_input.clear()
        vlan_input.clear()
    
    def delete_port(self, table, row):
        """从表格中删除端口配置"""
        table.removeRow(row)
        # 调整表格高度
        self.adjust_table_height(table)
    
    def adjust_table_height(self, table):
        """根据行数调整表格高度"""
        row_height = 30  # 每行高度
        header_height = 40  # 表头高度
        min_height = 100  # 最小高度
        height = max(min_height, header_height + row_height * table.rowCount())
        table.setFixedHeight(height)
        
        # 触发布局更新
        table.parent().adjustSize()
        table.parent().parent().adjustSize()
        table.parent().parent().parent().adjustSize()
        self.tab_widget.adjustSize()
    
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
        table.setItem(row, 0, QTableWidgetItem(f"Eth-Trunk {agg_id}"))
        # 模式
        table.setItem(row, 1, QTableWidgetItem(agg_mode.split(' ')[0]))
        # 均衡方式
        table.setItem(row, 2, QTableWidgetItem(agg_lb))
        # 成员
        table.setItem(row, 3, QTableWidgetItem(member_ports))
        # 操作按钮
        delete_button = QPushButton('删除')
        delete_button.setStyleSheet(f"""
            QPushButton {
                background-color: {t['page_bg']};
                color: {t['text_primary']};
                border: none;
                border-radius: {t['radius_md']}px;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: {t['hover_bg']};
            }
        """)
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
    
    def create_card(self, title, icon, description=''):
        """创建卡片，带功能描述"""
        card = QWidget()
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
            # 标签模式（不可编辑）
            value_label = QLabel(default_value)
            value_label.setStyleSheet(self._get_label_style())
            item_layout.addWidget(value_label)
        else:
            # 输入框模式
            input_field = QLineEdit()
            input_field.setFixedHeight(26)
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
            input_field.setStyleSheet(f"""
                QLineEdit {
                    border: 1px solid {t['input_border']};
                    border-radius: {t['radius_md']}px;
                    padding: 0 12px;
                    font-size: 10pt;
                    color: {t['text_main']};
                }
                QLineEdit:focus {
                    border-color: {t['border']};
                    outline: none;
                }
            """)
            if default_value:
                input_field.setText(default_value)
            item_layout.addWidget(input_field)
            self.form_fields[field_name] = input_field
        
        card.layout().addLayout(item_layout)
        
    def add_combo_item(self, card, label_text, field_name, options):
        """添加下拉选择框"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet(self._get_label_secondary_style())
        item_layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setFixedHeight(26)
        combo.setStyleSheet(f"""
            QComboBox {
                border: 1px solid {t['input_border']};
                border-radius: {t['radius_md']}px;
                padding: 0 12px;
                font-size: 10pt;
                color: {t['text_main']};
            }
            QComboBox:focus {
                border-color: {t['border']};
                outline: none;
            }
        """)
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
                config_commands.append(f"sysname {data.get('hostname')}")
            if data.get('enable_secret'):
                config_commands.append(f"aaa")
                config_commands.append(f"local-user admin password irreversible-cipher {data.get('enable_secret')}")
                config_commands.append(f"local-user admin privilege level 15")
                config_commands.append(f"local-user admin service-type terminal ssh telnet")
                config_commands.append(f"quit")
        
        if 'Console 串口登录配置' in checked_cards:
            if data.get('console_pwd'):
                config_commands.append(f"user-interface console 0")
                config_commands.append(f"authentication-mode password")
                config_commands.append(f"set authentication password cipher {data.get('console_pwd')}")
                config_commands.append(f"quit")
            elif data.get('console_username') and data.get('console_user_password'):
                config_commands.append(f"aaa")
                config_commands.append(f"local-user {data.get('console_username')} password irreversible-cipher {data.get('console_user_password')}")
                config_commands.append(f"local-user {data.get('console_username')} privilege level 15")
                config_commands.append(f"local-user {data.get('console_username')} service-type terminal")
                config_commands.append(f"quit")
                config_commands.append(f"user-interface console 0")
                config_commands.append(f"authentication-mode aaa")
                config_commands.append(f"quit")
        
        if '系统时间配置' in checked_cards:
            if data.get('system_time'):
                config_commands.append(f"clock datetime {data.get('system_time')}")
                config_commands.append(f"clock timezone beijing add 08:00:00")
        
        if 'SSH登录配置' in checked_cards:
            if data.get('ssh_username') and data.get('ssh_user_password'):
                config_commands.append(f"stelnet server enable")
                config_commands.append(f"ssh user {data.get('ssh_username')} authentication-type password")
                config_commands.append(f"ssh user {data.get('ssh_username')} service-type stelnet")
                config_commands.append(f"aaa")
                config_commands.append(f"local-user {data.get('ssh_username')} password irreversible-cipher {data.get('ssh_user_password')}")
                config_commands.append(f"local-user {data.get('ssh_username')} privilege level 15")
                config_commands.append(f"local-user {data.get('ssh_username')} service-type terminal ssh")
                config_commands.append(f"quit")
                config_commands.append(f"user-interface vty 0 4")
                config_commands.append(f"authentication-mode aaa")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
            elif data.get('ssh_password'):
                config_commands.append(f"stelnet server enable")
                config_commands.append(f"user-interface vty 0 4")
                config_commands.append(f"authentication-mode password")
                config_commands.append(f"set authentication password cipher {data.get('ssh_password')}")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
        
        if 'Telnet登录配置' in checked_cards:
            if data.get('telnet_username') and data.get('telnet_user_password'):
                config_commands.append(f"aaa")
                config_commands.append(f"local-user {data.get('telnet_username')} password irreversible-cipher {data.get('telnet_user_password')}")
                config_commands.append(f"local-user {data.get('telnet_username')} privilege level 15")
                config_commands.append(f"local-user {data.get('telnet_username')} service-type terminal")
                config_commands.append(f"quit")
                config_commands.append(f"user-interface vty 5 9")
                config_commands.append(f"authentication-mode aaa")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
            elif data.get('telnet_pwd'):
                config_commands.append(f"user-interface vty 5 9")
                config_commands.append(f"authentication-mode password")
                config_commands.append(f"set authentication password cipher {data.get('telnet_pwd')}")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
        
        if 'VLAN基础配置' in checked_cards:
            if data.get('vlan_basic'):
                vlan_input = data.get('vlan_basic').strip()
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
                                    config_commands.append(f"quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append(f"quit")
                    elif '-' in item:
                        parts = item.split('-')
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                for vlan_id in range(start, end + 1):
                                    config_commands.append(f"vlan {vlan_id}")
                                    config_commands.append(f"quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                config_commands.append(f"quit")
                    else:
                        # 处理单个VLAN
                        config_commands.append(f"vlan {item}")
                        config_commands.append(f"quit")
        
        if '业务VLAN创建' in checked_cards:
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
                                    if data.get('business_vlan_name'):
                                        config_commands.append(f"description {data.get('business_vlan_name')}")
                                    config_commands.append(f"quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                if data.get('business_vlan_name'):
                                    config_commands.append(f"description {data.get('business_vlan_name')}")
                                config_commands.append(f"quit")
                    elif '-' in item:
                        parts = item.split('-')
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                for vlan_id in range(start, end + 1):
                                    config_commands.append(f"vlan {vlan_id}")
                                    if data.get('business_vlan_name'):
                                        config_commands.append(f"description {data.get('business_vlan_name')}")
                                    config_commands.append(f"quit")
                            except ValueError:
                                # 如果不是有效的数字范围，当作单个VLAN处理
                                config_commands.append(f"vlan {item}")
                                if data.get('business_vlan_name'):
                                    config_commands.append(f"description {data.get('business_vlan_name')}")
                                config_commands.append(f"quit")
                    else:
                        # 处理单个VLAN
                        config_commands.append(f"vlan {item}")
                        if data.get('business_vlan_name'):
                            config_commands.append(f"description {data.get('business_vlan_name')}")
                        config_commands.append(f"quit")
            if data.get('mgmt_vlan'):
                config_commands.append(f"vlan {data.get('mgmt_vlan')}")
                config_commands.append(f"description manage")
                config_commands.append(f"quit")
        
        if '管理地址配置' in checked_cards:
            if data.get('mgmt_ip') and data.get('mgmt_vlan'):
                config_commands.append(f"interface Vlanif {data.get('mgmt_vlan')}")
                subnet = data.get('subnet_mask', '255.255.255.0')
                config_commands.append(f"ip address {data.get('mgmt_ip')} {subnet}")
                config_commands.append(f"quit")
            if data.get('gateway'):
                config_commands.append(f"ip route-static 0.0.0.0 0.0.0.0 {data.get('gateway')}")
        
        if 'OSPF路由配置' in checked_cards:
            if data.get('ospf_process') and data.get('area_id'):
                config_commands.append(f"ospf {data.get('ospf_process')}")
                config_commands.append(f"area {data.get('area_id')}")
                if data.get('network_addr') and data.get('wildcard_mask'):
                    config_commands.append(f"network {data.get('network_addr')} {data.get('wildcard_mask')}")
                config_commands.append(f"quit")
        
        if '静态路由配置' in checked_cards:
            if data.get('static_dest') and data.get('static_mask') and data.get('next_hop'):
                config_commands.append(f"ip route-static {data.get('static_dest')} {data.get('static_mask')} {data.get('next_hop')}")
        
        if '核心端口配置' in checked_cards:
            if data.get('core_port'):
                config_commands.append(f"interface GigabitEthernet {data.get('core_port')}")
                if data.get('port_speed'):
                    config_commands.append(f"speed {data.get('port_speed')}")
                if data.get('duplex_mode'):
                    config_commands.append(f"duplex {data.get('duplex_mode')}")
                config_commands.append(f"quit")
        
        # 检查是否有端口配置需要执行
        has_port_config = False
        if hasattr(self, 'access_table') and self.access_table.rowCount() > 0:
            has_port_config = True
        if hasattr(self, 'trunk_table') and self.trunk_table.rowCount() > 0:
            has_port_config = True
        
        if has_port_config:
            # 配置下联Access端口
            if '下联Access端口配置' in checked_cards:
                if hasattr(self, 'access_table') and self.access_table.rowCount() > 0:
                    for row in range(self.access_table.rowCount()):
                        interface = self.access_table.item(row, 0).text()
                        start_port = self.access_table.item(row, 1).text()
                        end_port = self.access_table.item(row, 2).text()
                        vlan = self.access_table.item(row, 3).text()
                        
                        # 转换接口缩写为完整格式
                        full_interface = interface
                        if interface == 'G0/':
                            full_interface = 'GigabitEthernet 0/'
                        elif interface == 'G1/':
                            full_interface = 'GigabitEthernet 1/'
                        elif interface == 'T0/':
                            full_interface = 'TenGigabitEthernet 0/'
                        
                        if start_port == end_port:
                            config_commands.append(f"interface {full_interface}{start_port}")
                        else:
                            # 提取接口类型和模块号
                            interface_parts = full_interface.split(' ')
                            interface_type = interface_parts[0]
                            module = interface_parts[1].rstrip('/')
                            config_commands.append(f"interface {interface_type} {module}/{start_port} to {module}/{end_port}")
                        config_commands.append("port link-type access")
                        config_commands.append(f"port default vlan {vlan}")
                        config_commands.append("quit")
            
            # 配置上联Trunk端口
            if '上联Trunk端口配置' in checked_cards:
                if hasattr(self, 'trunk_table') and self.trunk_table.rowCount() > 0:
                    for row in range(self.trunk_table.rowCount()):
                        interface = self.trunk_table.item(row, 0).text()
                        start_port = self.trunk_table.item(row, 1).text()
                        end_port = self.trunk_table.item(row, 2).text()
                        vlan = self.trunk_table.item(row, 3).text()
                        
                        # 转换接口缩写为完整格式
                        full_interface = interface
                        if interface == 'G0/':
                            full_interface = 'GigabitEthernet 0/'
                        elif interface == 'G1/':
                            full_interface = 'GigabitEthernet 1/'
                        elif interface == 'T0/':
                            full_interface = 'TenGigabitEthernet 0/'
                        
                        if start_port == end_port:
                            config_commands.append(f"interface {full_interface}{start_port}")
                        else:
                            # 提取接口类型和模块号
                            interface_parts = full_interface.split(' ')
                            interface_type = interface_parts[0]
                            module = interface_parts[1].rstrip('/')
                            config_commands.append(f"interface {interface_type} {module}/{start_port} to {module}/{end_port}")
                        config_commands.append("port link-type trunk")
                        config_commands.append(f"port trunk allow-pass vlan {vlan}")
                        config_commands.append("quit")
        
        if '链路聚合 (Eth-Trunk)' in checked_cards:
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
                    config_commands.append(f"link-aggregation load-balance {lb_algorithm}")
                
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
                        # 格式：Te 0/1 to Te 0/4 或 G 0/1 to G 0/4
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
                                full_interface_type = 'TenGigabitEthernet'
                            
                            # 构建端口范围字符串
                            port_range = f"{interface_num}{start} to {interface_num}{end}"
                            
                            # 配置聚合端口
                            config_commands.append(f"interface Eth-Trunk {agg_id}")
                            config_commands.append(f"port link-type trunk")
                            config_commands.append(f"port trunk allow-pass vlan all")
                            if mode == 'LACP':
                                config_commands.append(f"mode lacp")
                            config_commands.append(f"quit")
                            
                            # 配置成员端口
                            config_commands.append(f"interface {full_interface_type} {port_range}")
                            config_commands.append(f"eth-trunk {agg_id}")
                            config_commands.append(f"quit")
        
        if 'DHCP服务配置' in checked_cards:
            if data.get('dhcp_pool'):
                config_commands.append(f"dhcp enable")
                config_commands.append(f"ip pool {data.get('dhcp_pool')}")
                if data.get('network') and data.get('mask'):
                    config_commands.append(f"network {data.get('network')} mask {data.get('mask')}")
                if data.get('pool_gw'):
                    config_commands.append(f"gateway-list {data.get('pool_gw')}")
                if data.get('pool_start') and data.get('pool_end'):
                    config_commands.append(f"lease day 7 hour 0 minute 0")
                if data.get('exclude_start') and data.get('exclude_end'):
                    config_commands.append(f"excluded-ip-address {data.get('exclude_start')} {data.get('exclude_end')}")
                if data.get('dns1'):
                    config_commands.append(f"dns-list {data.get('dns1')} {data.get('dns2', '')}")
                config_commands.append(f"quit")
        
        if 'DHCP Snooping安全配置' in checked_cards:
            if data.get('trust_port'):
                config_commands.append(f"dhcp snooping enable")
                config_commands.append(f"interface GigabitEthernet {data.get('trust_port')}")
                config_commands.append(f"dhcp snooping trusted")
                config_commands.append(f"quit")
            if data.get('snooping_vlan'):
                config_commands.append(f"vlan {data.get('snooping_vlan')}")
                config_commands.append(f"dhcp snooping enable")
                config_commands.append(f"quit")
        
        if 'MSTP生成树防环配置' in checked_cards:
            config_commands.append(f"stp mode mstp")
            config_commands.append(f"stp region-configuration")
            if data.get('mst_name'):
                config_commands.append(f"region-name {data.get('mst_name')}")
            if data.get('revision'):
                config_commands.append(f"revision-level {data.get('revision')}")
            if data.get('ins1_vlan'):
                config_commands.append(f"instance 1 vlan {data.get('ins1_vlan')}")
            if data.get('ins2_vlan'):
                config_commands.append(f"instance 2 vlan {data.get('ins2_vlan')}")
            config_commands.append(f"active region-configuration")
            if data.get('mst_prio'):
                config_commands.append(f"stp instance 1 priority {data.get('mst_prio')}")
        
        if 'ACL访问控制配置' in checked_cards:
            if data.get('manage_net') and data.get('manage_wild'):
                config_commands.append(f"acl number 2000")
                config_commands.append(f"rule permit source {data.get('manage_net')} {data.get('manage_wild')}")
                config_commands.append(f"quit")
                if data.get('mgmt_vlan'):
                    config_commands.append(f"interface Vlanif {data.get('mgmt_vlan')}")
                    config_commands.append(f"traffic-filter inbound acl 2000")
                    config_commands.append(f"quit")
        
        if 'NTP时钟同步配置' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp server {data.get('ntp_server')}")
        
        if 'SNMPv2c配置' in checked_cards:
            config_commands.append(f"snmp-agent")
            if data.get('snmp_ro_community'):
                config_commands.append(f"snmp-agent community read {data.get('snmp_ro_community')}")
            if data.get('trap_server'):
                trap_community = data.get('trap_community', data.get('snmp_ro_community', 'public'))
                config_commands.append(f"snmp-agent target-host trap address udp-domain {data.get('trap_server')} params securityname {trap_community}")
        
        if '端口镜像配置' in checked_cards:
            if data.get('mirror_src') and data.get('mirror_dst'):
                config_commands.append(f"observe-port 1 interface GigabitEthernet {data.get('mirror_dst')}")
                config_commands.append(f"interface GigabitEthernet {data.get('mirror_src')}")
                config_commands.append(f"port-mirroring to observe-port 1 both")
                config_commands.append(f"quit")
        
        # 生成最终配置
        if config_commands:
            config.append("system-view")
            config.extend(config_commands)
            config.append("quit")
            config.append("save")
        
        self.preview_text.setPlainText('\n'.join(config))
    
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