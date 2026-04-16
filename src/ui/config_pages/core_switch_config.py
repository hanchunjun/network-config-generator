from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QGroupBox
from ui.config_pages.base_config_page import BaseConfigPage

class CoreSwitchConfig(BaseConfigPage):
    def __init__(self, parent, vendor):
        super().__init__(parent, vendor, 'core_switch')
        self.title.setText('核心交换机配置')
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
        
        # 面板2：端口与上联配置
        port_config = QGroupBox('端口与上联配置')
        port_layout = QVBoxLayout()
        
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
        
        server_vlan_layout = QHBoxLayout()
        server_vlan_label = QLabel('服务器业务 VLAN ID:')
        server_vlan_label.setFixedWidth(100)
        self.server_vlan = QLineEdit()
        server_vlan_layout.addWidget(server_vlan_label)
        server_vlan_layout.addWidget(self.server_vlan)
        vlan_create_layout.addLayout(server_vlan_layout)
        
        vlan_create_config.setLayout(vlan_create_layout)
        port_layout.addWidget(vlan_create_config)
        
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
        
        # 链路聚合配置
        agg_config = QGroupBox('链路聚合配置')
        agg_layout = QVBoxLayout()
        
        static_agg_id_layout = QHBoxLayout()
        static_agg_id_label = QLabel('静态聚合组号:')
        static_agg_id_label.setFixedWidth(100)
        self.static_agg_id = QLineEdit()
        static_agg_id_layout.addWidget(static_agg_id_label)
        static_agg_id_layout.addWidget(self.static_agg_id)
        agg_layout.addLayout(static_agg_id_layout)
        
        static_agg_ports_layout = QHBoxLayout()
        static_agg_ports_label = QLabel('静态聚合成员端口范围:')
        static_agg_ports_label.setFixedWidth(100)
        self.static_agg_ports = QLineEdit()
        static_agg_ports_layout.addWidget(static_agg_ports_label)
        static_agg_ports_layout.addWidget(self.static_agg_ports)
        agg_layout.addLayout(static_agg_ports_layout)
        
        lacp_agg_id_layout = QHBoxLayout()
        lacp_agg_id_label = QLabel('动态聚合组号:')
        lacp_agg_id_label.setFixedWidth(100)
        self.lacp_agg_id = QLineEdit()
        lacp_agg_id_layout.addWidget(lacp_agg_id_label)
        lacp_agg_id_layout.addWidget(self.lacp_agg_id)
        agg_layout.addLayout(lacp_agg_id_layout)
        
        lacp_agg_ports_layout = QHBoxLayout()
        lacp_agg_ports_label = QLabel('LACP 聚合成员端口范围:')
        lacp_agg_ports_label.setFixedWidth(100)
        self.lacp_agg_ports = QLineEdit()
        lacp_agg_ports_layout.addWidget(lacp_agg_ports_label)
        lacp_agg_ports_layout.addWidget(self.lacp_agg_ports)
        agg_layout.addLayout(lacp_agg_ports_layout)
        
        agg_config.setLayout(agg_layout)
        port_layout.addWidget(agg_config)
        
        # 下联 Access 端口配置
        down_port_config = QGroupBox('下联 Access 端口配置')
        down_port_layout = QVBoxLayout()
        
        down_port_range_layout = QHBoxLayout()
        down_port_range_label = QLabel('下联端口范围:')
        down_port_range_label.setFixedWidth(100)
        self.down_port_range = QLineEdit()
        down_port_range_layout.addWidget(down_port_range_label)
        down_port_range_layout.addWidget(self.down_port_range)
        down_port_layout.addLayout(down_port_range_layout)
        
        down_port_config.setLayout(down_port_layout)
        port_layout.addWidget(down_port_config)
        
        port_config.setLayout(port_layout)
        layout.addWidget(port_config)
        
        # 面板3：三层网关与路由配置
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
        
        server_gw_layout = QHBoxLayout()
        server_gw_label = QLabel('服务器网关 IP 地址:')
        server_gw_label.setFixedWidth(100)
        self.server_gw = QLineEdit()
        server_gw_layout.addWidget(server_gw_label)
        server_gw_layout.addWidget(self.server_gw)
        vlanif_layout.addLayout(server_gw_layout)
        
        server_mask_layout = QHBoxLayout()
        server_mask_label = QLabel('服务器网段子网掩码:')
        server_mask_label.setFixedWidth(100)
        self.server_mask = QLineEdit()
        server_mask_layout.addWidget(server_mask_label)
        server_mask_layout.addWidget(self.server_mask)
        vlanif_layout.addLayout(server_mask_layout)
        
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
        nh2_label = QLabel('下一跳 2:')
        nh2_label.setFixedWidth(100)
        self.nh2 = QLineEdit()
        nh2_layout.addWidget(nh2_label)
        nh2_layout.addWidget(self.nh2)
        static_route_layout.addLayout(nh2_layout)
        
        dst_net3_layout = QHBoxLayout()
        dst_net3_label = QLabel('目的网段 3:')
        dst_net3_label.setFixedWidth(100)
        self.dst_net3 = QLineEdit()
        dst_net3_layout.addWidget(dst_net3_label)
        dst_net3_layout.addWidget(self.dst_net3)
        static_route_layout.addLayout(dst_net3_layout)
        
        dst_mask3_layout = QHBoxLayout()
        dst_mask3_label = QLabel('目的网段子网掩码 3:')
        dst_mask3_label.setFixedWidth(100)
        self.dst_mask3 = QLineEdit()
        dst_mask3_layout.addWidget(dst_mask3_label)
        dst_mask3_layout.addWidget(self.dst_mask3)
        static_route_layout.addLayout(dst_mask3_layout)
        
        nh3_layout = QHBoxLayout()
        nh3_label = QLabel('下一跳 3:')
        nh3_label.setFixedWidth(100)
        self.nh3 = QLineEdit()
        nh3_layout.addWidget(nh3_label)
        nh3_layout.addWidget(self.nh3)
        static_route_layout.addLayout(nh3_layout)
        
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
        
        mgmt_net_layout = QHBoxLayout()
        mgmt_net_label = QLabel('管理网段:')
        mgmt_net_label.setFixedWidth(100)
        self.mgmt_net = QLineEdit()
        mgmt_net_layout.addWidget(mgmt_net_label)
        mgmt_net_layout.addWidget(self.mgmt_net)
        ospf_layout.addLayout(mgmt_net_layout)
        
        mgmt_wild_layout = QHBoxLayout()
        mgmt_wild_label = QLabel('管理网段反掩码:')
        mgmt_wild_label.setFixedWidth(100)
        self.mgmt_wild = QLineEdit()
        mgmt_wild_layout.addWidget(mgmt_wild_label)
        mgmt_wild_layout.addWidget(self.mgmt_wild)
        ospf_layout.addLayout(mgmt_wild_layout)
        
        user_net_layout = QHBoxLayout()
        user_net_label = QLabel('用户网段:')
        user_net_label.setFixedWidth(100)
        self.user_net = QLineEdit()
        user_net_layout.addWidget(user_net_label)
        user_net_layout.addWidget(self.user_net)
        ospf_layout.addLayout(user_net_layout)
        
        user_wild_layout = QHBoxLayout()
        user_wild_label = QLabel('用户网段反掩码:')
        user_wild_label.setFixedWidth(100)
        self.user_wild = QLineEdit()
        user_wild_layout.addWidget(user_wild_label)
        user_wild_layout.addWidget(self.user_wild)
        ospf_layout.addLayout(user_wild_layout)
        
        server_net_layout = QHBoxLayout()
        server_net_label = QLabel('服务器网段:')
        server_net_label.setFixedWidth(100)
        self.server_net = QLineEdit()
        server_net_layout.addWidget(server_net_label)
        server_net_layout.addWidget(self.server_net)
        ospf_layout.addLayout(server_net_layout)
        
        server_wild_layout = QHBoxLayout()
        server_wild_label = QLabel('服务器网段反掩码:')
        server_wild_label.setFixedWidth(100)
        self.server_wild = QLineEdit()
        server_wild_layout.addWidget(server_wild_label)
        server_wild_layout.addWidget(self.server_wild)
        ospf_layout.addLayout(server_wild_layout)
        
        area_id_layout = QHBoxLayout()
        area_id_label = QLabel('OSPF 区域号:')
        area_id_label.setFixedWidth(100)
        self.area_id = QLineEdit()
        area_id_layout.addWidget(area_id_label)
        area_id_layout.addWidget(self.area_id)
        ospf_layout.addLayout(area_id_layout)
        
        ospf_config.setLayout(ospf_layout)
        route_layout.addWidget(ospf_config)
        
        route_config.setLayout(route_layout)
        layout.addWidget(route_config)
        
        # 面板4：DHCP 服务 & 安全防环配置
        dhcp_security_config = QGroupBox('DHCP 服务 & 安全防环配置')
        dhcp_security_layout = QVBoxLayout()
        
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
        
        server_ex_start_layout = QHBoxLayout()
        server_ex_start_label = QLabel('服务器网段排除起始 IP:')
        server_ex_start_label.setFixedWidth(100)
        self.server_ex_start = QLineEdit()
        server_ex_start_layout.addWidget(server_ex_start_label)
        server_ex_start_layout.addWidget(self.server_ex_start)
        dhcp_server_layout.addLayout(server_ex_start_layout)
        
        server_ex_end_layout = QHBoxLayout()
        server_ex_end_label = QLabel('服务器网段排除结束 IP:')
        server_ex_end_label.setFixedWidth(100)
        self.server_ex_end = QLineEdit()
        server_ex_end_layout.addWidget(server_ex_end_label)
        server_ex_end_layout.addWidget(self.server_ex_end)
        dhcp_server_layout.addLayout(server_ex_end_layout)
        
        user_pool_layout = QHBoxLayout()
        user_pool_label = QLabel('用户地址池名称:')
        user_pool_label.setFixedWidth(100)
        self.user_pool = QLineEdit()
        user_pool_layout.addWidget(user_pool_label)
        user_pool_layout.addWidget(self.user_pool)
        dhcp_server_layout.addLayout(user_pool_layout)
        
        server_pool_layout = QHBoxLayout()
        server_pool_label = QLabel('服务器地址池名称:')
        server_pool_label.setFixedWidth(100)
        self.server_pool = QLineEdit()
        server_pool_layout.addWidget(server_pool_label)
        server_pool_layout.addWidget(self.server_pool)
        dhcp_server_layout.addLayout(server_pool_layout)
        
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
        dhcp_security_layout.addWidget(dhcp_server_config)
        
        # DHCP Snooping 安全配置
        dhcp_snooping_config = QGroupBox('DHCP Snooping 安全配置')
        dhcp_snooping_layout = QVBoxLayout()
        
        trust_port_layout = QHBoxLayout()
        trust_port_label = QLabel('信任上联端口:')
        trust_port_label.setFixedWidth(100)
        self.trust_port = QLineEdit()
        trust_port_layout.addWidget(trust_port_label)
        trust_port_layout.addWidget(self.trust_port)
        dhcp_snooping_layout.addLayout(trust_port_layout)
        
        snooping_vlan_layout = QHBoxLayout()
        snooping_vlan_label = QLabel('监听 VLAN 列表:')
        snooping_vlan_label.setFixedWidth(100)
        self.snooping_vlan = QLineEdit()
        snooping_vlan_layout.addWidget(snooping_vlan_label)
        snooping_vlan_layout.addWidget(self.snooping_vlan)
        dhcp_snooping_layout.addLayout(snooping_vlan_layout)
        
        dhcp_snooping_config.setLayout(dhcp_snooping_layout)
        dhcp_security_layout.addWidget(dhcp_snooping_config)
        
        # MSTP 生成树防环配置
        mstp_config = QGroupBox('MSTP 生成树防环配置')
        mstp_layout = QVBoxLayout()
        
        mst_name_layout = QHBoxLayout()
        mst_name_label = QLabel('MST 域名:')
        mst_name_label.setFixedWidth(100)
        self.mst_name = QLineEdit()
        mst_name_layout.addWidget(mst_name_label)
        mst_name_layout.addWidget(self.mst_name)
        mstp_layout.addLayout(mst_name_layout)
        
        ins1_vlan_layout = QHBoxLayout()
        ins1_vlan_label = QLabel('实例 1 VLAN 列表:')
        ins1_vlan_label.setFixedWidth(100)
        self.ins1_vlan = QLineEdit()
        ins1_vlan_layout.addWidget(ins1_vlan_label)
        ins1_vlan_layout.addWidget(self.ins1_vlan)
        mstp_layout.addLayout(ins1_vlan_layout)
        
        ins2_vlan_layout = QHBoxLayout()
        ins2_vlan_label = QLabel('实例 2 VLAN 列表:')
        ins2_vlan_label.setFixedWidth(100)
        self.ins2_vlan = QLineEdit()
        ins2_vlan_layout.addWidget(ins2_vlan_label)
        ins2_vlan_layout.addWidget(self.ins2_vlan)
        mstp_layout.addLayout(ins2_vlan_layout)
        
        mst_prio_layout = QHBoxLayout()
        mst_prio_label = QLabel('生成树优先级:')
        mst_prio_label.setFixedWidth(100)
        self.mst_prio = QLineEdit()
        mst_prio_layout.addWidget(mst_prio_label)
        mst_prio_layout.addWidget(self.mst_prio)
        mstp_layout.addLayout(mst_prio_layout)
        
        mstp_config.setLayout(mstp_layout)
        dhcp_security_layout.addWidget(mstp_config)
        
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
        dhcp_security_layout.addWidget(acl_config)
        
        dhcp_security_config.setLayout(dhcp_security_layout)
        layout.addWidget(dhcp_security_config)
        
        # 面板5：运维监控配置
        maintenance_config = QGroupBox('运维监控配置')
        maintenance_layout = QVBoxLayout()
        
        # NTP 时钟同步配置
        ntp_config = QGroupBox('NTP 时钟同步配置')
        ntp_layout = QVBoxLayout()
        
        ntp_server_layout = QHBoxLayout()
        ntp_server_label = QLabel('NTP 服务器 IP 地址:')
        ntp_server_label.setFixedWidth(100)
        self.ntp_server = QLineEdit()
        ntp_server_layout.addWidget(ntp_server_label)
        ntp_server_layout.addWidget(self.ntp_server)
        ntp_layout.addLayout(ntp_server_layout)
        
        ntp_config.setLayout(ntp_layout)
        maintenance_layout.addWidget(ntp_config)
        
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
        
        mirror_dst_layout = QHBoxLayout()
        mirror_dst_label = QLabel('镜像目的端口:')
        mirror_dst_label.setFixedWidth(100)
        self.mirror_dst = QLineEdit()
        mirror_dst_layout.addWidget(mirror_dst_label)
        mirror_dst_layout.addWidget(self.mirror_dst)
        mirror_layout.addLayout(mirror_dst_layout)
        
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
line console 0
 password {self.console_password.text()}
 login
 exec-timeout 10 0
 logging synchronous
