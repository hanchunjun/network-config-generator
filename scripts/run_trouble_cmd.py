#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障二次核查脚本
支持对异常设备进行安全指令检查和风险指令识别
"""

import os
import re
import socket
from datetime import datetime
from typing import List, Dict, Any, Tuple

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

# 路径配置
BASE_PATH: str = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH: str = os.path.join(BASE_PATH, "../config/device_list.txt")
EXCEPTION_PATH: str = os.path.join(BASE_PATH, "../output/single_exception")
REPORT_PATH: str = os.path.join(BASE_PATH, "../report")
CHECK_RESULT_PATH: str = os.path.join(BASE_PATH, "../output/trouble_check_result")
MANUAL_TASK_FILE: str = os.path.join(BASE_PATH, "../output/manual_high_risk_task.txt")

def _resolve_paths(project_dir: str):
    global CONFIG_PATH, EXCEPTION_PATH, REPORT_PATH, CHECK_RESULT_PATH, MANUAL_TASK_FILE
    CONFIG_PATH = os.path.join(project_dir, "config", "device_list.txt")
    EXCEPTION_PATH = os.path.join(project_dir, "output", "single_exception")
    REPORT_PATH = os.path.join(project_dir, "report")
    CHECK_RESULT_PATH = os.path.join(project_dir, "output", "trouble_check_result")
    MANUAL_TASK_FILE = os.path.join(project_dir, "output", "manual_high_risk_task.txt")

# 全厂商设备类型映射
DEV_TYPE_MAP: Dict[str, str] = {
    "锐捷": "ruijie_os",
    "华为": "huawei_vrp",
    "H3C": "h3c_comware",
    "思科": "cisco_ios"
}

# 安全只读指令（自动执行）
ALLOW_CMD_KEYS: List[str] = [
    "show ", "display ", "ping ", "traceroute "
]

# 高危配置指令（禁止自动执行）
DANGER_CMD_KEYS: List[str] = [
    "interface", "shutdown", "no shutdown",
    "ip route", "ospf", "bgp", "acl", "policy",
    "undo ", "save ", "reboot", "reset", "static"
]

def init_folder():
    os.makedirs(CHECK_RESULT_PATH, exist_ok=True)

def load_device_ip_dict():
    ip_dict = {}
    if not os.path.exists(CONFIG_PATH):
        return ip_dict
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            # ===================== 【修改1】6 → 7 适配7字段 =====================
            if len(parts) == 7:
                # ===================== 【修改2】新增 secret 变量 =====================
                ip, vendor, dev_mod, user, pwd, proto, secret = parts
                ip_dict[ip] = {
                    "vendor": vendor,
                    "user": user,
                    "pwd": pwd,
                    # ===================== 【修改3】存储特权密码 =====================
                    "secret": secret
                }
    return ip_dict

def get_fault_ip_list():
    fault_ips = []
    if not os.path.exists(EXCEPTION_PATH):
        return fault_ips
    pat = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
    for fname in os.listdir(EXCEPTION_PATH):
        res = pat.search(fname)
        if res:
            fault_ips.append(res.group(1))
    return list(set(fault_ips))

def extract_command_from_report(text):
    block_pat = r"```(.*?)```"
    blocks = re.findall(block_pat, text, re.S)
    cmd_list = []
    for b in blocks:
        for line in b.splitlines():
            line = line.strip()
            if line:
                cmd_list.append(line)
    return cmd_list

def classify_command(cmd_list):
    auto_list = []
    manual_list = []
    for cmd in cmd_list:
        is_allow = any(k in cmd for k in ALLOW_CMD_KEYS)
        is_risk = any(k in cmd for k in DANGER_CMD_KEYS)
        if is_allow and not is_risk:
            auto_list.append(cmd)
        else:
            manual_list.append(cmd)
    return auto_list, manual_list

# ===================== 【修改4】新增 secret 参数 =====================
def exec_single_device(ip, vendor, user, pwd, secret, cmd_list):
    if vendor not in DEV_TYPE_MAP:
        return f"【{ip}】不支持该厂商接入\r\n"

    dev_conn = {
        "device_type": DEV_TYPE_MAP[vendor],
        "host": ip,
        "username": user,
        "password": pwd,
        # ===================== 【修改5】新增特权密码配置 =====================
        "secret": secret,
        "timeout": 30,
        "port": 22
    }

    output = f"===== 故障设备 {ip} 二次核查结果 =====\r\n"
    try:
        with ConnectHandler(**dev_conn) as conn:
            # ===================== 【修改6】华为进入特权模式 =====================
            conn.enable()
            for cmd in cmd_list:
                output += f"\n>> 执行指令：{cmd}\n"
                output += conn.send_command(cmd)
        return output

    except NetmikoAuthenticationException:
        return f"【{ip}】二次核查失败：账号密码认证错误\r\n"
    except NetmikoTimeoutException:
        return f"【{ip}】二次核查失败：设备连接超时\r\n"
    except socket.gaierror:
        return f"【{ip}】二次核查失败：DNS解析异常\r\n"
    except ConnectionRefusedError:
        return f"【{ip}】二次核查失败：SSH端口拒绝\r\n"
    except Exception as e:
        return f"【{ip}】二次核查失败：{str(e)}\r\n"

def match_report_by_ip(ip):
    if not os.path.exists(REPORT_PATH):
        return ""
    for fname in os.listdir(REPORT_PATH):
        if ip in fname:
            fpath = os.path.join(REPORT_PATH, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                return f.read()
    return ""

def run_trouble(project_dir: str, progress_callback=None) -> List[str]:
    _resolve_paths(project_dir)
    init_folder()
    ip_dict = load_device_ip_dict()
    if not ip_dict:
        return ["未读取到项目设备清单 device_list.txt"]

    fault_ips = get_fault_ip_list()
    if not fault_ips:
        return ["未检测到故障设备，无需二次核查"]

    total = len(fault_ips)
    results: List[str] = []
    all_manual_risk: List[str] = []

    for idx, ip in enumerate(fault_ips):
        if progress_callback:
            progress_callback(idx + 1, total, f"正在核查 {ip} ...")

        if ip not in ip_dict:
            results.append(f"设备 {ip} 不在设备清单中，跳过核查")
            continue

        dev_info = ip_dict[ip]
        vendor = dev_info["vendor"]
        user = dev_info["user"]
        pwd = dev_info["pwd"]
        secret = dev_info["secret"]

        report_text = match_report_by_ip(ip)
        if not report_text:
            results.append(f"未找到设备 {ip} 对应故障报告，跳过")
            continue

        cmd_list = extract_command_from_report(report_text)
        auto_cmd, manual_cmd = classify_command(cmd_list)
        all_manual_risk.extend(manual_cmd)

        if not auto_cmd:
            results.append(f"设备 {ip} 无可用自动排查指令")
            continue

        res = exec_single_device(ip, vendor, user, pwd, secret, auto_cmd)
        save_file = os.path.join(CHECK_RESULT_PATH, f"二次核查_{ip}.txt")
        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        with open(save_file, "w", encoding="utf-8") as f:
            f.write(res)
        results.append(f"设备 {ip} 二次核查完成")

    os.makedirs(os.path.dirname(MANUAL_TASK_FILE), exist_ok=True)
    with open(MANUAL_TASK_FILE, "w", encoding="utf-8") as f:
        f.write("===== 高危配置操作清单【必须人工登录手动执行】=====\n")
        for item in set(all_manual_risk):
            f.write(item + "\n")

    if progress_callback:
        progress_callback(total, total, "故障二次核查完成")
    return results


def main():
    init_folder()
    ip_dict = load_device_ip_dict()
    if not ip_dict:
        print("❌ 未读取到项目设备清单 device_list.txt")
        return

    fault_ips = get_fault_ip_list()
    if not fault_ips:
        print("✅ 未检测到故障设备，无需二次核查")
        return
    print(f"🔍 检测到故障设备共 {len(fault_ips)} 台：{fault_ips}")

    all_manual_risk = []

    for ip in fault_ips:
        if ip not in ip_dict:
            print(f"⚠️ 设备 {ip} 不在设备清单中，跳过核查")
            continue

        dev_info = ip_dict[ip]
        vendor = dev_info["vendor"]
        user = dev_info["user"]
        pwd = dev_info["pwd"]
        # ===================== 【修改7】读取特权密码 =====================
        secret = dev_info["secret"]

        report_text = match_report_by_ip(ip)
        if not report_text:
            print(f"⚠️ 未找到设备 {ip} 对应故障报告，跳过")
            continue

        cmd_list = extract_command_from_report(report_text)
        auto_cmd, manual_cmd = classify_command(cmd_list)
        all_manual_risk.extend(manual_cmd)

        if not auto_cmd:
            print(f"ℹ️ 设备 {ip} 无可用自动排查指令")
            continue

        # ===================== 【修改8】传入 secret 参数 =====================
        res = exec_single_device(ip, vendor, user, pwd, secret, auto_cmd)
        save_file = os.path.join(CHECK_RESULT_PATH, f"二次核查_{ip}.txt")
        with open(save_file, "w", encoding="utf-8") as f:
            f.write(res)
        print(f"✅ 设备 {ip} 二次核查完成，结果已保存")

    with open(MANUAL_TASK_FILE, "w", encoding="utf-8") as f:
        f.write("===== 高危配置操作清单【必须人工登录手动执行】=====\n")
        for item in set(all_manual_risk):
            f.write(item + "\n")

    print("\n===== 故障设备二次核查全部执行完成 =====")
    print(f"📄 二次核查结果目录：{CHECK_RESULT_PATH}")
    print(f"📄 高危人工操作清单：{MANUAL_TASK_FILE}")

if __name__ == "__main__":
    main()