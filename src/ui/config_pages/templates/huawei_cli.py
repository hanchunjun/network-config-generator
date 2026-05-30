#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华为设备 CLI 命令生成模板

封装所有设备类型的华为特有 CLI 语法。
"""

from typing import List


class HuaweiCLITemplate:
    VENDOR = "huawei"

    @staticmethod
    def set_hostname(name: str) -> str:
        return f"sysname {name}"

    @staticmethod
    def set_enable_password(pwd: str) -> List[str]:
        return [
            "aaa",
            f" local-user admin password irreversible-cipher {pwd}",
            " local-user admin privilege level 15",
            " local-user admin service-type terminal ssh telnet",
            "quit"
        ]

    @staticmethod
    def set_system_time(time_str: str) -> List[str]:
        return [
            f"clock datetime {time_str}",
            "clock timezone beijing add 08:00:00"
        ]

    @staticmethod
    def exit_context() -> str:
        return "quit"

    # ==================================================================
    # Console
    # ==================================================================
    @staticmethod
    def line_console_0() -> str:
        return "user-interface console 0"

    @staticmethod
    def console_auth_mode_password() -> str:
        return "authentication-mode password"

    @staticmethod
    def console_auth_mode_aaa() -> str:
        return "authentication-mode aaa"

    @staticmethod
    def console_set_password(pwd: str) -> str:
        return f"set authentication password cipher {pwd}"

    @staticmethod
    def local_user_aaa(user: str, pwd: str, level: int = 15, services: str = "terminal ssh telnet") -> List[str]:
        return [
            "aaa",
            f" local-user {user} password irreversible-cipher {pwd}",
            f" local-user {user} privilege level {level}",
            f" local-user {user} service-type {services}",
            "quit"
        ]

    @staticmethod
    def local_user_service(user: str, pwd: str, level: int = 15, service: str = "terminal") -> List[str]:
        return [
            "aaa",
            f" local-user {user} password irreversible-cipher {pwd}",
            f" local-user {user} privilege level {level}",
            f" local-user {user} service-type {service}",
            "quit"
        ]

    @staticmethod
    def line_vty(start: int = 0, end: int = 4) -> str:
        return f"user-interface vty {start} {end}"

    @staticmethod
    def vty_auth_aaa() -> str:
        return "authentication-mode aaa"

    @staticmethod
    def vty_auth_password() -> str:
        return "authentication-mode password"

    @staticmethod
    def vty_set_password(pwd: str) -> str:
        return f"set authentication password cipher {pwd}"

    @staticmethod
    def protocol_inbound_ssh() -> str:
        return "protocol inbound ssh"

    @staticmethod
    def protocol_inbound_telnet() -> str:
        return "protocol inbound telnet"

    @staticmethod
    def stelnet_server_enable() -> str:
        return "stelnet server enable"

    @staticmethod
    def ssh_user_auth(user: str) -> List[str]:
        return [
            f"ssh user {user} authentication-type password",
            f"ssh user {user} service-type stelnet"
        ]

    # ==================================================================
    # VLAN
    # ==================================================================
    @staticmethod
    def create_vlan(vid: int, description: str = "") -> List[str]:
        lines = [f"vlan {vid}"]
        if description:
            lines.append(f" description {description}")
        lines.append("quit")
        return lines

    @staticmethod
    def interface_vlanif(vid: int) -> str:
        return f"interface Vlanif {vid}"

    @staticmethod
    def ip_address(ip: str, mask: str) -> str:
        return f"ip address {ip} {mask}"

    @staticmethod
    def ip_route_static(dst: str, mask: str, gw: str) -> str:
        return f"ip route-static {dst} {mask} {gw}"

    # ==================================================================
    # 端口 —— 华为特色：interface GigabitEthernet 0/0/1
    #   批量：interface GigabitEthernet 0/0/1 to GigabitEthernet 0/0/4
    # ==================================================================
    @staticmethod
    def interface_single(iface_type: str, *path: str) -> str:
        return f"interface {iface_type} {'/'.join(path)}"

    @staticmethod
    def interface_range_huawei(iface_type: str, slot: str, start: int, end: int) -> str:
        return f"interface {iface_type}{slot}/{start} to {iface_type.replace(' ', '')}{slot}/{end}"

    @staticmethod
    def port_link_type_access() -> str:
        return "port link-type access"

    @staticmethod
    def port_link_type_trunk() -> str:
        return "port link-type trunk"

    @staticmethod
    def port_default_vlan(vid: int) -> str:
        return f"port default vlan {vid}"

    @staticmethod
    def port_trunk_allow_pass_vlan(vlans: str) -> str:
        return f"port trunk allow-pass vlan {vlans}"

    # ==================================================================
    # 聚合口 —— Eth-Trunk
    # ==================================================================
    @staticmethod
    def interface_eth_trunk(trunk_id: int) -> str:
        return f"interface Eth-Trunk{trunk_id}"

    @staticmethod
    def eth_trunk_member_iface(iface: str, trunk_id: int) -> str:
        return f"eth-trunk {trunk_id}"

    @staticmethod
    def link_aggregation_load_balance(algo: str) -> str:
        return f"link-aggregation load-balance {algo}"

    @staticmethod
    def lacp_mode_active() -> str:
        return "mode lacp-static"

    # ==================================================================
    # 生成树
    # ==================================================================
    @staticmethod
    def spanning_tree_mode(mode: str) -> str:
        mapping = {"STP": "stp", "RSTP": "rstp", "MSTP": "mstp"}
        return f"stp mode {mapping.get(mode, 'rstp')}"

    @staticmethod
    def spanning_tree_priority(prio: int) -> str:
        return f"stp priority {prio}"

    @staticmethod
    def spanning_tree_portfast() -> str:
        return "stp edged-port enable"

    @staticmethod
    def spanning_tree_bpdu_protection() -> str:
        return "stp bpdu-protection"

    @staticmethod
    def spanning_tree_mst_config() -> List[str]:
        return ["stp region-configuration", "quit"]

    # ==================================================================
    # ACL
    # ==================================================================
    @staticmethod
    def acl_number_standard(num: int) -> str:
        return f"acl number {num}"

    @staticmethod
    def acl_number_extended(num: int) -> str:
        return f"acl number {num}"

    @staticmethod
    def acl_rule_permit_ip(src: str, dst: str) -> str:
        return f" rule 5 permit ip source {src} destination {dst}"

    @staticmethod
    def acl_rule_deny_ip(src: str, dst: str) -> str:
        return f" rule 5 deny ip source {src} destination {dst}"

    @staticmethod
    def acl_rule_permit_tcp(src: str, dst: str, port: str = "") -> str:
        rule = f" rule 5 permit tcp source {src} destination {dst}"
        if port:
            rule += f" destination-port eq {port}"
        return rule

    @staticmethod
    def acl_rule_deny_tcp(src: str, dst: str, port: str = "") -> str:
        rule = f" rule 5 deny tcp source {src} destination {dst}"
        if port:
            rule += f" destination-port eq {port}"
        return rule

    @staticmethod
    def acl_apply_to_interface(iface: str, acl_num: int, direction: str) -> List[str]:
        dir_map = {"入方向": "inbound", "出方向": "outbound"}
        d = dir_map.get(direction, "inbound")
        return [
            f"interface {iface}",
            f" traffic-filter {d} acl {acl_num}",
            "quit"
        ]

    # ==================================================================
    # DHCP Snooping
    # ==================================================================
    @staticmethod
    def dhcp_snooping_enable() -> str:
        return "dhcp snooping enable"

    @staticmethod
    def dhcp_snooping_trust() -> str:
        return "dhcp snooping trusted"

    @staticmethod
    def dhcp_snooping_verify_mac() -> str:
        return "dhcp snooping check mac-address"

    # ==================================================================
    # 防环
    # ==================================================================
    @staticmethod
    def loopback_detection_enable() -> str:
        return "loopback-detect enable"

    @staticmethod
    def stp_bpdufilter_enable() -> str:
        return "stp bpdu-filter enable"

    @staticmethod
    def error_down_auto_recovery(sec: int = 300) -> List[str]:
        return [
            "error-down auto-recovery cause bpdu-protection interval 30",
            f"error-down auto-recovery cause all interval {sec}"
        ]

    # ==================================================================
    # 管理地址
    # ==================================================================
    @staticmethod
    def management_interface_vlan(vid: int, ip: str, mask: str) -> List[str]:
        return [
            f"interface Vlanif {vid}",
            f" ip address {ip} {mask}",
            "quit"
        ]