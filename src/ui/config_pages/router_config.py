from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QGroupBox
from ui.config_pages.base_config_page import BaseConfigPage

class RouterConfig(BaseConfigPage):
    def __init__(self, parent, vendor):
        super().__init__(parent, vendor, 'router')
        self.title.setText('路由器配置')
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
        
        device_info.setLayout(device_layout)
        basic_layout.addWidget(device_info)
        
        # 本地登录配置
        local_login_config = QGroupBox('本地登录配置')
        local_login_layout = QVBoxLayout()
        
        console_password_layout = QHBoxLayout()
        console_password_label = QLabel('Console 登录密码:')
        console_password_label.setFixedWidth(100)
        self.console_password = QLineEdit()
        self.console_password.setEchoMode(QLineEdit.Password)
        console_password_layout.addWidget(console_password_label)
        console_password_layout.addWidget(self.console_password)
        local_login_layout.addLayout(console_password_layout)
        
        system_time_layout = QHBoxLayout()
        system_time_label = QLabel('系统时间:')
        system_time_label.setFixedWidth(100)
        self.system_time = QLineEdit()
        system_time_layout.addWidget(system_time_label)
        system_time_layout.addWidget(self.system_time)
        local_login_layout.addLayout(system_time_layout)
        
        ntp_server_layout = QHBoxLayout()
        ntp_server_label = QLabel('NTP 服务器 IP 地址:')
        ntp_server_label.setFixedWidth(100)
        self.ntp_server = QLineEdit()
        ntp_server_layout.addWidget(ntp_server_label)
        ntp_server_layout.addWidget(self.ntp_server)
        local_login_layout.addLayout(ntp_server_layout)
        
        local_login_config.setLayout(local_login_layout)
        basic_layout.addWidget(local_login_config)
        
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
        
        # 面板2：三层接口配置
        interface_config = QGroupBox('三层接口配置（纯路由 WAN/LAN 口）')
        interface_layout = QVBoxLayout()
        
        # 上联互联网 WAN 口配置
        wan_config = QGroupBox('上联互联网 WAN 口配置')
        wan_layout = QVBoxLayout()
        
        wan_port_layout = QHBoxLayout()
        wan_port_label = QLabel('上联 WAN 物理端口:')
        wan_port_label.setFixedWidth(100)
        self.wan_port = QLineEdit()
        wan_port_layout.addWidget(wan_port_label)
        wan_port_layout.addWidget(self.wan_port)
        wan_layout.addLayout(wan_port_layout)
        
        wan_ip_layout = QHBoxLayout()
        wan_ip_label = QLabel('WAN 口 IP 地址:')
        wan_ip_label.setFixedWidth(100)
        self.wan_ip = QLineEdit()
        wan_ip_layout.addWidget(wan_ip_label)
        wan_ip_layout.addWidget(self.wan_ip)
        wan_layout.addLayout(wan_ip_layout)
        
        wan_mask_layout = QHBoxLayout()
        wan_mask_label = QLabel('WAN 口子网掩码:')
        wan_mask_label.setFixedWidth(100)
        self.wan_mask = QLineEdit()
        wan_mask_layout.addWidget(wan_mask_label)
        wan_mask_layout.addWidget(self.wan_mask)
        wan_layout.addLayout(wan_mask_layout)
        
        isp_gateway_layout = QHBoxLayout()
        isp_gateway_label = QLabel('运营商网关 IP 地址:')
        isp_gateway_label.setFixedWidth(100)
        self.isp_gateway = QLineEdit()
        isp_gateway_layout.addWidget(isp_gateway_label)
        isp_gateway_layout.addWidget(self.isp_gateway)
        wan_layout.addLayout(isp_gateway_layout)
        
        wan_config.setLayout(wan_layout)
        interface_layout.addWidget(wan_config)
        
        # 内网用户 LAN 口配置
        lan_user_config = QGroupBox('内网用户 LAN 口配置')
        lan_user_layout = QVBoxLayout()
        
        lan_user_port_layout = QHBoxLayout()
        lan_user_port_label = QLabel('内网用户 LAN 物理端口:')
        lan_user_port_label.setFixedWidth(100)
        self.lan_user_port = QLineEdit()
        lan_user_port_layout.addWidget(lan_user_port_label)
        lan_user_port_layout.addWidget(self.lan_user_port)
        lan_user_layout.addLayout(lan_user_port_layout)
        
        user_gw_layout = QHBoxLayout()
        user_gw_label = QLabel('用户网段网关 IP:')
        user_gw_label.setFixedWidth(100)
        self.user_gw = QLineEdit()
        user_gw_layout.addWidget(user_gw_label)
        user_gw_layout.addWidget(self.user_gw)
        lan_user_layout.addLayout(user_gw_layout)
        
        user_mask_layout = QHBoxLayout()
        user_mask_label = QLabel('用户网段子网掩码:')
        user_mask_label.setFixedWidth(100)
        self.user_mask = QLineEdit()
        user_mask_layout.addWidget(user_mask_label)
        user_mask_layout.addWidget(self.user_mask)
        lan_user_layout.addLayout(user_mask_layout)
        
        lan_user_config.setLayout(lan_user_layout)
        interface_layout.addWidget(lan_user_config)
        
        # 内网服务器 LAN 口配置
        lan_server_config = QGroupBox('内网服务器 LAN 口配置')
        lan_server_layout = QVBoxLayout()
        
        lan_server_port_layout = QHBoxLayout()
        lan_server_port_label = QLabel('服务器 LAN 物理端口:')
        lan_server_port_label.setFixedWidth(100)
        self.lan_server_port = QLineEdit()
        lan_server_port_layout.addWidget(lan_server_port_label)
        lan_server_port_layout.addWidget(self.lan_server_port)
        lan_server_layout.addLayout(lan_server_port_layout)
        
        server_gw_layout = QHBoxLayout()
        server_gw_label = QLabel('服务器网段网关 IP:')
        server_gw_label.setFixedWidth(100)
        self.server_gw = QLineEdit()
        server_gw_layout.addWidget(server_gw_label)
        server_gw_layout.addWidget(self.server_gw)
        lan_server_layout.addLayout(server_gw_layout)
        
        server_mask_layout = QHBoxLayout()
        server_mask_label = QLabel('服务器网段子网掩码:')
        server_mask_label.setFixedWidth(100)
        self.server_mask = QLineEdit()
        server_mask_layout.addWidget(server_mask_label)
        server_mask_layout.addWidget(self.server_mask)
        lan_server_layout.addLayout(server_mask_layout)
        
        lan_server_config.setLayout(lan_server_layout)
        interface_layout.addWidget(lan_server_config)
        
        interface_config.setLayout(interface_layout)
        layout.addWidget(interface_config)
        
        # 面板3：NAT 地址转换配置
        nat_config = QGroupBox('NAT 地址转换配置（核心上网功能）')
        nat_layout = QVBoxLayout()
        
        # NAT 访问控制列表配置
        nat_acl_config = QGroupBox('NAT 访问控制列表配置')
        nat_acl_layout = QVBoxLayout()
        
        nat_acl_name_layout = QHBoxLayout()
        nat_acl_name_label = QLabel('NAT ACL 名称:')
        nat_acl_name_label.setFixedWidth(100)
        self.nat_acl_name = QLineEdit()
        nat_acl_name_layout.addWidget(nat_acl_name_label)
        nat_acl_name_layout.addWidget(self.nat_acl_name)
        nat_acl_layout.addLayout(nat_acl_name_layout)
        
        user_network_layout = QHBoxLayout()
        user_network_label = QLabel('用户网段地址:')
        user_network_label.setFixedWidth(100)
        self.user_network = QLineEdit()
        user_network_layout.addWidget(user_network_label)
        user_network_layout.addWidget(self.user_network)
        nat_acl_layout.addLayout(user_network_layout)
        
        user_wildcard_layout = QHBoxLayout()
        user_wildcard_label = QLabel('用户网段反掩码:')
        user_wildcard_label.setFixedWidth(100)
        self.user_wildcard = QLineEdit()
        user_wildcard_layout.addWidget(user_wildcard_label)
        user_wildcard_layout.addWidget(self.user_wildcard)
        nat_acl_layout.addLayout(user_wildcard_layout)
        
        server_network_layout = QHBoxLayout()
        server_network_label = QLabel('服务器网段地址:')
        server_network_label.setFixedWidth(100)
        self.server_network = QLineEdit()
        server_network_layout.addWidget(server_network_label)
        server_network_layout.addWidget(self.server_network)
        nat_acl_layout.addLayout(server_network_layout)
        
        server_wildcard_layout = QHBoxLayout()
        server_wildcard_label = QLabel('服务器网段反掩码:')
        server_wildcard_label.setFixedWidth(100)
        self.server_wildcard = QLineEdit()
        server_wildcard_layout.addWidget(server_wildcard_label)
        server_wildcard_layout.addWidget(self.server_wildcard)
        nat_acl_layout.addLayout(server_wildcard_layout)
        
        nat_acl_config.setLayout(nat_acl_layout)
        nat_layout.addWidget(nat_acl_config)
        
        # 动态 PAT 端口复用配置
        pat_config = QGroupBox('动态 PAT 端口复用配置')
        pat_layout = QVBoxLayout()
        
        pat_acl_name_layout = QHBoxLayout()
        pat_acl_name_label = QLabel('NAT ACL 名称:')
        pat_acl_name_label.setFixedWidth(100)
        self.pat_acl_name = QLineEdit()
        pat_acl_name_layout.addWidget(pat_acl_name_label)
        pat_acl_name_layout.addWidget(self.pat_acl_name)
        pat_layout.addLayout(pat_acl_name_layout)
        
        pat_wan_port_layout = QHBoxLayout()
        pat_wan_port_label = QLabel('上联 WAN 出口物理端口:')
        pat_wan_port_label.setFixedWidth(100)
        self.pat_wan_port = QLineEdit()
        pat_wan_port_layout.addWidget(pat_wan_port_label)
        pat_wan_port_layout.addWidget(self.pat_wan_port)
        pat_layout.addLayout(pat_wan_port_layout)
        
        pat_lan_user_port_layout = QHBoxLayout()
        pat_lan_user_port_label = QLabel('内网用户 LAN 物理端口:')
        pat_lan_user_port_label.setFixedWidth(100)
        self.pat_lan_user_port = QLineEdit()
        pat_lan_user_port_layout.addWidget(pat_lan_user_port_label)
        pat_lan_user_port_layout.addWidget(self.pat_lan_user_port)
        pat_layout.addLayout(pat_lan_user_port_layout)
        
        pat_lan_server_port_layout = QHBoxLayout()
        pat_lan_server_port_label = QLabel('内网服务器 LAN 物理端口:')
        pat_lan_server_port_label.setFixedWidth(100)
        self.pat_lan_server_port = QLineEdit()
        pat_lan_server_port_layout.addWidget(pat_lan_server_port_label)
        pat_lan_server_port_layout.addWidget(self.pat_lan_server_port)
        pat_layout.addLayout(pat_lan_server_port_layout)
        
        pat_config.setLayout(pat_layout)
        nat_layout.addWidget(pat_config)
        
        # 服务器端口映射配置
        port_map_config = QGroupBox('服务器端口映射配置')
        port_map_layout = QVBoxLayout()
        
        protocol_layout = QHBoxLayout()
        protocol_label = QLabel('传输协议类型:')
        protocol_label.setFixedWidth(100)
        self.protocol = QComboBox()
        self.protocol.addItems(['TCP', 'UDP'])
        protocol_layout.addWidget(protocol_label)
        protocol_layout.addWidget(self.protocol)
        port_map_layout.addLayout(protocol_layout)
        
        server_intranet_ip_layout = QHBoxLayout()
        server_intranet_ip_label = QLabel('内网服务器真实 IP:')
        server_intranet_ip_label.setFixedWidth(100)
        self.server_intranet_ip = QLineEdit()
        server_intranet_ip_layout.addWidget(server_intranet_ip_label)
        server_intranet_ip_layout.addWidget(self.server_intranet_ip)
        port_map_layout.addLayout(server_intranet_ip_layout)
        
        server_port_layout = QHBoxLayout()
        server_port_label = QLabel('内网服务器业务端口:')
        server_port_label.setFixedWidth(100)
        self.server_port = QLineEdit()
        server_port_layout.addWidget(server_port_label)
        server_port_layout.addWidget(self.server_port)
        port_map_layout.addLayout(server_port_layout)
        
        map_wan_port_layout = QHBoxLayout()
        map_wan_port_label = QLabel('上联 WAN 物理端口:')
        map_wan_port_label.setFixedWidth(100)
        self.map_wan_port = QLineEdit()
        map_wan_port_layout.addWidget(map_wan_port_label)
        map_wan_port_layout.addWidget(self.map_wan_port)
        port_map_layout.addLayout(map_wan_port_layout)
        
        map_external_port_layout = QHBoxLayout()
        map_external_port_label = QLabel('外网映射访问端口:')
        map_external_port_label.setFixedWidth(100)
        self.map_external_port = QLineEdit()
        map_external_port_layout.addWidget(map_external_port_label)
        map_external_port_layout.addWidget(self.map_external_port)
        port_map_layout.addLayout(map_external_port_layout)
        
        port_map_config.setLayout(port_map_layout)
        nat_layout.addWidget(port_map_config)
        
        nat_config.setLayout(nat_layout)
        layout.addWidget(nat_config)
        
        # 面板4：路由配置
        route_config = QGroupBox('路由配置')
        route_layout = QVBoxLayout()
        
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
        nh1_label = QLabel('下一跳 IP 地址 1:')
        nh1_label.setFixedWidth(100)
        self.nh1 = QLineEdit()
        nh1_layout.addWidget(nh1_label)
        nh1_layout.addWidget(self.nh1)
        static_route_layout.addLayout(nh1_layout)
        
        dst_net2_layout = QHBoxLayout()
        dst_net2_label = QLabel('目的网段 2:')
        dst_net2_label.setFixedWidth(100)
        self.dst_net2 = QLineEdit()
        dst_net2_layout.addWidget(dst_net2_label)
        dst_net2_layout.addWidget(self.dst_net2)
        static_route_layout.addLayout(dst_net2_layout)
        
        dst_mask2_layout = QHBoxLayout()
        dst_mask2_label = QLabel('目的网段子网掩码 2:')
        dst_mask2_label.setFixedWidth(100)
        self.dst_mask2 = QLineEdit()
        dst_mask2_layout.addWidget(dst_mask2_label)
        dst_mask2_layout.addWidget(self.dst_mask2)
        static_route_layout.addLayout(dst_mask2_layout)
        
        nh2_layout = QHBoxLayout()
        nh2_label = QLabel('下一跳 IP 地址 2:')
        nh2_label.setFixedWidth(100)
        self.nh2 = QLineEdit()
        nh2_layout.addWidget(nh2_label)
        nh2_layout.addWidget(self.nh2)
        static_route_layout.addLayout(nh2_layout)
        
        default_nh_layout = QHBoxLayout()
        default_nh_label = QLabel('默认路由下一跳 IP:')
        default_nh_label.setFixedWidth(100)
        self.default_nh = QLineEdit()
        default_nh_layout.addWidget(default_nh_label)
        default_nh_layout.addWidget(self.default_nh)
        static_route_layout.addLayout(default_nh_layout)
        
        static_route_config.setLayout(static_route_layout)
        route_layout.addWidget(static_route_config)
        
        # OSPF 动态路由配置
        ospf_config = QGroupBox('OSPF 动态路由配置')
        ospf_layout = QVBoxLayout()
        
        ospf_proc_layout = QHBoxLayout()
        ospf_proc_label = QLabel('OSPF 进程号:')
        ospf_proc_label.setFixedWidth(100)
        self.ospf_proc = QLineEdit()
        ospf_proc_layout.addWidget(ospf_proc_label)
        ospf_proc_layout.addWidget(self.ospf_proc)
        ospf_layout.addLayout(ospf_proc_layout)
        
        ospf_rid_layout = QHBoxLayout()
        ospf_rid_label = QLabel('OSPF 路由器 ID:')
        ospf_rid_label.setFixedWidth(100)
        self.ospf_rid = QLineEdit()
        ospf_rid_layout.addWidget(ospf_rid_label)
        ospf_rid_layout.addWidget(self.ospf_rid)
        ospf_layout.addLayout(ospf_rid_layout)
        
        area_id_layout = QHBoxLayout()
        area_id_label = QLabel('OSPF 区域号:')
        area_id_label.setFixedWidth(100)
        self.area_id = QLineEdit()
        area_id_layout.addWidget(area_id_label)
        area_id_layout.addWidget(self.area_id)
        ospf_layout.addLayout(area_id_layout)
        
        ospf_user_network_layout = QHBoxLayout()
        ospf_user_network_label = QLabel('需宣告用户网段:')
        ospf_user_network_label.setFixedWidth(100)
        self.ospf_user_network = QLineEdit()
        ospf_user_network_layout.addWidget(ospf_user_network_label)
        ospf_user_network_layout.addWidget(self.ospf_user_network)
        ospf_layout.addLayout(ospf_user_network_layout)
        
        user_wildcard_layout = QHBoxLayout()
        user_wildcard_label = QLabel('用户网段反掩码:')
        user_wildcard_label.setFixedWidth(100)
        self.ospf_user_wildcard = QLineEdit()
        user_wildcard_layout.addWidget(user_wildcard_label)
        user_wildcard_layout.addWidget(self.ospf_user_wildcard)
        ospf_layout.addLayout(user_wildcard_layout)
        
        ospf_server_network_layout = QHBoxLayout()
        ospf_server_network_label = QLabel('需宣告服务器网段:')
        ospf_server_network_label.setFixedWidth(100)
        self.ospf_server_network = QLineEdit()
        ospf_server_network_layout.addWidget(ospf_server_network_label)
        ospf_server_network_layout.addWidget(self.ospf_server_network)
        ospf_layout.addLayout(ospf_server_network_layout)
        
        server_wildcard_layout = QHBoxLayout()
        server_wildcard_label = QLabel('服务器网段反掩码:')
        server_wildcard_label.setFixedWidth(100)
        self.ospf_server_wildcard = QLineEdit()
        server_wildcard_layout.addWidget(server_wildcard_label)
        server_wildcard_layout.addWidget(self.ospf_server_wildcard)
        ospf_layout.addLayout(server_wildcard_layout)
        
        wan_passive_interface_layout = QHBoxLayout()
        wan_passive_interface_label = QLabel('WAN 被动接口名称:')
        wan_passive_interface_label.setFixedWidth(100)
        self.wan_passive_interface = QLineEdit()
        wan_passive_interface_layout.addWidget(wan_passive_interface_label)
        wan_passive_interface_layout.addWidget(self.wan_passive_interface)
        ospf_layout.addLayout(wan_passive_interface_layout)
        
        ospf_config.setLayout(ospf_layout)
        route_layout.addWidget(ospf_config)
        
        route_config.setLayout(route_layout)
        layout.addWidget(route_config)
        
        # 面板5：DHCP 服务配置
        dhcp_config = QGroupBox('DHCP 服务配置')
        dhcp_layout = QVBoxLayout()
        
        # 用户网段 DHCP 地址池
        user_pool_config = QGroupBox('用户网段 DHCP 地址池')
        user_pool_layout = QVBoxLayout()
        
        user_pool_name_layout = QHBoxLayout()
        user_pool_name_label = QLabel('用户 DHCP 地址池名称:')
        user_pool_name_label.setFixedWidth(100)
        self.user_pool_name = QLineEdit()
        user_pool_name_layout.addWidget(user_pool_name_label)
        user_pool_name_layout.addWidget(self.user_pool_name)
        user_pool_layout.addLayout(user_pool_name_layout)
        
        user_network_layout = QHBoxLayout()
        user_network_label = QLabel('用户网段地址:')
        user_network_label.setFixedWidth(100)
        self.dhcp_user_network = QLineEdit()
        user_network_layout.addWidget(user_network_label)
        user_network_layout.addWidget(self.dhcp_user_network)
        user_pool_layout.addLayout(user_network_layout)
        
        user_mask_layout = QHBoxLayout()
        user_mask_label = QLabel('用户网段子网掩码:')
        user_mask_label.setFixedWidth(100)
        self.dhcp_user_mask = QLineEdit()
        user_mask_layout.addWidget(user_mask_label)
        user_mask_layout.addWidget(self.dhcp_user_mask)
        user_pool_layout.addLayout(user_mask_layout)
        
        user_ex_start_layout = QHBoxLayout()
        user_ex_start_label = QLabel('用户网段排除起始 IP:')
        user_ex_start_label.setFixedWidth(100)
        self.user_ex_start = QLineEdit()
        user_ex_start_layout.addWidget(user_ex_start_label)
        user_ex_start_layout.addWidget(self.user_ex_start)
        user_pool_layout.addLayout(user_ex_start_layout)
        
        user_ex_end_layout = QHBoxLayout()
        user_ex_end_label = QLabel('用户网段排除结束 IP:')
        user_ex_end_label.setFixedWidth(100)
        self.user_ex_end = QLineEdit()
        user_ex_end_layout.addWidget(user_ex_end_label)
        user_ex_end_layout.addWidget(self.user_ex_end)
        user_pool_layout.addLayout(user_ex_end_layout)
        
        user_gw_layout = QHBoxLayout()
        user_gw_label = QLabel('用户网段默认网关 IP:')
        user_gw_label.setFixedWidth(100)
        self.dhcp_user_gw = QLineEdit()
        user_gw_layout.addWidget(user_gw_label)
        user_gw_layout.addWidget(self.dhcp_user_gw)
        user_pool_layout.addLayout(user_gw_layout)
        
        dns_primary_layout = QHBoxLayout()
        dns_primary_label = QLabel('主 DNS 服务器 IP:')
        dns_primary_label.setFixedWidth(100)
        self.dns_primary = QLineEdit()
        dns_primary_layout.addWidget(dns_primary_label)
        dns_primary_layout.addWidget(self.dns_primary)
        user_pool_layout.addLayout(dns_primary_layout)
        
        dns_standby_layout = QHBoxLayout()
        dns_standby_label = QLabel('备 DNS 服务器 IP:')
        dns_standby_label.setFixedWidth(100)
        self.dns_standby = QLineEdit()
        dns_standby_layout.addWidget(dns_standby_label)
        dns_standby_layout.addWidget(self.dns_standby)
        user_pool_layout.addLayout(dns_standby_layout)
        
        lease_day_layout = QHBoxLayout()
        lease_day_label = QLabel('地址租期天数:')
        lease_day_label.setFixedWidth(100)
        self.lease_day = QLineEdit()
        lease_day_layout.addWidget(lease_day_label)
        lease_day_layout.addWidget(self.lease_day)
        user_pool_layout.addLayout(lease_day_layout)
        
        user_pool_config.setLayout(user_pool_layout)
        dhcp_layout.addWidget(user_pool_config)
        
        # 服务器网段 DHCP 地址池
        server_pool_config = QGroupBox('服务器网段 DHCP 地址池')
        server_pool_layout = QVBoxLayout()
        
        server_pool_name_layout = QHBoxLayout()
        server_pool_name_label = QLabel('服务器 DHCP 地址池名称:')
        server_pool_name_label.setFixedWidth(100)
        self.server_pool_name = QLineEdit()
        server_pool_name_layout.addWidget(server_pool_name_label)
        server_pool_name_layout.addWidget(self.server_pool_name)
        server_pool_layout.addLayout(server_pool_name_layout)
        
        server_network_layout = QHBoxLayout()
        server_network_label = QLabel('服务器网段地址:')
        server_network_label.setFixedWidth(100)
        self.dhcp_server_network = QLineEdit()
        server_network_layout.addWidget(server_network_label)
        server_network_layout.addWidget(self.dhcp_server_network)
        server_pool_layout.addLayout(server_network_layout)
        
        server_mask_layout = QHBoxLayout()
        server_mask_label = QLabel('服务器网段子网掩码:')
        server_mask_label.setFixedWidth(100)
        self.dhcp_server_mask = QLineEdit()
        server_mask_layout.addWidget(server_mask_label)
        server_mask_layout.addWidget(self.dhcp_server_mask)
        server_pool_layout.addLayout(server_mask_layout)
        
        server_ex_start_layout = QHBoxLayout()
        server_ex_start_label = QLabel('服务器网段排除起始 IP:')
        server_ex_start_label.setFixedWidth(100)
        self.server_ex_start = QLineEdit()
        server_ex_start_layout.addWidget(server_ex_start_label)
        server_ex_start_layout.addWidget(self.server_ex_start)
        server_pool_layout.addLayout(server_ex_start_layout)
        
        server_ex_end_layout = QHBoxLayout()
        server_ex_end_label = QLabel('服务器网段排除结束 IP:')
        server_ex_end_label.setFixedWidth(100)
        self.server_ex_end = QLineEdit()
        server_ex_end_layout.addWidget(server_ex_end_label)
        server_ex_end_layout.addWidget(self.server_ex_end)
        server_pool_layout.addLayout(server_ex_end_layout)
        
        server_gw_layout = QHBoxLayout()
        server_gw_label = QLabel('服务器网段默认网关 IP:')
        server_gw_label.setFixedWidth(100)
        self.dhcp_server_gw = QLineEdit()
        server_gw_layout.addWidget(server_gw_label)
        server_gw_layout.addWidget(self.dhcp_server_gw)
        server_pool_layout.addLayout(server_gw_layout)
        
        server_pool_config.setLayout(server_pool_layout)
        dhcp_layout.addWidget(server_pool_config)
        
        dhcp_config.setLayout(dhcp_layout)
        layout.addWidget(dhcp_config)
        
        # 面板6：安全 ACL 访问控制配置
        security_config = QGroupBox('安全 ACL 访问控制配置')
        security_layout = QVBoxLayout()
        
        # 远程管理权限 ACL
        manage_acl_config = QGroupBox('远程管理权限 ACL')
        manage_acl_layout = QVBoxLayout()
        
        manage_acl_name_layout = QHBoxLayout()
        manage_acl_name_label = QLabel('管理 ACL 名称:')
        manage_acl_name_label.setFixedWidth(100)
        self.manage_acl_name = QLineEdit()
        manage_acl_name_layout.addWidget(manage_acl_name_label)
        manage_acl_name_layout.addWidget(self.manage_acl_name)
        manage_acl_layout.addLayout(manage_acl_name_layout)
        
        manage_network_layout = QHBoxLayout()
        manage_network_label = QLabel('允许管理网段 IP:')
        manage_network_label.setFixedWidth(100)
        self.manage_network = QLineEdit()
        manage_network_layout.addWidget(manage_network_label)
        manage_network_layout.addWidget(self.manage_network)
        manage_acl_layout.addLayout(manage_network_layout)
        
        manage_wildcard_layout = QHBoxLayout()
        manage_wildcard_label = QLabel('允许管理网段反掩码:')
        manage_wildcard_label.setFixedWidth(100)
        self.manage_wildcard = QLineEdit()
        manage_wildcard_layout.addWidget(manage_wildcard_label)
        manage_wildcard_layout.addWidget(self.manage_wildcard)
        manage_acl_layout.addLayout(manage_wildcard_layout)
        
        manage_acl_config.setLayout(manage_acl_layout)
        security_layout.addWidget(manage_acl_config)
        
        # 跨网段访问控制 ACL
        cross_acl_config = QGroupBox('跨网段访问控制 ACL')
        cross_acl_layout = QVBoxLayout()
        
        cross_segment_acl_name_layout = QHBoxLayout()
        cross_segment_acl_name_label = QLabel('跨网段 ACL 名称:')
        cross_segment_acl_name_label.setFixedWidth(100)
        self.cross_segment_acl_name = QLineEdit()
        cross_segment_acl_name_layout.addWidget(cross_segment_acl_name_label)
        cross_segment_acl_name_layout.addWidget(self.cross_segment_acl_name)
        cross_acl_layout.addLayout(cross_segment_acl_name_layout)
        
        source_network_layout = QHBoxLayout()
        source_network_label = QLabel('允许访问源网段 IP:')
        source_network_label.setFixedWidth(100)
        self.source_network = QLineEdit()
        source_network_layout.addWidget(source_network_label)
        source_network_layout.addWidget(self.source_network)
        cross_acl_layout.addLayout(source_network_layout)
        
        source_wildcard_layout = QHBoxLayout()
        source_wildcard_label = QLabel('源网段反掩码:')
        source_wildcard_label.setFixedWidth(100)
        self.source_wildcard = QLineEdit()
        source_wildcard_layout.addWidget(source_wildcard_label)
        source_wildcard_layout.addWidget(self.source_wildcard)
        cross_acl_layout.addLayout(source_wildcard_layout)
        
        dst_network_layout = QHBoxLayout()
        dst_network_label = QLabel('允许访问目的网段 IP:')
        dst_network_label.setFixedWidth(100)
        self.dst_network = QLineEdit()
        dst_network_layout.addWidget(dst_network_label)
        dst_network_layout.addWidget(self.dst_network)
        cross_acl_layout.addLayout(dst_network_layout)
        
        dst_wildcard_layout = QHBoxLayout()
        dst_wildcard_label = QLabel('目的网段反掩码:')
        dst_wildcard_label.setFixedWidth(100)
        self.dst_wildcard = QLineEdit()
        dst_wildcard_layout.addWidget(dst_wildcard_label)
        dst_wildcard_layout.addWidget(self.dst_wildcard)
        cross_acl_layout.addLayout(dst_wildcard_layout)
        
        lan_user_port_layout = QHBoxLayout()
        lan_user_port_label = QLabel('内网用户 LAN 物理端口:')
        lan_user_port_label.setFixedWidth(100)
        self.cross_lan_user_port = QLineEdit()
        lan_user_port_layout.addWidget(lan_user_port_label)
        lan_user_port_layout.addWidget(self.cross_lan_user_port)
        cross_acl_layout.addLayout(lan_user_port_layout)
        
        cross_acl_config.setLayout(cross_acl_layout)
        security_layout.addWidget(cross_acl_config)
        
        security_config.setLayout(security_layout)
        layout.addWidget(security_config)
        
        # 面板7：运维监控配置
        maintenance_config = QGroupBox('运维监控配置')
        maintenance_layout = QVBoxLayout()
        
        # SNMPv2c 监控配置
        snmp_config = QGroupBox('SNMPv2c 监控配置')
        snmp_layout = QVBoxLayout()
        
        snmp_ro_community_layout = QHBoxLayout()
        snmp_ro_community_label = QLabel('SNMP 只读团体名:')
        snmp_ro_community_label.setFixedWidth(100)
        self.snmp_ro_community = QLineEdit()
        snmp_ro_community_layout.addWidget(snmp_ro_community_label)
        snmp_ro_community_layout.addWidget(self.snmp_ro_community)
        snmp_layout.addLayout(snmp_ro_community_layout)
        
        trap_server_ip_layout = QHBoxLayout()
        trap_server_ip_label = QLabel('SNMP Trap 服务器 IP:')
        trap_server_ip_label.setFixedWidth(100)
        self.trap_server_ip = QLineEdit()
        trap_server_ip_layout.addWidget(trap_server_ip_label)
        trap_server_ip_layout.addWidget(self.trap_server_ip)
        snmp_layout.addLayout(trap_server_ip_layout)
        
        trap_community_layout = QHBoxLayout()
        trap_community_label = QLabel('SNMP Trap 团体名:')
        trap_community_label.setFixedWidth(100)
        self.trap_community = QLineEdit()
        trap_community_layout.addWidget(trap_community_label)
        trap_community_layout.addWidget(self.trap_community)
        snmp_layout.addLayout(trap_community_layout)
        
        device_location_layout = QHBoxLayout()
        device_location_label = QLabel('设备部署位置:')
        device_location_label.setFixedWidth(100)
        self.device_location = QLineEdit()
        device_location_layout.addWidget(device_location_label)
        device_location_layout.addWidget(self.device_location)
        snmp_layout.addLayout(device_location_layout)
        
        admin_contact_layout = QHBoxLayout()
        admin_contact_label = QLabel('网络管理员联系方式:')
        admin_contact_label.setFixedWidth(100)
        self.admin_contact = QLineEdit()
        admin_contact_layout.addWidget(admin_contact_label)
        admin_contact_layout.addWidget(self.admin_contact)
        snmp_layout.addLayout(admin_contact_layout)
        
        snmp_config.setLayout(snmp_layout)
        maintenance_layout.addWidget(snmp_config)
        
        # 日志服务配置
        log_config = QGroupBox('日志服务配置')
        log_layout = QVBoxLayout()
        
        log_server_ip_layout = QHBoxLayout()
        log_server_ip_label = QLabel('日志服务器 IP 地址:')
        log_server_ip_label.setFixedWidth(100)
        self.log_server_ip = QLineEdit()
        log_server_ip_layout.addWidget(log_server_ip_label)
        log_server_ip_layout.addWidget(self.log_server_ip)
        log_layout.addLayout(log_server_ip_layout)
        
        log_buffer_size_layout = QHBoxLayout()
        log_buffer_size_label = QLabel('日志缓存大小:')
        log_buffer_size_label.setFixedWidth(100)
        self.log_buffer_size = QLineEdit()
        log_buffer_size_layout.addWidget(log_buffer_size_label)
        log_buffer_size_layout.addWidget(self.log_buffer_size)
        log_layout.addLayout(log_buffer_size_layout)
        
        log_config.setLayout(log_layout)
        maintenance_layout.addWidget(log_config)
        
        # 端口镜像配置
        mirror_config = QGroupBox('端口镜像配置')
        mirror_layout = QVBoxLayout()
        
        mirror_session_id_layout = QHBoxLayout()
        mirror_session_id_label = QLabel('镜像会话 ID:')
        mirror_session_id_label.setFixedWidth(100)
        self.mirror_session_id = QLineEdit()
        mirror_session_id_layout.addWidget(mirror_session_id_label)
        mirror_session_id_layout.addWidget(self.mirror_session_id)
        mirror_layout.addLayout(mirror_session_id_layout)
        
        mirror_src_port_layout = QHBoxLayout()
        mirror_src_port_label = QLabel('镜像源物理端口:')
        mirror_src_port_label.setFixedWidth(100)
        self.mirror_src_port = QLineEdit()
        mirror_src_port_layout.addWidget(mirror_src_port_label)
        mirror_src_port_layout.addWidget(self.mirror_src_port)
        mirror_layout.addLayout(mirror_src_port_layout)
        
        mirror_direction_layout = QHBoxLayout()
        mirror_direction_label = QLabel('镜像流量方向:')
        mirror_direction_label.setFixedWidth(100)
        self.mirror_direction = QComboBox()
        self.mirror_direction.addItems(['进', '出', '双向'])
        mirror_direction_layout.addWidget(mirror_direction_label)
        mirror_direction_layout.addWidget(self.mirror_direction)
        mirror_layout.addLayout(mirror_direction_layout)
        
        mirror_dst_port_layout = QHBoxLayout()
        mirror_dst_port_label = QLabel('镜像目的物理端口:')
        mirror_dst_port_label.setFixedWidth(100)
        self.mirror_dst_port = QLineEdit()
        mirror_dst_port_layout.addWidget(mirror_dst_port_label)
        mirror_dst_port_layout.addWidget(self.mirror_dst_port)
        mirror_layout.addLayout(mirror_dst_port_layout)
        
        mirror_config.setLayout(mirror_layout)
        maintenance_layout.addWidget(mirror_config)
        
        maintenance_config.setLayout(maintenance_layout)
        layout.addWidget(maintenance_config)
        
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

