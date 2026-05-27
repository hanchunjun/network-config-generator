import os
import sys
import json
import time
import glob as glob_mod
import ssl
import socket
import subprocess
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
import certifi
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QTextEdit, QMessageBox, QProgressBar,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QDialogButtonBox, QCheckBox, QMenu,
                               QAction, QAbstractItemView, QTabWidget,
                               QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

from src.utils.resource_path import resource_path, get_app_dir, get_config_path, get_single_dir
from src.core.secure_config import SecureConfigFile
from src.core.local_audit_engine import LocalAuditEngine, AuditResult, Severity
from src.core.local_diagnostic_engine import LocalDiagnosticEngine, DiagResult, DiagSeverity
from src.core.theme_engine import ThemeEngine
from src.ui.system_settings_page import get_active_ai_config

SCRIPTS_DIR = resource_path("scripts")
sys.path.insert(0, SCRIPTS_DIR)

AI_CONFIG_PATH = get_config_path("config/ai_config.json")
SINGLE_DEVICES_PATH = os.path.join(get_single_dir(), "single_devices.json")

VENDORS = ["锐捷", "华为", "H3C", "思科"]
DEVICE_TYPES = ["核心交换机", "汇聚交换机", "接入交换机", "路由器", "防火墙", "AC控制器", "AP"]
PROTOCOLS = ["ssh", "telnet"]

DEV_TYPE_MAP = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

TEST_CMD_MAP = {
    "锐捷": ["show version", "show clock"],
    "华为": ["display version", "display clock"],
    "H3C": ["display version", "display clock"],
    "思科": ["show version", "show clock"]
}

INSPECT_EXCEPTION_KEYS = [
    "Down", "Error", "Warning", "CPU", "内存", "过载", "告警", "故障",
    "CRC", "reset", "spanning-tree", "邻居", "会话"
]

INSPECT_TYPE_NORMALIZE = {
    "核心交换机": "交换机", "汇聚交换机": "交换机", "接入交换机": "交换机",
    "交换机": "交换机", "路由器": "路由器", "防火墙": "交换机",
    "AC控制器": "交换机", "AP": "交换机",
}

INSPECT_DEFAULT_CMDS = ["show version", "show ip interface brief", "show cpu", "show memory"]

INSPECT_BASE_CMD_LIB: Dict[str, Dict[str, List[str]]] = {
    "锐捷": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip route", "show cpu", "show memory", "show logging"]
    },
    "华为": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "H3C": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "思科": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip interface brief", "show ip route", "show cpu", "show memory", "show logging"]
    }
}

FULL_CONFIG_CMD_MAP: Dict[str, str] = {
    "锐捷": "show running-config",
    "华为": "display current-configuration",
    "H3C": "display current-configuration",
    "思科": "show running-config"
}

STATUS_ICONS = {"success": "✅", "failed": "❌", "pending": "⚪"}
TAB_LOG = 0
TAB_BACKUP = 1
TAB_REPORT = 2
TAB_DIAGNOSIS = 3
TAB_COMPLIANCE = 4

COMPLIANCE_PROMPT = """{reviewer_rules}

---
设备IP: {device_ip}
配置:
{config_content}
"""

COMPLIANCE_API_TIMEOUT = 120
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 10]
MAX_RULES_LENGTH = 2000

RATE_LIMIT_MAX_RETRIES = 3
RATE_LIMIT_BACKOFF_BASE = 30
PROBE_TIMEOUT = 15


class ComplianceCheckThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    local_result_signal = pyqtSignal(str)

    def __init__(self, config_content: str, device_ip: str, ai_config: Dict[str, Any],
                 vendor_hint: str = ""):
        super().__init__()
        self.config_content = config_content
        self.device_ip = device_ip
        self.ai_config = ai_config
        self.vendor_hint = vendor_hint
        self._session = requests.Session()
        self._session.headers.update({
            "Connection": "keep-alive",
            "User-Agent": "NetOps-ComplianceChecker/2.0"
        })
        self._session.verify = certifi.where()
        self._local_result = None

    def _get_base_url(self) -> str:
        return self.ai_config['base_url'].rstrip('/')

    def _get_auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.ai_config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _run_local_audit(self) -> AuditResult:
        engine = LocalAuditEngine()
        result = engine.audit(
            config_text=self.config_content,
            device_ip=self.device_ip,
            vendor_hint=self.vendor_hint
        )
        return result

    def _format_local_result_for_display(self, result: AuditResult) -> str:
        SEV_CN = {
            Severity.CRITICAL: ("严重", "\U0001f534"),
            Severity.HIGH:    ("高危", "\U0001f7e0"),
            Severity.MEDIUM:  ("中危", "\U0001f7e1"),
            Severity.LOW:     ("低危", "\U0001f7e2"),
        }
        lines = []
        lines.append(f"## 本地合规审计结果")
        lines.append(f"- 设备IP：{self.device_ip}")
        lines.append(f"- 厂商：{result.vendor}")
        lines.append(f"- 审计耗时：{result.audit_time_ms}ms")
        lines.append("")
        verdict_icon = {"不通过": "\u274c", "警告": "\u26a0\ufe0f", "通过": "\u2705"}.get(result.verdict, "")
        lines.append(f"### {verdict_icon} 审计结论：{result.verdict}")
        c, h, m, l = result.critical_count, result.high_count, result.medium_count, result.low_count
        total = result.total_findings
        if total == 0:
            lines.append("\n> \u2705 未发现安全风险项，配置符合基本合规要求。")
        else:
            summary_parts = []
            if c > 0:
                summary_parts.append(f"\U0001f534 **{c}项严重风险** — 需立即处理")
            if h > 0:
                summary_parts.append(f"\U0001f7e0 **{h}项高危风险** — 建议尽快修复")
            if m > 0:
                summary_parts.append(f"\U0001f7e1 **{m}项中危风险** — 计划修复")
            if l > 0:
                summary_parts.append(f"\U0001f7e2 **{l}项低危风险** — 可后续优化")
            lines.append("")
            lines.append("> **发现摘要：** " + "；".join(summary_parts))
            lines.append("")
            sev_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
            for sev in sev_order:
                sev_findings = [f for f in result.findings if f.severity == sev]
                if not sev_findings:
                    continue
                cn_label, icon = SEV_CN[sev]
                lines.append(f"#### {icon} {cn_label}级别 ({len(sev_findings)}项)")
                lines.append("---")
                for i, f in enumerate(sev_findings, 1):
                    lines.append(f"**{i}. {f.title}** `{f.id}`")
                    loc = f"（配置位置：{f.location}）" if f.location else ""
                    if f.line_number > 0:
                        loc += f" 第{f.line_number}行"
                    lines.append(f"   - 问题：{f.issue}")
                    if loc:
                        lines.append(f"   - 位置：{loc}")
                    lines.append(f"   - 修复建议：{f.fix}")
                    lines.append("")
        lines.append("---")
        lines.append(f"| 严重 | 高危 | 中危 | 低危 | 合计 |")
        lines.append(f"| :--: | :--: | :--: | :--: | :--: |")
        lines.append(f"| {c} | {h} | {m} | {l} | {total} |")
        lines.append(f"\n> **审计结论：{verdict_icon} {result.verdict}**")
        return "\n".join(lines)

    def _probe_rate_limit(self) -> tuple:
        url = f"{self._get_base_url()}/chat/completions"
        probe_payload = {
            "model": self.ai_config["model"],
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 3
        }
        try:
            resp = self._session.post(url, headers=self._get_auth_headers(),
                                      json=probe_payload, timeout=PROBE_TIMEOUT)
            if resp.status_code == 200:
                return True, None
            elif resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_sec = int(retry_after) if retry_after and retry_after.isdigit() else RATE_LIMIT_BACKOFF_BASE
                return False, ("rate_limited", wait_sec, resp.text[:150])
            else:
                return False, ("http_error", resp.status_code, resp.text[:100])
        except requests.exceptions.ConnectionError as e:
            return False, ("conn_error", str(e)[:120])
        except requests.exceptions.Timeout:
            return False, ("timeout", None)
        except Exception as e:
            return False, ("unknown", f"{type(e).__name__}: {str(e)[:100]}")

    def _build_ai_refinement_payload(self, local_result: AuditResult) -> tuple:
        reviewer_path = resource_path(os.path.join("agents", "network-config-reviewer.md"))
        if os.path.exists(reviewer_path):
            with open(reviewer_path, "r", encoding="utf-8") as f:
                reviewer_rules = f.read()
        else:
            reviewer_rules = ""

        local_context = local_result.to_ai_prompt_context()

        # 精准提取问题配置周边上下文（替代全文截断，减少token）
        relevant_context = ""
        if local_result.total_findings > 0:
            relevant_context = local_result.extract_relevant_context(self.config_content, context_lines=6)

        prompt = (
            f"你是一名网络配置合规审计专家。请根据以下设备配置进行审计。\n\n"
            f"## 本地预检结果\n"
            f"{local_context}\n\n"
            f"## 设备信息\n"
            f"设备IP: {self.device_ip}\n"
            f"厂商: {local_result.vendor}\n"
        )
        if relevant_context:
            prompt += (
                f"\n## 问题相关配置上下文（精准提取）\n"
                f"```\n{relevant_context}\n```\n"
            )
        prompt += (
            f"\n## 任务要求\n"
            f"基于上述本地预检发现的问题：\n"
            f"1. 验证每个发现是否准确（排除误报）\n"
            f"2. 补充本地规则可能遗漏的其他问题\n"
            f"3. 为每个问题提供具体的修复命令\n"
            f"4. 使用标准格式输出最终审计报告，包含严重等级标识"
        )

        url = f"{self._get_base_url()}/chat/completions"
        system_prompt = reviewer_rules if reviewer_rules else "你是网络配置安全审计专家。负责验证审计发现并生成最终的中文审计报告。"
        payload = {
            "model": self.ai_config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }

        payload_size = len(json.dumps(payload).encode('utf-8'))
        return url, payload, payload_size

    def _handle_429(self, resp, attempt: int) -> tuple:
        retry_after = resp.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            wait_sec = int(retry_after)
        else:
            wait_sec = RATE_LIMIT_BACKOFF_BASE * (2 ** (attempt - 1))
        wait_sec = min(wait_sec, 120)
        is_last = attempt >= RATE_LIMIT_MAX_RETRIES
        if is_last:
            msg = (f"API request rate limited (retried {RATE_LIMIT_MAX_RETRIES} times)\n\n"
                   f"Service returned: HTTP 429 Too Many Requests\n"
                   f"Suggestions:\n"
                   f"1. Wait {wait_sec}s before retrying\n"
                   f"2. Check API quota\n"
                   f"3. Contact provider about limits\n"
                   f"4. Try another AI model config")
            return False, msg
        self.progress_signal.emit(f"API rate limited (429), waiting {wait_sec}s... (attempt {attempt}/{RATE_LIMIT_MAX_RETRIES})")
        time.sleep(wait_sec)
        return True, None

    def _classify_error(self, error: Exception, attempt: int, url: str,
                        status_code: int = 0) -> str:
        error_msg = str(error).lower()

        if status_code == 429 or "429" in error_msg or "too_many_requests" in error_msg or "rate limit" in error_msg:
            if attempt < RATE_LIMIT_MAX_RETRIES:
                return "API rate limited (429), waiting to retry..."
            return ("API request rate limited (retried %d times)\n\n"
                    "This is the API provider rate limit, not a program bug.\n"
                    "Suggestion: retry later or contact provider about quota") % RATE_LIMIT_MAX_RETRIES

        if "remote end closed" in error_msg or "connection reset" in error_msg or "broken pipe" in error_msg:
            if attempt < MAX_RETRIES:
                return f"Connection reset by server (attempt {attempt}), retrying..."
            return ("Connection refused after %d retries\n\n"
                    "Possible causes:\n"
                    "1. Provider gateway has size limits\n"
                    "2. Rate limit triggered connection close\n"
                    "3. Contact provider or try other AI config") % MAX_RETRIES

        if "timeout" in error_msg or "timed out" in error_msg:
            if attempt < MAX_RETRIES:
                return f"Request timeout (attempt {attempt}), retrying..."
            return f"Request timed out (waited {COMPLIANCE_API_TIMEOUT}s x {MAX_RETRIES})"

        if "connection refused" in error_msg:
            return f"Cannot connect to AI service (connection refused)\nURL: {url}"

        if "name or service not known" in error_msg or "getaddrinfo failed" in error_msg:
            return f"DNS resolution failed\nURL: {url}"

        if "401" in error_msg or "unauthorized" in error_msg or status_code == 401:
            return "Authentication failed: invalid or expired API Key"

        if "404" in error_msg or "not found" in error_msg or status_code == 404:
            return f"Model not found: {self.ai_config.get('model', 'unknown')}"

        return f"Request failed (attempt {attempt}): {type(error).__name__}: {error}"

    def run(self):
        debug_fp = os.path.join(get_app_dir(), "logs", "compliance_debug.log")
        def _dbg(msg):
            try:
                with open(debug_fp, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}\n")
            except Exception:
                pass

        try:
            _dbg("THREAD START")
            self.progress_signal.emit("Layer 1/2: Running local audit engine...")
            _dbg("after first progress_signal emit")
            t0 = time.time()

            local_result = self._run_local_audit()
            _dbg(f"local_audit done: {local_result.total_findings} findings")
            self._local_result = local_result

            local_time_ms = int((time.time() - t0) * 1000)
            self.progress_signal.emit(
                f"Local audit complete ({local_time_ms}ms): "
                f"{local_result.total_findings} findings, "
                f"Verdict={local_result.verdict}"
            )

            local_display = self._format_local_result_for_display(local_result)
            self.local_result_signal.emit(local_display)

            needs_ai = (
                local_result.critical_count > 0 or
                local_result.high_count >= 2 or
                (local_result.high_count > 0 and local_result.medium_count > 1)
            )
            _dbg(f"needs_ai={needs_ai} (C:{local_result.critical_count} H:{local_result.high_count} M:{local_result.medium_count})")

            if not needs_ai:
                self.progress_signal.emit(
                    f"本地审计完成：{local_result.verdict} — 配置安全，无需AI精审"
                )
                combined_report = (
                    f"# 网络配置合规审计报告\n\n"
                    f"## 设备：{self.device_ip} | 厂商：{local_result.vendor}\n"
                    f"## 审计模式：本地规则引擎（配置安全，跳过AI精审）\n"
                    f"## 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(combined_report)
                return

            if not self.ai_config.get('base_url') or not self.ai_config.get('api_key'):
                self.progress_signal.emit(
                    "AI未配置 — 仅显示本地审计结果"
                )
                combined_report = (
                    f"# 网络配置合规审计报告\n\n"
                    f"## 设备：{self.device_ip} | 厂商：{local_result.vendor}\n"
                    f"## 审计模式：仅本地审计（AI未配置）\n"
                    f"## 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"> 提示：请在【⚙ 模型设置】中配置AI模型以启用AI精审功能\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(combined_report)
                return

            self.progress_signal.emit("Layer 2/2: Probing AI availability...")
            _dbg("probing AI...")
            probe_ok, probe_result = self._probe_rate_limit()
            _dbg(f"probe result: ok={probe_ok}, type={probe_result[0] if probe_result else 'None'}")

            if not probe_ok:
                ptype = probe_result[0]
                if ptype == "rate_limited":
                    _, wait_sec, detail = probe_result
                    self.progress_signal.emit(
                        f"AI rate limited - showing local results only (retry after ~{wait_sec}s)"
                    )
                elif ptype in ("conn_error", "timeout"):
                    self.progress_signal.emit(
                        f"AI unavailable ({ptype}) - showing local results only"
                    )
                else:
                    self.progress_signal.emit(
                        f"AI probe failed ({ptype}) - showing local results only"
                    )

                combined_report = (
                    f"# Network Configuration Compliance Report\n\n"
                    f"## Device: {self.device_ip} | Vendor: {local_result.vendor}\n"
                    f"## Audit Mode: Local Only (AI unavailable)\n"
                    f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"> Note: AI service unavailable. Results from local rule engine (~80%% coverage).\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(combined_report)
                return

            self.progress_signal.emit("Layer 2/2: Sending findings to AI for refinement...")
            url, payload, payload_size = self._build_ai_refinement_payload(local_result)
            headers = self._get_auth_headers()

            self.progress_signal.emit(
                f"Sending AI request ({payload_size/1024:.1f}KB, optimized from full config)..."
            )
            self.progress_signal.emit("⏳ 等待AI分析结果（最长120秒，请耐心等待）...")
            _dbg(f"sending AI request: {payload_size/1024:.1f}KB")

            last_error = None
            last_status_code = 0

            for rl_attempt in range(1, RATE_LIMIT_MAX_RETRIES + 1):
                try:
                    if rl_attempt > 1:
                        wait = RATE_LIMIT_BACKOFF_BASE * (2 ** (rl_attempt - 2))
                        wait = min(wait, 120)
                        self.progress_signal.emit(f"API rate limited, waiting {wait}s before retry...")
                        time.sleep(wait)

                    resp = self._session.post(url, headers=headers, json=payload,
                                              timeout=COMPLIANCE_API_TIMEOUT)
                    last_status_code = resp.status_code

                    if resp.status_code == 200:
                        ai_content = resp.json()["choices"][0]["message"]["content"]
                        combined_report = (
                            f"# 网络配置合规审计报告\n\n"
                            f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                            f"## 审计模式: 双层审计（本地规则 + AI精审）\n"
                            f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            f"--- 第一层：本地规则引擎（发现 {local_result.total_findings} 个问题）---\n"
                            f"{local_result.to_summary_text()}\n\n"
                            f"--- 第二层：AI精审分析 ---\n"
                            f"{ai_content}"
                        )
                        self.finished_signal.emit(combined_report)
                        return

                    elif resp.status_code == 429:
                        should_retry, msg = self._handle_429(resp, rl_attempt)
                        if not should_retry:
                            self.progress_signal.emit("AI服务限速 - 降级使用本地审计结果")
                            combined_report = (
                                f"# 网络配置合规审计报告\n\n"
                                f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                                f"## 审计模式: 仅本地审计（AI服务限速）\n"
                                f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                f"> 注意：AI精审阶段遇到API限速，仅显示本地审计结果。\n\n"
                                f"{local_display}"
                            )
                            self.finished_signal.emit(combined_report)
                            return
                        last_error = Exception(f"HTTP 429: {resp.text[:150]}")
                        continue

                    else:
                        last_error = Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
                        if resp.status_code in [401, 403, 404]:
                            self.progress_signal.emit(
                                f"AI服务错误 {resp.status_code} - 降级使用本地审计结果"
                            )
                            combined_report = (
                                f"# 网络配置合规审计报告\n\n"
                                f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                                f"## 审计模式: 仅本地审计（AI服务异常）\n"
                                f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                f"> 注意：AI精审阶段遇到HTTP {resp.status_code}错误，仅显示本地审计结果。\n\n"
                                f"{local_display}"
                            )
                            self.finished_signal.emit(combined_report)
                            return
                        self.progress_signal.emit(
                            self._classify_error(last_error, 1, url, resp.status_code)
                        )

                except requests.exceptions.Timeout:
                    self.progress_signal.emit(
                        f"AI请求超时（{COMPLIANCE_API_TIMEOUT}秒）- 降级使用本地审计结果"
                    )
                    combined_report = (
                        f"# 网络配置合规审计报告\n\n"
                        f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                        f"## 审计模式: 仅本地审计（AI服务超时）\n"
                        f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"> 注意：AI精审阶段超时未响应，仅显示本地审计结果。\n\n"
                        f"{local_display}"
                    )
                    self.finished_signal.emit(combined_report)
                    return

                except requests.exceptions.ConnectionError as ce:
                    self.progress_signal.emit(
                        f"AI服务连接失败 - 降级使用本地审计结果"
                    )
                    combined_report = (
                        f"# 网络配置合规审计报告\n\n"
                        f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                        f"## 审计模式: 仅本地审计（AI服务不可达）\n"
                        f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"> 注意：AI精审阶段连接失败({type(ce).__name__})，仅显示本地审计结果。\n\n"
                        f"{local_display}"
                    )
                    self.finished_signal.emit(combined_report)
                    return

                except Exception as e:
                    last_error = e
                    break

            self.progress_signal.emit("AI请求失败 - 返回本地审计结果")
            combined_report = (
                f"# 网络配置合规审计报告\n\n"
                f"## 设备: {self.device_ip} | 厂商: {local_result.vendor}\n"
                f"## 审计模式: 仅本地审计（AI服务故障）\n"
                f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"> AI精审失败。以下为本地规则引擎结果（覆盖率约80%）。\n\n"
                f"{local_display}"
            )
            self.finished_signal.emit(combined_report)

        except Exception as e:
            _dbg(f"EXCEPTION in run(): {type(e).__name__}: {str(e)[:200]}")
            if self._local_result:
                fallback = self._format_local_result_for_display(self._local_result)
                self.error_signal.emit(
                    f"审计异常（本地结果仍可用）：\n"
                    f"{type(e).__name__}: {str(e)}\n\n{fallback}"
                )
            else:
                self.error_signal.emit(f"合规检查异常: {type(e).__name__}: {str(e)}")
        finally:
            self._session.close()


class AIDiagnosticThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    local_result_signal = pyqtSignal(str)

    def __init__(self, content: str, source_type: str, ai_config: Dict[str, Any]):
        super().__init__()
        self.content = content
        self.source_type = source_type
        self.ai_config = ai_config
        self._session = requests.Session()
        self._session.headers.update({
            "Connection": "keep-alive",
            "User-Agent": "NetOps-DiagnosticEngine/2.0"
        })
        try:
            _cert_path = certifi.where()
            if os.path.isfile(_cert_path):
                self._session.verify = _cert_path
            else:
                self._session.verify = True
        except Exception:
            self._session.verify = True
        self._local_diag_result = None

    def _run_local_diagnostic(self) -> DiagResult:
        engine = LocalDiagnosticEngine()
        return engine.diagnose(self.content, self.source_type)

    def _build_local_only_report(self, local_result: DiagResult, source_hints: dict) -> str:
        return (
            f"# 故障诊断报告\n\n"
            f"## 数据来源: {source_hints.get(self.source_type, self.source_type)}\n"
            f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"## 诊断模式: 本地运行时诊断（AI不可用，降级输出）\n\n"
            f"> 注意：AI精审阶段不可用，以下为本地运行时诊断结果。\n\n"
            f"{local_result.to_summary_text()}"
        )

    def run(self):
        debug_fp = os.path.join(get_app_dir(), "logs", "diagnosis_debug.log")
        def _dbg(msg):
            try:
                with open(debug_fp, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}\n")
            except Exception:
                pass

        try:
            _dbg("THREAD START (v2 dual-layer)")

            # ── Layer 1: 本地运行时诊断 ──
            self.progress_signal.emit("Layer 1/2: 本地运行时诊断引擎启动...")
            t0 = time.time()
            local_result = self._run_local_diagnostic()
            self._local_diag_result = local_result
            local_ms = int((time.time() - t0) * 1000)
            _dbg(f"local_diagnostic done: {local_result.total_findings} findings, {local_ms}ms")

            self.progress_signal.emit(
                f"本地诊断完成 ({local_ms}ms): 发现 {local_result.total_findings} 个异常，结论: {local_result.verdict}"
            )

            # 发送本地诊断结果到UI
            local_display = local_result.to_summary_text()
            self.local_result_signal.emit(local_display)

            # ── 判断是否需要AI精审 ──
            needs_ai = (
                local_result.critical_count > 0 or
                local_result.high_count >= 2 or
                (local_result.high_count > 0 and local_result.medium_count > 1)
            )
            _dbg(f"needs_ai={needs_ai} (C:{local_result.critical_count} H:{local_result.high_count} M:{local_result.medium_count})")

            if not needs_ai and local_result.total_findings == 0:
                # 无异常，直接返回本地结果
                self.progress_signal.emit("本地诊断未发现异常，跳过AI精审")
                report = (
                    f"# 故障诊断报告\n\n"
                    f"## 数据来源: {self.source_type}\n"
                    f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 诊断模式: 本地运行时诊断（未发现异常，跳过AI精审）\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
                return

            if not self.ai_config.get('base_url') or not self.ai_config.get('api_key'):
                self.progress_signal.emit("AI未配置 — 仅显示本地诊断结果")
                report = (
                    f"# 故障诊断报告\n\n"
                    f"## 数据来源: {self.source_type}\n"
                    f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 诊断模式: 仅本地诊断（AI未配置）\n\n"
                    f"> 提示：请在【⚙ 模型设置】中配置AI模型以启用AI精审功能\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
                return

            # ── Layer 2: AI精审 ──
            self.progress_signal.emit("Layer 2/2: 调用AI进行深度故障诊断...")

            troubleshooter_path = resource_path(os.path.join("agents", "network-troubleshooter.md"))
            if os.path.exists(troubleshooter_path):
                with open(troubleshooter_path, "r", encoding="utf-8") as f:
                    system_prompt = f.read()
                _dbg(f"agent file loaded, len={len(system_prompt)}")
            else:
                system_prompt = (
                    "你是资深网络工程师，专精于结构化故障排查。"
                    "通过OSI分层逐层诊断网络问题，生成包含证据和后续步骤的根本原因摘要。"
                )
                _dbg("agent file NOT found, using fallback prompt")

            source_hints = {
                "backup": "以下是一台网络设备的配置备份文件（running-config），请分析其中可能存在的故障隐患：",
                "report": "以下是一份网络设备巡检报告，请分析其中的异常指标和潜在故障风险：",
                "compliance": "以下是一份合规审计报告，请对发现的问题进行二次精审，补充遗漏的故障诊断：",
                "log": "以下是设备巡检/操作的执行日志，请根据日志内容进行故障诊断分析：",
            }
            hint = source_hints.get(self.source_type, "请对以下内容进行网络故障诊断分析：")

            # 构建AI Prompt：本地预诊断精简摘要 + 精准上下文提取
            local_context = local_result.to_ai_prompt_context()

            # 精准提取异常周边上下文（替代全文截断，减少token）
            relevant_context = ""
            if local_result.total_findings > 0:
                relevant_context = local_result.extract_relevant_context(self.content, context_lines=8)

            prompt = (
                f"{hint}\n\n"
                f"## 本地预诊断结果\n"
                f"{local_context}\n"
            )
            if relevant_context:
                prompt += (
                    f"\n## 异常相关上下文（精准提取）\n"
                    f"```\n{relevant_context}\n```\n"
                )
            prompt += (
                f"\n## 任务要求\n"
                f"基于上述本地预诊断发现的异常：\n"
                f"1. 对每个异常进行深度根因分析\n"
                f"2. 补充本地规则可能遗漏的其他问题\n"
                f"3. 按OSI分层给出排查步骤和具体命令\n"
                f"4. 输出标准化的故障诊断报告"
            )

            url = f"{self.ai_config['base_url'].rstrip('/')}/chat/completions"
            payload = {
                "model": self.ai_config["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 4000
            }

            headers = {
                "Authorization": f"Bearer {self.ai_config['api_key']}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload_size = len(json.dumps(payload).encode('utf-8'))

            self.progress_signal.emit(f"正在发送AI请求 ({payload_size/1024:.1f}KB)...")
            _dbg(f"sending POST to {url}, model={self.ai_config.get('model','?')}, size={payload_size/1024:.1f}KB")

            resp = self._session.post(url, headers=headers, json=payload, timeout=120)
            _dbg(f"response status={resp.status_code}")

            if resp.status_code == 200:
                try:
                    ai_result = resp.json()["choices"][0]["message"]["content"]
                except (KeyError, IndexError, ValueError) as parse_err:
                    _dbg(f"JSON parse error: {parse_err}, body={resp.text[:300]}")
                    self.progress_signal.emit("AI返回数据解析失败 — 降级使用本地诊断结果")
                    report = self._build_local_only_report(local_result, source_hints)
                    self.finished_signal.emit(report)
                    return

                report = (
                    f"# AI 故障诊断报告\n\n"
                    f"## 数据来源: {source_hints.get(self.source_type, '未知')}\n"
                    f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 使用模型: {self.ai_config.get('model', 'N/A')}\n"
                    f"## 诊断模式: 双层诊断（本地运行时诊断 + AI精审）\n\n"
                    f"--- 第一层：本地运行时诊断结果 ---\n"
                    f"{local_result.to_summary_text()}\n\n"
                    f"--- 第二层：AI深度诊断 ---\n"
                    f"{ai_result}"
                )
                _dbg(f"diagnosis report generated, len={len(report)}")
                self.finished_signal.emit(report)
            elif resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 30
                _dbg(f"rate limited, wait={wait}s")
                # 降级返回本地结果
                self.progress_signal.emit("AI服务限速 — 降级使用本地诊断结果")
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
                return
            elif resp.status_code == 401:
                _dbg("auth failed (401)")
                self.progress_signal.emit("AI认证失败 — 降级使用本地诊断结果")
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
                return
            elif resp.status_code == 404:
                _dbg(f"model not found (404): {self.ai_config.get('model')}")
                self.progress_signal.emit("AI模型不存在 — 降级使用本地诊断结果")
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
                return
            else:
                _dbg(f"http error {resp.status_code}: {resp.text[:200]}")
                self.progress_signal.emit(f"AI服务错误 {resp.status_code} — 降级使用本地诊断结果")
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
                return

        except requests.exceptions.ConnectionError as conn_err:
            _dbg(f"connection error: {type(conn_err).__name__}: {str(conn_err)[:200]}")
            self.progress_signal.emit("AI服务不可达 — 降级使用本地诊断结果")
            if self._local_diag_result:
                report = self._build_local_only_report(self._local_diag_result, source_hints)
                self.finished_signal.emit(report)
            else:
                self.error_signal.emit(f"无法连接AI服务({type(conn_err).__name__})，请检查网络和模型配置中的Base URL")
        except requests.exceptions.Timeout:
            _dbg("request timeout (>120s)")
            self.progress_signal.emit("AI诊断超时 — 降级使用本地诊断结果")
            if self._local_diag_result:
                report = self._build_local_only_report(self._local_diag_result, source_hints)
                self.finished_signal.emit(report)
            else:
                self.error_signal.emit("AI诊断超时(>120秒)，请重试或减小分析内容")
        except requests.exceptions.SSLError as ssl_err:
            _dbg(f"SSL error: {str(ssl_err)[:200]}")
            self.progress_signal.emit("SSL证书验证失败 — 降级使用本地诊断结果")
            if self._local_diag_result:
                report = self._build_local_only_report(self._local_diag_result, source_hints)
                self.finished_signal.emit(report)
            else:
                self.error_signal.emit(f"SSL证书验证失败: {str(ssl_err)[:150]}")
        except Exception as e:
            _dbg(f"UNEXPECTED EXCEPTION: {type(e).__name__}: {str(e)[:500]}")
            import traceback
            _dbg(traceback.format_exc())
            if self._local_diag_result:
                self.progress_signal.emit("AI诊断异常 — 降级使用本地诊断结果")
                report = self._build_local_only_report(self._local_diag_result, source_hints)
                self.finished_signal.emit(report)
            else:
                self.error_signal.emit(f"诊断异常: {type(e).__name__}: {str(e)}")
        finally:
            try:
                self._session.close()
            except Exception:
                pass
            _dbg("THREAD END")


class SingleDeviceWorker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int, str, str)
    error_signal = pyqtSignal(int, str)
    batch_progress = pyqtSignal(int, int)

    def __init__(self, task_type: str, devices: List[Dict], row_indices: List[int] = None):
        super().__init__()
        self.task_type = task_type
        self.devices = devices
        self.row_indices = row_indices or list(range(len(devices)))
        self._cancelled = False

    def run(self):
        total = len(self.devices)
        for idx, dev in enumerate(self.devices):
            if self._cancelled:
                break
            row_idx = self.row_indices[idx] if idx < len(self.row_indices) else idx
            try:
                if self.task_type == "inspect":
                    self._do_inspect(dev, row_idx, idx, total)

                elif self.task_type == "backup":
                    self._do_backup(dev, row_idx, idx, total)

                elif self.task_type == "test_connect":
                    self._do_test_connection(dev, row_idx)

            except ImportError as e:
                self.error_signal.emit(row_idx, f"模块导入失败：{str(e)}")
            except Exception as e:
                self.error_signal.emit(row_idx, str(e))

            self.batch_progress.emit(idx + 1, total)

    @staticmethod
    def _is_permission_error(e: Exception) -> bool:
        if isinstance(e, OSError) and e.errno == 10013:
            return True
        err_str = str(e)
        return "10013" in err_str or "access" in err_str.lower() and "socket" in err_str.lower()

    def _build_conn_params(self, dev: Dict) -> Dict:
        ip = dev["ip"]
        proto = dev.get("protocol", "ssh")
        vendor = dev.get("vendor", "锐捷")
        dev_type = DEV_TYPE_MAP.get(vendor, "cisco_ios")
        return {
            "device_type": dev_type,
            "host": ip,
            "username": dev["username"],
            "password": dev["password"],
            "secret": dev.get("enable_password", ""),
            "timeout": 120,
            "conn_timeout": 30,
            "auth_timeout": 60,
            "banner_timeout": 60,
            "allow_auto_change": True,
            "global_delay_factor": 2 if vendor == "锐捷" else 1,
            "port": 22 if proto == "ssh" else 23,
            "keepalive": 30,
        }

    def _do_backup(self, dev: Dict, row_idx: int, idx: int, total: int):
        from netmiko import ConnectHandler
        from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = dev["device_type"]
        proto = dev.get("protocol", "ssh")
        port = 22 if proto == "ssh" else 23

        config_cmd = FULL_CONFIG_CMD_MAP.get(vendor, "show running-config")

        required_fields = ["ip", "vendor", "device_type", "username", "password", "protocol"]
        missing = [f for f in required_fields if not dev.get(f)]
        if missing:
            self.error_signal.emit(row_idx, f"备份参数缺失: {', '.join(missing)}")
            return

        conn_params = self._build_conn_params(dev)

        self.progress_signal.emit(f"[{idx+1}/{total}] 开始备份 {ip} ...")
        self.progress_signal.emit(f"连接参数: device_type={conn_params['device_type']}, host={ip}, port={port}")

        base_dir = get_single_dir()
        backup_dir = os.path.join(base_dir, "config_backup")
        safe_dev_mod = "".join(c for c in device_type if c.isalnum() or c in '._-')

        max_retries = 3
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                delay = 3
                self.progress_signal.emit(f"第{attempt}次: 等待{delay}s后开始...")
                time.sleep(delay)

                self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")
                with ConnectHandler(**conn_params) as conn:
                    try:
                        conn.enable()
                    except Exception:
                        pass
                    config = conn.send_command(config_cmd)

                if not config or len(config) < 100:
                    self.finished_signal.emit(row_idx, f"【{ip}】配置获取失败，配置过短", "")
                    return

                os.makedirs(backup_dir, exist_ok=True)
                file_name = f"{safe_dev_mod}_{ip}_配置备份.txt"
                file_path = os.path.join(backup_dir, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"【设备厂商】：{vendor}\n")
                    f.write(f"【设备类型】：{device_type}\n")
                    f.write(f"【设备IP】：{ip}\n")
                    f.write(f"配置备份时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(config)

                hint = f"\n📁 备份目录：{backup_dir}"
                if attempt > 1:
                    self.finished_signal.emit(row_idx, f"【{ip}】第{attempt}次重试后备份成功", hint)
                else:
                    self.finished_signal.emit(row_idx, f"【{ip}】配置备份成功", hint)
                return

            except NetmikoAuthenticationException as e:
                last_err = f"认证失败: {str(e)}"
                self.progress_signal.emit(f"SSH认证: {last_err}")
            except (NetmikoTimeoutException, socket.timeout) as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"SSH超时: {last_err}")
            except socket.gaierror as e:
                last_err = f"DNS解析失败: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except ConnectionRefusedError as e:
                last_err = f"端口被拒绝: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except OSError as e:
                if self._is_permission_error(e):
                    last_err = "系统权限被拒绝(WinError 10013)\n⚠️ 可能原因：杀毒软件/防火墙拦截了程序的网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到杀毒软件白名单"
                    self.progress_signal.emit(f"权限错误: {last_err}")
                else:
                    last_err = f"OSError({e.errno}): {str(e)}"
                    self.progress_signal.emit(f"OS错误: {last_err}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"异常: {last_err}")

            if attempt < max_retries:
                self.progress_signal.emit(f"第{attempt}次失败，准备重试...")
                continue
            self.finished_signal.emit(row_idx, f"【{ip}】备份失败（已重试{max_retries}次）\n详情：{last_err}", "")
            return

    def _do_inspect(self, dev: Dict, row_idx: int, idx: int, total: int):
        from netmiko import ConnectHandler
        from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = dev["device_type"]
        proto = dev.get("protocol", "ssh")
        port = 22 if proto == "ssh" else 23

        if vendor not in DEV_TYPE_MAP:
            self.finished_signal.emit(row_idx, f"【{ip}】暂不支持该厂商适配", "")
            return

        normalized_type = INSPECT_TYPE_NORMALIZE.get(device_type, "交换机")
        cmd_list = INSPECT_BASE_CMD_LIB.get(vendor, {}).get(normalized_type, INSPECT_DEFAULT_CMDS)

        conn_params = self._build_conn_params(dev)

        self.progress_signal.emit(f"[{idx+1}/{total}] 开始巡检 {ip} ...")
        self.progress_signal.emit(f"连接参数: device_type={conn_params['device_type']}, host={ip}, port={port}")
        inspect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        base_dir = get_single_dir()

        max_retries = 3
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                delay = 3
                self.progress_signal.emit(f"第{attempt}次: 等待{delay}s后开始...")
                time.sleep(delay)

                self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")
                with ConnectHandler(**conn_params) as conn:
                    try:
                        conn.enable()
                    except Exception:
                        pass
                    res = ""
                    for cmd in cmd_list:
                        res += f"\n===== {cmd} =====\n"
                        try:
                            output = conn.send_command(cmd)
                            res += output if output.strip() else "(无输出)"
                        except Exception:
                            res += "(命令执行失败)"

                    err_flag = False
                    for key in INSPECT_EXCEPTION_KEYS:
                        if key in res:
                            err_flag = True
                            break

                    full_config_cmd = FULL_CONFIG_CMD_MAP.get(vendor, "")
                    if err_flag and full_config_cmd:
                        try:
                            res += f"\n\n===== 故障设备抓取完整运行配置 =====\n"
                            res += conn.send_command(full_config_cmd)
                        except Exception:
                            res += "(配置抓取失败)"

                status_line = "\u26a0\ufe0f 发现异常" if err_flag else "\u2705 巡检正常"

                full_report = (
                    f"===== 设备巡检报告 =====\n"
                    f"【设备IP】：{ip}\n"
                    f"【厂商】：{vendor}\n"
                    f"【设备类型】：{device_type}\n"
                    f"【巡检时间】：{inspect_time}\n"
                    f"【执行命令数】：{len(cmd_list)}\n"
                    f"{res}\n\n"
                    f"===== 巡检状态 =====\n"
                    f"{status_line}\n"
                )

                report_dir = os.path.join(base_dir, "report", "single_inspect")
                os.makedirs(report_dir, exist_ok=True)
                safe_ip = ip.replace(".", "_")
                report_name = f"{safe_ip}_{inspect_time.replace(':', '').replace(' ', '_')}_巡检报告.txt"
                report_path = os.path.join(report_dir, report_name)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(full_report)

                if err_flag:
                    exc_dir = os.path.join(base_dir, "output", "single_exception")
                    os.makedirs(exc_dir, exist_ok=True)
                    exc_name = f"{device_type}_{ip}_异常.txt"
                    exc_path = os.path.join(exc_dir, exc_name)
                    with open(exc_path, "w", encoding="utf-8") as f:
                        f.write(f"【设备厂商】：{vendor}\n")
                        f.write(f"【设备类型】：{device_type}\n")
                        f.write(f"【设备IP】：{ip}\n")
                        f.write(f"【巡检时间】：{inspect_time}\n\n")
                        f.write(full_report)

                hint = f"\n📄 报告已保存至：single/report/single_inspect/"
                if attempt > 1:
                    self.finished_signal.emit(row_idx, f"【{ip}】第{attempt}次重试后巡检成功\n{full_report}", hint)
                else:
                    self.finished_signal.emit(row_idx, full_report, hint)
                return

            except NetmikoAuthenticationException as e:
                last_err = f"认证失败: {str(e)}"
                self.progress_signal.emit(f"SSH认证: {last_err}")
            except (NetmikoTimeoutException, socket.timeout) as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"SSH超时: {last_err}")
            except socket.gaierror as e:
                last_err = f"DNS解析失败: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except ConnectionRefusedError as e:
                last_err = f"端口被拒绝: {str(e)}"
                self.progress_signal.emit(f"{last_err}")
            except OSError as e:
                if self._is_permission_error(e):
                    last_err = "系统权限被拒绝(WinError 10013)\n⚠️ 可能原因：杀毒软件/防火墙拦截了程序的网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到杀毒软件白名单"
                    self.progress_signal.emit(f"权限错误: {last_err}")
                else:
                    last_err = f"OSError({e.errno}): {str(e)}"
                    self.progress_signal.emit(f"OS错误: {last_err}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)}"
                self.progress_signal.emit(f"异常: {last_err}")

            if attempt < max_retries:
                self.progress_signal.emit(f"第{attempt}次失败，准备重试...")
                continue
            self.finished_signal.emit(row_idx, f"【{ip}】巡检失败（已重试{max_retries}次）\n详情：{last_err}", "")
            return

    def _do_test_connection(self, dev: Dict, row_idx: int):
        ip = dev["ip"]
        vendor = dev["vendor"]
        device_type = DEV_TYPE_MAP.get(vendor, "cisco_ios")

        self.progress_signal.emit(f"正在Ping {ip} ...")
        try:
            count_param = "-n" if os.name == "nt" else "-c"
            timeout_param = "-w" if os.name == "nt" else "-W"
            timeout_val = "2000" if os.name == "nt" else "2"
            subprocess.run(
                ["ping", count_param, "1", timeout_param, timeout_val, str(ip)],
                capture_output=True, text=True, timeout=5
            )
            ping_ok = True
        except Exception:
            ping_ok = False

        if not ping_ok:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"【测试时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"🔴 连接失败：设备不可达\n"
                f"原因：Ping超时，设备无响应\n\n"
                f"========== 测试结束 ==========", "")
            return

        self.progress_signal.emit(f"Ping成功，正在尝试{vendor}登录 ...")

        try:
            from netmiko import ConnectHandler
            from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

            conn_params = self._build_conn_params(dev)
            proto = dev.get("protocol", "ssh")
            port = 22 if proto == "ssh" else 23

            self.progress_signal.emit(f"建立SSH连接 {ip}:{port} ...")

            start = datetime.now()
            with ConnectHandler(**conn_params) as conn:
                try:
                    conn.enable()
                except Exception:
                    pass
                ver_output = ""
                test_cmds = TEST_CMD_MAP.get(vendor, ["show version"])
                for cmd in test_cmds:
                    try:
                        out = conn.send_command(cmd)
                        ver_output += f"\n----- {cmd} -----\n{out}\n" if out.strip() else ""
                    except Exception:
                        pass

                elapsed = (datetime.now() - start).total_seconds()

                report = (
                    f"========== 连接测试报告 ==========\n"
                    f"【设备IP】：{ip}\n"
                    f"【厂商】：{vendor}\n"
                    f"【设备类型】：{dev['device_type']}\n"
                    f"【测试时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"【总耗时】：{elapsed:.1f}秒\n"
                    f"🟢 登录认证：成功\n"
                    f"{ver_output}\n"
                    f"========== 测试结束 =========="
                )
                self.finished_signal.emit(row_idx, report, "")

        except NetmikoAuthenticationException:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 网络可达，但登录失败\n"
                f"原因：账号密码认证错误\n"
                f"========== 测试结束 ==========", "")
        except NetmikoTimeoutException:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接超时\n"
                f"原因：SSH协议握手超时或被拒绝\n"
                f"========== 测试结束 ==========", "")
        except socket.timeout:
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接超时\n"
                f"原因：TCP/SSH层超时\n"
                f"========== 测试结束 ==========", "")
        except OSError as e:
            if self._is_permission_error(e):
                reason = "系统权限被拒绝(WinError 10013)\n⚠️ 杀毒软件/防火墙可能拦截了程序网络连接\n→ 请将 NetworkConfigGenerator.exe 添加到白名单"
            else:
                err_msg = str(e)
                if "10061" in err_msg or "refused" in err_msg.lower():
                    reason = "SSH端口被拒绝（可能未开启或防火墙拦截）"
                elif "10060" in err_msg or "timed out" in err_msg.lower():
                    reason = "连接超时（网络不通或设备无响应）"
                else:
                    reason = f"网络异常: {err_msg}"
            self.finished_signal.emit(row_idx,
                f"========== 连接测试报告 ==========\n"
                f"【设备IP】：{ip}\n"
                f"🟡 Ping可达，但SSH连接失败\n"
                f"原因：{reason}\n"
                f"========== 测试结束 ==========", "")
        except Exception as e:
            self.error_signal.emit(row_idx, f"测试连接异常：{str(e)}")

    def cancel(self):
        self._cancelled = True


class DeviceFormDialog(QDialog):
    def __init__(self, parent=None, device: Dict = None):
        super().__init__(parent)
        self.device = device or {}
        self.setWindowTitle("添加设备" if not device else "编辑设备")
        self.setMinimumWidth(480)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        form_group = QGroupBox("设备信息")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("设备IP："))
        self.ip_input = QLineEdit(self.device.get("ip", ""))
        self.ip_input.setPlaceholderText("如：192.168.1.1")
        r1.addWidget(self.ip_input)
        form_layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("厂商："))
        self.vendor_combo = QComboBox()
        self.vendor_combo.addItems(VENDORS)
        if self.device.get("vendor") in VENDORS:
            self.vendor_combo.setCurrentText(self.device["vendor"])
        r2.addWidget(self.vendor_combo)
        r2.addWidget(QLabel("类型："))
        self.type_combo = QComboBox()
        self.type_combo.addItems(DEVICE_TYPES)
        if self.device.get("device_type") in DEVICE_TYPES:
            self.type_combo.setCurrentText(self.device["device_type"])
        r2.addWidget(self.type_combo)
        form_layout.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("协议："))
        self.proto_combo = QComboBox()
        self.proto_combo.addItems(PROTOCOLS)
        if self.device.get("protocol") in PROTOCOLS:
            self.proto_combo.setCurrentText(self.device["protocol"])
        r3.addWidget(self.proto_combo)
        r3.addWidget(QLabel("用户名："))
        self.user_input = QLineEdit(self.device.get("username", ""))
        self.user_input.setPlaceholderText("SSH/Telnet用户名")
        r3.addWidget(self.user_input)
        form_layout.addLayout(r3)

        r4 = QHBoxLayout()
        r4.addWidget(QLabel("密码："))
        self.pwd_input = QLineEdit(self.device.get("password", ""))
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setPlaceholderText("登录密码")
        r4.addWidget(self.pwd_input)
        r4.addWidget(QLabel("特权密码："))
        self.enable_input = QLineEdit(self.device.get("enable_password", ""))
        self.enable_input.setEchoMode(QLineEdit.Password)
        self.enable_input.setPlaceholderText("可选")
        r4.addWidget(self.enable_input)
        form_layout.addLayout(r4)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        t = ThemeEngine.get().current_theme
        radius_md = t['radius_md']
        radius_sm = t['radius_sm']
        style = f"""
            QLabel {{ font-size: 11pt; color: {t['text_secondary']}; }}
            QLineEdit, QComboBox {{
                border: 1px solid {t['border']};
                border-radius: {radius_md}px;
                padding: 4px 8px;
                font-size: 11pt;
                background-color: {t['page_bg']};
            }}
            QLineEdit:focus, QComboBox:focus {{ border-color: {t['primary']}; }}
            QGroupBox {{
                font-size: 11pt; font-weight: bold; color: {t['text_main']};
                border: 1px solid {t['border']}; border-radius: {radius_md}px;
                margin-top: 8px; padding: 12px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
            QPushButton {{ padding: 5px 8px; border-radius: {radius_md}px; font-size: 11pt; }}
        """
        self.setStyleSheet(style)

    def get_data(self) -> Optional[Dict]:
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "提示", "请输入设备IP地址")
            return None
        return {
            "ip": ip,
            "vendor": self.vendor_combo.currentText(),
            "device_type": self.type_combo.currentText(),
            "protocol": self.proto_combo.currentText(),
            "username": self.user_input.text().strip(),
            "password": self.pwd_input.text().strip(),
            "enable_password": self.enable_input.text().strip(),
            "last_status": "",
            "last_time": ""
        }


