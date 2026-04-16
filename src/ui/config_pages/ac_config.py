from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QGroupBox
from ui.config_pages.base_config_page import BaseConfigPage

class ACConfig(BaseConfigPage):
    def __init__(self, parent, vendor):
        super().__init__(parent, vendor, 'ac')
        self.title.setText('AC配置')
        self.init_config_area()
        
    def init_config_area(self):
        """初始化配置区域"""
        layout = QVBoxLayout()
        
        # 面板1：基础管理配置
        basic_config = QGroupBox('基础管理配置')
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
        
        enable_secret_layout = QHBoxLayout()
        enable_secret_label = QLabel('enable 加密密码:')
        enable_secret_label.setFixedWidth(100)
        self.enable_secret = QLineEdit()
        self.enable_secret.setEchoMode(QLineEdit.Password)
        enable_secret_layout.addWidget(enable_secret_label)
        enable_secret_layout.addWidget(self.enable_secret)
        device_layout.addLayout(enable_secret_layout)
        
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
        
        ntp_server_layout = QHBoxLayout()
        ntp_server_label = QLabel('NTP 服务器 IP 地址:')
        ntp_server_label.setFixedWidth(100)
        self.ntp_server = QLineEdit()
        ntp_server_layout.addWidget(ntp_server_label)
        ntp_server_layout.addWidget(self.ntp_server)
        device_layout.addLayout(ntp_server_layout)
        
        device_info.setLayout(device_layout)
        basic_layout.addWidget(device_info)
        
        # 管理 VLAN 配置
        mgmt_vlan_config = QGroupBox('管理 VLAN 配置')
        mgmt_vlan_layout = QVBoxLayout()
        
        mgmt_vlan_layout_ = QHBoxLayout()
        mgmt_vlan_label = QLabel('管理 VLAN ID:')
        mgmt_vlan_label.setFixedWidth(100)
        self.mgmt_vlan = QLineEdit()
        mgmt_vlan_layout_.addWidget(mgmt_vlan_label)
        mgmt_vlan_layout_.addWidget(self.mgmt_vlan)
        mgmt_vlan_layout.addLayout(mgmt_vlan_layout_)
        
        mgmt_ip_layout = QHBoxLayout()
        mgmt_ip_label = QLabel('管理 IP 地址:')
        mgmt_ip_label.setFixedWidth(100)
        self.mgmt_ip = QLineEdit()
        mgmt_ip_layout.addWidget(mgmt_ip_label)
        mgmt_ip_layout.addWidget(self.mgmt_ip)
        mgmt_vlan_layout.addLayout(mgmt_ip_layout)
        
        mgmt_mask_layout = QHBoxLayout()
        mgmt_mask_label = QLabel('管理 IP 子网掩码:')
        mgmt_mask_label.setFixedWidth(100)
        self.mgmt_mask = QLineEdit()
        mgmt_mask_layout.addWidget(mgmt_mask_label)
        mgmt_mask_layout.addWidget(self.mgmt_mask)
        mgmt_vlan_layout.addLayout(mgmt_mask_layout)
        
        mgmt_vlan_config.setLayout(mgmt_vlan_layout)
        basic_layout.addWidget(mgmt_vlan_config)
        
        # 远程登录配置
        remote_config = QGroupBox('远程登录配置')
        remote_layout = QVBoxLayout()
        
        ssh_user_layout = QHBoxLayout()
        ssh_user_label = QLabel('SSH 管理员用户名:')
        ssh_user_label.setFixedWidth(100)
        self.ssh_user = QLineEdit()
        ssh_user_layout.addWidget(ssh_user_label)
        ssh_user_layout.addWidget(self.ssh_user)
        remote_layout.addLayout(ssh_user_layout)
        
        ssh_pwd_layout = QHBoxLayout()
        ssh_pwd_label = QLabel('SSH 管理员密码:')
        ssh_pwd_label.setFixedWidth(100)
        self.ssh_pwd = QLineEdit()
        self.ssh_pwd.setEchoMode(QLineEdit.Password)
        ssh_pwd_layout.addWidget(ssh_pwd_label)
        ssh_pwd_layout.addWidget(self.ssh_pwd)
        remote_layout.addLayout(ssh_pwd_layout)
        
        telnet_pwd_layout = QHBoxLayout()
        telnet_pwd_label = QLabel('Telnet 登录密码:')
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
        
        # 面板2：WLAN 业务配置
        wlan_config = QGroupBox('WLAN 业务配置')
        wlan_layout = QVBoxLayout()
        
        # 业务 VLAN 创建
        vlan_create_config = QGroupBox('业务 VLAN 创建')
        vlan_create_layout = QVBoxLayout()
        
        user_vlan_layout = QHBoxLayout()
        user_vlan_label = QLabel('用户业务 VLAN ID:')
        user_vlan_label.setFixedWidth(100)
        self.user_vlan = QLineEdit()
        user_vlan_layout.addWidget(user_vlan_label)
        user_vlan_layout.addWidget(self.user_vlan)
        vlan_create_layout.addLayout(user_vlan_layout)
        
        vlan_create_config.setLayout(vlan_create_layout)
        wlan_layout.addWidget(vlan_create_config)
        
        # AP 管理 VLAN 配置
        ap_mgmt_config = QGroupBox('AP 管理 VLAN 配置')
        ap_mgmt_layout = QVBoxLayout()
        
        ap_mgmt_vlan_layout = QHBoxLayout()
        ap_mgmt_vlan_label = QLabel('AP 管理 VLAN ID:')
        ap_mgmt_vlan_label.setFixedWidth(100)
        self.ap_mgmt_vlan = QLineEdit()
        ap_mgmt_vlan_layout.addWidget(ap_mgmt_vlan_label)
        ap_mgmt_vlan_layout.addWidget(self.ap_mgmt_vlan)
        ap_mgmt_layout.addLayout(ap_mgmt_vlan_layout)
        
        ap_mgmt_ip_layout = QHBoxLayout()
        ap_mgmt_ip_label = QLabel('AP 管理网段 IP:')
        ap_mgmt_ip_label.setFixedWidth(100)
        self.ap_mgmt_ip = QLineEdit()
        ap_mgmt_ip_layout.addWidget(ap_mgmt_ip_label)
        ap_mgmt_ip_layout.addWidget(self.ap_mgmt_ip)
        ap_mgmt_layout.addLayout(ap_mgmt_ip_layout)
        
        ap_mgmt_mask_layout = QHBoxLayout()
        ap_mgmt_mask_label = QLabel('AP 管理网段子网掩码:')
        ap_mgmt_mask_label.setFixedWidth(100)
        self.ap_mgmt_mask = QLineEdit()
        ap_mgmt_mask_layout.addWidget(ap_mgmt_mask_label)
        ap_mgmt_mask_layout.addWidget(self.ap_mgmt_mask)
        ap_mgmt_layout.addLayout(ap_mgmt_mask_layout)
        
        ap_mgmt_config.setLayout(ap_mgmt_layout)
        wlan_layout.addWidget(ap_mgmt_config)
        
        # 无线 SSID 配置
        ssid_config = QGroupBox('无线 SSID 配置')
        ssid_layout = QVBoxLayout()
        
        ssid_name_layout = QHBoxLayout()
        ssid_name_label = QLabel('SSID 名称:')
        ssid_name_label.setFixedWidth(100)
        self.ssid_name = QLineEdit()
        ssid_name_layout.addWidget(ssid_name_label)
        ssid_name_layout.addWidget(self.ssid_name)
        ssid_layout.addLayout(ssid_name_layout)
        
        wlan_id_layout = QHBoxLayout()
        wlan_id_label = QLabel('WLAN ID:')
        wlan_id_label.setFixedWidth(100)
        self.wlan_id = QLineEdit()
        wlan_id_layout.addWidget(wlan_id_label)
        wlan_id_layout.addWidget(self.wlan_id)
        ssid_layout.addLayout(wlan_id_layout)
        
        ssid_vlan_layout = QHBoxLayout()
        ssid_vlan_label = QLabel('SSID 绑定 VLAN ID:')
        ssid_vlan_label.setFixedWidth(100)
        self.ssid_vlan = QLineEdit()
        ssid_vlan_layout.addWidget(ssid_vlan_label)
        ssid_vlan_layout.addWidget(self.ssid_vlan)
        ssid_layout.addLayout(ssid_vlan_layout)
        
        ssid_config.setLayout(ssid_layout)
        wlan_layout.addWidget(ssid_config)
        
        # 无线安全配置
        security_config = QGroupBox('无线安全配置')
        security_layout = QVBoxLayout()
        
        security_mode_layout = QHBoxLayout()
        security_mode_label = QLabel('安全模式:')
        security_mode_label.setFixedWidth(100)
        self.security_mode = QComboBox()
        self.security_mode.addItems(['WPA2-PSK', 'WPA3-PSK'])
        security_mode_layout.addWidget(security_mode_label)
        security_mode_layout.addWidget(self.security_mode)
        security_layout.addLayout(security_mode_layout)
        
        wpa_key_layout = QHBoxLayout()
        wpa_key_label = QLabel('WPA 密钥:')
        wpa_key_label.setFixedWidth(100)
        self.wpa_key = QLineEdit()
        self.wpa_key.setEchoMode(QLineEdit.Password)
        wpa_key_layout.addWidget(wpa_key_label)
        wpa_key_layout.addWidget(self.wpa_key)
        security_layout.addLayout(wpa_key_layout)
        
        security_config.setLayout(security_layout)
        wlan_layout.addWidget(security_config)
        
        # 无线 VAP 模板配置
        vap_config = QGroupBox('无线 VAP 模板配置')
        vap_layout = QVBoxLayout()
        
        vap_name_layout = QHBoxLayout()
        vap_name_label = QLabel('VAP 模板名称:')
        vap_name_label.setFixedWidth(100)
        self.vap_name = QLineEdit()
        vap_name_layout.addWidget(vap_name_label)
        vap_name_layout.addWidget(self.vap_name)
        vap_layout.addLayout(vap_name_layout)
        
        vap_config.setLayout(vap_layout)
        wlan_layout.addWidget(vap_config)
        
        # 无线 AP 组配置
        ap_group_config = QGroupBox('无线 AP 组配置')
        ap_group_layout = QVBoxLayout()
        
        ap_group_name_layout = QHBoxLayout()
        ap_group_name_label = QLabel('AP 组名称:')
        ap_group_name_label.setFixedWidth(100)
        self.ap_group_name = QLineEdit()
        ap_group_name_layout.addWidget(ap_group_name_label)
        ap_group_name_layout.addWidget(self.ap_group_name)
        ap_group_layout.addLayout(ap_group_name_layout)
        
        ap_group_config.setLayout(ap_group_layout)
        wlan_layout.addWidget(ap_group_config)
        
        # 无线射频配置
        radio_config = QGroupBox('无线射频配置')
        radio_layout = QVBoxLayout()
        
        radio_band_layout = QHBoxLayout()
        radio_band_label = QLabel('射频频段:')
        radio_band_label.setFixedWidth(100)
        self.radio_band = QComboBox()
        self.radio_band.addItems(['2.4GHz', '5GHz'])
        radio_band_layout.addWidget(radio_band_label)
        radio_band_layout.addWidget(self.radio_band)
        radio_layout.addLayout(radio_band_layout)
        
        channel_layout = QHBoxLayout()
        channel_label = QLabel('信道:')
        channel_label.setFixedWidth(100)
        self.channel = QLineEdit()
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.channel)
        radio_layout.addLayout(channel_layout)
        
        power_level_layout = QHBoxLayout()
        power_level_label = QLabel('发射功率:')
        power_level_label.setFixedWidth(100)
        self.power_level = QLineEdit()
        power_level_layout.addWidget(power_level_label)
        power_level_layout.addWidget(self.power_level)
        radio_layout.addLayout(power_level_layout)
        
        radio_config.setLayout(radio_layout)
        wlan_layout.addWidget(radio_config)
        
        wlan_config.setLayout(wlan_layout)
        layout.addWidget(wlan_config)
        
        # 面板3：端口与上联配置
        port_config = QGroupBox('端口与上联配置')
        port_layout = QVBoxLayout()
        
        # 上联 Trunk 端口配置
        trunk_config = QGroupBox('上联 Trunk 端口配置')
        trunk_layout = QVBoxLayout()
        
        up_port_layout = QHBoxLayout()
        up_port_label = QLabel('上联物理端口号:')
        up_port_label.setFixedWidth(100)
        self.up_port = QLineEdit()
        up_port_layout.addWidget(up_port_label)
        up_port_layout.addWidget(self.up_port)
        trunk_layout.addLayout(up_port_layout)
        
        trunk_config.setLayout(trunk_layout)
        port_layout.addWidget(trunk_config)
        
        # 下联 AP 接入端口配置
        ap_port_config = QGroupBox('下联 AP 接入端口配置')
        ap_port_layout = QVBoxLayout()
        
        ap_port_range_layout = QHBoxLayout()
        ap_port_range_label = QLabel('AP 接入端口范围:')
        ap_port_range_label.setFixedWidth(100)
        self.ap_port_range = QLineEdit()
        ap_port_range_layout.addWidget(ap_port_range_label)
        ap_port_range_layout.addWidget(self.ap_port_range)
        ap_port_layout.addLayout(ap_port_range_layout)
        
        ap_port_config.setLayout(ap_port_layout)
        port_layout.addWidget(ap_port_config)
        
        port_config.setLayout(port_layout)
        layout.addWidget(port_config)
        
        # 面板4：三层网关与路由配置
        route_config = QGroupBox('三层网关与路由配置')
        route_layout = QVBoxLayout()
        
        # 业务 VLANIF 三层网关配置
        vlanif_config = QGroupBox('业务 VLANIF 三层网关配置')
        vlanif_layout = QVBoxLayout()
        
        user_gw_layout = QHBoxLayout()
        user_gw_label = QLabel('用户网关 IP 地址:')
        user_gw_label.setFixedWidth(100)
        self.user_gw = QLineEdit()
        user_gw_layout.addWidget(user_gw_label)
        user_gw_layout.addWidget(self.user_gw)
        vlanif_layout.addLayout(user_gw_layout)
        
        user_mask_layout = QHBoxLayout()
        user_mask_label = QLabel('用户网段子网掩码:')
        user_mask_label.setFixedWidth(100)
        self.user_mask = QLineEdit()
        user_mask_layout.addWidget(user_mask_label)
        user_mask_layout.addWidget(self.user_mask)
        vlanif_layout.addLayout(user_mask_layout)
        
        vlanif_config.setLayout(vlanif_layout)
        route_layout.addWidget(vlanif_config)
        
        # 静态路由配置
        static_route_config = QGroupBox('静态路由配置')
        static_route_layout = QVBoxLayout()
        
        dst_net1_layout = QHBoxLayout()
        dst_net1_label = QLabel('目的网段 1:')
        dst_net1_label.setFixedWidth(100)
        self.dst_net1 = QLineEdit()
        dst_net1_layout.addWidget(dst_net1_label)
        dst_net1_layout.addWidget(self.dst_net1)
        static_route_layout.addLayout(dst_net1_layout)
        
        dst_mask1_layout = QHBoxLayout()
        dst_mask1_label = QLabel('目的网段子网掩码 1:')
        dst_mask1_label.setFixedWidth(100)
        self.dst_mask1 = QLineEdit()
        dst_mask1_layout.addWidget(dst_mask1_label)
        dst_mask1_layout.addWidget(self.dst_mask1)
        static_route_layout.addLayout(dst_mask1_layout)
        
        nh1_layout = QHBoxLayout()
        nh1_label = QLabel('下一跳 1:')
        nh1_label.setFixedWidth(100)
        self.nh1 = QLineEdit()
        nh1_layout.addWidget(nh1_label)
        nh1_layout.addWidget(self.nh1)
        static_route_layout.addLayout(nh1_layout)
        
        default_nh_layout = QHBoxLayout()
        default_nh_label = QLabel('默认路由下一跳:')
        default_nh_label.setFixedWidth(100)
        self.default_nh = QLineEdit()
        default_nh_layout.addWidget(default_nh_label)
        default_nh_layout.addWidget(self.default_nh)
        static_route_layout.addLayout(default_nh_layout)
        
        static_route_config.setLayout(static_route_layout)
        route_layout.addWidget(static_route_config)
        
        route_config.setLayout(route_layout)
        layout.addWidget(route_config)
        
        # 面板5：DHCP 服务配置
        dhcp_config = QGroupBox('DHCP 服务配置')
        dhcp_layout = QVBoxLayout()
        
        # DHCP Server 全局配置
        dhcp_server_config = QGroupBox('DHCP Server 全局配置')
        dhcp_server_layout = QVBoxLayout()
        
        user_ex_start_layout = QHBoxLayout()
        user_ex_start_label = QLabel('用户网段排除起始 IP:')
        user_ex_start_label.setFixedWidth(100)
        self.user_ex_start = QLineEdit()
        user_ex_start_layout.addWidget(user_ex_start_label)
        user_ex_start_layout.addWidget(self.user_ex_start)
        dhcp_server_layout.addLayout(user_ex_start_layout)
        
        user_ex_end_layout = QHBoxLayout()
        user_ex_end_label = QLabel('用户网段排除结束 IP:')
        user_ex_end_label.setFixedWidth(100)
        self.user_ex_end = QLineEdit()
        user_ex_end_layout.addWidget(user_ex_end_label)
        user_ex_end_layout.addWidget(self.user_ex_end)
        dhcp_server_layout.addLayout(user_ex_end_layout)
        
        ap_ex_start_layout = QHBoxLayout()
        ap_ex_start_label = QLabel('AP 管理网段排除起始 IP:')
        ap_ex_start_label.setFixedWidth(100)
        self.ap_ex_start = QLineEdit()
        ap_ex_start_layout.addWidget(ap_ex_start_label)
        ap_ex_start_layout.addWidget(self.ap_ex_start)
        dhcp_server_layout.addLayout(ap_ex_start_layout)
        
        ap_ex_end_layout = QHBoxLayout()
        ap_ex_end_label = QLabel('AP 管理网段排除结束 IP:')
        ap_ex_end_label.setFixedWidth(100)
        self.ap_ex_end = QLineEdit()
        ap_ex_end_layout.addWidget(ap_ex_end_label)
        ap_ex_end_layout.addWidget(self.ap_ex_end)
        dhcp_server_layout.addLayout(ap_ex_end_layout)
        
        user_pool_layout = QHBoxLayout()
        user_pool_label = QLabel('用户地址池名称:')
        user_pool_label.setFixedWidth(100)
        self.user_pool = QLineEdit()
        user_pool_layout.addWidget(user_pool_label)
        user_pool_layout.addWidget(self.user_pool)
        dhcp_server_layout.addLayout(user_pool_layout)
        
        ap_pool_layout = QHBoxLayout()
        ap_pool_label = QLabel('AP 地址池名称:')
        ap_pool_label.setFixedWidth(100)
        self.ap_pool = QLineEdit()
        ap_pool_layout.addWidget(ap_pool_label)
        ap_pool_layout.addWidget(self.ap_pool)
        dhcp_server_layout.addLayout(ap_pool_layout)
        
        dns1_layout = QHBoxLayout()
        dns1_label = QLabel('主 DNS:')
        dns1_label.setFixedWidth(100)
        self.dns1 = QLineEdit()
        dns1_layout.addWidget(dns1_label)
        dns1_layout.addWidget(self.dns1)
        dhcp_server_layout.addLayout(dns1_layout)
        
        dns2_layout = QHBoxLayout()
        dns2_label = QLabel('备 DNS:')
        dns2_label.setFixedWidth(100)
        self.dns2 = QLineEdit()
        dns2_layout.addWidget(dns2_label)
        dns2_layout.addWidget(self.dns2)
        dhcp_server_layout.addLayout(dns2_layout)
        
        dhcp_server_config.setLayout(dhcp_server_layout)
        dhcp_layout.addWidget(dhcp_server_config)
        
        dhcp_config.setLayout(dhcp_layout)
        layout.addWidget(dhcp_config)
        
        # 面板6：安全与运维监控配置
        security_maintenance_config = QGroupBox('安全与运维监控配置')
        security_maintenance_layout = QVBoxLayout()
        
        # ACL 访问控制配置
        acl_config = QGroupBox('ACL 访问控制配置')
        acl_layout = QVBoxLayout()
        
        manage_net_layout = QHBoxLayout()
        manage_net_label = QLabel('允许管理 IP 网段:')
        manage_net_label.setFixedWidth(100)
        self.manage_net = QLineEdit()
        manage_net_layout.addWidget(manage_net_label)
        manage_net_layout.addWidget(self.manage_net)
        acl_layout.addLayout(manage_net_layout)
        
        manage_wild_layout = QHBoxLayout()
        manage_wild_label = QLabel('允许管理网段反掩码:')
        manage_wild_label.setFixedWidth(100)
        self.manage_wild = QLineEdit()
        manage_wild_layout.addWidget(manage_wild_label)
        manage_wild_layout.addWidget(self.manage_wild)
        acl_layout.addLayout(manage_wild_layout)
        
        acl_config.setLayout(acl_layout)
        security_maintenance_layout.addWidget(acl_config)
        
        # SNMPv2c 配置
        snmp_config = QGroupBox('SNMPv2c 配置')
        snmp_layout = QVBoxLayout()
        
        snmp_ro_community_layout = QHBoxLayout()
        snmp_ro_community_label = QLabel('SNMP 只读团体名:')
        snmp_ro_community_label.setFixedWidth(100)
        self.snmp_ro_community = QLineEdit()
        snmp_ro_community_layout.addWidget(snmp_ro_community_label)
        snmp_ro_community_layout.addWidget(self.snmp_ro_community)
        snmp_layout.addLayout(snmp_ro_community_layout)
        
        trap_server_layout = QHBoxLayout()
        trap_server_label = QLabel('Trap 服务器 IP:')
        trap_server_label.setFixedWidth(100)
        self.trap_server = QLineEdit()
        trap_server_layout.addWidget(trap_server_label)
        trap_server_layout.addWidget(self.trap_server)
        snmp_layout.addLayout(trap_server_layout)
        
        trap_community_layout = QHBoxLayout()
        trap_community_label = QLabel('Trap 团体名:')
        trap_community_label.setFixedWidth(100)
        self.trap_community = QLineEdit()
        trap_community_layout.addWidget(trap_community_label)
        trap_community_layout.addWidget(self.trap_community)
        snmp_layout.addLayout(trap_community_layout)
        
        snmp_config.setLayout(snmp_layout)
        security_maintenance_layout.addWidget(snmp_config)
        
        security_maintenance_config.setLayout(security_maintenance_layout)
        layout.addWidget(security_maintenance_config)
        
        self.config_area.setLayout(layout)
        
    def generate_config(self):
        """生成配置脚本"""
        # 这里将实现配置脚本生成逻辑
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {self.hostname.text()}
enable secret {self.enable_secret.text()}
line console 0
 password {self.console_password.text()}
 login
 exec-timeout 10 0
 logging synchronous