# 本地登录配置
line console 0
 password {self.console_password.text()}
 login
 exec-timeout 10 0
 logging synchronous
exit
clock set {self.system_time.text()}
ntp server {self.ntp_server.text()}
ntp update-calendar

# 远程登录配置
ip ssh version 2
username {self.ssh_user.text()} privilege 15 password {self.ssh_pwd.text()}
crypto key generate rsa modulus 2048
line vty 0 15
 login local
 transport input ssh
 exec-timeout 15 0
exit

# 三层接口配置
interface {self.wan_port.text()}
 ip address {self.wan_ip.text()} {self.wan_mask.text()}
 no shutdown
exit

interface {self.lan_user_port.text()}
 ip address {self.user_gw.text()} {self.user_mask.text()}
 no shutdown
exit

interface {self.lan_server_port.text()}
 ip address {self.server_gw.text()} {self.server_mask.text()}
 no shutdown
exit

# NAT 地址转换配置
access-list {self.nat_acl_name.text()} permit ip {self.user_network.text()} {self.user_wildcard.text()} any
access-list {self.nat_acl_name.text()} permit ip {self.server_network.text()} {self.server_wildcard.text()} any

interface {self.pat_wan_port.text()}
 ip nat outside
 no shutdown
exit

interface {self.pat_lan_user_port.text()}
 ip nat inside
 no shutdown
