#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地运行时诊断引擎
从巡检报告、日志、配置中提取结构化异常信息，供AI精审使用
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


class DiagSeverity(Enum):
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


@dataclass
class DiagFinding:
    id: str
    severity: DiagSeverity
    category: str          # 分类：cpu/memory/interface/log/config
    title: str
    issue: str
    evidence: str          # 原始证据文本
    layer: str = ""        # OSI层级（如 Layer1/2/3）
    suggestion: str = ""   # 处置建议


@dataclass
class DiagResult:
    findings: List[DiagFinding] = field(default_factory=list)
    source_type: str = ""   # backup/report/log/compliance
    parse_time_ms: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DiagSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DiagSeverity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DiagSeverity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DiagSeverity.LOW)

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def verdict(self) -> str:
        if self.critical_count > 0:
            return "严重异常"
        if self.high_count >= 2:
            return "高危"
        if self.high_count > 0 or self.medium_count > 2:
            return "异常"
        if self.medium_count > 0 or self.low_count > 0:
            return "轻微异常"
        return "正常"

    def to_ai_prompt_context(self) -> str:
        """生成供AI使用的精简异常摘要（仅异常列表，无冗余证据/建议）"""
        if not self.findings:
            return "本地预诊断未发现明显异常。"

        lines = [f"本地预诊断发现 {self.total_findings} 个异常（结论: {self.verdict}）:"]
        for sev in [DiagSeverity.CRITICAL, DiagSeverity.HIGH, DiagSeverity.MEDIUM, DiagSeverity.LOW]:
            sev_items = [f for f in self.findings if f.severity == sev]
            if not sev_items:
                continue
            lines.append(f"\n{sev.label}:")
            for f in sev_items:
                layer_tag = f"[{f.layer}]" if f.layer else ""
                lines.append(f"- [{f.id}]{layer_tag} {f.title}: {f.issue}")

        return "\n".join(lines)

    def extract_relevant_context(self, content: str, context_lines: int = 8,
                                  max_total_lines: int = 200) -> str:
        """
        根据异常证据在原文中的位置，精准提取周边上下文行。
        不发送全文，只返回异常附近的片段，大幅减少token消耗。

        策略：用证据整行做精确子串匹配（非拆词），每证据最多匹配3行，
        总提取行数上限 max_total_lines，超出时降级为证据摘要。

        Args:
            content: 原始巡检报告/日志内容
            context_lines: 每个匹配行前后保留的行数
            max_total_lines: 提取总行数上限

        Returns:
            拼接后的精准上下文片段
        """
        if not self.findings or not content:
            return ""

        content_lines = content.splitlines()
        total_lines = len(content_lines)

        # 收集每个异常证据对应的行号（精确匹配，每证据最多3行）
        matched_line_sets = []
        for f in self.findings:
            if not f.evidence:
                continue
            evidence = f.evidence.strip()
            if not evidence:
                continue

            # 策略1：用证据文本整行做子串匹配（精确）
            line_set = set()
            for i, line in enumerate(content_lines):
                if evidence.lower() in line.lower():
                    line_set.add(i)
                    if len(line_set) >= 3:
                        break

            # 策略2：若精确匹配失败，取证据中长度>=6的子串匹配
            if not line_set:
                for sub in [evidence[i:i+20] for i in range(0, min(len(evidence), 60), 10)]:
                    if len(sub) < 6:
                        continue
                    for i, line in enumerate(content_lines):
                        if sub.lower() in line.lower():
                            line_set.add(i)
                            if len(line_set) >= 2:
                                break
                    if line_set:
                        break

            if line_set:
                matched_line_sets.append(line_set)

        if not matched_line_sets:
            # 无法精准定位，降级为证据摘要
            evidence_parts = []
            for f in self.findings:
                if f.evidence:
                    evidence_parts.append(f"[{f.id}] {f.evidence[:120]}")
            return "关键证据:\n" + "\n".join(evidence_parts)

        # 合并所有行号，应用 context_lines 扩展
        all_matched = set()
        for ls in matched_line_sets:
            for ln in ls:
                for j in range(max(0, ln - context_lines),
                               min(total_lines, ln + context_lines + 1)):
                    all_matched.add(j)

        # 总行数超限则降级
        if len(all_matched) > max_total_lines:
            evidence_parts = []
            for f in self.findings:
                if f.evidence:
                    evidence_parts.append(f"[{f.id}] {f.evidence[:120]}")
            return "关键证据:\n" + "\n".join(evidence_parts)

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
                parts.append("\n...（省略中间无关内容）...\n")
            parts.append("\n".join(content_lines[s:e + 1]))

        return "\n".join(parts)

    def to_summary_text(self) -> str:
        """生成人类可读的摘要"""
        if not self.findings:
            return "## 本地预诊断结果\n\n✅ 未发现明显异常。"

        lines = [f"## 本地预诊断结果（结论：{self.verdict}）"]
        c, h, m, l = self.critical_count, self.high_count, self.medium_count, self.low_count
        lines.append(f"| 严重 | 高危 | 中危 | 低危 | 合计 |")
        lines.append(f"| :--: | :--: | :--: | :--: | :--: |")
        lines.append(f"| {c} | {h} | {m} | {l} | {self.total_findings} |")
        lines.append("")

        sev_icons = {
            DiagSeverity.CRITICAL: "🔴",
            DiagSeverity.HIGH: "🟠",
            DiagSeverity.MEDIUM: "🟡",
            DiagSeverity.LOW: "🟢",
        }
        for sev in [DiagSeverity.CRITICAL, DiagSeverity.HIGH, DiagSeverity.MEDIUM, DiagSeverity.LOW]:
            sev_items = [f for f in self.findings if f.severity == sev]
            if not sev_items:
                continue
            icon = sev_icons[sev]
            lines.append(f"### {icon} {sev.label}（{len(sev_items)}项）")
            for f in sev_items:
                layer_tag = f"[{f.layer}]" if f.layer else ""
                lines.append(f"- **[{f.id}]** {layer_tag} {f.title}")
                lines.append(f"  - 问题：{f.issue}")
                if f.suggestion:
                    lines.append(f"  - 建议：{f.suggestion}")
                lines.append("")

        return "\n".join(lines)


