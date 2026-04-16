from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class HuaweiACConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'huawei', 'ac')
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
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、系统版本')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, '系统版本', 'version')
        self.add_form_item(card1, '字符集编码', 'charset')
        
        card2 = self.create_card('系统时钟与时区', '🕐', '配置时区信息')
        self.add_form_item(card2, '时区名称', 'timezone')
        self.add_form_item(card2, '时区偏移', 'timezone_offset')
        
        card3 = self.create_card('管理地址配置', '📍', '配置管理IP地址和默认网关')
        self.add_form_item(card3, '管理VLAN', 'mgmt_vlan')
        self.add_form_item(card3, '管理IP', 'mgmt_ip')
        self.add_form_item(card3, '子网掩码', 'subnet_mask')
        self.add_form_item(card3, '默认网关', 'gateway')
        
        card4 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录')
        self.add_form_item(card4, 'SSH用户名', 'ssh_user')
        self.add_form_item(card4, 'SSH密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card4, 'Telnet密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addWidget(card4)
        tab1.layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础配置')
        
        # Tab2：WLAN配置
        tab2 = self.create_tab_content()
        card5 = self.create_card('WLAN基本配置', '📶', '配置WLAN基本参数')
        self.add_form_item(card5, 'SSID名称', 'ssid_name')
        self.add_form_item(card5, 'WLAN ID', 'wlan_id')
        self.add_form_item(card5, '安全模板', 'security_template')
        self.add_form_item(card5, '服务模板', 'service_template')
        
        card6 = self.create_card('安全策略配置', '🔒', '配置WLAN安全策略')
        self.add_form_item(card6, '认证方式', 'auth_method')
        self.add_form_item(card6, 'PSK密码', 'psk_password', is_password=True)
        self.add_form_item(card6, 'Radius服务器', 'radius_server')
        self.add_form_item(card6, 'Radius密钥', 'radius_key', is_password=True)
        
        card7 = self.create_card('VAP配置', '🌐', '配置VAP虚拟接入点')
        self.add_form_item(card7, 'VAP名称', 'vap_name')
        self.add_form_item(card7, 'VAP ID', 'vap_id')
        self.add_form_item(card7, '绑定WLAN', 'bind_wlan')
        self.add_form_item(card7, '业务VLAN', 'service_vlan')
        
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addWidget(card7)
        tab2.layout.addStretch()
        tab_widget.addTab(tab2.widget, '📶 WLAN配置')
        
        # Tab3：AP管理
        tab3 = self.create_tab_content()
        card8 = self.create_card('AP基础配置', '📱', '配置AP基本信息')
        self.add_form_item(card8, 'AP名称', 'ap_name')
        self.add_form_item(card8, 'AP MAC地址', 'ap_mac')
        self.add_form_item(card8, 'AP型号', 'ap_model')
        
        card9 = self.create_card('AP分组配置', '📦', '配置AP分组')
        self.add_form_item(card9, '分组名称', 'group_name')
        self.add_form_item(card9, '分组描述', 'group_desc')
        
        card10 = self.create_card('AP模板配置', '📋', '配置AP模板')
        self.add_form_item(card10, '模板名称', 'template_name')
        self.add_form_item(card10, '模板类型', 'template_type')
        
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addWidget(card10)
        tab3.layout.addStretch()
        tab_widget.addTab(tab3.widget, '📱 AP管理')
        
        # Tab4：接口与链路
        tab4 = self.create_tab_content()
        card11 = self.create_card('上行接口配置', '🔌', '配置AC上行接口')
        self.add_form_item(card11, '上行接口', 'uplink_interface')
        self.add_form_item(card11, 'IP地址', 'uplink_ip')
        self.add_form_item(card11, '子网掩码', 'uplink_mask')
        
        card12 = self.create_card('CAPWAP隧道配置', '🌐', '配置CAPWAP隧道参数')
        self.add_form_item(card12, 'AC源地址', 'ac_source_ip')
        self.add_form_item(card12, 'CAPWAP端口', 'capwap_port')
        
        card13 = self.create_card('链路聚合配置', '🔗', '配置链路聚合')
        self.add_form_item(card13, '聚合端口', 'agg_ports')
        self.add_form_item(card13, '聚合组ID', 'agg_id')
        
        tab4.layout.addWidget(card11)
        tab4.layout.addWidget(card12)
        tab4.layout.addWidget(card13)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '🔌 接口与链路')
        
        # Tab5：安全与监控
        tab5 = self.create_tab_content()
        card14 = self.create_card('ACL访问控制', '📜', '配置访问控制列表')
        self.add_form_item(card14, 'ACL编号', 'acl_number')
        self.add_form_item(card14, '源地址', 'src_addr')
        self.add_form_item(card14, '目的地址', 'dst_addr')
        
        card15 = self.create_card('NTP时钟同步', '⏰', '配置NTP服务器')
        self.add_form_item(card15, 'NTP服务器', 'ntp_server')
        
        card16 = self.create_card('SNMP监控', '📈', '配置SNMP监控')
        self.add_form_item(card16, 'SNMP团体名', 'snmp_community')
        self.add_form_item(card16, 'Trap服务器', 'trap_server')
        
        card17 = self.create_card('QoS配置', '🚀', '配置QoS策略')
        self.add_form_item(card17, 'QoS模板', 'qos_template')
        self.add_form_item(card17, '带宽限制', 'bandwidth_limit')
        
        tab5.layout.addWidget(card14)
        tab5.layout.addWidget(card15)
        tab5.layout.addWidget(card16)
        tab5.layout.addWidget(card17)
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
                config_commands.append(f"sysname {data.get('hostname')}")
            if data.get('charset'):
                config_commands.append(f"language-mode {data.get('charset')}")
        
        if '系统时钟与时区' in checked_cards:
            if data.get('timezone') and data.get('timezone_offset'):
                config_commands.append(f"clock timezone {data.get('timezone')} {data.get('timezone_offset')}")
        
        if '管理地址配置' in checked_cards:
            if data.get('mgmt_vlan'):
                config_commands.append(f"vlan {data.get('mgmt_vlan')}")
                config_commands.append(f"description manage")
                config_commands.append(f"quit")
                if data.get('mgmt_ip'):
                    config_commands.append(f"interface Vlanif {data.get('mgmt_vlan')}")
                    subnet = data.get('subnet_mask', '255.255.255.0')
                    config_commands.append(f"ip address {data.get('mgmt_ip')} {subnet}")
                    config_commands.append(f"quit")
            if data.get('gateway'):
                config_commands.append(f"ip route-static 0.0.0.0 0.0.0.0 {data.get('gateway')}")
        
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
        
        if 'WLAN基本配置' in checked_cards:
            if data.get('wlan_id') and data.get('ssid_name'):
                config_commands.append(f"wlan")
                config_commands.append(f"ssid-profile name {data.get('ssid_name')}")
                config_commands.append(f"ssid {data.get('ssid_name')}")
                config_commands.append(f"quit")
                config_commands.append(f"quit")
        
        if '安全策略配置' in checked_cards:
            if data.get('security_template'):
                config_commands.append(f"wlan")
                config_commands.append(f"security-profile name {data.get('security_template')}")
                if data.get('auth_method') == 'WPA2-PSK':
                    config_commands.append(f"security wpa2 psk pass-phrase {data.get('psk_password')} aes")
                config_commands.append(f"quit")
                config_commands.append(f"quit")
        
        if 'VAP配置' in checked_cards:
            if data.get('vap_id') and data.get('vap_name'):
                config_commands.append(f"wlan")
                config_commands.append(f"vap-profile name {data.get('vap_name')}")
                if data.get('bind_wlan'):
                    config_commands.append(f"ssid-profile {data.get('bind_wlan')}")
                if data.get('security_template'):
                    config_commands.append(f"security-profile {data.get('security_template')}")
                if data.get('service_vlan'):
                    config_commands.append(f"service-vlan {data.get('service_vlan')}")
                config_commands.append(f"quit")
                config_commands.append(f"quit")
        
        if 'AP基础配置' in checked_cards:
            if data.get('ap_name') and data.get('ap_mac'):
                config_commands.append(f"wlan")
                config_commands.append(f"ap-id 0 ap-mac {data.get('ap_mac')}")
                config_commands.append(f"ap-name {data.get('ap_name')}")
                config_commands.append(f"quit")
                config_commands.append(f"quit")
        
        if '上行接口配置' in checked_cards:
            if data.get('uplink_interface') and data.get('uplink_ip'):
                config_commands.append(f"interface {data.get('uplink_interface')}")
                config_commands.append(f"ip address {data.get('uplink_ip')} {data.get('uplink_mask', '255.255.255.0')}")
                config_commands.append(f"undo shutdown")
                config_commands.append(f"quit")
        
        if 'CAPWAP隧道配置' in checked_cards:
            if data.get('ac_source_ip'):
                config_commands.append(f"capwap source interface Vlanif {data.get('mgmt_vlan', '1')}")
        
        if '链路聚合配置' in checked_cards:
            if data.get('agg_id') and data.get('agg_ports'):
                config_commands.append(f"interface Eth-Trunk {data.get('agg_id')}")
                config_commands.append(f"port link-type trunk")
                config_commands.append(f"port trunk allow-pass vlan all")
                config_commands.append(f"quit")
                config_commands.append(f"interface range {data.get('agg_ports')}")
                config_commands.append(f"eth-trunk {data.get('agg_id')}")
                config_commands.append(f"quit")
        
        if 'ACL访问控制' in checked_cards:
            if data.get('acl_number'):
                config_commands.append(f"acl number {data.get('acl_number')}")
                if data.get('src_addr'):
                    config_commands.append(f"rule permit ip source {data.get('src_addr')} 0.0.0.255")
                config_commands.append(f"quit")
        
        if 'NTP时钟同步' in checked_cards:
            if data.get('ntp_server'):
                config_commands.append(f"ntp server {data.get('ntp_server')}")
        
        if 'SNMP监控' in checked_cards:
            config_commands.append(f"snmp-agent")
            if data.get('snmp_community'):
                config_commands.append(f"snmp-agent community read {data.get('snmp_community')}")
            if data.get('trap_server'):
                config_commands.append(f"snmp-agent target-host trap address udp-domain {data.get('trap_server')} params securityname {data.get('snmp_community', 'public')}")
        
        if 'QoS配置' in checked_cards:
            if data.get('qos_template'):
                config_commands.append(f"wlan")
                config_commands.append(f"qos-profile name {data.get('qos_template')}")
                if data.get('bandwidth_limit'):
                    config_commands.append(f"rate-limit user down {data.get('bandwidth_limit')}")
                config_commands.append(f"quit")
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