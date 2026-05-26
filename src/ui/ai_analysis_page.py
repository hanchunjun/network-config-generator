#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI专家工作站
提供自由对话、合规审计、故障诊断 + Agent快捷指令 + 多文件输入
"""

import json
import os
import ssl
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QComboBox, QGroupBox, QTextEdit,
                               QMessageBox, QFileDialog, QProgressBar,
                               QLineEdit, QMenu, QAction, QListWidget,
                               QListWidgetItem, QSplitter, QFrame,
                               QTabWidget, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from src.utils.resource_path import get_config_path, get_app_dir, get_single_dir
from src.core.local_audit_engine import LocalAuditEngine, AuditResult, Severity
from src.core.local_diagnostic_engine import LocalDiagnosticEngine, DiagResult, DiagSeverity
from src.core.theme_engine import ThemeEngine
from src.ui.system_settings_page import get_active_ai_config

PROJECTS_CONFIG: str = get_config_path("config/projects_config.json")
RECENT_FILES_PATH: str = get_config_path("config/ai_recent_files.json")

AI_API_TIMEOUT = 120
MAX_CONTENT_LENGTH = 10000


class DropTextEdit(QTextEdit):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.file_dropped.emit(file_path)


class ExpertAnalysisThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    local_result_signal = pyqtSignal(str)

    def __init__(self, system_prompt: str, user_prompt: str, ai_config: Dict[str, Any],
                 tab_key: str = "", content_files: str = ""):
        super().__init__()
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.ai_config = ai_config
        self.tab_key = tab_key
        self.content_files = content_files
        self._local_result = None

    def _run_local_pre_check(self) -> str:
        """根据tab_key执行不同的本地预诊断，返回精简摘要 + 精准上下文"""
        if not self.content_files:
            return ""

        if self.tab_key == "compliance":
            # 合规审计：使用 LocalAuditEngine
            engine = LocalAuditEngine()
            result = engine.audit(self.content_files, "", "")
            self._local_result = result
            if result.total_findings > 0:
                summary = result.to_ai_prompt_context()
                relevant = result.extract_relevant_context(self.content_files, context_lines=6)
                ctx_block = f"\n## 问题相关配置上下文（精准提取）\n```\n{relevant}\n```\n" if relevant else ""
                return f"\n## 本地合规预检结果\n{summary}{ctx_block}\n"
            return ""
        elif self.tab_key in ("diagnose", "free"):
            # 故障诊断：使用 LocalDiagnosticEngine
            source_type = "report" if self.tab_key == "diagnose" else "log"
            engine = LocalDiagnosticEngine()
            result = engine.diagnose(self.content_files, source_type)
            self._local_result = result
            if result.total_findings > 0:
                # 精简摘要 + 精准上下文提取
                summary = result.to_ai_prompt_context()
                relevant = result.extract_relevant_context(self.content_files, context_lines=8)
                ctx_block = f"\n## 异常相关上下文（精准提取）\n```\n{relevant}\n```\n" if relevant else ""
                return f"\n## 本地运行时预诊断结果\n{summary}{ctx_block}\n"
            return ""
        return ""

    def run(self):
        try:
            if not self.ai_config.get("base_url") or not self.ai_config.get("api_key"):
                self.error_signal.emit("AI配置不完整")
                return

            # ── Layer 1: 本地预诊断（合规/诊断模式） ──
            local_context = ""
            if self.tab_key in ("compliance", "diagnose") and self.content_files:
                self.progress_signal.emit("Layer 1/2: 本地预诊断引擎启动...")
                t0 = time.time()
                local_context = self._run_local_pre_check()
                local_ms = int((time.time() - t0) * 1000)

                if local_context:
                    self.progress_signal.emit(f"本地预诊断完成 ({local_ms}ms)，发现异常，继续AI精审...")
                    if isinstance(self._local_result, AuditResult):
                        local_display = self._local_result.to_summary_text()
                    elif isinstance(self._local_result, DiagResult):
                        local_display = self._local_result.to_summary_text()
                    else:
                        local_display = local_context
                    self.local_result_signal.emit(local_display)
                else:
                    self.progress_signal.emit(f"本地预诊断完成 ({local_ms}ms)，未发现明显异常")

            # ── Layer 2: AI分析 ──
            # 将本地预诊断结果拼接到user_prompt中
            enhanced_prompt = self.user_prompt
            if local_context and local_context not in self.user_prompt:
                # 在user_prompt末尾追加本地预诊断结果
                enhanced_prompt = f"{self.user_prompt}\n{local_context}"

            url = f"{self.ai_config['base_url'].rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.ai_config['api_key']}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.ai_config["model"],
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 4096
            }

            self.progress_signal.emit("Layer 2/2: 正在调用AI引擎...")
            resp = requests.post(url, headers=headers, json=payload, timeout=AI_API_TIMEOUT)
            if resp.status_code == 200:
                result = resp.json()["choices"][0]["message"]["content"]

                # 如果有本地预诊断结果，拼接双层报告
                if local_context and self._local_result:
                    if isinstance(self._local_result, AuditResult):
                        local_summary = self._local_result.to_summary_text()
                        mode_label = "双层审计（本地规则 + AI精审）"
                    elif isinstance(self._local_result, DiagResult):
                        local_summary = self._local_result.to_summary_text()
                        mode_label = "双层诊断（本地运行时诊断 + AI精审）"
                    else:
                        local_summary = ""
                        mode_label = "本地预诊断 + AI分析"

                    if local_summary:
                        result = (
                            f"## 分析模式: {mode_label}\n\n"
                            f"--- 第一层：本地预诊断 ---\n"
                            f"{local_summary}\n\n"
                            f"--- 第二层：AI分析 ---\n"
                            f"{result}"
                        )

                self.finished_signal.emit(result)
            else:
                self.progress_signal.emit(f"AI服务错误 {resp.status_code} — 降级输出")
                if self._local_result:
                    if isinstance(self._local_result, AuditResult):
                        local_display = self._local_result.to_summary_text()
                    elif isinstance(self._local_result, DiagResult):
                        local_display = self._local_result.to_summary_text()
                    else:
                        local_display = str(self._local_result)
                    self.finished_signal.emit(
                        f"## AI服务不可用（HTTP {resp.status_code}）\n\n"
                        f"以下为本地预诊断结果：\n\n{local_display}"
                    )
                else:
                    self.error_signal.emit(f"AI服务错误 (HTTP {resp.status_code})")
        except requests.exceptions.ConnectionError:
            if self._local_result:
                if isinstance(self._local_result, AuditResult):
                    local_display = self._local_result.to_summary_text()
                elif isinstance(self._local_result, DiagResult):
                    local_display = self._local_result.to_summary_text()
                else:
                    local_display = str(self._local_result)
                self.finished_signal.emit(
                    f"## AI服务不可达\n\n以下为本地预诊断结果：\n\n{local_display}"
                )
            else:
                self.error_signal.emit("无法连接AI服务，请检查网络和模型配置")
        except requests.exceptions.Timeout:
            if self._local_result:
                if isinstance(self._local_result, AuditResult):
                    local_display = self._local_result.to_summary_text()
                elif isinstance(self._local_result, DiagResult):
                    local_display = self._local_result.to_summary_text()
                else:
                    local_display = str(self._local_result)
                self.finished_signal.emit(
                    f"## AI请求超时\n\n以下为本地预诊断结果：\n\n{local_display}"
                )
            else:
                self.error_signal.emit("AI请求超时，请重试")
        except Exception as e:
            if self._local_result:
                if isinstance(self._local_result, AuditResult):
                    local_display = self._local_result.to_summary_text()
                elif isinstance(self._local_result, DiagResult):
                    local_display = self._local_result.to_summary_text()
                else:
                    local_display = str(self._local_result)
                self.finished_signal.emit(
                    f"## AI分析异常: {type(e).__name__}\n\n以下为本地预诊断结果：\n\n{local_display}"
                )
            else:
                self.error_signal.emit(f"分析异常: {type(e).__name__}: {str(e)}")


class AIAnalysisPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._ai_thread = None
        self.last_result = ""
        self.recent_files = self._load_recent_files()
        self.multi_files = []
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()

    def _load_recent_files(self):
        try:
            if os.path.exists(RECENT_FILES_PATH):
                with open(RECENT_FILES_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [item for item in data if os.path.exists(item)]
        except Exception:
            pass
        return []

    def _btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['hover_bg']};
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                font-size: 9pt;
                padding: 5px 12px;
            }}
            QPushButton:hover {{ background-color: {t['border']}; border-color: {t['border_deep']}; }}
        """

    def _ai_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['ai_bg']};
                color: {t['ai_text']};
                border: 1px solid {t['ai_border']};
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {t['selection_bg']}; }}
            QPushButton:disabled {{ background-color: {t['hover_bg']}; color: {t['text_disabled']}; border-color: {t['border']}; }}
        """

    def _primary_btn_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QPushButton {{
                background-color: {t['primary']};
                color: {t['text_primary']};
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{ background-color: {t['primary_hover']}; }}
            QPushButton:disabled {{ background-color: {t['border_deep']}; }}
        """

    def _list_style(self) -> str:
        t = self._theme_engine.current_theme
        return f"""
            QListWidget {{
                border: 1px solid {t['border']};
                border-radius: 4px;
                background-color: {t['card_bg']};
                font-size: 10pt;
                outline: none;
            }}
            QListWidget::item {{ padding: 5px 8px; }}
            QListWidget::item:selected {{ background-color: {t['ai_bg']}; color: {t['text_main']}; }}
            QListWidget::item:hover {{ background-color: {t['hover_bg']}; }}
        """

    def _save_recent_files(self):
        try:
            with open(RECENT_FILES_PATH, "w", encoding="utf-8") as f:
                json.dump(self.recent_files, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        self._save_recent_files()
        self._refresh_recent_list()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("AI专家工作站")
        layout.addWidget(title)

        desc = QLabel("深度分析、多文件对比、自定义指令、多轮对话。一键式分析请使用单点巡检或运维任务中心。")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        input_group = QGroupBox("📂 输入文件")
        input_group.setStyleSheet(self._group_style())
        input_layout = QVBoxLayout()
        input_layout.setSpacing(4)

        add_row = QHBoxLayout()
        self.add_file_btn = QPushButton("选择文件")
        self.add_file_btn.setStyleSheet(self._btn_style())
        self.add_file_btn.clicked.connect(self._browse_files)
        add_row.addWidget(self.add_file_btn)

        self.add_multi_btn = QPushButton("批量选择")
        self.add_multi_btn.setStyleSheet(self._btn_style())
        self.add_multi_btn.clicked.connect(self._browse_multi_files)
        add_row.addWidget(self.add_multi_btn)

        self.clear_files_btn = QPushButton("清空")
        self.clear_files_btn.setStyleSheet(self._btn_style())
        self.clear_files_btn.clicked.connect(self._clear_input_files)
        add_row.addWidget(self.clear_files_btn)
        add_row.addStretch()
        input_layout.addLayout(add_row)

        self.input_file_list = QListWidget()
        self.input_file_list.setStyleSheet(self._list_style())
        self.input_file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.input_file_list.setMaximumHeight(100)
        self.input_file_list.setAcceptDrops(True)
        input_layout.addWidget(self.input_file_list)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        recent_group = QGroupBox("📋 最近文件")
        recent_group.setStyleSheet(self._group_style())
        recent_layout = QVBoxLayout()
        recent_layout.setSpacing(2)
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet(self._list_style())
        self.recent_list.setMaximumHeight(100)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_double_clicked)
        recent_layout.addWidget(self.recent_list)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)

        history_group = QGroupBox("📂 历史报告归档")
        history_group.setStyleSheet(self._group_style())
        history_layout = QVBoxLayout()
        history_layout.setSpacing(4)

        hbtn_row = QHBoxLayout()
        self.h_refresh_btn = QPushButton("🔄 刷新")
        self.h_refresh_btn.setStyleSheet(self._btn_style())
        self.h_refresh_btn.clicked.connect(self._refresh_history)
        hbtn_row.addWidget(self.h_refresh_btn)
        self.h_open_btn = QPushButton("📂 打开")
        self.h_open_btn.setStyleSheet(self._btn_style())
        self.h_open_btn.clicked.connect(self._open_history_file)
        hbtn_row.addWidget(self.h_open_btn)
        self.h_del_btn = QPushButton("🗑 删除")
        self.h_del_btn.setStyleSheet(self._btn_style())
        self.h_del_btn.clicked.connect(self._delete_history_file)
        hbtn_row.addWidget(self.h_del_btn)
        hbtn_row.addStretch()
        history_layout.addLayout(hbtn_row)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet(self._list_style())
        self.history_list.setMaximumHeight(100)
        self.history_list.itemDoubleClicked.connect(self._on_history_double_clicked)
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        layout.addStretch()
        panel.setLayout(layout)
        panel.setMaximumWidth(320)
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        agent_row = QHBoxLayout()
        agent_row.setSpacing(8)
        agent_label = QLabel("Agent快捷指令：")
        agent_row.addWidget(agent_label)
        self.agent_compliance_btn = QPushButton("🔍 一键合规巡检")
        self.agent_compliance_btn.setStyleSheet(self._ai_btn_style())
        self.agent_compliance_btn.setToolTip("加载合规审计Agent + 已选文件 → 预填Prompt → 可编辑后发送")
        self.agent_compliance_btn.clicked.connect(self._agent_compliance)
        agent_row.addWidget(self.agent_compliance_btn)
        self.agent_diagnose_btn = QPushButton("🩺 一键故障诊断")
        self.agent_diagnose_btn.setStyleSheet(self._ai_btn_style())
        self.agent_diagnose_btn.setToolTip("加载故障诊断Agent + 已选文件 → 预填Prompt → 可编辑后发送")
        self.agent_diagnose_btn.clicked.connect(self._agent_diagnose)
        agent_row.addWidget(self.agent_diagnose_btn)
        agent_row.addStretch()
        layout.addLayout(agent_row)

        self.tab_widget = QTabWidget()

        self.chat_tab = self._create_analysis_tab("💬 自由对话", "free")
        self.compliance_tab = self._create_analysis_tab("📋 合规审计", "compliance")
        self.diagnose_tab = self._create_analysis_tab("🩺 故障诊断", "diagnose")

        self.tab_widget.addTab(self.chat_tab, "💬 自由对话")
        self.tab_widget.addTab(self.compliance_tab, "📋 合规审计")
        self.tab_widget.addTab(self.diagnose_tab, "🩺 故障诊断")

        layout.addWidget(self.tab_widget)
        panel.setLayout(layout)
        return panel

    def _create_analysis_tab(self, title: str, tab_key: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(6)

        prompt_label = QLabel("Prompt编辑区（可直接修改后发送）：")
        layout.addWidget(prompt_label)

        prompt_edit = QTextEdit()
        prompt_edit.setPlaceholderText(
            "在此编辑Prompt...\n"
            "点击上方 [🔍一键合规巡检] 或 [🩺一键故障诊断] 自动填入Agent规则+文件内容。\n"
            "也可自由输入任意问题。"
        )
        prompt_edit.setMinimumHeight(150)

        if tab_key == "free":
            prompt_edit.setPlainText("你是资深网络运维专家，请用中文回答以下问题：\n\n")
        elif tab_key == "compliance":
            prompt_edit.setPlainText("你是网络配置合规审计专家。请对提供的设备配置进行合规性审计，输出分级整改报告。\n\n")
        elif tab_key == "diagnose":
            prompt_edit.setPlainText("你是资深网络故障诊断专家。请对提供的巡检报告/日志进行OSI分层故障诊断。\n\n")

        setattr(self, f"prompt_edit_{tab_key}", prompt_edit)
        layout.addWidget(prompt_edit)

        send_row = QHBoxLayout()
        send_row.setSpacing(8)
        send_btn = QPushButton("▶ 发送分析")
        send_btn.setStyleSheet(self._primary_btn_style())
        send_btn.clicked.connect(lambda: self._run_expert_analysis(tab_key))
        send_row.addWidget(send_btn)
        send_row.addStretch()

        self.send_btns = getattr(self, "send_btns", {})
        self.send_btns[tab_key] = send_btn

        save_btn = QPushButton("💾 保存报告")
        save_btn.setStyleSheet(self._btn_style())
        save_btn.clicked.connect(self._save_report)
        send_row.addWidget(save_btn)

        export_btn = QPushButton("📤 导出TXT")
        export_btn.setStyleSheet(self._btn_style())
        export_btn.clicked.connect(self._export_report)
        send_row.addWidget(export_btn)
        layout.addLayout(send_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪，等待输入...")
        layout.addWidget(self.status_label)

        result_edit = QTextEdit()
        result_edit.setReadOnly(True)
        result_edit.setPlaceholderText("AI分析结果将在此显示...")
        result_edit.setMinimumHeight(200)
        setattr(self, f"result_edit_{tab_key}", result_edit)
        layout.addWidget(result_edit)

        widget.setLayout(layout)
        return widget

    def _group_style(self):
        t = self._theme_engine.current_theme
        return f"""
            QGroupBox {{
                font-size: 10pt;
                font-weight: bold;
                color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding: 12px;
                background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """

    def _browse_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "文本文件 (*.txt *.log *.md *.cfg);;所有文件 (*.*)")
        if file_path:
            self.multi_files = [file_path]
            self._add_input_file(file_path)

    def _browse_multi_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "批量选择文件", "", "文本文件 (*.txt *.log *.md *.cfg);;所有文件 (*.*)")
        if file_paths:
            self.multi_files = list(file_paths)
            self.input_file_list.clear()
            for fp in file_paths:
                self._add_input_file(fp, add_to_recent=False)
            self._add_recent_file(file_paths[0])

    def _add_input_file(self, file_path, add_to_recent=True):
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        self.input_file_list.addItem(item)
        if add_to_recent:
            self._add_recent_file(file_path)

    def _clear_input_files(self):
        self.input_file_list.clear()
        self.multi_files = []

    def _refresh_recent_list(self):
        self.recent_list.clear()
        for f in self.recent_files:
            item = QListWidgetItem(os.path.basename(f))
            item.setData(Qt.UserRole, f)
            item.setToolTip(f)
            self.recent_list.addItem(item)

    def _on_recent_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        if os.path.exists(file_path):
            self._add_input_file(file_path)

    def _refresh_history(self):
        self.history_list.clear()
        report_dirs = []
        app_dir = get_app_dir()
        single_report_dir = os.path.join(get_single_dir(), "report")
        if os.path.exists(single_report_dir):
            report_dirs.append(single_report_dir)
        projects_dir = os.path.join(app_dir, "projects")
        if os.path.exists(projects_dir):
            for proj_name in os.listdir(projects_dir):
                proj_path = os.path.join(projects_dir, proj_name)
                if os.path.isdir(proj_path):
                    report_dir = os.path.join(proj_path, "report")
                    if os.path.exists(report_dir):
                        report_dirs.append(report_dir)
        import glob as glob_mod
        all_reports = []
        for rd in report_dirs:
            for root, dirs, files in os.walk(rd):
                for f in files:
                    if f.endswith(('.md', '.txt')):
                        fp = os.path.join(root, f)
                        all_reports.append((os.path.getmtime(fp), fp))
        all_reports.sort(reverse=True)
        for _, fp in all_reports[:50]:
            item = QListWidgetItem(os.path.basename(fp))
            item.setData(Qt.UserRole, fp)
            item.setToolTip(fp)
            self.history_list.addItem(item)

    def _open_history_file(self):
        item = self.history_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选中一个文件")
            return
        file_path = item.data(Qt.UserRole)
        if os.path.exists(file_path):
            os.startfile(file_path)

    def _delete_history_file(self):
        item = self.history_list.currentItem()
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
            self._refresh_history()
        except Exception as e:
            QMessageBox.critical(self, "删除失败", str(e))

    def _on_history_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                current_tab_idx = self.tab_widget.currentIndex()
                tab_keys = ["free", "compliance", "diagnose"]
                if 0 <= current_tab_idx < len(tab_keys):
                    result_edit = getattr(self, f"result_edit_{tab_keys[current_tab_idx]}", None)
                    if result_edit:
                        result_edit.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "打开失败", str(e))

    def _get_input_files_content(self) -> str:
        combined = ""
        for i in range(self.input_file_list.count()):
            item = self.input_file_list.item(i)
            file_path = item.data(Qt.UserRole)
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                combined += f"\n\n=== 文件{i + 1}: {os.path.basename(file_path)} ===\n{content}"
            except Exception:
                combined += f"\n\n=== 文件{i + 1}: {os.path.basename(file_path)} (无法读取) ==="
        return combined.strip()

    def _load_agent_file(self, agent_name: str) -> str:
        agent_path = os.path.join(get_app_dir(), "agents", agent_name)
        if os.path.exists(agent_path):
            with open(agent_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _agent_compliance(self):
        agent_rules = self._load_agent_file("network-config-reviewer.md")
        if not agent_rules:
            agent_rules = "你是网络配置合规审计专家，请用中文输出审计报告。"

        files_content = self._get_input_files_content()
        prompt = f"{agent_rules}\n\n---\n请对以下设备配置进行合规性审计：\n\n{files_content}"
        if not files_content:
            prompt = f"{agent_rules}\n\n---\n请粘贴设备配置内容进行合规审计..."

        prompt_edit = self.prompt_edit_compliance
        prompt_edit.setPlainText(prompt)
        self.tab_widget.setCurrentWidget(self.compliance_tab)

    def _agent_diagnose(self):
        agent_rules = self._load_agent_file("network-troubleshooter.md")
        if not agent_rules:
            agent_rules = "你是资深网络故障诊断专家。通过OSI分层逐层诊断网络问题。"

        files_content = self._get_input_files_content()
        prompt = f"{agent_rules}\n\n---\n请对以下内容进行故障诊断分析：\n\n{files_content}"
        if not files_content:
            prompt = f"{agent_rules}\n\n---\n请粘贴巡检报告或日志内容进行故障诊断..."

        prompt_edit = self.prompt_edit_diagnose
        prompt_edit.setPlainText(prompt)
        self.tab_widget.setCurrentWidget(self.diagnose_tab)

    def _run_expert_analysis(self, tab_key: str):
        config = get_active_ai_config()
        if not config or not config.get("api_key"):
            QMessageBox.warning(self, "提示", "请先在「模型设置」中配置AI模型")
            return

        prompt_edit = getattr(self, f"prompt_edit_{tab_key}", None)
        if not prompt_edit:
            return

        user_prompt = prompt_edit.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "提示", "请输入分析内容")
            return

        tab_key_to_system = {
            "free": "你是资深网络运维专家，请用中文回答用户问题。",
            "compliance": "你是网络配置合规审计专家，请用中文输出结构化的审计报告。",
            "diagnose": "你是资深网络故障诊断专家，采用OSI分层方法诊断网络问题。",
        }
        system_prompt = tab_key_to_system.get(tab_key, "你是资深网络运维专家，请用中文回答。")

        self.progress_bar.show()
        self.status_label.setText("正在调用AI引擎...")
        send_btn = self.send_btns.get(tab_key)
        if send_btn:
            send_btn.setEnabled(False)

        result_edit = getattr(self, f"result_edit_{tab_key}", None)
        if result_edit:
            result_edit.clear()

        # 获取已选文件内容（用于本地预诊断）
        files_content = self._get_input_files_content() if tab_key in ("compliance", "diagnose") else ""

        self._ai_thread = ExpertAnalysisThread(
            system_prompt, user_prompt, config,
            tab_key=tab_key, content_files=files_content
        )
        self._ai_thread.progress_signal.connect(lambda msg: self.status_label.setText(msg))
        self._ai_thread.local_result_signal.connect(
            lambda result: self.status_label.setText("本地预诊断完成，等待AI精审..."))
        self._ai_thread.finished_signal.connect(lambda r: self._on_expert_finished(r, tab_key))
        self._ai_thread.error_signal.connect(lambda e: self._on_expert_error(e, tab_key))
        self._ai_thread.start()

    def _on_expert_finished(self, result, tab_key):
        self.progress_bar.hide()
        self.status_label.setText("分析完成 ✅")
        self.last_result = result
        send_btn = self.send_btns.get(tab_key)
        if send_btn:
            send_btn.setEnabled(True)
        result_edit = getattr(self, f"result_edit_{tab_key}", None)
        if result_edit:
            result_edit.setMarkdown(result)

    def _on_expert_error(self, error_msg, tab_key):
        self.progress_bar.hide()
        self.status_label.setText(f"分析失败 ❌ {error_msg}")
        send_btn = self.send_btns.get(tab_key)
        if send_btn:
            send_btn.setEnabled(True)
        result_edit = getattr(self, f"result_edit_{tab_key}", None)
        if result_edit:
            result_edit.setPlainText(f"错误：{error_msg}")

    def _save_report(self):
        if not self.last_result:
            QMessageBox.warning(self, "提示", "没有可保存的分析结果")
            return
        project_dir = None
        if hasattr(self.parent, 'current_project') and self.parent.current_project:
            project_dir = self.parent.current_project
        if project_dir:
            report_dir = os.path.join(project_dir, "report")
            os.makedirs(report_dir, exist_ok=True)
            default_path = os.path.join(report_dir, f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        else:
            default_path = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path, _ = QFileDialog.getSaveFileName(self, "保存报告", default_path, "Markdown文件 (*.md);;文本文件 (*.txt)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.last_result)
                QMessageBox.information(self, "保存成功", f"报告已保存至：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", str(e))

    def _export_report(self):
        if not self.last_result:
            QMessageBox.warning(self, "提示", "没有可导出的分析结果")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "导出报告", f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "文本文件 (*.txt)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.last_result)
                QMessageBox.information(self, "导出成功", f"报告已导出至：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", str(e))

    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()

    def _apply_theme_style(self) -> None:
        t = self._theme_engine.current_theme
        # 页面级背景（只设置背景色和字体，不设置 color 属性）
        self.setStyleSheet(f"""
            AIAnalysisPage {{
                background-color: {t['page_bg']};
                font-family: {t['font_ui']};
            }}
        """)

        # 左侧面板标题和描述
        left_panel = self.layout().itemAt(0).widget()
        if left_panel:
            splitter = left_panel
            # 通过 findChildren 查找标题和描述标签
            for title_label in self.findChildren(QLabel):
                if title_label.text() == "AI专家工作站":
                    title_label.setStyleSheet(f"font-size: 15pt; font-weight: bold; color: {t['text_main']}; text-decoration: none;")
                elif title_label.text().startswith("深度分析、多文件对比"):
                    title_label.setStyleSheet(f"font-size: 9pt; color: {t['text_tertiary']};")

        # Agent快捷指令标签
        for agent_label in self.findChildren(QLabel):
            if agent_label.text() == "Agent快捷指令：":
                agent_label.setStyleSheet(f"font-size: 10pt; color: {t['text_secondary']}; font-weight: bold;")

        # 所有 Prompt编辑区标签
        for prompt_label in self.findChildren(QLabel):
            if prompt_label.text() == "Prompt编辑区（可直接修改后发送）：":
                prompt_label.setStyleSheet(f"font-size: 9pt; color: {t['text_tertiary']}; font-weight: bold;")

        # 状态标签
        self.status_label.setStyleSheet(f"font-size: 9pt; color: {t['text_tertiary']};")

        # 刷新 QGroupBox 样式（标题颜色）
        for group_box in self.findChildren(QGroupBox):
            group_box.setStyleSheet(self._group_style())

        # 刷新 TabWidget 样式
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {t['border']};
                border-radius: 4px;
                background-color: {t['card_bg']};
            }}
            QTabBar::tab {{
                border: 1px solid {t['border']};
                padding: 8px 20px;
                font-size: 10pt;
                background-color: {t['card_bg']};
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['card_bg']};
                border-bottom-color: {t['card_bg']};
                font-weight: bold;
                color: {t['accent']};
            }}
            QTabBar::tab:hover {{ background-color: {t['hover_bg']}; }}
        """)

        # 刷新 QTextEdit 样式（Prompt编辑区和结果区）
        for text_edit in self.findChildren(QTextEdit):
            if text_edit.isReadOnly():
                # 结果区
                text_edit.setStyleSheet(f"""
                    QTextEdit {{
                        border: 1px solid {t['border']};
                        border-radius: 4px;
                        padding: 10px;
                        font-size: 10pt;
                        background-color: {t['card_bg']};
                    }}
                """)
            else:
                # Prompt编辑区
                text_edit.setStyleSheet(f"""
                    QTextEdit {{
                        border: 1px solid {t['accent']};
                        border-radius: 4px;
                        padding: 10px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 10pt;
                        background-color: {t['card_bg']};
                    }}
                    QTextEdit:focus {{ border: 1px solid {t['accent']}; }}
                """)

        # 刷新 QListWidget 样式
        for list_widget in self.findChildren(QListWidget):
            list_widget.setStyleSheet(f"""
                QListWidget {{
                    border: 1px solid {t['border']};
                    border-radius: 4px;
                    background-color: {t['card_bg']};
                    font-size: 10pt;
                    outline: none;
                }}
                QListWidget::item {{ padding: 5px 8px; }}
                QListWidget::item:selected {{ background-color: {t['accent']}; color: {t['text_primary']}; }}
                QListWidget::item:hover {{ background-color: {t['hover_bg']}; }}
            """)

        # 刷新进度条样式
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {t['border']};
                border-radius: 2px;
                text-align: center;
                background-color: {t['card_bg']};
                font-size: 10px;
            }}
            QProgressBar::chunk {{ background-color: {t['accent']}; border-radius: 2px; }}
        """)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_recent_list()
        self._refresh_history()