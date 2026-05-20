"""
最终验证：测试所有四厂商的接入交换机和核心交换机
"""
import sys
import os
sys.path.insert(0, r'e:\network-config')
os.chdir(r'e:\network-config')

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

print("=" * 70)
print("【进度：80%｜当前任务：全厂商验证测试】")
print("=" * 70)

vendors = [
    ('锐捷', 'ruijie', 'RuijieAccessSwitchConfig', 'RuijieCoreSwitchConfig'),
    ('华为', 'huawei', 'HuaweiAccessSwitchConfig', 'HuaweiCoreSwitchConfig'),
    ('H3C', 'h3c', 'H3CAccessSwitchConfig', 'H3CCoreSwitchConfig'),
    ('思科', 'cisco', 'CiscoAccessSwitchConfig', 'CiscoCoreSwitchConfig'),
]

all_pass = True

for vendor_cn, vendor_en, access_class, core_class in vendors:
    print(f"\n{'='*50}")
    print(f"【{vendor_cn}】")
    print(f"{'='*50}")
    
    # 测试接入交换机
    print(f"  [1] 接入交换机...", end=" ")
    try:
        module = __import__(f'src.ui.config_pages.{vendor_en}.access_switch_config', fromlist=[access_class])
        cls = getattr(module, access_class)
        instance = cls(None)
        print("✅ 成功")
        
        # 检查Tab数量
        if hasattr(instance, 'tab_widget'):
            tab_count = instance.tab_widget.count()
            print(f"      Tab数量: {tab_count}")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        all_pass = False
    
    # 测试核心交换机
    print(f"  [2] 核心交换机...", end=" ")
    try:
        module = __import__(f'src.ui.config_pages.{vendor_en}.core_switch_config', fromlist=[core_class])
        cls = getattr(module, core_class)
        instance = cls(None)
        print("✅ 成功")
        
        # 检查Tab数量
        if hasattr(instance, 'tab_widget'):
            tab_count = instance.tab_widget.count()
            print(f"      Tab数量: {tab_count}")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        all_pass = False

app.quit()

print("\n" + "=" * 70)
if all_pass:
    print("🎉 全部测试通过！所有四厂商的接入/核心交换机均可正常实例化")
else:
    print("⚠️ 部分测试失败，请检查上方错误信息")
print("=" * 70)
