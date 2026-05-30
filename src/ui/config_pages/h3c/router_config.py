from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QRadioButton, QPushButton, QButtonGroup)
from PyQt5.QtCore import Qt
from src.ui.config_pages.base_config_page import BaseConfigPage
from src.core.theme_engine import ThemeEngine

class H3CRouterConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'h3c', 'router')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
        """初始化所有面板和卡片，使用Tab分组"""
        
        # 创建TabWidget
        tab_widget = QTabWidget()
        t = self._theme_engine.current_theme
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {
                border: none;
                background-color: {t['hover_bg']};
            }
            QTabBar::tab {
                background-color: {t['card_bg']};
                border: 1px solid {t['border']};
                border-bottom: none;
                padding: 6px 24px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 10pt;
                color: {t['text_secondary']};
            }
            QTabBar::tab:selected {
                background-color: {t['page_bg']};
                color: {t['card_bg']};
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: {t['hover_bg']};
            }
        """)
        
        # Tab1：基础配置
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码和系统时间')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable特权密码', 'enable_password', is_password=True)
        self.add_form_item(card1, '系统时间', 'system_time')
        
        # Console 串口登录配置卡片
        card_console = self.create_card('Console 串口登录配置', '🔐', '配置Console串口登录方式和密码')
        
        # 登录方式选择
        login_mode_layout = QHBoxLayout()
        login_mode_layout.setSpacing(4)
        
        label = QLabel('登录方式:')
        label.setFixedWidth(140)
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
        pwd_layout.setSpacing(4)
        
        label = QLabel('console密码:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        pwd_layout.addWidget(label)
        
        console_pwd_input = QLineEdit()
        console_pwd_input.setEchoMode(QLineEdit.Password)
        console_pwd_input.setPlaceholderText('请输入密码')
        console_pwd_input.setStyleSheet(self._get_input_style())
        pwd_layout.addWidget(console_pwd_input)
        self.form_fields['console_password'] = console_pwd_input
        
        pwd_layout.addStretch()
        card_console.layout().addLayout(pwd_layout)
        
        # 用户名和密码输入
        user_pwd_layout = QHBoxLayout()
        user_pwd_layout.setSpacing(4)
        
        label = QLabel('用户名:')
        label.setFixedWidth(140)
        label.setStyleSheet(self._get_label_secondary_style())
        user_pwd_layout.addWidget(label)
        
        user_input = QLineEdit()
        user_input.setPlaceholderText('请输入用户名')
        user_input.setStyleSheet(self._get_input_style())
        user_pwd_layout.addWidget(user_input)
        self.form_fields['console_username'] = user_input
        
        label = QLabel('密码:')
        label.setFixedWidth(72)
        label.setStyleSheet(self._get_label_secondary_style())
        user_pwd_layout.addWidget(label)
        
        user_pwd_input = QLineEdit()
        user_pwd_input.setEchoMode(QLineEdit.Password)
        user_pwd_input.setPlaceholderText('请输入密码')
        user_pwd_input.setStyleSheet(self._get_input_style())
        user_pwd_layout.addWidget(user_pwd_input)
        self.form_fields['console_user_password'] = user_pwd_input
        
        user_pwd_layout.addStretch()
        card_console.layout().addLayout(user_pwd_layout)
        
        # 系统时间配置卡片
        card_time = self.create_card('系统时间配置', '🕒', '配置设备系统时间')
        self.add_form_item(card_time, '系统时间', 'system_time')
        
        card2 = self.create_card('接口IP地址配置', '🌐', '配置各接口IP地址')
        self.add_form_item(card2, '接口1', 'interface1')
        self.add_form_item(card2, 'IP地址1', 'ip1')
        self.add_form_item(card2, '子网掩码1', 'mask1')
        self.add_form_item(card2, '接口2', 'interface2')
        self.add_form_item(card2, 'IP地址2', 'ip2')
        self.add_form_item(card2, '子网掩码2', 'mask2')
        
        card3 = self.create_card('管理地址与网关配置', '📍', '配置管理VLAN、IP地址、子网掩码和默认网关')
        self.add_form_item(card3, '管理VLAN ID', 'mgmt_vlan')
        self.add_form_item(card3, '管理IP', 'mgmt_ip')
        self.add_form_item(card3, '子网掩码', 'subnet_mask')
        self.add_form_item(card3, '默认网关地址', 'gateway')
        
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
        tab1.layout().addWidget(card2)
        tab1.layout().addWidget(card3)
        tab1.layout().addWidget(card_ssh)  # SSH登录配置卡片
        tab1.layout().addWidget(card_telnet)  # Telnet登录配置卡片
        tab1.content_layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：路由配置
        tab2 = self.create_tab_content()
        card5 = self.create_card('OSPF路由配置', '🌐', '配置OSPF路由进程、区域、网络宣告')
        self.add_form_item(card5, 'OSPF进程号', 'ospf_process')
        self.add_form_item(card5, '区域号', 'area_id')
        self.add_form_item(card5, '路由ID', 'router_id')
        self.add_form_item(card5, '网络地址', 'network_addr')
        self.add_form_item(card5, '子网掩码', 'network_mask')
        
        card6 = self.create_card('BGP路由配置', '🌐', '配置BGP路由进程、对等体、网络宣告')
        self.add_form_item(card6, 'BGP AS号', 'bgp_as')
        self.add_form_item(card6, '对等体IP', 'peer_ip')
        self.add_form_item(card6, '对等体AS号', 'peer_as')
        self.add_form_item(card6, '网络地址', 'bgp_network')
        self.add_form_item(card6, '子网掩码', 'bgp_mask')
        
        card7 = self.create_card('静态路由配置', '🌐', '配置静态路由')
        self.add_form_item(card7, '目标网络', 'static_network')
        self.add_form_item(card7, '子网掩码', 'static_mask')
        self.add_form_item(card7, '下一跳地址', 'next_hop')
        
        tab2.layout().addWidget(card5)
        tab2.layout().addWidget(card6)
        tab2.layout().addWidget(card7)
        tab2.content_layout.addStretch()
        tab_widget.addTab(tab2.widget, '🌐 路由配置')
        
        # Tab3：安全与监控
        tab3 = self.create_tab_content()
        card8 = self.create_card('ACL访问控制列表', '📜', '配置访问控制列表，限制访问管理VLAN的来源')
        self.add_form_item(card8, '允许管理网段', 'allow_segment')
        self.add_form_item(card8, '允许主机', 'allow_host')
        self.add_form_item(card8, '拒绝网段1', 'deny_segment1')
        self.add_form_item(card8, '拒绝网段2', 'deny_segment2')
        
        card9 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器，自动同步设备时钟')
        self.add_form_item(card9, 'NTP服务器地址', 'ntp_server')
        
        card10 = self.create_card('SNMPv2配置', '📈', '开启SNMP功能，配置团体名和Trap告警服务器')
        self.add_form_item(card10, 'SNMP只读团体名', 'snmp_community')
        self.add_form_item(card10, 'Trap服务器地址', 'trap_server')
        
        card11 = self.create_card('AAA本地认证配置', '🔐', '配置AAA本地认证，统一管理登录用户')
        self.add_form_item(card11, 'AAA用户名', 'aaa_user')
        self.add_form_item(card11, 'AAA密码', 'aaa_pwd', is_password=True)
        
        tab3.layout().addWidget(card8)
        tab3.layout().addWidget(card9)
        tab3.layout().addWidget(card10)
        tab3.layout().addWidget(card11)
        tab3.content_layout.addStretch()
        tab_widget.addTab(tab3.widget, '🔒 安全与监控')
        
        # Tab4：NAT与VPN
        tab4 = self.create_tab_content()
        card12 = self.create_card('NAT地址转换', '🌐', '配置NAT地址转换')
        self.add_form_item(card12, '内网网段', 'inside_network')
        self.add_form_item(card12, '外网接口', 'outside_interface')
        self.add_form_item(card12, '公网IP', 'public_ip')
        
        card13 = self.create_card('VPN配置', '🔐', '配置VPN')
        self.add_form_item(card13, 'VPN名称', 'vpn_name')
        self.add_form_item(card13, 'VPN密码', 'vpn_password', is_password=True)
        self.add_form_item(card13, '对等体IP', 'vpn_peer_ip')
        
        tab4.layout().addWidget(card12)
        tab4.layout().addWidget(card13)
        tab4.content_layout.addStretch()
        tab_widget.addTab(tab4.widget, '🌐 NAT与VPN')
        
        # 将TabWidget添加到左侧布局
        self.config_layout.addWidget(tab_widget)
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
            value_label.setStyleSheet(f"color: {self._theme_engine.current_theme['text_main']}; font-size: 10pt;")
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
            input_field.setStyleSheet(self._get_input_style())
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
                config_commands.append(f"sysname {data.get('hostname')}")
            if data.get('enable_password'):
                config_commands.append(f"super password level 3 hash {data.get('enable_password')}")
        
        if 'Console 串口登录配置' in checked_cards:
            if data.get('console_password'):
                config_commands.append(f"line console 0")
                config_commands.append(f"password {data.get('console_password')}")
                config_commands.append(f"login")
                config_commands.append(f"quit")
            elif data.get('console_username') and data.get('console_user_password'):
                config_commands.append(f"local-user {data.get('console_username')} class manage")
                config_commands.append(f"password hash {data.get('console_user_password')}")
                config_commands.append(f"service-type terminal")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
                config_commands.append(f"line console 0")
                config_commands.append(f"authentication-mode scheme")
                config_commands.append(f"quit")
        
        if '系统时间配置' in checked_cards:
            if data.get('system_time'):
                config_commands.append(f"clock datetime {data.get('system_time')}")
                config_commands.append(f"clock timezone beijing 8")
        
        if '接口IP地址配置' in checked_cards:
            if data.get('interface1') and data.get('ip1'):
                config_commands.append(f"interface {data.get('interface1')}")
                config_commands.append(f"ip address {data.get('ip1')} {data.get('mask1', '255.255.255.0')}")
                config_commands.append(f"undo shutdown")
                config_commands.append(f"quit")
            if data.get('interface2') and data.get('ip2'):
                config_commands.append(f"interface {data.get('interface2')}")
                config_commands.append(f"ip address {data.get('ip2')} {data.get('mask2', '255.255.255.0')}")
                config_commands.append(f"undo shutdown")
                config_commands.append(f"quit")
        
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
        
        if 'SSH登录配置' in checked_cards:
            if data.get('ssh_username') and data.get('ssh_user_password'):
                config_commands.append(f"ssh server enable")
                config_commands.append(f"local-user {data.get('ssh_username')}")
                config_commands.append(f"password simple {data.get('ssh_user_password')}")
                config_commands.append(f"service-type ssh")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"authentication-mode scheme")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
            elif data.get('ssh_password'):
                config_commands.append(f"ssh server enable")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"password {data.get('ssh_password')}")
                config_commands.append(f"login")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
        
        if 'Telnet登录配置' in checked_cards:
            if data.get('telnet_username') and data.get('telnet_user_password'):
                config_commands.append(f"local-user {data.get('telnet_username')}")
                config_commands.append(f"password simple {data.get('telnet_user_password')}")
                config_commands.append(f"service-type telnet")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
                config_commands.append(f"line vty 5 9")
                config_commands.append(f"authentication-mode scheme")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
            elif data.get('telnet_pwd'):
                config_commands.append(f"line vty 5 9")
                config_commands.append(f"password {data.get('telnet_pwd')}")
                config_commands.append(f"login")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
        
        if 'OSPF路由配置' in checked_cards:
            if data.get('ospf_process') and data.get('area_id'):
                config_commands.append(f"ospf {data.get('ospf_process')}")
                if data.get('router_id'):
                    config_commands.append(f"router-id {data.get('router_id')}")
                config_commands.append(f"area {data.get('area_id')}")
                if data.get('network_addr') and data.get('network_mask'):
                    config_commands.append(f"network {data.get('network_addr')} {data.get('network_mask')}")
                config_commands.append(f"quit")
        
        if 'BGP路由配置' in checked_cards:
            if data.get('bgp_as'):
                config_commands.append(f"bgp {data.get('bgp_as')}")
                if data.get('peer_ip') and data.get('peer_as'):
                    config_commands.append(f"peer {data.get('peer_ip')} as-number {data.get('peer_as')}")
                if data.get('bgp_network') and data.get('bgp_mask'):
                    config_commands.append(f"network {data.get('bgp_network')} {data.get('bgp_mask')}")
                config_commands.append(f"quit")
        
        if '静态路由配置' in checked_cards:
            if data.get('static_network') and data.get('static_mask') and data.get('next_hop'):
                config_commands.append(f"ip route-static {data.get('static_network')} {data.get('static_mask')} {data.get('next_hop')}")
        
        if 'ACL访问控制列表' in checked_cards:
            if data.get('allow_segment'):
                config_commands.append(f"acl number 2000")
                config_commands.append(f"rule permit source {data.get('allow_segment')} 0.0.0.255")
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
        
        if 'AAA本地认证配置' in checked_cards:
            if data.get('aaa_user') and data.get('aaa_pwd'):
                config_commands.append(f"local-user {data.get('aaa_user')}")
                config_commands.append(f"password simple {data.get('aaa_pwd')}")
                config_commands.append(f"service-type terminal ssh telnet")
                config_commands.append(f"authorization-attribute level 3")
                config_commands.append(f"quit")
        
        if 'NAT地址转换' in checked_cards:
            if data.get('inside_network') and data.get('outside_interface'):
                config_commands.append(f"acl number 2000")
                config_commands.append(f"rule permit source {data.get('inside_network')} 0.0.0.255")
                config_commands.append(f"quit")
                config_commands.append(f"interface {data.get('outside_interface')}")
                config_commands.append(f"nat outbound 2000")
                if data.get('public_ip'):
                    config_commands.append(f"nat server global {data.get('public_ip')} inside {data.get('inside_network')}")
                config_commands.append(f"quit")
        
        if 'VPN配置' in checked_cards:
            if data.get('vpn_name') and data.get('vpn_peer_ip'):
                config_commands.append(f"ike peer {data.get('vpn_name')}")
                config_commands.append(f"pre-shared-key {data.get('vpn_password', 'password')}")
                config_commands.append(f"remote-address {data.get('vpn_peer_ip')}")
                config_commands.append(f"quit")
        
        # 生成最终配置
        if config_commands:
            config.extend(config_commands)
            config.append("save force")
        
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