exit
clock set {self.system_time.text()}
clock timezone BJ +8

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

# 业务 VLAN 创建
vlan {self.user_vlan.text()}
 name User_VLAN
vlan {self.server_vlan.text()}
 name Server_VLAN
exit

# 上联 Trunk 端口配置
interface GigabitEthernet {self.up_port.text()}
 switchport mode trunk
 switchport trunk allowed vlan all
 switchport trunk native vlan {self.mgmt_vlan.text()}
 no shutdown
exit

# 链路聚合配置
interface Port-channel {self.static_agg_id.text()}
 switchport mode trunk
 switchport trunk allowed vlan all
exit
interface range {self.static_agg_ports.text()}
 channel-group {self.static_agg_id.text()} mode on
 no shutdown
exit

interface Port-channel {self.lacp_agg_id.text()}
 switchport mode trunk
 switchport trunk allowed vlan all
exit
interface range {self.lacp_agg_ports.text()}
 channel-group {self.lacp_agg_id.text()} mode active
 no shutdown
exit

# 下联 Access 端口配置
interface range {self.down_port_range.text()}
 switchport mode access
 switchport access vlan {self.user_vlan.text()}
 no shutdown
exit

# 业务 VLANIF 三层网关配置
interface Vlan {self.user_vlan.text()}
 ip address {self.user_gw.text()} {self.user_mask.text()}
 no shutdown
