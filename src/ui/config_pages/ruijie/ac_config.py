from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class RuijieACConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'ruijie', 'ac')
        self.form_fields = {}
        self.cards = []
        self.init_panels()
        
    def init_panels(self):
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
        
        tab1 = self.create_tab_content()
        card1 = self.create_card('设备基础信息', '🖥️', '配置设备主机名、系统版本')
        self.add_form_item(card1, '设备主机名', 'hostname')
        self.add_form_item(card1, '系统版本', 'version')
        self.add_form_item(card1, '字符集编码', 'charset')
        
        card2 = self.create_card('系统时钟与时区', '🕐', '配置时区信息')
        self.add_form_item(card2, '时区名称', 'timezone')
        self.add_form_item(card2, '时区偏移', 'timezone_offset')
        
        card3 = self.create_card('密码策略与加密', '🔐', '配置密码策略')
        self.add_form_item(card3, '密码最小长度', 'min_size')
        self.add_combo_item(card3, '启用强密码策略', 'strong_pwd', ['enable', 'disable'])
        self.add_combo_item(card3, '启用密码加密', 'pwd_encrypt', ['enable', 'disable'])
        
        card4 = self.create_card('特权密码配置', '🔑', '配置enable密码')
        self.add_form_item(card4, 'enable加密密码', 'enable_password', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addWidget(card4)
        tab1.layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 系统基础')
        
        tab2 = self.create_tab_content()
        card5 = self.create_card('VLAN创建配置', '📊', '配置VLAN')
        self.add_form_item(card5, '管理Super VLAN', 'super_vlan')
        self.add_form_item(card5, '子VLAN范围', 'sub_vlan_range')
        self.add_form_item(card5, '业务VLAN列表', 'vlan_list')
        
        card6 = self.create_card('AP管理网段接口', '🌐', '配置AP管理VLANIF')
        self.add_form_item(card6, 'VLANIF编号', 'mgmt_vlan')
        self.add_form_item(card6, 'IP地址', 'mgmt_ip')
        self.add_form_item(card6, '子网掩码', 'mgmt_mask')
        
        card7 = self.create_card('AC互联/上联接口', '🔗', '配置上联VLANIF')
        self.add_form_item(card7, 'VLANIF编号', 'uplink_vlan')
        self.add_form_item(card7, 'IP地址', 'uplink_ip')
        self.add_form_item(card7, '子网掩码', 'uplink_mask')
        
        card8 = self.create_card('万兆上联Trunk口', '🔌', '配置物理端口')
        self.add_form_item(card8, '物理端口', 'trunk_port')
        self.add_form_item(card8, '允许通过VLAN列表', 'allowed_vlan')
        
        # 链路聚合配置卡片
        card9 = self.create_card('链路聚合 (Port-Group)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
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
        self.agg_interface_combo.addItems(['GigabitEthernet ', 'TenGigabitEthernet '])
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
        card9.layout.addLayout(config_layout)
        
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
        card9.layout.addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addWidget(card7)
        tab2.layout.addWidget(card8)
        tab2.layout.addWidget(card9)
        tab2.layout.addStretch()
        tab_widget.addTab(tab2.widget, '🔌 接口与VLAN')
        
        tab3 = self.create_tab_content()
        card9 = self.create_card('AC控制器基础配置', '📡', '配置AC控制器')
        self.add_form_item(card9, 'AC控制IP', 'ac_ip')
        self.add_form_item(card9, '国家码', 'country')
        self.add_form_item(card9, 'CAPWAP控制IP', 'capwap_ip')
        
        card10 = self.create_card('全局射频速率配置', '📶', '配置2.4G/5G速率')
        self.add_form_item(card10, '802.11g速率配置', 'rate_11g')
        self.add_form_item(card10, '802.11b速率配置', 'rate_11b')
        self.add_form_item(card10, '802.11a速率配置', 'rate_11a')
        
        tab3.layout.addWidget(card9)
        tab3.layout.addWidget(card10)
        tab3.layout.addStretch()
        tab_widget.addTab(tab3.widget, '📡 AC全局无线')
        
        tab4 = self.create_tab_content()
        card11 = self.create_card('wlan-config基础配置', '📱', '配置WLAN')
        self.add_form_item(card11, 'wlan-config ID', 'wlan_id')
        self.add_form_item(card11, 'SSID名称', 'ssid_name')
        self.add_form_item(card11, '编码格式', 'ssid_code')
        self.add_form_item(card11, '上行平均限速', 'avg_up')
        self.add_form_item(card11, '上行突发限速', 'burst_up')
        self.add_form_item(card11, '下行平均限速', 'avg_down')
        self.add_form_item(card11, '下行突发限速', 'burst_down')
        self.add_form_item(card11, '防抖动时间', 'jitter_time')
        self.add_combo_item(card11, '隧道模式', 'tunnel_mode', ['local', 'central'])
        
        card12 = self.create_card('wlansec安全配置', '🔒', '配置WPA2-PSK')
        self.add_form_item(card12, 'wlansec ID', 'sec_id')
        self.add_form_item(card12, 'PSK密码', 'psk_key', is_password=True)
        
        card13 = self.create_card('IoT物联网SSID安全', '🌐', '配置物联网SSID')
        self.add_form_item(card13, 'IoT wlansec ID', 'iot_sec_id')
        self.add_form_item(card13, 'IoT PSK密码', 'iot_psk_key', is_password=True)
        
        tab4.layout.addWidget(card11)
        tab4.layout.addWidget(card12)
        tab4.layout.addWidget(card13)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '📱 WLAN配置')
        
        tab5 = self.create_tab_content()
        card14 = self.create_card('AP组基础配置', '🏢', '配置AP组')
        self.add_form_item(card14, 'AP组名称', 'ap_group_name')
        self.add_combo_item(card14, '射频模板开关', 'ript', ['enable', 'disable'])
        self.add_combo_item(card14, '粘性切换开关', 'sticky', ['enable', 'disable'])
        
        card15 = self.create_card('AP组VLAN映射', '🔀', '配置interface-mapping')
        self.add_form_item(card15, 'radio口', 'radio_id')
        self.add_form_item(card15, '业务VLAN', 'service_vlan')
        self.add_form_item(card15, '绑定wlan-id', 'wlan_id_map')
        
        card16 = self.create_card('AP组速率配置', '⚡', '配置2.4G/5G速率')
        self.add_form_item(card16, 'AP组名称', 'ap_group_rate')
        self.add_form_item(card16, '2.4G射频速率', 'rate_24g')
        self.add_form_item(card16, '5G射频速率', 'rate_5g')
        
        tab5.layout.addWidget(card14)
        tab5.layout.addWidget(card15)
        tab5.layout.addWidget(card16)
        tab5.layout.addStretch()
        tab_widget.addTab(tab5.widget, '🏢 AP组配置')
        
        tab6 = self.create_tab_content()
        card17 = self.create_card('ap-config all批量配置', '📋', '配置AP全局默认')
        self.add_form_item(card17, '全局用户数限制', 'total_sta')
        self.add_form_item(card17, '单radio用户限制', 'per_radio_sta')
        self.add_form_item(card17, '响应RSSI阈值', 'rssi')
        self.add_form_item(card17, '信道带宽', 'chan_width')
        self.add_combo_item(card17, '11ac支持', 'ac_support', ['enable', 'disable'])
        self.add_combo_item(card17, '11ax支持', 'ax_support', ['enable', 'disable'])
        
        tab6.layout.addWidget(card17)
        tab6.layout.addStretch()
        tab_widget.addTab(tab6.widget, '📋 AP全局配置')
        
        tab7 = self.create_tab_content()
        card18 = self.create_card('DHCP服务配置', '📶', '配置DHCP地址池')
        self.add_form_item(card18, '地址池名称', 'pool_name')
        self.add_form_item(card18, '网段', 'dhcp_network')
        self.add_form_item(card18, '掩码', 'dhcp_mask')
        self.add_form_item(card18, '网关', 'dhcp_gateway')
        self.add_form_item(card18, 'option138 AC地址', 'option138_ip')
        self.add_form_item(card18, '租期天数', 'lease_day')
        self.add_form_item(card18, '租期小时', 'lease_hour')
        self.add_form_item(card18, '租期分钟', 'lease_min')
        
        card19 = self.create_card('静态路由配置', '🛣️', '配置默认路由')
        self.add_form_item(card19, '默认路由下一跳', 'default_gateway')
        
        tab7.layout.addWidget(card18)
        tab7.layout.addWidget(card19)
        tab7.layout.addStretch()
        tab_widget.addTab(tab7.widget, '📶 DHCP与路由')
        
        tab8 = self.create_tab_content()
        card20 = self.create_card('Web管理配置', '🌐', '配置Web管理')
        self.add_form_item(card20, 'Web管理员用户名', 'web_user')
        self.add_form_item(card20, 'Web管理员密码', 'web_pwd', is_password=True)
        
        card21 = self.create_card('SSH服务配置', '🔐', '配置SSH服务')
        self.add_combo_item(card21, 'SSH服务启用', 'ssh_enable', ['enable', 'disable'])
        
        card22 = self.create_card('登录与AAA', '👤', '配置管理员登录')
        self.add_form_item(card22, '管理员用户名', 'admin_user')
        self.add_form_item(card22, '管理员权限级别', 'admin_priv')
        self.add_form_item(card22, '管理员加密密码', 'admin_pwd', is_password=True)
        self.add_combo_item(card22, 'VTY登录认证模式', 'vty_auth', ['local', 'aaa'])
        
        tab8.layout.addWidget(card20)
        tab8.layout.addWidget(card21)
        tab8.layout.addWidget(card22)
        tab8.layout.addStretch()
        tab_widget.addTab(tab8.widget, '🔧 管理与远程')
        
        tab9 = self.create_tab_content()
        card23 = self.create_card('日志服务器', '📋', '配置日志服务')
        self.add_form_item(card23, '日志服务器IP', 'log_server')
        
        card24 = self.create_card('SNMP配置', '📈', '配置SNMP')
        self.add_combo_item(card24, 'SNMP v1', 'snmp_v1', ['enable', 'disable'])
        self.add_combo_item(card24, 'SNMP v2c', 'snmp_v2c', ['enable', 'disable'])
        self.add_combo_item(card24, 'SNMP v3', 'snmp_v3', ['enable', 'disable'])
        self.add_combo_item(card24, 'SNMP操作日志', 'snmp_log', ['enable', 'disable'])
        
        card25 = self.create_card('云端管理', '☁️', '配置WIS/CWMP')
        self.add_form_item(card25, 'WIS服务器地址', 'wis_url')
        self.add_form_item(card25, 'CWMP ACS服务器地址', 'acs_url')
        self.add_form_item(card25, 'CWMP上报间隔', 'cwmp_interval')
        
        tab9.layout.addWidget(card23)
        tab9.layout.addWidget(card24)
        tab9.layout.addWidget(card25)
        tab9.layout.addStretch()
        tab_widget.addTab(tab9.widget, '📊 日志与SNMP')
        
        tab10 = self.create_tab_content()
        card26 = self.create_card('高级无线特性', '🚀', '配置高级无线功能')
        self.add_combo_item(card26, '无线转发模式', 'forward_mode', ['central', 'local'])
        self.add_combo_item(card26, 'Web带宽控制方向', 'bw_ctrl', ['both', 'up', 'down'])
        
        tab10.layout.addWidget(card26)
        tab10.layout.addStretch()
        tab_widget.addTab(tab10.widget, '🚀 高级特性')
        
        self.left_layout.addWidget(tab_widget)
        
    def create_tab_content(self):
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
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        checkbox = QCheckBox()
        checkbox.setStyleSheet('QCheckBox::indicator { width: 18px; height: 18px; }')
        title_layout.addWidget(checkbox)
        
        title_label = QLabel(f'{icon} {title}')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #1D2129;')
        title_layout.addWidget(title_label)
        
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet('font-size: 12px; color: #86909C;')
            title_layout.addWidget(desc_label)
        
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
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
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        if is_label:
            value_label = QLabel(default_value)
            value_label.setStyleSheet('color: #86909C; font-size: 14px;')
            item_layout.addWidget(value_label)
        else:
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(f'请输入{label_text}')
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
            if is_password:
                input_widget.setEchoMode(QLineEdit.Password)
            item_layout.addWidget(input_widget)
            self.form_fields[field_name] = input_widget
        
        item_layout.addStretch()
        card.layout.addLayout(item_layout)
        
    def add_combo_item(self, card, label_text, field_name, options):
        item_layout = QHBoxLayout()
        item_layout.setSpacing(16)
        
        label = QLabel(f'{label_text}:')
        label.setFixedWidth(160)
        label.setStyleSheet('color: #4E5969; font-size: 14px;')
        item_layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E5E6EB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 1px solid #165DFF;
            }
        """)
        item_layout.addWidget(combo)
        self.form_fields[field_name] = combo
        
        item_layout.addStretch()
        card.layout.addLayout(item_layout)
        
    def get_form_data(self):
        data = {}
        for field_name, widget in self.form_fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
        return data
    
    def get_checked_cards(self):
        checked = []
        for card in self.cards:
            if card.checkbox.isChecked():
                checked.append(card.title)
        return checked
    
    def reset_all_fields(self):
        for widget in self.form_fields.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        for card in self.cards:
            card.checkbox.setChecked(False)
    
    def generate_config(self):
        data = self.get_form_data()
        checked_cards = self.get_checked_cards()
        
        config = []
        
        if '设备基础信息' in checked_cards:
            if data.get('hostname'):
                config.append("enable")
                config.append("configure terminal")
                if data.get('version'):
                    config.append(f"version AC_RGOS {data.get('version')}")
                if data.get('charset'):
                    config.append(f"language character-set {data.get('charset')}")
                config.append(f"hostname {data.get('hostname')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '系统时钟与时区' in checked_cards:
            if data.get('timezone'):
                config.append("enable")
                config.append("configure terminal")
                offset = data.get('timezone_offset', '+8')
                config.append(f"clock timezone {data.get('timezone')} {offset} 0")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '密码策略与加密' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("password policy printable-character-check")
            if data.get('min_size'):
                config.append(f"password policy min-size {data.get('min_size')}")
            if data.get('strong_pwd') == 'enable':
                config.append("password policy strong")
            if data.get('pwd_encrypt') == 'enable':
                config.append("service password-encryption")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '特权密码配置' in checked_cards:
            if data.get('enable_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"enable password 7 {data.get('enable_password')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'VLAN创建配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('super_vlan'):
                config.append(f"vlan {data.get('super_vlan')}")
                config.append(" supervlan")
                if data.get('sub_vlan_range'):
                    config.append(f" subvlan {data.get('sub_vlan_range')}")
                config.append("!")
            if data.get('vlan_list'):
                config.append(f"vlan range {data.get('vlan_list')}")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if 'AP管理网段接口' in checked_cards:
            if data.get('mgmt_vlan') and data.get('mgmt_ip'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface VLAN {data.get('mgmt_vlan')}")
                config.append(f" ip address {data.get('mgmt_ip')} {data.get('mgmt_mask')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'AC互联/上联接口' in checked_cards:
            if data.get('uplink_vlan') and data.get('uplink_ip'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface VLAN {data.get('uplink_vlan')}")
                config.append(f" ip address {data.get('uplink_ip')} {data.get('uplink_mask')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '万兆上联Trunk口' in checked_cards:
            if data.get('trunk_port'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface TenGigabitEthernet {data.get('trunk_port')}")
                config.append(" switchport mode trunk")
                if data.get('allowed_vlan'):
                    config.append(f" switchport trunk allowed vlan only {data.get('allowed_vlan')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '链路聚合 (Port-Group)' in checked_cards:
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
                    config.append("enable")
                    config.append("configure terminal")
                    config.append(f"port-group load-balance {lb_algorithm}")
                    config.append("exit")
                    config.append("write")
                    config.append("")
                
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
                            port_range = f"{interface_type} {start} {interface_type} {end}"
                            
                            config.append("enable")
                            config.append("configure terminal")
                            
                            # 配置聚合端口
                            config.append(f"interface range {port_range}")
                            if mode == 'LACP':
                                config.append(f" channel-group {agg_id} mode active")
                            else:
                                config.append(f" channel-group {agg_id} mode on")
                            config.append(" no shutdown")
                            config.append("exit")
                            
                            # 配置聚合端口接口
                            config.append(f"interface Port-Channel {agg_id}")
                            config.append(" no shutdown")
                            config.append("exit")
                            
                            config.append("exit")
                            config.append("write")
                            config.append("")
        
        if 'AC控制器基础配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("ac-controller")
            config.append(" country CN")
            if data.get('ac_ip'):
                config.append(f" capwap ctrl-ip {data.get('ac_ip')}")
            config.append(" no ac-control disable")
            config.append(" wlan-features 0x3")
            config.append(" wqos fs enable")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '全局射频速率配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("ac-controller")
            config.append(" 802.11g network rate 1 disabled")
            config.append(" 802.11g network rate 2 disabled")
            config.append(" 802.11g network rate 5 disabled")
            config.append(" 802.11g network rate 6 supported")
            config.append(" 802.11g network rate 9 supported")
            config.append(" 802.11g network rate 11 mandatory")
            config.append(" 802.11g network rate 12 supported")
            config.append(" 802.11g network rate 18 supported")
            config.append(" 802.11g network rate 24 supported")
            config.append(" 802.11g network rate 36 supported")
            config.append(" 802.11g network rate 48 supported")
            config.append(" 802.11g network rate 54 supported")
            config.append(" 802.11b network rate 1 disabled")
            config.append(" 802.11b network rate 2 disabled")
            config.append(" 802.11b network rate 5 disabled")
            config.append(" 802.11b network rate 11 mandatory")
            config.append(" 802.11a network rate 6 mandatory")
            config.append(" 802.11a network rate 9 supported")
            config.append(" 802.11a network rate 12 mandatory")
            config.append(" 802.11a network rate 18 supported")
            config.append(" 802.11a network rate 24 mandatory")
            config.append(" 802.11a network rate 36 supported")
            config.append(" 802.11a network rate 48 supported")
            config.append(" 802.11a network rate 54 supported")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if 'wlan-config基础配置' in checked_cards:
            if data.get('wlan_id') and data.get('ssid_name'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"wlan-config {data.get('wlan_id')} {data.get('ssid_name')}")
                config.append(" ssid-code utf-8")
                if data.get('avg_up') and data.get('burst_up'):
                    config.append(f" wlan-based per-user-limit up-streams average-data-rate {data.get('avg_up')} burst-data-rate {data.get('burst_up')}")
                if data.get('avg_down') and data.get('burst_down'):
                    config.append(f" wlan-based per-user-limit down-streams average-data-rate {data.get('avg_down')} burst-data-rate {data.get('burst_down')}")
                config.append(" prevent-jitter enable")
                if data.get('jitter_time'):
                    config.append(f" prevent-jitter time {data.get('jitter_time')}")
                if data.get('tunnel_mode'):
                    config.append(f" tunnel {data.get('tunnel_mode')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'wlansec安全配置' in checked_cards:
            if data.get('sec_id') and data.get('psk_key'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"wlansec {data.get('sec_id')}")
                config.append(" security rsn enable")
                config.append(" security rsn ciphers aes enable")
                config.append(" security rsn akm psk enable")
                config.append(f" security rsn akm psk set-key ascii {data.get('psk_key')}")
                config.append(" security wpa enable")
                config.append(" security wpa ciphers aes enable")
                config.append(" security wpa akm psk enable")
                config.append(f" security wpa akm psk set-key ascii {data.get('psk_key')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'IoT物联网SSID安全' in checked_cards:
            if data.get('iot_sec_id') and data.get('iot_psk_key'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"wlansec {data.get('iot_sec_id')}")
                config.append(" security rsn enable")
                config.append(" security rsn ciphers aes enable")
                config.append(" security rsn akm psk enable")
                config.append(f" security rsn akm psk set-key ascii {data.get('iot_psk_key')}")
                config.append(" security wpa enable")
                config.append(" security wpa ciphers aes enable")
                config.append(" security wpa akm psk enable")
                config.append(f" security wpa akm psk set-key ascii {data.get('iot_psk_key')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'AP组基础配置' in checked_cards:
            if data.get('ap_group_name'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ap-group {data.get('ap_group_name')}")
                if data.get('ript') == 'enable':
                    config.append(" ript enable")
                if data.get('sticky') == 'enable':
                    config.append(" sticky-steering enable")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'AP组VLAN映射' in checked_cards:
            if data.get('ap_group_name') and data.get('radio_id'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ap-group {data.get('ap_group_name')}")
                config.append(f" interface-mapping {data.get('radio_id')} {data.get('service_vlan')} ap-wlan-id {data.get('wlan_id_map')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'AP组速率配置' in checked_cards:
            if data.get('ap_group_rate'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ap-group {data.get('ap_group_rate')}")
                config.append(" 802.11g network rate 1 disabled")
                config.append(" 802.11g network rate 2 disabled")
                config.append(" 802.11g network rate 5 disabled")
                config.append(" 802.11g network rate 6 disabled")
                config.append(" 802.11g network rate 9 disabled")
                config.append(" 802.11g network rate 11 mandatory")
                config.append(" 802.11g network rate 12 mandatory")
                config.append(" 802.11g network rate 18 supported")
                config.append(" 802.11g network rate 24 supported")
                config.append(" 802.11g network rate 36 supported")
                config.append(" 802.11g network rate 48 supported")
                config.append(" 802.11g network rate 54 supported")
                config.append(" 802.11a network rate 6 disabled")
                config.append(" 802.11a network rate 9 disabled")
                config.append(" 802.11a network rate 12 mandatory")
                config.append(" 802.11a network rate 18 supported")
                config.append(" 802.11a network rate 24 mandatory")
                config.append(" 802.11a network rate 36 supported")
                config.append(" 802.11a network rate 48 supported")
                config.append(" 802.11a network rate 54 supported")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'ap-config all批量配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("ap-config all")
            config.append(" hide-ssid sta-reach-limit")
            if data.get('total_sta'):
                config.append(f" sta-limit {data.get('total_sta')}")
            if data.get('per_radio_sta'):
                config.append(f" sta-limit {data.get('per_radio_sta')} radio 1")
                config.append(f" sta-limit {data.get('per_radio_sta')} radio 2")
            if data.get('rssi'):
                config.append(f" response-rssi {data.get('rssi')} radio 1")
                config.append(f" response-rssi {data.get('rssi')} radio 2")
            if data.get('chan_width'):
                config.append(f" chan-width {data.get('chan_width')} radio all")
            if data.get('ac_support') == 'enable':
                config.append(" 11acsupport enable radio all")
            if data.get('ax_support') == 'enable':
                config.append(" 11axsupport enable radio all")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if 'DHCP服务配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            config.append("service dhcp")
            config.append("!")
            if data.get('pool_name'):
                config.append(f"ip dhcp pool {data.get('pool_name')}")
                if data.get('option138_ip'):
                    config.append(f" option 138 ip {data.get('option138_ip')}")
                if data.get('lease_day'):
                    config.append(f" lease {data.get('lease_day')} {data.get('lease_hour', '0')} {data.get('lease_min', '0')}")
                if data.get('dhcp_network'):
                    config.append(f" network {data.get('dhcp_network')} {data.get('dhcp_mask')}")
                if data.get('dhcp_gateway'):
                    config.append(f" default-router {data.get('dhcp_gateway')}")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '静态路由配置' in checked_cards:
            if data.get('default_gateway'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip route 0.0.0.0 0.0.0.0 {data.get('default_gateway')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'Web管理配置' in checked_cards:
            if data.get('web_user') and data.get('web_pwd'):
                config.append("enable")
                config.append("configure terminal")
                config.append("enable service web-server http")
                config.append("enable service web-server https")
                config.append("web-server http redirect-to-https")
                config.append(f"webmaster level 0 username {data.get('web_user')} password {data.get('web_pwd')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'SSH服务配置' in checked_cards:
            if data.get('ssh_enable') == 'enable':
                config.append("enable")
                config.append("configure terminal")
                config.append("enable service ssh-server")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '登录与AAA' in checked_cards:
            if data.get('admin_user') and data.get('admin_pwd'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line vty 0 15")
                config.append(" login local")
                config.append("!")
                config.append(f"username {data.get('admin_user')} privilege {data.get('admin_priv', '15')} password 7 {data.get('admin_pwd')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '日志服务器' in checked_cards:
            if data.get('log_server'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"logging server {data.get('log_server')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if 'SNMP配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('snmp_v1') == 'disable':
                config.append("no snmp-server enable version v1")
            if data.get('snmp_v2c') == 'enable':
                config.append("snmp-server enable version v2c")
            if data.get('snmp_v3') == 'enable':
                config.append("snmp-server enable version v3")
            if data.get('snmp_log') == 'enable':
                config.append("snmp-server logging set-operation")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '云端管理' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('wis_url'):
                config.append("wis enable")
                config.append(f"wis server-url {data.get('wis_url')}")
                config.append("!")
            if data.get('acs_url'):
                config.append("cwmp")
                config.append(f" acs url {data.get('acs_url')}")
                if data.get('cwmp_interval'):
                    config.append(f" cpe inform interval {data.get('cwmp_interval')}")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '高级无线特性' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('forward_mode'):
                config.append(f"wlan-cap forward {data.get('forward_mode')}")
            if data.get('bw_ctrl'):
                config.append(f"web-bw-ctrl {data.get('bw_ctrl')}")
            config.append("wids")
            config.append("black-white-list")
            config.append("virtual-ac domain 100")
            config.append("nfpp")
            config.append("frn")
            config.append("exit")
            config.append("write")
            config.append("")
        
        self.code_editor.setPlainText('\n'.join(config))
    
    def copy_script(self):
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_editor.toPlainText())
    
    def export_config(self):
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
        table.setItem(row, 0, QTableWidgetItem(f"Port-Group {agg_id}"))
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
