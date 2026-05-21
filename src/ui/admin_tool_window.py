#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员制码工具主窗口

独立程序，不与用户端合并。
仅限管理员【天技老韩】本地使用，禁止外发。

功能：
- 输入机器码 → 一键生成激活码
- 台账记录（姓名/机器码/激活码/备注/时间）
- 方案B：黑名单管理
"""

import sys
import os
from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QSplitter, QAbstractItemView
)

from src.core.admin_keygen import (
    generate_code_for_machine,
    save_record,
    load_records,
    delete_record,
    add_to_blacklist,
    remove_from_blacklist,
    load_blacklist,
    export_blacklist_for_upload,
)
from src.core.activation_engine import get_machine_code


class AdminToolWindow(QMainWindow):
    """管理员制码工具主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetOps 管理员制码工具 V3.0 — 天技老韩专用")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._apply_style()
        self._refresh_records()
        self._refresh_blacklist()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ── 标题 ──
        title = QLabel("🔐 NetOps 管理员制码工具")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1565C0;")
        main_layout.addWidget(title)

        subtitle = QLabel("仅限管理员本地使用，禁止外发")
        subtitle.setFont(QFont("Microsoft YaHei", 9))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #9E9E9E;")
        main_layout.addWidget(subtitle)

        # ── 分割器：上（制码）+ 下（台账+黑名单）──
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter, stretch=1)

        # ── 上半部分：制码区 ──
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(12)

        # 机器码输入
        machine_group = QGroupBox("激活码生成")
        machine_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        mg_layout = QVBoxLayout(machine_group)
        mg_layout.setSpacing(10)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addWidget(QLabel("机器码："))
        self._machine_input = QLineEdit()
        self._machine_input.setPlaceholderText("粘贴用户发来的32位机器码")
        self._machine_input.setFont(QFont("Consolas", 11))
        self._machine_input.setMinimumHeight(36)
        input_layout.addWidget(self._machine_input, stretch=1)
        mg_layout.addLayout(input_layout)

        gen_btn = QPushButton("⚡ 一键生成激活码")
        gen_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        gen_btn.setMinimumHeight(40)
        gen_btn.setCursor(Qt.PointingHandCursor)
        gen_btn.clicked.connect(self._on_generate)
        mg_layout.addWidget(gen_btn)

        # 激活码结果
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("激活码："))
        self._code_result = QLineEdit()
        self._code_result.setReadOnly(True)
        self._code_result.setFont(QFont("Consolas", 14, QFont.Bold))
        self._code_result.setAlignment(Qt.AlignCenter)
        self._code_result.setMinimumHeight(40)
        self._code_result.setStyleSheet(
            "QLineEdit { color: #1565C0; background-color: #E3F2FD; }"
        )
        result_layout.addWidget(self._code_result, stretch=1)

        copy_code_btn = QPushButton("📋 复制")
        copy_code_btn.setFixedSize(80, 40)
        copy_code_btn.setCursor(Qt.PointingHandCursor)
        copy_code_btn.clicked.connect(self._copy_code)
        result_layout.addWidget(copy_code_btn)
        mg_layout.addLayout(result_layout)

        # 用户信息
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("用户姓名："))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("用户姓名/标识（选填）")
        info_layout.addWidget(self._name_input)
        info_layout.addWidget(QLabel("备注："))
        self._note_input = QLineEdit()
        self._note_input.setPlaceholderText("用途/备注（选填）")
        info_layout.addWidget(self._note_input)
        mg_layout.addLayout(info_layout)

        save_btn = QPushButton("💾 保存台账")
        save_btn.setMinimumHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save_record)
        mg_layout.addWidget(save_btn)

        top_layout.addWidget(machine_group)

        # 黑名单快捷操作
        bl_group = QGroupBox("方案B：黑名单管理")
        bl_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        bl_layout = QHBoxLayout(bl_group)
        bl_layout.setSpacing(10)

        self._bl_input = QLineEdit()
        self._bl_input.setPlaceholderText("输入要封禁/解封的机器码")
        self._bl_input.setFont(QFont("Consolas", 10))
        bl_layout.addWidget(self._bl_input, stretch=1)

        bl_add_btn = QPushButton("🚫 加入黑名单")
        bl_add_btn.setCursor(Qt.PointingHandCursor)
        bl_add_btn.clicked.connect(self._on_add_blacklist)
        bl_layout.addWidget(bl_add_btn)

        bl_rm_btn = QPushButton("✅ 移除黑名单")
        bl_rm_btn.setCursor(Qt.PointingHandCursor)
        bl_rm_btn.clicked.connect(self._on_remove_blacklist)
        bl_layout.addWidget(bl_rm_btn)

        top_layout.addWidget(bl_group)

        splitter.addWidget(top_widget)

        # ── 下半部分：台账 + 黑名单 ──
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(16)

        # 台账表格
        record_group = QGroupBox("授权台账")
        record_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        rg_layout = QVBoxLayout(record_group)

        self._records_table = QTableWidget()
        self._records_table.setColumnCount(5)
        self._records_table.setHorizontalHeaderLabels(
            ["姓名", "机器码", "激活码", "备注", "授权时间"]
        )
        self._records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._records_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        rg_layout.addWidget(self._records_table)

        del_btn = QPushButton("🗑 删除选中记录")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self._on_delete_record)
        rg_layout.addWidget(del_btn)

        bottom_layout.addWidget(record_group, stretch=2)

        # 黑名单列表
        bl_list_group = QGroupBox("黑名单列表")
        bl_list_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        bl_list_layout = QVBoxLayout(bl_list_group)

        self._bl_list = QTextEdit()
        self._bl_list.setReadOnly(True)
        self._bl_list.setFont(QFont("Consolas", 9))
        bl_list_layout.addWidget(self._bl_list)

        export_btn = QPushButton("📤 导出黑名单（用于上传GitHub）")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._on_export_blacklist)
        bl_list_layout.addWidget(export_btn)

        bottom_layout.addWidget(bl_list_group, stretch=1)

        splitter.addWidget(bottom_widget)
        splitter.setSizes([300, 300])

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background-color: #FAFAFA; }
            QGroupBox {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #424242;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover { background-color: #0D47A1; }
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus { border-color: #1565C0; }
            QTableWidget {
                border: 1px solid #E0E0E0;
                gridline-color: #EEEEEE;
            }
        """)

    # ── 事件处理 ──

    def _on_generate(self) -> None:
        machine_code = self._machine_input.text().strip().upper()
        if not machine_code:
            QMessageBox.warning(self, "提示", "请输入机器码")
            return
        if len(machine_code) != 32:
            QMessageBox.warning(self, "提示", "机器码格式不正确，应为32位")
            return

        code = generate_code_for_machine(machine_code)
        self._code_result.setText(code)

    def _copy_code(self) -> None:
        code = self._code_result.text()
        if code:
            QApplication.clipboard().setText(code)

    def _on_save_record(self) -> None:
        machine_code = self._machine_input.text().strip().upper()
        code = self._code_result.text()
        name = self._name_input.text().strip()
        note = self._note_input.text().strip()

        if not machine_code or not code:
            QMessageBox.warning(self, "提示", "请先生成激活码")
            return

        if save_record(name or "未命名", machine_code, code, note):
            QMessageBox.information(self, "成功", "台账记录已保存")
            self._refresh_records()
            self._name_input.clear()
            self._note_input.clear()
        else:
            QMessageBox.critical(self, "错误", "保存失败")

    def _on_delete_record(self) -> None:
        row = self._records_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选中一条记录")
            return
        if QMessageBox.question(self, "确认", "确定删除选中记录？") == QMessageBox.Yes:
            delete_record(row)
            self._refresh_records()

    def _on_add_blacklist(self) -> None:
        code = self._bl_input.text().strip().upper()
        if not code:
            QMessageBox.warning(self, "提示", "请输入机器码")
            return
        if add_to_blacklist(code):
            QMessageBox.information(self, "成功", f"已加入黑名单：{code[:8]}...")
            self._bl_input.clear()
            self._refresh_blacklist()
        else:
            QMessageBox.critical(self, "错误", "操作失败")

    def _on_remove_blacklist(self) -> None:
        code = self._bl_input.text().strip().upper()
        if not code:
            QMessageBox.warning(self, "提示", "请输入机器码")
            return
        if remove_from_blacklist(code):
            QMessageBox.information(self, "成功", f"已从黑名单移除：{code[:8]}...")
            self._bl_input.clear()
            self._refresh_blacklist()
        else:
            QMessageBox.critical(self, "错误", "操作失败")

    def _on_export_blacklist(self) -> None:
        content = export_blacklist_for_upload()
        if not content.strip():
            QMessageBox.information(self, "提示", "黑名单为空")
            return
        QApplication.clipboard().setText(content)
        QMessageBox.information(
            self, "已复制",
            f"黑名单内容已复制到剪贴板（共 {content.strip().count(chr(10))} 条）\n\n"
            "请粘贴到 GitHub 仓库根目录的 blacklist.txt 文件中提交。"
        )

    # ── 刷新 ──

    def _refresh_records(self) -> None:
        records = load_records()
        self._records_table.setRowCount(len(records))
        for i, rec in enumerate(records):
            self._records_table.setItem(i, 0, QTableWidgetItem(rec.get("name", "")))
            self._records_table.setItem(i, 1, QTableWidgetItem(rec.get("machine_code", "")[:12] + "..."))
            self._records_table.setItem(i, 2, QTableWidgetItem(rec.get("activation_code", "")))
            self._records_table.setItem(i, 3, QTableWidgetItem(rec.get("note", "")))
            self._records_table.setItem(i, 4, QTableWidgetItem(rec.get("created_at", "")[:19]))

    def _refresh_blacklist(self) -> None:
        codes = load_blacklist()
        self._bl_list.setPlainText("\n".join(codes) if codes else "（黑名单为空）")


def run_admin_tool():
    """启动管理员制码工具"""
    app = QApplication(sys.argv)
    window = AdminToolWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_admin_tool()
