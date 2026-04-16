from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class HuaweiRouterConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'huawei', 'router')
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
        
        # Tab1：基础管理配置
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、特权密码')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, 'enable加密密码', 'enable_secret', is_password=True)
        
        card2 = self.create_card('本地登录配置', '🔐', '配置Console登录密码和系统时钟')
        self.add_form_item(card2, 'Console登录密码', 'console_pwd', is_password=True)
        self.add_form_item(card2, '系统时间', 'system_time')
        
        card3 = self.create_card('远程登录配置', '🌐', '配置SSH和Telnet远程登录')
        self.add_form_item(card3, 'SSH用户名', 'ssh_user')
        self.add_form_item(card3, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card3, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础管理')
        
        # Tab2：接口配置
        tab2 = self.create_tab_content()
        card4 = self.create_card('物理接口配置', '🔌', '配置物理接口IP地址和描述')
        self.add_form_item(card4, '接口名称', 'interface_name')
        self.add_form_item(card4, 'IP地址', 'interface_ip')
        self.add_form_item(card4, '子网掩码', 'interface_mask')
        self.add_form_item(card4, '接口描述', 'interface_desc')
        
        card5 = self.create_card('Loopback接口配置', '🔄', '配置Loopback接口作为路由器ID')
        self.add_form_item(card5, 'Loopback接口号', 'loopback_id')
        self.add_form_item(card5, 'IP地址', 'loopback_ip')
        self.add_form_item(card5, '子网掩码', 'loopback_mask')
        
        card6 = self.create_card('VLAN接口配置', '🌐', '配置VLAN接口和IP地址')
        self.add_form_item(card6, 'VLAN ID', 'vlan_id')
        self.add_form_item(card6, 'VLAN名称', 'vlan_name')
        self.add_form_item(card6, 'IP地址', 'vlan_ip')
        self.add_form_item(card6, '子网掩码', 'vlan_mask')
        
        tab2.layout.addWidget(card4)
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addStretch()
        tab_widget.addTab(tab2.widget, '🔌 接口配置')
        
        # Tab3：路由配置
        tab3 = self.create_tab_content()
        card7 = self.create_card('静态路由配置', '🛣️', '配置静态路由和默认路由')
        self.add_form_item(card7, '目标网段', 'static_dest')
        self.add_form_item(card7, '子网掩码', 'static_mask')
        self.add_form_item(card7, '下一跳地址', 'next_hop')
        self.add_form_item(card7, '默认网关', 'default_gateway')
        
        card8 = self.create_card('OSPF路由配置', '🌐', '配置OSPF动态路由协议')
        self.add_form_item(card8, 'OSPF进程号', 'ospf_process')
        self.add_form_item(card8, '区域ID', 'area_id')
        self.add_form_item(card8, '网络地址', 'network_addr')
        self.add_form_item(card8, '反掩码', 'wildcard_mask')
        self.add_form_item(card8, '路由器ID', 'router_id')
        
        card9 = self.create_card('BGP路由配置', '🌍', '配置BGP边界网关协议')
        self.add_form_item(card9, 'BGP AS号', 'bgp_as')
        self.add_form_item(card9, '对等体IP', 'peer_ip')
        self.add_form_item(card9, '对等体AS号', 'peer_as')
        self.add_form_item(card9, '网络地址', 'bgp_network')
        self.add_form_item(card9, '子网掩码', 'bgp_mask')
        
        tab3.layout.addWidget(card7)
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addStretch()
        tab_widget.addTab(tab3.widget, '🌐 路由配置')
        
        # Tab4：安全配置
        tab4 = self.create_tab_content()
        card10 = self.create_card('ACL访问控制配置', '📜', '配置访问控制列表')
        self.add_form_item(card10, 'ACL编号', 'acl_number')
        self.add_form_item(card10, '源地址', 'src_addr')
        self.add_form_item(card10, '源反掩码', 'src_wild')
        self.add_form_item(card10, '目的地址', 'dst_addr')
        self.add_form_item(card10, '目的反掩码', 'dst_wild')
        self.add_form_item(card10, '协议', 'protocol')
        self.add_form_item(card10, '端口号', 'port')
        
        card11 = self.create_card('NAT地址转换配置', '🔄', '配置NAT地址转换')
        self.add_form_item(card11, '内部网段', 'inside_network')
        self.add_form_item(card11, '内部掩码', 'inside_mask')
        self.add_form_item(card11, '外部接口', 'outside_interface')
        self.add_form_item(card11, '外部IP地址', 'outside_ip')
        
        card12 = self.create_card('防火墙区域配置', '🛡️', '配置防火墙安全区域')
        self.add_form_item(card12, '内部区域接口', 'inside_interface')
        self.add_form_item(card12, '外部区域接口', 'outside_interface_fw')
        
        tab4.layout.addWidget(card10)
        tab4.layout.addWidget(card11)
        tab4.layout.addWidget(card12)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '🔒 安全配置')
        
        # Tab5：服务与监控
        tab5 = self.create_tab_content()
        card13 = self.create_card('DHCP服务配置', '📶', '配置DHCP服务器')
        self.add_form_item(card13, 'DHCP池名称', 'dhcp_pool')
        self.add_form_item(card13, '网络地址', 'dhcp_network')
        self.add_form_item(card13, '子网掩码', 'dhcp_mask')
        self.add_form_item(card13, '网关地址', 'dhcp_gw')
        self.add_form_item(card13, '地址池起始', 'dhcp_start')
        self.add_form_item(card13, '地址池结束', 'dhcp_end')
        self.add_form_item(card13, 'DNS服务器', 'dhcp_dns')
        
        card14 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器')
        self.add_form_item(card14, 'NTP服务器地址', 'ntp_server')
        
        card15 = self.create_card('SNMP监控配置', '📈', '配置SNMP监控')
        self.add_form_item(card15, 'SNMP团体名', 'snmp_community')
        self.add_form_item(card15, 'Trap服务器', 'trap_server')
        
        card16 = self.create_card('QoS服务质量', '🚀', '配置QoS策略')
        self.add_form_item(card16, '接口', 'qos_interface')
        self.add_form_item(card16, '带宽限制', 'bandwidth_limit')
        
        tab5.layout.addWidget(card13)
        tab5.layout.addWidget(card14)
        tab5.layout.addWidget(card15)
        tab5.layout.addWidget(card16)
        tab5.layout.addStretch()
        tab_widget.addTab(tab5.widget, '📊 服务与监控')
        
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
            if data.get('enable_secret'):
                config_commands.append(f"aaa")
                config_commands.append(f"local-user admin password irreversible-cipher {data.get('enable_secret')}")
                config_commands.append(f"local-user admin privilege level 15")
                config_commands.append(f"local-user admin service-type terminal ssh telnet")
                config_commands.append(f"quit")
        
        if '本地登录配置' in checked_cards:
            if data.get('console_pwd'):
                config_commands.append(f"user-interface console 0")
                config_commands.append(f"authentication-mode password")
                config_commands.append(f"set authentication password cipher {data.get('console_pwd')}")
                config_commands.append(f"quit")
            if data.get('system_time'):
                config_commands.append(f"clock datetime {data.get('system_time')}")
                config_commands.append(f"clock timezone beijing add 08:00:00")
        
        if '远程登录配置' in checked_cards:
            if data.get('ssh_user') and data.get('ssh_pwd'):
                config_commands.append(f"stelnet server enable")
                config_commands.append(f"ssh user {data.get('ssh_user')} authentication-type password")
                config_commands.append(f"ssh user {data.get('ssh_user')} service-type stelnet")
                config_commands.append(f"aaa")
                config_commands.append(f"local-user {data.get('ssh_user')} password irreversible-cipher {data.get('ssh_pwd')}")
                config_commands.append(f"local-user {data.get('ssh_user')} privilege level 15")
                config_commands.append(f"local-user {data.get('ssh_user')} service-type terminal ssh")
                config_commands.append(f"quit")
                config_commands.append(f"user-interface vty 0 4")
                config_commands.append(f"authentication-mode aaa")
                config_commands.append(f"protocol inbound ssh")
                config_commands.append(f"quit")
            if data.get('telnet_pwd'):
                config_commands.append(f"user-interface vty 0 4")
                config_commands.append(f"authentication-mode password")
                config_commands.append(f"set authentication password cipher {data.get('telnet_pwd')}")
                config_commands.append(f"protocol inbound telnet")
                config_commands.append(f"quit")
        
        if '物理接口配置' in checked_cards:
            if data.get('interface_name') and data.get('interface_ip'):
                config_commands.append(f"interface {data.get('interface_name')}")
                config_commands.append(f"ip address {data.get('interface_ip')} {data.get('interface_mask', '255.255.255.0')}")
                if data.get('interface_desc'):
                    config_commands.append(f"description {data.get('interface_desc')}")
                config_commands.append(f"undo shutdown")
                config_commands.append(f"quit")
        
        if 'Loopback接口配置' in checked_cards:
            if data.get('loopback_id') and data.get('loopback_ip'):
                config_commands.append(f"interface LoopBack {data.get('loopback_id')}")
                config_commands.append(f"ip address {data.get('loopback_ip')} {data.get('loopback_mask', '255.255.255.255')}")
                config_commands.append(f"quit")
        
        if 'VLAN接口配置' in checked_cards:
            if data.get('vlan_id'):
                config_commands.append(f"vlan {data.get('vlan_id')}")
                if data.get('vlan_name'):
                    config_commands.append(f"description {data.get('vlan_name')}")
                config_commands.append(f"quit")
                if data.get('vlan_ip'):
                    config_commands.append(f"interface Vlanif {data.get('vlan_id')}")
                    config_commands.append(f"ip address {data.get('vlan_ip')} {data.get('vlan_mask', '255.255.255.0')}")
                    config_commands.append(f"quit")
        
        if '静态路由配置' in checked_cards:
            if data.get('static_dest') and data.get('static_mask') and data.get('next_hop'):
                config_commands.append(f"ip route-static {data.get('static_dest')} {data.get('static_mask')} {data.get('next_hop')}")
            if data.get('default_gateway'):
                config_commands.append(f"ip route-static 0.0.0.0 0.0.0.0 {data.get('default_gateway')}")
        
        if 'OSPF路由配置' in checked_cards:
            if data.get('ospf_process') and data.get('area_id'):
                config_commands.append(f"ospf {data.get('ospf_process')}")
                if data.get('router_id'):
                    config_commands.append(f"router-id {data.get('router_id')}")
                config_commands.append(f"area {data.get('area_id')}")
                if data.get('network_addr') and data.get('wildcard_mask'):
                    config_commands.append(f"network {data.get('network_addr')} {data.get('wildcard_mask')}")
                config_commands.append(f"quit")
        
        if 'BGP路由配置' in checked_cards:
            if data.get('bgp_as'):
                config_commands.append(f"bgp {data.get('bgp_as')}")
                if data.get('peer_ip') and data.get('peer_as'):
                    config_commands.append(f"peer {data.get('peer_ip')} as-number {data.get('peer_as')}")
                if data.get('bgp_network') and data.get('bgp_mask'):
                    config_commands.append(f"network {data.get('bgp_network')} {data.get('bgp_mask')}")
                config_commands.append(f"quit")
        
        if 'ACL访问控制配置' in checked_cards:
            if data.get('acl_number'):
                config_commands.append(f"acl number {data.get('acl_number')}")
                if data.get('src_addr') and data.get('src_wild'):
                    config_commands.append(f"rule permit {data.get('protocol', 'ip')} source {data.get('src_addr')} {data.get('src_wild')}")
                config_commands.append(f"quit")
        
        if 'NAT地址转换配置' in checked_cards:
            if data.get('inside_network') and data.get('inside_mask') and data.get('outside_interface'):
                config_commands.append(f"acl number 2000")
                config_commands.append(f"rule permit source {data.get('inside_network')} {data.get('inside_mask')}")
                config_commands.append(f"quit")
                config_commands.append(f"interface {data.get('outside_interface')}")
                config_commands.append(f"nat outbound 2000")
                if data.get('outside_ip'):
                    config_commands.append(f"ip address {data.get('outside_ip')} 255.255.255.0")
                config_commands.append(f"quit")
        
        if '防火墙区域配置' in checked_cards:
            if data.get('inside_interface'):
                config_commands.append(f"firewall zone trust")
                config_commands.append(f"add interface {data.get('inside_interface')}")
                config_commands.append(f"quit")
            if data.get('outside_interface_fw'):
                config_commands.append(f"firewall zone untrust")
                config_commands.append(f"add interface {data.get('outside_interface_fw')}")
                config_commands.append(f"quit")
        
        if 'DHCP服务配置' in checked_cards:
            if data.get('dhcp_pool'):
                config_commands.append(f"dhcp enable")
                config_commands.append(f"ip pool {data.get('dhcp_pool')}")
                if data.get('dhcp_network') and data.get('dhcp_mask'):
                    config_commands.append(f"network {data.get('dhcp_network')} mask {data.get('dhcp_mask')}")
                if data.get('dhcp_gw'):
                    config_commands.append(f"gateway-list {data.get('dhcp_gw')}")
                if data.get('dhcp_start') and data.get('dhcp_end'):
                    config_commands.append(f"lease day 7 hour 0 minute 0")
                if data.get('dhcp_dns'):
                    config_commands.append(f"dns-list {data.get('dhcp_dns')}")
                config_commands.append(f"quit")
        
        if 'NTP时钟同步' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp server {data.get('ntp_server')}")
        
        if 'SNMP监控配置' in checked_cards:
            config_commands.append(f"snmp-agent")
            if data.get('snmp_community'):
                config_commands.append(f"snmp-agent community read {data.get('snmp_community')}")
            if data.get('trap_server'):
                config_commands.append(f"snmp-agent target-host trap address udp-domain {data.get('trap_server')} params securityname {data.get('snmp_community', 'public')}")
        
        if 'QoS服务质量' in checked_cards:
            if data.get('qos_interface') and data.get('bandwidth_limit'):
                config_commands.append(f"interface {data.get('qos_interface')}")
                config_commands.append(f"qos lr outbound cir {data.get('bandwidth_limit')}")
                config_commands.append(f"quit")
        
        # 生成最终配置
        if config_commands:
            config.append("system-view")
            config.extend(config_commands)
            config.append("quit")
            config.append("save")
        
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