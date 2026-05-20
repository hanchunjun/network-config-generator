import os
import json
import base64
import uuid
import socket
import subprocess
import platform
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from src.utils.resource_path import get_config_path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature


class KeyManager:
    CURRENT_VERSION = "v2"
    KEY_FILE = Path(get_config_path("config/key_info.json"))
    MACHINE_ID_FILE = Path(get_config_path("config/machine_id.json"))

    def __init__(self):
        self._key_cache: Optional[bytes] = None
        self._key_version: str = self.CURRENT_VERSION
        self._lock = threading.Lock()

    def derive_key(self) -> bytes:
        """派生加密密钥（带版本控制和缓存）"""
        with self._lock:
            if self._key_cache:
                return self._key_cache

            key_info = self._load_or_create_key_info()
            key = self._derive_key_with_version(key_info)
            self._key_cache = key
            return key

    def _load_or_create_key_info(self) -> Dict[str, Any]:
        """加载或创建密钥信息"""
        self.KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

        if self.KEY_FILE.exists():
            try:
                with open(self.KEY_FILE, 'r', encoding='utf-8') as f:
                    key_info = json.load(f)

                # 验证密钥信息完整性
                if not self._validate_key_info(key_info):
                    raise ValueError("密钥信息不完整或无效")

                # 检查是否需要升级
                if key_info.get("version") != self.CURRENT_VERSION:
                    key_info = self._upgrade_key_info(key_info)

                return key_info
            except Exception as e:
                # 密钥文件损坏，重新生成
                print(f"加载密钥信息失败，重新生成: {e}")
                return self._create_new_key_info()

        # 创建新的密钥信息
        return self._create_new_key_info()

    def _validate_key_info(self, key_info: Dict[str, Any]) -> bool:
        """验证密钥信息完整性"""
        required_fields = ["version", "salt"]
        for field in required_fields:
            if field not in key_info:
                return False

        # 验证salt格式
        try:
            salt = key_info["salt"]
            base64.b64decode(salt.encode('ascii'))
        except Exception:
            return False

        return True

    def _create_new_key_info(self) -> Dict[str, Any]:
        """创建新的密钥信息"""
        machine_id = self._get_machine_id()

        key_info = {
            "version": self.CURRENT_VERSION,
            "salt": base64.b64encode(os.urandom(32)).decode('ascii'),
            "machine_id": machine_id,
            "created_at": datetime.now().isoformat(),
            "backup_key": base64.b64encode(os.urandom(32)).decode('ascii')
        }

        # 保存机器ID信息
        self._save_machine_id_info(machine_id)

        # 保存密钥信息
        with open(self.KEY_FILE, 'w', encoding='utf-8') as f:
            json.dump(key_info, f, indent=2)

        return key_info

    def _upgrade_key_info(self, old_key_info: Dict[str, Any]) -> Dict[str, Any]:
        """升级密钥信息到当前版本"""
        print(f"升级密钥信息从 {old_key_info.get('version')} 到 {self.CURRENT_VERSION}")

        new_key_info = {
            "version": self.CURRENT_VERSION,
            "salt": old_key_info.get("salt", base64.b64encode(os.urandom(32)).decode('ascii')),
            "machine_id": self._get_machine_id(),
            "created_at": old_key_info.get("created_at", datetime.now().isoformat()),
            "backup_key": old_key_info.get("backup_key", base64.b64encode(os.urandom(32)).decode('ascii')),
            "upgraded_from": old_key_info.get("version")
        }

        # 保存升级后的密钥信息
        with open(self.KEY_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_key_info, f, indent=2)

        return new_key_info

    def _save_machine_id_info(self, machine_id: str):
        """保存机器ID信息"""
        machine_info = {
            "machine_id": machine_id,
            "platform": platform.system(),
            "hostname": socket.gethostname(),
            "created_at": datetime.now().isoformat()
        }

        with open(self.MACHINE_ID_FILE, 'w', encoding='utf-8') as f:
            json.dump(machine_info, f, indent=2)

    def _derive_key_with_version(self, key_info: Dict[str, Any]) -> bytes:
        """根据版本派生密钥"""
        version = key_info.get("version", "v1")

        if version == "v1":
            return self._derive_v1(key_info)
        else:
            return self._derive_v2(key_info)

    def _derive_v2(self, key_info: Dict[str, Any]) -> bytes:
        """V2版本密钥派生"""
        machine_id = self._get_machine_id().encode("utf-8")
        salt = base64.b64decode(key_info["salt"].encode('ascii'))
        backup_key = key_info.get("backup_key", "").encode('ascii')

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,
        )
        return kdf.derive(machine_id + backup_key)

    def _derive_v1(self, key_info: Dict[str, Any]) -> bytes:
        """V1版本兼容（原实现）"""
        machine_id = self._get_machine_id().encode("utf-8")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"NetworkConfigGenerator::AES::Salt::2024",  # 原硬编码盐值
            iterations=600000,
        )
        return kdf.derive(machine_id)

    def get_key_version(self) -> str:
        """获取当前密钥版本"""
        return self._key_version

    def _get_machine_id(self) -> str:
        """获取机器唯一标识"""
        parts = []

        try:
            parts.append(socket.gethostname())
        except Exception:
            parts.append("unknown-host")

        try:
            if platform.system().lower() == "win32":
                result = subprocess.run(
                    ["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Cryptography",
                     "/v", "MachineGuid"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.splitlines():
                    if "MachineGuid" in line:
                        guid = line.strip().split()[-1]
                        parts.append(guid)
                        break
        except Exception:
            pass

        if len(parts) == 1:
            try:
                parts.append(str(uuid.getnode()))
            except Exception:
                parts.append("fallback-id")

        return "|".join(parts)


class EncryptedDataManager:
    """加密数据管理器，支持多版本解密"""

    def __init__(self):
        self.key_manager = KeyManager()

    def encrypt(self, plaintext: str) -> str:
        """加密数据"""
        if not plaintext:
            return plaintext

        key = self.key_manager.derive_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        encrypted = base64.b64encode(nonce + ciphertext).decode("ascii")

        version = self.key_manager.get_key_version()
        return f"ENC:{version}:{encrypted}"

    def decrypt(self, stored: str) -> str:
        """解密数据（支持多版本）"""
        if not stored or not stored.startswith("ENC:"):
            return stored

        parts = stored.split(":", 2)
        if len(parts) < 3:
            return stored  # 旧格式，使用原逻辑

        version = parts[1]
        encrypted_data = parts[2]

        return self.decrypt_with_version(encrypted_data, version)

    def decrypt_with_version(self, encrypted_data: str, version: str) -> str:
        """根据版本解密数据"""
        try:
            key = self.key_manager.derive_key()
            aesgcm = AESGCM(key)
            raw = base64.b64decode(encrypted_data)
            nonce = raw[:12]
            ciphertext = raw[12:]
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception:
            # 解密失败，尝试使用原V1逻辑
            if version != "v1":
                return self._decrypt_v1_fallback(encrypted_data)
            return encrypted_data

    def _decrypt_v1_fallback(self, encrypted_data: str) -> str:
        """V1版本解密回退"""
        try:
            key = self.key_manager._derive_v1({})
            aesgcm = AESGCM(key)
            raw = base64.b64decode(encrypted_data)
            nonce = raw[:12]
            ciphertext = raw[12:]
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception:
            return encrypted_data

    def is_encrypted(self, stored: str) -> bool:
        """检查数据是否已加密"""
        if not stored:
            return False
        return stored.startswith("ENC:")

    def migrate_old_data(self, old_encrypted_data: str) -> str:
        """迁移旧加密数据到新格式"""
        if not old_encrypted_data.startswith("ENC:"):
            return old_encrypted_data

        # 检查是否是旧格式（没有版本号）
        parts = old_encrypted_data.split(":")
        if len(parts) == 2:  # 旧格式: ENC:encrypted_data
            encrypted_data = parts[1]
            try:
                # 尝试用V1解密
                plaintext = self._decrypt_v1_fallback(encrypted_data)
                if plaintext != encrypted_data:
                    # 用新格式重新加密
                    return self.encrypt(plaintext)
            except Exception:
                pass

        return old_encrypted_data


# 全局实例
encrypted_manager = EncryptedDataManager()


from datetime import datetime