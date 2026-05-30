#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目运维
提供批量备份、全网巡检、故障核查 + AI合规巡检/故障诊断 + 文件管理
"""

import json
import os
import sys
import ssl
import time
import glob as glob_mod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests
import certifi
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QTextEdit, QMessageBox,
                               QProgressBar, QComboBox, QTabWidget,
                               QListWidget, QListWidgetItem, QSplitter,
                               QFrame, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.utils.resource_path import get_config_path, get_app_dir, resource_path
from src.core.logger import netops_logger
from src.core.theme_engine import ThemeEngine
from src.core.local_audit_engine import LocalAuditEngine, AuditResult, Severity
from src.core.local_diagnostic_engine import LocalDiagnosticEngine, DiagResult, DiagSeverity
from src.utils.validators import ProjectValidator
from src.utils.file_operators import JSONFileManager
from src.ui.system_settings_page import get_active_ai_config

# 将 scripts 目录加入 sys.path，确保打包后 __import__ 能找到脚本模块
_SCRIPTS_DIR = resource_path("scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

PROJECTS_CONFIG: str = get_config_path("config/projects_config.json")

TASK_MODULES = {
    "backup": "scripts.backup_all_config",
    "inspect": "scripts.network_inspect",
    "trouble": "scripts.run_trouble_cmd",
}

TASK_NAMES = {"backup": "批量配置备份", "inspect": "全网自动化巡检", "trouble": "故障设备二次核查"}
TASK_ICONS = {"backup": "💾", "inspect": "🔍", "trouble": "🛠"}
AI_API_TIMEOUT = 120

TAB_BACKUP = 0
TAB_REPORT = 1
TAB_DIAGNOSIS = 2
TAB_COMPLIANCE = 3

def _btn_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {t['text_secondary']};
            border: 1px solid {t['border']};
            border-radius: {r}px;
            font-size: 10pt;
            padding: 4px 8px;
        }}
        QPushButton:hover {{ background-color: transparent; border-color: {t['border_deep']}; }}
    """


def _danger_btn_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {t['text_secondary']};
            border: 1px solid {t['border']};
            border-radius: {r}px;
            font-size: 10pt;
            padding: 4px 8px;
        }}
        QPushButton:hover {{
            background-color: transparent;
            border-color: {t['border']};
            color: {t['text_secondary']};
        }}
    """


def _ai_btn_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {t['text_secondary']};
            border: 1px solid {t['border']};
            border-radius: {r}px;
            font-size: 11pt;
            font-weight: bold;
            padding: 5px 8px;
        }}
        QPushButton:hover {{
            background-color: transparent;
            border-color: {t['border']};
            color: {t['text_secondary']};
        }}
        QPushButton:disabled {{
            background-color: transparent;
            color: {t['text_disabled']};
            border-color: {t['border']};
        }}
    """


def _primary_btn_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {r}px;
            font-size: 11pt;
            font-weight: bold;
            padding: 5px 8px;
        }}
        QPushButton:hover {{
            background-color: transparent;
            border-color: {t['border']};
        }}
        QPushButton:pressed {{
            background-color: transparent;
        }}
        QPushButton:disabled {{
            background-color: transparent;
            border-color: {t['border']};
            color: {t['text_tertiary']};
        }}
    """


def _list_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QListWidget {{
            border: 1px solid {t['border']};
            border-radius: {r}px;
            background-color: {t['card_bg']};
            font-size: 11pt;
            outline: none;
        }}
        QListWidget::item {{ padding: 5px 8px; }}
        QListWidget::item:selected {{ background-color: {t['selection_bg']}; color: {t['text_main']}; }}
        QListWidget::item:hover {{ background-color: {t['page_bg']}; }}
    """


def _preview_style(t: dict) -> str:
    r = t['radius_md']
    return f"""
        QTextEdit {{
            border: 1px solid {t['border']};
            border-radius: {r}px;
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10pt;
            background-color: {t['hover_bg']};
            color: {t['text_secondary']};
        }}
    """


