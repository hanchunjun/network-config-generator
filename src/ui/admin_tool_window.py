#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员制码工具主窗口

独立程序，不与用户端合并。
仅限管理员【老韩】本地使用，禁止外发。

功能：
- 输入机器码 → 一键生成激活码
- 台账记录（姓名/机器码/激活码/备注/时间）—— AES-GCM 加密存储
- 台账备份/恢复/导出/导入
- 方案B：黑名单管理

数据目录（与用户端完全隔离）：
    admin_data/
    ├── records.dat       ← 授权台账（加密）
    ├── blacklist.txt     ← 本地黑名单
    └── backup/           ← 台账备份
"""

import os
import sys
from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QSplitter, QAbstractItemView, QFileDialog, QComboBox, QInputDialog
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
    backup_records,
    list_backups,
    restore_backup,
    export_records_to_json,
    import_records_from_json,
    format_record_time,
    get_record_expire_status,
)
from src.core.activation_engine import get_machine_code
from src.core.theme_engine import ThemeEngine
from src.utils.resource_path import get_admin_data_dir


class AdminToolWindow(QMainWindow):
    """管理员制码工具主窗口"""

    def __init__(self):
        super().__init__()
        self._theme_engine = ThemeEngine.get()
        self.setWindowTitle("NetOps 管理员制码工具 V0.3.0 — 老韩专用")
        self.setMinimumSize(900, 650)
        self._setup_ui()
        self._apply_style()
        self._refresh_records()
        self._refresh_blacklist()
        self._refresh_backup_list()

    def _setup_ui(self) -> None:
        t = self._theme_engine.current_theme
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # ── 标题 ──
        title = QLabel("🔐 NetOps 管理员制码工具")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {t['primary']};")
        main_layout.addWidget(title)

        subtitle = QLabel("台账加密存储 · 独立数据目录 · 备份恢复 · 仅限管理员本地使用")
        subtitle.setFont(QFont("Microsoft YaHei", 9))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {t['text_tertiary']};")
        main_layout.addWidget(subtitle)

        # ── 数据目录提示 ──
        dir_label = QLabel(f"📁 数据目录：{get_admin_data_dir()}")
        dir_label.setFont(QFont("Consolas", 8))
        dir_label.setStyleSheet(f"color: {t['border_deep']}; padding: 2px 8px;")
        dir_label.setWordWrap(True)
        main_layout.addWidget(dir_label)

        # ── 分割器：上（制码+黑名单）+ 下（台账+备份）──
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter, stretch=1)

        # ═══════════════════════════════════════════
        # 上半部分：制码 + 黑名单
        # ═══════════════════════════════════════════
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(10)

        # ── 制码区 ──
        machine_group = QGroupBox("激活码生成")
        machine_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        mg_layout = QVBoxLayout(machine_group)
        mg_layout.setSpacing(8)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
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

        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("激活码："))
        self._code_result = QLineEdit()
        self._code_result.setReadOnly(True)
        self._code_result.setFont(QFont("Consolas", 14, QFont.Bold))
        self._code_result.setAlignment(Qt.AlignCenter)
        self._code_result.setMinimumHeight(40)
        result_layout.addWidget(self._code_result, stretch=1)
        copy_code_btn = QPushButton("📋 复制")
        copy_code_btn.setFixedSize(80, 40)
        copy_code_btn.setCursor(Qt.PointingHandCursor)
        copy_code_btn.clicked.connect(self._copy_code)
        result_layout.addWidget(copy_code_btn)
        mg_layout.addLayout(result_layout)

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

        # 有效期选择 + 生成时间显示
        validity_layout = QHBoxLayout()
        validity_layout.addWidget(QLabel("有效期："))
        self._validity_combo = QComboBox()
        self._validity_combo.addItems([
            "永久（方案A）",
            "1825天（5年）",
            "3650天（10年）",
            "1095天（3年）",
            "730天（2年）",
            "365天（1年）",
            "180天（方案B·半年）",
            "90天（季度）",
            "30天（月度）",
            "7天（周度）",
        ])
        self._validity_combo.setMinimumHeight(30)
        validity_layout.addWidget(self._validity_combo)
        validity_layout.addStretch()
        # 生成时间标签
        self._gen_time_label = QLabel("")
        self._gen_time_label.setFont(QFont("Microsoft YaHei", 9))
        validity_layout.addWidget(self._gen_time_label)
        mg_layout.addLayout(validity_layout)

        save_btn = QPushButton("💾 保存台账")
        save_btn.setMinimumHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save_record)
        mg_layout.addWidget(save_btn)

        top_layout.addWidget(machine_group)

        # ── 黑名单 ──
        bl_group = QGroupBox("方案B：黑名单管理")
        bl_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        bl_layout = QHBoxLayout(bl_group)
        bl_layout.setSpacing(8)

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

        export_bl_btn = QPushButton("📤 导出黑名单")
        export_bl_btn.setCursor(Qt.PointingHandCursor)
        export_bl_btn.clicked.connect(self._on_export_blacklist)
        bl_layout.addWidget(export_bl_btn)

        top_layout.addWidget(bl_group)
        splitter.addWidget(top_widget)

        # ═══════════════════════════════════════════
        # 下半部分：台账 + 备份管理
        # ═══════════════════════════════════════════
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(12)

        # ── 台账表格 ──
        record_group = QGroupBox("授权台账（加密存储）")
        record_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        rg_layout = QVBoxLayout(record_group)

        self._records_table = QTableWidget()
        self._records_table.setColumnCount(6)
        self._records_table.setHorizontalHeaderLabels(
            ["姓名", "机器码", "激活码", "授权时间", "有效期", "备注"]
        )
        self._records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._records_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 机器码固定宽度
        self._records_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 激活码固定宽度
        self._records_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        rg_layout.addWidget(self._records_table)

        record_btn_layout = QHBoxLayout()
        del_btn = QPushButton("🗑 删除选中")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self._on_delete_record)
        record_btn_layout.addWidget(del_btn)
        record_btn_layout.addStretch()
        rg_layout.addLayout(record_btn_layout)

        bottom_layout.addWidget(record_group, stretch=2)

        # ── 备份管理 ──
        backup_group = QGroupBox("台账备份与恢复")
        backup_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        bkp_layout = QVBoxLayout(backup_group)

        # 备份列表
        self._backup_combo = QComboBox()
        self._backup_combo.setMinimumHeight(30)
        bkp_layout.addWidget(QLabel("备份历史："))
        bkp_layout.addWidget(self._backup_combo)

        # 备份操作按钮
        bkp_btn_layout = QHBoxLayout()

        backup_btn = QPushButton("📦 立即备份")
        backup_btn.setCursor(Qt.PointingHandCursor)
        backup_btn.clicked.connect(self._on_backup)
        bkp_btn_layout.addWidget(backup_btn)

        restore_btn = QPushButton("↩ 恢复选中")
        restore_btn.setCursor(Qt.PointingHandCursor)
        restore_btn.clicked.connect(self._on_restore)
        bkp_btn_layout.addWidget(restore_btn)

        bkp_layout.addLayout(bkp_btn_layout)

        bkp_layout.addWidget(QLabel("── 导出 / 导入 ──"))

        # 导出/导入按钮
        io_btn_layout = QHBoxLayout()

        export_json_btn = QPushButton("📄 导出JSON")
        export_json_btn.setCursor(Qt.PointingHandCursor)
        export_json_btn.setToolTip("导出台账为明文JSON文件（用于存档）")
        export_json_btn.clicked.connect(self._on_export_json)
        io_btn_layout.addWidget(export_json_btn)

        import_json_btn = QPushButton("📥 导入JSON")
        import_json_btn.setCursor(Qt.PointingHandCursor)
        import_json_btn.setToolTip("从JSON文件导入台账（支持合并/覆盖）")
        import_json_btn.clicked.connect(self._on_import_json)
        io_btn_layout.addWidget(import_json_btn)

        bkp_layout.addLayout(io_btn_layout)

        # 黑名单列表展示
        bkp_layout.addWidget(QLabel("── 黑名单 ──"))
        self._bl_list = QTextEdit()
        self._bl_list.setReadOnly(True)
        self._bl_list.setFont(QFont("Consolas", 9))
        self._bl_list.setMaximumHeight(100)
        bkp_layout.addWidget(self._bl_list)

        bottom_layout.addWidget(backup_group, stretch=1)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([280, 370])

    def _apply_style(self) -> None:
        t = self._theme_engine.current_theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t['card_bg']}; }}
            QGroupBox {{
                border: 1px solid {t['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: {t['text_main']};
            }}
            QPushButton {{
                background-color: {t['primary']};
                color: {t['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{ background-color: {t['primary_hover']}; }}
            QLineEdit {{
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QLineEdit:focus {{ border-color: {t['primary']}; }}
            QTableWidget {{
                border: 1px solid {t['border']};
                gridline-color: {t['card_bg']};
            }}
            QComboBox {{
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)
        # 激活码结果框样式（特殊处理）
        self._code_result.setStyleSheet(
            f"QLineEdit {{ color: {t['primary']}; background-color: {t['hover_bg']}; }}"
        )
        # 生成时间标签样式
        self._gen_time_label.setStyleSheet(f"color: {t['success']};")

    # ═══════════════════════════════════════════
    # 事件处理
    # ═══════════════════════════════════════════

    def _on_generate(self) -> None:
        machine_code = self._machine_input.text().strip().upper()
        if not machine_code:
            QMessageBox.warning(self, "提示", "请输入机器码")
            return
        if len(machine_code) != 32:
            QMessageBox.warning(self, "提示", "机器码格式不正确，应为32位")
            return
        # 获取当前选择的有效期天数
        validity_idx = self._validity_combo.currentIndex()
        validity_days = [0, 1825, 3650, 1095, 730, 365, 180, 90, 30, 7][validity_idx]
        # 生成18位激活码（含有效期编码）
        full_code = generate_code_for_machine(machine_code, validity_days)
        self._code_result.setText(full_code)
        # 显示生成时间和有效期信息
        from datetime import datetime, timedelta
        gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if validity_days > 0:
            expire_at = (datetime.now() + timedelta(days=validity_days)).strftime("%Y-%m-%d")
            self._gen_time_label.setText(f"⏱ {gen_time}  |  有效期{validity_days}天  到期{expire_at}")
        else:
            self._gen_time_label.setText(f"⏱ {gen_time}  |  永久授权")

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

        # 解析有效期
        validity_map = {
            0: 0,     # 永久
            1: 1825,  # 5年
            2: 3650,  # 10年
            3: 1095,  # 3年
            4: 730,   # 2年
            5: 365,   # 1年
            6: 180,   # 半年
            7: 90,    # 季度
            8: 30,    # 月度
            9: 7,     # 周度
        }
        validity_days = validity_map.get(self._validity_combo.currentIndex(), 0)

        if save_record(name or "未命名", machine_code, code, note, validity_days):
            expire_info = ""
            if validity_days > 0:
                from datetime import datetime, timedelta
                expire_at = (datetime.now() + timedelta(days=validity_days)).strftime("%Y-%m-%d")
                expire_info = f"\n\n有效期：{validity_days}天\n到期时间：{expire_at}"
            QMessageBox.information(self, "成功", f"台账记录已保存（加密存储）{expire_info}")
            self._refresh_records()
            self._name_input.clear()
            self._note_input.clear()
            self._gen_time_label.clear()
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

    # ── 备份/恢复/导出/导入 ──

    def _on_backup(self) -> None:
        ok, result = backup_records()
        if ok:
            QMessageBox.information(self, "备份成功", f"台账已备份至：\n{result}")
            self._refresh_backup_list()
        else:
            QMessageBox.warning(self, "备份失败", result)

    def _on_restore(self) -> None:
        backup_file = self._backup_combo.currentText()
        if not backup_file:
            QMessageBox.warning(self, "提示", "请先选择要恢复的备份文件")
            return
        if QMessageBox.question(
            self, "确认恢复",
            f"确定从备份恢复？\n\n备份文件：{backup_file}\n\n"
            "恢复前会自动创建当前台账的安全备份。"
        ) != QMessageBox.Yes:
            return
        ok, msg = restore_backup(backup_file)
        if ok:
            QMessageBox.information(self, "恢复成功", msg)
            self._refresh_records()
            self._refresh_backup_list()
        else:
            QMessageBox.critical(self, "恢复失败", msg)

    def _on_export_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "导出台账为JSON", "admin_records_export.json", "JSON文件 (*.json)"
        )
        if not path:
            return
        ok, msg = export_records_to_json(path)
        if ok:
            QMessageBox.information(self, "导出成功", msg)
        else:
            QMessageBox.warning(self, "导出失败", msg)

    def _on_import_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "从JSON导入台账", "", "JSON文件 (*.json)"
        )
        if not path:
            return
        # 选择合并还是覆盖
        choice = QInputDialog.getItem(
            self, "导入方式",
            "选择导入方式：\n合并 = 追加新记录\n覆盖 = 替换全部台账",
            ["合并（推荐）", "覆盖"], 0, False
        )
        if not choice:
            return
        merge = choice.startswith("合并")
        ok, msg = import_records_from_json(path, merge=merge)
        if ok:
            QMessageBox.information(self, "导入成功", msg)
            self._refresh_records()
        else:
            QMessageBox.warning(self, "导入失败", msg)

    # ═══════════════════════════════════════════
    # 刷新
    # ═══════════════════════════════════════════

    def _refresh_records(self) -> None:
        records = load_records()
        self._records_table.setRowCount(len(records))
        for i, rec in enumerate(records):
            self._records_table.setItem(i, 0, QTableWidgetItem(rec.get("name", "")))
            mc = rec.get("machine_code", "")
            self._records_table.setItem(i, 1, QTableWidgetItem(mc[:12] + "..." if len(mc) > 12 else mc))
            self._records_table.setItem(i, 2, QTableWidgetItem(rec.get("activation_code", "")))
            # 格式化时间显示
            self._records_table.setItem(i, 3, QTableWidgetItem(format_record_time(rec.get("created_at", ""))))
            # 有效期状态
            expire_text = get_record_expire_status(rec)
            expire_item = QTableWidgetItem(expire_text)
            # 永久有效绿色，有期限蓝色
            if rec.get("validity_days", 0) == 0:
                expire_item.setForeground(Qt.darkGreen)
            else:
                expire_item.setForeground(Qt.darkBlue)
            self._records_table.setItem(i, 4, expire_item)
            self._records_table.setItem(i, 5, QTableWidgetItem(rec.get("note", "")))

    def _refresh_blacklist(self) -> None:
        codes = load_blacklist()
        self._bl_list.setPlainText("\n".join(codes) if codes else "（黑名单为空）")

    def _refresh_backup_list(self) -> None:
        backups = list_backups()
        self._backup_combo.clear()
        self._backup_combo.addItems(backups)


def run_admin_tool():
    """启动管理员制码工具"""
    app = QApplication(sys.argv)
    window = AdminToolWindow()
    # 默认窗口大小为屏幕可用区域宽高的80%
    screen = app.primaryScreen().availableGeometry()
    w = int(screen.width() * 0.8)
    h = int(screen.height() * 0.8)
    window.resize(w, h)
    # 居中显示
    window.move(
        (screen.width() - w) // 2,
        (screen.height() - h) // 2,
    )
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_admin_tool()
