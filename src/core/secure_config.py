import json
import os
from typing import Dict, Any, Optional

from src.core.key_manager import KeyManager, EncryptedDataManager


class SecureConfigFile:
    _instance = None

    def __init__(self):
        self._enc = EncryptedDataManager()
        self._km = KeyManager()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save(self, filepath: str, data: Dict[str, Any]) -> bool:
        enc_path = filepath + ".enc"
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            encrypted = self._enc.encrypt(json_str)
            tmp_path = enc_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(encrypted)
            os.replace(tmp_path, enc_path)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception as e:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return False

    def load(self, filepath: str) -> Optional[Dict[str, Any]]:
        enc_path = filepath + ".enc"
        for path in [enc_path, filepath]:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                if self._enc.is_encrypted(raw):
                    decrypted = self._enc.decrypt(raw)
                    return json.loads(decrypted)
                else:
                    data = json.loads(raw)
                    if path == filepath and os.path.exists(enc_path):
                        pass
                    else:
                        self.save(filepath, data)
                    return data
            except Exception:
                continue
        return None