exit

interface {self.pat_lan_server_port.text()}
 ip nat inside
 no shutdown
exit

ip nat inside source list {self.pat_acl_name.text()} interface {self.pat_wan_port.text()} overload

# 服务器端口映射
ip nat inside source static {self.protocol.currentText().lower()} {self.server_intranet_ip.text()} {self.server_port.text()} interface {self.map_wan_port.text()} {self.map_external_port.text()}

# 路由配置
ip route {self.dst_net1.text()} {self.dst_mask1.text()} {self.nh1.text()}
ip route {self.dst_net2.text()} {self.dst_mask2.text()} {self.nh2.text()}
ip route 0.0.0.0 0.0.0.0 {self.default_nh.text()}

# OSPF 动态路由配置
router ospf {self.ospf_proc.text()}
 router-id {self.ospf_rid.text()}
 network {self.ospf_user_network.text()} {self.ospf_user_wildcard.text()} area {self.area_id.text()}
 network {self.ospf_server_network.text()} {self.ospf_server_wildcard.text()} area {self.area_id.text()}
 passive-interface {self.wan_passive_interface.text()}
exit

# DHCP 服务配置
service dhcp
ip dhcp excluded-address {self.user_ex_start.text()} {self.user_ex_end.text()}
ip dhcp excluded-address {self.server_ex_start.text()} {self.server_ex_end.text()}