class SingleDevicePage(QWidget):
    COL_CHECK = 0
    COL_IP = 1
    COL_VENDOR = 2
    COL_TYPE = 3
    COL_PROTO = 4
    COL_USER = 5
    COL_STATUS = 6
    COL_TIME = 7
    COL_DATA = 8

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.worker = None
        self.devices: List[Dict] = []
        self._secure_cfg = SecureConfigFile.instance()
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._load_devices()
        self.refresh_backup_list()
        self.refresh_report_list()
        self.refresh_compliance_list()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)

        table_group = QGroupBox("设备清单")
        table_group.setStyleSheet(self._group_style())
        table_layout = QVBoxLayout()
        table_layout.setSpacing(6)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        t = self._theme_engine.current_theme
        self.add_btn = QPushButton("+ 添加设备")
        self.add_btn.setFixedSize(100, 30)
        self.add_btn.setStyleSheet(self._toolbar_btn_style(t['page_bg'], t['text_secondary']))
        self.add_btn.clicked.connect(self.on_add_device)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.setFixedSize(72, 30)
        self.edit_btn.setStyleSheet(self._toolbar_btn_style(t['page_bg'], t['text_secondary']))
        self.edit_btn.clicked.connect(self.on_edit_device)
        toolbar.addWidget(self.edit_btn)

        self.del_btn = QPushButton("🗑️ 删除")
        self.del_btn.setFixedSize(72, 30)
        self.del_btn.setStyleSheet(self._small_danger_btn_style())
        self.del_btn.clicked.connect(self.on_delete_device)
        toolbar.addWidget(self.del_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.setFixedSize(72, 30)
        self.clear_btn.setStyleSheet(self._toolbar_btn_style(t['page_bg'], t['text_tertiary']))
        self.clear_btn.clicked.connect(self.on_clear_all)
        toolbar.addWidget(self.clear_btn)

        self.select_count_lbl = QLabel("")
        self.select_count_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        toolbar.addWidget(self.select_count_lbl)
        toolbar.addStretch()
        table_layout.addLayout(toolbar)

        t = self._theme_engine.current_theme
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["", "IP地址", "厂商", "设备类型", "协议", "用户名", "状态", "最后执行", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 32)
        self.table.setColumnWidth(2, 56)
        self.table.setColumnWidth(3, 96)
        self.table.setColumnWidth(4, 52)
        self.table.setColumnWidth(5, 76)
        self.table.setColumnWidth(6, 46)
        self.table.setColumnWidth(7, 140)
        self.table.setColumnWidth(8, 0)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(80)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                gridline-color: {t['border_deep']}; background-color: {t['card_bg']}; font-size: 10pt;
            }}
            QTableWidget::item {{ padding: 2px 4px; }}
            QTableWidget::item:alternate {{ background-color: {t['hover_bg']}; }}
            QHeaderView::section {{
                background-color: {t['toolbar_bg']}; border: none;
                border-bottom: 1px solid {t['border']}; padding: 2px 6px;
                font-size: 10pt; font-weight: bold; color: {t['text_secondary']};
            }}
        """)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.doubleClicked.connect(self.on_table_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)
        table_layout.addWidget(self.table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.inspect_btn = QPushButton("▶ 批量巡检")
        self.inspect_btn.setFixedSize(110, 30)
        self.inspect_btn.setStyleSheet(self._primary_btn_style())
        self.inspect_btn.clicked.connect(self.run_batch_inspect)
        action_row.addWidget(self.inspect_btn)

        self.backup_btn = QPushButton("💾 批量备份")
        self.backup_btn.setFixedSize(110, 30)
        self.backup_btn.setStyleSheet(self._secondary_btn_style())
        self.backup_btn.clicked.connect(self.run_batch_backup)
        action_row.addWidget(self.backup_btn)

        self.test_btn = QPushButton("🔗 测试连接")
        self.test_btn.setFixedSize(100, 30)
        self.test_btn.setStyleSheet(self._secondary_btn_style())
        self.test_btn.clicked.connect(self.run_batch_test)
        action_row.addWidget(self.test_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(60, 30)
        self.cancel_btn.setStyleSheet(self._cancel_btn_style())
        self.cancel_btn.clicked.connect(self.on_cancel_task)
        self.cancel_btn.setVisible(False)
        action_row.addWidget(self.cancel_btn)

        t = self._theme_engine.current_theme
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m")
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                text-align: center; height: 16px; background-color: {t['page_bg']}; font-size: 10pt;
            }}
            QProgressBar::chunk {{ background-color: {t['primary']}; border-radius: {t['radius_sm']}px; }}
        """)
        action_row.addWidget(self.progress_bar, 1)
        layout.addLayout(action_row)

        t = self._theme_engine.current_theme
        self.status_label = QLabel("就绪，等待操作...")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding-left: 4px;")
        layout.addWidget(self.status_label)

        self.result_tabs = QTabWidget()
        self.result_tabs.setDocumentMode(True)
        self.result_tabs.setTabPosition(QTabWidget.North)
        self.result_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                background-color: {t['card_bg']}; top: -1px;
            }}
            QTabBar::tab {{
                background-color: {t['page_bg']}; border: 1px solid {t['border']};
                border-bottom: none; border-top-left-radius: {t['radius_lg']}px;
                border-top-right-radius: {t['radius_lg']}px; padding: 5px 8px;
                font-size: 11pt; color: {t['text_secondary']}; margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['card_bg']}; color: {t['primary']};
                border-bottom: 2px solid {t['primary']}; font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{ background-color: {t['selection_bg']}; color: {t['primary']}; }}
        """)

        self.result_tabs.addTab(self._create_log_tab(), "📋 执行日志")
        self.result_tabs.addTab(self._create_backup_tab(), "💾 备份配置")
        self.result_tabs.addTab(self._create_report_tab(), "📄 巡检报告")
        self.result_tabs.addTab(self._create_diagnosis_tab(), "🩺 诊断报告")
        self.result_tabs.addTab(self._create_compliance_tab(), "🔍 合规审计")

        layout.addWidget(self.result_tabs, 1)

        t = self._theme_engine.current_theme
        desc_label = QLabel("管理常用设备清单，支持批量巡检/备份/连接测试/AI分析。数据加密存储，跟随EXE便携使用。")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; padding: 4px 0;")
        layout.addWidget(desc_label)

        self.setLayout(layout)
        self._update_select_count()

    def _text_edit_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QTextEdit {{
                border: none; border-radius: {t['radius_md']}px; padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt; background-color: {t['input_bg']}; color: {t['text_secondary']};
                selection-background-color: {t['selection_bg']}; selection-color: {t['text_main']};
            }}
        """

    def _list_widget_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QListWidget {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                background-color: {t['input_bg']}; font-size: 10pt; outline: none;
            }}
            QListWidget::item {{
                padding: 4px 8px; border-bottom: 1px solid {t['border_deep']};
            }}
            QListWidget::item:hover {{ background-color: {t['selection_bg']}; }}
            QListWidget::item:selected {{
                background-color: {t['primary']}; color: {t['text_primary']};
            }}
        """

    def _combo_small_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QComboBox {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                padding: 4px 8px; font-size: 11pt; background-color: {t['page_bg']};
            }}
            QComboBox:focus {{ border-color: {t['primary']}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{ image: none; border: 2px solid {t['text_tertiary']};
                width: 6px; height: 6px; transform: rotate(45deg);
                margin-right: 6px; }}
            QComboBox QAbstractItemView {{
                border: 1px solid {t['border']}; background-color: {t['card_bg']};
                selection-background-color: {t['selection_bg']}; outline: none;
            }}
        """

    def _create_log_tab(self) -> QWidget:
        t = self._theme_engine.current_theme
        w = QWidget()
        l = QVBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(4)

        bar = QHBoxLayout()
        self.log_clear_btn = QPushButton("清空日志")
        self.log_clear_btn.setFixedSize(70, 26)
        self.log_clear_btn.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: 1px solid {t['border']};
                border-radius: {t['radius_sm']}px; font-size: 10pt; color: {t['text_tertiary']}; padding: 2px 8px; }}
            QPushButton:hover {{ border-color: {t['primary']}; color: {t['primary']}; }}
        """)
        self.log_clear_btn.clicked.connect(lambda: self.log_text.clear())
        bar.addWidget(self.log_clear_btn)
        bar.addStretch()

        self.log_diagnose_btn = QPushButton("🩺 AI故障诊断")
        self.log_diagnose_btn.setFixedSize(100, 30)
        self.log_diagnose_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']}; }}
        """)
        self.log_diagnose_btn.clicked.connect(lambda: self.run_ai_diagnose("log"))
        bar.addWidget(self.log_diagnose_btn)

        self.log_info_lbl = QLabel("")
        self.log_info_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        bar.addWidget(self.log_info_lbl)
        l.addLayout(bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(self._text_edit_style())
        l.addWidget(self.log_text)
        w.setLayout(l)
        return w

    def _create_backup_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(8)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("设备筛选："))
        self.backup_filter_combo = QComboBox()
        self.backup_filter_combo.setMinimumWidth(140)
        self.backup_filter_combo.setStyleSheet(self._combo_small_style())
        self.backup_filter_combo.addItem("全部设备")
        self.backup_filter_combo.currentTextChanged.connect(self.on_backup_filter_changed)
        filter_row.addWidget(self.backup_filter_combo)
        left_panel.addLayout(filter_row)

        backup_btn_row = QHBoxLayout()
        backup_btn_row.setSpacing(4)
        self.backup_refresh_btn = QPushButton("🔄 刷新")
        self.backup_refresh_btn.setFixedSize(60, 26)
        self.backup_refresh_btn.setStyleSheet(self._small_btn_style())
        self.backup_refresh_btn.clicked.connect(self.refresh_backup_list)
        backup_btn_row.addWidget(self.backup_refresh_btn)

        self.backup_open_btn = QPushButton("📂 打开")
        self.backup_open_btn.setFixedSize(60, 26)
        self.backup_open_btn.setStyleSheet(self._small_btn_style())
        self.backup_open_btn.clicked.connect(self.on_open_backup_file)
        backup_btn_row.addWidget(self.backup_open_btn)

        self.backup_del_btn = QPushButton("🗑 删除")
        self.backup_del_btn.setFixedSize(60, 26)
        self.backup_del_btn.setStyleSheet(self._small_danger_btn_style())
        self.backup_del_btn.clicked.connect(self.on_delete_backup_file)
        backup_btn_row.addWidget(self.backup_del_btn)
        backup_btn_row.addStretch()
        left_panel.addLayout(backup_btn_row)

        self.backup_file_list = QListWidget()
        self.backup_file_list.setMinimumWidth(200)
        self.backup_file_list.setMaximumWidth(280)
        self.backup_file_list.setStyleSheet(self._list_widget_style())
        self.backup_file_list.currentItemChanged.connect(self.on_backup_file_selected)
        left_panel.addWidget(self.backup_file_list, 1)

        l.addLayout(left_panel, 0)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.backup_file_name_lbl = QLabel("未选择文件")
        self.backup_file_name_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.backup_file_name_lbl)
        info_bar.addStretch()

        self.ai_inspect_btn = QPushButton("🔍 AI合规巡检")
        self.ai_inspect_btn.setFixedSize(100, 30)
        self.ai_inspect_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']}; }}
        """)
        self.ai_inspect_btn.clicked.connect(self.run_ai_inspect)
        info_bar.addWidget(self.ai_inspect_btn)

        right_panel.addLayout(info_bar)

        self.backup_content = QTextEdit()
        self.backup_content.setReadOnly(True)
        self.backup_content.setStyleSheet(self._text_edit_style())
        self.backup_content.setPlaceholderText("选择左侧文件查看备份内容...")
        right_panel.addWidget(self.backup_content, 1)

        l.addLayout(right_panel, 1)
        w.setLayout(l)
        return w

    def _create_report_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(8)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("设备筛选："))
        self.report_filter_combo = QComboBox()
        self.report_filter_combo.setMinimumWidth(140)
        self.report_filter_combo.setStyleSheet(self._combo_small_style())
        self.report_filter_combo.addItem("全部设备")
        self.report_filter_combo.currentTextChanged.connect(self.on_report_filter_changed)
        filter_row.addWidget(self.report_filter_combo)
        left_panel.addLayout(filter_row)

        report_btn_row = QHBoxLayout()
        report_btn_row.setSpacing(4)
        self.report_refresh_btn = QPushButton("🔄 刷新")
        self.report_refresh_btn.setFixedSize(60, 26)
        self.report_refresh_btn.setStyleSheet(self._small_btn_style())
        self.report_refresh_btn.clicked.connect(self.refresh_report_list)
        report_btn_row.addWidget(self.report_refresh_btn)

        self.report_open_btn = QPushButton("📂 打开")
        self.report_open_btn.setFixedSize(60, 26)
        self.report_open_btn.setStyleSheet(self._small_btn_style())
        self.report_open_btn.clicked.connect(self.on_open_report_file)
        report_btn_row.addWidget(self.report_open_btn)

        self.report_del_btn = QPushButton("🗑 删除")
        self.report_del_btn.setFixedSize(60, 26)
        self.report_del_btn.setStyleSheet(self._small_danger_btn_style())
        self.report_del_btn.clicked.connect(self.on_delete_report_file)
        report_btn_row.addWidget(self.report_del_btn)
        report_btn_row.addStretch()
        left_panel.addLayout(report_btn_row)

        self.report_file_list = QListWidget()
        self.report_file_list.setMinimumWidth(200)
        self.report_file_list.setMaximumWidth(280)
        self.report_file_list.setStyleSheet(self._list_widget_style())
        self.report_file_list.currentItemChanged.connect(self.on_report_file_selected)
        left_panel.addWidget(self.report_file_list, 1)

        l.addLayout(left_panel, 0)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.report_title_lbl = QLabel("未选择报告")
        self.report_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.report_title_lbl)
        info_bar.addStretch()

        self.report_ai_btn = QPushButton("🩺 AI故障诊断")
        self.report_ai_btn.setFixedSize(100, 30)
        self.report_ai_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']}; }}
        """)
        self.report_ai_btn.clicked.connect(lambda: self.run_ai_diagnose("report"))
        self.report_ai_btn.setEnabled(False)
        info_bar.addWidget(self.report_ai_btn)

        right_panel.addLayout(info_bar)

        self.report_content = QTextEdit()
        self.report_content.setReadOnly(True)
        self.report_content.setStyleSheet(self._text_edit_style())
        self.report_content.setPlaceholderText("选择左侧报告查看详情...")
        right_panel.addWidget(self.report_content, 1)

        l.addLayout(right_panel, 1)
        w.setLayout(l)
        return w

    def _create_diagnosis_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(6)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)

        diag_btn_row = QHBoxLayout()
        diag_btn_row.setSpacing(4)
        self.diagnosis_refresh_btn = QPushButton("🔄 刷新")
        self.diagnosis_refresh_btn.setFixedSize(60, 26)
        self.diagnosis_refresh_btn.setStyleSheet(self._small_btn_style())
        self.diagnosis_refresh_btn.clicked.connect(self.refresh_diagnosis_list)
        diag_btn_row.addWidget(self.diagnosis_refresh_btn)

        self.diagnosis_open_btn = QPushButton("📂 打开")
        self.diagnosis_open_btn.setFixedSize(60, 26)
        self.diagnosis_open_btn.setStyleSheet(self._small_btn_style())
        self.diagnosis_open_btn.clicked.connect(self.on_open_diagnosis_file)
        diag_btn_row.addWidget(self.diagnosis_open_btn)

        self.diagnosis_del_btn = QPushButton("🗑 删除")
        self.diagnosis_del_btn.setFixedSize(60, 26)
        self.diagnosis_del_btn.setStyleSheet(self._small_danger_btn_style())
        self.diagnosis_del_btn.clicked.connect(self.on_delete_diagnosis_file)
        diag_btn_row.addWidget(self.diagnosis_del_btn)
        diag_btn_row.addStretch()
        left_panel.addLayout(diag_btn_row)

        self.diagnosis_file_list = QListWidget()
        self.diagnosis_file_list.setMinimumWidth(200)
        self.diagnosis_file_list.setMaximumWidth(280)
        self.diagnosis_file_list.setStyleSheet(self._list_widget_style())
        self.diagnosis_file_list.currentItemChanged.connect(self.on_diagnosis_file_selected)
        left_panel.addWidget(self.diagnosis_file_list, 1)

        l.addLayout(left_panel, 0)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.diagnosis_title_lbl = QLabel("未选择报告")
        self.diagnosis_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.diagnosis_title_lbl)
        info_bar.addStretch()

        right_panel.addLayout(info_bar)

        self.diagnosis_content = QTextEdit()
        self.diagnosis_content.setReadOnly(True)
        self.diagnosis_content.setStyleSheet(self._text_edit_style())
        self.diagnosis_content.setPlaceholderText("选择左侧诊断报告查看内容，或通过其他Tab的[🩺AI故障诊断]按钮生成新报告。")
        right_panel.addWidget(self.diagnosis_content, 1)

        l.addLayout(right_panel, 1)
        w.setLayout(l)
        return w

    def _create_compliance_tab(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.setSpacing(6)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)

        comp_btn_row = QHBoxLayout()
        comp_btn_row.setSpacing(4)
        self.compliance_refresh_btn = QPushButton("🔄 刷新")
        self.compliance_refresh_btn.setFixedSize(60, 26)
        self.compliance_refresh_btn.setStyleSheet(self._small_btn_style())
        self.compliance_refresh_btn.clicked.connect(self.refresh_compliance_list)
        comp_btn_row.addWidget(self.compliance_refresh_btn)

        self.compliance_open_btn = QPushButton("📂 打开")
        self.compliance_open_btn.setFixedSize(60, 26)
        self.compliance_open_btn.setStyleSheet(self._small_btn_style())
        self.compliance_open_btn.clicked.connect(self.on_open_compliance_file)
        comp_btn_row.addWidget(self.compliance_open_btn)

        self.compliance_del_btn = QPushButton("🗑 删除")
        self.compliance_del_btn.setFixedSize(60, 26)
        self.compliance_del_btn.setStyleSheet(self._small_danger_btn_style())
        self.compliance_del_btn.clicked.connect(self.on_delete_compliance_file)
        comp_btn_row.addWidget(self.compliance_del_btn)
        comp_btn_row.addStretch()
        left_panel.addLayout(comp_btn_row)

        self.compliance_file_list = QListWidget()
        self.compliance_file_list.setMinimumWidth(200)
        self.compliance_file_list.setMaximumWidth(280)
        self.compliance_file_list.setStyleSheet(self._list_widget_style())
        self.compliance_file_list.currentItemChanged.connect(self.on_compliance_file_selected)
        left_panel.addWidget(self.compliance_file_list, 1)

        l.addLayout(left_panel, 0)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)

        info_bar = QHBoxLayout()
        t = self._theme_engine.current_theme
        self.compliance_title_lbl = QLabel("未选择报告")
        self.compliance_title_lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
        info_bar.addWidget(self.compliance_title_lbl)
        info_bar.addStretch()

        self.compliance_refine_btn = QPushButton("🩺 AI精审")
        self.compliance_refine_btn.setFixedSize(80, 30)
        self.compliance_refine_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']}; }}
        """)
        self.compliance_refine_btn.clicked.connect(lambda: self.run_ai_diagnose("compliance"))
        self.compliance_refine_btn.setEnabled(False)
        info_bar.addWidget(self.compliance_refine_btn)

        right_panel.addLayout(info_bar)

        self.compliance_content = QTextEdit()
        self.compliance_content.setReadOnly(True)
        self.compliance_content.setStyleSheet(self._text_edit_style())
        self.compliance_content.setPlaceholderText("选择左侧审计报告查看内容，或在【备份配置】Tab选中配置文件后点击[🔍AI合规巡检]生成新报告。")
        right_panel.addWidget(self.compliance_content, 1)

        l.addLayout(right_panel, 1)
        w.setLayout(l)
        return w

    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()

    def _apply_theme_style(self) -> None:
        if self._theme_engine is None:
            return
        t = self._theme_engine.current_theme
        # 页面级背景（只设置背景和字体，不设置color避免覆盖子控件）
        self.setStyleSheet(f"""
            SingleDevicePage {{
                background-color: {t['page_bg']};
                font-family: {t['font_ui']};
            }}
        """)
        # QGroupBox 单独设置（避免在页面级 setStyleSheet 中使用 color 属性）
        if hasattr(self, 'table_group'):
            self.table_group.setStyleSheet(self._group_style())
        # 表格
        if hasattr(self, 'table'):
            self.table.setStyleSheet(self._table_style())
        # TabWidget
        if hasattr(self, 'result_tabs'):
            self.result_tabs.setStyleSheet(self._result_tabs_style())
        # 工具栏按钮
        for attr, style_fn in [
            ('add_btn', lambda: self._toolbar_btn_style(t['page_bg'], t['text_secondary'])),
            ('edit_btn', lambda: self._toolbar_btn_style(t['page_bg'], t['text_secondary'])),
            ('del_btn', self._small_danger_btn_style),
            ('clear_btn', lambda: self._toolbar_btn_style(t['page_bg'], t['text_tertiary'])),
        ]:
            btn = getattr(self, attr, None)
            if btn is not None:
                btn.setStyleSheet(style_fn())
        # 操作按钮
        if hasattr(self, 'inspect_btn'):
            self.inspect_btn.setStyleSheet(self._primary_btn_style())
        if hasattr(self, 'backup_btn'):
            self.backup_btn.setStyleSheet(self._secondary_btn_style())
        if hasattr(self, 'test_btn'):
            self.test_btn.setStyleSheet(self._secondary_btn_style())
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setStyleSheet(self._cancel_btn_style())
        # 进度条
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setStyleSheet(self._progress_style())
        # 状态标签
        for attr in ('status_label', 'select_count_lbl'):
            lbl = getattr(self, attr, None)
            if lbl is not None:
                lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")
        # 描述标签
        if hasattr(self, 'desc_label'):
            self.desc_label.setStyleSheet(
                f"font-size: 10pt; color: {t['text_tertiary']}; padding: 4px 0;")
        # 刷新所有 Tab 内容
        self._refresh_all_tabs()

    def _refresh_all_tabs(self) -> None:
        """刷新所有结果 Tab 的内部控件样式"""
        t = self._theme_engine.current_theme
        for i in range(self.result_tabs.count()):
            page = self.result_tabs.widget(i)
            if page is None:
                continue
            # 使用 findChildren 刷新子控件
            for lst in page.findChildren(QListWidget):
                lst.setStyleSheet(self._list_widget_style())
            for te in page.findChildren(QTextEdit):
                te.setStyleSheet(self._text_edit_style())
            for cb in page.findChildren(QComboBox):
                cb.setStyleSheet(self._combo_small_style())
            # 收集当前 page 的 del 按钮引用
            _page_del_btns = [
                getattr(page, a, None) for a in (
                    'backup_del_btn', 'report_del_btn',
                    'diagnosis_del_btn', 'compliance_del_btn')
            ]
            for btn in page.findChildren(QPushButton):
                obj_name = btn.objectName()
                if 'del' in obj_name or btn in _page_del_btns:
                    btn.setStyleSheet(self._small_danger_btn_style())
                elif any(kw in obj_name for kw in ('ai_', 'inspect', 'diagnose', 'refine')):
                    btn.setStyleSheet(self._ai_small_btn_style())
                else:
                    btn.setStyleSheet(self._small_btn_style())
            # 刷新 Tab 内 QLabel（"设备筛选："、文件名标签、info 标签等）
            for lbl in page.findChildren(QLabel):
                obj_name = lbl.objectName()
                if any(kw in obj_name for kw in ('_title_lbl', '_name_lbl')):
                    lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: bold;")
                else:
                    lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")

    def _group_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QGroupBox {{
                font-size: 11pt; font-weight: bold; color: {t['text_main']};
                border: 1px solid {t['border']}; border-radius: {t['radius_lg']}px;
                margin-top: 4px; padding: 4px 10px; background-color: {t['card_bg']};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
        """

    def _toolbar_btn_style(self, bg: str, fg: str) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {bg}; color: {fg}; border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 10pt;
            }}
            QPushButton:hover {{ border-color: {t['primary']}; }}
        """

    def _primary_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['primary']}; color: {t['text_primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 11pt; font-weight: bold;
                padding: 5px 8px;
            }}
            QPushButton:hover {{
                background-color: {t['primary_hover']};
                border-color: {t['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {t['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {t['border_deep']}; border-color: {t['border']};
                color: {t['text_tertiary']};
            }}
        """

    def _secondary_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['page_bg']}; border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 11pt;
            }}
            QPushButton:hover {{ border-color: {t['primary']}; color: {t['primary']}; }}
            QPushButton:disabled {{ background-color: {t['border_deep']}; }}
        """

    def _table_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QTableWidget {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                gridline-color: {t['border_deep']}; background-color: {t['card_bg']}; font-size: 10pt;
            }}
            QTableWidget::item {{ padding: 2px 4px; }}
            QTableWidget::item:alternate {{ background-color: {t['hover_bg']}; }}
            QHeaderView::section {{
                background-color: {t['toolbar_bg']}; border: none;
                border-bottom: 1px solid {t['border']}; padding: 2px 6px;
                font-size: 10pt; font-weight: bold; color: {t['text_secondary']};
            }}
        """

    def _result_tabs_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QTabWidget::pane {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                background-color: {t['card_bg']}; top: -1px;
            }}
            QTabBar::tab {{
                background-color: {t['page_bg']}; border: 1px solid {t['border']};
                border-bottom: none; border-top-left-radius: {t['radius_lg']}px;
                border-top-right-radius: {t['radius_lg']}px; padding: 5px 8px;
                font-size: 11pt; color: {t['text_secondary']}; margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['card_bg']}; color: {t['primary']};
                border-bottom: 2px solid {t['primary']}; font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{ background-color: {t['selection_bg']}; color: {t['primary']}; }}
        """

    def _progress_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QProgressBar {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                text-align: center; height: 20px; background-color: {t['page_bg']}; font-size: 10pt;
            }}
            QProgressBar::chunk {{ background-color: {t['primary']}; border-radius: {t['radius_sm']}px; }}
        """

    def _ai_small_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']};
            }}
        """

    def _test_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['page_bg']}; color: {t['text_secondary']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {t['hover_bg']};
                border-color: {t['primary']}; color: {t['primary']};
            }}
            QPushButton:disabled {{ background-color: {t['border_deep']}; }}
        """

    def _cancel_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['page_bg']}; color: {t['text_secondary']};
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px; font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {t['hover_bg']};
                border-color: {t['primary']}; color: {t['primary']};
            }}
        """

    def _small_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{ background-color: {t['page_bg']}; border: 1px solid {t['border']};
                border-radius: {t['radius_sm']}px; font-size: 10pt; color: {t['text_secondary']}; padding: 2px 8px; }}
            QPushButton:hover {{ border-color: {t['primary']}; color: {t['primary']}; }}
        """

    def _small_danger_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{ background-color: {t['page_bg']}; border: 1px solid {t['danger']};
                border-radius: {t['radius_sm']}px; font-size: 10pt; color: {t['danger']}; padding: 2px 8px; }}
            QPushButton:hover {{ background-color: {t['hover_bg']}; border-color: {t['danger']}; color: {t['danger']}; }}
        """

    def _get_selected_devices(self) -> tuple:
        rows = []
        devs = []
        for row in range(self.table.rowCount()):
            item = self.table.cellWidget(row, self.COL_CHECK)
            if item and isinstance(item, QCheckBox) and item.isChecked():
                data_item = self.table.item(row, self.COL_DATA)
                if data_item:
                    devs.append(data_item.data(Qt.UserRole))
                    rows.append(row)
        return rows, devs

    def _refresh_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.devices))
        for row, dev in enumerate(self.devices):
            chk = QCheckBox()
            chk.setStyleSheet("margin-left: 6px;")
            self.table.setCellWidget(row, self.COL_CHECK, chk)

            for col, key in [(self.COL_IP, "ip"), (self.COL_VENDOR, "vendor"),
                             (self.COL_TYPE, "device_type"), (self.COL_PROTO, "protocol"),
                             (self.COL_USER, "username"), (self.COL_STATUS, "last_status"),
                             (self.COL_TIME, "last_time")]:
                item = QTableWidgetItem(str(dev.get(key, "")))
                item.setTextAlignment(Qt.AlignCenter)
                if col == self.COL_STATUS:
                    icon = STATUS_ICONS.get(dev.get("status", ""), "")
                    if icon:
                        item.setText(icon)
                if col == self.COL_IP:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

            data_item = QTableWidgetItem()
            data_item.setData(Qt.UserRole, dev)
            self.table.setItem(row, self.COL_DATA, data_item)

        self.table.blockSignals(False)
        self._update_select_count()
        self._refresh_device_filters()

    def _update_select_count(self):
        count = sum(1 for r in range(self.table.rowCount())
                     if self.table.cellWidget(r, self.COL_CHECK)
                     and isinstance(self.table.cellWidget(r, self.COL_CHECK), QCheckBox)
                     and self.table.cellWidget(r, self.COL_CHECK).isChecked())
        total = self.table.rowCount()
        self.select_count_lbl.setText(f"共 {total} 台 | 已选 {count} 台")
        line_count = self.log_text.document().blockCount() if hasattr(self, 'log_text') else 0
        if hasattr(self, 'log_info_lbl'):
            self.log_info_lbl.setText(f"{line_count} 行")

    def on_item_changed(self, item):
        if item.column() == self.COL_CHECK:
            self._update_select_count()

    def on_add_device(self):
        dialog = DeviceFormDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                self.devices.append(data)
                self._refresh_table()
                self._save_devices()
                self.log_append(f"✅ 已添加设备：{data['ip']} ({data['vendor']} {data['device_type']})")

    def on_edit_device(self):
        rows, _ = self._get_selected_devices()
        if not rows:
            if self.table.currentRow() >= 0:
                rows = [self.table.currentRow()]
            else:
                QMessageBox.information(self, "提示", "请先选择要编辑的设备行")
                return
        row = rows[0]
        data_item = self.table.item(row, self.COL_DATA)
        if not data_item:
            return
        dev = data_item.data(Qt.UserRole)
        dialog = DeviceFormDialog(self, dev)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data:
                new_data["last_status"] = dev.get("last_status", "")
                new_data["last_time"] = dev.get("last_time", "")
                self.devices[row] = new_data
                self._refresh_table()
                self._save_devices()
                self.log_append(f"✏️ 已更新设备：{new_data['ip']}")

    def on_delete_device(self):
        rows, _ = self._get_selected_devices()
        if not rows:
            QMessageBox.information(self, "提示", "请先勾选要删除的设备")
            return
        reply = QMessageBox.question(self, "确认删除",
                                     f'确定要删除选中的 {len(rows)} 台设备吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        for row in sorted(rows, reverse=True):
            del self.devices[row]
        self._refresh_table()
        self._save_devices()
        self.log_append(f"🗑️ 已删除 {len(rows)} 台设备")

    def on_clear_all(self):
        if not self.devices:
            return
        reply = QMessageBox.question(self, "确认清空",
                                     f'确定要清空全部 {len(self.devices)} 台设备吗？此操作不可恢复。',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.devices.clear()
        self._refresh_table()
        self._save_devices()
        self.log_append("🗑️ 已清空全部设备列表")

    def on_table_double_click(self, index):
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if col == self.COL_STATUS:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                ip = dev.get("ip", "")
                status = dev.get("last_status", "")
                if status == "success":
                    self.result_tabs.setCurrentIndex(TAB_BACKUP)
                    self._select_backup_by_ip(ip)
                elif status == "failed":
                    self.result_tabs.setCurrentIndex(TAB_LOG)
                return
        if col != self.COL_CHECK:
            self.edit_btn.click()

    def on_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu(self)
        edit_act = menu.addAction("✏️ 编辑此设备")
        del_act = menu.addAction("🗑️ 删除此设备")
        sel_act = menu.addAction("☑️ 选中此设备")
        view_bk = menu.addAction("💾 查看备份")
        view_rp = menu.addAction("📄 查看巡检报告")
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == edit_act:
            self.table.selectRow(row)
            self.on_edit_device()
        elif action == del_act:
            self.table.selectRow(row)
            rows, _ = self._get_selected_devices()
            if row not in rows:
                chk = self.table.cellWidget(row, self.COL_CHECK)
                if isinstance(chk, QCheckBox):
                    chk.setChecked(True)
            self.on_delete_device()
        elif action == sel_act:
            chk = self.table.cellWidget(row, self.COL_CHECK)
            if isinstance(chk, QCheckBox):
                chk.setChecked(not chk.isChecked())
        elif action == view_bk:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                self.result_tabs.setCurrentIndex(TAB_BACKUP)
                self._select_backup_by_ip(dev.get("ip", ""))
        elif action == view_rp:
            data_item = self.table.item(row, self.COL_DATA)
            if data_item:
                dev = data_item.data(Qt.UserRole)
                self.result_tabs.setCurrentIndex(TAB_REPORT)
                self._select_report_by_ip(dev.get("ip", ""))

    def _load_devices(self):
        raw = self._secure_cfg.load(SINGLE_DEVICES_PATH)
        if raw and isinstance(raw, dict):
            self.devices = raw.get("devices", [])
        self._refresh_table()

    def _save_devices(self):
        data = {"devices": self.devices, "updated": datetime.now().isoformat()}
        self._secure_cfg.save(SINGLE_DEVICES_PATH, data)

    def _set_buttons_enabled(self, enabled: bool):
        self.inspect_btn.setEnabled(enabled)
        self.backup_btn.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(enabled)
        self.del_btn.setEnabled(enabled)
        self.cancel_btn.setVisible(not enabled)

    def log_append(self, msg: str):
        ts = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.append(f"{ts} {msg}")
        self._update_select_count()

    def run_batch_inspect(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要巡检的设备")
            return
        self._start_batch_task("inspect", devs, rows, "批量巡检")

    def run_batch_backup(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要备份的设备")
            return
        self._start_batch_task("backup", devs, rows, "批量备份")

    def run_batch_test(self):
        rows, devs = self._get_selected_devices()
        if not devs:
            QMessageBox.information(self, "提示", "请先勾选要测试的设备")
            return
        self._start_batch_task("test_connect", devs, rows, "批量测试连接")

    def _start_batch_task(self, task_type: str, devs: List[Dict], rows: List[int], label: str):
        self._set_buttons_enabled(False)
        self.log_text.clear()
        self.progress_bar.setMaximum(len(devs))
        self.progress_bar.setValue(0)
        self.status_label.setText(f"正在{label}... 共 {len(devs)} 台")
        self.result_tabs.setCurrentIndex(TAB_LOG)

        self.worker = SingleDeviceWorker(task_type, devs, rows)
        self.worker.progress_signal.connect(self.on_progress)
        self.worker.finished_signal.connect(self.on_task_finished)
        self.worker.error_signal.connect(self.on_task_error)
        self.worker.batch_progress.connect(self.on_batch_progress)
        self.worker.start()

    def on_progress(self, msg: str):
        self.log_append(msg)

    def on_task_finished(self, row_idx: int, result: str, hint: str):
        self.log_append(result)
        t = self._theme_engine.current_theme
        if row_idx < len(self.devices):
            self.devices[row_idx]["last_status"] = "success"
            self.devices[row_idx]["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            status_item = self.table.item(row_idx, self.COL_STATUS)
            time_item = self.table.item(row_idx, self.COL_TIME)
            if status_item:
                status_item.setText("✅")
                status_item.setForeground(QColor(t['success']))
            if time_item:
                time_item.setText(self.devices[row_idx]["last_time"])

    def on_task_error(self, row_idx: int, err_msg: str):
        self.log_append(f"❌ 错误：{err_msg}")
        t = self._theme_engine.current_theme
        if row_idx < len(self.devices):
            self.devices[row_idx]["last_status"] = "failed"
            self.devices[row_idx]["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            status_item = self.table.item(row_idx, self.COL_STATUS)
            time_item = self.table.item(row_idx, self.COL_TIME)
            if status_item:
                status_item.setText("❌")
                status_item.setForeground(QColor(t['danger']))
            if time_item:
                time_item.setText(self.devices[row_idx]["last_time"])

    def on_batch_progress(self, current: int, total: int):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"执行中... {current}/{total}")
        if current >= total:
            self._on_batch_complete(total)

    def _on_batch_complete(self, total: int):
        self._set_buttons_enabled(True)
        self._save_devices()
        self.status_label.setText(f"✅ 全部完成！共处理 {total} 台设备")
        self.log_append(f"\n{'='*50}")
        self.log_append(f"✅ 批量任务完成！共 {total} 台设备处理完毕")
        self.log_append(f"{'='*50}")
        self.refresh_backup_list()
        self.refresh_report_list()

    def on_cancel_task(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.log_append("⚠️ 用户取消任务，等待当前设备完成...")

    def run_ai_inspect(self):
        try:
            t = self._theme_engine.current_theme
            self.ai_inspect_btn.setStyleSheet(f"""
                QPushButton {{ background-color: {t['hover_bg']}; color: {t['text_tertiary']};
                    border: 1px solid {t['border']};
                    border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            """)
            self.ai_inspect_btn.setText("⏳ 分析中...")
            self.ai_inspect_btn.setEnabled(False)
            self.result_tabs.setCurrentIndex(TAB_LOG)
            self.log_append("=" * 60)
            self.log_append("🔍 AI合规巡检 — 启动中...")
            ai_config = get_active_ai_config()
            if not ai_config or not ai_config.get("base_url") or not ai_config.get("api_key"):
                self.log_append("⚠️ AI模型未配置，请在【⚙ 模型设置】中配置")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "请先在【⚙ 模型设置】中配置AI模型后再使用AI合规巡检功能。")
                return
            item = self.backup_file_list.currentItem()
            if not item:
                self.log_append("⚠️ 未选择备份文件")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "请先在左侧【备份配置】列表中选择一个配置文件。")
                return
            fp = item.data(Qt.UserRole)
            if not fp:
                self.log_append("⚠️ 备份文件路径无效")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "所选文件路径无效，请重新选择。")
                return
            self.log_append(f"📄 配置文件: {os.path.basename(fp)}")
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                self.log_append(f"❌ 读取文件失败: {str(e)}")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "读取失败", f"无法读取配置文件:\n{str(e)}")
                return
            if not content or len(content.strip()) < 50:
                self.log_append("⚠️ 配置文件内容为空或过短")
                self._restore_inspect_btn()
                QMessageBox.warning(self, "提示", "配置文件内容为空或过短，无法进行合规审计。")
                return
            self.log_append(f"✅ 配置已加载 ({len(content):,} 字符)，启动AI分析...")
            self._start_ai_inspect(content, os.path.basename(fp), ai_config)
        except Exception as e:
            self.log_append(f"❌ 合规巡检启动异常: {type(e).__name__}: {str(e)}")
            self._restore_inspect_btn()
            QMessageBox.critical(self, "错误", f"合规巡检启动失败:\n{type(e).__name__}: {str(e)}")

    def _restore_inspect_btn(self):
        t = self._theme_engine.current_theme
        self.ai_inspect_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                border: 1px solid {t['primary']};
                border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: {t['hover_bg']};
                border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                color: {t['text_tertiary']}; }}
        """)
        self.ai_inspect_btn.setText("🔍 AI合规巡检")
        self.ai_inspect_btn.setEnabled(True)

    def _start_ai_inspect(self, config_content: str, filename: str, ai_config: Dict[str, Any]):
        self.log_append("🔍 AI合规巡检已启动，正在进行双层审计（本地预检 + AI精审）...")
        device_ip = ""
        item = self.backup_file_list.currentItem()
        if item:
            text = item.text()
            for d in self.devices:
                if d.get("ip", "") in text:
                    device_ip = d["ip"]
                    break
        thread = ComplianceCheckThread(config_content, device_ip, ai_config)
        self._ai_inspect_thread = thread
        thread.progress_signal.connect(self.log_append)
        thread.finished_signal.connect(self.on_ai_inspect_finished)
        thread.error_signal.connect(lambda msg: (
            self.log_append(f"❌ {msg}"),
            self._restore_inspect_btn()
        ))
        thread.local_result_signal.connect(self._show_local_audit_result)
        thread.start()

    def _show_local_audit_result(self, result_text: str):
        self.result_tabs.setCurrentIndex(TAB_BACKUP)
        self.backup_content.setPlainText(result_text)
        self.backup_file_name_lbl.setText("📋 本地预检结果")

    def on_ai_inspect_finished(self, report: str):
        self._restore_inspect_btn()
        comp_dir = os.path.join(get_single_dir(), "report", "compliance")
        os.makedirs(comp_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"compliance_{ts}.md"
        try:
            with open(os.path.join(comp_dir, fname), "w", encoding="utf-8") as f:
                f.write(report)
        except Exception:
            pass
        self.refresh_compliance_list()
        self.compliance_content.setPlainText(report)
        self.compliance_title_lbl.setText(f"📄 {fname}")
        self.result_tabs.setCurrentIndex(TAB_COMPLIANCE)
        self.log_append("✅ AI合规巡检完成")

    def run_ai_diagnose(self, source_type: str):
        try:
            t = self._theme_engine.current_theme
            btn_map_all = {
                "report": self.report_ai_btn,
                "compliance": self.compliance_refine_btn,
                "log": self.log_diagnose_btn,
            }
            active_btn = btn_map_all.get(source_type)
            if active_btn:
                active_btn.setEnabled(False)
                active_btn.setText("⏳ 诊断中...")
                active_btn.setStyleSheet(f"""
                    QPushButton {{ background-color: {t['hover_bg']}; color: {t['text_tertiary']};
                        border: 1px solid {t['border']};
                        border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
                    QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                        color: {t['text_tertiary']}; }}
                """)
            self.result_tabs.setCurrentIndex(TAB_LOG)
            self.log_append("=" * 60)
            self.log_append("🩺 AI故障诊断 — 启动中...")
            ai_config = get_active_ai_config()
            if not ai_config or not ai_config.get("base_url") or not ai_config.get("api_key"):
                self.log_append("⚠️ AI模型未配置，请在【⚙ 模型设置】中配置")
                self._restore_diagnose_btn(source_type)
                QMessageBox.warning(self, "提示", "请先在【⚙ 模型设置】中配置AI模型后再使用AI故障诊断功能。")
                return
            content_map = {
                "backup": self.backup_content.toPlainText(),
                "report": self.report_content.toPlainText(),
                "compliance": self.compliance_content.toPlainText(),
                "log": self.log_text.toPlainText(),
            }
            content = content_map.get(source_type, "")
            if not content.strip():
                hints = {"backup": "请先选择一个备份配置文件", "report": "请先选择一份巡检报告",
                         "compliance": "请先选择一份审计报告", "log": "执行日志为空，请先执行操作"}
                self.log_append(f"⚠️ {hints.get(source_type, '没有可分析的内容')}")
                self._restore_diagnose_btn(source_type)
                QMessageBox.warning(self, "提示", hints.get(source_type, "没有可分析的内容"))
                return
            self.log_append(f"📄 数据来源: {source_type} ({len(content):,} 字符)")
            self.log_append("✅ 数据已加载，启动AI诊断引擎...")
            thread = AIDiagnosticThread(content, source_type, ai_config)
            self._ai_diagnose_thread = thread
            thread.progress_signal.connect(self.log_append)
            thread.finished_signal.connect(lambda r: self._on_diagnose_finished(r, source_type))
            thread.error_signal.connect(lambda msg: self._on_diagnose_error(msg, source_type))
            thread.start()
        except Exception as e:
            self.log_append(f"❌ 故障诊断启动异常: {type(e).__name__}: {str(e)}")
            self._restore_diagnose_btn(source_type)
            QMessageBox.critical(self, "错误", f"故障诊断启动失败:\n{type(e).__name__}: {str(e)}")

    def _restore_diagnose_btn(self, source_type: str):
        try:
            t = self._theme_engine.current_theme
            style_map = {
                "report": f"""
                    QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                        border: 1px solid {t['primary']};
                        border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
                    QPushButton:hover {{ background-color: {t['hover_bg']};
                        border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
                    QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                        color: {t['text_tertiary']}; }}
                """,
                "compliance": f"""
                    QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                        border: 1px solid {t['primary']};
                        border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
                    QPushButton:hover {{ background-color: {t['hover_bg']};
                        border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
                    QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                        color: {t['text_tertiary']}; }}
                """,
                "log": f"""
                    QPushButton {{ background-color: {t['page_bg']}; color: {t['primary']};
                        border: 1px solid {t['primary']};
                        border-radius: {t['radius_md']}px; font-size: 10pt; font-weight: bold; }}
                    QPushButton:hover {{ background-color: {t['hover_bg']};
                        border-color: {t['primary_hover']}; color: {t['primary_hover']}; }}
                    QPushButton:disabled {{ background-color: {t['hover_bg']}; border-color: {t['border']};
                        color: {t['text_tertiary']}; }}
                """,
            }
            text_map = {
                "report": "🩺 AI故障诊断",
                "compliance": "🩺 AI精审",
                "log": "🩺 AI故障诊断",
            }
            btn_map = {"report": self.report_ai_btn,
                       "compliance": self.compliance_refine_btn, "log": self.log_diagnose_btn}
            btn = btn_map.get(source_type)
            if btn:
                btn.setText(text_map.get(source_type, "🩺 AI故障诊断"))
                btn.setStyleSheet(style_map.get(source_type, ""))
                btn.setEnabled(True)
        except Exception as e:
            logger.warning(f"恢复诊断按钮异常(可忽略): {type(e).__name__}: {str(e)}")

    def _on_diagnose_error(self, msg: str, source_type: str):
        try:
            try:
                self.log_append(f"❌ {msg}")
            except Exception:
                pass
            try:
                self._restore_diagnose_btn(source_type)
            except Exception as btn_err:
                logger.warning(f"恢复诊断按钮异常: {btn_err}")
            QMessageBox.warning(self, "AI诊断失败", f"故障诊断过程中出现错误：\n\n{msg}")
        except Exception as e:
            logger.error(f"诊断错误回调异常: {type(e).__name__}: {str(e)}")
            try:
                QMessageBox.critical(self, "错误", f"AI诊断回调异常:\n{type(e).__name__}: {str(e)}")
            except Exception:
                pass

    def _on_diagnose_finished(self, report: str, source_type: str):
        _dbg_fp = os.path.join(get_app_dir(), "logs", "diagnosis_debug.log")
        def _cb_log(msg):
            try:
                os.makedirs(os.path.dirname(_dbg_fp), exist_ok=True)
                with open(_dbg_fp, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [CB] {msg}\n")
            except Exception:
                pass
        try:
            _cb_log("_on_diagnose_finished START")
            # 1. 保存报告文件
            try:
                diag_dir = os.path.join(get_single_dir(), "report", "diagnosis")
                os.makedirs(diag_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"diagnosis_{ts}.md"
                with open(os.path.join(diag_dir, fname), "w", encoding="utf-8") as f:
                    f.write(report)
                _cb_log(f"report saved: {fname}")
            except Exception as write_err:
                _cb_log(f"write file error: {write_err}")
                fname = "诊断报告"

            # 2. 刷新文件列表（独立保护，不影响后续步骤）
            try:
                _cb_log("refreshing diagnosis list...")
                self.refresh_diagnosis_list()
            except Exception as refresh_err:
                _cb_log(f"refresh list error: {type(refresh_err).__name__}: {refresh_err}")

            # 3. 更新诊断内容显示
            try:
                _cb_log("setting content to diagnosis widget...")
                self.diagnosis_content.setPlainText(report)
                self.diagnosis_title_lbl.setText(f"📄 {fname}")
            except Exception as content_err:
                _cb_log(f"set content error: {type(content_err).__name__}: {content_err}")

            # 4. 切换到诊断Tab
            try:
                _cb_log("switching to diagnosis tab...")
                self.result_tabs.setCurrentIndex(TAB_DIAGNOSIS)
            except Exception as tab_err:
                _cb_log(f"switch tab error: {type(tab_err).__name__}: {tab_err}")

            # 5. 恢复按钮状态
            try:
                _cb_log("restoring button state...")
                self._restore_diagnose_btn(source_type)
            except Exception as btn_err:
                _cb_log(f"restore btn error: {type(btn_err).__name__}: {btn_err}")

            # 6. 日志
            try:
                self.log_append("✅ AI故障诊断完成")
            except Exception:
                pass

            _cb_log("_on_diagnose_finished END OK")
        except Exception as e:
            _cb_log(f"_on_diagnose_finished CRASH: {type(e).__name__}: {str(e)[:500]}")
            import traceback
            _cb_log(traceback.format_exc())
            logger.error(f"诊断完成回调崩溃: {type(e).__name__}: {str(e)}")
            try:
                self._restore_diagnose_btn(source_type)
            except Exception:
                pass
            try:
                self.log_append(f"⚠️ 诊断报告已生成但显示异常: {type(e).__name__}")
            except Exception:
                pass

    def _refresh_device_filters(self):
        ips = sorted(set(d.get("ip", "") for d in self.devices if d.get("ip")))
        for combo in [self.backup_filter_combo, self.report_filter_combo]:
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("全部设备")
            combo.addItems(ips)
            if current and (current in ips or current == "全部设备"):
                combo.setCurrentText(current)
            combo.blockSignals(False)

    def _get_backup_dir(self) -> str:
        return os.path.join(get_single_dir(), "config_backup")

    def _get_report_dir(self) -> str:
        return os.path.join(get_single_dir(), "report", "single_inspect")

    def refresh_backup_list(self):
        bdir = self._get_backup_dir()
        self.backup_file_list.blockSignals(True)
        self.backup_file_list.clear()
        if not os.path.isdir(bdir):
            self.backup_file_list.addItem(self._make_placeholder_item("暂无备份文件"))
            self.backup_file_list.blockSignals(False)
            return
        pattern = os.path.join(bdir, "*.*")
        files = sorted(glob_mod.glob(pattern), key=os.path.getmtime, reverse=True)
        filter_ip = self.backup_filter_combo.currentText()
        if filter_ip and filter_ip != "全部设备":
            files = [f for f in files if filter_ip in os.path.basename(f)]
        if not files:
            self.backup_file_list.addItem(self._make_placeholder_item("暂无匹配文件"))
            self.backup_file_list.blockSignals(False)
            return
        for fp in files:
            name = os.path.basename(fp)
            size_kb = os.path.getsize(fp) / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%m-%d %H:%M")
            item = QListWidgetItem(f"{name}\n  ({size_kb:.1f}KB · {mtime})")
            item.setToolTip(fp)
            item.setData(Qt.UserRole, fp)
            self.backup_file_list.addItem(item)
        self.backup_file_list.blockSignals(False)
        if self.backup_file_list.count() > 0:
            self.backup_file_list.setCurrentRow(0)

    def on_backup_filter_changed(self, _text: str):
        self.refresh_backup_list()

    def on_backup_file_selected(self, item: QListWidgetItem):
        if not item or not item.data(Qt.UserRole):
            self.backup_content.clear()
            self.backup_file_name_lbl.setText("未选择文件")
            self.ai_inspect_btn.setEnabled(False)
            return
        fp = item.data(Qt.UserRole)
        self.backup_file_name_lbl.setText(f"📄 {os.path.basename(fp)}")
        self.ai_inspect_btn.setEnabled(True)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if len(content) > 500000:
                self.backup_content.setPlainText(content[:500000] + f"\n\n... 文件过大，已截断显示（共 {len(content):,} 字符）")
            else:
                self.backup_content.setPlainText(content)
        except Exception as e:
            self.backup_content.setPlainText(f"读取失败：{str(e)}")

    def _select_backup_by_ip(self, ip: str):
        idx = self.backup_filter_combo.findText(ip)
        if idx >= 0:
            self.backup_filter_combo.setCurrentIndex(idx)
        self.refresh_backup_list()
        if self.backup_file_list.count() > 0:
            self.backup_file_list.setCurrentRow(0)

    def on_open_backup_file(self):
        item = self.backup_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        if os.path.exists(fp):
            os.startfile(fp)

    def on_delete_backup_file(self):
        item = self.backup_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "提示", "请先选择要删除的备份文件")
            return
        fp = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除该备份文件吗？\n{os.path.basename(fp)}",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(fp)
                self.refresh_backup_list()
            except Exception as e:
                QMessageBox.warning(self, "删除失败", str(e))

    def on_open_compliance_file(self):
        item = self.compliance_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        if os.path.exists(fp):
            os.startfile(fp)

    def on_open_report_file(self):
        item = self.report_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        if os.path.exists(fp):
            os.startfile(fp)

    def on_delete_report_file(self):
        item = self.report_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "提示", "请先选择要删除的报告文件")
            return
        fp = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除该报告文件吗？\n{os.path.basename(fp)}",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(fp)
                self.refresh_report_list()
            except Exception as e:
                QMessageBox.warning(self, "删除失败", str(e))

    def refresh_compliance_list(self):
        comp_dir = os.path.join(get_single_dir(), "report", "compliance")
        self.compliance_file_list.blockSignals(True)
        self.compliance_file_list.clear()
        if not os.path.isdir(comp_dir):
            self.compliance_file_list.addItem(self._make_placeholder_item("暂无审计报告"))
            self.compliance_file_list.blockSignals(False)
            return
        files = sorted(glob_mod.glob(os.path.join(comp_dir, "*.*")),
                       key=os.path.getmtime, reverse=True)
        if not files:
            self.compliance_file_list.addItem(self._make_placeholder_item("暂无审计报告"))
            self.compliance_file_list.blockSignals(False)
            return
        for fp in files:
            name = os.path.basename(fp)
            size_kb = os.path.getsize(fp) / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%m-%d %H:%M")
            label = f"{name}  ({size_kb:.1f}KB · {mtime})"
            item = QListWidgetItem(label)
            item.setToolTip(fp)
            item.setData(Qt.UserRole, fp)
            self.compliance_file_list.addItem(item)
        self.compliance_file_list.blockSignals(False)
        if files:
            self.compliance_file_list.setCurrentRow(0)

    def on_compliance_file_selected(self, current, previous):
        if not current or not current.data(Qt.UserRole):
            self.compliance_refine_btn.setEnabled(False)
            return
        self.compliance_refine_btn.setEnabled(True)
        fp = current.data(Qt.UserRole)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                report = f.read()
            styled = self._style_compliance_report(report)
            self.compliance_title_lbl.setText(f"📄 {os.path.basename(fp)}")
            self.compliance_content.setHtml(styled)
        except Exception as e:
            self.compliance_content.setPlainText(f"读取审计报告失败：{str(e)}")

    def on_open_compliance_dir(self):
        comp_dir = os.path.join(get_single_dir(), "report", "compliance")
        os.makedirs(comp_dir, exist_ok=True)
        os.startfile(comp_dir)

    def on_delete_compliance_file(self):
        item = self.compliance_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        name = os.path.basename(fp)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除审计报告「{name}」吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(fp)
            self.refresh_compliance_list()
            self.compliance_title_lbl.setText("未选择文件")
            self.compliance_content.clear()
            self.log_text.append(f"🗑 已删除审计报告：{name}")
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"无法删除文件：{str(e)}")

    def refresh_diagnosis_list(self):
        self.diagnosis_file_list.clear()
        ddir = os.path.join(get_single_dir(), "report", "diagnosis")
        os.makedirs(ddir, exist_ok=True)
        files = sorted(glob_mod.glob(os.path.join(ddir, "*.md")),
                       key=os.path.getmtime, reverse=True)
        for fpath in files[:50]:
            item = QListWidgetItem(f"{os.path.basename(fpath)} ({self._fmt_size(os.path.getsize(fpath))})")
            item.setData(Qt.UserRole, fpath)
            self.diagnosis_file_list.addItem(item)
        if files:
            self.diagnosis_file_list.setCurrentRow(0)

    def on_diagnosis_file_selected(self, current, previous):
        if not current or not current.data(Qt.UserRole):
            self.diagnosis_title_lbl.setText("未选择报告")
            return
        fp = current.data(Qt.UserRole)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.diagnosis_title_lbl.setText(f"📄 {os.path.basename(fp)}")
            self.diagnosis_content.setPlainText(content)
        except Exception as e:
            self.diagnosis_content.setPlainText(f"读取诊断报告失败：{str(e)}")

    def on_open_diagnosis_file(self):
        item = self.diagnosis_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        if os.path.exists(fp):
            os.startfile(fp)

    def on_delete_diagnosis_file(self):
        item = self.diagnosis_file_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        fp = item.data(Qt.UserRole)
        name = os.path.basename(fp)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除诊断报告「{name}」吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(fp)
            self.refresh_diagnosis_list()
            self.diagnosis_title_lbl.setText("未选择报告")
            self.diagnosis_content.clear()
            self.log_text.append(f"🗑 已删除诊断报告：{name}")
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"无法删除文件：{str(e)}")

    def _style_compliance_report(self, report: str) -> str:
        t = self._theme_engine.current_theme
        html = "<div style='font-family: Microsoft YaHei, sans-serif; line-height: 1.7;'>"
        lines = report.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("### CRITICAL") or "[CRITICAL-" in stripped:
                html += f"<p style='color: {t['danger']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### HIGH") or "[HIGH-" in stripped:
                html += f"<p style='color: {t['warning']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### MEDIUM") or "[MEDIUM-" in stripped:
                html += f"<p style='color: {t['warning']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("### LOW") or "[LOW-" in stripped:
                html += f"<p style='color: {t['text_tertiary']}; font-weight: bold; margin: 6px 0;'>{self._escape_html(line)}</p>"
            elif "Verdict:" in stripped or "判定:" in stripped:
                if "PASS" in stripped or "通过" in stripped:
                    html += f"<p style='color: {t['success']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['success_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                elif "BLOCK" in stripped or "阻止" in stripped:
                    html += f"<p style='color: {t['danger']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['danger_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                elif "WARNING" in stripped or "警告" in stripped:
                    html += f"<p style='color: {t['warning']}; font-weight: bold; font-size: 11pt; margin-top: 12px; padding: 10px; background: {t['warning_bg']}; border-radius: {t['radius_md']}px;'>{self._escape_html(line)}</p>"
                else:
                    html += f"<p style='margin: 4px 0;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("#"):
                html += f"<p style='color: {t['primary']}; font-weight: bold; font-size: 11pt; margin-top: 10px;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("|"):
                html += f"<p style='color: {t['text_secondary']}; margin: 2px 0; font-family: Consolas, monospace;'>{self._escape_html(line)}</p>"
            elif stripped.startswith("---"):
                html += f"<hr style='border: none; border-top: 1px solid {t['border']}; margin: 8px 0;'/>"
            else:
                html += f"<p style='margin: 2px 0; color: {t['text_main']};'>{self._escape_html(line)}</p>"
        html += "</div>"
        return html

    @staticmethod
    def _escape_html(text: str) -> str:
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;").replace(" ", "&nbsp;"))

    def refresh_report_list(self):
        rdir = self._get_report_dir()
        self.report_file_list.blockSignals(True)
        self.report_file_list.clear()
        if not os.path.isdir(rdir):
            self.report_file_list.addItem(self._make_placeholder_item("暂无巡检报告"))
            self.report_file_list.blockSignals(False)
            return
        pattern = os.path.join(rdir, "*.*")
        files = sorted(glob_mod.glob(pattern), key=os.path.getmtime, reverse=True)
        filter_ip = self.report_filter_combo.currentText()
        if filter_ip and filter_ip != "全部设备":
            files = [f for f in files if filter_ip in os.path.basename(f)]
        if not files:
            self.report_file_list.addItem(self._make_placeholder_item("暂无匹配报告"))
            self.report_file_list.blockSignals(False)
            return
        for fp in files:
            name = os.path.basename(fp)
            size_kb = os.path.getsize(fp) / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%m-%d %H:%M")
            item = QListWidgetItem(f"{name}\n  ({size_kb:.1f}KB · {mtime})")
            item.setToolTip(fp)
            item.setData(Qt.UserRole, fp)
            self.report_file_list.addItem(item)
        self.report_file_list.blockSignals(False)
        if files:
            self.report_file_list.setCurrentRow(0)

    def on_report_filter_changed(self, _text: str):
        self.refresh_report_list()

    def on_report_file_selected(self, item: QListWidgetItem):
        if not item or not item.data(Qt.UserRole):
            self.report_content.clear()
            self.report_title_lbl.setText("未选择报告")
            self.report_ai_btn.setEnabled(False)
            return
        fp = item.data(Qt.UserRole)
        self.report_title_lbl.setText(f"📄 {os.path.basename(fp)}")
        self.report_ai_btn.setEnabled(True)
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.report_content.setPlainText(content)
        except Exception as e:
            self.report_content.setPlainText(f"读取失败：{str(e)}")

    def _select_report_by_ip(self, ip: str):
        idx = self.report_filter_combo.findText(ip)
        if idx >= 0:
            self.report_filter_combo.setCurrentIndex(idx)
        self.refresh_report_list()
        if self.report_file_list.count() > 0:
            self.report_file_list.setCurrentRow(0)

    def on_open_report_dir(self):
        rdir = self._get_report_dir()
        os.makedirs(rdir, exist_ok=True)
        os.startfile(rdir)


    def _make_placeholder_item(self, text: str) -> QListWidgetItem:
        t = self._theme_engine.current_theme
        item = QListWidgetItem(text)
        item.setForeground(QColor(t['text_tertiary']))
        item.setFlags(Qt.NoItemFlags)
        return item
