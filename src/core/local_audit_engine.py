import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @property
    def label(self) -> str:
        return {
            "CRITICAL": "严重",
            "HIGH": "高危",
            "MEDIUM": "中危",
            "LOW": "低危",
        }[self.value]

    @property
    def verdict_label(self) -> str:
        return {
            "CRITICAL": "不通过",
            "HIGH": "警告",
            "MEDIUM": "警告",
            "LOW": "通过",
        }[self.value]


@dataclass
class Finding:
    id: str
    severity: Severity
    title: str
    issue: str
    location: str
    risk: str
    fix: str
    matched_line: str = ""
    line_number: int = 0


@dataclass
class AuditResult:
    findings: List[Finding] = field(default_factory=list)
    device_type: str = "unknown"
    vendor: str = "unknown"
    config_size: int = 0
    audit_time_ms: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def verdict(self) -> str:
        if self.critical_count > 0:
            return "不通过"
        if self.high_count >= 3:
            return "警告"
        if self.high_count > 0 or self.medium_count > 2:
            return "警告"
        return "通过"

    def to_summary_text(self) -> str:
        SEV_CN = {"CRITICAL": ("严重", "\U0001f534"), "HIGH": ("高危", "\U0001f7e0"),
                  "MEDIUM": ("中危", "\U0001f7e1"), "LOW": ("低危", "\U0001f7e2")}
        lines = [f"## 本地合规审计报告（审计结论：{self.verdict}）"]
        c, h, m, l = self.critical_count, self.high_count, self.medium_count, self.low_count
        lines.append(f"| 严重 | 高危 | 中危 | 低危 | 合计 |")
        lines.append(f"| :--: | :--: | :--: | :--: | :--: |")
        lines.append(f"| {c} | {h} | {m} | {l} | {self.total_findings} |")
        lines.append("")
        for f in self.findings:
            cn_label, icon = SEV_CN[f.severity.value]
            lines.append(f"{icon} **[{f.id}]** [{cn_label}] {f.title}")
            lines.append(f"   - 问题：{f.issue}")
            lines.append(f"   - 风险：{f.risk}")
            lines.append(f"   - 修复建议：{f.fix}")
            lines.append("")
        return "\n".join(lines)

    def to_ai_prompt_context(self) -> str:
        """生成供AI使用的精简合规问题列表（仅问题，无冗余风险/修复重复）"""
        if not self.findings:
            return "本地合规预检未发现明显问题。"

        lines = [f"本地合规预检发现 {self.total_findings} 个问题（结论: {self.verdict}）:"]
        for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            sev_items = [f for f in self.findings if f.severity == sev]
            if not sev_items:
                continue
            lines.append(f"\n{sev.label}:")
            for f in sev_items:
                lines.append(f"- [{f.id}] {f.title}: {f.issue}")

        return "\n".join(lines)

    def extract_relevant_context(self, content: str, context_lines: int = 6,
                                  max_total_lines: int = 150) -> str:
        """
        根据合规问题在配置中的位置，精准提取相关配置段落。
        不发送全文，只返回问题配置行附近的上下文，大幅减少token消耗。

        策略：优先用 line_number 精确定位，其次用 matched_line 子串匹配，
        每问题最多匹配2行，总提取行数上限 max_total_lines。

        Args:
            content: 原始配置内容
            context_lines: 每个匹配行前后保留的行数
            max_total_lines: 提取总行数上限

        Returns:
            拼接后的精准配置上下文片段
        """
        if not self.findings or not content:
            return ""

        config_lines = content.splitlines()
        total_lines = len(config_lines)

        # 收集每个问题在原文中的行号（每问题最多2行）
        matched_line_sets = []
        for f in self.findings:
            line_set = set()
            # 优先用已记录的 line_number
            if f.line_number > 0:
                line_set.add(f.line_number - 1)  # 转为0索引
            # 其次用 matched_line 文本精确匹配
            elif f.matched_line:
                search_text = f.matched_line.strip()
                for i, line in enumerate(config_lines):
                    if search_text in line or line.strip() == search_text:
                        line_set.add(i)
                        if len(line_set) >= 2:
                            break
            if line_set:
                matched_line_sets.append(line_set)

        if not matched_line_sets:
            parts = []
            for f in self.findings:
                if f.matched_line:
                    parts.append(f"[{f.id}] {f.matched_line}")
            return "关键问题配置行:\n" + "\n".join(parts) if parts else ""

        # 合并所有行号，应用 context_lines 扩展
        all_matched = set()
        for ls in matched_line_sets:
            for ln in ls:
                for j in range(max(0, ln - context_lines),
                               min(total_lines, ln + context_lines + 1)):
                    all_matched.add(j)

        # 总行数超限则降级为摘要
        if len(all_matched) > max_total_lines:
            parts = []
            for f in self.findings:
                if f.matched_line:
                    parts.append(f"[{f.id}] {f.matched_line}")
            return "关键问题配置行:\n" + "\n".join(parts)

        # 合并连续区间
        sorted_lines = sorted(all_matched)
        merged_ranges = []
        start = sorted_lines[0]
        end = sorted_lines[0]
        for ln in sorted_lines[1:]:
            if ln <= end + 1:
                end = ln
            else:
                merged_ranges.append((start, end))
                start = end = ln
        merged_ranges.append((start, end))

        # 提取区间内容
        parts = []
        for s, e in merged_ranges:
            if parts:
                parts.append("\n...（省略中间无关配置）...\n")
            snippet = "\n".join(config_lines[s:e + 1])
            parts.append(snippet)

        return "\n".join(parts)


