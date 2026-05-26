#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活核心引擎 — 软件授权激活体系核心模块

职责：
1. 机器码生成（CPU序列号 + 硬盘物理序列号 → MD5 → 32位大写）
2. 激活码生成与校验（机器码 + 内置私钥 → 16位大写）
3. 授权文件加密存储与读取（AES-GCM）
4. 启动激活状态校验
5. 方案B：180天黑名单静默校验

三套方案共用此模块，管理员制码工具复用 generate_activation_code() 算法。
"""

import hashlib
import json
import os
import platform
import socket
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.core.logger import netops_logger
from src.utils.resource_path import get_activation_dir

# ─── 内置私钥（用户端与管理员制码工具必须完全一致）───
_ACTIVATION_SECRET_KEY: str = "NetOps::Activation::SecretKey::2026"

# ─── 激活文件路径（activation/ 独立目录）───
_ACTIVATION_DIR: str = get_activation_dir()
LICENSE_FILE: str = os.path.join(_ACTIVATION_DIR, "license.dat")
BLACKLIST_CHECK_FILE: str = os.path.join(_ACTIVATION_DIR, "bl_check.dat")

# ─── 方案B：黑名单URL（静态TXT，每行一个机器码）───
BLACKLIST_URL: str = "https://raw.githubusercontent.com/hanchunjun/network-config-generator/main/blacklist.txt"

# ─── 校验周期（秒）───
CHECK_INTERVAL_SECONDS: int = 180 * 24 * 3600  # 180天


def _get_cpu_serial() -> str:
    """获取CPU序列号（Windows优先使用wmic，Linux使用dmidecode）"""
    system = platform.system().lower()
    try:
        if system == "win32":
            result = subprocess.run(
                ["wmic", "cpu", "get", "ProcessorId"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line and line.lower() != "processorid":
                    return line
        elif system == "linux":
            result = subprocess.run(
                ["sudo", "dmidecode", "-t", "processor"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                if "ID:" in line:
                    return line.split("ID:")[-1].strip()
    except Exception:
        pass
    return ""


def _get_disk_serial() -> str:
    """获取硬盘物理序列号（Windows使用wmic，Linux使用lsblk/hdparm）"""
    system = platform.system().lower()
    try:
        if system == "win32":
            result = subprocess.run(
                ["wmic", "diskdrive", "get", "SerialNumber"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line and line.lower() != "serialnumber":
                    return line
        elif system == "linux":
            result = subprocess.run(
                ["lsblk", "-ndo", "SERIAL", "/dev/sda"],
                capture_output=True, text=True, timeout=10
            )
            serial = result.stdout.strip()
            if serial:
                return serial
    except Exception:
        pass
    return ""


def _get_fallback_id() -> str:
    """降级方案：使用主机名 + MAC地址生成唯一标识"""
    parts = []
    try:
        parts.append(socket.gethostname())
    except Exception:
        parts.append("unknown-host")
    try:
        mac = hex(uuid_getnode())
        parts.append(mac)
    except Exception:
        parts.append("no-mac")
    return "|".join(parts)


def get_machine_code() -> str:
    """生成设备唯一机器码。

    采集 CPU序列号 + 硬盘物理序列号，MD5加密后输出32位大写。
    硬件采集失败时降级使用主机名+MAC地址。

    Returns:
        str: 32位大写MD5机器码

    硬件绑定特性：
        - 重装系统、修改系统设置、更新驱动 → 不改变机器码
        - 更换CPU / 硬盘 → 变更机器码，原激活失效
    """
    cpu = _get_cpu_serial()
    disk = _get_disk_serial()

    if not cpu and not disk:
        # 降级方案
        fallback = _get_fallback_id()
        netops_logger.get_logger().warning(
            f"硬件序列号采集失败，使用降级方案生成机器码"
        )
        raw = fallback
    else:
        raw = f"{cpu}|{disk}"

    machine_code: str = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()
    return machine_code


def generate_activation_code(machine_code: str) -> str:
    """根据机器码生成激活码。

    算法：MD5(machine_code + 内置私钥) → 取前16位大写

    Args:
        machine_code: 32位大写机器码

    Returns:
        str: 16位大写激活码

    注意：此函数必须与管理员制码工具中的算法完全一致。
    """
    combined: str = f"{machine_code}{_ACTIVATION_SECRET_KEY}"
    code: str = hashlib.md5(combined.encode("utf-8")).hexdigest()[:16].upper()
    return code


# 有效期编码表：索引 → validity_days
_VALIDITY_TABLE = [
    0,      # 0: 永久
    1825,   # 1: 5年
    3650,   # 2: 10年
    1095,   # 3: 3年
    730,    # 4: 2年
    365,    # 5: 1年
    180,    # 6: 半年
    90,     # 7: 季度
    30,     # 8: 月度
    7,      # 9: 周度
]

# 反向查找：validity_days → 索引（找最接近的匹配）
_VALIDITY_TO_INDEX = {v: i for i, v in enumerate(_VALIDITY_TABLE)}


def encode_activation_code(code: str, validity_days: int) -> str:
    """将有效期索引编码到激活码末尾，生成18位激活码。

    格式：16位激活码 + 2位hex有效期索引（大写）

    Args:
        code: 16位激活码
        validity_days: 有效期天数

    Returns:
        str: 18位激活码（含有效期编码）
    """
    idx = _VALIDITY_TO_INDEX.get(validity_days, 0)
    return f"{code}{idx:02X}"


def decode_activation_code(full_code: str) -> Tuple[str, int]:
    """从18位激活码中解析出16位激活码和有效期天数。

    兼容16位旧格式（无有效期编码，返回永久）。

    Args:
        full_code: 用户输入的激活码（16位或18位）

    Returns:
        Tuple[str, int]: (16位激活码, 有效期天数，0=永久)
    """
    code = full_code.strip().upper()
    if len(code) == 18:
        base_code = code[:16]
        try:
            idx = int(code[16:18], 16)
            validity_days = _VALIDITY_TABLE[idx] if 0 <= idx < len(_VALIDITY_TABLE) else 0
        except (ValueError, IndexError):
            validity_days = 0
        return base_code, validity_days
    # 16位旧格式，视为永久
    return code, 0


def verify_activation_code(activation_code: str, machine_code: str) -> bool:
    """校验激活码是否匹配指定机器码。

    支持16位（旧格式）和18位（含有效期编码）两种格式。

    Args:
        activation_code: 用户输入的激活码
        machine_code: 本机机器码

    Returns:
        bool: 是否匹配
    """
    base_code, _validity_days = decode_activation_code(activation_code)
    expected = generate_activation_code(machine_code)
    return base_code == expected


def _derive_license_key(machine_code: str) -> bytes:
    """从机器码派生AES-GCM加密密钥。

    Args:
        machine_code: 本机机器码

    Returns:
        bytes: 32字节AES密钥
    """
    return hashlib.sha256(
        f"{machine_code}{_ACTIVATION_SECRET_KEY}".encode("utf-8")
    ).digest()


def save_license(machine_code: str, activation_code: str,
                license_path: Optional[str] = None,
                validity_days: int = 0) -> bool:
    """加密存储授权信息。

    使用AES-GCM加密，密钥由机器码+私钥派生。

    Args:
        machine_code: 本机机器码
        activation_code: 激活码
        license_path: 授权文件路径，默认使用全局 LICENSE_FILE
        validity_days: 有效期天数，0=永久，180=半年，365=1年，以此类推

    Returns:
        bool: 保存是否成功
    """
    path = license_path or LICENSE_FILE
    try:
        now = datetime.now()
        expire_at = ""
        if validity_days > 0:
            expire_at = (now + timedelta(days=validity_days)).strftime("%Y-%m-%d")

        license_data = {
            "machine_code": machine_code,
            "activation_code": activation_code,
            "activated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "validity_days": validity_days,
            "expire_at": expire_at,
            "version": "v3.1",
        }
        plaintext = json.dumps(license_data, ensure_ascii=False).encode("utf-8")

        key = _derive_license_key(machine_code)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        tmp_file = f"{path}.tmp"
        with open(tmp_file, "wb") as f:
            f.write(nonce + ciphertext)
        os.replace(tmp_file, path)

        netops_logger.get_logger().info("授权文件保存成功")
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"授权文件保存失败: {e}")
        return False


def load_license(license_path: Optional[str] = None) -> Optional[dict]:
    """读取并解密授权文件。

    Args:
        license_path: 授权文件路径，默认使用全局 LICENSE_FILE

    Returns:
        dict: 授权信息字典，失败返回None
    """
    path = license_path or LICENSE_FILE
    try:
        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            raw = f.read()

        if len(raw) < 13:
            return None

        machine_code = get_machine_code()
        key = _derive_license_key(machine_code)
        aesgcm = AESGCM(key)
        nonce = raw[:12]
        ciphertext = raw[12:]

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            license_data: dict[str, Any] = json.loads(plaintext.decode("utf-8"))
            return license_data
        except Exception:
            netops_logger.get_logger().error("授权文件解密失败，可能已被篡改")
            return None

    except Exception as e:
        netops_logger.get_logger().error(f"读取授权文件失败: {e}")
        return None


def check_activation(license_path: Optional[str] = None,
                     machine_code: Optional[str] = None) -> Tuple[bool, str, dict]:
    """启动时激活状态校验。

    校验逻辑：
    1. 读取授权文件
    2. 解密验证完整性
    3. 比对机器码一致性
    4. 计算剩余有效期

    Args:
        license_path: 授权文件路径，默认使用全局 LICENSE_FILE
        machine_code: 预计算的机器码（避免重复调用 WMIC），为 None 时自动采集

    Returns:
        Tuple[bool, str, dict]: (是否已激活, 状态描述, 详细信息)
            详细信息字典包含：
            - activated_at: 激活时间
            - validity_days: 有效期天数（0=永久）
            - expire_at: 到期时间（永久为空字符串）
            - days_remaining: 剩余天数（永久为-1，已过期为0）
            - is_permanent: 是否永久
    """
    license_data = load_license(license_path=license_path)
    if license_data is None:
        return False, "未激活", {}

    current_code = machine_code if machine_code else get_machine_code()
    saved_code = license_data.get("machine_code", "")

    if current_code != saved_code:
        netops_logger.get_logger().warning(
            f"机器码不匹配: 当前={current_code}, 授权={saved_code}"
        )
        return False, "授权失效", {}

    # 计算剩余天数
    validity_days = license_data.get("validity_days", 0)
    expire_at_str = license_data.get("expire_at", "")
    activated_at = license_data.get("activated_at", "")

    days_remaining = -1  # 永久为-1
    is_permanent = validity_days == 0

    if not is_permanent and expire_at_str:
        expire_dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                expire_dt = datetime.strptime(expire_at_str.strip(), fmt)
                break
            except ValueError:
                continue
        if expire_dt is None:
            # 最后尝试截取前10字符按日期解析
            try:
                expire_dt = datetime.strptime(expire_at_str.strip()[:10], "%Y-%m-%d")
            except Exception:
                pass
        if expire_dt is not None:
            delta = expire_dt - datetime.now()
            days_remaining = max(0, delta.days)
            if days_remaining == 0:
                return False, "授权已过期", {
                    "activated_at": activated_at,
                    "validity_days": validity_days,
                    "expire_at": expire_at_str,
                    "days_remaining": 0,
                    "is_permanent": False,
                }

    info = {
        "activated_at": activated_at,
        "validity_days": validity_days,
        "expire_at": expire_at_str,
        "days_remaining": days_remaining,
        "is_permanent": is_permanent,
    }
    return True, "已激活", info


# ─── 方案B：180天黑名单校验 ───

def get_last_check_time() -> Optional[float]:
    """获取上次联网校验时间戳。

    Returns:
        float: Unix时间戳，无记录返回None
    """
    try:
        if not os.path.exists(BLACKLIST_CHECK_FILE):
            return None
        with open(BLACKLIST_CHECK_FILE, "r") as f:
            data: dict[str, Any] = json.load(f)
        return data.get("last_check")
    except Exception:
        return None


def set_last_check_time(timestamp: Optional[float] = None) -> bool:
    """记录本次联网校验时间。

    Args:
        timestamp: Unix时间戳，默认当前时间

    Returns:
        bool: 写入是否成功
    """
    try:
        ts = timestamp if timestamp else time.time()
        Path(BLACKLIST_CHECK_FILE).parent.mkdir(parents=True, exist_ok=True)
        tmp_file = f"{BLACKLIST_CHECK_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump({"last_check": ts}, f)
        os.replace(tmp_file, BLACKLIST_CHECK_FILE)
        return True
    except Exception as e:
        netops_logger.get_logger().error(f"写入校验时间失败: {e}")
        return False


def is_due_for_check() -> bool:
    """判断是否到达180天校验周期。

    Returns:
        bool: 是否需要联网校验
    """
    last = get_last_check_time()
    if last is None:
        return True  # 从未校验过，立即校验
    elapsed = time.time() - last
    return elapsed >= CHECK_INTERVAL_SECONDS


def check_blacklist(url: str = BLACKLIST_URL) -> Tuple[bool, str]:
    """联网校验云端黑名单。

    拉取远程TXT黑名单，逐行比对机器码。
    联网失败直接跳过，不判失效。

    Args:
        url: 黑名单TXT文件URL

    Returns:
        Tuple[bool, str]: (是否在黑名单中, 描述信息)
            - (False, "校验通过") — 不在黑名单
            - (False, "联网失败，跳过校验") — 网络异常
            - (True, "设备已被封禁") — 在黑名单中
    """
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "NetOps/3.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
    except Exception as e:
        netops_logger.get_logger().warning(f"黑名单联网校验失败，跳过: {e}")
        return False, "联网失败，跳过校验"

    machine_code = get_machine_code()
    for line in content.splitlines():
        if line.strip().upper() == machine_code:
            netops_logger.get_logger().warning(f"本机机器码在黑名单中，授权失效")
            return True, "设备已被封禁"

    return False, "校验通过"


def perform_silent_check(url: str = BLACKLIST_URL) -> Tuple[bool, str]:
    """执行方案B静默校验（满180天时触发）。

    无界面、无弹窗、不打扰用户。
    联网失败直接跳过，不判失效。

    Args:
        url: 黑名单URL

    Returns:
        Tuple[bool, str]: (授权是否有效, 描述)
    """
    if not is_due_for_check():
        return True, "未到校验周期"

    in_blacklist, msg = check_blacklist(url)
    set_last_check_time()  # 无论成功失败都刷新时间

    if in_blacklist:
        return False, "授权已失效"

    return True, msg


# ─── 兼容导入 ───
# uuid.getnode() 用于降级方案
from uuid import getnode as uuid_getnode  # noqa: E402
