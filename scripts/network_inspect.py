#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全网健康巡检脚本
支持锐捷、华为、H3C、思科设备自动化巡检
"""

import os
import socket
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

# 路径配置
BASE_PATH: str = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH: str = os.path.join(BASE_PATH, "../config/device_list.txt")
OUTPUT_ALL: str = os.path.join(BASE_PATH, "../output/all_device_full.md")
EXCEPTION_PATH: str = os.path.join(BASE_PATH, "../output/single_exception")
REPORT_PATH: str = os.path.join(BASE_PATH, "../report")

def _resolve_paths(project_dir: str):
    global CONFIG_PATH, OUTPUT_ALL, EXCEPTION_PATH, REPORT_PATH
    CONFIG_PATH = os.path.join(project_dir, "config", "device_list.txt")
    OUTPUT_ALL = os.path.join(project_dir, "output", "all_device_full.md")
    EXCEPTION_PATH = os.path.join(project_dir, "output", "single_exception")
    REPORT_PATH = os.path.join(project_dir, "report")

# 故障关键字匹配库
EXCEPTION_KEYS: List[str] = [
    "Down", "Error", "Warning", "CPU", "内存", "过载", "告警", "故障",
    "CRC", "reset", "spanning-tree", "邻居", "会话"
]

TYPE_NORMALIZE: Dict[str, str] = {
    "核心交换机": "交换机",
    "汇聚交换机": "交换机",
    "接入交换机": "交换机",
    "交换机": "交换机",
    "路由器": "路由器",
    "防火墙": "交换机",
    "AC控制器": "交换机",
    "AP": "交换机",
}

DEFAULT_INSPECT_CMDS: List[str] = ["show version", "show ip interface brief", "show cpu", "show memory"]

BASE_CMD_LIB: Dict[str, Dict[str, List[str]]] = {
    "锐捷": {
        "交换机": ["show version", "show ip interface brief", "show cpu", "show memory", "show logging"],
        "路由器": ["show version", "show ip route", "show cpu", "show memory", "show logging"]
    },
    "华为": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory", "display logbuffer"]
    },
    "H3C": {
        "交换机": ["display version", "display ip interface brief", "display cpu", "display memory", "display logbuffer"],
        "路由器": ["display version", "display ip interface brief", "display ip routing-table", "display cpu", "display memory"]
    },
    "思科": {
        "交换机": ["show version", "show ip interface brief", "show cpu usage", "show memory", "show logging"],
        "路由器": ["show version", "show ip route", "show cpu usage", "show memory", "show logging"]
    }
}

# 全厂商完整配置抓取命令
FULL_CONFIG_CMD: Dict[str, str] = {
    "锐捷": "show running-config",
    "华为": "display current-configuration",
    "H3C": "display current-configuration",
    "思科": "show running-config"
}

# Netmiko官方标准设备类型映射
DEV_TYPE_MAP: Dict[str, str] = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

def init_folder():
    os.makedirs(EXCEPTION_PATH, exist_ok=True)
    os.makedirs(REPORT_PATH, exist_ok=True)

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

def has_exception(content):
    for key in EXCEPTION_KEYS:
        if key in content:
            return True
    return False

def save_err_log(dev_info, content):
    if isinstance(dev_info, dict):
        ip = dev_info.get("ip", "")
        vendor = dev_info.get("vendor", "")
        dev_mod = dev_info.get("device_type", "")
        user = dev_info.get("username", "")
        pwd = dev_info.get("password", "")
        proto = dev_info.get("protocol", "ssh")
        secret = dev_info.get("enable_password", "")
    else:
        ip, vendor, dev_mod, user, pwd, proto, secret = dev_info
    file_name = f"{dev_mod}_{ip}_异常.txt"
    
    err_dir = EXCEPTION_PATH
    os.makedirs(err_dir, exist_ok=True)
    file_path = os.path.join(err_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"【设备厂商】：{vendor}\n")
        f.write(f"【设备类型】：{dev_mod}\n")
        f.write(f"【设备IP】：{ip}\n")
        f.write(f"【巡检时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(content)

def _get_single_report_dir():
    return os.path.join(REPORT_PATH, "single_inspect")


def device_inspect(dev_info, progress_callback=None):
    if isinstance(dev_info, dict):
        ip = dev_info.get("ip", "")
        vendor = dev_info.get("vendor", "")
        dev_mod = dev_info.get("device_type", "")
        user = dev_info.get("username", "")
        pwd = dev_info.get("password", "")
        proto = dev_info.get("protocol", "ssh")
        secret = dev_info.get("enable_password", "")
    else:
        ip, vendor, dev_mod, user, pwd, proto, secret = dev_info

    if vendor not in DEV_TYPE_MAP:
        return f"【{ip}】暂不支持该厂商适配"

    normalized_type = TYPE_NORMALIZE.get(dev_mod, "交换机")
    cmd_list = BASE_CMD_LIB.get(vendor, {}).get(normalized_type, DEFAULT_INSPECT_CMDS)

    dev_conn = {
        "device_type": DEV_TYPE_MAP[vendor],
        "host": ip,
        "username": user,
        "password": pwd,
        "secret": secret,
        "timeout": 60,
        "port": 22
    }

    inspect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(0.5 * attempt)
            with ConnectHandler(**dev_conn) as conn:
                conn.enable()
                res = ""
                for cmd in cmd_list:
                    res += f"\n===== {cmd} =====\n"
                    try:
                        output = conn.send_command(cmd)
                        res += output if output.strip() else "(无输出)"
                    except Exception:
                        res += "(命令执行失败)"

                err_flag = has_exception(res)
                if err_flag and vendor in FULL_CONFIG_CMD:
                    try:
                        res += f"\n\n===== 故障设备抓取完整运行配置 =====\n"
                        res += conn.send_command(FULL_CONFIG_CMD[vendor])
                    except Exception:
                        res += "(配置抓取失败)"

            status_line = "\u26a0\ufe0f 发现异常" if err_flag else "\u2705 巡检正常"

            full_report = f"""===== 设备巡检报告 =====