class OpsWorkerThread(QThread):
    progress_signal = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, task_type: str, project_dir: str):
        super().__init__()
        self.task_type = task_type
        self.project_dir = Path(project_dir) if project_dir else None

    def _validate_task_type(self) -> bool:
        return self.task_type in TASK_MODULES

    def _validate_project_dir(self) -> bool:
        if not self.project_dir:
            return False
        return self.project_dir.exists() and self.project_dir.is_dir()

    def run(self):
        try:
            if not self._validate_task_type():
                self.error_signal.emit(f"未知的任务类型: {self.task_type}")
                return
            if not self._validate_project_dir():
                self.error_signal.emit("项目目录不存在或无效")
                return
            try:
                module_name = TASK_MODULES[self.task_type]
                module = __import__(module_name, fromlist=[''])
            except ImportError as e:
                self.error_signal.emit(f"无法加载任务模块: {str(e)}")
                return
            task_func_name = f"run_{self.task_type}"
            if not hasattr(module, task_func_name):
                self.error_signal.emit(f"任务模块缺少执行函数: {task_func_name}")
                return
            task_func = getattr(module, task_func_name)
            self.progress_signal.emit(0, 100, "任务初始化...")
            results = task_func(str(self.project_dir), progress_callback=self._progress)
            if not isinstance(results, list):
                self.error_signal.emit("任务执行返回结果格式错误")
                return
            self.finished_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(f"任务执行失败: {str(e)}")

    def _progress(self, current: int, total: int, message: str):
        self.progress_signal.emit(current, total, message)