ip dhcp pool {self.user_pool_name.text()}
 network {self.dhcp_user_network.text()} {self.dhcp_user_mask.text()}
 default-router {self.dhcp_user_gw.text()}
 dns-server {self.dns_primary.text()} {self.dns_standby.text()}
 lease {self.lease_day.text()} 0 0
exit

ip dhcp pool {self.server_pool_name.text()}
 network {self.dhcp_server_network.text()} {self.dhcp_server_mask.text()}
 default-router {self.server_gw.text()}
 dns-server {self.dns_primary.text()} {self.dns_standby.text()}
 lease 30 0 0
exit

# 安全 ACL 访问控制配置
access-list {self.manage_acl_name.text()} permit ip {self.manage_network.text()} {self.manage_wildcard.text()} any
access-list {self.cross_segment_acl_name.text()} permit ip {self.source_network.text()} {self.source_wildcard.text()} {self.dst_network.text()} {self.dst_wildcard.text()}

line vty 0 15
 access-class {self.manage_acl_name.text()} in
exit

interface {self.cross_lan_user_port.text()}
 ip access-group {self.cross_segment_acl_name.text()} in
exit

# 运维监控配置
snmp-server community {self.snmp_ro_community.text()} ro
snmp-server host {self.trap_server_ip.text()} traps version 2c {self.trap_community.text()}
snmp-server enable traps

