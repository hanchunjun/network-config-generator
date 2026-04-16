from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QComboBox, QFrame, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt
from ui.config_pages.base_config_page import BaseConfigPage

class RuijieRouterConfig(BaseConfigPage):
    def __init__(self, parent):
        super().__init__(parent, 'ruijie', 'router')
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
        self.add_form_item(card2, 'Console登录密码', 'console_password', is_password=True)
        self.add_form_item(card2, '系统时间', 'system_time')
        self.add_form_item(card2, 'NTP服务器IP地址', 'ntp_server')
        
        card3 = self.create_card('远程登录配置', '👤', '配置SSH和Telnet远程登录')
        self.add_form_item(card3, 'SSH管理员用户名', 'ssh_user')
        self.add_form_item(card3, 'SSH管理员密码', 'ssh_pwd', is_password=True)
        self.add_form_item(card3, 'Telnet登录密码', 'telnet_pwd', is_password=True)
        
        tab1.layout.addWidget(card1)
        tab1.layout.addWidget(card2)
        tab1.layout.addWidget(card3)
        tab1.layout.addStretch()
        tab_widget.addTab(tab1.widget, '⚙️ 基础管理')
        
        # Tab2：三层接口配置
        tab2 = self.create_tab_content()
        card4 = self.create_card('上联互联网WAN口配置', '🌐', '配置WAN口IP地址和运营商网关')
        self.add_form_item(card4, '上联WAN物理端口', 'wan_port')
        self.add_form_item(card4, 'WAN口IP地址', 'wan_ip')
        self.add_form_item(card4, 'WAN口子网掩码', 'wan_mask')
        self.add_form_item(card4, '运营商网关IP地址', 'isp_gateway')
        
        card5 = self.create_card('内网用户LAN口配置', '🔌', '配置内网用户网段网关')
        self.add_form_item(card5, '内网用户LAN物理端口', 'lan_user_port')
        self.add_form_item(card5, '用户网段网关IP', 'user_gw')
        self.add_form_item(card5, '用户网段子网掩码', 'user_mask')
        
        card6 = self.create_card('内网服务器LAN口配置', '🖥️', '配置内网服务器网段网关')
        self.add_form_item(card6, '服务器LAN物理端口', 'lan_server_port')
        self.add_form_item(card6, '服务器网段网关IP', 'server_gw')
        self.add_form_item(card6, '服务器网段子网掩码', 'server_mask')
        
        # 链路聚合配置卡片
        card7 = self.create_card('链路聚合 (Port-Group)', '🔗', '配置端口聚合，支持静态和动态LACP模式')
        
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
        card7.layout.addLayout(config_layout)
        
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
        card7.layout.addWidget(self.agg_table)
        
        # 连接信号
        create_button.clicked.connect(lambda: self.add_agg_port(self.agg_id_input, self.agg_mode_combo, self.agg_lb_combo, self.agg_interface_combo, self.agg_start_port, self.agg_end_port, self.agg_table))
        
        tab2.layout.addWidget(card4)
        tab2.layout.addWidget(card5)
        tab2.layout.addWidget(card6)
        tab2.layout.addWidget(card7)
        tab2.layout.addStretch()
        tab_widget.addTab(tab2.widget, '🔌 三层接口')
        
        # Tab3：NAT地址转换配置
        tab3 = self.create_tab_content()
        card7 = self.create_card('NAT访问控制列表配置', '📜', '配置NAT访问控制列表')
        self.add_form_item(card7, 'NAT ACL名称', 'nat_acl_name')
        self.add_form_item(card7, '用户网段地址', 'user_network')
        self.add_form_item(card7, '用户网段反掩码', 'user_wildcard')
        self.add_form_item(card7, '服务器网段地址', 'server_network')
        self.add_form_item(card7, '服务器网段反掩码', 'server_wildcard')
        
        card8 = self.create_card('动态PAT端口复用配置', '🔄', '配置动态NAT端口复用')
        self.add_form_item(card8, 'NAT ACL名称', 'nat_acl_name_2')
        self.add_form_item(card8, '上联WAN出口物理端口', 'wan_port_2')
        self.add_form_item(card8, '内网用户LAN物理端口', 'lan_user_port_2')
        self.add_form_item(card8, '内网服务器LAN物理端口', 'lan_server_port_2')
        self.add_form_item(card8, '互联网WAN物理端口', 'wan_port_3')
        
        card9 = self.create_card('服务器端口映射配置', '🔗', '配置外网访问内网服务器端口映射')
        self.add_combo_item(card9, '传输协议类型', 'protocol', ['tcp', 'udp'])
        self.add_form_item(card9, '内网服务器真实IP地址', 'server_intranet_ip')
        self.add_form_item(card9, '内网服务器业务端口', 'server_port')
        self.add_form_item(card9, '上联WAN物理端口', 'wan_port_4')
        self.add_form_item(card9, '外网映射访问端口', 'map_external_port')
        
        tab3.layout.addWidget(card7)
        tab3.layout.addWidget(card8)
        tab3.layout.addWidget(card9)
        tab3.layout.addStretch()
        tab_widget.addTab(tab3.widget, '🔄 NAT地址转换')
        
        # Tab4：路由配置
        tab4 = self.create_tab_content()
        card10 = self.create_card('静态路由配置', '🛣️', '配置静态路由条目')
        self.add_form_item(card10, '目的网段1', 'dst_net1')
        self.add_form_item(card10, '目的网段子网掩码1', 'dst_mask1')
        self.add_form_item(card10, '下一跳IP地址1', 'nh1')
        self.add_form_item(card10, '目的网段2', 'dst_net2')
        self.add_form_item(card10, '目的网段子网掩码2', 'dst_mask2')
        self.add_form_item(card10, '下一跳IP地址2', 'nh2')
        self.add_form_item(card10, '默认路由下一跳IP', 'default_nh')
        
        card11 = self.create_card('OSPF动态路由配置', '🔄', '配置OSPF动态路由协议')
        self.add_form_item(card11, 'OSPF进程号', 'ospf_proc')
        self.add_form_item(card11, 'OSPF路由器ID', 'ospf_rid')
        self.add_form_item(card11, 'OSPF区域号', 'area_id')
        self.add_form_item(card11, '需宣告用户网段', 'user_network_2')
        self.add_form_item(card11, '用户网段反掩码', 'user_wildcard_2')
        self.add_form_item(card11, '需宣告服务器网段', 'server_network_2')
        self.add_form_item(card11, '服务器网段反掩码', 'server_wildcard_2')
        self.add_form_item(card11, 'WAN被动接口名称', 'wan_port_5')
        
        tab4.layout.addWidget(card10)
        tab4.layout.addWidget(card11)
        tab4.layout.addStretch()
        tab_widget.addTab(tab4.widget, '🛣️ 路由配置')
        

        
        # Tab6：安全ACL访问控制配置
        tab6 = self.create_tab_content()
        card14 = self.create_card('远程管理权限ACL配置', '🔒', '配置远程管理权限ACL')
        self.add_form_item(card14, '管理ACL名称', 'manage_acl_name')
        self.add_form_item(card14, '允许管理网段IP', 'manage_network')
        self.add_form_item(card14, '允许管理网段反掩码', 'manage_wildcard')
        
        card15 = self.create_card('跨网段访问控制ACL配置', '🛡️', '配置跨网段访问控制ACL')
        self.add_form_item(card15, '跨网段ACL名称', 'cross_segment_acl_name')
        self.add_form_item(card15, '允许访问源网段IP', 'source_network')
        self.add_form_item(card15, '源网段反掩码', 'source_wildcard')
        self.add_form_item(card15, '允许访问目的网段IP', 'dst_network')
        self.add_form_item(card15, '目的网段反掩码', 'dst_wildcard')
        self.add_form_item(card15, '内网用户LAN物理端口', 'lan_user_port_3')
        
        tab6.layout.addWidget(card14)
        tab6.layout.addWidget(card15)
        tab6.layout.addStretch()
        tab_widget.addTab(tab6.widget, '🔒 安全ACL')
        
        # Tab7：运维监控配置
        tab7 = self.create_tab_content()
        card16 = self.create_card('SNMPv2c监控配置', '📈', '配置SNMP监控')
        self.add_form_item(card16, 'SNMP只读团体名', 'snmp_ro_community')
        self.add_form_item(card16, 'SNMP Trap服务器IP', 'trap_server_ip')
        self.add_form_item(card16, 'SNMP Trap团体名', 'trap_community')
        self.add_form_item(card16, '设备部署位置', 'device_location')
        self.add_form_item(card16, '网络管理员联系方式', 'admin_contact')
        
        card17 = self.create_card('日志服务配置', '📋', '配置日志服务')
        self.add_form_item(card17, '日志服务器IP地址', 'log_server_ip')
        self.add_form_item(card17, '日志缓存大小', 'log_buffer_size')
        
        card18 = self.create_card('端口镜像配置', '🔍', '配置端口镜像')
        self.add_form_item(card18, '镜像会话ID', 'mirror_session_id')
        self.add_form_item(card18, '镜像源物理端口', 'mirror_src_port')
        self.add_combo_item(card18, '镜像流量方向', 'mirror_direction', ['both', 'rx', 'tx'])
        self.add_form_item(card18, '镜像目的物理端口', 'mirror_dst_port')
        
        tab7.layout.addWidget(card16)
        tab7.layout.addWidget(card17)
        tab7.layout.addWidget(card18)
        tab7.layout.addStretch()
        tab_widget.addTab(tab7.widget, '📊 运维监控')
        
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
        """添加下拉选择项"""
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
                config.append("service timestamps log datetime local")
                config.append("service timestamps debug datetime local")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('enable_secret'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"enable secret {data.get('enable_secret')}")
                config.append("enable service password-encryption")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '本地登录配置' in checked_cards:
            if data.get('console_password'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line console 0")
                config.append(f" password {data.get('console_password')}")
                config.append(" login")
                config.append(" exec-timeout 10 0")
                config.append(" logging synchronous")
                config.append(" history size 100")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('system_time'):
                config.append("enable")
                config.append(f"clock set {data.get('system_time')}")
                config.append("configure terminal")
                config.append("clock timezone BJ add 08:00")
                config.append("clock summer-time none")
                if data.get('ntp_server'):
                    config.append(f"ntp server {data.get('ntp_server')}")
                    config.append("ntp update-calendar")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '远程登录配置' in checked_cards:
            if data.get('ssh_user') and data.get('ssh_pwd'):
                config.append("enable")
                config.append("configure terminal")
                config.append("enable service ssh-server")
                config.append("ip ssh version 2")
                config.append("crypto key generate rsa modulus 2048")
                config.append(f"username {data.get('ssh_user')} privilege 15 password {data.get('ssh_pwd')}")
                config.append("line vty 0 15")
                config.append(" login local")
                config.append(" transport input ssh")
                config.append(" exec-timeout 15 0")
                config.append("exit")
                config.append("write")
                config.append("")
            if data.get('telnet_pwd'):
                config.append("enable")
                config.append("configure terminal")
                config.append("line vty 16 20")
                config.append(f" password {data.get('telnet_pwd')}")
                config.append(" login")
                config.append(" transport input telnet")
                config.append(" exec-timeout 10 0")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '上联互联网WAN口配置' in checked_cards:
            if data.get('wan_port') and data.get('wan_ip'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface {data.get('wan_port')}")
                config.append(f" ip address {data.get('wan_ip')} {data.get('wan_mask')}")
                config.append(" description TO_INTERNET")
                config.append(" no shutdown")
                config.append("exit")
                if data.get('isp_gateway'):
                    config.append(f"ip route 0.0.0.0 0.0.0.0 {data.get('isp_gateway')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '内网用户LAN口配置' in checked_cards:
            if data.get('lan_user_port') and data.get('user_gw'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface {data.get('lan_user_port')}")
                config.append(f" ip address {data.get('user_gw')} {data.get('user_mask')}")
                config.append(" description LAN_USER_SEGMENT")
                config.append(" no shutdown")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '内网服务器LAN口配置' in checked_cards:
            if data.get('lan_server_port') and data.get('server_gw'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"interface {data.get('lan_server_port')}")
                config.append(f" ip address {data.get('server_gw')} {data.get('server_mask')}")
                config.append(" description LAN_SERVER_SEGMENT")
                config.append(" no shutdown")
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
        
        if 'NAT访问控制列表配置' in checked_cards:
            if data.get('nat_acl_name'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip access-list standard {data.get('nat_acl_name')}")
                if data.get('user_network'):
                    config.append(f" permit {data.get('user_network')} {data.get('user_wildcard')}")
                if data.get('server_network'):
                    config.append(f" permit {data.get('server_network')} {data.get('server_wildcard')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '动态PAT端口复用配置' in checked_cards:
            if data.get('nat_acl_name_2') and data.get('wan_port_2'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip nat inside source list {data.get('nat_acl_name_2')} interface {data.get('wan_port_2')} overload")
                if data.get('lan_user_port_2'):
                    config.append(f"interface {data.get('lan_user_port_2')}")
                    config.append(" ip nat inside")
                    config.append("exit")
                if data.get('lan_server_port_2'):
                    config.append(f"interface {data.get('lan_server_port_2')}")
                    config.append(" ip nat inside")
                    config.append("exit")
                if data.get('wan_port_3'):
                    config.append(f"interface {data.get('wan_port_3')}")
                    config.append(" ip nat outside")
                    config.append("exit")
                config.append("write")
                config.append("")
        
        if '服务器端口映射配置' in checked_cards:
            if data.get('server_intranet_ip') and data.get('server_port'):
                config.append("enable")
                config.append("configure terminal")
                protocol = data.get('protocol', 'tcp')
                config.append(f"ip nat inside source static {protocol} {data.get('server_intranet_ip')} {data.get('server_port')} interface {data.get('wan_port_4')} {data.get('map_external_port')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '静态路由配置' in checked_cards:
            routes = []
            if data.get('dst_net1') and data.get('dst_mask1') and data.get('nh1'):
                routes.append(f"ip route {data.get('dst_net1')} {data.get('dst_mask1')} {data.get('nh1')}")
            if data.get('dst_net2') and data.get('dst_mask2') and data.get('nh2'):
                routes.append(f"ip route {data.get('dst_net2')} {data.get('dst_mask2')} {data.get('nh2')}")
            if data.get('default_nh'):
                routes.append(f"ip route 0.0.0.0 0.0.0.0 {data.get('default_nh')}")
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
                if data.get('area_id'):
                    config.append(f" area {data.get('area_id')}")
                if data.get('user_network_2'):
                    config.append(f" network {data.get('user_network_2')} {data.get('user_wildcard_2')} area {data.get('area_id')}")
                if data.get('server_network_2'):
                    config.append(f" network {data.get('server_network_2')} {data.get('server_wildcard_2')} area {data.get('area_id')}")
                if data.get('wan_port_5'):
                    config.append(f" passive-interface {data.get('wan_port_5')}")
                config.append(" default-information originate always")
                config.append("exit")
                config.append("write")
                config.append("")
        

        
        if '远程管理权限ACL配置' in checked_cards:
            if data.get('manage_acl_name'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip access-list standard {data.get('manage_acl_name')}")
                if data.get('manage_network'):
                    config.append(f" permit {data.get('manage_network')} {data.get('manage_wildcard')}")
                config.append(" deny any")
                config.append("exit")
                config.append("line vty 0 15")
                config.append(f" access-class {data.get('manage_acl_name')} in")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '跨网段访问控制ACL配置' in checked_cards:
            if data.get('cross_segment_acl_name'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"ip access-list extended {data.get('cross_segment_acl_name')}")
                if data.get('source_network') and data.get('dst_network'):
                    config.append(f" permit ip {data.get('source_network')} {data.get('source_wildcard')} {data.get('dst_network')} {data.get('dst_wildcard')}")
                config.append(" deny ip any any")
                config.append("exit")
                if data.get('lan_user_port_3'):
                    config.append(f"interface {data.get('lan_user_port_3')}")
                    config.append(f" ip access-group {data.get('cross_segment_acl_name')} in")
                    config.append("exit")
                config.append("write")
                config.append("")
        
        if 'SNMPv2c监控配置' in checked_cards:
            config.append("enable")
            config.append("configure terminal")
            if data.get('snmp_ro_community'):
                config.append(f"snmp-server community {data.get('snmp_ro_community')} ro")
            if data.get('trap_server_ip') and data.get('trap_community'):
                config.append(f"snmp-server host {data.get('trap_server_ip')} traps {data.get('trap_community')} version 2c")
            config.append("snmp-server enable traps")
            if data.get('device_location'):
                config.append(f"snmp-server location {data.get('device_location')}")
            if data.get('admin_contact'):
                config.append(f"snmp-server contact {data.get('admin_contact')}")
            config.append("exit")
            config.append("write")
            config.append("")
        
        if '日志服务配置' in checked_cards:
            if data.get('log_server_ip'):
                config.append("enable")
                config.append("configure terminal")
                config.append(f"logging host {data.get('log_server_ip')}")
                if data.get('log_buffer_size'):
                    config.append(f"logging buffered {data.get('log_buffer_size')}")
                config.append("logging facility local7")
                config.append("logging on")
                config.append("exit")
                config.append("write")
                config.append("")
        
        if '端口镜像配置' in checked_cards:
            if data.get('mirror_src_port') and data.get('mirror_dst_port'):
                config.append("enable")
                config.append("configure terminal")
                session_id = data.get('mirror_session_id', '1')
                direction = data.get('mirror_direction', 'both')
                config.append(f"monitor session {session_id} source interface {data.get('mirror_src_port')} {direction}")
                config.append(f"monitor session {session_id} destination interface {data.get('mirror_dst_port')}")
                config.append("exit")
                config.append("write")
                config.append("")
        
        self.code_editor.setPlainText('\n'.join(config))
    
    def copy_script(self):
        """复制脚本到剪贴板（覆盖基类方法）"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_editor.toPlainText())
    
    def add_agg_port(self, agg_id_input, agg_mode_combo, agg_lb_combo, agg_interface_combo, agg_start_port, agg_end_port, agg_table):
        """添加聚合端口"""
        agg_id = agg_id_input.text()
        mode = agg_mode_combo.currentText()
        lb = agg_lb_combo.currentText()
        interface_type = agg_interface_combo.currentText()
        start_port = agg_start_port.text()
        end_port = agg_end_port.text()
        
        if not agg_id or not start_port or not end_port:
            return
        
        # 简化模式显示
        if 'LACP' in mode:
            mode = 'LACP'
        else:
            mode = 'Manual'
        
        # 简化负载均衡显示
        lb = lb.split(' ')[0]
        
        # 构建成员端口字符串
        member = f"{interface_type}{start_port} to {interface_type}{end_port}"
        
        # 添加到表格
        row_position = agg_table.rowCount()
        agg_table.insertRow(row_position)
        
        # 设置表格内容
        agg_table.setItem(row_position, 0, QTableWidgetItem(f"Port-Channel {agg_id}"))
        agg_table.setItem(row_position, 1, QTableWidgetItem(mode))
        agg_table.setItem(row_position, 2, QTableWidgetItem(lb))
        agg_table.setItem(row_position, 3, QTableWidgetItem(member))
        
        # 添加删除按钮
        delete_button = QPushButton("删除")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #F53F3F;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        delete_button.clicked.connect(lambda: self.remove_agg_port(agg_table, row_position))
        agg_table.setCellWidget(row_position, 4, delete_button)
    
    def remove_agg_port(self, agg_table, row):
        """删除聚合端口"""
        agg_table.removeRow(row)
    
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