VENDOR_RULES = {
    "cisco_ios": {
        "name": "Cisco IOS",
        "patterns": {
            "vty_section": re.compile(r"^line\s+vty\s+\d+\s+\d+", re.MULTILINE | re.IGNORECASE),
            "telnet_enabled": re.compile(r"transport\s+input\s+(?!.*ssh)(?!.*none).*telnet", re.MULTILINE | re.IGNORECASE),
            "ssh_only": re.compile(r"transport\s+input\s+ssh\s*$", re.MULTILINE | re.IGNORECASE),
            "snmp_community_public": re.compile(r"snmp-server\s+community\s+(public|private)\s+\w*", re.MULTILINE | re.IGNORECASE),
            "enable_password": re.compile(r"^\s*enable\s+password\s+", re.MULTILINE | re.IGNORECASE),
            "enable_secret": re.compile(r"^\s*enable\s+secret\s+", re.MULTILINE | re.IGNORECASE),
            "password_encryption": re.compile(r"service\s+password-encryption", re.MULTILINE | re.IGNORECASE),
            "plaintext_password": re.compile(r"(?:username|password)\s+\w+\s+password\s+[\"']?[a-zA-Z0-9_]+[\"']?", re.MULTILINE | re.IGNORECASE),
            "ssh_version_1": re.compile(r"ip\s+ssh\s+version\s+1\b", re.MULTILINE | re.IGNORECASE),
            "ntp_server": re.compile(r"ntp\s+server\s+\d", re.MULTILINE | re.IGNORECASE),
            "logging_config": re.compile(r"logging\s+(?:host|buffered|server)", re.MULTILINE | re.IGNORECASE),
            "banner_login": re.compile(r"banner\s+(?:login|motd|exec)\s*\^", re.MULTILINE | re.IGNORECASE),
            "domain_lookup": re.compile(r"no\s+ip\s+domain-lookup", re.MULTILINE | re.IGNORECASE),
            "exec_timeout_disabled": re.compile(r"line\s+vty.*?(?:exec-timeout\s+0\s+0|no\s+exec-timeout)", re.MULTILINE | re.IGNORECASE | re.DOTALL),
            "hostname_set": re.compile(r"hostname\s+\S+", re.MULTILINE | re.IGNORECASE),
            "weak_passwords": re.compile(r"(?:password|secret)\s+(?:cisco|admin|test|12345|password|pass|default)\b", re.MULTILINE | re.IGNORECASE),
            "access_class_vty": re.compile(r"(?:ip\s+)?access-class\s+\w+\s+(?:in|out)", re.MULTILINE | re.IGNORECASE),
            "snmp_v3": re.compile(r"snmp-server\s+group\s+\w+\s+v3", re.MULTILINE | re.IGNORECASE),
        },
        "rule_checks": [
            {
                "id": "CISCO-C01",
                "severity": "CRITICAL",
                "title": "Telnet Enabled (Cleartext Remote Access)",
                "pattern_key": "telnet_enabled",
                "condition": "match",
                "issue": "Telnet is enabled on VTY lines, allowing cleartext remote access that can be intercepted.",
                "risk": "Attackers can capture credentials and configuration data from network traffic.",
                "fix": "Disable telnet and use SSH only:\n line vty 0 4\n  transport input ssh\n  no transport input telnet",
            },
            {
                "id": "CISCO-C02",
                "severity": "CRITICAL",
                "title": "SNMP Default Community String (public/private)",
                "pattern_key": "snmp_community_public",
                "condition": "match",
                "issue": "SNMP is configured with default community string 'public' (RO) or 'private' (RW).",
                "risk": "Anyone can read device info (public) or fully control it (private). These are constantly scanned.",
                "fix": "Change to non-default community strings or use SNMPv3 with authentication and encryption:\n snmp-server group MYGROUP v3 priv\n snmp-server user admin MYGROUP v3 auth sha PASSWORD123 priv aes256 KEY123",
            },
            {
                "id": "CISCO-H01",
                "severity": "HIGH",
                "title": "Uses enable password Instead of enable secret",
                "pattern_key": "enable_password",
                "condition": "match_and_not",
                "negate_pattern_key": "enable_secret",
                "issue": "'enable password' uses Type-7 reversible encryption instead of secure hashing.",
                "risk": "Type-7 passwords can be easily decrypted online. Credentials are not properly protected.",
                "fix": "Replace with 'enable secret' which uses MD5 hashing:\n enable secret <strong-password>\n no enable password <old-password>",
            },
            {
                "id": "CISCO-H02",
                "severity": "HIGH",
                "title": "SSH Version 1 Enabled (Known Vulnerabilities)",
                "pattern_key": "ssh_version_1",
                "condition": "match",
                "issue": "SSH version 1 is enabled which has known cryptographic vulnerabilities.",
                "risk": "Man-in-the-middle attacks possible due to weak encryption in SSHv1.",
                "fix": "Force SSH version 2 only:\n ip ssh version 2\n ip ssh version 1 is removed by default when v2 is set",
            },
            {
                "id": "CISCO-H03",
                "severity": "HIGH",
                "title": "VTY Lines Without Access-Class Restriction",
                "pattern_key": "vty_section",
                "condition": "match_and_not",
                "negate_pattern_key": "access_class_vty",
                "issue": "VTY lines are configured but no access-class (ACL) restricts source IPs.",
                "risk": "Any host on the network can attempt brute-force login to management interfaces.",
                "fix": "Create an ACL for management access and apply it:\n ip access-list standard MGMT\n  permit 192.168.100.0 0.0.0.255\n  deny any log\n!\n line vty 0 4\n  access-class MGMT in",
            },
            {
                "id": "CISCO-H04",
                "severity": "HIGH",
                "title": "Weak/Common Password Detected",
                "pattern_key": "weak_passwords",
                "condition": "match",
                "issue": "A commonly used weak password was detected (cisco/admin/test/12345 etc.).",
                "risk": "These passwords are in every brute-force dictionary and will be cracked quickly.",
                "fix": "Use strong passwords (12+ chars, mixed case, numbers, symbols):\n username admin secret Str0ng@P@ssw0rd!2026",
            },
            {
                "id": "CISCO-M01",
                "severity": "MEDIUM",
                "title": "NTP Server Not Configured",
                "pattern_key": "ntp_server",
                "condition": "not_match",
                "issue": "No NTP server is configured for time synchronization.",
                "risk": "Log timestamps will be incorrect, making incident response and troubleshooting difficult.",
                "fix": "Configure NTP server(s):\n ntp server pool.ntp.org\n ntp server ntp.aliyun.com\n service timestamps log datetime msec localtime",
            },
            {
                "id": "CISCO-M02",
                "severity": "MEDIUM",
                "title": "Logging/Syslog Not Configured",
                "pattern_key": "logging_config",
                "condition": "not_match",
                "issue": "No logging destination (syslog server or buffer) is configured.",
                "risk": "No audit trail for security events. Cannot investigate incidents after the fact.",
                "fix": "Configure syslog:\n logging host 192.168.1.10\n logging buffered 16384\n logging trap informational\n service timestamps log datetime msec localtime",
            },
            {
                "id": "CISCO-M03",
                "severity": "MEDIUM",
                "title": "Login Banner Not Set",
                "pattern_key": "banner_login",
                "condition": "not_match",
                "issue": "No legal warning banner is displayed at login.",
                "risk": "No legal protection against unauthorized access attempts.",
                "fix": "Set a login banner:\n banner login ^\n Authorized Access Only!\n All sessions are monitored and logged.\n Unauthorized access will be prosecuted.\n ^",
            },
            {
                "id": "CISCO-M04",
                "severity": "MEDIUM",
                "title": "Password Encryption Service Disabled",
                "pattern_key": "password_encryption",
                "condition": "not_match",
                "issue": "'service password-encryption' is not enabled.",
                "risk": "Passwords in config are stored in plaintext (or visible Type-7). Anyone viewing config sees credentials.",
                "fix": "Enable password encryption:\n service password-encryption\n Note: This provides Type-7 encryption (weak but better than plaintext)",
            },
            {
                "id": "CISCO-M05",
                "severity": "MEDIUM",
                "title": "IP Domain-Lookup Not Disabled",
                "pattern_key": "domain_lookup",
                "condition": "not_match",
                "issue": "'no ip domain-lookup' is not configured.",
                "risk": "Typos in CLI commands trigger DNS lookups, causing delays and potential information leaks.",
                "fix": "Disable domain lookup:\n no ip domain-lookup",
            },
            {
                "id": "CISCO-M06",
                "severity": "MEDIUM",
                "title": "Exec-Timeout Not Configured or Too Long",
                "pattern_key": "exec_timeout_disabled",
                "condition": "match",
                "issue": "VTY exec-timeout is disabled (0 0) or not set, allowing sessions to stay open indefinitely.",
                "risk": "Abandoned sessions lock out other admins and create security risk if left unattended.",
                "fix": "Set reasonable timeout on VTY lines:\n line vty 0 4\n  exec-timeout 15 0",
            },
            {
                "id": "CISCO-L01",
                "severity": "LOW",
                "title": "Hostname Not Configured",
                "pattern_key": "hostname_set",
                "condition": "not_match",
                "issue": "Device hostname is not set or using default.",
                "risk": "Difficult to identify device in logs and network maps.",
                "fix": "Set a meaningful hostname:\n hostname CORE-SW-01-FLOOR3",
            },
            {
                "id": "CISCO-L02",
                "severity": "LOW",
                "title": "SNMP Using Insecure v2c (Cleartext)",
                "pattern_key": "snmp_community_public",
                "condition": "match_and_not",
                "negate_pattern_key": "snmp_v3",
                "issue": "SNMP community strings are sent in cleartext (SNMPv2c).",
                "risk": "Community strings can be sniffed from network traffic.",
                "fix": "Migrate to SNMPv3 with auth+priv, or accept risk for non-production environments.",
            },
        ],
    },
    "huawei_vrp": {
        "name": "Huawei VRP",
        "patterns": {
            "vty_section": re.compile(r"^user-interface\s+vty\s+\d+\s+\d+", re.MULTILINE | re.IGNORECASE),
            "telnet_enabled": re.compile(r"protocol\s+incoming\s+(?!.*ssh)(?!.*none).*telnet", re.MULTILINE | re.IGNORECASE),
            "ssh_only": re.compile(r"protocol\s+incoming\s+ssh(?:\s|$)", re.MULTILINE | re.IGNORECASE),
            "snmp_community_public": re.compile(r"snmp-agent\s+community\s+(?:read|write)\s+(?:public|private)\b", re.MULTILINE | re.IGNORECASE),
            "super_password_weak": re.compile(r"super\s+password\s+(?:cipher|simple)?\s*(?:cisco|admin|test|12345|password|Huawei@123)\b", re.MULTILINE | re.IGNORECASE),
            "password_encryption": re.compile(r"set\s+authentication\s+password\s+cipher", re.MULTILINE | re.IGNORECASE),
            "plaintext_password": re.compile(r"set\s+authentication\s+password\s+simple\s+\S+", re.MULTILINE | re.IGNORECASE),
            "ssh_first_time": re.compile(r"ssh\s+client\s+first-time\s+enable", re.MULTILINE | re.IGNORECASE),
            "ntp_server": re.compile(r"ntp-server\s+(?:unicast-server|refclock-master)", re.MULTILINE | re.IGNORECASE),
            "logging_config": re.compile(r"info-center\s+(?:loghost|logfile)", re.MULTILINE | re.IGNORECASE),
            "banner_login": re.compile(r"header\s+(?:login|shell|input)\s*\"", re.MULTILINE | re.IGNORECASE),
            "domain_lookup": re.compile(r"undo\s+dns\s+resolve", re.MULTILINE | re.IGNORECASE),
            "idle_timeout_long": re.compile(r"idle-timeout\s+(\d+)\s*", re.MULTILINE | re.IGNORECASE),
            "hostname_set": re.compile(r"sysname\s+\S+", re.MULTILINE | re.IGNORECASE),
            "weak_passwords": re.compile(r"(?:password|cipher|simple)\s+(?:cisco|admin|test|12345|password|pass|default|Huawei@123)\b", re.MULTILINE | re.IGNORECASE),
            "acl_on_vty": re.compile(r"(?:acl\s+\d+|traffic-policy)\s+(?:inbound|outbound)", re.MULTILINE | re.IGNORECASE),
            "snmp_v3": re.compile(r"snmp-agent\s+usm-user\s+\w+\s+\w+\s+v3", re.MULTILINE | re.IGNORECASE),
        },
        "rule_checks": [
            {
                "id": "HUAWEI-C01",
                "severity": "CRITICAL",
                "title": "Telnet Enabled (Cleartext Remote Access)",
                "pattern_key": "telnet_enabled",
                "condition": "match",
                "issue": "Telnet is enabled on VTY user interface, allowing cleartext remote access.",
                "risk": "Credentials and session data transmitted in plaintext can be intercepted.",
                "fix": "Disable telnet and use SSH only:\n user-interface vty 0 4\n  protocol incoming ssh\n undo protocol incoming telnet",
            },
            {
                "id": "HUAWEI-C02",
                "severity": "CRITICAL",
                "title": "SNMP Default Community String (public/private)",
                "pattern_key": "snmp_community_public",
                "condition": "match",
                "issue": "SNMP agent uses default community string 'public' or 'private'.",
                "risk": "Default communities allow unauthorized read/write access to device MIB.",
                "fix": "Change to unique community strings or use SNMPv3:\n snmp-agent group v3grp v3 privacy\n snmp-agent usm-user v3user v3grp v3 authentication-mode sha Password123 privacy-mode aes128 Key123",
            },
            {
                "id": "HUAWEI-H01",
                "severity": "HIGH",
                "title": "Weak Super Password Detected",
                "pattern_key": "weak_passwords",
                "condition": "match",
                "issue": "A common weak password detected in super password or user authentication.",
                "risk": "Easily guessable passwords lead to full device compromise.",
                "fix": "Use strong cipher passwords:\n super password cipher StrongP@ss2026!",
            },
            {
                "id": "HUAWEI-H02",
                "severity": "HIGH",
                "title": "Plaintext Password in Configuration",
                "pattern_key": "plaintext_password",
                "condition": "match",
                "issue": "Password configured with 'simple' keyword, stored as plaintext in config.",
                "risk": "Anyone viewing config file sees actual password.",
                "fix": "Always use 'cipher' mode:\n set authentication password cipher <encrypted-value>",
            },
            {
                "id": "HUAWEI-H03",
                "severity": "HIGH",
                "title": "VTY Without ACL Restriction",
                "pattern_key": "vty_section",
                "condition": "match_and_not",
                "negate_pattern_key": "acl_on_vty",
                "issue": "VTY user interface has no ACL or traffic policy restricting source IPs.",
                "risk": "Any network host can attempt management login.",
                "fix": "Apply ACL to VTY:\n acl number 2000\n  rule permit source 192.168.100.0 0.0.0.255\n  rule deny\n user-interface vty 0 4\n  acl 2000 inbound",
            },
            {
                "id": "HUAWEI-H04",
                "severity": "HIGH",
                "title": "SSH First-Time Enable Security Risk",
                "pattern_key": "ssh_first_time",
                "condition": "match",
                "issue": "'ssh client first-time enable' auto-accepts unknown host keys.",
                "risk": "Vulnerable to man-in-the-middle attacks during initial SSH connections.",
                "fix": "Disable first-time trust and manually configure known host keys:\n undo ssh client first-time enable\n ssh client assign hostkey x.x.x.x rsa ...",
            },
            {
                "id": "HUAWEI-M01",
                "severity": "MEDIUM",
                "title": "NTP Server Not Configured",
                "pattern_key": "ntp_server",
                "condition": "not_match",
                "issue": "No NTP time synchronization source configured.",
                "risk": "Incorrect timestamps in logs affect incident analysis.",
                "fix": "Configure NTP:\n ntp-service unicast-server ntp.aliyun.com\n ntp-service authentication enable",
            },
            {
                "id": "HUAWEI-M02",
                "severity": "MEDIUM",
                "title": "Info-Center Logging Not Configured",
                "pattern_key": "logging_config",
                "condition": "not_match",
                "issue": "No syslog server or logfile destination configured via info-center.",
                "risk": "No centralized log collection for security monitoring.",
                "fix": "Configure info-center logging:\n info-center loghost 192.168.1.10 facility local7\n info-center timestamp log date precision-time centisecond",
            },
            {
                "id": "HUAWEI-M03",
                "severity": "MEDIUM",
                "title": "Login Banner/Header Not Set",
                "pattern_key": "banner_login",
                "condition": "not_match",
                "issue": "No login warning header/banner is displayed.",
                "risk": "No legal notice before authentication.",
                "fix": "Set login header:\n header login information \"Authorized Access Only. All sessions logged.\"",
            },
            {
                "id": "HUAWEI-M04",
                "severity": "MEDIUM",
                "title": "DNS Resolution Not Disabled",
                "pattern_key": "domain_lookup",
                "condition": "not_match",
                "issue": "DNS resolution is still enabled (no 'undo dns resolve').",
                "risk": "CLI typos trigger DNS queries causing delays.",
                "fix": "Disable DNS resolution:\n undo dns resolve",
            },
            {
                "id": "HUAWEI-M05",
                "severity": "MEDIUM",
                "title": "Idle Timeout Too Long or Disabled",
                "pattern_key": "idle_timeout_long",
                "condition": "match",
                "issue": "Idle timeout is very long (>30 min) or disabled, keeping sessions open indefinitely.",
                "risk": "Abandoned sessions become security risks.",
                "fix": "Set reasonable idle timeout:\n idle-timeout 10",
            },
            {
                "id": "HUAWEI-L01",
                "severity": "LOW",
                "title": "Sysname Not Configured",
                "pattern_key": "hostname_set",
                "condition": "not_match",
                "issue": "Device sysname is not set or using default.",
                "risk": "Hard to identify device in network topology.",
                "fix": "Set sysname:\n sysname SW-Core-Floor3-Huawei",
            },
            {
                "id": "HUAWEI-L02",
                "severity": "LOW",
                "title": "SNMP Using Insecure v2c",
                "pattern_key": "snmp_community_public",
                "condition": "match_and_not",
                "negate_pattern_key": "snmp_v3",
                "issue": "SNMP v2c sends community strings in cleartext.",
                "risk": "Community strings can be captured from network traffic.",
                "fix": "Consider migrating to SNMPv3 with authentication and privacy.",
            },
        ],
    },
    "h3c_comware": {
        "name": "H3C Comware",
        "inherit_from": "huawei_vrp",
        "pattern_overrides": {
            "vty_section": re.compile(r"^user-interface\s+vty\s+\d+\s+\d+", re.MULTILINE | re.IGNORECASE),
            "telnet_enabled": re.compile(r"protocol\s+incoming\s+(?!.*ssh)(?!.*none).*telnet", re.MULTILINE | re.IGNORECASE),
            "snmp_community_public": re.compile(r"snmp-agent\s+community\s+(?:read|write)\s+(?:public|private)\b", re.MULTILINE | re.IGNORECASE),
            "ntp_server": re.compile(r"ntp-service\s+(?:unicast-server|refclock-master)", re.MULTILINE | re.IGNORECASE),
            "logging_config": re.compile(r"info-center\s+(?:loghost|logfile)", re.MULTILINE | re.IGNORECASE),
            "banner_login": re.compile(r"header\s+(?:login|shell|input)\s*", re.MULTILINE | re.IGNORECASE),
            "domain_lookup": re.compile(r"undo\s+dns\s+resolve", re.MULTILINE | re.IGNORECASE),
            "hostname_set": re.compile(r"sysname\s+\S+", re.MULTILINE | re.IGNORECASE),
            "weak_passwords": re.compile(r"(?:password|cipher|simple)\s+(?:cisco|admin|test|12345|password|pass|default|h3c@123)\b", re.MULTILINE | re.IGNORECASE),
        },
        "id_prefix": "H3C",
    },
    "ruijie_os": {
        "name": "Ruijie OS",
        "inherit_from": "cisco_ios",
        "pattern_overrides": {
            "vty_section": re.compile(r"^line\s+vty\s+\d+\s+\d+", re.MULTILINE | re.IGNORECASE),
            "telnet_enabled": re.compile(r"transport\s+input\s+(?!.*ssh)(?!.*none).*telnet", re.MULTILINE | re.IGNORECASE),
            "snmp_community_public": re.compile(r"snmp-server\s+community\s+(public|private)\s+\w*", re.MULTILINE | re.IGNORECASE),
            "enable_password": re.compile(r"^\s*enable\s+password\s+", re.MULTILINE | re.IGNORECASE),
            "enable_secret": re.compile(r"^\s*enable\s+secret\s+", re.MULTILINE | re.IGNORECASE),
            "ssh_version_1": re.compile(r"ip\s+ssh\s+version\s+1\b", re.MULTILINE | re.IGNORECASE),
            "ntp_server": re.compile(r"ntp\s+server\s+\d", re.MULTILINE | re.IGNORECASE),
            "logging_config": re.compile(r"logging\s+(?:host|buffered|server)", re.MULTILINE | re.IGNORECASE),
            "banner_login": re.compile(r"banner\s+(?:login|motd|exec)\s*\^", re.MULTILINE | re.IGNORECASE),
            "domain_lookup": re.compile(r"no\s+ip\s+domain-lookup", re.MULTILINE | re.IGNORECASE),
            "hostname_set": re.compile(r"hostname\s+\S+", re.MULTILINE | re.IGNORECASE),
            "weak_passwords": re.compile(r"(?:password|secret)\s+(?:cisco|ruijie|admin|test|12345|password|pass|default)\b", re.MULTILINE | re.IGNORECASE),
        },
        "id_prefix": "RGOS",
    },
}