# ──────────────────────────────────────────────
# 运行时状态诊断规则
# ──────────────────────────────────────────────

# CPU 过载检测
CPU_RULES: List[Dict[str, Any]] = [
    {
        "id": "CPU-C01",
        "severity": DiagSeverity.CRITICAL,
        "title": "CPU利用率持续过高",
        "pattern": re.compile(
            r"(?:cpu|CPU|Cpu)\s*(?:utilization|usage|利用率)?\s*[:\s]*(?:five\s*min|5\s*min|one\s*min|1\s*min|max|average)?\s*[:\s]*(\d{2,3})\s*%",
            re.IGNORECASE
        ),
        "threshold": 90,
        "issue_tpl": "CPU利用率达到{value}%，超过严重阈值90%",
        "suggestion": "检查是否有异常进程或流量风暴；考虑启用QoS限速或升级设备",
        "layer": "系统",
    },
    {
        "id": "CPU-H01",
        "severity": DiagSeverity.HIGH,
        "title": "CPU利用率偏高",
        "pattern": re.compile(
            r"(?:cpu|CPU|Cpu)\s*(?:utilization|usage|利用率)?\s*[:\s]*(?:five\s*min|5\s*min|one\s*min|1\s*min|max|average)?\s*[:\s]*(\d{2,3})\s*%",
            re.IGNORECASE
        ),
        "threshold": 70,
        "issue_tpl": "CPU利用率为{value}%，超过警戒阈值70%",
        "suggestion": "关注CPU趋势，排查是否存在异常流量或环路",
        "layer": "系统",
    },
]