exit
clock set {self.system_time.text()}
ntp server {self.ntp_server.text()}
ntp update-calendar

# 管理 VLAN 配置
vlan {self.mgmt_vlan.text()}
 name Management_VLAN
exit
interface Vlan {self.mgmt_vlan.text()}
 ip address {self.mgmt_ip.text()} {self.mgmt_mask.text()}
 no shutdown
exit

# 远程登录配置
ip ssh version 2
username {self.ssh_user.text()} privilege 15 password {self.ssh_pwd.text()}
crypto key generate rsa modulus 2048
line vty 0 15
 login local
 transport input ssh
 exec-timeout 15 0
exit

# WLAN 业务配置
vlan {self.user_vlan.text()}
 name User_VLAN
exit

vlan {self.ap_mgmt_vlan.text()}
 name AP_Management_VLAN
exit

# 无线 SSID 配置
wlan ssid {self.ssid_name.text()}
 wlan-id {self.wlan_id.text()}
 vlan {self.ssid_vlan.text()}
 security wpa psk set-key ascii 0 {self.wpa_key.text()}
 security wpa wpa2
 exit

# 无线 VAP 模板配置
wlan vap-template {self.vap_name.text()}
 ssid {self.ssid_name.text()}
 bind wlan-id {self.wlan_id.text()}
 exit

