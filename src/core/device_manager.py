import os
import json
import csv
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.core.crypto_utils import encrypt_password, decrypt_password, is_encrypted, migrate_old_passwords
from src.core.logger import netops_logger
from src.utils.validators import DeviceValidator, ProjectValidator
from src.utils.file_operators import DeviceFileManager, JSONFileManager, AtomicFileWriter

VENDORS: List[str] = ["锐捷", "华为", "H3C", "思科"]
DEVICE_TYPES: List[str] = ["核心交换机", "接入交换机", "路由器", "AC控制器", "防火墙", "负载均衡", "服务器"]
PROTOCOLS: List[str] = ["ssh", "telnet"]
DEVICE_HEADERS: List[str] = ["IP地址", "厂商", "设备类型", "用户名", "密码", "协议", "特权密码", "分组", "标签"]

DEVICE_TEMPLATES = {
    "锐捷-核心交换机": {
        "厂商": "锐捷", "设备类型": "核心交换机", "协议": "ssh",
        "描述": "锐捷 RG-S8600E / RG-S7800E 系列核心交换机"
    },
    "锐捷-接入交换机": {
        "厂商": "锐捷", "设备类型": "接入交换机", "协议": "ssh",
        "描述": "锐捷 RG-S2900 / RG-S5300 系列接入交换机"
    },
    "锐捷-路由器": {
        "厂商": "锐捷", "设备类型": "路由器", "协议": "ssh",
        "描述": "锐捷 RG-RSR 系列路由器"
    },
    "锐捷-AC控制器": {
        "厂商": "锐捷", "设备类型": "AC控制器", "协议": "ssh",
        "描述": "锐捷 RG-WS 系列无线控制器"
    },
    "华为-核心交换机": {
        "厂商": "华为", "设备类型": "核心交换机", "协议": "ssh",
        "描述": "华为 S12700 / S9700 系列核心交换机"
    },
    "华为-接入交换机": {
        "厂商": "华为", "设备类型": "接入交换机", "协议": "ssh",
        "描述": "华为 S5700 / S3700 系列接入交换机"
    },
    "华为-路由器": {
        "厂商": "华为", "设备类型": "路由器", "协议": "ssh",
        "描述": "华为 AR / NE 系列路由器"
    },
    "华为-AC控制器": {
        "厂商": "华为", "设备类型": "AC控制器", "协议": "ssh",
        "描述": "华为 AC6000 / AC8000 系列无线控制器"
    },
    "H3C-核心交换机": {
        "厂商": "H3C", "设备类型": "核心交换机", "协议": "ssh",
        "描述": "H3C S10500 / S7500E 系列核心交换机"
    },
    "H3C-接入交换机": {
        "厂商": "H3C", "设备类型": "接入交换机", "协议": "ssh",
        "描述": "H3C S5500 / S5100 系列接入交换机"
    },
    "H3C-路由器": {
        "厂商": "H3C", "设备类型": "路由器", "协议": "ssh",
        "描述": "H3C SR / MSR 系列路由器"
    },
    "H3C-AC控制器": {
        "厂商": "H3C", "设备类型": "AC控制器", "协议": "ssh",
        "描述": "H3C WX 系列无线控制器"
    },
    "思科-核心交换机": {
        "厂商": "思科", "设备类型": "核心交换机", "协议": "ssh",
        "描述": "Cisco Catalyst 9000 / Nexus 系列核心交换机"
    },
    "思科-接入交换机": {
        "厂商": "思科", "设备类型": "接入交换机", "协议": "ssh",
        "描述": "Cisco Catalyst 2000 / 3000 系列接入交换机"
    },
    "思科-路由器": {
        "厂商": "思科", "设备类型": "路由器", "协议": "ssh",
        "描述": "Cisco ISR / ASR 系列路由器"
    },
    "思科-AC控制器": {
        "厂商": "思科", "设备类型": "AC控制器", "协议": "ssh",
        "描述": "Cisco WLC 系列无线控制器"
    },
}