【设备IP】：{ip}
【厂商】：{vendor}
【设备类型】：{dev_mod}
【巡检时间】：{inspect_time}
【执行命令数】：{len(cmd_list)}
{res}

===== 巡检状态 =====
{status_line}
"""

            if err_flag:
                save_err_log(dev_info, full_report)

            _save_single_report(ip, vendor, dev_mod, inspect_time, full_report)

            if attempt > 1:
                return f"【{ip}】第{attempt}次重试后巡检成功\n{full_report}"
            return full_report

        except NetmikoAuthenticationException:
            return f"【{ip}】巡检失败：账号密码认证错误"
        except (NetmikoTimeoutException, socket.timeout) as e:
            last_error = e
            if attempt < max_retries:
                continue
            return f"【{ip}】巡检失败：设备连接超时/不可达（已重试{max_retries}次）"
        except socket.gaierror:
            return f"【{ip}】巡检失败：DNS解析异常"
        except ConnectionRefusedError:
            return f"【{ip}】巡检失败：SSH端口未开放或被拒绝"
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                continue
            return f"【{ip}】巡检失败：{str(e)}"

    return f"【{ip}】巡检失败：{str(last_error)}"


def _save_single_report(ip, vendor, dev_mod, inspect_time, content):
    try:
        report_dir = _get_single_report_dir()
        os.makedirs(report_dir, exist_ok=True)
        safe_ip = ip.replace(".", "_")
        file_name = f"{safe_ip}_{inspect_time.replace(':', '').replace(' ', '_')}_巡检报告.txt"
        file_path = os.path.join(report_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass

def run_inspect(project_dir: str, progress_callback=None) -> List[str]:
    _resolve_paths(project_dir)
    init_folder()
    dev_list = load_device_list()
    if not dev_list:
        return ["未读取到设备清单"]
    total = len(dev_list)
    results: List[str] = []
    all_content = [f"# 全网设备巡检总报告\n巡检时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    for idx, dev in enumerate(dev_list):
        if progress_callback:
            progress_callback(idx + 1, total, f"正在巡检 {dev[0]} ...")
        result = device_inspect(dev, progress_callback)
        results.append(result)
        all_content.append(result)
    os.makedirs(os.path.dirname(OUTPUT_ALL), exist_ok=True)
    with open(OUTPUT_ALL, "w", encoding="utf-8") as f:
        f.write("\n".join(all_content))
    if progress_callback:
        progress_callback(total, total, "全网巡检完成")
    return results


def main():
    init_folder()
    dev_list = load_device_list()
    if not dev_list:
        print("未读取到设备清单，请检查config/device_list.txt")
        return
    all_content = [f"# 全网设备巡检总报告\n巡检时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    print("===== 开始全网日常自动化巡检 =====")
    for dev in dev_list:
        print(device_inspect(dev))
    with open(OUTPUT_ALL, "w", encoding="utf-8") as f:
        f.write("\n".join(all_content))
    print("===== 日常巡检全部执行完成 =====")
    print(f"全网巡检汇总报告：{OUTPUT_ALL}")
    print(f"故障设备日志目录：{EXCEPTION_PATH}")

if __name__ == "__main__":
    main()