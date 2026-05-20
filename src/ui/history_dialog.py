from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt


class HistoryDialog(QDialog):
    def __init__(self, parent=None, history=None):
        super().__init__(parent)
        self.setWindowTitle("设备变更历史")
        self.setMinimumWidth(700)
        self.setMinimumHeight(450)
        self.history = history or []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("设备变更历史")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1D2129;")
        layout.addWidget(title)

        if not self.history:
            empty_label = QLabel("暂无变更记录")
            empty_label.setStyleSheet("font-size: 14px; color: #86909C;")
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)
        else:
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["时间", "操作", "详情", "设备数"])
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setStyleSheet("""
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

            action_labels = {
                "add": "新增设备", "delete": "删除设备", "modify": "修改设备",
                "import": "导入清单", "export": "导出清单",
                "template": "应用模板", "discover": "批量发现",
                "save": "保存清单", "batch_paste": "批量粘贴",
            }

            for row, entry in enumerate(reversed(self.history)):
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp", "")))
                action = entry.get("action", "")
                table.setItem(row, 1, QTableWidgetItem(action_labels.get(action, action)))
                table.setItem(row, 2, QTableWidgetItem(entry.get("details", "")))
                table.setItem(row, 3, QTableWidgetItem(str(entry.get("device_count", ""))))

            layout.addWidget(table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 38)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA; border: 1px solid #E5E6EB;
                border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { border: 1px solid #165DFF; }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)