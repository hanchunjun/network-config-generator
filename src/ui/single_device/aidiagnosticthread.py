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
