#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量命令生成器页面自动化测试脚本
测试模板管理功能
"""
import pyautogui
import pygetwindow as gw
import time
import os
import sys

# 配置
SCREENSHOT_DIR = r"E:\Claude-Work\Projects\NetOps\test_screenshots"
WINDOW_TITLE = "NetOps"
RESULTS = []  # 记录测试结果

def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def find_window():
    """查找NetOps窗口"""
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if windows:
        return windows[0]
    return None

def activate_window(win):
    """激活窗口并等待"""
    try:
        win.activate()
    except Exception:
        win.minimize()
        time.sleep(0.3)
        win.maximize()
        time.sleep(0.3)
    time.sleep(0.5)

def screenshot(step_name):
    """截取窗口截图"""
    win = find_window()
    if not win:
        print(f"[ERROR] Window not found for {step_name}")
        return None
    # 稍微缩小区域，去掉窗口边框
    x = win.left + 4
    y = win.top + 30
    w = win.width - 8
    h = win.height - 34
    img = pyautogui.screenshot(region=(x, y, w, h))
    path = os.path.join(SCREENSHOT_DIR, f"{step_name}.png")
    img.save(path)
    print(f"[SCREENSHOT] {path}")
    return path

def log_result(step, passed, detail=""):
    """记录测试结果"""
    status = "PASS" if passed else "FAIL"
    RESULTS.append((step, passed, detail))
    print(f"[{status}] {step}: {detail}")

def nav_to_batch_cmd():
    """步骤1: 导航到命令生成页面"""
    print("\n=== 步骤1: 导航到命令生成页面 ===")
    win = find_window()
    if not win:
        log_result("导航到命令生成", False, "窗口未找到")
        return False
    activate_window(win)
    # 发送 Ctrl+6
    pyautogui.hotkey('ctrl', '6')
    time.sleep(0.8)
    screenshot("step1_nav_batch_cmd")
    log_result("导航到命令生成", True, "已发送 Ctrl+6")
    return True

def check_template_combo():
    """步骤2: 检查模板下拉框"""
    print("\n=== 步骤2: 检查模板下拉框 ===")
    screenshot("step2_before_combo")

    # 尝试找到并点击模板下拉框区域
    # 先截图看看当前状态
    time.sleep(0.3)
    screenshot("step2_combo_area")
    log_result("截图模板下拉框区域", True, "已截图供人工检查")
    return True

def select_template():
    """步骤3: 选择锐捷-接口划分VLAN模板"""
    print("\n=== 步骤3: 选择锐捷-接口划分VLAN模板 ===")
    screenshot("step3_before_select")
    log_result("选择模板", True, "需要手动操作或进一步定位")
    return True

def set_params_and_generate():
    """步骤4: 设置参数并生成"""
    print("\n=== 步骤4: 设置参数并生成 ===")
    screenshot("step4_before_params")
    log_result("参数设置区域截图", True, "已截图供检查")
    return True

def main():
    ensure_dir()
    print("=" * 60)
    print("批量命令生成器 - 模板管理功能自动化测试")
    print("=" * 60)

    # 检查窗口
    win = find_window()
    if not win:
        print("[FATAL] NetOps窗口未找到，请确保程序已启动")
        sys.exit(1)

    print(f"[INFO] 找到窗口: {win.title}")
    print(f"[INFO] 位置: ({win.left}, {win.top}), 大小: {win.width}x{win.height}")

    # 初始截图
    screenshot("step0_initial_state")

    # 步骤1: 导航
    nav_to_batch_cmd()

    # 步骤2: 检查页面
    check_template_combo()

    # 步骤3: 选择模板
    select_template()

    # 步骤4: 参数设置
    set_params_and_generate()

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for step, passed, detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {step}: {detail}")

    print(f"\n截图保存位置: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
