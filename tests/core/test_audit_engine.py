"""local_audit_engine.py 单元测试 — 合规审计引擎。"""
import pytest
from src.core.local_audit_engine import (
    LocalAuditEngine, AuditResult, Finding, Severity,
    run_local_audit
)


# ─── 测试用配置片段 ───────────────────────────────────────

CISCO_INSECURE = """\
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
"""

CISCO_SECURE = """\
hostname Core-SW-01
!
enable secret 0 $tr0ngP@ss!
!
service password-encryption
!
snmp-server group MYGROUP v3 priv
snmp-server user admin MYGROUP v3 auth sha Pass123 priv aes256 Key123
!
interface GigabitEthernet0/0/1
 description Uplink-Core
 switchport mode access
 switchport access vlan 100
!
line vty 0 4
 access-class MGMT in
 transport input ssh
 login local
 exec-timeout 15 0
!
ip ssh version 2
!
ntp server pool.ntp.org
logging host 192.168.1.10
logging buffered 16384
logging trap informational
service timestamps log datetime msec localtime
no ip domain-lookup
!
ip access-list standard MGMT
 permit 192.168.100.0 0.0.0.255
 deny any log
!
banner login ^
Authorized Access Only!
^
"""

HUAWEI_INSECURE = """\
sysname Huawei-SW
super password simple huawei@123
snmp-agent community read public
snmp-agent community write private
user-interface vty 0 4
 protocol incoming telnet
 set authentication password simple Admin123
"""

HUAWEI_SECURE = """\
sysname CoreSW-Huawei-01
super password cipher %^%$StrongPass123%^%$
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
"""


class TestSeverity:
    """严重级别枚举测试"""

    def test_labels(self):
        assert Severity.CRITICAL.label == "严重"
        assert Severity.HIGH.label == "高危"
        assert Severity.MEDIUM.label == "中危"
        assert Severity.LOW.label == "低危"

    def test_verdict_labels(self):
        assert Severity.CRITICAL.verdict_label == "不通过"
        assert Severity.HIGH.verdict_label == "警告"
        assert Severity.MEDIUM.verdict_label == "警告"
        assert Severity.LOW.verdict_label == "通过"


class TestAuditResult:
    """审计结果数据结构测试"""

    def test_empty_result(self):
        r = AuditResult(findings=[])
        assert r.total_findings == 0
        assert r.critical_count == 0
        assert r.verdict == "通过"

    def test_verdict_critical(self):
        r = AuditResult(findings=[
            Finding(id="T1", severity=Severity.CRITICAL, title="t", issue="i",
                    location="L", risk="r", fix="f"),
        ])
        assert r.verdict == "不通过"

    def test_verdict_high(self):
        r = AuditResult(findings=[
            Finding(id="T1", severity=Severity.HIGH, title="t", issue="i",
                    location="L", risk="r", fix="f"),
            Finding(id="T2", severity=Severity.HIGH, title="t", issue="i",
                    location="L", risk="r", fix="f"),
            Finding(id="T3", severity=Severity.HIGH, title="t", issue="i",
                    location="L", risk="r", fix="f"),
        ])
        assert r.verdict == "警告"

    def test_verdict_pass(self):
        r = AuditResult(findings=[
            Finding(id="T1", severity=Severity.LOW, title="t", issue="i",
                    location="L", risk="r", fix="f"),
        ])
        assert r.verdict == "通过"


