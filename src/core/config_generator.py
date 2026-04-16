class ConfigGenerator:
    """配置生成器类"""
    
    @staticmethod
    def generate_access_switch_config(vendor, **kwargs):
        """生成接入交换机配置"""
        if vendor == 'huawei':
            return ConfigGenerator._generate_huawei_access_switch_config(**kwargs)
        elif vendor == 'ruijie':
            return ConfigGenerator._generate_ruijie_access_switch_config(**kwargs)
        elif vendor == 'h3c':
            return ConfigGenerator._generate_h3c_access_switch_config(**kwargs)
        elif vendor == 'cisco':
            return ConfigGenerator._generate_cisco_access_switch_config(**kwargs)
        else:
            return "# 不支持的厂商"
    
    @staticmethod
    def generate_core_switch_config(vendor, **kwargs):
        """生成核心交换机配置"""
        if vendor == 'huawei':
            return ConfigGenerator._generate_huawei_core_switch_config(**kwargs)
        elif vendor == 'ruijie':
            return ConfigGenerator._generate_ruijie_core_switch_config(**kwargs)
        elif vendor == 'h3c':
            return ConfigGenerator._generate_h3c_core_switch_config(**kwargs)
        elif vendor == 'cisco':
            return ConfigGenerator._generate_cisco_core_switch_config(**kwargs)
        else:
            return "# 不支持的厂商"
    
    @staticmethod
    def generate_router_config(vendor, **kwargs):
        """生成路由器配置"""
        if vendor == 'huawei':
            return ConfigGenerator._generate_huawei_router_config(**kwargs)
        elif vendor == 'ruijie':
            return ConfigGenerator._generate_ruijie_router_config(**kwargs)
        elif vendor == 'h3c':
            return ConfigGenerator._generate_h3c_router_config(**kwargs)
        elif vendor == 'cisco':
            return ConfigGenerator._generate_cisco_router_config(**kwargs)
        else:
            return "# 不支持的厂商"
    
    @staticmethod
    def generate_ac_config(vendor, **kwargs):
        """生成AC配置"""
        if vendor == 'huawei':
            return ConfigGenerator._generate_huawei_ac_config(**kwargs)
        elif vendor == 'ruijie':
            return ConfigGenerator._generate_ruijie_ac_config(**kwargs)
        elif vendor == 'h3c':
            return ConfigGenerator._generate_h3c_ac_config(**kwargs)
        elif vendor == 'cisco':
            return ConfigGenerator._generate_cisco_ac_config(**kwargs)
        else:
            return "# 不支持的厂商"
    
    # 华为接入交换机配置
    @staticmethod
    def _generate_huawei_access_switch_config(**kwargs):
        config = f"""
# 设备基础信息
<HUAWEI> system-view
[HUAWEI] sysname {kwargs.get('hostname', 'Switch')}
[HUAWEI] super password cipher {kwargs.get('enable_password', 'admin123')}
[HUAWEI] clock timezone BJ add 08:00:00
[HUAWEI] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 管理VLAN配置
[HUAWEI] vlan {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[HUAWEI] interface vlanif {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[HUAWEI] user-interface console 0
[HUAWEI-ui-console0] authentication-mode password
[HUAWEI-ui-console0] set authentication password cipher {kwargs.get('console_password', 'admin123')}
[HUAWEI-ui-console0] quit
[HUAWEI] user-interface vty 0 4
[HUAWEI-ui-vty0-4] authentication-mode aaa
[HUAWEI-ui-vty0-4] protocol inbound ssh
[HUAWEI-ui-vty0-4] quit
[HUAWEI] aaa
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} password cipher {kwargs.get('ssh_pwd', 'admin123')}
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} privilege level 15
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} service-type ssh
[HUAWEI-aaa] quit
[HUAWEI] ssh server enable

# 业务VLAN创建
[HUAWEI] vlan batch {kwargs.get('user_vlan', '10')} {kwargs.get('server_vlan', '20')}

# 上联Trunk端口配置
[HUAWEI] interface {kwargs.get('up_port', 'GigabitEthernet0/0/1')}
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port link-type trunk
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port trunk allow-pass vlan all
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] quit

# 下联Access端口配置
[HUAWEI] interface range {kwargs.get('down_port_range', 'GigabitEthernet0/0/2 to GigabitEthernet0/0/24')}
[HUAWEI-if-range] port link-type access
[HUAWEI-if-range] port default vlan {kwargs.get('user_vlan', '10')}
[HUAWEI-if-range] quit

# 安全防环配置
[HUAWEI] stp enable
[HUAWEI] stp mode rstp
[HUAWEI] interface range {kwargs.get('down_port_range', 'GigabitEthernet0/0/2 to GigabitEthernet0/0/24')}
[HUAWEI-if-range] stp edged-port enable
[HUAWEI-if-range] quit

# DHCP Snooping配置
[HUAWEI] dhcp enable
[HUAWEI] dhcp snooping enable
[HUAWEI] vlan {kwargs.get('user_vlan', '10')}
[HUAWEI-vlan{kwargs.get('user_vlan', '10')}] dhcp snooping enable
[HUAWEI-vlan{kwargs.get('user_vlan', '10')}] quit
[HUAWEI] interface {kwargs.get('up_port', 'GigabitEthernet0/0/1')}
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] dhcp snooping trust
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] quit

# 运维监控配置
[HUAWEI] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}
[HUAWEI] snmp-agent
[HUAWEI] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[HUAWEI] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[HUAWEI] snmp-agent trap enable

[HUAWEI] save
<HUAWEI>
        """
        return config
    
    # 锐捷接入交换机配置
    @staticmethod
    def _generate_ruijie_access_switch_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'Switch')}
enable secret {kwargs.get('enable_password', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 January 2024')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 业务VLAN创建
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('server_vlan', '20')}
 name Server_VLAN

# 上联Trunk端口配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 下联Access端口配置
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/2-24')}
 switchport mode access
 switchport access vlan {kwargs.get('user_vlan', '10')}
 no shutdown

# 安全防环配置
spanning-tree
spanning-tree mode rstp
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/2-24')}
 spanning-tree portfast

# DHCP Snooping配置
service dhcp
ip dhcp snooping
ip dhcp snooping vlan {kwargs.get('user_vlan', '10')}
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 ip dhcp snooping trust

# 运维监控配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config
    
    # H3C接入交换机配置
    @staticmethod
    def _generate_h3c_access_switch_config(**kwargs):
        config = f"""
# 设备基础信息
system-view
[H3C] sysname {kwargs.get('hostname', 'Switch')}
[H3C] super password level 3 simple {kwargs.get('enable_password', 'admin123')}
[H3C] clock timezone BJ add 08:00:00
[H3C] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 管理VLAN配置
[H3C] vlan {kwargs.get('mgmt_vlan', '100')}
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[H3C] interface vlan-interface {kwargs.get('mgmt_vlan', '100')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[H3C] user-interface console 0
[H3C-ui-console0] authentication-mode password
[H3C-ui-console0] set authentication password simple {kwargs.get('console_password', 'admin123')}
[H3C-ui-console0] quit
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] authentication-mode scheme
[H3C-ui-vty0-4] protocol inbound ssh
[H3C-ui-vty0-4] quit
[H3C] local-user {kwargs.get('ssh_user', 'admin')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] password simple {kwargs.get('ssh_pwd', 'admin123')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] service-type ssh
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] authorization-attribute user-role network-admin
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] quit
[H3C] ssh server enable

# 业务VLAN创建
[H3C] vlan {kwargs.get('user_vlan', '10')}
[H3C-vlan{kwargs.get('user_vlan', '10')}] name User_VLAN
[H3C-vlan{kwargs.get('user_vlan', '10')}] quit
[H3C] vlan {kwargs.get('server_vlan', '20')}
[H3C-vlan{kwargs.get('server_vlan', '20')}] name Server_VLAN
[H3C-vlan{kwargs.get('server_vlan', '20')}] quit

# 上联Trunk端口配置
[H3C] interface {kwargs.get('up_port', 'GigabitEthernet1/0/1')}
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port link-type trunk
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port trunk permit vlan all
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] quit

# 下联Access端口配置
[H3C] interface range {kwargs.get('down_port_range', 'GigabitEthernet1/0/2 to GigabitEthernet1/0/24')}
[H3C-if-range] port link-type access
[H3C-if-range] port access vlan {kwargs.get('user_vlan', '10')}
[H3C-if-range] quit

# 安全防环配置
[H3C] stp enable
[H3C] stp mode rstp
[H3C] interface range {kwargs.get('down_port_range', 'GigabitEthernet1/0/2 to GigabitEthernet1/0/24')}
[H3C-if-range] stp edged-port enable
[H3C-if-range] quit

# DHCP Snooping配置
[H3C] dhcp-snooping
[H3C] interface vlan-interface {kwargs.get('user_vlan', '10')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] dhcp-snooping enable
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] quit
[H3C] interface {kwargs.get('up_port', 'GigabitEthernet1/0/1')}
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] dhcp-snooping trust
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] quit

# 运维监控配置
[H3C] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}
[H3C] snmp-agent
[H3C] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[H3C] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[H3C] snmp-agent trap enable

[H3C] save
<H3C>
        """
        return config
    
    # Cisco接入交换机配置
    @staticmethod
    def _generate_cisco_access_switch_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'Switch')}
