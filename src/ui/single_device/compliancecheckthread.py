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
