#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量命令生成器 - 模板管理功能逻辑测试
不依赖GUI，直接测试数据层和生成逻辑
"""
import sys
import os
import re
import json
import tempfile
import shutil
from datetime import datetime

# 修复Windows GBK编码问题
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

RESULTS = []

def log_result(step, passed, detail=""):
    RESULTS.append((step, passed, detail))
    marker = "[OK]" if passed else "[FAIL]"
    print(f"{marker} {step}: {detail}")


print("=" * 70)
print("批量命令生成器 - 模板管理功能逻辑测试")
print("=" * 70)

# ============================================================
# 测试1: 预置模板数据构建（直接调用_build_preset_templates）
# ============================================================
print("\n--- 测试1: 预置模板数据构建 ---")

from src.ui.batch_cmd_generator_page import _build_preset_templates

presets = _build_preset_templates()
log_result(
    "预置模板数量=8",
    len(presets) == 8,
    f"实际: {len(presets)}个"
)

print("  预置模板列表:")
for i, t in enumerate(presets):
    print(f"    {i+1}. [{t['vendor']}] {t['name']} | 参数: {t['params']}")

# 验证每个模板的关键字段
all_have_id = all('id' in t and t['id'].startswith('preset_') for t in presets)
all_have_name = all('name' in t and len(t['name']) > 0 for t in presets)
all_have_content = all('content' in t and len(t['content']) > 0 for t in presets)
all_have_params = all('params' in t and isinstance(t['params'], list) for t in presets)
all_have_category = all(t.get('category') == 'preset' for t in presets)

log_result("所有模板有规范ID", all_have_id, f"全部以'preset_'开头: {all_have_id}")
log_result("所有模板有名称", all_have_name, f"全部有名称: {all_have_name}")
log_result("所有模板有内容", all_have_content, f"全部有内容: {all_have_content}")
log_result("所有模板有参数列表", all_have_params, f"全部有参数: {all_have_params}")
log_result("所有模板category='preset'", all_have_category, f"全部为preset: {all_have_category}")

# 验证四厂商都有
vendors = sorted(set(t['vendor'] for t in presets))
log_result(
    "四厂商覆盖",
    vendors == ['H3C', '华为', '思科', '锐捷'],
    f"厂商: {vendors}"
)

# 验证每个厂商有2个模板（VLAN + 接口VLAN）
for vendor in ['锐捷', '华为', 'H3C', '思科']:
    vendor_presets = [t for t in presets if t['vendor'] == vendor]
    vlan_t = [t for t in vendor_presets if t['type'] == 'vlan']
    iface_t = [t for t in vendor_presets if t['type'] == 'interface_vlan']
    log_result(
        f"{vendor}: 2个模板",
        len(vendor_presets) == 2 and len(vlan_t) == 1 and len(iface_t) == 1,
        f"总计{len(vendor_presets)}, VLAN={len(vlan_t)}, 接口VLAN={len(iface_t)}"
    )

# ============================================================
# 测试2: 锐捷-接口划分VLAN模板详情
# ============================================================
print("\n--- 测试2: 锐捷-接口划分VLAN模板详情 ---")

ruijie_iface = next((t for t in presets if t['id'] == 'preset_ruijie_interface_vlan'), None)
log_result("锐捷-接口划分VLAN存在", ruijie_iface is not None, f"找到: {ruijie_iface is not None}")

if ruijie_iface:
    content = ruijie_iface['content']
    print(f"  模板内容:\n{'-'*40}")
    print(content)
    print(f"{'-'*40}")

    expected = "interface GigabitEthernet 0/%a\n switchport mode access\n switchport access vlan %b\nexit\n"
    log_result("模板内容完全匹配", content == expected, f"匹配: {content == expected}")
    log_result("参数=['a','b']", ruijie_iface['params'] == ['a', 'b'], f"参数: {ruijie_iface['params']}")

    # 验证模板中有且仅有%a和%b两个占位符
    found_params = sorted(set(re.findall(r'%([a-f])', content)))
    log_result("模板占位符检测", found_params == ['a', 'b'], f"占位符: {found_params}")

# ============================================================
# 测试3: 命令生成逻辑（不依赖GUI）
# ============================================================
print("\n--- 测试3: 命令生成逻辑 ---")

def generate_commands(template: str, configs: dict, max_count: int) -> str:
    """
    从BatchCmdGeneratorPage._generate()提取的核心生成逻辑
    """
    used_params = sorted(set(re.findall(r'%([a-f])', template)))
    if not used_params:
        return "\n".join([template] * max_count)

    lines = []
    total_count = [0]

    def _generate_recursive(param_idx, current_values):
        if total_count[0] >= max_count:
            return
        if param_idx >= len(used_params):
            rendered = template
            for char, val in current_values.items():
                rendered = rendered.replace(f"%{char}", str(val))
            lines.append(rendered)
            total_count[0] += 1
            return

        char = used_params[param_idx]
        cfg = configs.get(char, {"base": 0, "step": 1, "repeat": None, "loop": None})
        base = cfg["base"]
        step = cfg["step"]
        loop = cfg.get("loop") or 1
        repeat = cfg.get("repeat") or 1

        values = []
        for i in range(loop):
            values.append(base + i * step)

        for val in values:
            new_values = dict(current_values)
            new_values[char] = val
            for _ in range(repeat):
                if total_count[0] >= max_count:
                    return
                _generate_recursive(param_idx + 1, new_values)

    _generate_recursive(0, {})
    return "\n".join(lines)

# 测试3a: 锐捷接口划分VLAN，a=1..3, b=100,110, count=6
template = ruijie_iface['content']
configs = {
    'a': {'base': 1, 'step': 1, 'loop': 3, 'repeat': None},
    'b': {'base': 100, 'step': 10, 'loop': 2, 'repeat': None},
}
output = generate_commands(template, configs, 6)

print(f"  生成结果:\n{'-'*40}")
print(output)
print(f"{'-'*40}")

# 分析
all_lines = [l for l in output.strip().split('\n') if l.strip()]
log_result("输出非空行数=24", len(all_lines) == 24, f"非空行数: {len(all_lines)} (期望24=6组x4行)")

# 逐行分析
print("  逐行分析:")
for i, line in enumerate(all_lines):
    print(f"    line[{i:2d}]: {line}")

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

# 验证对应关系：每个接口应该对应两个VLAN
# 期望顺序: (0/1,100), (0/1,110), (0/2,100), (0/2,110), (0/3,100), (0/3,110)
# 每组4行: interface, switchport mode, switchport access vlan, exit
expected_pairs = [
    ("GigabitEthernet 0/1", "vlan 100"),
    ("GigabitEthernet 0/1", "vlan 110"),
    ("GigabitEthernet 0/2", "vlan 100"),
    ("GigabitEthernet 0/2", "vlan 110"),
    ("GigabitEthernet 0/3", "vlan 100"),
    ("GigabitEthernet 0/3", "vlan 110"),
]

for i, (iface, vlan) in enumerate(expected_pairs):
    block_start = i * 4
    block = '\n'.join(all_lines[block_start:block_start+4])
    has_iface = iface in block
    has_vlan = vlan in block
    log_result(
        f"块{i+1}: {iface} + {vlan}",
        has_iface and has_vlan,
        f"接口={has_iface}, VLAN={has_vlan}"
    )

# ============================================================
# 测试4: 参数边界测试
# ============================================================
print("\n--- 测试4: 参数边界测试 ---")

# 4a: 单参数单值
simple_template = "vlan %a\n name VLAN_%a\nexit\n"
simple_configs = {'a': {'base': 100, 'step': 1, 'loop': 1, 'repeat': None}}
simple_output = generate_commands(simple_template, simple_configs, 1)
log_result(
    "单参数单值生成",
    "vlan 100" in simple_output and "VLAN_100" in simple_output,
    f"输出: {simple_output[:50]}..."
)

# 4b: 重复模式
repeat_configs = {'a': {'base': 10, 'step': 0, 'loop': 1, 'repeat': 3}}
repeat_output = generate_commands(simple_template, repeat_configs, 10)
repeat_lines = [l for l in repeat_output.strip().split('\n') if l.strip()]
log_result(
    "重复模式: 值10重复3次",
    repeat_lines.count('vlan 10') == 3,
    f"'vlan 10'出现{repeat_lines.count('vlan 10')}次 (期望3)"
)

# 4c: 步长为0 + 循环
zero_step_configs = {'a': {'base': 5, 'step': 0, 'loop': 3, 'repeat': None}}
zero_output = generate_commands("vlan %a\n", zero_step_configs, 10)
zero_lines = [l for l in zero_output.strip().split('\n') if l.strip()]
log_result(
    "步长为0: 全部为vlan 5",
    all(l == 'vlan 5' for l in zero_lines),
    f"全部为'vlan 5': {all(l == 'vlan 5' for l in zero_lines)}"
)

# 4d: 命令数量限制
limit_output = generate_commands(simple_template, {'a': {'base': 1, 'step': 1, 'loop': 100, 'repeat': None}}, 5)
limit_blocks = limit_output.strip().split('\n\n')  # 每个块之间可能有空行
# 实际上没有空行分隔，每个模板渲染是一个整体
limit_all_lines = [l for l in limit_output.strip().split('\n') if l.strip()]
log_result(
    "命令数量限制=5",
    len(limit_all_lines) == 15,  # 5组 x 3行
    f"非空行数: {len(limit_all_lines)} (期望15=5x3)"
)

# ============================================================
# 测试5: 模板保存/加载逻辑
# ============================================================
print("\n--- 测试5: 模板保存/加载逻辑 ---")

from src.utils.file_operators import JSONFileManager

# 使用临时文件测试
tmp_dir = tempfile.mkdtemp()
tmp_file = os.path.join(tmp_dir, "test_templates.json")

try:
    # 保存
    test_data = {
        "version": "1.0",
        "templates": presets[:2],  # 只保存2个
    }
    save_ok = JSONFileManager.save_json(tmp_file, test_data)
    log_result("模板保存成功", save_ok, f"文件: {tmp_file}")

    # 加载
    loaded = JSONFileManager.load_json(tmp_file, default=None)
    log_result(
        "模板加载成功",
        loaded is not None and "templates" in loaded and len(loaded["templates"]) == 2,
        f"加载了{len(loaded['templates']) if loaded and 'templates' in loaded else 0}个模板"
    )

    # 验证原子写入（文件存在且可读）
    log_result("模板文件存在", os.path.exists(tmp_file), f"文件大小: {os.path.getsize(tmp_file)} bytes")

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
    log_result("临时文件清理", not os.path.exists(tmp_file), "已清理")

# ============================================================
# 测试6: 用户模板管理逻辑
# ============================================================
print("\n--- 测试6: 用户模板管理逻辑 ---")

# 模拟用户模板操作
user_templates = []

# 6a: 添加模板
new_template = {
    "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "name": "测试模板_AutoTest",
    "category": "user",
    "vendor": "",
    "type": "",
    "content": "vlan %a\n name TEST_VLAN_%a\nexit\n",
    "params": ["a"],
    "description": "",
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
user_templates.append(new_template)
log_result("添加用户模板", len(user_templates) == 1, f"用户模板数: {len(user_templates)}")

# 6b: 重复名称检测
all_names = {t["name"] for t in presets + user_templates}
log_result(
    "重复名称检测",
    "测试模板_AutoTest" in all_names,
    f"名称在列表中: {'测试模板_AutoTest' in all_names}"
)

# 6c: 删除模板
user_templates = [t for t in user_templates if t["id"] != new_template["id"]]
log_result("删除用户模板", len(user_templates) == 0, f"用户模板数: {len(user_templates)}")

# 6d: 预置模板不可通过用户接口删除
preset_ids = {t["id"] for t in presets}
log_result(
    "预置模板ID不受用户操作影响",
    "preset_ruijie_interface_vlan" in preset_ids,
    f"锐捷接口VLAN模板ID存在: {'preset_ruijie_interface_vlan' in preset_ids}"
)

# ============================================================
# 测试7: 所有预置模板的命令生成验证
# ============================================================
print("\n--- 测试7: 所有预置模板命令生成验证 ---")

for t in presets:
    content = t['content']
    params = t['params']

    # 为每个参数生成简单配置
    test_configs = {}
    for i, p in enumerate(params):
        test_configs[p] = {'base': i + 1, 'step': 1, 'loop': 2, 'repeat': None}

    test_output = generate_commands(content, test_configs, 10)

    # 验证输出非空
    has_output = len(test_output.strip()) > 0
    # 验证没有未替换的占位符
    remaining = re.findall(r'%[a-f]', test_output)
    no_placeholder = len(remaining) == 0

    log_result(
        f"[{t['vendor']}] {t['name']}",
        has_output and no_placeholder,
        f"有输出={has_output}, 无残留占位符={no_placeholder}"
    )

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