class DeviceManager:
    def __init__(self, project_path=None):
        self.project_path = project_path
        self.devices = []

    def set_project(self, project_path):
        self.project_path = project_path
        self.devices = []

    def _device_file(self):
        if not self.project_path:
            return None
        return os.path.join(self.project_path, "config", "device_list.txt")

    def _history_file(self):
        if not self.project_path:
            return None
        return os.path.join(self.project_path, "config", "device_history.json")

    def load_devices(self):
        """
        加载设备列表，支持旧格式迁移
        """
        self.devices = []
        device_file = self._device_file()
        if not device_file:
            return self.devices

        try:
            # 读取原始文件内容
            lines = DeviceFileManager.load_device_list(device_file)
            if not lines:
                logger = netops_logger.get_logger()
                logger.info("设备列表文件为空或不存在")
                return self.devices

            migrated_passwords = []
            migrated_devices = []

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 7:
                    logger = netops_logger.get_logger()
                    logger.warning(f"设备列表第 {line_num} 行格式不正确，跳过")
                    continue

                try:
                    device = {
                        "ip": parts[0],
                        "vendor": parts[1],
                        "device_type": parts[2],
                        "username": parts[3],
                        "password": parts[4],  # 先不解密，批量处理
                        "protocol": parts[5],
                        "enable_password": parts[6],
                        "group": parts[7] if len(parts) > 7 else "",
                        "tags": parts[8] if len(parts) > 8 else "",
                    }

                    # 验证设备数据
                    is_valid, error = DeviceValidator.validate_device_data(device, [])
                    if not is_valid and error:
                        logger = netops_logger.get_logger()
                        logger.warning(f"设备列表第 {line_num} 行验证失败: {error}，跳过")
                        continue

                    migrated_devices.append(device)
                    migrated_passwords.extend([parts[4], parts[6]])

                except Exception as e:
                    logger = netops_logger.get_logger()
                    logger.error(f"设备列表第 {line_num} 行处理失败: {e}")
                    continue

            # 批量迁移旧格式密码
            if migrated_passwords:
                migrated_passwords = migrate_old_passwords(migrated_passwords)

            # 解密密码并构建最终设备列表
            password_idx = 0
            for device in migrated_devices:
                try:
                    device["password"] = decrypt_password(migrated_passwords[password_idx])
                    device["enable_password"] = decrypt_password(migrated_passwords[password_idx + 1])
                    self.devices.append(device)
                    password_idx += 2
                except Exception as e:
                    logger = netops_logger.get_logger()
                    logger.error(f"设备密码解密失败: {e}")
                    # 解密失败时跳过此设备，避免数据丢失

            logger = netops_logger.get_logger()
            logger.info(f"成功加载 {len(self.devices)} 台设备")

        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"加载设备列表失败: {e}")

        return self.devices

    def save_devices(self, devices=None):
        """
        保存设备列表（原子操作）
        """
        if devices is not None:
            self.devices = devices

        device_file = self._device_file()
        if not device_file:
            logger = netops_logger.get_logger()
            logger.error("项目路径未设置，无法保存设备列表")
            return False

        try:
            # 验证设备数据
            valid_devices = []
            existing_ips = [d["ip"] for d in self.devices]

            for idx, device in enumerate(self.devices):
                is_valid, error = DeviceValidator.validate_device_data(device, [])
                if not is_valid:
                    logger = netops_logger.get_logger()
                    logger.warning(f"设备数据验证失败（索引 {idx}）: {error}，跳过保存")
                    continue
                valid_devices.append(device)

            # 准备文件内容
            lines = ["# 格式：IP,厂商,设备类型,用户名,密码,协议,特权密码,分组,标签\n"]
            lines.append("# 密码已加密存储（ENC:前缀），请勿手动编辑\n")

            for device in valid_devices:
                pwd = encrypt_password(device['password']) if not is_encrypted(device['password']) else device['password']
                enable = encrypt_password(device['enable_password']) if not is_encrypted(device['enable_password']) else device['enable_password']
                line = f"{device['ip']},{device['vendor']},{device['device_type']},{device['username']},{pwd},{device['protocol']},{enable},{device.get('group', '')},{device.get('tags', '')}\n"
                lines.append(line)

            # 原子写入文件
            success = DeviceFileManager.save_device_list(device_file, lines)
            if success:
                logger = netops_logger.get_logger()
                logger.info(f"成功保存 {len(valid_devices)} 台设备到 {device_file}")
                return True
            else:
                raise IOError("文件保存失败")

        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"保存设备列表失败: {e}")
            return False

    def export_txt(self, file_path, parent_widget=None):
        """
        导出设备列表为TXT格式（带安全确认）

        Args:
            file_path: 导出文件路径
            parent_widget: 父窗口组件（用于显示确认对话框）

        Returns:
            是否成功
        """
        # 安全确认
        if parent_widget and len(self.devices) > 0:
            from src.ui.security_dialogs import ExportWarningDialog
            dialog = ExportWarningDialog(parent_widget, "txt", len(self.devices))
            if dialog.exec_() != dialog.Accepted:
                logger = netops_logger.get_logger()
                logger.info("用户取消导出操作")
                return False

        try:
            with AtomicFileWriter(file_path) as temp_file:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write("# 设备清单导出\n")
                    f.write(f"# 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("# ⚠️  注意：导出文件密码为明文，请妥善保管！\n")
                    f.write(f"# 导出设备数量：{len(self.devices)} 台\n")
                    f.write("# " + ",".join(DEVICE_HEADERS) + "\n")

                    for device in self.devices:
                        pwd = decrypt_password(device['password']) if is_encrypted(device['password']) else device['password']
                        enable = decrypt_password(device['enable_password']) if is_encrypted(device['enable_password']) else device['enable_password']
                        line = f"{device['ip']},{device['vendor']},{device['device_type']},{device['username']},{pwd},{device['protocol']},{enable},{device.get('group', '')},{device.get('tags', '')}\n"
                        f.write(line)

            logger = netops_logger.get_logger()
            logger.info(f"成功导出 {len(self.devices)} 台设备到 {file_path}")
            return True

        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"导出设备列表失败: {e}")
            return False

    def export_csv(self, file_path, parent_widget=None):
        """
        导出设备列表为CSV格式（带安全确认）
        """
        # 安全确认
        if parent_widget and len(self.devices) > 0:
            from src.ui.security_dialogs import ExportWarningDialog
            dialog = ExportWarningDialog(parent_widget, "csv", len(self.devices))
            if dialog.exec_() != dialog.Accepted:
                return False

        try:
            with AtomicFileWriter(file_path) as temp_file:
                with open(temp_file, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(DEVICE_HEADERS)
                    for d in self.devices:
                        pwd = decrypt_password(d['password']) if is_encrypted(d['password']) else d['password']
                        enable = decrypt_password(d['enable_password']) if is_encrypted(d['enable_password']) else d['enable_password']
                        writer.writerow([
                            d["ip"], d["vendor"], d["device_type"], d["username"],
                            pwd, d["protocol"], enable,
                            d.get("group", ""), d.get("tags", "")
                        ])

            logger = netops_logger.get_logger()
            logger.info(f"成功导出 {len(self.devices)} 台设备到 {file_path}")
            return True

        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"导出CSV失败: {e}")
            return False

    def export_excel(self, file_path, parent_widget=None):
        """
        导出设备列表为Excel格式（带安全确认）
        """
        # 安全确认
        if parent_widget and len(self.devices) > 0:
            from src.ui.security_dialogs import ExportWarningDialog
            dialog = ExportWarningDialog(parent_widget, "xlsx", len(self.devices))
            if dialog.exec_() != dialog.Accepted:
                return False

        try:
            import pandas as pd
            data = []
            for d in self.devices:
                pwd = decrypt_password(d['password']) if is_encrypted(d['password']) else d['password']
                enable = decrypt_password(d['enable_password']) if is_encrypted(d['enable_password']) else d['enable_password']
                data.append([
                    d["ip"], d["vendor"], d["device_type"], d["username"],
                    pwd, d["protocol"], enable,
                    d.get("group", ""), d.get("tags", "")
                ])
            df = pd.DataFrame(data, columns=DEVICE_HEADERS)
            df.to_excel(file_path, index=False, engine="openpyxl")

            logger = netops_logger.get_logger()
            logger.info(f"成功导出 {len(self.devices)} 台设备到 {file_path}")
            return True

        except ImportError as e:
            logger = netops_logger.get_logger()
            logger.error(f"缺少必要依赖，无法导出Excel: {e}")
            return False
        except Exception as e:
            logger = netops_logger.get_logger()
            logger.error(f"导出Excel失败: {e}")
            return False

    def import_txt(self, file_path):
        devices = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 7:
                    devices.append({
                        "ip": parts[0], "vendor": parts[1], "device_type": parts[2],
                        "username": parts[3], "password": parts[4], "protocol": parts[5],
                        "enable_password": parts[6],
                        "group": parts[7] if len(parts) > 7 else "",
                        "tags": parts[8] if len(parts) > 8 else "",
                    })
        return devices

    def import_csv(self, file_path):
        devices = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                devices.append({
                    "ip": row.get("IP地址", row.get("ip", "")),
                    "vendor": row.get("厂商", row.get("vendor", "")),
                    "device_type": row.get("设备类型", row.get("device_type", "")),
                    "username": row.get("用户名", row.get("username", "")),
                    "password": row.get("密码", row.get("password", "")),
                    "protocol": row.get("协议", row.get("protocol", "")),
                    "enable_password": row.get("特权密码", row.get("enable_password", "")),
                    "group": row.get("分组", row.get("group", "")),
                    "tags": row.get("标签", row.get("tags", "")),
                })
        return devices

    def import_excel(self, file_path):
        try:
            import pandas as pd
            df = pd.read_excel(file_path, engine="openpyxl")
            col_map = {
                "IP地址": "ip", "ip": "ip", "IP": "ip",
                "厂商": "vendor", "vendor": "vendor",
                "设备类型": "device_type", "device_type": "device_type",
                "用户名": "username", "username": "username",
                "密码": "password", "password": "password",
                "协议": "protocol", "protocol": "protocol",
                "特权密码": "enable_password", "enable_password": "enable_password",
                "分组": "group", "group": "group",
                "标签": "tags", "tags": "tags",
            }
            df = df.rename(columns=col_map)
            devices = []
            for _, row in df.iterrows():
                devices.append({
                    "ip": str(row.get("ip", "")),
                    "vendor": str(row.get("vendor", "")),
                    "device_type": str(row.get("device_type", "")),
                    "username": str(row.get("username", "")),
                    "password": str(row.get("password", "")),
                    "protocol": str(row.get("protocol", "")),
                    "enable_password": str(row.get("enable_password", "")),
                    "group": str(row.get("group", "")),
                    "tags": str(row.get("tags", "")),
                })
            return devices
        except ImportError:
            return None

    def generate_template(self, file_path, fmt="csv"):
        template_devices = [
            {"ip": "192.168.1.1", "vendor": "锐捷", "device_type": "核心交换机",
             "username": "admin", "password": "your_password", "protocol": "ssh",
             "enable_password": "enable_pass", "group": "核心区", "tags": "核心,生产"},
            {"ip": "192.168.1.2", "vendor": "华为", "device_type": "接入交换机",
             "username": "admin", "password": "your_password", "protocol": "ssh",
             "enable_password": "enable_pass", "group": "接入层", "tags": "接入,办公"},
            {"ip": "192.168.1.254", "vendor": "H3C", "device_type": "路由器",
             "username": "admin", "password": "your_password", "protocol": "ssh",
             "enable_password": "enable_pass", "group": "出口区", "tags": "出口,边界"},
        ]

        if fmt == "csv":
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(DEVICE_HEADERS)
                for d in template_devices:
                    writer.writerow([d["ip"], d["vendor"], d["device_type"],
                                     d["username"], d["password"], d["protocol"],
                                     d["enable_password"], d["group"], d["tags"]])
        elif fmt == "txt":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# 设备清单模板\n")
                f.write("# " + ",".join(DEVICE_HEADERS) + "\n")
                for d in template_devices:
                    f.write(f"{d['ip']},{d['vendor']},{d['device_type']},{d['username']},{d['password']},{d['protocol']},{d['enable_password']},{d['group']},{d['tags']}\n")
        elif fmt == "xlsx":
            try:
                import pandas as pd
                data = [[d["ip"], d["vendor"], d["device_type"], d["username"],
                         d["password"], d["protocol"], d["enable_password"],
                         d["group"], d["tags"]] for d in template_devices]
                df = pd.DataFrame(data, columns=DEVICE_HEADERS)
                df.to_excel(file_path, index=False, engine="openpyxl")
            except ImportError:
                return False
        return True

    def record_history(self, action, details, device_count=0):
        history_file = self._history_file()
        if not history_file:
            return

        history = {"changes": []}
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        history["changes"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details,
            "device_count": device_count,
        })

        if len(history["changes"]) > 500:
            history["changes"] = history["changes"][-500:]

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def get_history(self):
        history_file = self._history_file()
        if not history_file or not os.path.exists(history_file):
            return []
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("changes", [])

    def get_device_count(self):
        return len(self.devices)

    def get_groups(self):
        groups = set()
        for d in self.devices:
            g = d.get("group", "").strip()
            if g:
                groups.add(g)
        return sorted(groups)

    def get_devices_by_group(self, group):
        return [d for d in self.devices if d.get("group", "") == group]

    def get_stats(self):
        stats = {"total": len(self.devices), "by_vendor": {}, "by_type": {}, "by_group": {}}
        for d in self.devices:
            v = d["vendor"]
            t = d["device_type"]
            g = d.get("group", "未分组")
            stats["by_vendor"][v] = stats["by_vendor"].get(v, 0) + 1
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
            stats["by_group"][g] = stats["by_group"].get(g, 0) + 1
        return stats