COMMON_RULES = [
    {
        "id": "COMM-M01",
        "severity": "MEDIUM",
        "title": "Configuration File Contains Plaintext Sensitive Data",
        "check_func": "_check_plaintext_secrets",
        "issue": "Configuration contains potentially sensitive data that should be protected.",
        "risk": "Sensitive data exposure if config file is accessed by unauthorized persons.",
        "fix": "Review and encrypt sensitive values. Use enable-secret, cipher mode, or external secrets manager.",
    },
]


class LocalAuditEngine:
    VENDOR_TYPE_MAP = {
        "思科": "cisco_ios",
        "华为": "huawei_vrp",
        "H3C": "h3c_comware",
        "锐捷": "ruijie_os",
        "cisco": "cisco_ios",
        "huawei": "huawei_vrp",
        "h3c": "h3c_comware",
        "ruijie": "ruijie_os",
    }

    def __init__(self):
        self._resolved_rules = {}
        self._resolve_all_rules()

    def _resolve_all_rules(self):
        for vendor_key, vendor_data in VENDOR_RULES.items():
            rules = list(vendor_data.get("rule_checks", []))
            inherit = vendor_data.get("inherit_from")
            overrides = vendor_data.get("pattern_overrides", {})
            prefix = vendor_data.get("id_prefix", "")

            if inherit and inherit in VENDOR_RULES:
                parent_rules = VENDOR_RULES[inherit].get("rule_checks", [])
                parent_patterns = VENDOR_RULES[inherit].get("patterns", {})
                merged_patterns = dict(parent_patterns)
                merged_patterns.update(overrides)
                for pr in parent_rules:
                    rule_copy = dict(pr)
                    if prefix:
                        rule_copy["id"] = rule_copy["id"].split("-")[0] + "-" + prefix + "-" + rule_copy["id"].split("-", 2)[-1] if "-" in rule_copy["id"][2:] else rule_copy["id"]
                    rules.append(rule_copy)
            else:
                merged_patterns = dict(vendor_data.get("patterns", {}))
                merged_patterns.update(overrides)

            self._resolved_rules[vendor_key] = {
                "name": vendor_data["name"],
                "patterns": merged_patterns,
                "rules": rules,
            }

    def detect_vendor(self, config_text: str, hint_vendor: str = "") -> str:
        if hint_vendor and hint_vendor.lower() in self.VENDOR_TYPE_MAP:
            return self.VENDOR_TYPE_MAP[hint_vendor.lower()]

        txt_lower = config_text.lower()

        unique_indicators = {
            "huawei_vrp": ["display current-configuration", "display version",
                           "user-interface vty", "super password", "super password cipher",
                           "info-center", "ntp-service", "acl number", "traffic-filter",
                           "undo", "sysname"],
            "h3c_comware": ["display current-configuration", "display version",
                            "user-interface vty", "info-center", "undo",
                            "irf-domain", "lldp global enable", "domain default enable"],
        }

        shared_ios = ["show running-config", "show version", "interface gigabitethernet",
                      "spanning-tree", "line vty", "enable secret", "enable password",
                      "service password-encryption", "banner login", "banner motd",
                      "ip ssh version", "snmp-server community"]

        ruijie_unique = ["rgos", "ruijie", "show ruijie", "version rgos",
                         "show boot-variable", "license update"]

        cisco_unique = ["cisco ios software", "cisco ios xe", "cisco ios xr",
                        "show inventory", "module ", "hw-module", "power inline"]

        scores = {}

        for vendor, keywords in unique_indicators.items():
            score = sum(3 for kw in keywords if kw in txt_lower)
            scores[vendor] = score

        ruijie_score = sum(5 for kw in ruijie_unique if kw in txt_lower)
        cisco_score = sum(5 for kw in cisco_unique if kw in txt_lower)

        shared_hits = sum(1 for kw in shared_ios if kw in txt_lower)

        if ruijie_score > 0 or cisco_score > 0:
            if ruijie_score > cisco_score:
                scores["ruijie_os"] = ruijie_score + (shared_hits * 0.5)
                scores["cisco_ios"] = cisco_score
            elif cisco_score > ruijie_score:
                scores["cisco_ios"] = cisco_score + (shared_hits * 0.5)
                scores["ruijie_os"] = ruijie_score
            else:
                scores["cisco_ios"] = shared_hits * 0.5
                scores["ruijie_os"] = shared_hits * 0.5
        else:
            scores["cisco_ios"] = shared_hits * 0.5
            scores["ruijie_os"] = shared_hits * 0.5

        best = max(scores, key=scores.get) if scores else "cisco_ios"
        return best if scores[best] > 0 else "cisco_ios"

    def _get_matched_line(self, pattern, config_text: str) -> Tuple[str, int]:
        match = pattern.search(config_text)
        if match:
            line_num = config_text[:match.start()].count('\n') + 1
            return match.group().strip(), line_num
        return "", 0

    def _check_plaintext_secrets(self, config_text: str) -> Optional[dict]:
        secret_patterns = [
            (re.compile(r"password\s+\S{1,4}\s*$", re.MULTILINE | re.IGNORECASE), "Very short password"),
            (re.compile(r"secret\s+0\s+\w+", re.MULTILINE | re.IGNORECASE), "Unhashed secret (type 0)"),
            (re.compile(r"(?:pre-shared-key|wpa-psk)\s+\S+", re.MULTILINE | re.IGNORECASE), "PSK key in plaintext"),
        ]
        for pat, desc in secret_patterns:
            m = pat.search(config_text)
            if m:
                return {"matched": True, "detail": desc}
        return None

    def audit(self, config_text: str, device_ip: str = "", vendor_hint: str = "") -> AuditResult:
        import time
        start = time.time()

        vendor_key = self.detect_vendor(config_text, vendor_hint)
        vendor_rules = self._resolved_rules.get(vendor_key)
        if not vendor_rules:
            vendor_key = "cisco_ios"
            vendor_rules = self._resolved_rules[vendor_key]

        patterns = vendor_rules["patterns"]
        rules = vendor_rules["rules"]
        findings = []

        for rule_def in rules:
            pattern_key = rule_def.get("pattern_key")
            condition = rule_def.get("condition", "match")

            if pattern_key and pattern_key in patterns:
                pattern = patterns[pattern_key]
                negate_key = rule_def.get("negate_pattern_key")
                negate_pattern = patterns.get(negate_key) if negate_key else None

                matched = bool(pattern.search(config_text))
                negated = bool(negate_pattern.search(config_text)) if negate_pattern else False

                should_fire = False
                if condition == "match":
                    should_fire = matched
                elif condition == "not_match":
                    should_fire = not matched
                elif condition == "match_and_not":
                    should_fire = matched and not negated

                if should_fire:
                    matched_line, line_num = self._get_matched_line(pattern, config_text)
                    finding = Finding(
                        id=rule_def["id"],
                        severity=Severity(rule_def["severity"]),
                        title=rule_def["title"],
                        issue=rule_def["issue"],
                        location=f"Line {line_num}" if line_num > 0 else "Global",
                        risk=rule_def["risk"],
                        fix=rule_def["fix"],
                        matched_line=matched_line,
                        line_number=line_num,
                    )
                    findings.append(finding)

            check_func_name = rule_def.get("check_func")
            if check_func_name and hasattr(self, check_func_name):
                func = getattr(self, check_func_name)
                result = func(config_text)
                if result and result.get("matched"):
                    finding = Finding(
                        id=rule_def["id"],
                        severity=Severity(rule_def["severity"]),
                        title=rule_def["title"],
                        issue=f"{rule_def['issue']} ({result.get('detail', '')})",
                        location="Global",
                        risk=rule_def["risk"],
                        fix=rule_def["fix"],
                    )
                    findings.append(finding)

        elapsed_ms = int((time.time() - start) * 1000)

        return AuditResult(
            findings=findings,
            device_type=device_ip,
            vendor=vendor_rules["name"],
            config_size=len(config_text),
            audit_time_ms=elapsed_ms,
        )

    def get_rule_count(self, vendor_key: str = None) -> int:
        if vendor_key and vendor_key in self._resolved_rules:
            return len(self._resolved_rules[vendor_key]["rules"])
        total = 0
        for vr in self._resolved_rules.values():
            total += len(vr.get("rules", []))
        return total


