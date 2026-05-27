from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,
                               QAbstractItemView, QCheckBox)
from PyQt5.QtCore import Qt

from src.core.device_manager import DEVICE_TEMPLATES
from src.core.theme_engine import ThemeEngine


class DeviceTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme_engine = ThemeEngine.get()
        self.setWindowTitle("设备模板库")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.selected_templates = []
        self.init_ui()

    def init_ui(self):
        t = self._theme_engine.current_theme
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("设备模板库")
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {t['text_main']};")
        layout.addWidget(title)

        desc = QLabel("选择模板后，将自动填充厂商、设备类型和协议信息，您只需补充IP和登录凭据即可。")
        desc.setStyleSheet(f"font-size: 13pt; color: {t['text_tertiary']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        template_group = QGroupBox("可用模板")
        template_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14pt; font-weight: bold; color: {t['text_main']};
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                margin-top: 8px; padding: 16px; background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        template_layout = QVBoxLayout()
        template_layout.setSpacing(12)

        self.template_table = QTableWidget()
        self.template_table.setColumnCount(4)
        self.template_table.setHorizontalHeaderLabels(["选择", "模板名称", "厂商", "设备类型"])
        self.template_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.template_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.template_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {t['border']}; border-radius: {t['radius_md']}px;
                background-color: {t['card_bg']}; gridline-color: {t['hover_bg']};
            }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{
                background-color: {t['hover_bg']}; border: none;
                border-bottom: 1px solid {t['border']}; padding: 8px;
                font-weight: bold; color: {t['text_main']};
            }}
        """)

        row = 0
        for name, info in DEVICE_TEMPLATES.items():
            self.template_table.insertRow(row)
            cb = QCheckBox()
            self.template_table.setCellWidget(row, 0, cb)
            self.template_table.setItem(row, 1, QTableWidgetItem(name))
            self.template_table.setItem(row, 2, QTableWidgetItem(info["厂商"]))
            self.template_table.setItem(row, 3, QTableWidgetItem(info["设备类型"]))
            row += 1

        template_layout.addWidget(self.template_table)

        select_layout = QHBoxLayout()
        select_layout.setSpacing(12)
        self.select_all_cb = QCheckBox("全选")
        self.select_all_cb.setStyleSheet(f"font-size: 13pt;")
        self.select_all_cb.stateChanged.connect(self._toggle_select_all)
        select_layout.addWidget(self.select_all_cb)
        select_layout.addStretch()
        template_layout.addLayout(select_layout)

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(88, 30)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']}; border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 11pt; padding: 5px 8px;
            }}
            QPushButton:hover {{ border: 1px solid {t['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("应用选中模板")
        apply_btn.setFixedSize(128, 30)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['hover_bg']}; color: {t['text_main']};
                border: 1px solid {t['border']};
                border-radius: {t['radius_md']}px; font-size: 11pt; padding: 5px 8px;
            }}
            QPushButton:hover {{
                background-color: {t['card_bg']};
                border-color: {t['border']};
                color: {t['text_secondary']};
            }}
            QPushButton:disabled {{
                background-color: {t['hover_bg']};
                border-color: {t['border']};
                color: {t['text_tertiary']};
            }}
        """)
        apply_btn.clicked.connect(self._apply_templates)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _toggle_select_all(self, state):
        for row in range(self.template_table.rowCount()):
            widget = self.template_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(state == Qt.Checked)

    def _apply_templates(self):
        self.selected_templates = []
        for row in range(self.template_table.rowCount()):
            widget = self.template_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                name_item = self.template_table.item(row, 1)
                if name_item:
                    self.selected_templates.append(name_item.text())

        if not self.selected_templates:
            QMessageBox.warning(self, "提示", "请至少选择一个模板")
            return

        self.accept()

    def get_selected_templates(self):
        return self.selected_templates