# 内存告警检测
MEMORY_RULES: List[Dict[str, Any]] = [
    {
        "id": "MEM-C01",
        "severity": DiagSeverity.CRITICAL,
        "title": "内存利用率严重不足",
        "pattern": re.compile(
            r"(?:memory|mem|内存)\s*(?:utilization|usage|利用率|used)?\s*[:\s]*(\d{2,3})\s*%",
            re.IGNORECASE
        ),
        "threshold": 90,
        "issue_tpl": "内存利用率达到{value}%，可能导致设备不稳定",
        "suggestion": "检查内存泄漏进程，考虑重启或升级内存",
        "layer": "系统",
    },
    {
        "id": "MEM-H01",
        "severity": DiagSeverity.HIGH,
        "title": "内存利用率偏高",
        "pattern": re.compile(
            r"(?:memory|mem|内存)\s*(?:utilization|usage|利用率|used)?\s*[:\s]*(\d{2,3})\s*%",
            re.IGNORECASE
        ),
        "threshold": 80,
        "issue_tpl": "内存利用率为{value}%",
        "suggestion": "持续监控内存趋势，排查是否存在内存泄漏",
        "layer": "系统",
    },
]

# 接口异常检测
INTERFACE_RULES: List[Dict[str, Any]] = [
    {
        "id": "IF-C01",
        "severity": DiagSeverity.CRITICAL,
        "title": "接口链路Down",
        "pattern": re.compile(
            r"(\S+)\s+(?:is\s+)?(?:down|administratively\s+down|err-disabled)",
            re.IGNORECASE
        ),
        "exclude_pattern": re.compile(r"administratively\s+down", re.IGNORECASE),
        "issue_tpl": "接口 {value} 处于Down状态",
        "suggestion": "检查物理链路、光模块、对端设备状态",
        "layer": "Layer1",
    },
    {
        "id": "IF-C02",
        "severity": DiagSeverity.CRITICAL,
        "title": "接口存在大量CRC错误",
        "pattern": re.compile(
            r"(\d+)\s+(?:CRC|crc|input\s+errors)",
            re.IGNORECASE
        ),
        "threshold": 100,
        "issue_tpl": "检测到 {value} 个CRC错误，可能存在物理层故障",
        "suggestion": "检查网线/光模块/接口速率和双工协商",
        "layer": "Layer1",
    },
    {
        "id": "IF-H01",
        "severity": DiagSeverity.HIGH,
        "title": "接口存在输入错误",
        "pattern": re.compile(
            r"(\d+)\s+input\s+errors",
            re.IGNORECASE
        ),
        "threshold": 10,
        "issue_tpl": "接口存在 {value} 个输入错误",
        "suggestion": "检查链路质量，排查是否存在CRC或帧错误",
        "layer": "Layer1",
    },
    {
        "id": "IF-H02",
        "severity": DiagSeverity.HIGH,
        "title": "接口存在丢包",
        "pattern": re.compile(
            r"(\d+)\s+(?:output\s+drops|input\s+drops|丢包|drops)",
            re.IGNORECASE
        ),
        "threshold": 100,
        "issue_tpl": "接口存在 {value} 个丢包",
        "suggestion": "检查接口带宽利用率，考虑启用QoS或扩容链路",
        "layer": "Layer2",
    },
    {
        "id": "IF-M01",
        "severity": DiagSeverity.MEDIUM,
        "title": "接口双工不匹配",
        "pattern": re.compile(
            r"(?:duplex|Duplex)\s*(?:mismatch|不匹配)",
            re.IGNORECASE
        ),
        "issue_tpl": "检测到双工不匹配",
        "suggestion": "将两端接口设置为相同的双工模式，建议两端均设为auto",
        "layer": "Layer1",
    },
]

