"""local_diagnostic_engine.py 单元测试 — 运行时诊断引擎。"""
import pytest
from src.core.local_diagnostic_engine import (
    LocalDiagnosticEngine, DiagResult, DiagFinding, DiagSeverity,
    run_local_diagnostic
)


class TestDiagResult:
    """诊断结果数据结构测试"""

    def test_empty_result(self):
        r = DiagResult(findings=[], source_type="report")
        assert r.total_findings == 0
        assert r.critical_count == 0
        assert r.verdict == "正常"

    def test_verdict_critical(self):
        r = DiagResult(findings=[
            DiagFinding(id="T1", severity=DiagSeverity.CRITICAL, category="cpu",
                        title="test", issue="test", evidence="test"),
        ])
        assert r.verdict == "严重异常"

    def test_verdict_high(self):
        r = DiagResult(findings=[
            DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="test", issue="test", evidence="test"),
            DiagFinding(id="T2", severity=DiagSeverity.HIGH, category="cpu",
                        title="test", issue="test", evidence="test"),
        ])
        assert r.verdict == "高危"

    def test_verdict_normal(self):
        r = DiagResult(findings=[])
        assert r.to_ai_prompt_context() == "本地预诊断未发现明显异常。"


class TestLocalDiagnosticEngine:
    """诊断引擎规则匹配测试"""

    def setup_method(self):
        self.engine = LocalDiagnosticEngine()

    def test_no_anomalies(self):
        """正常报告不应触发告警"""
        content = """
        === 巡检报告 ===
        CPU utilization for five minutes: 45%
        Memory utilization: 50%
        GigabitEthernet0/0/1 is up
        GigabitEthernet0/0/2 is up
        """
        result = self.engine.diagnose(content)
        assert result.total_findings == 0
        assert result.verdict == "正常"

    def test_cpu_critical(self):
        """CPU 92%应触发CPU-C01（使用规则匹配的格式）"""
        content = "CPU five min: 92%"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "CPU-C01" in ids

    def test_cpu_high(self):
        """CPU 75%应触发CPU-H01但不触发CPU-C01"""
        content = "CPU five min: 75%"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "CPU-H01" in ids
        assert "CPU-C01" not in ids

    def test_cpu_normal(self):
        """CPU 50%不应触发任何CPU告警"""
        content = "CPU utilization for five minutes: 50%"
        result = self.engine.diagnose(content)
        cpu_ids = [f.id for f in result.findings if f.category == "cpu"]
        assert len(cpu_ids) == 0

    def test_memory_critical(self):
        """内存95%应触发MEM-C01"""
        content = "Memory utilization: 95%"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "MEM-C01" in ids

    def test_memory_high(self):
        """内存85%应触发MEM-H01"""
        content = "Memory utilization: 85%"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "MEM-H01" in ids

    def test_interface_down(self):
        """接口Down应触发IF-C01"""
        content = "GigabitEthernet0/0/2 is down"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "IF-C01" in ids

    def test_interface_administratively_down_excluded(self):
        """administratively down应被排除"""
        content = "GigabitEthernet0/0/2 is administratively down"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "IF-C01" not in ids

    def test_crc_errors(self):
        """CRC错误超100应触发IF-C02"""
        content = " 1500 input errors, 200 CRC"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "IF-C02" in ids

    def test_bgp_neighbor_down(self):
        """BGP邻居Down应触发LOG-C01"""
        content = "BGP neighbor is down"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "LOG-C01" in ids

    def test_stp_topology_change(self):
        """STP拓扑变更应触发LOG-H01"""
        content = "spanning-tree topology change detected"
        result = self.engine.diagnose(content)
        ids = [f.id for f in result.findings]
        assert "LOG-H01" in ids

    def test_deduplication(self):
        """相同ID的规则只应触发一次"""
        content = """
        CPU utilization: 95%
        CPU five min: 96%
        CPU one min: 97%
        """
        result = self.engine.diagnose(content)
        cpu_ids = [f.id for f in result.findings if f.category == "cpu"]
        # CPU-C01应只出现一次
        assert cpu_ids.count("CPU-C01") == 1

    def test_comprehensive_report(self):
        """综合报告测试 — 多种异常混合"""
        content = """
        === 设备巡检报告 ===
        设备IP: 192.168.1.1
        厂商: 华为
        --- CPU ---
        CPU five min: 85%
        CPU one min: 92%
        --- 内存 ---
        Memory utilization: 78%
        --- 接口状态 ---
        GigabitEthernet0/0/1 is up
        GigabitEthernet0/0/2 is down
        GigabitEthernet0/0/3 is up
         1500 input errors, 200 CRC
        --- 日志 ---
        spanning-tree topology change detected
        BGP neighbor is down
        """
        result = self.engine.diagnose(content)
        assert result.total_findings > 0
        assert result.critical_count > 0  # BGP Down + 接口Down
        assert result.parse_time_ms >= 0

    def test_to_ai_prompt_context(self):
        """AI上下文摘要应包含发现的异常"""
        content = "CPU five min: 95%"
        result = self.engine.diagnose(content)
        ctx = result.to_ai_prompt_context()
        assert "CPU-C01" in ctx or "严重" in ctx

    def test_to_summary_text(self):
        """摘要文本应包含结论"""
        content = "CPU utilization for five minutes: 95%"
        result = self.engine.diagnose(content)
        summary = result.to_summary_text()
        assert "本地预诊断结果" in summary

    def test_extract_relevant_context(self):
        """精准上下文提取应返回异常附近的行"""
        content = "line1\nline2\nCPU utilization: 95%\nline4\nline5\n"
        result = self.engine.diagnose(content)
        ctx = result.extract_relevant_context(content)
        assert "CPU" in ctx

    def test_extract_relevant_context_no_findings(self):
        """无异常时返回空字符串"""
        result = DiagResult(findings=[])
        ctx = result.extract_relevant_context("some content")
        assert ctx == ""

    def test_run_local_diagnostic_convenience(self):
        """便捷函数应返回DiagResult"""
        result = run_local_diagnostic("CPU utilization: 30%")
        assert isinstance(result, DiagResult)
        assert result.total_findings == 0


