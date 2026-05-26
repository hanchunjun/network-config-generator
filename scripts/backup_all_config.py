#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量配置备份脚本
支持锐捷、华为、H3C、思科设备配置备份
"""

import ipaddress
import os
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

# 路径配置
BASE_PATH: str = os.path.dirname(os.path.abspath(__file__))
BACKUP_PATH: str = os.path.join(BASE_PATH, "../config_backup")

def _resolve_paths(project_dir: str):
    global CONFIG_PATH, BACKUP_PATH
    CONFIG_PATH = os.path.join(project_dir, "config", "device_list.txt")
    BACKUP_PATH = os.path.join(project_dir, "config_backup")

# 全厂商配置备份命令库
FULL_CONFIG_CMD: Dict[str, str] = {
    "锐捷": "show running-config",
    "华为": "display current-configuration",
    "H3C": "display current-configuration",
    "思科": "show running-config"
}

# 官方标准设备类型映射
DEV_TYPE_MAP: Dict[str, str] = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

# 安全配置
SSH_TIMEOUT: int = 60
MAX_RETRIES: int = 3
SAFE_SSH_CONFIG: Dict[str, Any] = {
    "timeout": SSH_TIMEOUT,
}

def _get_ssh_port() -> int:
    """获取 SSH 端口，支持 NETOPS_SSH_PORT 环境变量，无效值回退 22。"""
    raw = os.environ.get('NETOPS_SSH_PORT', '22')
    try:
        port = int(raw)
        if 1 <= port <= 65535:
            return port
    except (ValueError, TypeError):
        pass
    return 22


def init_folder():
    os.makedirs(BACKUP_PATH, exist_ok=True)

def load_device_list():
    dev_list = []
    if not os.path.exists(CONFIG_PATH):
        return dev_list
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            # ===================== 【修改1】6 → 7 =====================
            if len(parts) == 7:
                dev_list.append(parts)
    return dev_list

def _is_valid_ip(ip: str) -> bool:
    """验证IP地址格式

    Args:
        ip: IP地址字符串

    Returns:
        是否有效
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def _is_safe_path(base_path: str, target_path: str) -> bool:
    """验证路径安全性，防止路径遍历

    Args:
        base_path: 基础路径
        target_path: 目标路径

    Returns:
        是否安全
    """
    base_abs = os.path.abspath(base_path)
    target_abs = os.path.abspath(target_path)
    return target_abs.startswith(base_abs)


