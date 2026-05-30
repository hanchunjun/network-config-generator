#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思科设备 CLI 命令生成模板

封装所有设备类型的 Cisco IOS 特有 CLI 语法。
"""

from typing import List


class CiscoCLITemplate:
    VENDOR = "cisco"

    @staticmethod
    def set_hostname(name: str) -> str:
        return f"hostname {name}"

    @staticmethod
    def set_enable_password(pwd: str) -> str:
        return f"enable secret {pwd}"

    @staticmethod
    def set_system_time(time_str: str) -> str:
        return f"clock set {time_str}"

    @staticmethod
    def exit_context() -> str:
        return "exit"

    # ==================================================================
    # Console
    # ==================================================================
    @staticmethod
    def line_console_0() -> str:
        return "line console 0"

    @staticmethod
    def console_password(pwd: str) -> str:
        return f"password {pwd}"

    @staticmethod
    def console_login() -> str:
        return "login"

    @staticmethod
    def console_login_local() -> str:
        return "login local"

    @staticmethod
    def username_privilege_secret(user: str, level: int, pwd: str) -> str:
        return f"username {user} privilege {level} secret {pwd}"

    @staticmethod
    def line_vty(start: int = 0, end: int = 4) -> str:
        return f"line vty {start} {end}"

    @staticmethod
    def vty_password(pwd: str) -> str:
        return f"password {pwd}"

    @staticmethod
    def transport_input_ssh() -> str:
        return "transport input ssh"

    @staticmethod
    def transport_input_telnet() -> str:
        return "transport input telnet"

    @staticmethod
    def crypto_key_generate_rsa(modulus: int = 1024) -> str:
        return f"crypto key generate rsa modulus {modulus}"

    @staticmethod
    def ip_domain_name(domain: str = "example.com") -> str:
        return f"ip domain-name {domain}"

    @staticmethod
    def no_ip_domain_lookup() -> str:
        return "no ip domain-lookup"

    # ==================================================================
    # VLAN
    # ==================================================================
    @staticmethod
    def create_vlan(vid: int, name: str = "") -> List[str]:
        lines = [f"vlan {vid}"]
        if name:
            lines.append(f" name {name}")
        lines.append("exit")
        return lines

    @staticmethod
    def interface_vlan(vid: int) -> str:
        return f"interface vlan {vid}"

    @staticmethod
    def ip_address(ip: str, mask: str) -> str:
        return f"ip address {ip} {mask}"

    @staticmethod
    def ip_route_default(gateway: str) -> str:
        return f"ip default-gateway {gateway}"

    @staticmethod
    def ip_route_static(dst: str, mask: str, gw: str) -> str:
        return f"ip route {dst} {mask} {gw}"

    # ==================================================================
    # 端口 —— 思科特色：interface GigabitEthernet0/1
    #   批量：interface range GigabitEthernet0/1 - 4
    # ==================================================================
    @staticmethod
    def interface_single(iface_type: str, *path: str) -> str:
        return f"interface {iface_type}{''.join(path)}"

    @staticmethod
    def interface_range_cisco(iface_type: str, prefix: str, start: int, end: int) -> str:
        if start == end:
            return f"interface {iface_type}{prefix}{start}"
        return f"interface range {iface_type}{prefix}{start} - {end}"

    @staticmethod
    def switchport_mode_access() -> str:
        return "switchport mode access"

    @staticmethod
    def switchport_mode_trunk() -> str:
        return "switchport mode trunk"

    @staticmethod
    def switchport_access_vlan(vid: int) -> str:
        return f"switchport access vlan {vid}"

    @staticmethod
    def switchport_trunk_allowed_vlan(vlans: str) -> str:
        return f"switchport trunk allowed vlan {vlans}"

    @staticmethod
    def switchport_trunk_encapsulation_dot1q() -> str:
        return "switchport trunk encapsulation dot1q"

    # ==================================================================
    # 聚合口 —— Port-Channel
    # ==================================================================
    @staticmethod
    def interface_port_channel(po_id: int) -> str:
        return f"interface Port-channel{po_id}"

    @staticmethod
    def channel_group(po_id: int, mode: str = "active") -> str:
        return f"channel-group {po_id} mode {mode}"

    @staticmethod
    def port_channel_load_balance(algo: str) -> str:
        return f"port-channel load-balance {algo}"

    # ==================================================================
    # 生成树
    # ==================================================================
    @staticmethod
    def spanning_tree_mode(mode: str) -> str:
        mapping = {"STP": "pvst", "RSTP": "rapid-pvst", "MSTP": "mst"}
        return f"spanning-tree mode {mapping.get(mode, 'rapid-pvst')}"

    @staticmethod
    def spanning_tree_priority(prio: int) -> str:
        return f"spanning-tree vlan 1 priority {prio}"

    @staticmethod
    def spanning_tree_portfast() -> str:
        return "spanning-tree portfast"

    @staticmethod
    def spanning_tree_bpduguard_enable() -> str:
        return "spanning-tree bpduguard enable"

    @staticmethod
    def spanning_tree_mst_config() -> List[str]:
        return ["spanning-tree mst configuration", "exit"]

    # ==================================================================
    # ACL
    # ==================================================================
    @staticmethod
    def acl_number_extended(num: int) -> str:
        return f"ip access-list extended ACL_{num}"

    @staticmethod
    def acl_rule_permit_ip(src: str, dst: str) -> str:
        return f" permit ip {src} {dst}"

    @staticmethod
    def acl_rule_deny_ip(src: str, dst: str) -> str:
        return f" deny ip {src} {dst}"

    @staticmethod
    def acl_rule_permit_tcp(src: str, dst: str, port: str = "") -> str:
        rule = f" permit tcp {src} {dst}"
        if port:
            rule += f" eq {port}"
        return rule

    @staticmethod
    def acl_rule_deny_tcp(src: str, dst: str, port: str = "") -> str:
        rule = f" deny tcp {src} {dst}"
        if port:
            rule += f" eq {port}"
        return rule

    @staticmethod
    def acl_apply_to_interface(iface: str, acl_num: int, direction: str) -> List[str]:
        dir_map = {"入方向": "in", "出方向": "out"}
        d = dir_map.get(direction, "in")
        return [
            f"interface {iface}",
            f" ip access-group ACL_{acl_num} {d}",
            "exit"
        ]

    # ==================================================================
    # DHCP Snooping
    # ==================================================================
    @staticmethod
    def ip_dhcp_snooping() -> str:
        return "ip dhcp snooping"

    @staticmethod
    def ip_dhcp_snooping_trust() -> str:
        return "ip dhcp snooping trust"

    @staticmethod
    def ip_dhcp_snooping_verify_mac() -> str:
        return "ip dhcp snooping verify mac-address"

    @staticmethod
    def ip_dhcp_snooping_vlan(vid: int) -> str:
        return f"ip dhcp snooping vlan {vid}"

    # ==================================================================
    # 防环
    # ==================================================================
    @staticmethod
    def errdisable_recovery_cause(sec: int = 300) -> str:
        return f"errdisable recovery cause all {sec}"

    @staticmethod
    def spanning_tree_bpdufilter_enable() -> str:
        return "spanning-tree bpdufilter enable"

    # ==================================================================
    # 管理地址
    # ==================================================================
    @staticmethod
    def management_interface_vlan(vid: int, ip: str, mask: str) -> List[str]:
        return [
            f"interface vlan {vid}",
            f" ip address {ip} {mask}",
            "exit"
        ]