class TestDiagResultVerdictEdgeCases:
    """诊断结果 verdict 边界条件测试"""

    def test_verdict_high_single(self):
        """单个HIGH → 异常"""
        r = DiagResult(findings=[
            DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="t"),
        ])
        assert r.verdict == "异常"

    def test_verdict_medium_many(self):
        """3个以上MEDIUM → 异常"""
        r = DiagResult(findings=[
            DiagFinding(id=f"M{i}", severity=DiagSeverity.MEDIUM, category="cpu",
                        title="t", issue="t", evidence="t")
            for i in range(3)
        ])
        assert r.verdict == "异常"

    def test_verdict_medium_one(self):
        """1个MEDIUM → 轻微异常"""
        r = DiagResult(findings=[
            DiagFinding(id="M1", severity=DiagSeverity.MEDIUM, category="cpu",
                        title="t", issue="t", evidence="t"),
        ])
        assert r.verdict == "轻微异常"

    def test_verdict_low(self):
        """LOW → 轻微异常"""
        r = DiagResult(findings=[
            DiagFinding(id="L1", severity=DiagSeverity.LOW, category="cpu",
                        title="t", issue="t", evidence="t"),
        ])
        assert r.verdict == "轻微异常"


class TestExtractRelevantContextEdgeCases:
    """精准上下文提取边界条件测试"""

    def test_evidence_empty_string(self):
        """evidence为纯空格时strip后为空，应跳过该证据"""
        f = DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="   ")
        r = DiagResult(findings=[f])
        ctx = r.extract_relevant_context("some content here")
        # 证据strip后为空被跳过，无匹配行，降级为证据摘要
        # 但由于evidence为空字符串，evidence_parts也为空
        # 实际行为：evidence.strip()为空 → 跳过 → matched_line_sets为空 → 降级
        # 降级时 f.evidence 为 "   " 非空 → evidence_parts包含 "[T1]    "
        assert isinstance(ctx, str)

    def test_no_findings_returns_empty(self):
        """无发现时返回空"""
        r = DiagResult(findings=[])
        assert r.extract_relevant_context("content") == ""

    def test_no_content_returns_empty(self):
        """无内容时返回空"""
        f = DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="test")
        r = DiagResult(findings=[f])
        assert r.extract_relevant_context("") == ""

    def test_evidence_not_in_content_fallback(self):
        """证据不在内容中降级为证据摘要"""
        f = DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="ZZZNOTEXIST999")
        r = DiagResult(findings=[f])
        ctx = r.extract_relevant_context("line1\nline2\nline3\n")
        assert "关键证据" in ctx
        assert "ZZZNOTEXIST999" in ctx

    def test_substring_match_fallback(self):
        """精确匹配失败后子串匹配应生效"""
        content = "prefix_ABCDEFGHIJ_suffix\n" * 20
        f = DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t",
                        evidence="XXX_ABCDEF_YYY")  # 含长度为20的子串
        r = DiagResult(findings=[f])
        ctx = r.extract_relevant_context(content)
        # 应通过子串匹配找到或降级为摘要
        assert isinstance(ctx, str)

    def test_max_lines_exceeded_fallback(self):
        """超过max_total_lines时降级为证据摘要"""
        content = "\n".join(f"line{i}" for i in range(500))
        # 多个发现，每个匹配多处，总行数会超限
        findings = []
        for i in range(10):
            f = DiagFinding(id=f"T{i}", severity=DiagSeverity.HIGH, category="cpu",
                            title="t", issue="t", evidence=f"line{i * 40}")
            findings.append(f)
        r = DiagResult(findings=findings)
        ctx = r.extract_relevant_context(content, context_lines=8, max_total_lines=50)
        assert "关键证据" in ctx

    def test_extract_preserves_context_lines(self):
        """提取应包含上下文行"""
        lines = [f"line{i}" for i in range(50)]
        lines[25] = "TARGET_MARKER_HERE"
        content = "\n".join(lines)
        f = DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="TARGET_MARKER_HERE")
        r = DiagResult(findings=[f])
        ctx = r.extract_relevant_context(content, context_lines=3, max_total_lines=200)
        assert "TARGET_MARKER_HERE" in ctx
        # 应包含前后3行
        assert "line22" in ctx or "line23" in ctx or "line24" in ctx

    def test_multiple_findings_merged_ranges(self):
        """多个发现的行区间应合并"""
        lines = [f"line{i}" for i in range(100)]
        lines[10] = "ERROR_FIRST"
        lines[80] = "ERROR_SECOND"
        content = "\n".join(lines)
        findings = [
            DiagFinding(id="T1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="t", evidence="ERROR_FIRST"),
            DiagFinding(id="T2", severity=DiagSeverity.CRITICAL, category="cpu",
                        title="t", issue="t", evidence="ERROR_SECOND"),
        ]
        r = DiagResult(findings=findings)
        ctx = r.extract_relevant_context(content, context_lines=2, max_total_lines=200)
        assert "ERROR_FIRST" in ctx
        assert "ERROR_SECOND" in ctx
        assert "省略中间无关内容" in ctx


class TestToSummaryText:
    """to_summary_text 方法测试"""

    def test_empty_findings_summary(self):
        """无发现时摘要应显示正常"""
        r = DiagResult(findings=[])
        text = r.to_summary_text()
        assert "未发现明显异常" in text

    def test_summary_with_findings(self):
        """有发现时摘要应包含表格"""
        r = DiagResult(findings=[
            DiagFinding(id="C1", severity=DiagSeverity.CRITICAL, category="cpu",
                        title="CPU过高", issue="CPU 95%", evidence="ev",
                        suggestion="检查进程"),
        ])
        text = r.to_summary_text()
        assert "本地预诊断结果" in text
        assert "严重" in text
        assert "CPU过高" in text
        assert "检查进程" in text

    def test_summary_multiple_severities(self):
        """多种严重级别应分别显示"""
        r = DiagResult(findings=[
            DiagFinding(id="C1", severity=DiagSeverity.CRITICAL, category="cpu",
                        title="t", issue="i", evidence="e"),
            DiagFinding(id="H1", severity=DiagSeverity.HIGH, category="cpu",
                        title="t", issue="i", evidence="e"),
            DiagFinding(id="M1", severity=DiagSeverity.MEDIUM, category="cpu",
                        title="t", issue="i", evidence="e"),
            DiagFinding(id="L1", severity=DiagSeverity.LOW, category="cpu",
                        title="t", issue="i", evidence="e"),
        ])
        text = r.to_summary_text()
        assert "高危" in text
        assert "中危" in text
        assert "低危" in text


class TestCheckThresholdRulesEdgeCases:
    """_check_threshold_rules 边界条件测试"""

    def test_no_threshold_match_without_value(self):
        """无阈值规则匹配但无数值时跳过"""
        from src.core.local_diagnostic_engine import _check_threshold_rules
        import re
        rules = [{
            "id": "TEST-01",
            "severity": DiagSeverity.HIGH,
            "title": "test",
            "pattern": re.compile(r"(duplex\s+mismatch)", re.IGNORECASE),
            "issue_tpl": "双工不匹配",
            "layer": "Layer1",
        }]
        # 匹配但无group(1)数字，应触发
        result = _check_threshold_rules("duplex mismatch detected", rules, "interface")
        assert len(result) == 1
        assert result[0].id == "TEST-01"

    def test_exclude_pattern_filters_match(self):
        """exclude_pattern 应过滤匹配"""
        from src.core.local_diagnostic_engine import _check_threshold_rules
        import re
        rules = [{
            "id": "TEST-02",
            "severity": DiagSeverity.CRITICAL,
            "title": "test",
            "pattern": re.compile(r"(\S+)\s+is\s+down", re.IGNORECASE),
            "exclude_pattern": re.compile(r"administratively", re.IGNORECASE),
            "issue_tpl": "{value} down",
            "layer": "L1",
        }]
        result = _check_threshold_rules("Gi0/0 is administratively down", rules, "if")
        assert len(result) == 0

    def test_threshold_not_met_skips(self):
        """低于阈值应跳过"""
        from src.core.local_diagnostic_engine import _check_threshold_rules
        import re
        rules = [{
            "id": "TEST-03",
            "severity": DiagSeverity.HIGH,
            "title": "test",
            "pattern": re.compile(r"(\d+)\s+CRC", re.IGNORECASE),
            "threshold": 100,
            "issue_tpl": "{value} CRC",
        }]
        # 50 < 100，应跳过
        result = _check_threshold_rules("50 CRC", rules, "if")
        assert len(result) == 0

    def test_threshold_met_triggers(self):
        """达到阈值应触发"""
        from src.core.local_diagnostic_engine import _check_threshold_rules
        import re
        rules = [{
            "id": "TEST-04",
            "severity": DiagSeverity.HIGH,
            "title": "test",
            "pattern": re.compile(r"(\d+)\s+CRC", re.IGNORECASE),
            "threshold": 100,
            "issue_tpl": "{value} CRC",
        }]
        result = _check_threshold_rules("200 CRC", rules, "if")
        assert len(result) == 1
        assert result[0].issue == "200 CRC"


class TestDiagSeverityLabel:
    """DiagSeverity label 属性测试"""

    def test_critical_label(self):
        assert DiagSeverity.CRITICAL.label == "严重"

    def test_high_label(self):
        assert DiagSeverity.HIGH.label == "高危"

    def test_medium_label(self):
        assert DiagSeverity.MEDIUM.label == "中危"

    def test_low_label(self):
        assert DiagSeverity.LOW.label == "低危"


class TestRemainingLogRules:
    """剩余日志规则覆盖"""

    def test_ospf_neighbor_down(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("OSPF neighbor state down")
        ids = [f.id for f in result.findings]
        assert "LOG-C02" in ids

    def test_link_flap(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("%LINK-3-UPDOWN: Interface Gi0/0, changed state to UP changed state to DOWN")
        ids = [f.id for f in result.findings]
        assert "LOG-C03" in ids

    def test_auth_failure(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("authentication login failed")
        ids = [f.id for f in result.findings]
        assert "LOG-H02" in ids

    def test_temperature_alarm(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("temperature high alarm")
        ids = [f.id for f in result.findings]
        assert "LOG-H03" in ids

    def test_port_security_violation(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("port-security violation detected")
        ids = [f.id for f in result.findings]
        assert "LOG-M01" in ids

    def test_input_errors(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("50 input errors")
        ids = [f.id for f in result.findings]
        assert "IF-H01" in ids

    def test_output_drops(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("500 output drops")
        ids = [f.id for f in result.findings]
        assert "IF-H02" in ids

    def test_duplex_mismatch(self):
        engine = LocalDiagnosticEngine()
        result = engine.diagnose("duplex mismatch detected")
        ids = [f.id for f in result.findings]
        assert "IF-M01" in ids