enable secret {kwargs.get('enable_password', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 Jan 2024')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 业务VLAN创建
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('server_vlan', '20')}
 name Server_VLAN

# 上联Trunk端口配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 下联Access端口配置
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/2-24')}
 switchport mode access
 switchport access vlan {kwargs.get('user_vlan', '10')}
 no shutdown

# 安全防环配置
spanning-tree
spanning-tree mode rapid-pvst
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/2-24')}
 spanning-tree portfast

# DHCP Snooping配置
service dhcp
ip dhcp snooping
ip dhcp snooping vlan {kwargs.get('user_vlan', '10')}
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 ip dhcp snooping trust

# 运维监控配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config
    
    # 华为核心交换机配置
    @staticmethod
    def _generate_huawei_core_switch_config(**kwargs):
        config = f"""
# 设备基础信息
<HUAWEI> system-view
[HUAWEI] sysname {kwargs.get('hostname', 'CoreSwitch')}
[HUAWEI] super password cipher {kwargs.get('enable_secret', 'admin123')}
[HUAWEI] clock timezone BJ add 08:00:00
[HUAWEI] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 管理VLAN配置
[HUAWEI] vlan {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[HUAWEI] interface vlanif {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[HUAWEI] user-interface console 0
[HUAWEI-ui-console0] authentication-mode password
[HUAWEI-ui-console0] set authentication password cipher {kwargs.get('console_password', 'admin123')}
[HUAWEI-ui-console0] quit
[HUAWEI] user-interface vty 0 4
[HUAWEI-ui-vty0-4] authentication-mode aaa
[HUAWEI-ui-vty0-4] protocol inbound ssh
[HUAWEI-ui-vty0-4] quit
[HUAWEI] aaa
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} password cipher {kwargs.get('ssh_pwd', 'admin123')}
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} privilege level 15
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} service-type ssh
[HUAWEI-aaa] quit
[HUAWEI] ssh server enable

# 业务VLAN创建
[HUAWEI] vlan batch {kwargs.get('user_vlan', '10')} {kwargs.get('server_vlan', '20')}

# 上联Trunk端口配置
[HUAWEI] interface {kwargs.get('up_port', 'GigabitEthernet0/0/1')}
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port link-type trunk
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port trunk allow-pass vlan all
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] quit

# 链路聚合配置
[HUAWEI] interface Eth-Trunk {kwargs.get('static_agg_id', '1')}
[HUAWEI-Eth-Trunk{kwargs.get('static_agg_id', '1')}] port link-type trunk
[HUAWEI-Eth-Trunk{kwargs.get('static_agg_id', '1')}] port trunk allow-pass vlan all
[HUAWEI-Eth-Trunk{kwargs.get('static_agg_id', '1')}] mode lacp-static
[HUAWEI-Eth-Trunk{kwargs.get('static_agg_id', '1')}] quit
[HUAWEI] interface range {kwargs.get('static_agg_ports', 'GigabitEthernet0/0/2 to GigabitEthernet0/0/4')}
[HUAWEI-if-range] eth-trunk {kwargs.get('static_agg_id', '1')}
[HUAWEI-if-range] quit

# 下联Access端口配置
[HUAWEI] interface range {kwargs.get('down_port_range', 'GigabitEthernet0/0/5 to GigabitEthernet0/0/24')}
[HUAWEI-if-range] port link-type access
[HUAWEI-if-range] port default vlan {kwargs.get('user_vlan', '10')}
[HUAWEI-if-range] quit

# 三层网关配置
[HUAWEI] interface vlanif {kwargs.get('user_vlan', '10')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] quit
[HUAWEI] interface vlanif {kwargs.get('server_vlan', '20')}
[HUAWEI-Vlanif{kwargs.get('server_vlan', '20')}] ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('server_vlan', '20')}] quit

# 静态路由配置
[HUAWEI] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# OSPF配置
[HUAWEI] ospf {kwargs.get('ospf_proc', '1')}
[HUAWEI-ospf-1] router-id {kwargs.get('ospf_rid', '1.1.1.1')}
[HUAWEI-ospf-1] area {kwargs.get('area_id', '0')}
[HUAWEI-ospf-1-area-0.0.0.0] network {kwargs.get('mgmt_net', '192.168.100.0')} {kwargs.get('mgmt_wild', '0.0.0.255')}
[HUAWEI-ospf-1-area-0.0.0.0] network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_wild', '0.0.0.255')}
[HUAWEI-ospf-1-area-0.0.0.0] network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_wild', '0.0.0.255')}
[HUAWEI-ospf-1-area-0.0.0.0] quit
[HUAWEI-ospf-1] quit

# DHCP配置
[HUAWEI] dhcp enable
[HUAWEI] ip pool {kwargs.get('user_pool', 'user_pool')}
[HUAWEI-ip-pool-user_pool] gateway-list {kwargs.get('user_gw', '192.168.10.1')}
[HUAWEI-ip-pool-user_pool] network {kwargs.get('user_net', '192.168.10.0')} mask {kwargs.get('user_mask', '255.255.255.0')}
[HUAWEI-ip-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[HUAWEI-ip-pool-user_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[HUAWEI-ip-pool-user_pool] quit
[HUAWEI] ip pool {kwargs.get('server_pool', 'server_pool')}
[HUAWEI-ip-pool-server_pool] gateway-list {kwargs.get('server_gw', '192.168.20.1')}
[HUAWEI-ip-pool-server_pool] network {kwargs.get('server_net', '192.168.20.0')} mask {kwargs.get('server_mask', '255.255.255.0')}
[HUAWEI-ip-pool-server_pool] excluded-ip-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
[HUAWEI-ip-pool-server_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[HUAWEI-ip-pool-server_pool] quit
[HUAWEI] interface vlanif {kwargs.get('user_vlan', '10')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] dhcp select global
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] quit
[HUAWEI] interface vlanif {kwargs.get('server_vlan', '20')}
[HUAWEI-Vlanif{kwargs.get('server_vlan', '20')}] dhcp select global
[HUAWEI-Vlanif{kwargs.get('server_vlan', '20')}] quit

# 安全配置
[HUAWEI] dhcp snooping enable
[HUAWEI] vlan {kwargs.get('user_vlan', '10')}
[HUAWEI-vlan{kwargs.get('user_vlan', '10')}] dhcp snooping enable
[HUAWEI-vlan{kwargs.get('user_vlan', '10')}] quit
[HUAWEI] interface {kwargs.get('up_port', 'GigabitEthernet0/0/1')}
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] dhcp snooping trust
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] quit

# MSTP配置
[HUAWEI] stp enable
[HUAWEI] stp mode mstp
[HUAWEI] stp region-configuration
[HUAWEI-mst-region] region-name {kwargs.get('mst_name', 'Core')}
[HUAWEI-mst-region] instance {kwargs.get('ins1_vlan', '1')} vlan {kwargs.get('ins1_vlan', '10')}
[HUAWEI-mst-region] instance {kwargs.get('ins2_vlan', '2')} vlan {kwargs.get('ins2_vlan', '20')}
[HUAWEI-mst-region] active region-configuration
[HUAWEI-mst-region] quit
[HUAWEI] stp instance {kwargs.get('ins1_vlan', '1')} priority {kwargs.get('mst_prio', '4096')}

# 运维监控配置
[HUAWEI] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}
[HUAWEI] snmp-agent
[HUAWEI] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[HUAWEI] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[HUAWEI] snmp-agent trap enable

[HUAWEI] save
<HUAWEI>
        """
        return config
    
    # 锐捷核心交换机配置
    @staticmethod
    def _generate_ruijie_core_switch_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'CoreSwitch')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 January 2024')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 业务VLAN创建
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('server_vlan', '20')}
 name Server_VLAN

# 上联Trunk端口配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 链路聚合配置
interface Port-channel {kwargs.get('static_agg_id', '1')}
 switchport mode trunk
 switchport trunk allowed vlan all
interface range {kwargs.get('static_agg_ports', 'GigabitEthernet0/2-4')}
 channel-group {kwargs.get('static_agg_id', '1')} mode on
 no shutdown