exit

interface Vlan {self.server_vlan.text()}
 ip address {self.server_gw.text()} {self.server_mask.text()}
 no shutdown
exit

# 静态路由配置
ip route {self.dst_net1.text()} {self.dst_mask1.text()} {self.nh1.text()}
ip route {self.dst_net2.text()} {self.dst_mask2.text()} {self.nh2.text()}
ip route {self.dst_net3.text()} {self.dst_mask3.text()} {self.nh3.text()}

# OSPF 动态路由配置
router ospf {self.ospf_proc.text()}
 router-id {self.ospf_rid.text()}
 network {self.mgmt_net.text()} {self.mgmt_wild.text()} area {self.area_id.text()}
 network {self.user_net.text()} {self.user_wild.text()} area {self.area_id.text()}
 network {self.server_net.text()} {self.server_wild.text()} area {self.area_id.text()}
exit
interface Vlan {self.mgmt_vlan.text()}
 ip ospf {self.ospf_proc.text()} area {self.area_id.text()}
exit
interface Vlan {self.user_vlan.text()}
 ip ospf {self.ospf_proc.text()} area {self.area_id.text()}
exit
interface Vlan {self.server_vlan.text()}
 ip ospf {self.ospf_proc.text()} area {self.area_id.text()}
exit

# DHCP 服务配置
service dhcp
ip dhcp relay information option
ip dhcp excluded-address {self.user_ex_start.text()} {self.user_ex_end.text()}
ip dhcp excluded-address {self.server_ex_start.text()} {self.server_ex_end.text()}