def backup_one_device(dev_info: List[str]) -> str:
    """备份单个设备配置

    Args:
        dev_info: 设备信息列表 [IP, 厂商, 设备类型, 用户名, 密码, 协议, 特权密码]

    Returns:
        备份结果信息
    """
    # ===================== 【修改2】新增 secret 参数 =====================
    ip, vendor, dev_mod, user, pwd, proto, secret = dev_info

    # 验证IP地址
    if not _is_valid_ip(ip):
        return f"【{ip}】无效的IP地址格式"

    # 验证厂商支持
    if vendor not in DEV_TYPE_MAP or vendor not in FULL_CONFIG_CMD:
        return f"【{ip}】不支持该厂商配置备份"

    # 构建安全的SSH连接配置
    dev_conn = {
        "device_type": DEV_TYPE_MAP[vendor],
        "host": ip,
        "username": user,
        "password": pwd,
        # ===================== 【修改3】新增特权密码 =====================
        "secret": secret,
        "port": _get_ssh_port(),  # 支持自定义端口（NETOPS_SSH_PORT 环境变量）
        **SAFE_SSH_CONFIG,  # 应用安全配置
    }

    max_retries = MAX_RETRIES
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(0.5 * attempt)
            with ConnectHandler(**dev_conn) as conn:
                try:
                    conn.enable()
                except Exception:
                    pass
                config = conn.send_command(FULL_CONFIG_CMD[vendor])

            if not config or len(config) < 100:
                return f"【{ip}】配置获取失败，配置过短"

            safe_dev_mod = "".join(c for c in dev_mod if c.isalnum() or c in '._-')
            file_name = f"{safe_dev_mod}_{ip}_配置备份.txt"
            file_path = os.path.join(BACKUP_PATH, file_name)

            os.makedirs(BACKUP_PATH, exist_ok=True)

            if not _is_safe_path(BACKUP_PATH, file_path):
                return f"【{ip}】备份路径不安全，拒绝操作"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"【设备厂商】：{vendor}\n")
                f.write(f"【设备类型】：{dev_mod}\n")
                f.write(f"【设备IP】：{ip}\n")
                f.write(f"配置备份时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(config)

            if attempt > 1:
                return f"【{ip}】第{attempt}次重试后配置备份成功"
            return f"【{ip}】配置备份成功"

        except NetmikoAuthenticationException:
            _log_error(f"认证失败: {ip}")
            return f"【{ip}】认证失败，请检查凭据"
        except (NetmikoTimeoutException, socket.timeout) as e:
            last_error = e
            _log_error(f"连接超时(第{attempt}次): {ip}")
            if attempt < max_retries:
                continue
            return f"【{ip}】连接超时（已重试{max_retries}次），请检查网络"
        except socket.gaierror:
            _log_error(f"DNS解析失败: {ip}")
            return f"【{ip}】DNS解析失败，请检查网络"
        except ConnectionRefusedError:
            _log_error(f"SSH端口拒绝: {ip}")
            return f"【{ip}】SSH端口拒绝连接，请检查端口和防火墙"
        except Exception as e:
            last_error = e
            _log_error(f"备份失败(第{attempt}次) {ip}: {str(e)}")
            if attempt < max_retries:
                continue
            return f"【{ip}】备份失败：{str(e)}"

    return f"【{ip}】备份失败：{str(last_error)}"


def _log_error(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if getattr(sys, 'frozen', False):
        log_dir = os.path.join(os.path.dirname(sys.executable), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "backup_error.log")
    else:
        log_file = os.path.join(BASE_PATH, "backup_error.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # 日志写入失败不影响主流程

def run_backup(project_dir: str, progress_callback=None, max_workers: int = 5) -> List[str]:
    """批量备份（并发模式）。

    Args:
        project_dir: 项目目录路径
        progress_callback: 进度回调函数 (completed, total, message)
        max_workers: 最大并发线程数（默认 5，单台设备不影响）
    """
    _resolve_paths(project_dir)
    init_folder()
    dev_list = load_device_list()
    if not dev_list:
        return ["未读取到项目设备清单"]

    total = len(dev_list)
    if total <= 1 or max_workers <= 1:
        # 单设备或显式指定单线程时，保持串行行为
        results: List[str] = []
        for idx, dev in enumerate(dev_list):
            if progress_callback:
                progress_callback(idx + 1, total, f"正在备份 {dev[0]} ...")
            results.append(backup_one_device(dev))
        if progress_callback:
            progress_callback(total, total, "全网配置备份完成")
        return results

    # 多设备并发备份
    results: List[str] = [""] * total  # 预分配，保持顺序
    completed = 0
    with ThreadPoolExecutor(max_workers=min(max_workers, total)) as executor:
        future_to_idx = {
            executor.submit(backup_one_device, dev): idx
            for idx, dev in enumerate(dev_list)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                dev_ip = dev_list[idx][0] if idx < len(dev_list) else "未知"
                results[idx] = f"【{dev_ip}】备份异常: {e}"
            completed += 1
            if progress_callback:
                progress_callback(completed, total, f"已完成 {dev_list[idx][0]}")

    if progress_callback:
        progress_callback(total, total, "全网配置备份完成")
    return results


def main():
    init_folder()
    dev_list = load_device_list()
    if not dev_list:
        print("未读取到项目设备清单")
        return
    print("===== 开始全网设备基线配置备份 =====")
    for dev in dev_list:
        print(backup_one_device(dev))
    print("===== 全网配置备份全部完成 =====")
    print(f"配置备份文件存放目录：{BACKUP_PATH}")

if __name__ == "__main__":
    main()