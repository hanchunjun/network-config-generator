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
