from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,
                               QAbstractItemView, QCheckBox)
from PyQt5.QtCore import Qt

from src.core.device_manager import DEVICE_TEMPLATES


class DeviceTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设备模板库")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.selected_templates = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("设备模板库")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1D2129;")
        layout.addWidget(title)

        desc = QLabel("选择模板后，将自动填充厂商、设备类型和协议信息，您只需补充IP和登录凭据即可。")
        desc.setStyleSheet("font-size: 13px; color: #86909C;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        template_group = QGroupBox("可用模板")
        template_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #1D2129;
                border: 1px solid #E5E6EB; border-radius: 6px;
                margin-top: 8px; padding: 16px; background-color: #FAFBFC;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }
        """)
        template_layout = QVBoxLayout()
        template_layout.setSpacing(12)

        self.template_table = QTableWidget()
        self.template_table.setColumnCount(4)
        self.template_table.setHorizontalHeaderLabels(["选择", "模板名称", "厂商", "设备类型"])
        self.template_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.template_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.template_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E6EB; border-radius: 4px;
                background-color: #FFFFFF; gridline-color: #F2F3F5;
            }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background-color: #F7F8FA; border: none;
                border-bottom: 1px solid #E5E6EB; padding: 8px;
                font-weight: bold; color: #1D2129;
            }
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
        self.select_all_cb.setStyleSheet("font-size: 13px;")
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
        cancel_btn.setFixedSize(100, 38)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA; border: 1px solid #E5E6EB;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { border: 1px solid #165DFF; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("应用选中模板")
        apply_btn.setFixedSize(140, 38)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #165DFF; color: white; border: none;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { background-color: #0E42D2; }
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