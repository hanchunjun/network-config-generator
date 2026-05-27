import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QFrame,
                               QMessageBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests

from src.core.theme_engine import ThemeEngine
from src.utils.resource_path import get_config_path, ensure_dirs
from src.core.secure_config import SecureConfigFile

AI_CONFIG_PATH: str = get_config_path("config/ai_config.json")
_secure_cfg = SecureConfigFile.instance()

AI_VENDORS = [
    ("OpenAI", "https://api.openai.com/v1", "gpt-4o"),
    ("DeepSeek", "https://api.deepseek.com/v1", "deepseek-chat"),
    ("通义千问", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
    ("智谱GLM", "https://open.bigmodel.cn/api/paas/v4", "glm-4"),
    ("Moonshot", "https://api.moonshot.cn/v1", "moonshot-v1-8k"),
    ("自定义", "", "")
]


class AIConnectivityThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, base_url, api_key, model):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def run(self):
        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                self.finished_signal.emit(True, "连接成功，模型响应正常")
            elif resp.status_code == 401:
                self.finished_signal.emit(False, "认证失败：API Key 无效")
            elif resp.status_code == 404:
                self.finished_signal.emit(False, "模型不存在：请检查模型名称")
            else:
                self.finished_signal.emit(False, f"请求失败：HTTP {resp.status_code} - {resp.text[:200]}")
        except requests.exceptions.Timeout:
            self.finished_signal.emit(False, "连接超时：请检查 BaseURL 地址")
        except requests.exceptions.ConnectionError:
            self.finished_signal.emit(False, "无法连接：请检查 BaseURL 地址是否正确")
        except Exception as e:
            self.finished_signal.emit(False, f"测试失败：{str(e)}")


class SystemSettingsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.test_thread = None
        self.profiles: list = []
        self.active_name: str = ""
        self._is_new_profile: bool = False
        self._theme_engine = ThemeEngine.get()
        self.init_ui()
        self._theme_engine.theme_changed.connect(self._on_theme_changed)
        self._apply_theme_style()
        self.load_config()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._title_label = QLabel("模型设置")
        self._title_label.setStyleSheet("font-size: 14pt; font-weight: bold; text-decoration: none;")
        layout.addWidget(self._title_label)

        selector_group = QGroupBox("")
        selector_group.setStyleSheet("QGroupBox { border: none; background: transparent; margin: 0; padding: 0; }")
        sel_layout = QHBoxLayout()
        sel_layout.setSpacing(8)

        self._sel_label = QLabel("配置选择：")
        self._sel_label.setStyleSheet("font-size: 11pt;")
        sel_layout.addWidget(self._sel_label)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(260)
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)
        sel_layout.addWidget(self.profile_combo)

        self.add_btn = QPushButton("+ 新增")
        self.add_btn.setFixedSize(80, 30)
        self.add_btn.clicked.connect(self.on_add_new)
        sel_layout.addWidget(self.add_btn)

        self.del_btn = QPushButton("删除")
        self.del_btn.setFixedSize(60, 30)
        self.del_btn.clicked.connect(self.on_delete_profile)
        sel_layout.addWidget(self.del_btn)

        self.rename_btn = QPushButton("✏️ 重命名")
        self.rename_btn.setFixedSize(80, 30)
        self.rename_btn.clicked.connect(self.on_rename_profile)
        sel_layout.addWidget(self.rename_btn)

        self.profile_count_lbl = QLabel("")
        self.profile_count_lbl.setStyleSheet("font-size: 11pt;")
        sel_layout.addWidget(self.profile_count_lbl)
        sel_layout.addStretch()

        selector_group.setLayout(sel_layout)
        layout.addWidget(selector_group)

        ai_group = QGroupBox("AI 模型配置")
        self._ai_group = ai_group
        ai_layout = QVBoxLayout()
        ai_layout.setSpacing(14)

        vendor_layout = QHBoxLayout()
        vendor_label = QLabel("模型厂商")
        vendor_label.setFixedWidth(120)
        vendor_label.setStyleSheet("font-size: 11pt; font-weight: normal;")
        vendor_layout.addWidget(vendor_label)
        self.vendor_combo = QComboBox()
        self.vendor_combo.setFixedWidth(280)
        for name, _, _ in AI_VENDORS:
            self.vendor_combo.addItem(name)
        self.vendor_combo.currentIndexChanged.connect(self.on_vendor_changed)
        vendor_layout.addWidget(self.vendor_combo)
        vendor_layout.addStretch()
        ai_layout.addLayout(vendor_layout)

        url_layout = QHBoxLayout()
        url_label = QLabel("BaseURL")
        url_label.setFixedWidth(120)
        url_label.setStyleSheet("font-size: 11pt; font-weight: normal;")
        url_layout.addWidget(url_label)
        self.url_input = QLineEdit()
        self.url_input.setFixedWidth(520)
        self.url_input.setPlaceholderText("请输入API接口地址（如 https://api.openai.com/v1）")
        url_layout.addWidget(self.url_input)
        url_layout.addStretch()
        ai_layout.addLayout(url_layout)

        key_layout = QHBoxLayout()
        key_label = QLabel("API Key")
        key_label.setFixedWidth(120)
        key_label.setStyleSheet("font-size: 11pt; font-weight: normal;")
        key_layout.addWidget(key_label)
        self.key_input = QLineEdit()
        self.key_input.setFixedWidth(520)
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setPlaceholderText("请输入API Key（sk-...）")
        key_layout.addWidget(self.key_input)

        self.show_key_btn = QPushButton("显示")
        self.show_key_btn.setFixedSize(64, 30)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.show_key_btn)
        key_layout.addStretch()
        ai_layout.addLayout(key_layout)

        model_layout = QHBoxLayout()
        model_label = QLabel("模型名称")
        model_label.setFixedWidth(120)
        model_label.setStyleSheet("font-size: 11pt; font-weight: normal;")
        model_layout.addWidget(model_label)
        self.model_input = QLineEdit()
        self.model_input.setFixedWidth(320)
        self.model_input.setPlaceholderText("请输入模型名称（如 gpt-4o、deepseek-chat）")
        model_layout.addWidget(self.model_input)
        model_layout.addStretch()
        ai_layout.addLayout(model_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        self.save_btn = QPushButton("保存配置")
        self.save_btn.setFixedSize(120, 30)
        self.save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(self.save_btn)

        self.test_btn = QPushButton("测试连通性")
        self.test_btn.setFixedSize(120, 30)
        self.test_btn.clicked.connect(self.test_connectivity)
        btn_layout.addWidget(self.test_btn)

        self.test_status = QLabel("")
        self.test_status.setStyleSheet("font-size: 11pt;")
        btn_layout.addWidget(self.test_status)
        btn_layout.addStretch()
        ai_layout.addLayout(btn_layout)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        general_group = QGroupBox("全局设置")
        self._general_group = general_group
        general_layout = QVBoxLayout()
        general_layout.setSpacing(12)

        self.tips_checkbox = QCheckBox("开启操作提示与异常提醒")
        self.tips_checkbox.setChecked(True)
        self.tips_checkbox.setStyleSheet("font-size: 11pt; font-weight: normal;")
        general_layout.addWidget(self.tips_checkbox)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        layout.addStretch()
        self.setLayout(layout)
        self._apply_theme_style()

    def _on_theme_changed(self, theme_id: str) -> None:
        self._apply_theme_style()

    def _apply_theme_style(self) -> None:
        t = self._theme_engine.current_theme
        primary = t["primary"]
        primary_hover = t["primary_hover"]
        success = t["success"]
        success_hover = t["success_hover"]
        danger = t["danger"]
        danger_hover = t["danger_hover"]
        text_main = t["text_main"]
        text_secondary = t["text_secondary"]
        text_tertiary = t["text_tertiary"]
        text_primary = t["text_primary"]
        border = t["border"]
        input_bg = t["input_bg"]
        hover_bg = t["hover_bg"]
        card_bg = t["card_bg"]
        radius_md = t["radius_md"]
        radius_lg = t["radius_lg"]

        # 标题
        self._title_label.setStyleSheet(
            f"font-size: 14pt; font-weight: bold; color: {text_main}; text-decoration: none;"
        )

        # 选择器标签
        self._sel_label.setStyleSheet(f"font-size: 11pt; color: {text_secondary};")
        self.profile_count_lbl.setStyleSheet(f"font-size: 11pt; color: {text_tertiary};")

        # 配置选择栏按钮（次要按钮样式）
        secondary_btn = f"""
            QPushButton {{
                background-color: transparent;
                color: {text_secondary};
                border: 1px solid {border};
                border-radius: {radius_md}px;
                font-size: 11pt;
                padding: 5px 8px;
                min-height: 28px;
            }}
            QPushButton:hover {{ background-color: transparent; border-color: {border_deep}; }}
        """
        self.add_btn.setStyleSheet(secondary_btn)
        self.del_btn.setStyleSheet(secondary_btn)
        self.rename_btn.setStyleSheet(secondary_btn)

        # 下拉框样式
        combo_style = f"""
            QComboBox {{
                border: 1px solid {t['input_border']};
                border-radius: {radius_md}px;
                padding: 6px 14px;
                font-size: 11pt;
                background-color: {card_bg};
                color: {text_main};
            }}
            QComboBox:hover {{ border-color: {primary}; }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox::down-arrow {{ image: none; border: none; }}
            QComboBox QAbstractItemView {{
                border: 1px solid {border};
                selection-background-color: {hover_bg};
                background-color: {card_bg};
                color: {text_main};
            }}
        """
        self.profile_combo.setStyleSheet(combo_style)
        self.vendor_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {t['input_border']};
                border-radius: {radius_md}px;
                padding: 4px 8px;
                font-size: 11pt;
                background-color: {input_bg};
                color: {text_main};
            }}
            QComboBox:hover {{ border: 1px solid {primary}; }}
            QComboBox::drop-down {{ border: none; }}
        """)

        # 输入框通用样式
        line_style = f"""
            QLineEdit {{
                border: 1px solid {t['input_border']};
                border-radius: {radius_md}px;
                padding: 4px 8px;
                font-size: 11pt;
                background-color: {input_bg};
                color: {text_main};
            }}
            QLineEdit:focus {{ border: 1px solid {primary}; background-color: {card_bg}; }}
        """
        self.url_input.setStyleSheet(line_style)
        self.key_input.setStyleSheet(line_style)
        self.model_input.setStyleSheet(line_style)

        # 显示/隐藏按钮
        self.show_key_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {border};
                border-radius: {radius_md}px;
                font-size: 11pt;
                color: {text_secondary};
            }}
            QPushButton:hover {{ border-color: {primary}; color: {primary}; }}
        """)

        # 保存按钮（次要按钮样式，统一无色）
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_secondary};
                border: 1px solid {border};
                border-radius: {radius_md}px;
                font-size: 11pt;
                padding: 5px 8px;
            }}
            QPushButton:hover {{
                background-color: transparent;
                border-color: {border_deep};
                color: {text_main};
            }}
        """)

        # 测试连通性按钮（次要按钮样式，统一无色）
        self.test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_secondary};
                border: 1px solid {border};
                border-radius: {radius_md}px;
                font-size: 11pt;
                padding: 5px 8px;
            }}
            QPushButton:hover {{
                background-color: transparent;
                border-color: {border_deep};
                color: {text_main};
            }}
            QPushButton:disabled {{
                background-color: transparent;
                border-color: {border};
                color: {text_tertiary};
            }}
        """)

        # 测试状态标签
        self.test_status.setStyleSheet(f"font-size: 11pt; color: {text_tertiary};")

        # AI 模型配置分组框
        self._ai_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 12pt;
                font-weight: bold;
                color: {text_main};
                border: 1px solid {border};
                border-radius: {radius_lg}px;
                margin-top: 10px;
                padding: 18px 14px 10px 14px;
                background-color: {card_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }}
        """)

        # 字段标签（模型厂商/BaseURL/API Key/模型名称）
        for lbl in self._ai_group.findChildren(QLabel):
            lbl.setStyleSheet(f"font-size: 11pt; color: {text_secondary}; font-weight: normal;")

        # 全局设置分组框
        self._general_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 12pt;
                font-weight: bold;
                color: {text_main};
                border: 1px solid {border};
                border-radius: {radius_lg}px;
                margin-top: 10px;
                padding: 18px 14px 10px 14px;
                background-color: {card_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }}
        """)

        # 复选框
        self.tips_checkbox.setStyleSheet(
            f"font-size: 11pt; color: {text_secondary}; font-weight: normal;"
        )

    def on_vendor_changed(self, index):
        if index < len(AI_VENDORS):
            _, url, model = AI_VENDORS[index]
            if url:
                self.url_input.setText(url)
            if model:
                self.model_input.setText(model)

    def toggle_key_visibility(self):
        if self.key_input.echoMode() == QLineEdit.Password:
            self.key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("隐藏")
        else:
            self.key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("显示")

    def load_config(self):
        config = _secure_cfg.load(AI_CONFIG_PATH)
        if config is None:
            config = {}
        if "profiles" not in config and "base_url" in config:
            config["profiles"] = [{
                "name": "默认配置",
                "vendor": config.get("vendor", ""),
                "base_url": config.get("base_url", ""),
                "api_key": config.get("api_key", ""),
                "model": config.get("model", "")
            }]
            config["active_profile"] = "默认配置"
        self.profiles = config.get("profiles", [])
        self.active_name = config.get("active_profile", "")
        if not self.profiles:
            self.profiles.append({
                "name": "默认配置",
                "vendor": "",
                "base_url": "",
                "api_key": "",
                "model": ""
            })
            self.active_name = "默认配置"
        self._refresh_profile_list()
        self._load_active_to_form()

    def _refresh_profile_list(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        names = [p["name"] for p in self.profiles]
        self.profile_combo.addItems(names)
        if self.active_name in names:
            self.profile_combo.setCurrentIndex(names.index(self.active_name))
        else:
            self.active_name = names[0] if names else ""
            self.profile_combo.setCurrentIndex(0)
        self.profile_combo.blockSignals(False)
        self.del_btn.setEnabled(len(self.profiles) > 1)
        self.rename_btn.setEnabled(len(self.profiles) > 0)
        self.profile_count_lbl.setText(f"共 {len(self.profiles)} 个配置")

    def _load_active_to_form(self):
        profile = None
        for p in self.profiles:
            if p["name"] == self.active_name:
                profile = p
                break
        if profile is None and self.profiles:
            profile = self.profiles[0]
            self.active_name = profile["name"]
        if profile is None:
            return
        self.url_input.setText(profile.get("base_url", ""))
        self.key_input.setText(profile.get("api_key", ""))
        self.model_input.setText(profile.get("model", ""))
        vendor = profile.get("vendor", "")
        if vendor:
            for i, (name, _, _) in enumerate(AI_VENDORS):
                if name == vendor:
                    self.vendor_combo.setCurrentIndex(i)
                    break
        model_display = profile.get("model", "未设置")
        url_host = ""
        raw_url = profile.get("base_url", "")
        if raw_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(raw_url)
                url_host = parsed.hostname or raw_url
            except Exception:
                url_host = raw_url[:40] + "..." if len(raw_url) > 40 else raw_url
        self.test_status.setText(f"当前：{self.active_name} | 模型：{model_display} | {url_host}")
        self.test_status.setStyleSheet(f"font-size: 11pt; color: {self._theme_engine.current_theme['text_tertiary']};")
        self._is_new_profile = False

    def on_profile_changed(self, index):
        if index < 0 or index >= len(self.profiles):
            return
        old_name = self.active_name
        self.active_name = self.profiles[index]["name"]
        self._load_active_to_form()
        if old_name != self.active_name:
            self.test_status.setStyleSheet(f"font-size: 11pt; color: {self._theme_engine.current_theme['primary']};")

    def on_add_new(self):
        existing_names = {p["name"] for p in self.profiles}
        base = f"新配置{len(self.profiles) + 1}"
        name = base
        idx = 1
        while name in existing_names:
            idx += 1
            name = f"{base}_{idx}"
        new_p = {"name": name, "vendor": "", "base_url": "", "api_key": "", "model": ""}
        self.profiles.append(new_p)
        self.active_name = name
        self._is_new_profile = True
        self._refresh_profile_list()
        self.url_input.clear()
        self.key_input.clear()
        self.model_input.clear()
        self.vendor_combo.setCurrentIndex(len(AI_VENDORS) - 1)
        self.url_input.setFocus()

    def on_delete_profile(self):
        if len(self.profiles) <= 1:
            QMessageBox.information(self, "提示", "至少需要保留一个配置")
            return
        current = self.active_name
        reply = QMessageBox.question(
            self, "确认删除",
            f'确定要删除配置「{current}」吗？\n删除后不可恢复。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.profiles = [p for p in self.profiles if p["name"] != current]
        self.active_name = self.profiles[0]["name"]
        self._refresh_profile_list()
        self._load_active_to_form()
        self._save_all()

    def on_rename_profile(self):
        from PyQt5.QtWidgets import QInputDialog
        old_name = self.active_name
        existing = {p["name"] for p in self.profiles}
        new_name, ok = QInputDialog.getText(
            self, "重命名配置",
            f'将「{old_name}」改名为：',
            text=old_name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        if new_name == old_name:
            return
        if new_name in existing:
            QMessageBox.warning(self, "名称重复", f'已存在名为「{new_name}」的配置')
            return
        for p in self.profiles:
            if p["name"] == old_name:
                p["name"] = new_name
                break
        self.active_name = new_name
        self._refresh_profile_list()
        self.test_status.setText(f"已重命名：{old_name} → {new_name}")
        self.test_status.setStyleSheet(f"font-size: 11pt; color: {self._theme_engine.current_theme['success']};")
        self._save_all()

    def save_config(self):
        name = self.active_name.strip()
        if not name:
            QMessageBox.warning(self, "名称不能为空", "请先选择或新增一个配置")
            return
        vendor = self.vendor_combo.currentText()
        base_url = self.url_input.text().strip()
        api_key = self.key_input.text().strip()
        model = self.model_input.text().strip()
        if not base_url or not api_key or not model:
            QMessageBox.warning(self, "参数不完整", "BaseURL、API Key 和模型名称不能为空")
            return
        updated = False
        for p in self.profiles:
            if p["name"] == name:
                p.update({
                    "vendor": vendor,
                    "base_url": base_url,
                    "api_key": api_key,
                    "model": model,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                updated = True
                break
        if not updated:
            self.profiles.append({
                "name": name,
                "vendor": vendor,
                "base_url": base_url,
                "api_key": api_key,
                "model": model,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        self._save_all()
        QMessageBox.information(self, "保存成功", f"AI 配置「{name}」已保存")

    def _save_all(self):
        config = {
            "profiles": self.profiles,
            "active_profile": self.active_name
        }
        ok = _secure_cfg.save(AI_CONFIG_PATH, config)
        if not ok:
            QMessageBox.warning(self, "保存失败", "配置文件加密保存失败，已回退为明文存储")

    def test_connectivity(self):
        base_url = self.url_input.text().strip()
        api_key = self.key_input.text().strip()
        model = self.model_input.text().strip()
        if not base_url or not api_key or not model:
            QMessageBox.warning(self, "参数不完整", "请填写 BaseURL、API Key 和模型名称")
            return
        self.test_btn.setEnabled(False)
        self.test_status.setText("正在测试连接...")
        self.test_status.setStyleSheet(f"font-size: 11pt; color: {self._theme_engine.current_theme['primary']};")
        self.test_thread = AIConnectivityThread(base_url, api_key, model)
        self.test_thread.finished_signal.connect(self.on_test_finished)
        self.test_thread.start()

    def on_test_finished(self, success, message):
        self.test_btn.setEnabled(True)
        t = self._theme_engine.current_theme
        if success:
            self.test_status.setText(message)
            self.test_status.setStyleSheet(f"font-size: 11pt; color: {t['success']};")
        else:
            self.test_status.setText(message)
            self.test_status.setStyleSheet(f"font-size: 11pt; color: {t['text_secondary']};")


def get_active_ai_config() -> dict:
        config = _secure_cfg.load(AI_CONFIG_PATH)
        if config is None:
            return {}
        profiles = config.get("profiles", [])
        active = config.get("active_profile", "")
        if "profiles" in config:
            for p in profiles:
                if p["name"] == active:
                    return {
                        "vendor": p.get("vendor", ""),
                        "base_url": p.get("base_url", ""),
                        "api_key": p.get("api_key", ""),
                        "model": p.get("model", "")
                    }
            if profiles:
                p = profiles[0]
                return {
                    "vendor": p.get("vendor", ""),
                    "base_url": p.get("base_url", ""),
                    "api_key": p.get("api_key", ""),
                    "model": p.get("model", "")
                }
        else:
            return {
                "vendor": config.get("vendor", ""),
                "base_url": config.get("base_url", ""),
                "api_key": config.get("api_key", ""),
                "model": config.get("model", "")
            }
        return {}
