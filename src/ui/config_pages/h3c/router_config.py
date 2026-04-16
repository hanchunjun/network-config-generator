from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

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
        tab_widget.setStyleSheet("""
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
        
        card4 = self.create_tab_content()
        card4 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录方式及用户名密码')
        self.add_form_item(card4, 'SSH用户名', 'ssh_user')
        self.add_form_item(card4, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card4, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addWidget(card4)
        tab1.layout.addStretch()
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
        
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addWidget(card7)
        tab2.layout.addStretch()
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
        
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addWidget(card10)
        tab3.layout.addWidget(card11)
        tab3.layout.addStretch()
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
        
        tab4.layout.addWidget(card12)
        tab4.layout.addWidget(card13)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '🌐 NAT与VPN')
        
        # 将TabWidget添加到左侧布局
        self.left_layout.addWidget(tab_widget)
        
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
    
    def reset_form(self):
        """重置表单（覆盖基类方法）"""
        self.reset_all_fields()
        self.code_editor.clear()