# 无线 AP 组配置
wlan ap-group {self.ap_group_name.text()}
 vap-template {self.vap_name.text()} wlan {self.wlan_id.text()}
 exit

# 无线射频配置
wlan radio-2g-profile default
 channel {self.channel.text()}
 power-level {self.power_level.text()}
 exit

wlan radio-5g-profile default
 channel {self.channel.text()}
 power-level {self.power_level.text()}
 exit

# 端口与上联配置
interface GigabitEthernet {self.up_port.text()}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown
exit

interface range {self.ap_port_range.text()}
 switchport mode trunk
 switchport trunk allowed vlan {self.user_vlan.text()},{self.ap_mgmt_vlan.text()}
 no shutdown
exit

# 三层网关与路由配置
interface Vlan {self.user_vlan.text()}
 ip address {self.user_gw.text()} {self.user_mask.text()}
 no shutdown
exit

interface Vlan {self.ap_mgmt_vlan.text()}
 ip address {self.ap_mgmt_ip.text()} {self.ap_mgmt_mask.text()}
 no shutdown
exit

# 静态路由配置
ip route {self.dst_net1.text()} {self.dst_mask1.text()} {self.nh1.text()}
ip route 0.0.0.0 0.0.0.0 {self.default_nh.text()}

# DHCP 服务配置
service dhcp
ip dhcp excluded-address {self.user_ex_start.text()} {self.user_ex_end.text()}
ip dhcp excluded-address {self.ap_ex_start.text()} {self.ap_ex_end.text()}