class OpsComplianceThread(QThread):
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
        self._local_result = None

    def _run_local_audit(self) -> AuditResult:
        engine = LocalAuditEngine()
        return engine.audit(self.config_content, self.device_ip, self.vendor_hint)

    def _build_local_only_report(self, local_result: AuditResult) -> str:
        SEV_CN = {
            Severity.CRITICAL: "严重", Severity.HIGH: "高危",
            Severity.MEDIUM: "中危", Severity.LOW: "低危",
        }
        lines = [f"## 本地合规审计结果（结论：{local_result.verdict}）"]
        c, h, m, l = local_result.critical_count, local_result.high_count, local_result.medium_count, local_result.low_count
        lines.append(f"| 严重 | 高危 | 中危 | 低危 | 合计 |")
        lines.append(f"| :--: | :--: | :--: | :--: | :--: |")
        lines.append(f"| {c} | {h} | {m} | {l} | {local_result.total_findings} |")
        lines.append("")
        for f in local_result.findings:
            cn = SEV_CN.get(f.severity, "")
            lines.append(f"- **[{f.id}]** [{cn}] {f.title}：{f.issue}")
        return "\n".join(lines)

    def run(self):
        try:
            # ── Layer 1: 本地合规审计 ──
            self.progress_signal.emit("Layer 1/2: 本地合规审计引擎启动...")
            t0 = time.time()
            local_result = self._run_local_audit()
            self._local_result = local_result
            local_ms = int((time.time() - t0) * 1000)

            self.progress_signal.emit(
                f"本地审计完成 ({local_ms}ms): {local_result.total_findings} 个问题，结论: {local_result.verdict}"
            )

            local_display = self._build_local_only_report(local_result)
            self.local_result_signal.emit(local_display)

            # 判断是否需要AI精审
            needs_ai = (
                local_result.critical_count > 0 or
                local_result.high_count >= 2 or
                (local_result.high_count > 0 and local_result.medium_count > 1)
            )

            if not needs_ai:
                self.progress_signal.emit(f"本地审计结论：{local_result.verdict} — 无需AI精审")
                report = (
                    f"# 合规巡检报告\n\n"
                    f"## 设备IP: {self.device_ip}\n"
                    f"## 巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 审计模式: 本地规则引擎（配置安全，跳过AI精审）\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
                return

            if not self.ai_config.get('base_url') or not self.ai_config.get('api_key'):
                self.progress_signal.emit("AI未配置 — 仅显示本地审计结果")
                report = (
                    f"# 合规巡检报告\n\n"
                    f"## 设备IP: {self.device_ip}\n"
                    f"## 巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 审计模式: 仅本地审计（AI未配置）\n\n"
                    f"> 提示：请在【⚙ 模型设置】中配置AI模型以启用AI精审功能\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
                return

            # ── Layer 2: AI精审 ──
            self.progress_signal.emit("Layer 2/2: 调用AI进行合规精审...")

            reviewer_path = os.path.join(get_app_dir(), "agents", "network-config-reviewer.md")
            if os.path.exists(reviewer_path):
                with open(reviewer_path, "r", encoding="utf-8") as f:
                    reviewer_rules = f.read()
            else:
                reviewer_rules = "你是网络配置合规审计专家，请用中文输出审计报告。"

            local_context = local_result.to_ai_prompt_context()

            # 精准提取问题配置周边上下文（替代全文截断，减少token）
            relevant_context = ""
            if local_result.total_findings > 0:
                relevant_context = local_result.extract_relevant_context(self.config_content, context_lines=6)

            prompt = (
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
                f"4. 使用标准格式输出最终审计报告"
            )

            url = f"{self.ai_config['base_url'].rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.ai_config['api_key']}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.ai_config["model"],
                "messages": [
                    {"role": "system", "content": reviewer_rules},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 4096
            }

            self.progress_signal.emit("正在发送AI合规巡检请求...")
            resp = requests.post(url, headers=headers, json=payload, timeout=AI_API_TIMEOUT)
            if resp.status_code == 200:
                ai_result = resp.json()["choices"][0]["message"]["content"]
                report = (
                    f"# AI 合规巡检报告\n\n"
                    f"## 设备IP: {self.device_ip}\n"
                    f"## 巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 使用模型: {self.ai_config.get('model', 'N/A')}\n"
                    f"## 审计模式: 双层审计（本地规则 + AI精审）\n\n"
                    f"--- 第一层：本地规则引擎结果 ---\n"
                    f"{local_result.to_summary_text()}\n\n"
                    f"--- 第二层：AI精审分析 ---\n"
                    f"{ai_result}"
                )
                self.finished_signal.emit(report)
            else:
                self.progress_signal.emit(f"AI服务错误 {resp.status_code} — 降级使用本地审计结果")
                report = (
                    f"# 合规巡检报告\n\n"
                    f"## 设备IP: {self.device_ip}\n"
                    f"## 巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 审计模式: 仅本地审计（AI服务异常 HTTP {resp.status_code}）\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
        except Exception as e:
            if self._local_result:
                self.progress_signal.emit("AI精审异常 — 降级使用本地审计结果")
                report = (
                    f"# 合规巡检报告\n\n"
                    f"## 设备IP: {self.device_ip}\n"
                    f"## 巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 审计模式: 仅本地审计（AI精审异常: {type(e).__name__}）\n\n"
                    f"{self._build_local_only_report(self._local_result)}"
                )
                self.finished_signal.emit(report)
            else:
                self.error_signal.emit(f"巡检异常: {type(e).__name__}: {str(e)}")


class OpsDiagnosticThread(QThread):
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
        self._local_diag_result = None
        try:
            _cert_path = certifi.where()
            if os.path.isfile(_cert_path):
                self._session.verify = _cert_path
            else:
                self._session.verify = True
        except Exception:
            self._session.verify = True

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
                    df.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [OPS] {msg}\n")
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

            self.progress_signal.emit(
                f"本地诊断完成 ({local_ms}ms): {local_result.total_findings} 个异常，结论: {local_result.verdict}"
            )

            local_display = local_result.to_summary_text()
            self.local_result_signal.emit(local_display)

            # 判断是否需要AI精审
            needs_ai = (
                local_result.critical_count > 0 or
                local_result.high_count >= 2 or
                (local_result.high_count > 0 and local_result.medium_count > 1)
            )

            if not needs_ai and local_result.total_findings == 0:
                self.progress_signal.emit("本地诊断未发现异常，跳过AI精审")
                report = (
                    f"# 故障诊断报告\n\n"
                    f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 诊断模式: 本地运行时诊断（未发现异常，跳过AI精审）\n\n"
                    f"{local_display}"
                )
                self.finished_signal.emit(report)
                return

            if not self.ai_config.get('base_url') or not self.ai_config.get('api_key'):
                self.progress_signal.emit("AI未配置 — 仅显示本地诊断结果")
                source_hints = {
                    "backup": "配置备份", "report": "巡检报告",
                    "compliance": "合规审计", "log": "操作日志",
                }
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
                return

            # ── Layer 2: AI精审 ──
            self.progress_signal.emit("Layer 2/2: 调用AI进行深度故障诊断...")

            troubleshooter_path = os.path.join(get_app_dir(), "agents", "network-troubleshooter.md")
            if os.path.exists(troubleshooter_path):
                with open(troubleshooter_path, "r", encoding="utf-8") as f:
                    system_prompt = f.read()
                _dbg(f"agent file loaded, len={len(system_prompt)}")
            else:
                system_prompt = "你是资深网络工程师，专精于结构化故障排查。通过OSI分层逐层诊断网络问题。"
                _dbg("agent file NOT found, using fallback prompt")

            source_hints = {
                "backup": "以下是一台网络设备的配置备份文件，请分析其中可能存在的故障隐患：",
                "report": "以下是一份网络设备巡检报告，请分析其中的异常指标和潜在故障风险：",
                "compliance": "以下是一份合规审计报告，请对发现的问题进行二次诊断：",
                "log": "以下是设备巡检/操作日志，请根据日志内容进行故障诊断分析：",
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
            headers = {
                "Authorization": f"Bearer {self.ai_config['api_key']}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {
                "model": self.ai_config["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 4000
            }

            self.progress_signal.emit("正在发送AI诊断请求...")
            _dbg(f"sending POST to {url}, model={self.ai_config.get('model','?')}")
            resp = self._session.post(url, headers=headers, json=payload, timeout=AI_API_TIMEOUT)
            _dbg(f"response status={resp.status_code}")

            if resp.status_code == 200:
                try:
                    ai_result = resp.json()["choices"][0]["message"]["content"]
                except (KeyError, IndexError, ValueError) as parse_err:
                    _dbg(f"JSON parse error: {parse_err}")
                    self.progress_signal.emit("AI返回数据解析失败 — 降级使用本地诊断结果")
                    report = self._build_local_only_report(local_result, source_hints)
                    self.finished_signal.emit(report)
                    return

                report = (
                    f"# AI 故障诊断报告\n\n"
                    f"## 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"## 使用模型: {self.ai_config.get('model', 'N/A')}\n"
                    f"## 诊断模式: 双层诊断（本地运行时诊断 + AI精审）\n\n"
                    f"--- 第一层：本地运行时诊断结果 ---\n"
                    f"{local_result.to_summary_text()}\n\n"
                    f"--- 第二层：AI深度诊断 ---\n"
                    f"{ai_result}"
                )
                _dbg("diagnosis report generated")
                self.finished_signal.emit(report)
            else:
                _dbg(f"http error {resp.status_code}: {resp.text[:200]}")
                self.progress_signal.emit(f"AI服务错误 {resp.status_code} — 降级使用本地诊断结果")
                report = self._build_local_only_report(local_result, source_hints)
                self.finished_signal.emit(report)
        except Exception as e:
            _dbg(f"UNEXPECTED EXCEPTION: {type(e).__name__}: {str(e)[:500]}")
            import traceback
            _dbg(traceback.format_exc())
            if self._local_diag_result:
                self.progress_signal.emit("AI诊断异常 — 降级使用本地诊断结果")
                source_hints = {
                    "backup": "配置备份", "report": "巡检报告",
                    "compliance": "合规审计", "log": "操作日志",
                }
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


class TaskCard(QGroupBox):
    def __init__(self, task_type: str, parent_page):
        super().__init__(TASK_ICONS.get(task_type, "") + " " + TASK_NAMES.get(task_type, task_type))
        self.task_type = task_type
        self.parent_page = parent_page
        self.worker = None
        self._running = False
        self._last_run_time = ""
        self._theme_engine = ThemeEngine.get()

        self.setStyleSheet(self._card_style())
        self.setMinimumWidth(280)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(6, 12, 6, 6)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {self._theme_engine.current_theme['text_tertiary']}; font-weight: normal;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setStyleSheet(self._progress_style())
        layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("▶ 执行")
        self.run_btn.setFixedHeight(26)
        self.run_btn.setStyleSheet(_primary_btn_style(self._theme_engine.current_theme))
        self.run_btn.clicked.connect(self._run_task)
        btn_row.addWidget(self.run_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _run_task(self):
        project_dir = self.parent_page._get_project_dir()
        if not project_dir:
            QMessageBox.warning(self, "提示", "请先在顶部选择一个项目")
            return
        device_file = os.path.join(project_dir, "config", "device_list.txt")
        if not os.path.exists(device_file):
            QMessageBox.warning(self, "提示", f"项目设备清单不存在：\n{device_file}")
            return

        self._running = True
        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在执行...")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {self._theme_engine.current_theme['primary']}; font-weight: normal;")

        self.worker = OpsWorkerThread(self.task_type, project_dir)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, current, total, message):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"{current}/{total} - {message}")

    def _on_finished(self, results):
        self._running = False
        self.run_btn.setEnabled(True)
        self.progress_bar.setValue(self.progress_bar.maximum())
        self._last_run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status_label.setText(f"完成 ✅ {self._last_run_time}")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {self._theme_engine.current_theme['success']}; font-weight: normal;")
        self.parent_page._on_task_completed(self.task_type)

    def _on_error(self, error_msg):
        self._running = False
        self.run_btn.setEnabled(True)
        self.status_label.setText("执行出错 ❌")
        self.status_label.setStyleSheet(f"font-size: 10pt; color: {self._theme_engine.current_theme['danger']}; font-weight: normal;")
        QMessageBox.critical(self, "任务执行失败", f"执行过程中出现错误：\n\n{error_msg}")

    def _card_style(self) -> str:
        t = self._theme_engine.current_theme
        r = t['radius_lg']
        return f"""
            QGroupBox {{
                font-size: 11pt;
                font-weight: bold;
                color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {r}px;
                margin-top: 10px;
                padding: 14px 12px 10px 12px;
                background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """

    def _progress_style(self) -> str:
        t = self._theme_engine.current_theme
        r = t['radius_sm']
        return f"""
            QProgressBar {{
                border: 1px solid {t['border']};
                border-radius: {r}px;
                text-align: center;
                background-color: {t['page_bg']};
                font-size: 10pt;
            }}
            QProgressBar::chunk {{
                background-color: {t['page_bg']};
                border-radius: {r}px;
            }}
        """


class FileResultTab(QWidget):
    def __init__(self, tab_name: str, scan_dir_key: str, parent_page):
        super().__init__()
        self.tab_name = tab_name
        self.scan_dir_key = scan_dir_key
        self.parent_page = parent_page
        self._theme_engine = ThemeEngine.get()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(3)
        t = self._theme_engine.current_theme
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet(_btn_style(t))
        self.refresh_btn.clicked.connect(self._refresh_list)
        btn_row.addWidget(self.refresh_btn)
        self.open_btn = QPushButton("📂 打开")
        self.open_btn.setStyleSheet(_btn_style(t))
        self.open_btn.clicked.connect(self._open_file)
        btn_row.addWidget(self.open_btn)
        self.del_btn = QPushButton("🗑 删除")
        self.del_btn.setStyleSheet(_danger_btn_style(t))
        self.del_btn.clicked.connect(self._delete_file)
        btn_row.addWidget(self.del_btn)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(_list_style(t))
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.currentItemChanged.connect(self._on_file_selected)
        self.file_list.setMinimumWidth(200)
        left_layout.addWidget(self.file_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(_preview_style(t))
        self.preview_text.setPlaceholderText("选择左侧文件查看内容")
        right_layout.addWidget(self.preview_text)

        self.ai_btn_layout = QHBoxLayout()
        self.ai_btn_layout.setSpacing(6)
        self.ai_btn_layout.addStretch()

        if tab_name in ("💾备份文件",):
            self.compliance_btn = QPushButton("🔍 AI合规巡检")
            self.compliance_btn.setStyleSheet(_ai_btn_style(t))
            self.compliance_btn.clicked.connect(self._run_compliance_check)
            self.ai_btn_layout.addWidget(self.compliance_btn)

        if tab_name in ("📊巡检报告", "🩺诊断报告"):
            self.diagnose_btn = QPushButton("🩺 AI故障诊断")
            self.diagnose_btn.setStyleSheet(_ai_btn_style(t))
            self.diagnose_btn.clicked.connect(self._run_diagnose)
            self.ai_btn_layout.addWidget(self.diagnose_btn)

        if tab_name in ("🔍合规审计",):
            self.deep_audit_btn = QPushButton("🩺 AI精审")
            self.deep_audit_btn.setStyleSheet(_ai_btn_style(t))
            self.deep_audit_btn.clicked.connect(self._run_deep_audit)
            self.ai_btn_layout.addWidget(self.deep_audit_btn)

        right_layout.addLayout(self.ai_btn_layout)
        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def _get_scan_dirs(self):
        project_dir = self.parent_page._get_project_dir()
        if not project_dir:
            return []
        base_map = {
            "backup": [os.path.join(project_dir, "config_backup")],
            "report": [
                os.path.join(project_dir, "report"),
                os.path.join(project_dir, "output", "trouble_check_result"),
                os.path.join(project_dir, "output", "single_exception"),
            ],
            "diagnosis": [os.path.join(project_dir, "report", "diagnosis")],
            "compliance": [os.path.join(project_dir, "report", "compliance")],
        }
        dirs = base_map.get(self.scan_dir_key, [])
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
        return dirs

    def refresh_list(self):
        scan_dirs = self._get_scan_dirs()
        self.file_list.clear()
        all_files = []
        seen = set()
        for scan_dir in scan_dirs:
            if not scan_dir or not os.path.exists(scan_dir):
                continue
            for f in glob_mod.glob(os.path.join(scan_dir, "**/*"), recursive=True):
                if os.path.isfile(f) and f not in seen:
                    seen.add(f)
                    all_files.append(f)
        all_files.sort(key=os.path.getmtime, reverse=True)
        for f in all_files:
            item = QListWidgetItem(os.path.basename(f))
            item.setData(Qt.UserRole, f)
            self.file_list.addItem(item)

    def _refresh_list(self):
        self.refresh_list()

    def _open_file(self):
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选中一个文件")
            return
        file_path = item.data(Qt.UserRole)
        if os.path.exists(file_path):
            os.startfile(file_path)

    def _delete_file(self):
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选中要删除的文件")
            return
        file_path = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认删除",
            f"确定要删除文件吗？\n{os.path.basename(file_path)}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(file_path)
            self.refresh_list()
            self.preview_text.clear()
        except Exception as e:
            QMessageBox.critical(self, "删除失败", str(e))

    def _on_file_selected(self, current, previous):
        if not current:
            return
        file_path = current.data(Qt.UserRole)
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.preview_text.setPlainText(content)
        except Exception as e:
            self.preview_text.setPlainText(f"无法读取文件：{str(e)}")

    def _get_selected_content(self) -> tuple:
        item = self.file_list.currentItem()
        if not item:
            return "", ""
        file_path = item.data(Qt.UserRole)
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return os.path.basename(file_path), content
        except Exception:
            return "", ""

    def _run_compliance_check(self):
        filename, content = self._get_selected_content()
        if not content:
            QMessageBox.information(self, "提示", "请先选中一个备份文件")
            return
        ai_config = get_active_ai_config()
        if not ai_config or not ai_config.get("api_key"):
            QMessageBox.warning(self, "提示", "请先在「模型设置」中配置AI模型")
            return
        device_ip = filename.replace(".txt", "").replace(".cfg", "").replace("backup_", "")
        self.parent_page._ai_compliance_thread = OpsComplianceThread(content, device_ip, ai_config)
        self.parent_page._ai_compliance_thread.progress_signal.connect(
            lambda msg: self.preview_text.setPlainText(msg))
        self.parent_page._ai_compliance_thread.local_result_signal.connect(
            lambda result: self.preview_text.setPlainText(f"📋 本地预检完成，等待AI精审...\n\n{result}"))
        self.parent_page._ai_compliance_thread.finished_signal.connect(
            self._on_compliance_done)
        self.parent_page._ai_compliance_thread.error_signal.connect(
            lambda err: self.preview_text.setPlainText(f"错误：{err}"))
        self.parent_page._ai_compliance_thread.start()

    def _on_compliance_done(self, report):
        project_dir = self.parent_page._get_project_dir()
        if project_dir:
            comp_dir = os.path.join(project_dir, "report", "compliance")
            os.makedirs(comp_dir, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = os.path.join(comp_dir, f"compliance_{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
        self.preview_text.setPlainText(report)
        self.parent_page.switch_to_tab(TAB_COMPLIANCE)

    def _run_diagnose(self):
        filename, content = self._get_selected_content()
        if not content:
            QMessageBox.information(self, "提示", "请先选中一个报告文件")
            return
        ai_config = get_active_ai_config()
        if not ai_config or not ai_config.get("api_key"):
            QMessageBox.warning(self, "提示", "请先在「模型设置」中配置AI模型")
            return
        source_type = "report"
        if self.tab_name == "🩺诊断报告":
            source_type = "compliance"
        if hasattr(self, 'diagnose_btn'):
            self.diagnose_btn.setEnabled(False)
            self.diagnose_btn.setText("⏳ 诊断中...")
        self.preview_text.setPlainText("正在调用AI故障诊断引擎，请稍候...")
        self.parent_page._ai_diagnostic_thread = OpsDiagnosticThread(content, source_type, ai_config)
        self.parent_page._ai_diagnostic_thread.progress_signal.connect(
            lambda msg: self.preview_text.setPlainText(msg))
        self.parent_page._ai_diagnostic_thread.local_result_signal.connect(
            lambda result: self.preview_text.setPlainText(f"📋 本地诊断完成，等待AI精审...\n\n{result}"))
        self.parent_page._ai_diagnostic_thread.finished_signal.connect(
            self._on_diagnose_done)
        self.parent_page._ai_diagnostic_thread.error_signal.connect(
            lambda err: self._on_diagnose_error(err))
        self.parent_page._ai_diagnostic_thread.start()

    def _on_diagnose_error(self, err: str):
        self.preview_text.setPlainText(f"❌ 错误：{err}")
        if hasattr(self, 'diagnose_btn'):
            self.diagnose_btn.setEnabled(True)
            self.diagnose_btn.setText("🩺 AI故障诊断")
        QMessageBox.warning(self, "AI诊断失败", f"故障诊断过程中出现错误：\n\n{err}")

    def _on_diagnose_done(self, report):
        project_dir = self.parent_page._get_project_dir()
        if project_dir:
            diag_dir = os.path.join(project_dir, "report", "diagnosis")
            os.makedirs(diag_dir, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = os.path.join(diag_dir, f"diagnosis_{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
        self.preview_text.setPlainText(report)
        if hasattr(self, 'diagnose_btn'):
            self.diagnose_btn.setEnabled(True)
            self.diagnose_btn.setText("🩺 AI故障诊断")
        self.parent_page.switch_to_tab(TAB_DIAGNOSIS)

    def _run_deep_audit(self):
        filename, content = self._get_selected_content()
        if not content:
            QMessageBox.information(self, "提示", "请先选中一个审计报告文件")
            return
        ai_config = get_active_ai_config()
        if not ai_config or not ai_config.get("api_key"):
            QMessageBox.warning(self, "提示", "请先在「模型设置」中配置AI模型")
            return
        self.parent_page._ai_compliance_thread = OpsComplianceThread(content, "审计精审", ai_config)
        self.parent_page._ai_compliance_thread.progress_signal.connect(
            lambda msg: self.preview_text.setPlainText(msg))
        self.parent_page._ai_compliance_thread.local_result_signal.connect(
            lambda result: self.preview_text.setPlainText(f"📋 本地预检完成，等待AI精审...\n\n{result}"))
        self.parent_page._ai_compliance_thread.finished_signal.connect(
            self._on_compliance_done)
        self.parent_page._ai_compliance_thread.error_signal.connect(
            lambda err: self.preview_text.setPlainText(f"错误：{err}"))
        self.parent_page._ai_compliance_thread.start()


class OpsToolboxPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._ai_compliance_thread = None
        self._ai_diagnostic_thread = None
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("项目运维")
        self.title_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {self._theme_engine.current_theme['text_main']}; text-decoration: none;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.proj_label = QLabel("项目：")
        self.proj_label.setStyleSheet(f"font-size: 11pt; color: {self._theme_engine.current_theme['text_secondary']}; font-weight: normal;")
        header_layout.addWidget(self.proj_label)

        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(280)
        self.project_combo.setStyleSheet(self._combo_style())
        header_layout.addWidget(self.project_combo)

        self.refresh_btn = QPushButton("🔄 刷新项目")
        self.refresh_btn.setFixedSize(88, 28)
        self.refresh_btn.setStyleSheet(_btn_style(self._theme_engine.current_theme))
        self.refresh_btn.clicked.connect(self._refresh_projects)
        header_layout.addWidget(self.refresh_btn)
        layout.addLayout(header_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)
        self.backup_card = TaskCard("backup", self)
        cards_layout.addWidget(self.backup_card)
        self.inspect_card = TaskCard("inspect", self)
        cards_layout.addWidget(self.inspect_card)
        self.trouble_card = TaskCard("trouble", self)
        cards_layout.addWidget(self.trouble_card)
        cards_layout.addStretch()
        layout.addLayout(cards_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._tab_style())

        self.backup_tab = FileResultTab("💾备份文件", "backup", self)
        self.report_tab = FileResultTab("📊巡检报告", "report", self)
        self.diagnosis_tab = FileResultTab("🩺诊断报告", "diagnosis", self)
        self.compliance_tab = FileResultTab("🔍合规审计", "compliance", self)

        self.tab_widget.addTab(self.backup_tab, "💾备份文件")
        self.tab_widget.addTab(self.report_tab, "📊巡检报告")
        self.tab_widget.addTab(self.diagnosis_tab, "🩺诊断报告")
        self.tab_widget.addTab(self.compliance_tab, "🔍合规审计")

        layout.addWidget(self.tab_widget)

        self.desc_label = QLabel("三个运维任务独立运行，所有操作仅执行只读指令。AI分析结果自动归档到项目 report/ 目录。")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(f"font-size: 10pt; color: {self._theme_engine.current_theme['text_tertiary']}; padding: 2px 0;")
        layout.addWidget(self.desc_label)

        self.setLayout(layout)

    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()

    def _apply_theme_style(self) -> None:
        if self._theme_engine is None:
            return
        t = self._theme_engine.current_theme
        self.setStyleSheet(f"""
            OpsToolboxPage {{
                background-color: {t['page_bg']};
                font-family: {t['font_ui']};
            }}
        """)
        if hasattr(self, 'project_combo'):
            self.project_combo.setStyleSheet(self._combo_style())
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setStyleSheet(self._tab_style())
        # 标题和描述标签
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(
                f"font-size: 14pt; font-weight: bold; color: {t['text_main']}; text-decoration: none;")
        if hasattr(self, 'proj_label'):
            self.proj_label.setStyleSheet(
                f"font-size: 11pt; color: {t['text_secondary']}; font-weight: normal;")
        if hasattr(self, 'desc_label'):
            self.desc_label.setStyleSheet(
                f"font-size: 10pt; color: {t['text_tertiary']}; padding: 2px 0;")
        # 刷新按钮
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setStyleSheet(_btn_style(t))
        # 三个任务卡片
        if hasattr(self, 'backup_card'):
            self._refresh_task_card(self.backup_card)
        if hasattr(self, 'inspect_card'):
            self._refresh_task_card(self.inspect_card)
        if hasattr(self, 'trouble_card'):
            self._refresh_task_card(self.trouble_card)
        # 四个结果Tab
        if hasattr(self, 'backup_tab'):
            self._refresh_file_tab(self.backup_tab)
        if hasattr(self, 'report_tab'):
            self._refresh_file_tab(self.report_tab)
        if hasattr(self, 'diagnosis_tab'):
            self._refresh_file_tab(self.diagnosis_tab)
        if hasattr(self, 'compliance_tab'):
            self._refresh_file_tab(self.compliance_tab)

    def _refresh_task_card(self, card) -> None:
        """刷新单个 TaskCard 的样式"""
        card.setStyleSheet(card._card_style())
        t = self._theme_engine.current_theme
        if hasattr(card, 'status_label'):
            card.status_label.setStyleSheet(
                f"font-size: 10pt; color: {t['text_tertiary']}; font-weight: normal;")
        if hasattr(card, 'progress_bar'):
            card.progress_bar.setStyleSheet(card._progress_style())
        if hasattr(card, 'run_btn'):
            card.run_btn.setStyleSheet(_primary_btn_style(t))

    def _refresh_file_tab(self, tab) -> None:
        """刷新单个 FileResultTab 的样式"""
        t = self._theme_engine.current_theme
        for attr in ('refresh_btn', 'open_btn'):
            btn = getattr(tab, attr, None)
            if btn is not None:
                btn.setStyleSheet(_btn_style(t))
        del_btn = getattr(tab, 'del_btn', None)
        if del_btn is not None:
            del_btn.setStyleSheet(_danger_btn_style(t))
        if hasattr(tab, 'file_list'):
            tab.file_list.setStyleSheet(_list_style(t))
        if hasattr(tab, 'preview_text'):
            tab.preview_text.setStyleSheet(_preview_style(t))
        # AI 按钮
        for attr in ('compliance_btn', 'diagnose_btn', 'deep_audit_btn'):
            btn = getattr(tab, attr, None)
            if btn is not None:
                btn.setStyleSheet(_ai_btn_style(t))
        # QSplitter handle 颜色（中间竖线）
        for sp in tab.findChildren(QSplitter):
            sp.setStyleSheet(
                f"QSplitter::handle {{ background-color: {t['border']}; }}"
                f"QSplitter::handle:horizontal {{ width: 2px; }}"
                f"QSplitter::handle:vertical {{ height: 2px; }}"
            )
        # Tab 内 QLabel（"设备筛选：" 等）
        for lbl in tab.findChildren(QLabel):
            lbl.setStyleSheet(f"font-size: 10pt; color: {t['text_tertiary']};")

    def _combo_style(self) -> str:
        t = self._theme_engine.current_theme
        r = t['radius_md']
        return f"""
            QComboBox {{
                border: 1px solid {t['input_border']}; border-radius: {r}px;
                padding: 4px 8px; font-size: 11pt; background-color: {t['card_bg']};
            }}
            QComboBox:hover {{ border: 1px solid {t['border']}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                border: 1px solid {t['border']}; selection-background-color: {t['selection_bg']};
                outline: none;
            }}
        """

    def _tab_style(self) -> str:
        t = self._theme_engine.current_theme
        r = t['radius_md']
        return f"""
            QTabWidget::pane {{
                border: 1px solid {t['border']};
                border-radius: {r}px;
                background-color: {t['card_bg']};
            }}
            QTabBar::tab {{
                border: 1px solid {t['border']};
                padding: 8px 20px;
                font-size: 11pt;
                background-color: {t['page_bg']};
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['card_bg']};
                border-bottom-color: {t['card_bg']};
                font-weight: bold;
                color: {t['text_secondary']};
            }}
            QTabBar::tab:hover {{ background-color: {t['selection_bg']}; }}
        """

    def _refresh_projects(self):
        current = self.project_combo.currentText()
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("-- 请选择项目 --", "")
        try:
            config = JSONFileManager.load_json(PROJECTS_CONFIG, {"projects": {}})
            projects = config.get("projects", {})
            for name, project_info in projects.items():
                if isinstance(project_info, dict):
                    path = project_info.get("path", "")
                else:
                    path = project_info
                if path:
                    is_valid, _ = ProjectValidator.validate_project_path(path)
                    if is_valid:
                        self.project_combo.addItem(name, path)
            logger = netops_logger.get_logger()
            logger.info(f"运维工具箱刷新项目列表，找到 {len(projects)} 个项目")
        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"刷新项目列表失败: {e}")
        if current:
            idx = self.project_combo.findText(current)
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
        self.project_combo.blockSignals(False)

    def _get_project_dir(self) -> Optional[str]:
        idx = self.project_combo.currentIndex()
        if idx <= 0:
            return None
        return self.project_combo.currentData()

    def _on_task_completed(self, task_type: str):
        tab_map = {"backup": TAB_BACKUP, "inspect": TAB_REPORT, "trouble": TAB_REPORT}
        target_tab = tab_map.get(task_type, TAB_REPORT)
        self.switch_to_tab(target_tab)

    def switch_to_tab(self, index: int):
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
        self._refresh_all_tabs()

    def _refresh_all_tabs(self):
        self.backup_tab.refresh_list()
        self.report_tab.refresh_list()
        self.diagnosis_tab.refresh_list()
        self.compliance_tab.refresh_list()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_projects()
        self._refresh_all_tabs()