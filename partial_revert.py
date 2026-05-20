"""
部分回退：将华为/H3C/思科的generate_config恢复为空壳
保留崩溃修复（BaseConfigPage/addTab）
"""

EMPTY_GENERATE_CONFIG = '''    def generate_config(self):
        """生成配置脚本（基础实现，各厂商应覆盖此方法）"""
        config = []
        config.append("! 此方法应在子类中实现厂商特定命令")
        config.append("")
        self.preview_text.setPlainText('\\n'.join(config))
'''

def revert_generate_config(filepath, vendor_name):
    """将generate_config方法回退为空壳"""
    print(f"\n  回退 {vendor_name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到generate_config方法的开始位置
    start_idx = None
    for i, line in enumerate(lines):
        if 'def generate_config(self):' in line:
            start_idx = i
            break
    
    if start_idx is None:
        print(f"    ⚠️ 未找到generate_config方法")
        return False
    
    # 截断到generate_config方法开始处
    # 保留之前的内容 + 空壳方法
    new_lines = lines[:start_idx]
    new_lines.append(EMPTY_GENERATE_CONFIG)
    new_lines.append('\n')  # 文件末尾换行
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # 统计变化
    old_count = len(lines)
    new_count = len(new_lines)
    print(f"    ✅ 已回退: {old_count}行 → {new_count}行 (-{old_count - new_count}行)")
    return True

def main():
    print("=" * 60)
    print("【进度：40%｜当前任务：部分回退 - 仅回退generate_config】")
    print("=" * 60)
    
    files = [
        (r'e:\network-config\src\ui\config_pages\huawei\access_switch_config.py', '华为'),
        (r'e:\network-config\src\ui\config_pages\h3c\access_switch_config.py', 'H3C'),
        (r'e:\network-config\src\ui\config_pages\cisco\access_switch_config.py', '思科'),
    ]
    
    reverted = 0
    for path, name in files:
        if revert_generate_config(path, name):
            reverted += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 部分回退完成: {reverted}/{len(files)} 个文件已处理")
    print("✅ 保留的修复: BaseConfigPage增强 + 四厂商addTab兼容")
    print("=" * 60)

if __name__ == '__main__':
    main()