# 日志告警检测
LOG_RULES: List[Dict[str, Any]] = [
    {
        "id": "LOG-C01",
        "severity": DiagSeverity.CRITICAL,
        "title": "BGP邻居状态异常",
        "pattern": re.compile(
            r"(?:BGP|bgp)\s+(?:neighbor|邻居|peer|session)\s+(?:is\s+|状态\s+)?(?:down|Idle|Active|Connect)",
            re.IGNORECASE
        ),
        "issue_tpl": "BGP邻居状态异常",
        "suggestion": "检查BGP邻居配置、AS号、TCP 179端口连通性、ACL规则",
        "layer": "Layer3",
    },
    {
        "id": "LOG-C02",
        "severity": DiagSeverity.CRITICAL,
        "title": "OSPF邻居状态变化",
        "pattern": re.compile(
            r"(?:OSPF|ospf)\s+(?:neighbor|邻居|nbr)\s+(?:state\s+)?(?:down|init|2-way\s*→\s*init)",
            re.IGNORECASE
        ),
        "issue_tpl": "OSPF邻居状态变化，路由可能受影响",
        "suggestion": "检查OSPF区域配置、Hello/Dead间隔、接口MTU",
        "layer": "Layer3",
    },
    {
        "id": "LOG-C03",
        "severity": DiagSeverity.CRITICAL,
        "title": "接口频繁Up/Down震荡",
        "pattern": re.compile(
            r"(?:%LINK|LINK|接口).*(?:changed\s+state|UP|DOWN).*(?:changed\s+state|UP|DOWN)",
            re.IGNORECASE
        ),
        "issue_tpl": "接口存在频繁Up/Down震荡",
        "suggestion": "检查物理链路稳定性、光功率、端口协商",
        "layer": "Layer1",
    },
    {
        "id": "LOG-H01",
        "severity": DiagSeverity.HIGH,
        "title": "STP拓扑变更",
        "pattern": re.compile(
            r"(?:spanning-tree|STP|stp).*(?:topology\s+change|TCN|拓扑变更)",
            re.IGNORECASE
        ),
        "issue_tpl": "检测到STP拓扑变更",
        "suggestion": "排查网络中是否存在链路震荡或新设备接入",
        "layer": "Layer2",
    },
    {
        "id": "LOG-H02",
        "severity": DiagSeverity.HIGH,
        "title": "认证失败日志",
        "pattern": re.compile(
            r"(?:authentication|认证|login)\s+(?:fail|failed|失败|denied|拒绝)",
            re.IGNORECASE
        ),
        "issue_tpl": "检测到认证失败事件",
        "suggestion": "排查是否为暴力破解尝试或配置错误",
        "layer": "应用层",
    },
    {
        "id": "LOG-H03",
        "severity": DiagSeverity.HIGH,
        "title": "温度告警",
        "pattern": re.compile(
            r"(?:temperature|温度|thermal)\s*(?:high|alarm|告警|over)",
            re.IGNORECASE
        ),
        "issue_tpl": "设备温度过高",
        "suggestion": "检查风扇状态、机房空调、设备通风",
        "layer": "硬件",
    },
    {
        "id": "LOG-M01",
        "severity": DiagSeverity.MEDIUM,
        "title": "端口安全违规",
        "pattern": re.compile(
            r"(?:port-security|端口安全|secure-violation|violation)",
            re.IGNORECASE
        ),
        "issue_tpl": "检测到端口安全违规",
        "suggestion": "检查是否有未授权设备接入",
        "layer": "Layer2",
    },
]


def _check_threshold_rules(content: str, rules: List[Dict[str, Any]], category: str) -> List[DiagFinding]:
    """通用阈值规则检查"""
    findings = []
    for rule in rules:
        pattern = rule["pattern"]
        for match in pattern.finditer(content):
            # 对于administratively down排除
            if "exclude_pattern" in rule and rule["exclude_pattern"].search(match.group(0)):
                continue

            threshold = rule.get("threshold")
            if threshold is not None:
                # 提取数值
                value_str = None
                for g in match.groups():
                    if g and g.isdigit():
                        value_str = g
                        break
                if value_str is None:
                    continue
                value = int(value_str)
                if value < threshold:
                    continue
                issue = rule["issue_tpl"].format(value=value)
                evidence = match.group(0).strip()
            else:
                # 无阈值，匹配即触发
                issue = rule["issue_tpl"].format(value=match.group(1) if match.lastindex else match.group(0))
                evidence = match.group(0).strip()

            finding = DiagFinding(
                id=rule["id"],
                severity=rule["severity"],
                category=category,
                title=rule["title"],
                issue=issue,
                evidence=evidence[:200],
                layer=rule.get("layer", ""),
                suggestion=rule.get("suggestion", ""),
            )
            findings.append(finding)

    return findings