ip dhcp pool {self.user_pool.text()}
 network {self.user_net.text()} {self.user_mask.text()}
 default-router {self.user_gw.text()}
 dns-server {self.dns1.text()} {self.dns2.text()}
 lease 7 0 0
exit

ip dhcp pool {self.server_pool.text()}
 network {self.server_net.text()} {self.server_mask.text()}
 default-router {self.server_gw.text()}
 dns-server {self.dns1.text()} {self.dns2.text()}
 lease 30 0 0
exit

# DHCP Snooping 安全配置
ip dhcp snooping
ip dhcp snooping vlan {self.snooping_vlan.text()}
ip dhcp snooping verify mac-address
interface {self.trust_port.text()}
 ip dhcp snooping trust
exit

# MSTP 生成树防环配置
spanning-tree mode mst
spanning-tree mst configuration
 name {self.mst_name.text()}
 revision 1
 instance 1 vlan {self.ins1_vlan.text()}
 instance 2 vlan {self.ins2_vlan.text()}
 exit
spanning-tree mst 1 priority {self.mst_prio.text()}
spanning-tree

# ACL 访问控制配置
ip access-list standard 10
 permit {self.manage_net.text()} {self.manage_wild.text()}
 deny any
exit
line vty 0 15
 access-class 10 in
