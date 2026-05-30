#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H3C（华三）设备 CLI 命令生成模板

封装所有设备类型的 H3C 特有 CLI 语法。
"""

from typing import List


class H3CCLITemplate:
    VENDOR = "h3c"

    @staticmethod
    def set_hostname(name: str) -> str:
        return f"sysname {name}"

    @staticmethod
    def set_enable_password(pwd: str) -> str:
        return f"super password role network-admin hash {pwd}"

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
        return "line console 0"

    @staticmethod
    def console_password(pwd: str) -> str:
        return f"password {pwd}"

    @staticmethod
    def console_login() -> str:
        return "login"

    @staticmethod
    def console_auth_mode_scheme() -> str:
        return "authentication-mode scheme"

    @staticmethod
    def local_user_manage(user: str, pwd: str, level: int = 3) -> List[str]:
        return [
            f"local-user {user} class manage",
            f" password hash {pwd}",
            f" service-type terminal",
            f" authorization-attribute level {level}",
            "quit"
        ]

    @staticmethod
    def local_user_ssh(user: str, pwd: str, level: int = 3) -> List[str]:
        return [
            f"local-user {user} class manage",
            f" password simple {pwd}",
            f" service-type ssh",
            f" authorization-attribute level {level}",
            "quit"
        ]

    @staticmethod
    def local_user_telnet(user: str, pwd: str, level: int = 3) -> List[str]:
        return [
            f"local-user {user} class manage",
            f" password simple {pwd}",
            f" service-type telnet",
            f" authorization-attribute level {level}",
            "quit"
        ]

    @staticmethod
    def line_vty(start: int = 0, end: int = 4) -> str:
        return f"line vty {start} {end}"

    @staticmethod
    def vty_auth_scheme() -> str:
        return "authentication-mode scheme"

    @staticmethod
    def vty_password(pwd: str) -> str:
        return f"password simple {pwd}"

    @staticmethod
    def vty_login() -> str:
        return "login"

    @staticmethod
    def protocol_inbound_ssh() -> str:
        return "protocol inbound ssh"

    @staticmethod
    def protocol_inbound_telnet() -> str:
        return "protocol inbound telnet"

    @staticmethod
    def ssh_server_enable() -> str:
        return "ssh server enable"

    @staticmethod
    def telnet_server_enable() -> str:
        return "telnet server enable"

    # ==================================================================
    # VLAN
    # ==================================================================
    @staticmethod
    def create_vlan(vid: int, name: str = "") -> List[str]:
        lines = [f"vlan {vid}"]
        if name:
            lines.append(f" name {name}")
        lines.append("quit")
        return lines

    @staticmethod
    def interface_vlan_iface(vid: int) -> str:
        return f"interface vlan-interface {vid}"

    @staticmethod
    def ip_address(ip: str, mask: str) -> str:
        return f"ip address {ip} {mask}"

    @staticmethod
    def ip_route_static(dst: str, mask: str, gw: str) -> str:
        return f"ip route-static {dst} {mask} {gw}"

    # ==================================================================
    # 端口
    # ==================================================================
    @staticmethod
    def interface_single(iface_type: str, *path: str) -> str:
        return f"interface {iface_type} {'/'.join(path)}"

    @staticmethod
    def interface_range_h3c(iface_type: str, slot_sub: str, start: int, end: int) -> str:
        return f"interface range {iface_type} {slot_sub}{start} to {iface_type} {slot_sub}{end}"

    @staticmethod
    def port_link_type_access() -> str:
        return "port link-type access"

    @staticmethod
    def port_link_type_trunk() -> str:
        return "port link-type trunk"

    @staticmethod
    def port_access_vlan(vid: int) -> str:
        return f"port access vlan {vid}"

    @staticmethod
    def port_trunk_permit_vlan(vlans: str) -> str:
        return f"port trunk permit vlan {vlans}"

    # ==================================================================
    # 聚合口 —— Bridge-Aggregation
    # ==================================================================
    @staticmethod
    def interface_bridge_aggregation(agg_id: int) -> str:
        return f"interface Bridge-Aggregation {agg_id}"

    @staticmethod
    def bridge_agg_member_iface(iface: str, agg_id: int) -> str:
        return f"port link-aggregation group {agg_id}"

    @staticmethod
    def link_aggregation_load_sharing(algo: str) -> str:
        return f"link-aggregation global load-sharing mode {algo}"

    @staticmethod
    def lacp_mode_active() -> str:
        return "link-aggregation mode dynamic"

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
        return "stp edged-port"

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
        return f"acl advanced {num}"

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
            f" packet-filter {acl_num} {d}",
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
        return "dhcp snooping trust"

    @staticmethod
    def dhcp_snooping_verify_mac() -> str:
        return "dhcp snooping check mac-address"

    # ==================================================================
    # 防环
    # ==================================================================
    @staticmethod
    def loopback_detection_enable() -> str:
        return "loopback-detection enable"

    @staticmethod
    def stp_bpdufilter_enable() -> str:
        return "stp bpdu-filter enable"

    @staticmethod
    def error_down_auto_recovery(sec: int = 300) -> str:
        return f"error-down auto-recovery interval {sec}"

    # ==================================================================
    # 管理地址
    # ==================================================================
    @staticmethod
    def management_interface_vlan(vid: int, ip: str, mask: str) -> List[str]:
        return [
            f"interface vlan-interface {vid}",
            f" ip address {ip} {mask}",
            "quit"
        ]