def _deduplicate_findings(findings: List[DiagFinding]) -> List[DiagFinding]:
    """去重：相同ID只保留一条"""
    seen = set()
    result = []
    for f in findings:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f)
    return result


class LocalDiagnosticEngine:
    """本地运行时诊断引擎：从巡检报告/日志中提取结构化异常"""

    def __init__(self):
        self._cpu_rules = CPU_RULES
        self._mem_rules = MEMORY_RULES
        self._if_rules = INTERFACE_RULES
        self._log_rules = LOG_RULES

    def diagnose(self, content: str, source_type: str = "report") -> DiagResult:
        """
        对输入内容进行运行时异常诊断

        Args:
            content: 巡检报告/日志/配置内容
            source_type: 来源类型（backup/report/log/compliance）

        Returns:
            DiagResult 结构化诊断结果
        """
        import time
        start = time.time()

        all_findings: List[DiagFinding] = []

        # CPU检查
        all_findings.extend(_check_threshold_rules(content, self._cpu_rules, "cpu"))

        # 内存检查
        all_findings.extend(_check_threshold_rules(content, self._mem_rules, "memory"))

        # 接口检查
        all_findings.extend(_check_threshold_rules(content, self._if_rules, "interface"))

        # 日志告警检查
        all_findings.extend(_check_threshold_rules(content, self._log_rules, "log"))

        # 去重
        all_findings = _deduplicate_findings(all_findings)

        elapsed_ms = int((time.time() - start) * 1000)

        return DiagResult(
            findings=all_findings,
            source_type=source_type,
            parse_time_ms=elapsed_ms,
        )


def run_local_diagnostic(content: str, source_type: str = "report") -> DiagResult:
    """便捷函数：执行本地运行时诊断"""
    engine = LocalDiagnosticEngine()
    return engine.diagnose(content, source_type)


if __name__ == "__main__":
    # 测试
    test_report = """
    === 设备巡检报告 ===
    设备IP: 192.168.1.1
    厂商: 华为

    --- CPU ---
    CPU utilization for five minutes: 85%
    CPU utilization for one minute: 92%

    --- 内存 ---
    Memory utilization: 78%

    --- 接口状态 ---
    GigabitEthernet0/0/1 is up
    GigabitEthernet0/0/2 is down
    GigabitEthernet0/0/3 is up
     1500 input errors, 200 CRC

    --- 日志 ---
    %LINK-3-UPDOWN: Interface GigabitEthernet0/0/2, changed state to down
    %BGP-5-ADJCHANGE: neighbor 10.0.0.2 Down
    %SPANTREE-2-TOPOLOGY_CHANGE: Topology change detected
    """

    engine = LocalDiagnosticEngine()
    result = engine.diagnose(test_report, "report")

    print("=" * 60)
    print(f"  本地运行时诊断引擎测试")
    print(f"  来源: {result.source_type}")
    print(f"  耗时: {result.parse_time_ms}ms")
    print(f"  结论: {result.verdict}")
    print(f"  发现: {result.total_findings} (C:{result.critical_count} H:{result.high_count} M:{result.medium_count} L:{result.low_count})")
    print("=" * 60)

    for f in result.findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    问题: {f.issue}")
        print(f"    证据: {f.evidence[:80]}")
        print()

    print("\n--- AI Prompt Context ---")
    print(result.to_ai_prompt_context())
