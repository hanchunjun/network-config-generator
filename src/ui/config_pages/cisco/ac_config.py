from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class CiscoACConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'cisco', 'ac')
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
        
        card2 = self.create_card('管理地址与网关配置', '📍', '配置管理VLAN、IP地址、子网掩码和默认网关')
        self.add_form_item(card2, '管理VLAN ID', 'mgmt_vlan')
        self.add_form_item(card2, '管理IP', 'mgmt_ip')
        self.add_form_item(card2, '子网掩码', 'subnet_mask')
        self.add_form_item(card2, '默认网关地址', 'gateway')
        
        card3 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录方式及用户名密码')
        self.add_form_item(card3, 'SSH用户名', 'ssh_user')
        self.add_form_item(card3, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card3, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：WLAN配置
        tab2 = self.create_tab_content()
        card4 = self.create_card('WLAN基本配置', '📶', '配置WLAN基本参数')
        self.add_form_item(card4, 'SSID名称', 'ssid_name')
        self.add_form_item(card4, 'WLAN ID', 'wlan_id')
        self.add_form_item(card4, '安全模板', 'security_template')
        self.add_form_item(card4, '服务模板', 'service_template')
        
        card5 = self.create_card('安全策略配置', '🔒', '配置WLAN安全策略')
        self.add_form_item(card5, '认证方式', 'auth_method')
        self.add_form_item(card5, 'PSK密码', 'psk_password', is_password=True)
        self.add_form_item(card5, 'Radius服务器', 'radius_server')
        self.add_form_item(card5, 'Radius密钥', 'radius_key', is_password=True)
        
        card6 = self.create_card('VAP配置', '🌐', '配置VAP虚拟接入点')
        self.add_form_item(card6, 'VAP名称', 'vap_name')
        self.add_form_item(card6, 'VAP ID', 'vap_id')
        self.add_form_item(card6, '绑定WLAN', 'bind_wlan')
        self.add_form_item(card6, '业务VLAN', 'service_vlan')
        
        tab2.layout.addWidget(card4)
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addStretch()
        tab_widget.addTab(tab2.widget, '📶 WLAN配置')
        
        # Tab3：AP管理
        tab3 = self.create_tab_content()
        card7 = self.create_card('AP基础配置', '📱', '配置AP基本信息')
        self.add_form_item(card7, 'AP名称', 'ap_name')
        self.add_form_item(card7, 'AP MAC地址', 'ap_mac')
        self.add_form_item(card7, 'AP型号', 'ap_model')
        
        card8 = self.create_card('AP分组配置', '📦', '配置AP分组')
        self.add_form_item(card8, '分组名称', 'group_name')
        self.add_form_item(card8, '分组描述', 'group_desc')
        
        card9 = self.create_card('AP模板配置', '📋', '配置AP模板')
        self.add_form_item(card9, '模板名称', 'template_name')
        self.add_form_item(card9, '模板类型', 'template_type')
        
        tab3.layout.addWidget(card7)
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addStretch()
        tab_widget.addTab(tab3.widget, '📱 AP管理')
        
        # Tab4：接口与链路
        tab4 = self.create_tab_content()
        card10 = self.create_card('上行接口配置', '🔌', '配置AC上行接口')
        self.add_form_item(card10, '上行接口', 'uplink_interface')
        self.add_form_item(card10, 'IP地址', 'uplink_ip')
        self.add_form_item(card10, '子网掩码', 'uplink_mask')
        
        card11 = self.create_card('CAPWAP隧道配置', '🌐', '配置CAPWAP隧道参数')
        self.add_form_item(card11, 'AC源地址', 'ac_source_ip')
        self.add_form_item(card11, 'CAPWAP端口', 'capwap_port')
        
        card12 = self.create_card('链路聚合配置', '🔗', '配置链路聚合')
        self.add_form_item(card12, '聚合端口', 'agg_ports')
        self.add_form_item(card12, '聚合组ID', 'agg_id')
        
        tab4.layout.addWidget(card10)
        tab4.layout.addWidget(card11)
        tab4.layout.addWidget(card12)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '🔌 接口与链路')
        
        # Tab5：安全与监控
        tab5 = self.create_tab_content()
        card13 = self.create_card('ACL访问控制', '📜', '配置访问控制列表')
        self.add_form_item(card13, 'ACL编号', 'acl_number')
        self.add_form_item(card13, '源地址', 'src_addr')
        self.add_form_item(card13, '目的地址', 'dst_addr')
        
        card14 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器')
        self.add_form_item(card14, 'NTP服务器', 'ntp_server')
        
        card15 = self.create_card('SNMP监控', '📈', '配置SNMP监控')
        self.add_form_item(card15, 'SNMP团体名', 'snmp_community')
        self.add_form_item(card15, 'Trap服务器', 'trap_server')
        
        card16 = self.create_card('QoS配置', '🚀', '配置QoS策略')
        self.add_form_item(card16, 'QoS模板', 'qos_template')
        self.add_form_item(card16, '带宽限制', 'bandwidth_limit')
        
        tab5.layout.addWidget(card13)
        tab5.layout.addWidget(card14)
        tab5.layout.addWidget(card15)
        tab5.layout.addWidget(card16)
        tab5.layout.addStretch()
        tab_widget.addTab(tab5.widget, '🔒 安全与监控')
        
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
                config_commands.append(f"hostname {data.get('hostname')}")
            if data.get('enable_password'):
                config_commands.append(f"enable secret {data.get('enable_password')}")
            if data.get('console_password'):
                config_commands.append(f"line console 0")
                config_commands.append(f"password {data.get('console_password')}")
                config_commands.append(f"login")
                config_commands.append(f"exit")
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
                config_commands.append(f"hostname {data.get('hostname', 'ac')}")
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
        
        if 'WLAN基本配置' in checked_cards:
            if data.get('wlan_id') and data.get('ssid_name'):
                config_commands.append(f"wlan ssid-profile name {data.get('ssid_name')}")
                config_commands.append(f"ssid {data.get('ssid_name')}")
                config_commands.append(f"exit")
        
        if '安全策略配置' in checked_cards:
            if data.get('security_template'):
                config_commands.append(f"wlan security-profile name {data.get('security_template')}")
                if data.get('auth_method') == 'WPA2-PSK':
                    config_commands.append(f"wpa psk set-key ascii 0 {data.get('psk_password')}")
                    config_commands.append(f"wpa akm dot1x psk")
                    config_commands.append(f"wpa ciphers aes")
                config_commands.append(f"exit")
        
        if 'VAP配置' in checked_cards:
            if data.get('vap_id') and data.get('vap_name'):
                config_commands.append(f"wlan profile name {data.get('vap_name')}")
                if data.get('bind_wlan'):
                    config_commands.append(f"ssid-profile {data.get('bind_wlan')}")
                if data.get('security_template'):
                    config_commands.append(f"security-profile {data.get('security_template')}")
                if data.get('service_vlan'):
                    config_commands.append(f"vlan {data.get('service_vlan')}")
                config_commands.append(f"exit")
        
        if 'AP基础配置' in checked_cards:
            if data.get('ap_name') and data.get('ap_mac'):
                config_commands.append(f"ap name {data.get('ap_name')} mac {data.get('ap_mac')}")
                if data.get('ap_model'):
                    config_commands.append(f"ap-type {data.get('ap_model')}")
                config_commands.append(f"exit")
        
        if 'AP分组配置' in checked_cards:
            if data.get('group_name'):
                config_commands.append(f"ap group {data.get('group_name')}")
                if data.get('group_desc'):
                    config_commands.append(f"description {data.get('group_desc')}")
                config_commands.append(f"exit")
        
        if '上行接口配置' in checked_cards:
            if data.get('uplink_interface') and data.get('uplink_ip'):
                config_commands.append(f"interface {data.get('uplink_interface')}")
                config_commands.append(f"ip address {data.get('uplink_ip')} {data.get('uplink_mask', '255.255.255.0')}")
                config_commands.append(f"no shutdown")
                config_commands.append(f"exit")
        
        if 'CAPWAP隧道配置' in checked_cards:
            if data.get('ac_source_ip'):
                config_commands.append(f"capwap source interface vlan {data.get('mgmt_vlan', '1')}")
        
        if '链路聚合配置' in checked_cards:
            if data.get('agg_id') and data.get('agg_ports'):
                config_commands.append(f"interface port-channel {data.get('agg_id')}")
                config_commands.append(f"switchport mode trunk")
                config_commands.append(f"switchport trunk allowed vlan all")
                config_commands.append(f"exit")
                config_commands.append(f"interface range {data.get('agg_ports')}")
                config_commands.append(f"channel-group {data.get('agg_id')} mode active")
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
            if data.get('qos_template'):
                config_commands.append(f"wlan qos-profile name {data.get('qos_template')}")
                if data.get('bandwidth_limit'):
                    config_commands.append(f"client-rate-limit down {data.get('bandwidth_limit')}")
                config_commands.append(f"exit")
        
        # 生成最终配置
        if config_commands:
            config.append("enable")
            config.append("configure terminal")
            config.extend(config_commands)
            config.append("exit")
            config.append("exit")
            config.append("write memory")
        
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