# 下联Access端口配置
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/5-24')}
 switchport mode access
 switchport access vlan {kwargs.get('user_vlan', '10')}
 no shutdown

# 三层网关配置
interface vlan {kwargs.get('user_vlan', '10')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown
interface vlan {kwargs.get('server_vlan', '20')}
 ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
 no shutdown

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# OSPF配置
router ospf {kwargs.get('ospf_proc', '1')}
 router-id {kwargs.get('ospf_rid', '1.1.1.1')}
 network {kwargs.get('mgmt_net', '192.168.100.0')} {kwargs.get('mgmt_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}

# DHCP配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
ip dhcp pool {kwargs.get('user_pool', 'user_pool')}
 network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_mask', '255.255.255.0')}
 default-router {kwargs.get('user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 7 0 0
ip dhcp pool {kwargs.get('server_pool', 'server_pool')}
 network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_mask', '255.255.255.0')}
 default-router {kwargs.get('server_gw', '192.168.20.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 30 0 0

# 安全配置
ip dhcp snooping
ip dhcp snooping vlan {kwargs.get('user_vlan', '10')}
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 ip dhcp snooping trust

# MSTP配置
spanning-tree mode mst
spanning-tree mst configuration
 name {kwargs.get('mst_name', 'Core')}
 revision 1
 instance {kwargs.get('ins1_vlan', '1')} vlan {kwargs.get('ins1_vlan', '10')}
 instance {kwargs.get('ins2_vlan', '2')} vlan {kwargs.get('ins2_vlan', '20')}
 exit
spanning-tree mst {kwargs.get('ins1_vlan', '1')} priority {kwargs.get('mst_prio', '4096')}

# 运维监控配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config
    
    # H3C核心交换机配置
    @staticmethod
    def _generate_h3c_core_switch_config(**kwargs):
        config = f"""
# 设备基础信息
system-view
[H3C] sysname {kwargs.get('hostname', 'CoreSwitch')}
[H3C] super password level 3 simple {kwargs.get('enable_secret', 'admin123')}
[H3C] clock timezone BJ add 08:00:00
[H3C] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 管理VLAN配置
[H3C] vlan {kwargs.get('mgmt_vlan', '100')}
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[H3C] interface vlan-interface {kwargs.get('mgmt_vlan', '100')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[H3C] user-interface console 0
[H3C-ui-console0] authentication-mode password
[H3C-ui-console0] set authentication password simple {kwargs.get('console_password', 'admin123')}
[H3C-ui-console0] quit
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] authentication-mode scheme
[H3C-ui-vty0-4] protocol inbound ssh
[H3C-ui-vty0-4] quit
[H3C] local-user {kwargs.get('ssh_user', 'admin')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] password simple {kwargs.get('ssh_pwd', 'admin123')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] service-type ssh
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] authorization-attribute user-role network-admin
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] quit
[H3C] ssh server enable

# 业务VLAN创建
[H3C] vlan {kwargs.get('user_vlan', '10')}
[H3C-vlan{kwargs.get('user_vlan', '10')}] name User_VLAN
[H3C-vlan{kwargs.get('user_vlan', '10')}] quit
[H3C] vlan {kwargs.get('server_vlan', '20')}
[H3C-vlan{kwargs.get('server_vlan', '20')}] name Server_VLAN
[H3C-vlan{kwargs.get('server_vlan', '20')}] quit

# 上联Trunk端口配置
[H3C] interface {kwargs.get('up_port', 'GigabitEthernet1/0/1')}
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port link-type trunk
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port trunk permit vlan all
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] quit

# 链路聚合配置
[H3C] interface Bridge-Aggregation {kwargs.get('static_agg_id', '1')}
[H3C-Bridge-Aggregation{kwargs.get('static_agg_id', '1')}] port link-type trunk
[H3C-Bridge-Aggregation{kwargs.get('static_agg_id', '1')}] port trunk permit vlan all
[H3C-Bridge-Aggregation{kwargs.get('static_agg_id', '1')}] quit
[H3C] interface range {kwargs.get('static_agg_ports', 'GigabitEthernet1/0/2 to GigabitEthernet1/0/4')}
[H3C-if-range] port link-aggregation group {kwargs.get('static_agg_id', '1')}
[H3C-if-range] quit

# 下联Access端口配置
[H3C] interface range {kwargs.get('down_port_range', 'GigabitEthernet1/0/5 to GigabitEthernet1/0/24')}
[H3C-if-range] port link-type access
[H3C-if-range] port access vlan {kwargs.get('user_vlan', '10')}
[H3C-if-range] quit

# 三层网关配置
[H3C] interface vlan-interface {kwargs.get('user_vlan', '10')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] quit
[H3C] interface vlan-interface {kwargs.get('server_vlan', '20')}
[H3C-Vlan-interface{kwargs.get('server_vlan', '20')}] ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('server_vlan', '20')}] quit

# 静态路由配置
[H3C] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# OSPF配置
[H3C] ospf {kwargs.get('ospf_proc', '1')}
[H3C-ospf-1] router-id {kwargs.get('ospf_rid', '1.1.1.1')}
[H3C-ospf-1] area {kwargs.get('area_id', '0')}
[H3C-ospf-1-area-0.0.0.0] network {kwargs.get('mgmt_net', '192.168.100.0')} {kwargs.get('mgmt_wild', '0.0.0.255')}
[H3C-ospf-1-area-0.0.0.0] network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_wild', '0.0.0.255')}
[H3C-ospf-1-area-0.0.0.0] network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_wild', '0.0.0.255')}
[H3C-ospf-1-area-0.0.0.0] quit
[H3C-ospf-1] quit

# DHCP配置
[H3C] dhcp enable
[H3C] dhcp server ip-pool {kwargs.get('user_pool', 'user_pool')}
[H3C-dhcp-pool-user_pool] network {kwargs.get('user_net', '192.168.10.0')} mask {kwargs.get('user_mask', '255.255.255.0')}
[H3C-dhcp-pool-user_pool] gateway-list {kwargs.get('user_gw', '192.168.10.1')}
[H3C-dhcp-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[H3C-dhcp-pool-user_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[H3C-dhcp-pool-user_pool] quit
[H3C] dhcp server ip-pool {kwargs.get('server_pool', 'server_pool')}
[H3C-dhcp-pool-server_pool] network {kwargs.get('server_net', '192.168.20.0')} mask {kwargs.get('server_mask', '255.255.255.0')}
[H3C-dhcp-pool-server_pool] gateway-list {kwargs.get('server_gw', '192.168.20.1')}
[H3C-dhcp-pool-server_pool] excluded-ip-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
[H3C-dhcp-pool-server_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[H3C-dhcp-pool-server_pool] quit

# 安全配置
[H3C] dhcp-snooping
[H3C] interface vlan-interface {kwargs.get('user_vlan', '10')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] dhcp-snooping enable
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] quit
[H3C] interface {kwargs.get('up_port', 'GigabitEthernet1/0/1')}
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] dhcp-snooping trust
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] quit

# MSTP配置
[H3C] stp enable
[H3C] stp mode mstp
[H3C] stp region-configuration
[H3C-mst-region] region-name {kwargs.get('mst_name', 'Core')}
[H3C-mst-region] instance {kwargs.get('ins1_vlan', '1')} vlan {kwargs.get('ins1_vlan', '10')}
[H3C-mst-region] instance {kwargs.get('ins2_vlan', '2')} vlan {kwargs.get('ins2_vlan', '20')}
[H3C-mst-region] active region-configuration
[H3C-mst-region] quit
[H3C] stp instance {kwargs.get('ins1_vlan', '1')} priority {kwargs.get('mst_prio', '4096')}

# 运维监控配置
[H3C] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}
[H3C] snmp-agent
[H3C] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[H3C] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[H3C] snmp-agent trap enable

[H3C] save
<H3C>
        """
        return config
    
    # Cisco核心交换机配置
    @staticmethod
    def _generate_cisco_core_switch_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'CoreSwitch')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 Jan 2024')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 业务VLAN创建
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('server_vlan', '20')}
 name Server_VLAN

# 上联Trunk端口配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 链路聚合配置
interface Port-channel {kwargs.get('static_agg_id', '1')}
 switchport mode trunk
 switchport trunk allowed vlan all
interface range {kwargs.get('static_agg_ports', 'GigabitEthernet0/2-4')}
 channel-group {kwargs.get('static_agg_id', '1')} mode on
 no shutdown

# 下联Access端口配置
interface range {kwargs.get('down_port_range', 'GigabitEthernet0/5-24')}
 switchport mode access
 switchport access vlan {kwargs.get('user_vlan', '10')}
 no shutdown

# 三层网关配置
interface vlan {kwargs.get('user_vlan', '10')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown
interface vlan {kwargs.get('server_vlan', '20')}
 ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
 no shutdown

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# OSPF配置
router ospf {kwargs.get('ospf_proc', '1')}
 router-id {kwargs.get('ospf_rid', '1.1.1.1')}
 network {kwargs.get('mgmt_net', '192.168.100.0')} {kwargs.get('mgmt_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_wild', '0.0.0.255')} area {kwargs.get('area_id', '0')}

# DHCP配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
ip dhcp pool {kwargs.get('user_pool', 'user_pool')}
 network {kwargs.get('user_net', '192.168.10.0')} {kwargs.get('user_mask', '255.255.255.0')}
 default-router {kwargs.get('user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 7 0 0
ip dhcp pool {kwargs.get('server_pool', 'server_pool')}
 network {kwargs.get('server_net', '192.168.20.0')} {kwargs.get('server_mask', '255.255.255.0')}
 default-router {kwargs.get('server_gw', '192.168.20.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 30 0 0

# 安全配置
ip dhcp snooping
ip dhcp snooping vlan {kwargs.get('user_vlan', '10')}
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 ip dhcp snooping trust

# MSTP配置
spanning-tree mode mst
spanning-tree mst configuration
 name {kwargs.get('mst_name', 'Core')}
 revision 1
 instance {kwargs.get('ins1_vlan', '1')} vlan {kwargs.get('ins1_vlan', '10')}
 instance {kwargs.get('ins2_vlan', '2')} vlan {kwargs.get('ins2_vlan', '20')}
 exit
spanning-tree mst {kwargs.get('ins1_vlan', '1')} priority {kwargs.get('mst_prio', '4096')}

# 运维监控配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config
    
    # 华为路由器配置
    @staticmethod
    def _generate_huawei_router_config(**kwargs):
        config = f"""
# 设备基础信息
<Huawei> system-view
[Huawei] sysname {kwargs.get('hostname', 'Router')}
[Huawei] super password cipher {kwargs.get('enable_secret', 'admin123')}
[Huawei] clock timezone BJ add 08:00:00
[Huawei] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 本地登录配置
[Huawei] user-interface console 0
[Huawei-ui-console0] authentication-mode password
[Huawei-ui-console0] set authentication password cipher {kwargs.get('console_password', 'admin123')}
[Huawei-ui-console0] quit

# NTP配置
[Huawei] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}

# 远程登录配置
[Huawei] user-interface vty 0 4
[Huawei-ui-vty0-4] authentication-mode aaa
[Huawei-ui-vty0-4] protocol inbound ssh
[Huawei-ui-vty0-4] quit
[Huawei] aaa
[Huawei-aaa] local-user {kwargs.get('ssh_user', 'admin')} password cipher {kwargs.get('ssh_pwd', 'admin123')}
[Huawei-aaa] local-user {kwargs.get('ssh_user', 'admin')} privilege level 15
[Huawei-aaa] local-user {kwargs.get('ssh_user', 'admin')} service-type ssh
[Huawei-aaa] quit
[Huawei] ssh server enable

# 三层接口配置
[Huawei] interface {kwargs.get('wan_port', 'GigabitEthernet0/0/0')}
[Huawei-{kwargs.get('wan_port', 'GigabitEthernet0/0/0')}] ip address {kwargs.get('wan_ip', '200.200.200.1')} {kwargs.get('wan_mask', '255.255.255.252')}
[Huawei-{kwargs.get('wan_port', 'GigabitEthernet0/0/0')}] quit
[Huawei] interface {kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}
[Huawei-{kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[Huawei-{kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}] quit
[Huawei] interface {kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}
[Huawei-{kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}] ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
[Huawei-{kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}] quit

# NAT配置
[Huawei] acl number 2000
[Huawei-acl-basic-2000] rule permit source {kwargs.get('user_network', '192.168.10.0')} {kwargs.get('user_wildcard', '0.0.0.255')}
[Huawei-acl-basic-2000] rule permit source {kwargs.get('server_network', '192.168.20.0')} {kwargs.get('server_wildcard', '0.0.0.255')}
[Huawei-acl-basic-2000] quit
[Huawei] interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/0/0')}
[Huawei-{kwargs.get('pat_wan_port', 'GigabitEthernet0/0/0')}] nat outbound 2000
[Huawei-{kwargs.get('pat_wan_port', 'GigabitEthernet0/0/0')}] quit

# 端口映射
[Huawei] interface {kwargs.get('map_wan_port', 'GigabitEthernet0/0/0')}
[Huawei-{kwargs.get('map_wan_port', 'GigabitEthernet0/0/0')}] nat server protocol {kwargs.get('protocol', 'tcp')} global current-interface {kwargs.get('map_external_port', '80')} inside {kwargs.get('server_intranet_ip', '192.168.20.10')} {kwargs.get('server_port', '80')}
[Huawei-{kwargs.get('map_wan_port', 'GigabitEthernet0/0/0')}] quit

# 静态路由配置
[Huawei] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '200.200.200.2')}

# OSPF配置
[Huawei] ospf {kwargs.get('ospf_proc', '1')}
[Huawei-ospf-1] router-id {kwargs.get('ospf_rid', '1.1.1.1')}
[Huawei-ospf-1] area {kwargs.get('area_id', '0')}
[Huawei-ospf-1-area-0.0.0.0] network {kwargs.get('ospf_user_network', '192.168.10.0')} {kwargs.get('ospf_user_wildcard', '0.0.0.255')}
[Huawei-ospf-1-area-0.0.0.0] network {kwargs.get('ospf_server_network', '192.168.20.0')} {kwargs.get('ospf_server_wildcard', '0.0.0.255')}
[Huawei-ospf-1-area-0.0.0.0] quit
[Huawei-ospf-1] quit

# DHCP配置
[Huawei] dhcp enable
[Huawei] ip pool {kwargs.get('user_pool_name', 'user_pool')}
[Huawei-ip-pool-user_pool] gateway-list {kwargs.get('dhcp_user_gw', '192.168.10.1')}
[Huawei-ip-pool-user_pool] network {kwargs.get('dhcp_user_network', '192.168.10.0')} mask {kwargs.get('dhcp_user_mask', '255.255.255.0')}
[Huawei-ip-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[Huawei-ip-pool-user_pool] dns-list {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
[Huawei-ip-pool-user_pool] quit
[Huawei] ip pool {kwargs.get('server_pool_name', 'server_pool')}
[Huawei-ip-pool-server_pool] gateway-list {kwargs.get('dhcp_server_gw', '192.168.20.1')}
[Huawei-ip-pool-server_pool] network {kwargs.get('dhcp_server_network', '192.168.20.0')} mask {kwargs.get('dhcp_server_mask', '255.255.255.0')}
[Huawei-ip-pool-server_pool] excluded-ip-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
[Huawei-ip-pool-server_pool] dns-list {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
[Huawei-ip-pool-server_pool] quit
[Huawei] interface {kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}
[Huawei-{kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}] dhcp select global
[Huawei-{kwargs.get('lan_user_port', 'GigabitEthernet0/0/1')}] quit
[Huawei] interface {kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}
[Huawei-{kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}] dhcp select global
[Huawei-{kwargs.get('lan_server_port', 'GigabitEthernet0/0/2')}] quit

# 安全ACL配置
[Huawei] acl number 2001
[Huawei-acl-basic-2001] rule permit source {kwargs.get('manage_network', '192.168.100.0')} {kwargs.get('manage_wildcard', '0.0.0.255')}
[Huawei-acl-basic-2001] quit
[Huawei] user-interface vty 0 4
[Huawei-ui-vty0-4] acl 2001 inbound
[Huawei-ui-vty0-4] quit

# 运维监控配置
[Huawei] snmp-agent
[Huawei] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[Huawei] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server_ip', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[Huawei] snmp-agent trap enable
[Huawei] info-center loghost {kwargs.get('log_server_ip', '192.168.100.254')}

[Huawei] save
<Huawei>
        """
        return config
    
    # 锐捷路由器配置
    @staticmethod
    def _generate_ruijie_router_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'Router')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 January 2024')}

# 本地登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous

# NTP配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}

# 远程登录配置
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 三层接口配置
interface {kwargs.get('wan_port', 'GigabitEthernet0/1')}
 ip address {kwargs.get('wan_ip', '200.200.200.1')} {kwargs.get('wan_mask', '255.255.255.252')}
 no shutdown
interface {kwargs.get('lan_user_port', 'GigabitEthernet0/2')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown
interface {kwargs.get('lan_server_port', 'GigabitEthernet0/3')}
 ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
 no shutdown

# NAT配置
access-list {kwargs.get('nat_acl_name', '100')} permit ip {kwargs.get('user_network', '192.168.10.0')} {kwargs.get('user_wildcard', '0.0.0.255')} any
access-list {kwargs.get('nat_acl_name', '100')} permit ip {kwargs.get('server_network', '192.168.20.0')} {kwargs.get('server_wildcard', '0.0.0.255')} any
interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/1')}
 ip nat outside
 no shutdown
interface {kwargs.get('pat_lan_user_port', 'GigabitEthernet0/2')}
 ip nat inside
 no shutdown
interface {kwargs.get('pat_lan_server_port', 'GigabitEthernet0/3')}
 ip nat inside
 no shutdown
ip nat inside source list {kwargs.get('pat_acl_name', '100')} interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/1')} overload

# 端口映射
ip nat inside source static {kwargs.get('protocol', 'tcp')} {kwargs.get('server_intranet_ip', '192.168.20.10')} {kwargs.get('server_port', '80')} interface {kwargs.get('map_wan_port', 'GigabitEthernet0/1')} {kwargs.get('map_external_port', '80')}

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '200.200.200.2')}

# OSPF配置
router ospf {kwargs.get('ospf_proc', '1')}
 router-id {kwargs.get('ospf_rid', '1.1.1.1')}
 network {kwargs.get('ospf_user_network', '192.168.10.0')} {kwargs.get('ospf_user_wildcard', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('ospf_server_network', '192.168.20.0')} {kwargs.get('ospf_server_wildcard', '0.0.0.255')} area {kwargs.get('area_id', '0')}

# DHCP配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
ip dhcp pool {kwargs.get('user_pool_name', 'user_pool')}
 network {kwargs.get('dhcp_user_network', '192.168.10.0')} {kwargs.get('dhcp_user_mask', '255.255.255.0')}
 default-router {kwargs.get('dhcp_user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
 lease {kwargs.get('lease_day', '7')} 0 0
ip dhcp pool {kwargs.get('server_pool_name', 'server_pool')}
 network {kwargs.get('dhcp_server_network', '192.168.20.0')} {kwargs.get('dhcp_server_mask', '255.255.255.0')}
 default-router {kwargs.get('dhcp_server_gw', '192.168.20.1')}
 dns-server {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
 lease 30 0 0

# 安全ACL配置
ip access-list standard {kwargs.get('manage_acl_name', '10')}
 permit {kwargs.get('manage_network', '192.168.100.0')} {kwargs.get('manage_wildcard', '0.0.0.255')}
 deny any
line vty 0 4
 access-class {kwargs.get('manage_acl_name', '10')} in

# 运维监控配置
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server_ip', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server location {kwargs.get('device_location', 'Server Room')}
snmp-server contact {kwargs.get('admin_contact', 'Admin')}
snmp-server enable traps
logging host {kwargs.get('log_server_ip', '192.168.100.254')}
logging buffered {kwargs.get('log_buffer_size', '51200')}

# 端口镜像配置
monitor session {kwargs.get('mirror_session_id', '1')} source interface {kwargs.get('mirror_src_port', 'GigabitEthernet0/2')} both
monitor session {kwargs.get('mirror_session_id', '1')} destination interface {kwargs.get('mirror_dst_port', 'GigabitEthernet0/4')}

exit
write
        """
        return config
    
    # H3C路由器配置
    @staticmethod
    def _generate_h3c_router_config(**kwargs):
        config = f"""
# 设备基础信息
system-view
[H3C] sysname {kwargs.get('hostname', 'Router')}
[H3C] super password level 3 simple {kwargs.get('enable_secret', 'admin123')}
[H3C] clock timezone BJ add 08:00:00
[H3C] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 本地登录配置
[H3C] user-interface console 0
[H3C-ui-console0] authentication-mode password
[H3C-ui-console0] set authentication password simple {kwargs.get('console_password', 'admin123')}
[H3C-ui-console0] quit

# NTP配置
[H3C] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}

# 远程登录配置
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] authentication-mode scheme
[H3C-ui-vty0-4] protocol inbound ssh
[H3C-ui-vty0-4] quit
[H3C] local-user {kwargs.get('ssh_user', 'admin')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] password simple {kwargs.get('ssh_pwd', 'admin123')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] service-type ssh
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] authorization-attribute user-role network-admin
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] quit
[H3C] ssh server enable

# 三层接口配置
[H3C] interface {kwargs.get('wan_port', 'GigabitEthernet0/0')}
[H3C-{kwargs.get('wan_port', 'GigabitEthernet0/0')}] ip address {kwargs.get('wan_ip', '200.200.200.1')} {kwargs.get('wan_mask', '255.255.255.252')}
[H3C-{kwargs.get('wan_port', 'GigabitEthernet0/0')}] quit
[H3C] interface {kwargs.get('lan_user_port', 'GigabitEthernet0/1')}
[H3C-{kwargs.get('lan_user_port', 'GigabitEthernet0/1')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[H3C-{kwargs.get('lan_user_port', 'GigabitEthernet0/1')}] quit
[H3C] interface {kwargs.get('lan_server_port', 'GigabitEthernet0/2')}
[H3C-{kwargs.get('lan_server_port', 'GigabitEthernet0/2')}] ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
[H3C-{kwargs.get('lan_server_port', 'GigabitEthernet0/2')}] quit

# NAT配置
[H3C] acl number 2000
[H3C-acl-basic-2000] rule permit source {kwargs.get('user_network', '192.168.10.0')} {kwargs.get('user_wildcard', '0.0.0.255')}
[H3C-acl-basic-2000] rule permit source {kwargs.get('server_network', '192.168.20.0')} {kwargs.get('server_wildcard', '0.0.0.255')}
[H3C-acl-basic-2000] quit
[H3C] interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/0')}
[H3C-{kwargs.get('pat_wan_port', 'GigabitEthernet0/0')}] nat outbound 2000
[H3C-{kwargs.get('pat_wan_port', 'GigabitEthernet0/0')}] quit

# 端口映射
[H3C] nat server protocol {kwargs.get('protocol', 'tcp')} global {kwargs.get('map_external_port', '80')} inside {kwargs.get('server_intranet_ip', '192.168.20.10')} {kwargs.get('server_port', '80')}

# 静态路由配置
[H3C] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '200.200.200.2')}

# OSPF配置
[H3C] ospf {kwargs.get('ospf_proc', '1')}
[H3C-ospf-1] router-id {kwargs.get('ospf_rid', '1.1.1.1')}
[H3C-ospf-1] area {kwargs.get('area_id', '0')}
[H3C-ospf-1-area-0.0.0.0] network {kwargs.get('ospf_user_network', '192.168.10.0')} {kwargs.get('ospf_user_wildcard', '0.0.0.255')}
[H3C-ospf-1-area-0.0.0.0] network {kwargs.get('ospf_server_network', '192.168.20.0')} {kwargs.get('ospf_server_wildcard', '0.0.0.255')}
[H3C-ospf-1-area-0.0.0.0] quit
[H3C-ospf-1] quit

# DHCP配置
[H3C] dhcp enable
[H3C] dhcp server ip-pool {kwargs.get('user_pool_name', 'user_pool')}
[H3C-dhcp-pool-user_pool] network {kwargs.get('dhcp_user_network', '192.168.10.0')} mask {kwargs.get('dhcp_user_mask', '255.255.255.0')}
[H3C-dhcp-pool-user_pool] gateway-list {kwargs.get('dhcp_user_gw', '192.168.10.1')}
[H3C-dhcp-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[H3C-dhcp-pool-user_pool] dns-list {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
[H3C-dhcp-pool-user_pool] quit
[H3C] dhcp server ip-pool {kwargs.get('server_pool_name', 'server_pool')}
[H3C-dhcp-pool-server_pool] network {kwargs.get('dhcp_server_network', '192.168.20.0')} mask {kwargs.get('dhcp_server_mask', '255.255.255.0')}
[H3C-dhcp-pool-server_pool] gateway-list {kwargs.get('dhcp_server_gw', '192.168.20.1')}
[H3C-dhcp-pool-server_pool] excluded-ip-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
[H3C-dhcp-pool-server_pool] dns-list {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
[H3C-dhcp-pool-server_pool] quit

# 安全ACL配置
[H3C] acl number 2001
[H3C-acl-basic-2001] rule permit source {kwargs.get('manage_network', '192.168.100.0')} {kwargs.get('manage_wildcard', '0.0.0.255')}
[H3C-acl-basic-2001] quit
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] acl 2001 inbound
[H3C-ui-vty0-4] quit

# 运维监控配置
[H3C] snmp-agent
[H3C] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[H3C] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server_ip', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[H3C] snmp-agent trap enable
[H3C] info-center loghost {kwargs.get('log_server_ip', '192.168.100.254')}

[H3C] save
<H3C>
        """
        return config
    
    # Cisco路由器配置
    @staticmethod
    def _generate_cisco_router_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'Router')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 Jan 2024')}

# 本地登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous

# NTP配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}

# 远程登录配置
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# 三层接口配置
interface {kwargs.get('wan_port', 'GigabitEthernet0/0')}
 ip address {kwargs.get('wan_ip', '200.200.200.1')} {kwargs.get('wan_mask', '255.255.255.252')}
 no shutdown
interface {kwargs.get('lan_user_port', 'GigabitEthernet0/1')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown
interface {kwargs.get('lan_server_port', 'GigabitEthernet0/2')}
 ip address {kwargs.get('server_gw', '192.168.20.1')} {kwargs.get('server_mask', '255.255.255.0')}
 no shutdown

# NAT配置
access-list {kwargs.get('nat_acl_name', '100')} permit ip {kwargs.get('user_network', '192.168.10.0')} {kwargs.get('user_wildcard', '0.0.0.255')} any
access-list {kwargs.get('nat_acl_name', '100')} permit ip {kwargs.get('server_network', '192.168.20.0')} {kwargs.get('server_wildcard', '0.0.0.255')} any
interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/0')}
 ip nat outside
 no shutdown
interface {kwargs.get('pat_lan_user_port', 'GigabitEthernet0/1')}
 ip nat inside
 no shutdown
interface {kwargs.get('pat_lan_server_port', 'GigabitEthernet0/2')}
 ip nat inside
 no shutdown
ip nat inside source list {kwargs.get('pat_acl_name', '100')} interface {kwargs.get('pat_wan_port', 'GigabitEthernet0/0')} overload

# 端口映射
ip nat inside source static {kwargs.get('protocol', 'tcp')} {kwargs.get('server_intranet_ip', '192.168.20.10')} {kwargs.get('server_port', '80')} interface {kwargs.get('map_wan_port', 'GigabitEthernet0/0')} {kwargs.get('map_external_port', '80')}

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '200.200.200.2')}

# OSPF配置
router ospf {kwargs.get('ospf_proc', '1')}
 router-id {kwargs.get('ospf_rid', '1.1.1.1')}
 network {kwargs.get('ospf_user_network', '192.168.10.0')} {kwargs.get('ospf_user_wildcard', '0.0.0.255')} area {kwargs.get('area_id', '0')}
 network {kwargs.get('ospf_server_network', '192.168.20.0')} {kwargs.get('ospf_server_wildcard', '0.0.0.255')} area {kwargs.get('area_id', '0')}

# DHCP配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('server_ex_start', '192.168.20.1')} {kwargs.get('server_ex_end', '192.168.20.10')}
ip dhcp pool {kwargs.get('user_pool_name', 'user_pool')}
 network {kwargs.get('dhcp_user_network', '192.168.10.0')} {kwargs.get('dhcp_user_mask', '255.255.255.0')}
 default-router {kwargs.get('dhcp_user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
 lease {kwargs.get('lease_day', '7')} 0 0
ip dhcp pool {kwargs.get('server_pool_name', 'server_pool')}
 network {kwargs.get('dhcp_server_network', '192.168.20.0')} {kwargs.get('dhcp_server_mask', '255.255.255.0')}
 default-router {kwargs.get('dhcp_server_gw', '192.168.20.1')}
 dns-server {kwargs.get('dns_primary', '8.8.8.8')} {kwargs.get('dns_standby', '114.114.114.114')}
 lease 30 0 0

# 安全ACL配置
ip access-list standard {kwargs.get('manage_acl_name', '10')}
 permit {kwargs.get('manage_network', '192.168.100.0')} {kwargs.get('manage_wildcard', '0.0.0.255')}
 deny any
line vty 0 4
 access-class {kwargs.get('manage_acl_name', '10')} in

# 运维监控配置
snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server_ip', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server location {kwargs.get('device_location', 'Server Room')}
snmp-server contact {kwargs.get('admin_contact', 'Admin')}
snmp-server enable traps
logging host {kwargs.get('log_server_ip', '192.168.100.254')}
logging buffered {kwargs.get('log_buffer_size', '51200')}

# 端口镜像配置
monitor session {kwargs.get('mirror_session_id', '1')} source interface {kwargs.get('mirror_src_port', 'GigabitEthernet0/1')} both
monitor session {kwargs.get('mirror_session_id', '1')} destination interface {kwargs.get('mirror_dst_port', 'GigabitEthernet0/3')}

exit
write
        """
        return config
    
    # 华为AC配置
    @staticmethod
    def _generate_huawei_ac_config(**kwargs):
        config = f"""
# 设备基础信息
<HUAWEI> system-view
[HUAWEI] sysname {kwargs.get('hostname', 'AC')}
[HUAWEI] super password cipher {kwargs.get('enable_secret', 'admin123')}
[HUAWEI] clock timezone BJ add 08:00:00
[HUAWEI] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 本地登录配置
[HUAWEI] user-interface console 0
[HUAWEI-ui-console0] authentication-mode password
[HUAWEI-ui-console0] set authentication password cipher {kwargs.get('console_password', 'admin123')}
[HUAWEI-ui-console0] quit

# NTP配置
[HUAWEI] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}

# 管理VLAN配置
[HUAWEI] vlan {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[HUAWEI-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[HUAWEI] interface vlanif {kwargs.get('mgmt_vlan', '100')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[HUAWEI] user-interface vty 0 4
[HUAWEI-ui-vty0-4] authentication-mode aaa
[HUAWEI-ui-vty0-4] protocol inbound ssh
[HUAWEI-ui-vty0-4] quit
[HUAWEI] aaa
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} password cipher {kwargs.get('ssh_pwd', 'admin123')}
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} privilege level 15
[HUAWEI-aaa] local-user {kwargs.get('ssh_user', 'admin')} service-type ssh
[HUAWEI-aaa] quit
[HUAWEI] ssh server enable

# WLAN业务配置
[HUAWEI] vlan batch {kwargs.get('user_vlan', '10')} {kwargs.get('ap_mgmt_vlan', '50')}

# AP管理VLAN配置
[HUAWEI] interface vlanif {kwargs.get('ap_mgmt_vlan', '50')}
[HUAWEI-Vlanif{kwargs.get('ap_mgmt_vlan', '50')}] ip address {kwargs.get('ap_mgmt_ip', '192.168.50.1')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('ap_mgmt_vlan', '50')}] quit

# 无线SSID配置
[HUAWEI] wlan
[HUAWEI-wlan-view] ssid-profile name {kwargs.get('ssid_name', 'SSID')}
[HUAWEI-wlan-ssid-prof-SSID] ssid {kwargs.get('ssid_name', 'SSID')}
[HUAWEI-wlan-ssid-prof-SSID] quit

# 无线安全配置
[HUAWEI-wlan-view] security-profile name {kwargs.get('security_mode', 'WPA2-PSK')}
[HUAWEI-wlan-sec-prof-WPA2-PSK] security wpa psk pass-phrase {kwargs.get('wpa_key', 'password123')} aes
[HUAWEI-wlan-sec-prof-WPA2-PSK] quit

# 无线VAP模板配置
[HUAWEI-wlan-view] vap-profile name {kwargs.get('vap_name', 'VAP')}
[HUAWEI-wlan-vap-prof-VAP] ssid-profile {kwargs.get('ssid_name', 'SSID')}
[HUAWEI-wlan-vap-prof-VAP] security-profile {kwargs.get('security_mode', 'WPA2-PSK')}
[HUAWEI-wlan-vap-prof-VAP] service-vlan vlan-id {kwargs.get('ssid_vlan', '10')}
[HUAWEI-wlan-vap-prof-VAP] quit

# 无线AP组配置
[HUAWEI-wlan-view] ap-group name {kwargs.get('ap_group_name', 'AP-Group')}
[HUAWEI-wlan-ap-group-AP-Group] vap-profile {kwargs.get('vap_name', 'VAP')} wlan 1 radio all
[HUAWEI-wlan-ap-group-AP-Group] quit

# 无线射频配置
[HUAWEI-wlan-view] radio-profile name {kwargs.get('radio_band', '2.4GHz')}
[HUAWEI-wlan-radio-prof-2.4GHz] channel {kwargs.get('channel', '1')}
[HUAWEI-wlan-radio-prof-2.4GHz] power {kwargs.get('power_level', '1')}
[HUAWEI-wlan-radio-prof-2.4GHz] quit
[HUAWEI-wlan-view] quit

# 端口与上联配置
[HUAWEI] interface {kwargs.get('up_port', 'GigabitEthernet0/0/1')}
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port link-type trunk
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] port trunk allow-pass vlan all
[HUAWEI-{kwargs.get('up_port', 'GigabitEthernet0/0/1')}] quit

# 下联AP接入端口配置
[HUAWEI] interface range {kwargs.get('ap_port_range', 'GigabitEthernet0/0/2 to GigabitEthernet0/0/24')}
[HUAWEI-if-range] port link-type trunk
[HUAWEI-if-range] port trunk allow-pass vlan {kwargs.get('user_vlan', '10')},{kwargs.get('ap_mgmt_vlan', '50')}
[HUAWEI-if-range] quit

# 三层网关与路由配置
[HUAWEI] interface vlanif {kwargs.get('user_vlan', '10')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] quit

# 静态路由配置
[HUAWEI] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# DHCP服务配置
[HUAWEI] dhcp enable
[HUAWEI] ip pool {kwargs.get('user_pool', 'user_pool')}
[HUAWEI-ip-pool-user_pool] gateway-list {kwargs.get('user_gw', '192.168.10.1')}
[HUAWEI-ip-pool-user_pool] network {kwargs.get('user_gw', '192.168.10.0')} mask {kwargs.get('user_mask', '255.255.255.0')}
[HUAWEI-ip-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[HUAWEI-ip-pool-user_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[HUAWEI-ip-pool-user_pool] quit
[HUAWEI] ip pool {kwargs.get('ap_pool', 'ap_pool')}
[HUAWEI-ip-pool-ap_pool] gateway-list {kwargs.get('ap_mgmt_ip', '192.168.50.1')}
[HUAWEI-ip-pool-ap_pool] network {kwargs.get('ap_mgmt_ip', '192.168.50.0')} mask {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
[HUAWEI-ip-pool-ap_pool] excluded-ip-address {kwargs.get('ap_ex_start', '192.168.50.1')} {kwargs.get('ap_ex_end', '192.168.50.10')}
[HUAWEI-ip-pool-ap_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[HUAWEI-ip-pool-ap_pool] quit
[HUAWEI] interface vlanif {kwargs.get('user_vlan', '10')}
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] dhcp select global
[HUAWEI-Vlanif{kwargs.get('user_vlan', '10')}] quit
[HUAWEI] interface vlanif {kwargs.get('ap_mgmt_vlan', '50')}
[HUAWEI-Vlanif{kwargs.get('ap_mgmt_vlan', '50')}] dhcp select global
[HUAWEI-Vlanif{kwargs.get('ap_mgmt_vlan', '50')}] quit

# 安全与运维监控配置
[HUAWEI] acl number 2000
[HUAWEI-acl-basic-2000] rule permit source {kwargs.get('manage_net', '192.168.100.0')} {kwargs.get('manage_wild', '0.0.0.255')}
[HUAWEI-acl-basic-2000] quit
[HUAWEI] user-interface vty 0 4
[HUAWEI-ui-vty0-4] acl 2000 inbound
[HUAWEI-ui-vty0-4] quit

[HUAWEI] snmp-agent
[HUAWEI] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[HUAWEI] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[HUAWEI] snmp-agent trap enable

[HUAWEI] save
<HUAWEI>
        """
        return config
    
    # 锐捷AC配置
    @staticmethod
    def _generate_ruijie_ac_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'AC')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 January 2024')}

# 本地登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous

# NTP配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# WLAN业务配置
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('ap_mgmt_vlan', '50')}
 name AP_Management

# AP管理VLAN配置
interface vlan {kwargs.get('ap_mgmt_vlan', '50')}
 ip address {kwargs.get('ap_mgmt_ip', '192.168.50.1')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
 no shutdown

# 无线SSID配置
wlan ssid {kwargs.get('ssid_name', 'SSID')}
 wlan-id {kwargs.get('wlan_id', '1')}
 vlan {kwargs.get('ssid_vlan', '10')}
 security wpa psk set-key ascii 0 {kwargs.get('wpa_key', 'password123')}
 security wpa wpa2
 exit

# 无线VAP模板配置
wlan vap-template {kwargs.get('vap_name', 'VAP')}
 ssid {kwargs.get('ssid_name', 'SSID')}
 bind wlan-id {kwargs.get('wlan_id', '1')}
 exit

# 无线AP组配置
wlan ap-group {kwargs.get('ap_group_name', 'AP-Group')}
 vap-template {kwargs.get('vap_name', 'VAP')} wlan {kwargs.get('wlan_id', '1')}
 exit

# 无线射频配置
wlan radio-2g-profile default
 channel {kwargs.get('channel', '1')}
 power-level {kwargs.get('power_level', '1')}
 exit

wlan radio-5g-profile default
 channel {kwargs.get('channel', '36')}
 power-level {kwargs.get('power_level', '1')}
 exit

# 端口与上联配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 下联AP接入端口配置
interface range {kwargs.get('ap_port_range', 'GigabitEthernet0/2-24')}
 switchport mode trunk
 switchport trunk allowed vlan {kwargs.get('user_vlan', '10')},{kwargs.get('ap_mgmt_vlan', '50')}
 no shutdown

# 三层网关与路由配置
interface vlan {kwargs.get('user_vlan', '10')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# DHCP服务配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('ap_ex_start', '192.168.50.1')} {kwargs.get('ap_ex_end', '192.168.50.10')}
ip dhcp pool {kwargs.get('user_pool', 'user_pool')}
 network {kwargs.get('user_gw', '192.168.10.0')} {kwargs.get('user_mask', '255.255.255.0')}
 default-router {kwargs.get('user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 7 0 0
ip dhcp pool {kwargs.get('ap_pool', 'ap_pool')}
 network {kwargs.get('ap_mgmt_ip', '192.168.50.0')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
 default-router {kwargs.get('ap_mgmt_ip', '192.168.50.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 30 0 0

# 安全与运维监控配置
ip access-list standard 10
 permit {kwargs.get('manage_net', '192.168.100.0')} {kwargs.get('manage_wild', '0.0.0.255')}
 deny any
line vty 0 4
 access-class 10 in

snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config
    
    # H3C AC配置
    @staticmethod
    def _generate_h3c_ac_config(**kwargs):
        config = f"""
# 设备基础信息
system-view
[H3C] sysname {kwargs.get('hostname', 'AC')}
[H3C] super password level 3 simple {kwargs.get('enable_secret', 'admin123')}
[H3C] clock timezone BJ add 08:00:00
[H3C] clock datetime {kwargs.get('system_time', '2024-01-01 00:00:00')}

# 本地登录配置
[H3C] user-interface console 0
[H3C-ui-console0] authentication-mode password
[H3C-ui-console0] set authentication password simple {kwargs.get('console_password', 'admin123')}
[H3C-ui-console0] quit

# NTP配置
[H3C] ntp-service unicast-server {kwargs.get('ntp_server', '123.123.123.123')}

# 管理VLAN配置
[H3C] vlan {kwargs.get('mgmt_vlan', '100')}
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] name Management
[H3C-vlan{kwargs.get('mgmt_vlan', '100')}] quit
[H3C] interface vlan-interface {kwargs.get('mgmt_vlan', '100')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('mgmt_vlan', '100')}] quit

# 远程登录配置
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] authentication-mode scheme
[H3C-ui-vty0-4] protocol inbound ssh
[H3C-ui-vty0-4] quit
[H3C] local-user {kwargs.get('ssh_user', 'admin')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] password simple {kwargs.get('ssh_pwd', 'admin123')}
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] service-type ssh
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] authorization-attribute user-role network-admin
[H3C-luser-manage-{kwargs.get('ssh_user', 'admin')}] quit
[H3C] ssh server enable

# WLAN业务配置
[H3C] vlan {kwargs.get('user_vlan', '10')}
[H3C-vlan{kwargs.get('user_vlan', '10')}] name User_VLAN
[H3C-vlan{kwargs.get('user_vlan', '10')}] quit
[H3C] vlan {kwargs.get('ap_mgmt_vlan', '50')}
[H3C-vlan{kwargs.get('ap_mgmt_vlan', '50')}] name AP_Management
[H3C-vlan{kwargs.get('ap_mgmt_vlan', '50')}] quit

# AP管理VLAN配置
[H3C] interface vlan-interface {kwargs.get('ap_mgmt_vlan', '50')}
[H3C-Vlan-interface{kwargs.get('ap_mgmt_vlan', '50')}] ip address {kwargs.get('ap_mgmt_ip', '192.168.50.1')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('ap_mgmt_vlan', '50')}] quit

# 无线SSID配置
[H3C] wlan service-template {kwargs.get('wlan_id', '1')}
[H3C-wlan-st-1] ssid {kwargs.get('ssid_name', 'SSID')}
[H3C-wlan-st-1] vlan {kwargs.get('ssid_vlan', '10')}
[H3C-wlan-st-1] authentication-method open-system
[H3C-wlan-st-1] encryption-method wpa2-psk aes pass-phrase {kwargs.get('wpa_key', 'password123')}
[H3C-wlan-st-1] service-template enable
[H3C-wlan-st-1] quit

# 无线AP组配置
[H3C] wlan ap-group {kwargs.get('ap_group_name', 'AP-Group')}
[H3C-wlan-ap-group-AP-Group] service-template {kwargs.get('wlan_id', '1')} interface-group 1
[H3C-wlan-ap-group-AP-Group] quit

# 无线射频配置
[H3C] wlan radio-policy {kwargs.get('radio_band', '2.4GHz')}
[H3C-wlan-rp-2.4GHz] channel {kwargs.get('channel', '1')}
[H3C-wlan-rp-2.4GHz] power {kwargs.get('power_level', '1')}
[H3C-wlan-rp-2.4GHz] quit

# 端口与上联配置
[H3C] interface {kwargs.get('up_port', 'GigabitEthernet1/0/1')}
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port link-type trunk
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] port trunk permit vlan all
[H3C-{kwargs.get('up_port', 'GigabitEthernet1/0/1')}] quit

# 下联AP接入端口配置
[H3C] interface range {kwargs.get('ap_port_range', 'GigabitEthernet1/0/2 to GigabitEthernet1/0/24')}
[H3C-if-range] port link-type trunk
[H3C-if-range] port trunk permit vlan {kwargs.get('user_vlan', '10')},{kwargs.get('ap_mgmt_vlan', '50')}
[H3C-if-range] quit

# 三层网关与路由配置
[H3C] interface vlan-interface {kwargs.get('user_vlan', '10')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
[H3C-Vlan-interface{kwargs.get('user_vlan', '10')}] quit

# 静态路由配置
[H3C] ip route-static {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# DHCP服务配置
[H3C] dhcp enable
[H3C] dhcp server ip-pool {kwargs.get('user_pool', 'user_pool')}
[H3C-dhcp-pool-user_pool] network {kwargs.get('user_gw', '192.168.10.0')} mask {kwargs.get('user_mask', '255.255.255.0')}
[H3C-dhcp-pool-user_pool] gateway-list {kwargs.get('user_gw', '192.168.10.1')}
[H3C-dhcp-pool-user_pool] excluded-ip-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
[H3C-dhcp-pool-user_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[H3C-dhcp-pool-user_pool] quit
[H3C] dhcp server ip-pool {kwargs.get('ap_pool', 'ap_pool')}
[H3C-dhcp-pool-ap_pool] network {kwargs.get('ap_mgmt_ip', '192.168.50.0')} mask {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
[H3C-dhcp-pool-ap_pool] gateway-list {kwargs.get('ap_mgmt_ip', '192.168.50.1')}
[H3C-dhcp-pool-ap_pool] excluded-ip-address {kwargs.get('ap_ex_start', '192.168.50.1')} {kwargs.get('ap_ex_end', '192.168.50.10')}
[H3C-dhcp-pool-ap_pool] dns-list {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
[H3C-dhcp-pool-ap_pool] quit

# 安全与运维监控配置
[H3C] acl number 2000
[H3C-acl-basic-2000] rule permit source {kwargs.get('manage_net', '192.168.100.0')} {kwargs.get('manage_wild', '0.0.0.255')}
[H3C-acl-basic-2000] quit
[H3C] user-interface vty 0 4
[H3C-ui-vty0-4] acl 2000 inbound
[H3C-ui-vty0-4] quit

[H3C] snmp-agent
[H3C] snmp-agent community read {kwargs.get('snmp_ro_community', 'public')}
[H3C] snmp-agent target-host trap address udp-domain {kwargs.get('trap_server', '192.168.100.254')} params securityname {kwargs.get('trap_community', 'public')}
[H3C] snmp-agent trap enable

[H3C] save
<H3C>
        """
        return config
    
    # Cisco AC配置
    @staticmethod
    def _generate_cisco_ac_config(**kwargs):
        config = f"""
# 设备基础信息
enable
configure terminal
hostname {kwargs.get('hostname', 'AC')}
enable secret {kwargs.get('enable_secret', 'admin123')}
clock timezone BJ +8
clock set {kwargs.get('system_time', '00:00:00 1 Jan 2024')}

# 本地登录配置
line console 0
 password {kwargs.get('console_password', 'admin123')}
 login
 exec-timeout 10 0
 logging synchronous

# NTP配置
ntp server {kwargs.get('ntp_server', '123.123.123.123')}

# 管理VLAN配置
vlan {kwargs.get('mgmt_vlan', '100')}
 name Management
interface vlan {kwargs.get('mgmt_vlan', '100')}
 ip address {kwargs.get('mgmt_ip', '192.168.100.1')} {kwargs.get('mgmt_mask', '255.255.255.0')}
 no shutdown

# 远程登录配置
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
username {kwargs.get('ssh_user', 'admin')} privilege 15 password {kwargs.get('ssh_pwd', 'admin123')}
ip ssh version 2

# WLAN业务配置
vlan {kwargs.get('user_vlan', '10')}
 name User_VLAN
vlan {kwargs.get('ap_mgmt_vlan', '50')}
 name AP_Management

# AP管理VLAN配置
interface vlan {kwargs.get('ap_mgmt_vlan', '50')}
 ip address {kwargs.get('ap_mgmt_ip', '192.168.50.1')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
 no shutdown

# 无线SSID配置
wlan {kwargs.get('wlan_id', '1')}
 ssid {kwargs.get('ssid_name', 'SSID')}
 vlan {kwargs.get('ssid_vlan', '10')}
 security wpa psk set-key ascii 0 {kwargs.get('wpa_key', 'password123')}
 security wpa wpa2
 exit

# 无线VAP模板配置
ap group {kwargs.get('ap_group_name', 'AP-Group')}
 wlan {kwargs.get('wlan_id', '1')} vlan {kwargs.get('ssid_vlan', '10')}
 exit

# 无线射频配置
ap dot11 {kwargs.get('radio_band', '24ghz')}
 channel {kwargs.get('channel', '1')}
 power local {kwargs.get('power_level', '1')}
 exit

# 端口与上联配置
interface {kwargs.get('up_port', 'GigabitEthernet0/1')}
 switchport mode trunk
 switchport trunk allowed vlan all
 no shutdown

# 下联AP接入端口配置
interface range {kwargs.get('ap_port_range', 'GigabitEthernet0/2-24')}
 switchport mode trunk
 switchport trunk allowed vlan {kwargs.get('user_vlan', '10')},{kwargs.get('ap_mgmt_vlan', '50')}
 no shutdown

# 三层网关与路由配置
interface vlan {kwargs.get('user_vlan', '10')}
 ip address {kwargs.get('user_gw', '192.168.10.1')} {kwargs.get('user_mask', '255.255.255.0')}
 no shutdown

# 静态路由配置
ip route {kwargs.get('dst_net1', '0.0.0.0')} {kwargs.get('dst_mask1', '0.0.0.0')} {kwargs.get('nh1', '192.168.100.254')}

# DHCP服务配置
service dhcp
ip dhcp excluded-address {kwargs.get('user_ex_start', '192.168.10.1')} {kwargs.get('user_ex_end', '192.168.10.10')}
ip dhcp excluded-address {kwargs.get('ap_ex_start', '192.168.50.1')} {kwargs.get('ap_ex_end', '192.168.50.10')}
ip dhcp pool {kwargs.get('user_pool', 'user_pool')}
 network {kwargs.get('user_gw', '192.168.10.0')} {kwargs.get('user_mask', '255.255.255.0')}
 default-router {kwargs.get('user_gw', '192.168.10.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 7 0 0
ip dhcp pool {kwargs.get('ap_pool', 'ap_pool')}
 network {kwargs.get('ap_mgmt_ip', '192.168.50.0')} {kwargs.get('ap_mgmt_mask', '255.255.255.0')}
 default-router {kwargs.get('ap_mgmt_ip', '192.168.50.1')}
 dns-server {kwargs.get('dns1', '8.8.8.8')} {kwargs.get('dns2', '114.114.114.114')}
 lease 30 0 0

# 安全与运维监控配置
ip access-list standard 10
 permit {kwargs.get('manage_net', '192.168.100.0')} {kwargs.get('manage_wild', '0.0.0.255')}
 deny any
line vty 0 4
 access-class 10 in

snmp-server community {kwargs.get('snmp_ro_community', 'public')} ro
snmp-server host {kwargs.get('trap_server', '192.168.100.254')} traps version 2c {kwargs.get('trap_community', 'public')}
snmp-server enable traps

exit
write
        """
        return config