def run_local_audit(config_content: str, device_ip: str = "",
                    vendor_hint: str = "") -> AuditResult:
    engine = LocalAuditEngine()
    return engine.audit(config_content, device_ip, vendor_hint)


if __name__ == "__main__":
    test_configs = {
        "cisco_insecure": """!
hostname Switch-Insecure
!
enable password cisco123
!
snmp-server community public RO
snmp-server community private RW
!
interface GigabitEthernet0/0/1
 description Uplink-to-Core
 switchport mode access
 switchport access vlan 100
!
line vty 0 4
 password telnetpass
 login local
 transport input telnet
!
ip ssh version 1
!
""",
        "huawei_secure": """#
sysname CoreSW-Huawei-01
#
super password cipher %^%$StrongPass123%^%$
#
interface GigabitEthernet0/0/1
 description Uplink-Core
 port link-type access
 port default vlan 100
#
user-interface vty 0 4
 protocol incoming ssh
 set authentication password cipher %^%$Admin@2026%^%$
 acl 2000 inbound
#
ntp-service unicast-server ntp.aliyun.com
info-center loghost 192.168.1.10
header login information "Authorized Access Only"
undo dns resolve
idle-timeout 10
#
snmp-agent group v3group v3 privacy
snmp-agent usm-user v3user v3group v3 authentication-mode sha Pass123 privacy-mode aes128 Key123
#
""",
    }

    engine = LocalAuditEngine()
    print("=" * 60)
    print("  LocalAuditEngine Test")
    print("=" * 60)

    for name, config in test_configs.items():
        print(f"\n--- Testing: {name} ({len(config)} chars) ---")
        result = engine.audit(config, "172.20.100.254")
        print(f"  Vendor: {result.vendor}")
        print(f"  Verdict: {result.verdict}")
        print(f"  Findings: {result.total_findings} (C:{result.critical_count} H:{result.high_count} M:{result.medium_count} L:{result.low_count})")
        print(f"  Time: {result.audit_time_ms}ms")
        for f in result.findings:
            sev_icon = {"CRITICAL": "[!]", "HIGH": "[*]", "MEDIUM": "[~]", "LOW": "[-]"}
            print(f"  {sev_icon[f.severity.value]} {f.id}: {f.title}")

    print(f"\n  Total rules loaded: {engine.get_rule_count()}")
