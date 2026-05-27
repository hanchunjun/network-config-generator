from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QRadioButton, QPushButton)
from PyQt5.QtCore import Qt
from src.ui.config_pages.base_config_page import BaseConfigPage
from src.core.theme_engine import ThemeEngine

class CiscoRouterConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'cisco', 'router')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
        """初始化所有面板和卡片，使用Tab分组"""
        
        # 创建TabWidget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: {t['hover_bg']};
            }
            QTabBar::tab {
                background-color: {t['card_bg']};
                border: 1px solid {t['border']};
                border-bottom: none;
                padding: 10px 24px;
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
        
        card2 = self.create_card('管理地址与网关配置', '📍', '配置管理VLAN、IP地址、子网掩码和默认网关')
        self.add_form_item(card2, '管理VLAN ID', 'mgmt_vlan')
        self.add_form_item(card2, '管理IP', 'mgmt_ip')
        self.add_form_item(card2, '子网掩码', 'subnet_mask')
        self.add_form_item(card2, '默认网关地址', 'gateway')
        
        card3 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录方式及用户名密码')
        self.add_form_item(card3, 'SSH用户名', 'ssh_user')
        self.add_form_item(card3, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card3, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout().addWidget(card1)
        tab1.layout().addWidget(card_console)  # Console 串口登录配置卡片
        tab1.layout().addWidget(card_time)    # 系统时间配置卡片
        tab1.layout().addWidget(card2)
        tab1.layout().addWidget(card3)
        tab1.content_layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：接口配置
        tab2 = self.create_tab_content()
        card4 = self.create_card('物理接口配置', '🔌', '配置物理接口的IP地址、掩码和描述')
        self.add_form_item(card4, '接口名称', 'interface_name')
        self.add_form_item(card4, 'IP地址', 'interface_ip')
        self.add_form_item(card4, '子网掩码', 'interface_mask')
        self.add_form_item(card4, '接口描述', 'interface_desc')
        
        card5 = self.create_card('VLAN接口配置', '🌐', '配置VLAN接口的IP地址和掩码')
        self.add_form_item(card5, 'VLAN ID', 'vlan_id')
        self.add_form_item(card5, 'VLAN名称', 'vlan_name')
        self.add_form_item(card5, 'VLAN IP', 'vlan_ip')
        self.add_form_item(card5, 'VLAN掩码', 'vlan_mask')
        
        card6 = self.create_card('端口聚合配置', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        self.add_form_item(card6, '聚合组ID', 'agg_id')
        self.add_form_item(card6, '聚合端口范围', 'agg_ports')
        self.add_combo_item(card6, '聚合模式', 'agg_mode', ['静态', '动态'])
        
        tab2.layout().addWidget(card4)
        tab2.layout().addWidget(card5)
        tab2.layout().addWidget(card6)
        tab2.content_layout.addStretch()
        tab_widget.addTab(tab2.widget, '🔌 接口配置')
        
        # Tab3：路由配置
        tab3 = self.create_tab_content()
        card7 = self.create_card('OSPF路由配置', '🌐', '配置OSPF路由进程，设置区域和网络')
        self.add_form_item(card7, 'OSPF进程号', 'ospf_process')
        self.add_form_item(card7, '区域ID', 'area_id')
        self.add_form_item(card7, '网络地址', 'network_addr')
        self.add_form_item(card7, '通配符掩码', 'wildcard_mask')
        self.add_form_item(card7, '路由器ID', 'router_id')
        
        card8 = self.create_card('BGP路由配置', '🌐', '配置BGP路由，设置邻居和网络')
        self.add_form_item(card8, 'BGP AS号', 'bgp_as')
        self.add_form_item(card8, '邻居IP', 'peer_ip')
        self.add_form_item(card8, '邻居AS号', 'peer_as')
        self.add_form_item(card8, '发布网络', 'bgp_network')
        
        card9 = self.create_card('静态路由配置', '🌐', '配置静态路由，设置下一跳')
        self.add_form_item(card9, '目标网络', 'static_network')
        self.add_form_item(card9, '子网掩码', 'static_mask')
        self.add_form_item(card9, '下一跳地址', 'next_hop')
        
        tab3.layout().addWidget(card7)
        tab3.layout().addWidget(card8)
        tab3.layout().addWidget(card9)
        tab3.content_layout.addStretch()
        tab_widget.addTab(tab3.widget, '🌐 路由配置')
        
        # Tab4：安全与VPN
        tab4 = self.create_tab_content()
        card10 = self.create_card('NAT地址转换', '🔄', '配置NAT地址转换，实现内网访问外网')
        self.add_form_item(card10, '内部网络', 'inside_network')
        self.add_form_item(card10, '外部接口', 'outside_interface')
        self.add_form_item(card10, '公网IP', 'public_ip')
        
        card11 = self.create_card('VPN配置', '🔒', '配置VPN，实现安全远程访问')
        self.add_form_item(card11, 'VPN名称', 'vpn_name')
        self.add_form_item(card11, '本地网段', 'local_network')
        self.add_form_item(card11, '对端网段', 'remote_network')
        self.add_form_item(card11, '对端IP', 'peer_ip')
        self.add_form_item(card11, '预共享密钥', 'psk_key', is_password=True)
        
        card12 = self.create_card('ACL访问控制', '📜', '配置访问控制列表，限制流量')
        self.add_form_item(card12, 'ACL编号', 'acl_number')
        self.add_form_item(card12, '源地址', 'src_addr')
        self.add_form_item(card12, '目的地址', 'dst_addr')
        
        tab4.layout().addWidget(card10)
        tab4.layout().addWidget(card11)
        tab4.layout().addWidget(card12)
        tab4.content_layout.addStretch()
        tab_widget.addTab(tab4.widget, '🔒 安全与VPN')
        
        # Tab5：运维与监控
        tab5 = self.create_tab_content()
        card13 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器，同步设备时间')
        self.add_form_item(card13, 'NTP服务器', 'ntp_server')
        
        card14 = self.create_card('SNMP监控', '📈', '配置SNMP，实现设备监控')
        self.add_form_item(card14, 'SNMP团体名', 'snmp_community')
        self.add_form_item(card14, 'Trap服务器', 'trap_server')
        
        card15 = self.create_card('QoS配置', '🚀', '配置QoS策略，优化网络性能')
        self.add_form_item(card15, 'QoS策略名称', 'qos_policy')
        self.add_form_item(card15, '带宽限制', 'bandwidth_limit')
        
        tab5.layout().addWidget(card13)
        tab5.layout().addWidget(card14)
        tab5.layout().addWidget(card15)
        tab5.content_layout.addStretch()
        tab_widget.addTab(tab5.widget, '📊 运维与监控')
        
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
            value_label.setStyleSheet(f"color: {self._theme_engine.current_theme['text_main']}; font-size: 10pt;")
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
                config_commands.append(f"hostname {data.get('hostname')}")
            if data.get('enable_password'):
                config_commands.append(f"enable secret {data.get('enable_password')}")
        
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
        
        if '系统时间配置' in checked_cards:
            if data.get('system_time'):
                config_commands.append(f"clock set {data.get('system_time')}")
        
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
        
        if '远程登录配置' in checked_cards:
            if data.get('ssh_user') and data.get('ssh_pwd'):
                config_commands.append(f"hostname {data.get('hostname', 'router')}")
                config_commands.append(f"ip domain-name example.com")
                config_commands.append(f"crypto key generate rsa modulus 1024")
                config_commands.append(f"username {data.get('ssh_user')} privilege 15 secret {data.get('ssh_pwd')}")
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"login local")
                config_commands.append(f"transport input ssh")
                config_commands.append(f"exit")
            if data.get('telnet_pwd'):
                config_commands.append(f"line vty 0 4")
                config_commands.append(f"password {data.get('telnet_pwd')}")
                config_commands.append(f"login")
                config_commands.append(f"transport input telnet")
                config_commands.append(f"exit")
        
        if '物理接口配置' in checked_cards:
            if data.get('interface_name') and data.get('interface_ip'):
                config_commands.append(f"interface {data.get('interface_name')}")
                config_commands.append(f"ip address {data.get('interface_ip')} {data.get('interface_mask', '255.255.255.0')}")
                if data.get('interface_desc'):
                    config_commands.append(f"description {data.get('interface_desc')}")
                config_commands.append(f"no shutdown")
                config_commands.append(f"exit")
        
        if 'VLAN接口配置' in checked_cards:
            if data.get('vlan_id'):
                config_commands.append(f"vlan {data.get('vlan_id')}")
                if data.get('vlan_name'):
                    config_commands.append(f"name {data.get('vlan_name')}")
                config_commands.append(f"exit")
                if data.get('vlan_ip'):
                    config_commands.append(f"interface vlan {data.get('vlan_id')}")
                    config_commands.append(f"ip address {data.get('vlan_ip')} {data.get('vlan_mask', '255.255.255.0')}")
                    config_commands.append(f"exit")
        
        if '端口聚合配置' in checked_cards:
            if data.get('agg_id') and data.get('agg_ports'):
                config_commands.append(f"interface port-channel {data.get('agg_id')}")
                config_commands.append(f"no shutdown")
                if data.get('agg_mode') == '动态':
                    config_commands.append(f"channel-protocol lacp")
                    config_commands.append(f"channel-group {data.get('agg_id')} mode active")
                else:
                    config_commands.append(f"channel-group {data.get('agg_id')} mode on")
                config_commands.append(f"exit")
                config_commands.append(f"interface range {data.get('agg_ports')}")
                if data.get('agg_mode') == '动态':
                    config_commands.append(f"channel-protocol lacp")
                    config_commands.append(f"channel-group {data.get('agg_id')} mode active")
                else:
                    config_commands.append(f"channel-group {data.get('agg_id')} mode on")
                config_commands.append(f"no shutdown")
                config_commands.append(f"exit")
        
        if 'OSPF路由配置' in checked_cards:
            if data.get('ospf_process') and data.get('area_id'):
                config_commands.append(f"router ospf {data.get('ospf_process')}")
                if data.get('router_id'):
                    config_commands.append(f"router-id {data.get('router_id')}")
                if data.get('network_addr') and data.get('wildcard_mask'):
                    config_commands.append(f"network {data.get('network_addr')} {data.get('wildcard_mask')} area {data.get('area_id')}")
                config_commands.append(f"exit")
        
        if 'BGP路由配置' in checked_cards:
            if data.get('bgp_as'):
                config_commands.append(f"router bgp {data.get('bgp_as')}")
                if data.get('peer_ip') and data.get('peer_as'):
                    config_commands.append(f"neighbor {data.get('peer_ip')} remote-as {data.get('peer_as')}")
                if data.get('bgp_network'):
                    config_commands.append(f"network {data.get('bgp_network')}")
                config_commands.append(f"exit")
        
        if '静态路由配置' in checked_cards:
            if data.get('static_network') and data.get('static_mask') and data.get('next_hop'):
                config_commands.append(f"ip route {data.get('static_network')} {data.get('static_mask')} {data.get('next_hop')}")
        
        if 'NAT地址转换' in checked_cards:
            if data.get('inside_network') and data.get('outside_interface'):
                config_commands.append(f"access-list 100 permit ip {data.get('inside_network')} 0.0.0.255 any")
                config_commands.append(f"interface {data.get('outside_interface')}")
                config_commands.append(f"ip nat outside")
                config_commands.append(f"exit")
                config_commands.append(f"interface vlan 1")
                config_commands.append(f"ip nat inside")
                config_commands.append(f"exit")
                config_commands.append(f"ip nat inside source list 100 interface {data.get('outside_interface')} overload")
        
        if 'VPN配置' in checked_cards:
            if data.get('vpn_name') and data.get('local_network') and data.get('remote_network') and data.get('peer_ip') and data.get('psk_key'):
                config_commands.append(f"crypto isakmp policy 10")
                config_commands.append(f"encr aes")
                config_commands.append(f"hash sha")
                config_commands.append(f"authentication pre-share")
                config_commands.append(f"group 2")
                config_commands.append(f"exit")
                config_commands.append(f"crypto isakmp key {data.get('psk_key')} address {data.get('peer_ip')}")
                config_commands.append(f"crypto ipsec transform-set myset esp-aes esp-sha-hmac")
                config_commands.append(f"exit")
                config_commands.append(f"access-list 101 permit ip {data.get('local_network')} 0.0.0.255 {data.get('remote_network')} 0.0.0.255")
                config_commands.append(f"crypto map mymap 10 ipsec-isakmp")
                config_commands.append(f"set peer {data.get('peer_ip')}")
                config_commands.append(f"set transform-set myset")
                config_commands.append(f"match address 101")
                config_commands.append(f"exit")
        
        if 'ACL访问控制' in checked_cards:
            if data.get('acl_number'):
                config_commands.append(f"access-list {data.get('acl_number')} permit ip any any")
        
        if 'NTP时钟同步' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp server {data.get('ntp_server')}")
        
        if 'SNMP监控' in checked_cards:
            config_commands.append(f"snmp-server community {data.get('snmp_community', 'public')} RO")
            if data.get('trap_server'):
                config_commands.append(f"snmp-server host {data.get('trap_server')} {data.get('snmp_community', 'public')}")
        
        if 'QoS配置' in checked_cards:
            if data.get('qos_policy'):
                config_commands.append(f"class-map {data.get('qos_policy')}")
                config_commands.append(f"match any")
                config_commands.append(f"exit")
                config_commands.append(f"policy-map {data.get('qos_policy')}")
                config_commands.append(f"class {data.get('qos_policy')}")
                if data.get('bandwidth_limit'):
                    config_commands.append(f"police {data.get('bandwidth_limit')} conform-action transmit exceed-action drop")
                config_commands.append(f"exit")
        
        # 生成最终配置
        if config_commands:
            config.append("enable")
            config.append("configure terminal")
            config.extend(config_commands)
            config.append("exit")
            config.append("exit")
            config.append("write memory")
        
        self.preview_text.setPlainText('\n'.join(config))
    
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