logging host {self.log_server_ip.text()}
logging buffered {self.log_buffer_size.text()}

monitor session {self.mirror_session_id.text()} source interface {self.mirror_src_port.text()} {self.mirror_direction.currentText()}
monitor session {self.mirror_session_id.text()} destination interface {self.mirror_dst_port.text()}

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
        self.ssh_user.clear()
        self.ssh_pwd.clear()
        self.telnet_pwd.clear()
        self.wan_port.clear()
        self.wan_ip.clear()
        self.wan_mask.clear()
        self.isp_gateway.clear()
        self.lan_user_port.clear()
        self.user_gw.clear()
        self.user_mask.clear()
        self.lan_server_port.clear()
        self.server_gw.clear()
        self.server_mask.clear()
        self.nat_acl_name.clear()
        self.user_network.clear()
        self.user_wildcard.clear()
        self.server_network.clear()
        self.server_wildcard.clear()
        self.pat_acl_name.clear()
        self.pat_wan_port.clear()
        self.pat_lan_user_port.clear()
        self.pat_lan_server_port.clear()
        self.protocol.setCurrentIndex(0)
        self.server_intranet_ip.clear()
        self.server_port.clear()
        self.map_wan_port.clear()
        self.map_external_port.clear()
        self.dst_net1.clear()
        self.dst_mask1.clear()
        self.nh1.clear()
        self.dst_net2.clear()
        self.dst_mask2.clear()
        self.nh2.clear()
        self.default_nh.clear()
        self.ospf_proc.clear()
        self.ospf_rid.clear()
        self.area_id.clear()
        self.ospf_user_network.clear()
        self.ospf_user_wildcard.clear()
        self.ospf_server_network.clear()
        self.ospf_server_wildcard.clear()
        self.wan_passive_interface.clear()
        self.user_pool_name.clear()
        self.dhcp_user_network.clear()
        self.dhcp_user_mask.clear()
        self.user_ex_start.clear()
        self.user_ex_end.clear()
        self.dhcp_user_gw.clear()
        self.dns_primary.clear()
        self.dns_standby.clear()
        self.lease_day.clear()
        self.server_pool_name.clear()
        self.dhcp_server_network.clear()
        self.dhcp_server_mask.clear()
        self.server_ex_start.clear()
        self.server_ex_end.clear()
        self.manage_acl_name.clear()
        self.manage_network.clear()
        self.manage_wildcard.clear()
        self.cross_segment_acl_name.clear()
        self.source_network.clear()
        self.source_wildcard.clear()
        self.dst_network.clear()
        self.dst_wildcard.clear()
        self.cross_lan_user_port.clear()
        self.snmp_ro_community.clear()
        self.trap_server_ip.clear()
        self.trap_community.clear()
        self.device_location.clear()
        self.admin_contact.clear()
        self.log_server_ip.clear()
        self.log_buffer_size.clear()
        self.mirror_session_id.clear()
        self.mirror_src_port.clear()
        self.mirror_direction.setCurrentIndex(0)
        self.mirror_dst_port.clear()
        # 重置代码编辑器
        self.code_editor.clear()
        
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
        self.ssh_user.clear()
        self.ssh_pwd.clear()
        self.telnet_pwd.clear()
        self.wan_port.clear()
        self.wan_ip.clear()
        self.wan_mask.clear()
        self.isp_gateway.clear()
        self.lan_user_port.clear()
        self.user_gw.clear()
        self.user_mask.clear()
        self.lan_server_port.clear()
        self.server_gw.clear()
        self.server_mask.clear()
        self.nat_acl_name.clear()
        self.user_network.clear()
        self.user_wildcard.clear()
        self.server_network.clear()
        self.server_wildcard.clear()
        self.pat_acl_name.clear()
        self.pat_wan_port.clear()
        self.pat_lan_user_port.clear()
        self.pat_lan_server_port.clear()
        self.server_intranet_ip.clear()
        self.server_port.clear()
        self.map_wan_port.clear()
        self.map_external_port.clear()
        self.dst_net1.clear()
        self.dst_mask1.clear()
        self.nh1.clear()
        self.dst_net2.clear()
        self.dst_mask2.clear()
        self.nh2.clear()
        self.default_nh.clear()
        self.ospf_proc.clear()
        self.ospf_rid.clear()
        self.area_id.clear()
        self.ospf_user_network.clear()
        self.ospf_user_wildcard.clear()
        self.ospf_server_network.clear()
        self.ospf_server_wildcard.clear()
        self.wan_passive_interface.clear()
        self.user_pool_name.clear()
        self.dhcp_user_network.clear()
        self.dhcp_user_mask.clear()
        self.user_ex_start.clear()
        self.user_ex_end.clear()
        self.dhcp_user_gw.clear()
        self.dns_primary.clear()
        self.dns_standby.clear()
        self.lease_day.clear()
        self.server_pool_name.clear()
        self.dhcp_server_network.clear()
        self.dhcp_server_mask.clear()
        self.server_ex_start.clear()
        self.server_ex_end.clear()
        self.dhcp_server_gw.clear()
        self.manage_acl_name.clear()
        self.manage_network.clear()
        self.manage_wildcard.clear()
        self.cross_segment_acl_name.clear()
        self.source_network.clear()
        self.source_wildcard.clear()
        self.dst_network.clear()
        self.dst_wildcard.clear()
        self.cross_lan_user_port.clear()
        self.snmp_ro_community.clear()
        self.trap_server_ip.clear()
        self.trap_community.clear()
        self.device_location.clear()
        self.admin_contact.clear()
        self.log_server_ip.clear()
        self.log_buffer_size.clear()
        self.mirror_session_id.clear()
        self.mirror_src_port.clear()
        self.mirror_dst_port.clear()
        # 重置代码编辑器
        self.code_editor.clear()