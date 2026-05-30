#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锐捷设备 CLI 命令生成模板

提供 ~50 个静态方法，封装所有设备类型（接入/核心/路由/AC）的锐捷特有 CLI 语法。
"""

from typing import List


class RuijieCLITemplate:
    VENDOR = "ruijie"

    # ==================================================================
    # 基础信息
    # ==================================================================
    @staticmethod
    def set_hostname(name: str) -> str:
        return f"hostname {name}"

    @staticmethod
    def set_enable_password(pwd: str) -> str:
        return f"enable password {pwd}"

    @staticmethod
    def set_enable_secret(pwd: str) -> str:
        return f"enable secret 0 {pwd}"

    @staticmethod
    def set_system_time(time_str: str) -> str:
        return f"clock set {time_str}"

    @staticmethod
    def exit_context() -> str:
        return "exit"

    # ==================================================================
    # Console 配置
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
        return f"username {user} privilege {level} secret 0 {pwd}"

    @staticmethod
    def line_vty(start: int = 0, end: int = 4) -> str:
        return f"line vty {start} {end}"

    @staticmethod
    def line_vty_password(pwd: str) -> str:
        return f"password {pwd}"

    @staticmethod
    def transport_input_ssh() -> str:
        return "transport input ssh"

    @staticmethod
    def transport_input_telnet() -> str:
        return "transport input telnet"

    @staticmethod
    def enable_service_ssh() -> str:
        return "enable service ssh-server"

    @staticmethod
    def enable_service_telnet() -> str:
        return "enable service telnet-server"

    @staticmethod
    def crypto_key_generate_rsa(modulus: int = 1024) -> str:
        return f"crypto key generate rsa modulus {modulus}"

    @staticmethod
    def ip_domain_name(domain: str = "example.com") -> str:
        return f"ip domain-name {domain}"

    @staticmethod
    def ip_ssh_version(ver: int = 2) -> str:
        return f"ip ssh version {ver}"

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
    def create_vlan_range(start: int, end: int) -> List[str]:
        return [RuijieCLITemplate.create_vlan(v) for v in range(start, end + 1)]

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
    # 端口 —— 锐捷特色：interface range G 0/1 - 0/4 或 interface G 0/1
    # ==================================================================
    @staticmethod
    def interface_single(iface_type: str, *path: str) -> str:
        return f"interface {iface_type} {'/'.join(path)}"

    @staticmethod
    def interface_range_ruijie(iface_type: str, slot: str, start: int, end: int) -> str:
        if start == end:
            return f"interface {iface_type} {slot}/{start}"
        return f"interface range {iface_type} {slot}/{start} - {slot}/{end}"

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
        return f"switchport trunk allowed vlan add {vlans}"

    # ==================================================================
    # 聚合口 —— AggregatePort
    # ==================================================================
    @staticmethod
    def interface_aggregateport(agg_id: int) -> str:
        return f"interface AggregatePort {agg_id}"

    @staticmethod
    def aggregateport_member_range(iface_type: str, slot: str, start: int, end: int, agg_id: int, mode: str = "active") -> List[str]:
        lines = [
            f"interface range {iface_type} {slot}/{start} - {slot}/{end}",
            f"port-group {agg_id}"
        ]
        if mode == "active":
            lines[-1] += " mode active"
        lines.append("exit")
        return lines

    @staticmethod
    def aggregateport_load_balance(algo: str) -> str:
        return f"aggregateport load-balance {algo}"

    @staticmethod
    def lacp_mode_active() -> str:
        return "lacp mode active"

    # ==================================================================
    # 生成树 STP/RSTP/MSTP
    # ==================================================================
    @staticmethod
    def spanning_tree_mode(mode: str) -> str:
        return f"spanning-tree mode {mode}"

    @staticmethod
    def spanning_tree_priority(prio: int) -> str:
        return f"spanning-tree priority {prio}"

    @staticmethod
    def spanning_tree_portfast() -> str:
        return "spanning-tree portfast"

    @staticmethod
    def spanning_tree_bpdu_protection() -> str:
        return "spanning-tree bpdu-protection"

    @staticmethod
    def spanning_tree_mst_config() -> List[str]:
        return ["spanning-tree mst configuration", "exit"]

    # ==================================================================
    # ACL
    # ==================================================================
    @staticmethod
    def acl_number_standard(num: int) -> str:
        return f"access-list {num}"

    @staticmethod
    def acl_number_extended(num: int) -> str:
        return f"ip access-list extended {num}"

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
        return [f"interface {iface}", f" ip access-group {acl_num} {d}", "exit"]

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

    # ==================================================================
    # 防环 / RLDP
    # ==================================================================
    @staticmethod
    def rldp_enable() -> str:
        return "rldp enable"

    @staticmethod
    def errdisable_recovery() -> str:
        return "errdisable recovery"

    @staticmethod
    def errdisable_recovery_interval(sec: int = 120) -> str:
        return f"errdisable recovery interval {sec}"

    @staticmethod
    def spanning_tree_bpdufilter_enable() -> str:
        return "spanning-tree bpdufilter enable"

    @staticmethod
    def rldp_port_loop_detect_shutdown() -> str:
        return "rldp port loop-detect shutdown-port"

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