ip dhcp pool {self.user_pool.text()}
 network {self.user_gw.text()} {self.user_mask.text()}
 default-router {self.user_gw.text()}
 dns-server {self.dns1.text()} {self.dns2.text()}
 lease 7 0 0
exit

ip dhcp pool {self.ap_pool.text()}
 network {self.ap_mgmt_ip.text()} {self.ap_mgmt_mask.text()}
 default-router {self.ap_mgmt_ip.text()}
 dns-server {self.dns1.text()} {self.dns2.text()}
 lease 30 0 0
exit

# 安全与运维监控配置
ip access-list standard 10
 permit {self.manage_net.text()} {self.manage_wild.text()}
 deny any
exit
line vty 0 15
 access-class 10 in
exit

snmp-server community {self.snmp_ro_community.text()} ro
snmp-server host {self.trap_server.text()} traps version 2c {self.trap_community.text()}
snmp-server enable traps

exit
write
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
        self.enable_secret.clear()
        self.console_password.clear()
        self.system_time.clear()
        self.ntp_server.clear()
        self.mgmt_vlan.clear()
        self.mgmt_ip.clear()
        self.mgmt_mask.clear()
        self.ssh_user.clear()
        self.ssh_pwd.clear()
        self.telnet_pwd.clear()
        self.user_vlan.clear()
        self.ap_mgmt_vlan.clear()
        self.ap_mgmt_ip.clear()
        self.ap_mgmt_mask.clear()
        self.ssid_name.clear()
        self.wlan_id.clear()
        self.ssid_vlan.clear()
        self.wpa_key.clear()
        self.vap_name.clear()
        self.ap_group_name.clear()
        self.channel.clear()
        self.power_level.clear()
        self.up_port.clear()
        self.ap_port_range.clear()
        self.user_gw.clear()
        self.user_mask.clear()
        self.dst_net1.clear()
        self.dst_mask1.clear()
        self.nh1.clear()
        self.default_nh.clear()
        self.user_ex_start.clear()
        self.user_ex_end.clear()
        self.ap_ex_start.clear()
        self.ap_ex_end.clear()
        self.user_pool.clear()
        self.ap_pool.clear()
        self.dns1.clear()
        self.dns2.clear()
        self.manage_net.clear()
        self.manage_wild.clear()
        self.snmp_ro_community.clear()
        self.trap_server.clear()
        self.trap_community.clear()
        # 重置代码编辑器
        self.code_editor.clear()