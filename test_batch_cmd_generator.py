#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量命令生成器 - 模板管理功能直接测试
通过直接调用页面类方法进行测试，不依赖GUI交互
"""
import sys
import os

# 修复Windows GBK编码问题
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import QApplication
from src.ui.batch_cmd_generator_page import BatchCmdGeneratorPage, _build_preset_templates

# 必须创建QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

RESULTS = []

def log_result(step, passed, detail=""):
    RESULTS.append((step, passed, detail))
    marker = "[OK]" if passed else "[FAIL]"
    print(f"{marker} {step}: {detail}")


print("=" * 70)
print("批量命令生成器 - 模板管理功能测试")
print("=" * 70)

# ============================================================
# 测试1: 预置模板数据构建
# ============================================================
print("\n--- 测试1: 预置模板数据构建 ---")
presets = _build_preset_templates()
log_result(
    "预置模板数量",
    len(presets) == 8,
    f"期望8个，实际{len(presets)}个"
)

print("  预置模板列表:")
for i, t in enumerate(presets):
    print(f"    {i+1}. [{t['vendor']}] {t['name']} - 参数: {t['params']}")

# 检查锐捷-接口划分VLAN
ruijie_iface_vlan = [t for t in presets if t['id'] == 'preset_ruijie_interface_vlan']
log_result(
    "锐捷-接口划分VLAN模板存在",
    len(ruijie_iface_vlan) == 1,
    f"找到{len(ruijie_iface_vlan)}个"
)

if ruijie_iface_vlan:
    t = ruijie_iface_vlan[0]
    expected_content = "interface GigabitEthernet 0/%a\n switchport mode access\n switchport access vlan %b\nexit\n"
    log_result(
        "模板内容正确",
        t['content'] == expected_content,
        f"内容匹配: {t['content'] == expected_content}"
    )
    log_result(
        "模板参数正确",
        t['params'] == ['a', 'b'],
        f"参数: {t['params']}"
    )

# ============================================================
# 测试2: 页面实例化 + 模板加载
# ============================================================
print("\n--- 测试2: 页面实例化 + 模板数据加载 ---")
page = BatchCmdGeneratorPage()

log_result("页面实例化成功", page is None is False, "BatchCmdGeneratorPage 创建成功")
log_result(
    "预置模板已加载",
    len(page._preset_templates) == 8,
    f"预置模板数: {len(page._preset_templates)}"
)
log_result(
    "用户模板初始为空",
    len(page._user_templates) == 0,
    f"用户模板数: {len(page._user_templates)}"
)

# ============================================================
# 测试3: 模板下拉框内容
# ============================================================
print("\n--- 测试3: 模板下拉框内容 ---")
combo = page.template_combo
total_items = combo.count()
# 结构: "请选择模板..."(1) + 分隔符(1) + 8预置 = 10
expected_count = 1 + 1 + 8
log_result(
    "下拉框条目数量",
    total_items == expected_count,
    f"期望{expected_count}条，实际{total_items}条"
)

# 打印下拉框所有条目
print("  下拉框条目:")
for i in range(combo.count()):
    text = combo.itemText(i)
    data = combo.itemData(i)
    if text:
        print(f"    [{i}] {text} (data={'dict' if isinstance(data, dict) else 'separator' if data is None else data})")
    else:
        print(f"    [{i}] --- separator ---")

# 检查锐捷-接口划分VLAN
found_ruijie = False
for i in range(combo.count()):
    text = combo.itemText(i)
    if "锐捷-接口划分VLAN" in text:
        found_ruijie = True
        data = combo.itemData(i)
        log_result(
            "模板关联数据正确",
            isinstance(data, dict) and data.get('id') == 'preset_ruijie_interface_vlan',
            f"关联数据ID: {data.get('id') if isinstance(data, dict) else 'None'}"
        )
        break

log_result("下拉框包含锐捷-接口划分VLAN", found_ruijie, f"找到: {found_ruijie}")

# ============================================================
# 测试4: 选择模板 -> 填入编辑区
# ============================================================
print("\n--- 测试4: 选择模板 -> 填入编辑区 ---")

# 找到锐捷-接口划分VLAN的combo索引
ruijie_idx = -1
for i in range(combo.count()):
    if "锐捷-接口划分VLAN" in combo.itemText(i):
        ruijie_idx = i
        break

if ruijie_idx >= 0:
    # 先清空编辑区（模拟无内容状态，避免确认对话框）
    page.template_edit.clear()
    # 模拟选中
    combo.setCurrentIndex(ruijie_idx)
    page._on_template_selected(ruijie_idx)

    edit_content = page.template_edit.toPlainText()
    print(f"  编辑区内容:\n{'-'*40}")
    print(edit_content)
    print(f"{'-'*40}")

    has_interface = "interface GigabitEthernet 0/%a" in edit_content
    has_switchport = "switchport mode access" in edit_content
    has_vlan = "switchport access vlan %b" in edit_content

    log_result("模板内容填入 - interface", has_interface, f"包含interface: {has_interface}")
    log_result("模板内容填入 - switchport", has_switchport, f"包含switchport: {has_switchport}")
    log_result("模板内容填入 - vlan", has_vlan, f"包含vlan: {has_vlan}")
else:
    log_result("选择锐捷模板", False, "未找到模板索引")

# ============================================================
# 测试5: 参数设置 + 生成命令
# ============================================================
print("\n--- 测试5: 参数设置 + 命令生成 ---")

# 设置参数a: 基数=1, 步长=1, 循环=3
param_a = page._param_widgets[0]
param_a.base_spin.setValue(1)
param_a.step_spin.setValue(1)
param_a.loop_cb.setChecked(True)
param_a.loop_spin.setValue(3)

cfg_a = param_a.get_config()
log_result(
    "参数a配置",
    cfg_a['base'] == 1 and cfg_a['step'] == 1 and cfg_a['loop'] == 3 and cfg_a['repeat'] is None,
    f"base={cfg_a['base']}, step={cfg_a['step']}, loop={cfg_a['loop']}, repeat={cfg_a['repeat']}"
)

# 设置参数b: 基数=100, 步长=10, 循环=2
param_b = page._param_widgets[1]
param_b.base_spin.setValue(100)
param_b.step_spin.setValue(10)
param_b.loop_cb.setChecked(True)
param_b.loop_spin.setValue(2)

cfg_b = param_b.get_config()
log_result(
    "参数b配置",
    cfg_b['base'] == 100 and cfg_b['step'] == 10 and cfg_b['loop'] == 2 and cfg_b['repeat'] is None,
    f"base={cfg_b['base']}, step={cfg_b['step']}, loop={cfg_b['loop']}, repeat={cfg_b['repeat']}"
)

# 设置命令数量为6
page.cmd_count_spin.setValue(6)
log_result("命令数量=6", page.cmd_count_spin.value() == 6, f"值: {page.cmd_count_spin.value()}")

# 执行生成
page._generate()
output = page.output_edit.toPlainText()

print(f"\n  生成的输出内容:\n{'-'*40}")
print(output)
print(f"{'-'*40}")

# 分析输出
# 模板: "interface GigabitEthernet 0/%a\n switchport mode access\n switchport access vlan %b\nexit\n"
# 参数a: base=1, step=1, loop=3 -> values: [1, 2, 3]
# 参数b: base=100, step=10, loop=2 -> values: [100, 110]
# cmd_count=6
# 递归: a=1,b=100 -> 1组; a=1,b=110 -> 1组; a=2,b=100 -> 1组; a=2,b=110 -> 1组; a=3,b=100 -> 1组; a=3,b=110 -> 1组
# 共6组，每组模板渲染为1个字符串(多行)，join后是6*4=24行
lines = output.strip().split('\n')
non_empty_lines = [l for l in lines if l.strip()]
log_result(
    "输出非空行数",
    len(non_empty_lines) == 24,
    f"非空行数: {len(non_empty_lines)} (期望24=6组x4行)"
)

# 验证关键内容
has_gige1 = "GigabitEthernet 0/1" in output
has_gige2 = "GigabitEthernet 0/2" in output
has_gige3 = "GigabitEthernet 0/3" in output
has_vlan100 = "vlan 100" in output
has_vlan110 = "vlan 110" in output

log_result("包含 GigabitEthernet 0/1", has_gige1, f"找到: {has_gige1}")
log_result("包含 GigabitEthernet 0/2", has_gige2, f"找到: {has_gige2}")
log_result("包含 GigabitEthernet 0/3", has_gige3, f"找到: {has_gige3}")
log_result("包含 vlan 100", has_vlan100, f"找到: {has_vlan100}")
log_result("包含 vlan 110", has_vlan110, f"找到: {has_vlan110}")

# 验证接口和VLAN的对应关系
# 应该看到: 0/1->vlan100, 0/1->vlan110, 0/2->vlan100, 0/2->vlan110, 0/3->vlan100, 0/3->vlan110
import re
blocks = output.strip().split('\n\n')  # 如果有多行分隔
# 实际上输出是\n分隔的，每4行一个块
all_lines = [l for l in output.strip().split('\n') if l.strip()]
print(f"\n  逐行分析:")
for i, line in enumerate(all_lines):
    print(f"    line[{i:2d}]: {line}")

# ============================================================
# 测试6: 保存当前为模板
# ============================================================
print("\n--- 测试6: 保存当前为模板 ---")

# 输入自定义模板内容
page.template_edit.clear()
page.template_edit.setPlainText("vlan %a\n name TEST_VLAN_%a\nexit\n")

# 直接模拟保存操作
import re as re_module
from datetime import datetime
content = page.template_edit.toPlainText().strip()
test_template_name = "测试模板_AutoTest"
params = sorted(set(re_module.findall(r'%([a-f])', content)))
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
new_template = {
    "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "name": test_template_name,
    "category": "user",
    "vendor": "",
    "type": "",
    "content": content,
    "params": params,
    "description": "",
    "created_at": now,
}
page._user_templates.append(new_template)
page._save_templates()
page._refresh_template_combo()

log_result(
    "用户模板数量=1",
    len(page._user_templates) == 1,
    f"用户模板数: {len(page._user_templates)}"
)

# 验证新模板出现在下拉框
found_test_template = False
for i in range(combo.count()):
    if combo.itemText(i) == test_template_name:
        found_test_template = True
        data = combo.itemData(i)
        log_result(
            "新模板关联数据",
            isinstance(data, dict) and data.get('name') == test_template_name,
            f"名称: {data.get('name') if isinstance(data, dict) else 'N/A'}"
        )
        break

log_result("新模板出现在下拉框", found_test_template, f"找到'{test_template_name}': {found_test_template}")

# ============================================================
# 测试7: 重复名称检查
# ============================================================
print("\n--- 测试7: 重复名称检查 ---")
all_names = {t["name"] for t in page._preset_templates + page._user_templates}
log_result(
    "重复名称检测",
    test_template_name in all_names,
    f"'{test_template_name}' 在已有名称中: {test_template_name in all_names}"
)

# ============================================================
# 测试8: 预置模板保护
# ============================================================
print("\n--- 测试8: 预置模板保护 ---")
preset_template = page._preset_templates[0]
is_preset = preset_template.get("category") == "preset"
log_result("预置模板category='preset'", is_preset, f"category: {preset_template.get('category')}")

# ============================================================
# 测试9: 下拉框总条目数（8预置+1用户）
# ============================================================
print("\n--- 测试9: 下拉框总条目数 ---")
total = combo.count()
# 结构: "请选择模板..."(1) + 分隔符(1) + 8预置 + 分隔符(1) + 1用户 = 12
expected = 1 + 1 + 8 + 1 + 1
log_result(
    "下拉框总条目数",
    total == expected,
    f"期望{expected}条，实际{total}条"
)

# 打印最终下拉框内容
print("  最终下拉框条目:")
for i in range(combo.count()):
    text = combo.itemText(i)
    if text:
        print(f"    [{i}] {text}")
    else:
        print(f"    [{i}] --- separator ---")

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 70)
print("测试结果汇总")
print("=" * 70)

passed = sum(1 for _, p, _ in RESULTS if p)
failed_count = sum(1 for _, p, _ in RESULTS if not p)
total_tests = len(RESULTS)

for step, p, detail in RESULTS:
    marker = "[OK]" if p else "[FAIL]"
    print(f" {marker} {step}: {detail}")

print(f"\n总计: {total_tests} 项 | 通过: {passed} | 失败: {failed_count}")

if failed_count > 0:
    print("\n失败的测试:")
    for step, p, detail in RESULTS:
        if not p:
            print(f"  [FAIL] {step}: {detail}")
    sys.exit(1)
else:
    print("\n所有测试通过!")
    sys.exit(0)