exit

# 运维监控配置
ntp server {self.ntp_server.text()}
ntp update-calendar

snmp-server community {self.snmp_ro_community.text()} ro
snmp-server host {self.trap_server.text()} traps version 2c {self.trap_community.text()}
snmp-server enable traps

# 端口镜像配置
monitor session 1 source interface {self.mirror_src.text()} both
monitor session 1 destination interface {self.mirror_dst.text()}

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
        self.mgmt_vlan.clear()
        self.mgmt_ip.clear()
        self.mgmt_mask.clear()
        self.ssh_user.clear()
        self.ssh_pwd.clear()
        self.telnet_pwd.clear()
        self.user_vlan.clear()
        self.server_vlan.clear()
        self.up_port.clear()
        self.static_agg_id.clear()
        self.static_agg_ports.clear()
        self.lacp_agg_id.clear()
        self.lacp_agg_ports.clear()
        self.down_port_range.clear()
        self.user_gw.clear()
        self.user_mask.clear()
        self.server_gw.clear()
        self.server_mask.clear()
        self.dst_net1.clear()
        self.dst_mask1.clear()
        self.nh1.clear()
        self.dst_net2.clear()
        self.dst_mask2.clear()
        self.nh2.clear()
        self.dst_net3.clear()
        self.dst_mask3.clear()
        self.nh3.clear()
        self.ospf_proc.clear()
        self.ospf_rid.clear()
        self.mgmt_net.clear()
        self.mgmt_wild.clear()
        self.user_net.clear()
        self.user_wild.clear()
        self.server_net.clear()
        self.server_wild.clear()
        self.area_id.clear()
        self.user_ex_start.clear()
        self.user_ex_end.clear()
        self.server_ex_start.clear()
        self.server_ex_end.clear()
        self.user_pool.clear()
        self.server_pool.clear()
        self.dns1.clear()
        self.dns2.clear()
        self.trust_port.clear()
        self.snooping_vlan.clear()
        self.mst_name.clear()
        self.ins1_vlan.clear()
        self.ins2_vlan.clear()
        self.mst_prio.clear()
        self.manage_net.clear()
        self.manage_wild.clear()
        self.ntp_server.clear()
        self.snmp_ro_community.clear()
        self.trap_server.clear()
        self.trap_community.clear()
        self.mirror_src.clear()
        self.mirror_dst.clear()
        # 重置代码编辑器
        self.code_editor.clear()