class TestVendorDetection:
    """厂商自动识别测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_detect_cisco(self):
        vk = self.engine.detect_vendor(CISCO_INSECURE)
        assert vk == "cisco_ios"

    def test_detect_huawei(self):
        vk = self.engine.detect_vendor(HUAWEI_INSECURE)
        assert vk == "huawei_vrp"

    def test_detect_with_hint(self):
        vk = self.engine.detect_vendor("some config", hint_vendor="华为")
        assert vk == "huawei_vrp"

    def test_detect_with_hint_ruijie(self):
        vk = self.engine.detect_vendor("some config", hint_vendor="锐捷")
        assert vk == "ruijie_os"

    def test_detect_with_hint_h3c(self):
        vk = self.engine.detect_vendor("some config", hint_vendor="H3C")
        assert vk == "h3c_comware"

    def test_detect_empty_fallback(self):
        """空配置应回退到cisco_ios"""
        vk = self.engine.detect_vendor("")
        assert vk == "cisco_ios"


class TestCiscoAudit:
    """Cisco配置合规审计测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_insecure_cisco(self):
        result = self.engine.audit(CISCO_INSECURE)
        ids = [f.id for f in result.findings]
        # 应检测到：Telnet、SNMP public、enable password、SSHv1
        assert "CISCO-C01" in ids  # Telnet
        assert "CISCO-C02" in ids  # SNMP public
        assert "CISCO-H01" in ids  # enable password
        assert "CISCO-H02" in ids  # SSHv1
        assert result.verdict == "不通过"

    def test_secure_cisco(self):
        result = self.engine.audit(CISCO_SECURE)
        ids = [f.id for f in result.findings]
        # 不应检测到Telnet、SNMP public、enable password、SSHv1
        assert "CISCO-C01" not in ids
        assert "CISCO-C02" not in ids
        assert "CISCO-H01" not in ids
        assert "CISCO-H02" not in ids

    def test_vendor_reported(self):
        result = self.engine.audit(CISCO_INSECURE)
        assert result.vendor == "Cisco IOS"

    def test_config_size_recorded(self):
        result = self.engine.audit(CISCO_INSECURE)
        assert result.config_size == len(CISCO_INSECURE)


class TestHuaweiAudit:
    """华为配置合规审计测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_insecure_huawei(self):
        result = self.engine.audit(HUAWEI_INSECURE)
        ids = [f.id for f in result.findings]
        assert "HUAWEI-C01" in ids  # Telnet
        assert "HUAWEI-C02" in ids  # SNMP public
        assert result.verdict == "不通过"

    def test_secure_huawei(self):
        result = self.engine.audit(HUAWEI_SECURE)
        ids = [f.id for f in result.findings]
        assert "HUAWEI-C01" not in ids
        assert "HUAWEI-C02" not in ids

    def test_vendor_reported(self):
        result = self.engine.audit(HUAWEI_INSECURE)
        assert result.vendor == "Huawei VRP"


class TestAuditContextExtraction:
    """精准上下文提取测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_context_extraction(self):
        result = self.engine.audit(CISCO_INSECURE)
        ctx = result.extract_relevant_context(CISCO_INSECURE)
        assert len(ctx) > 0
        # 应包含问题配置行
        assert "telnet" in ctx.lower() or "snmp" in ctx.lower()

    def test_context_no_findings(self):
        result = AuditResult(findings=[])
        ctx = result.extract_relevant_context("some config")
        assert ctx == ""

    def test_context_empty_content(self):
        result = self.engine.audit(CISCO_INSECURE)
        ctx = result.extract_relevant_context("")
        assert ctx == ""


class TestAuditSummary:
    """摘要文本生成测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_summary_with_findings(self):
        result = self.engine.audit(CISCO_INSECURE)
        summary = result.to_summary_text()
        assert "本地合规审计报告" in summary
        assert "不通过" in summary

    def test_ai_prompt_context(self):
        result = self.engine.audit(CISCO_INSECURE)
        ctx = result.to_ai_prompt_context()
        assert "本地合规预检" in ctx
        assert str(result.total_findings) in ctx

    def test_ai_prompt_no_findings(self):
        result = AuditResult(findings=[])
        ctx = result.to_ai_prompt_context()
        assert ctx == "本地合规预检未发现明显问题。"


class TestConvenienceFunction:
    """便捷函数测试"""

    def test_run_local_audit(self):
        result = run_local_audit(CISCO_INSECURE)
        assert isinstance(result, AuditResult)
        assert result.total_findings > 0

    def test_run_with_vendor_hint(self):
        result = run_local_audit(HUAWEI_INSECURE, vendor_hint="华为")
        assert result.vendor == "Huawei VRP"


class TestRuleCount:
    """规则加载测试"""

    def setup_method(self):
        self.engine = LocalAuditEngine()

    def test_rules_loaded(self):
        total = self.engine.get_rule_count()
        assert total > 0

    def test_vendor_rule_count(self):
        count = self.engine.get_rule_count("cisco_ios")
        assert count > 0
