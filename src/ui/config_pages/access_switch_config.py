from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QGroupBox
from ui.config_pages.base_config_page import BaseConfigPage

class AccessSwitchConfig(BaseConfigPage):
    def __init__(self, parent, vendor):
        super().__init__(parent, vendor, 'access_switch')
        self.title.setText('接入交换机配置')
        self.init_config_area()
        
    def init_config_area(self):
        """初始化配置区域"""
        layout = QVBoxLayout()
        
        # 面板1：基础配置
        basic_config = QGroupBox('基础配置')
        basic_layout = QVBoxLayout()
        
        # 设备基础信息
        device_info = QGroupBox('设备基础信息')
        device_layout = QVBoxLayout()
        
        hostname_layout = QHBoxLayout()
        hostname_label = QLabel('设备主机名:')
        hostname_label.setFixedWidth(100)
        self.hostname = QLineEdit()
        hostname_layout.addWidget(hostname_label)
        hostname_layout.addWidget(self.hostname)
        device_layout.addLayout(hostname_layout)
        
        enable_password_layout = QHBoxLayout()
        enable_password_label = QLabel('enable 特权密码:')
        enable_password_label.setFixedWidth(100)
        self.enable_password = QLineEdit()
        self.enable_password.setEchoMode(QLineEdit.Password)
        enable_password_layout.addWidget(enable_password_label)
        enable_password_layout.addWidget(self.enable_password)
        device_layout.addLayout(enable_password_layout)
        
        console_password_layout = QHBoxLayout()
        console_password_label = QLabel('Console 登录密码:')
        console_password_label.setFixedWidth(100)
        self.console_password = QLineEdit()
        self.console_password.setEchoMode(QLineEdit.Password)
        console_password_layout.addWidget(console_password_label)
        console_password_layout.addWidget(self.console_password)
        device_layout.addLayout(console_password_layout)
        
        system_time_layout = QHBoxLayout()
        system_time_label = QLabel('系统时间:')
        system_time_label.setFixedWidth(100)
        self.system_time = QLineEdit()
        system_time_layout.addWidget(system_time_label)
        system_time_layout.addWidget(self.system_time)
        device_layout.addLayout(system_time_layout)
        
        device_info.setLayout(device_layout)
        basic_layout.addWidget(device_info)
        
        # VLAN 基础配置
        vlan_config = QGroupBox('VLAN 基础配置')
        vlan_layout = QVBoxLayout()
        
        business_vlan_layout = QHBoxLayout()
        business_vlan_label = QLabel('业务 VLAN ID:')
        business_vlan_label.setFixedWidth(100)
        self.business_vlan = QLineEdit()
        business_vlan_layout.addWidget(business_vlan_label)
        business_vlan_layout.addWidget(self.business_vlan)
        vlan_layout.addLayout(business_vlan_layout)
        
        business_vlan_name_layout = QHBoxLayout()
        business_vlan_name_label = QLabel('业务 VLAN 名称:')
        business_vlan_name_label.setFixedWidth(100)
        self.business_vlan_name = QLineEdit()
        business_vlan_name_layout.addWidget(business_vlan_name_label)
        business_vlan_name_layout.addWidget(self.business_vlan_name)
        vlan_layout.addLayout(business_vlan_name_layout)
        
        mgmt_vlan_layout = QHBoxLayout()
        mgmt_vlan_label = QLabel('管理 VLAN ID:')
        mgmt_vlan_label.setFixedWidth(100)
        self.mgmt_vlan = QLineEdit()
        mgmt_vlan_layout.addWidget(mgmt_vlan_label)
        mgmt_vlan_layout.addWidget(self.mgmt_vlan)
        vlan_layout.addLayout(mgmt_vlan_layout)
        
        vlan_config.setLayout(vlan_layout)
        basic_layout.addWidget(vlan_config)
        
        # 管理地址与网关配置
        mgmt_config = QGroupBox('管理地址与网关配置')
        mgmt_layout = QVBoxLayout()
        
        mgmt_ip_layout = QHBoxLayout()
        mgmt_ip_label = QLabel('管理 IP:')
        mgmt_ip_label.setFixedWidth(100)
        self.mgmt_ip = QLineEdit()
        mgmt_ip_layout.addWidget(mgmt_ip_label)
        mgmt_ip_layout.addWidget(self.mgmt_ip)
        # 添加小字提示
        hint_label = QLabel('输入示例：192.168.0.2')
        hint_label.setStyleSheet('color: #165DFF; font-size: 12px;')
        mgmt_ip_layout.addWidget(hint_label)
        mgmt_layout.addLayout(mgmt_ip_layout)
        
        subnet_mask_layout = QHBoxLayout()
        subnet_mask_label = QLabel('子网掩码:')
        subnet_mask_label.setFixedWidth(100)
        self.subnet_mask = QLineEdit()
        subnet_mask_layout.addWidget(subnet_mask_label)
        subnet_mask_layout.addWidget(self.subnet_mask)
        # 添加小字提示
        hint_label = QLabel('输入示例：255.255.255.0')
        hint_label.setStyleSheet('color: #165DFF; font-size: 12px;')
        subnet_mask_layout.addWidget(hint_label)
        mgmt_layout.addLayout(subnet_mask_layout)
        
        gateway_layout = QHBoxLayout()
        gateway_label = QLabel('默认网关地址:')
        gateway_label.setFixedWidth(100)
        self.gateway = QLineEdit()
        gateway_layout.addWidget(gateway_label)
        gateway_layout.addWidget(self.gateway)
        # 添加小字提示
        hint_label = QLabel('输入示例：192.168.0.1')
        hint_label.setStyleSheet('color: #000000; font-size: 12px;')
        gateway_layout.addWidget(hint_label)
        mgmt_layout.addLayout(gateway_layout)
        
        mgmt_config.setLayout(mgmt_layout)
        basic_layout.addWidget(mgmt_config)
        
        # 远程登录配置
        remote_config = QGroupBox('远程登录配置')
        remote_layout = QVBoxLayout()
        
        ssh_user_layout = QHBoxLayout()
        ssh_user_label = QLabel('SSH 用户名:')
        ssh_user_label.setFixedWidth(100)
        self.ssh_user = QLineEdit()
        ssh_user_layout.addWidget(ssh_user_label)
        ssh_user_layout.addWidget(self.ssh_user)
        remote_layout.addLayout(ssh_user_layout)
        
        ssh_pwd_layout = QHBoxLayout()
        ssh_pwd_label = QLabel('SSH 密码:')
        ssh_pwd_label.setFixedWidth(100)
        self.ssh_pwd = QLineEdit()
        self.ssh_pwd.setEchoMode(QLineEdit.Password)
        ssh_pwd_layout.addWidget(ssh_pwd_label)
        ssh_pwd_layout.addWidget(self.ssh_pwd)
        remote_layout.addLayout(ssh_pwd_layout)
        
        telnet_pwd_layout = QHBoxLayout()
        telnet_pwd_label = QLabel('Telnet 密码:')
        telnet_pwd_label.setFixedWidth(100)
        self.telnet_pwd = QLineEdit()
        self.telnet_pwd.setEchoMode(QLineEdit.Password)
        telnet_pwd_layout.addWidget(telnet_pwd_label)
        telnet_pwd_layout.addWidget(self.telnet_pwd)
        remote_layout.addLayout(telnet_pwd_layout)
        
        remote_config.setLayout(remote_layout)
        basic_layout.addWidget(remote_config)
        
        basic_config.setLayout(basic_layout)
        layout.addWidget(basic_config)
        
        # 面板2：端口与上联配置
        port_config = QGroupBox('端口与上联配置')
        port_layout = QVBoxLayout()
        
        # 客户端接入端口配置
        access_port_config = QGroupBox('客户端接入端口配置')
        access_port_layout = QVBoxLayout()
        
        access_port1_layout = QHBoxLayout()
        access_port1_label = QLabel('接入端口范围 1:')
        access_port1_label.setFixedWidth(100)
        self.access_port1 = QLineEdit()
        access_port1_layout.addWidget(access_port1_label)
        access_port1_layout.addWidget(self.access_port1)
        access_port_layout.addLayout(access_port1_layout)
        
        access_vlan1_layout = QHBoxLayout()
        access_vlan1_label = QLabel('接入 VLAN 1:')
        access_vlan1_label.setFixedWidth(100)
        self.access_vlan1 = QLineEdit()
        access_vlan1_layout.addWidget(access_vlan1_label)
        access_vlan1_layout.addWidget(self.access_vlan1)
        access_port_layout.addLayout(access_vlan1_layout)
        
        access_port2_layout = QHBoxLayout()
        access_port2_label = QLabel('接入端口范围 2:')
        access_port2_label.setFixedWidth(100)
        self.access_port2 = QLineEdit()
        access_port2_layout.addWidget(access_port2_label)
        access_port2_layout.addWidget(self.access_port2)
        access_port_layout.addLayout(access_port2_layout)
        
        access_vlan2_layout = QHBoxLayout()
        access_vlan2_label = QLabel('接入 VLAN 2:')
        access_vlan2_label.setFixedWidth(100)
        self.access_vlan2 = QLineEdit()
        access_vlan2_layout.addWidget(access_vlan2_label)
        access_vlan2_layout.addWidget(self.access_vlan2)
        access_port_layout.addLayout(access_vlan2_layout)
        
        access_port_config.setLayout(access_port_layout)
        port_layout.addWidget(access_port_config)
        
        # 上联 Trunk 端口配置
        trunk_config = QGroupBox('上联 Trunk 端口配置')
        trunk_layout = QVBoxLayout()
        
        up_port_layout = QHBoxLayout()
        up_port_label = QLabel('上联端口号:')
        up_port_label.setFixedWidth(100)
        self.up_port = QLineEdit()
        up_port_layout.addWidget(up_port_label)
        up_port_layout.addWidget(self.up_port)
        trunk_layout.addLayout(up_port_layout)
        
        port_layout_layout = QHBoxLayout()
        port_label = QLabel('端口号:')
        port_label.setFixedWidth(100)
        self.port = QLineEdit()
        port_layout_layout.addWidget(port_label)
        port_layout_layout.addWidget(self.port)
        trunk_layout.addLayout(port_layout_layout)
        
        port_speed_layout = QHBoxLayout()
        port_speed_label = QLabel('端口速率:')
        port_speed_label.setFixedWidth(100)
        self.port_speed = QComboBox()
        self.port_speed.addItems(['10M', '100M', '1000M'])
        port_speed_layout.addWidget(port_speed_label)
        port_speed_layout.addWidget(self.port_speed)
        trunk_layout.addLayout(port_speed_layout)
        
        duplex_mode_layout = QHBoxLayout()
        duplex_mode_label = QLabel('双工模式:')
        duplex_mode_label.setFixedWidth(100)
        self.duplex_mode = QComboBox()
        self.duplex_mode.addItems(['auto', 'full', 'half'])
        duplex_mode_layout.addWidget(duplex_mode_label)
        duplex_mode_layout.addWidget(self.duplex_mode)
        trunk_layout.addLayout(duplex_mode_layout)
        
        optic_port_layout = QHBoxLayout()
        optic_port_label = QLabel('光电端口号:')
        optic_port_label.setFixedWidth(100)
        self.optic_port = QLineEdit()
        optic_port_layout.addWidget(optic_port_label)
        optic_port_layout.addWidget(self.optic_port)
        trunk_layout.addLayout(optic_port_layout)
        
        medium_type_layout = QHBoxLayout()
        medium_type_label = QLabel('光电模式:')
        medium_type_label.setFixedWidth(100)
        self.medium_type = QComboBox()
        self.medium_type.addItems(['copper', 'fiber'])
        medium_type_layout.addWidget(medium_type_label)
        medium_type_layout.addWidget(self.medium_type)
        trunk_layout.addLayout(medium_type_layout)
        
        trunk_config.setLayout(trunk_layout)
        port_layout.addWidget(trunk_config)
        
        # 链路聚合配置
        agg_config = QGroupBox('链路聚合配置')
        agg_layout = QVBoxLayout()
        
        agg_port_range_layout = QHBoxLayout()
        agg_port_range_label = QLabel('聚合端口范围:')
        agg_port_range_label.setFixedWidth(100)
        self.agg_port_range = QLineEdit()
        agg_port_range_layout.addWidget(agg_port_range_label)
        agg_port_range_layout.addWidget(self.agg_port_range)
        agg_layout.addLayout(agg_port_range_layout)
        
        agg_id_layout = QHBoxLayout()
        agg_id_label = QLabel('聚合组号:')
        agg_id_label.setFixedWidth(100)
        self.agg_id = QLineEdit()
        agg_id_layout.addWidget(agg_id_label)
        agg_id_layout.addWidget(self.agg_id)
        agg_layout.addLayout(agg_id_layout)
        
        agg_mode_layout = QHBoxLayout()
        agg_mode_label = QLabel('聚合模式:')
        agg_mode_label.setFixedWidth(100)
        self.agg_mode = QComboBox()
        self.agg_mode.addItems(['静态', '动态'])
        agg_mode_layout.addWidget(agg_mode_label)
        agg_mode_layout.addWidget(self.agg_mode)
        agg_layout.addLayout(agg_mode_layout)
        
        agg_config.setLayout(agg_layout)
        port_layout.addWidget(agg_config)
        
        port_config.setLayout(port_layout)
        layout.addWidget(port_config)
        
        # 面板3：安全与防环配置
        security_config = QGroupBox('安全与防环配置')
        security_layout = QVBoxLayout()
        
        # DHCP Snooping 功能
        dhcp_snooping_config = QGroupBox('DHCP Snooping 功能')
        dhcp_snooping_layout = QVBoxLayout()
        
        trust_port_layout = QHBoxLayout()
        trust_port_label = QLabel('信任端口号:')
        trust_port_label.setFixedWidth(100)
        self.trust_port = QLineEdit()
        trust_port_layout.addWidget(trust_port_label)
        trust_port_layout.addWidget(self.trust_port)
        dhcp_snooping_layout.addLayout(trust_port_layout)
        
        dhcp_snooping_config.setLayout(dhcp_snooping_layout)
        security_layout.addWidget(dhcp_snooping_config)
        
        # 接口防环配置
        loop_config = QGroupBox('接口防环配置')
        loop_layout = QVBoxLayout()
        
        loop_port_layout = QHBoxLayout()
        loop_port_label = QLabel('防环端口范围:')
        loop_port_label.setFixedWidth(100)
        self.loop_port = QLineEdit()
        loop_port_layout.addWidget(loop_port_label)
        loop_port_layout.addWidget(self.loop_port)
        loop_layout.addLayout(loop_port_layout)
        
        loop_config.setLayout(loop_layout)
        security_layout.addWidget(loop_config)
        
        # 生成树 MSTP 配置
        mstp_config = QGroupBox('生成树 MSTP 配置')
        mstp_layout = QVBoxLayout()
        
        mst_vlan1_layout = QHBoxLayout()
        mst_vlan1_label = QLabel('MST 实例 1 VLAN:')
        mst_vlan1_label.setFixedWidth(100)
        self.mst_vlan1 = QLineEdit()
        mst_vlan1_layout.addWidget(mst_vlan1_label)
        mst_vlan1_layout.addWidget(self.mst_vlan1)
        mstp_layout.addLayout(mst_vlan1_layout)
        
        mst_vlan2_layout = QHBoxLayout()
        mst_vlan2_label = QLabel('MST 实例 2 VLAN:')
        mst_vlan2_label.setFixedWidth(100)
        self.mst_vlan2 = QLineEdit()
        mst_vlan2_layout.addWidget(mst_vlan2_label)
        mst_vlan2_layout.addWidget(self.mst_vlan2)
        mstp_layout.addLayout(mst_vlan2_layout)
        
        mst_prio_layout = QHBoxLayout()
        mst_prio_label = QLabel('优先级:')
        mst_prio_label.setFixedWidth(100)
        self.mst_prio = QLineEdit()
        mst_prio_layout.addWidget(mst_prio_label)
        mst_prio_layout.addWidget(self.mst_prio)
        mstp_layout.addLayout(mst_prio_layout)
        
        mstp_config.setLayout(mstp_layout)
        security_layout.addWidget(mstp_config)
        
        # ACL 访问控制列表
        acl_config = QGroupBox('ACL 访问控制列表')
        acl_layout = QVBoxLayout()
        
        allow_segment_layout = QHBoxLayout()
        allow_segment_label = QLabel('允许管理网段:')
        allow_segment_label.setFixedWidth(100)
        self.allow_segment = QLineEdit()
        allow_segment_layout.addWidget(allow_segment_label)
        allow_segment_layout.addWidget(self.allow_segment)
        acl_layout.addLayout(allow_segment_layout)
        
        allow_host_layout = QHBoxLayout()
        allow_host_label = QLabel('允许主机:')
        allow_host_label.setFixedWidth(100)
        self.allow_host = QLineEdit()
        allow_host_layout.addWidget(allow_host_label)
        allow_host_layout.addWidget(self.allow_host)
        acl_layout.addLayout(allow_host_layout)
        
        deny_segment1_layout = QHBoxLayout()
        deny_segment1_label = QLabel('拒绝网段 1:')
        deny_segment1_label.setFixedWidth(100)
        self.deny_segment1 = QLineEdit()
        deny_segment1_layout.addWidget(deny_segment1_label)
        deny_segment1_layout.addWidget(self.deny_segment1)
        acl_layout.addLayout(deny_segment1_layout)
        
        deny_segment2_layout = QHBoxLayout()
        deny_segment2_label = QLabel('拒绝网段 2:')
        deny_segment2_label.setFixedWidth(100)
        self.deny_segment2 = QLineEdit()
        deny_segment2_layout.addWidget(deny_segment2_label)
        deny_segment2_layout.addWidget(self.deny_segment2)
        acl_layout.addLayout(deny_segment2_layout)
        
        acl_config.setLayout(acl_layout)
        security_layout.addWidget(acl_config)
        
        security_config.setLayout(security_layout)
        layout.addWidget(security_config)
        
        # 面板4：运维与调试功能
        maintenance_config = QGroupBox('运维与调试功能')
        maintenance_layout = QVBoxLayout()
        
        # NTP 时钟同步
        ntp_config = QGroupBox('NTP 时钟同步')
        ntp_layout = QVBoxLayout()
        
        ntp_server_layout = QHBoxLayout()
        ntp_server_label = QLabel('NTP 服务器地址:')
        ntp_server_label.setFixedWidth(100)
        self.ntp_server = QLineEdit()
        ntp_server_layout.addWidget(ntp_server_label)
        ntp_server_layout.addWidget(self.ntp_server)
        ntp_layout.addLayout(ntp_server_layout)
        
        ntp_config.setLayout(ntp_layout)
        maintenance_layout.addWidget(ntp_config)
        
        # SNMPv2 配置
        snmp_config = QGroupBox('SNMPv2 配置')
        snmp_layout = QVBoxLayout()
        
        snmp_community_layout = QHBoxLayout()
        snmp_community_label = QLabel('SNMP 只读团体名:')
        snmp_community_label.setFixedWidth(100)
        self.snmp_community = QLineEdit()
        snmp_community_layout.addWidget(snmp_community_label)
        snmp_community_layout.addWidget(self.snmp_community)
        snmp_layout.addLayout(snmp_community_layout)
        
        trap_server_layout = QHBoxLayout()
        trap_server_label = QLabel('Trap 服务器地址:')
        trap_server_label.setFixedWidth(100)
        self.trap_server = QLineEdit()
        trap_server_layout.addWidget(trap_server_label)
        trap_server_layout.addWidget(self.trap_server)
        snmp_layout.addLayout(trap_server_layout)
        
        snmp_config.setLayout(snmp_layout)
        maintenance_layout.addWidget(snmp_config)
        
        # 端口镜像配置
        mirror_config = QGroupBox('端口镜像配置')
        mirror_layout = QVBoxLayout()
        
        mirror_src_layout = QHBoxLayout()
        mirror_src_label = QLabel('镜像源端口:')
        mirror_src_label.setFixedWidth(100)
        self.mirror_src = QLineEdit()
        mirror_src_layout.addWidget(mirror_src_label)
        mirror_src_layout.addWidget(self.mirror_src)
        mirror_layout.addLayout(mirror_src_layout)
        
        mirror_dir_layout = QHBoxLayout()
        mirror_dir_label = QLabel('流量方向:')
        mirror_dir_label.setFixedWidth(100)
        self.mirror_dir = QComboBox()
        self.mirror_dir.addItems(['rx', 'tx', 'both'])
        mirror_dir_layout.addWidget(mirror_dir_label)
        mirror_dir_layout.addWidget(self.mirror_dir)
        mirror_layout.addLayout(mirror_dir_layout)
        
        mirror_dst_layout = QHBoxLayout()
        mirror_dst_label = QLabel('镜像目的端口:')
        mirror_dst_label.setFixedWidth(100)
        self.mirror_dst = QLineEdit()
        mirror_dst_layout.addWidget(mirror_dst_label)
        mirror_dst_layout.addWidget(self.mirror_dst)
        mirror_layout.addLayout(mirror_dst_layout)
        
        mirror_config.setLayout(mirror_layout)
        maintenance_layout.addWidget(mirror_config)
        
        # AAA 本地认证配置
        aaa_config = QGroupBox('AAA 本地认证配置')
        aaa_layout = QVBoxLayout()
        
        aaa_user_layout = QHBoxLayout()
        aaa_user_label = QLabel('AAA 用户名:')
        aaa_user_label.setFixedWidth(100)
        self.aaa_user = QLineEdit()
        aaa_user_layout.addWidget(aaa_user_label)
        aaa_user_layout.addWidget(self.aaa_user)
        aaa_layout.addLayout(aaa_user_layout)
        
        aaa_pwd_layout = QHBoxLayout()
        aaa_pwd_label = QLabel('AAA 密码:')
        aaa_pwd_label.setFixedWidth(100)
        self.aaa_pwd = QLineEdit()
        self.aaa_pwd.setEchoMode(QLineEdit.Password)
        aaa_pwd_layout.addWidget(aaa_pwd_label)
        aaa_pwd_layout.addWidget(self.aaa_pwd)
        aaa_layout.addLayout(aaa_pwd_layout)
        
        aaa_config.setLayout(aaa_layout)
        maintenance_layout.addWidget(aaa_config)
        
        maintenance_config.setLayout(maintenance_layout)
        layout.addWidget(maintenance_config)
        
        self.config_area.setLayout(layout)
        
    def generate_config(self):
        """生成配置脚本"""
        # 这里将实现配置脚本生成逻辑
        config = f"""
# 设备基础信息
<HUAWEI> system-view
[HUAWEI] sysname {self.hostname.text()}
[HUAWEI] super password cipher {self.enable_password.text()}
[HUAWEI] user-interface console 0
[HUAWEI-ui-console0] authentication-mode password
[HUAWEI-ui-console0] set authentication password cipher {self.console_password.text()}
[HUAWEI-ui-console0] quit
[HUAWEI] clock datetime {self.system_time.text()}
[HUAWEI] clock timezone beijing add 08:00

# VLAN 基础配置
[HUAWEI] vlan {self.business_vlan.text()}
[HUAWEI-vlan{self.business_vlan.text()}] name {self.business_vlan_name.text()}
[HUAWEI-vlan{self.business_vlan.text()}] quit
[HUAWEI] vlan {self.mgmt_vlan.text()}
[HUAWEI-vlan{self.mgmt_vlan.text()}] name manage
[HUAWEI-vlan{self.mgmt_vlan.text()}] quit

# 管理地址与网关配置
[HUAWEI] interface Vlanif {self.mgmt_vlan.text()}
[HUAWEI-Vlanif{self.mgmt_vlan.text()}] ip address {self.mgmt_ip.text()} {self.subnet_mask.text()}
[HUAWEI-Vlanif{self.mgmt_vlan.text()}] quit
[HUAWEI] ip route-static 0.0.0.0 0.0.0.0 {self.gateway.text()}

# 远程登录配置
[HUAWEI] stelnet server enable
[HUAWEI] user-interface vty 0 4
[HUAWEI-ui-vty0-4] authentication-mode aaa
[HUAWEI-ui-vty0-4] protocol inbound ssh
[HUAWEI-ui-vty0-4] quit
[HUAWEI] aaa
[HUAWEI-aaa] local-user {self.ssh_user.text()} password irreversible-cipher {self.ssh_pwd.text()}
[HUAWEI-aaa] local-user {self.ssh_user.text()} service-type ssh
[HUAWEI-aaa] local-user {self.ssh_user.text()} privilege level 15
[HUAWEI-aaa] quit
[HUAWEI] rsa local-key-pair create

# 端口与上联配置
[HUAWEI] port-group 1
[HUAWEI-port-group1] group-member GigabitEthernet 0/0/1 to 0/0/12
[HUAWEI-port-group1] port link-type access
[HUAWEI-port-group1] port default vlan {self.access_vlan1.text()}
[HUAWEI-port-group1] quit
[HUAWEI] port-group 2
[HUAWEI-port-group2] group-member GigabitEthernet 0/0/13 to 0/0/24
[HUAWEI-port-group2] port link-type access
[HUAWEI-port-group2] port default vlan {self.access_vlan2.text()}
[HUAWEI-port-group2] quit

[HUAWEI] interface GigabitEthernet {self.up_port.text()}
[HUAWEI-GigabitEthernet{self.up_port.text()}] port link-type trunk
[HUAWEI-GigabitEthernet{self.up_port.text()}] port trunk allow-pass vlan all
[HUAWEI-GigabitEthernet{self.up_port.text()}] quit

# 安全与防环配置
[HUAWEI] dhcp enable
[HUAWEI] dhcp snooping enable
[HUAWEI] interface {self.trust_port.text()}
[HUAWEI-{self.trust_port.text()}] dhcp snooping trusted
[HUAWEI-{self.trust_port.text()}] quit

[HUAWEI] stp enable
[HUAWEI] stp mode mstp
[HUAWEI] stp region-configuration
[HUAWEI-mst-region] instance 1 vlan {self.mst_vlan1.text()}
[HUAWEI-mst-region] instance 2 vlan {self.mst_vlan2.text()}
[HUAWEI-mst-region] active region-configuration
[HUAWEI-mst-region] quit
[HUAWEI] stp instance 1 priority {self.mst_prio.text()}

# 运维与调试功能
[HUAWEI] ntp server {self.ntp_server.text()}
[HUAWEI] ntp source Vlanif {self.mgmt_vlan.text()}

[HUAWEI] snmp-agent
[HUAWEI] snmp-agent sys-info version v2c
[HUAWEI] snmp-agent community read {self.snmp_community.text()}
[HUAWEI] snmp-agent target-host trap address udp-domain {self.trap_server.text()} params securityname {self.snmp_community.text()} v2c
[HUAWEI] snmp-agent trap enable

[HUAWEI] observe-port 1 interface {self.mirror_dst.text()}
[HUAWEI] interface {self.mirror_src.text()}
[HUAWEI-{self.mirror_src.text()}] port-mirroring to observe-port 1 {self.mirror_dir.currentText()}
[HUAWEI-{self.mirror_src.text()}] quit

[HUAWEI] aaa
[HUAWEI-aaa] local-user {self.aaa_user.text()} password irreversible-cipher {self.aaa_pwd.text()}
[HUAWEI-aaa] local-user {self.aaa_user.text()} privilege level 15
[HUAWEI-aaa] local-user {self.aaa_user.text()} service-type terminal ssh telnet
[HUAWEI-aaa] quit

[HUAWEI] save
        """
        self.code_editor.setText(config)
        
    def copy_script(self):
        """复制脚本到剪贴板"""
        import pyperclip
        pyperclip.copy(self.code_editor.toPlainText())
        
    def export_config(self):
        """导出配置文件"""
        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "导出配置文件", "", "配置文件 (*.txt);;所有文件 (*.*)", options=options)
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
        
    def reset_form(self):
        """重置表单"""
        # 重置所有输入框
        self.hostname.clear()
        self.enable_password.clear()
        self.console_password.clear()
        self.system_time.clear()
        self.business_vlan.clear()
        self.business_vlan_name.clear()
        self.mgmt_vlan.clear()
        self.mgmt_ip.clear()
        self.subnet_mask.clear()
        self.gateway.clear()
        self.ssh_user.clear()
        self.ssh_pwd.clear()
        self.telnet_pwd.clear()
        self.access_port1.clear()
        self.access_vlan1.clear()
        self.access_port2.clear()
        self.access_vlan2.clear()
        self.up_port.clear()
        self.port.clear()
        self.optic_port.clear()
        self.agg_port_range.clear()
        self.agg_id.clear()
        self.trust_port.clear()
        self.loop_port.clear()
        self.mst_vlan1.clear()
        self.mst_vlan2.clear()
        self.mst_prio.clear()
        self.allow_segment.clear()
        self.allow_host.clear()
        self.deny_segment1.clear()
        self.deny_segment2.clear()
        self.ntp_server.clear()
        self.snmp_community.clear()
        self.trap_server.clear()
        self.mirror_src.clear()
        self.mirror_dst.clear()
        self.aaa_user.clear()
        self.aaa_pwd.clear()
        # 重置代码编辑器
        self.code_editor.clear()