#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置生成器缓存测试（V0.3.7 新增）

覆盖：
- functools.lru_cache 缓存命中
- frozenset(kwargs.items()) 作为缓存键的正确性
- 四厂商四类设备配置生成缓存
- 缓存不跨越不同参数调用
"""

import pytest

from src.core.config_generator import ConfigGenerator


class TestConfigGeneratorCache:
    """ConfigGenerator LRU 缓存测试。"""

    def setup_method(self):
        """每个测试前清空 LRU 缓存。"""
        ConfigGenerator._cached_generate.cache_clear()

    def teardown_method(self):
        ConfigGenerator._cached_generate.cache_clear()

    def test_cache_hit_same_params(self):
        """相同参数第二次调用应命中缓存。"""
        # 第一次调用
        r1 = ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-01",
            enable_password="TestPass123",
            vlan_id=10,
            vlan_name="Sales",
        )
        info1 = ConfigGenerator._cached_generate.cache_info()
        # 第二次调用（相同参数）
        r2 = ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-01",
            enable_password="TestPass123",
            vlan_id=10,
            vlan_name="Sales",
        )
        info2 = ConfigGenerator._cached_generate.cache_info()
        # 结果相同
        assert r1 == r2
        # 缓存命中次数 +1
        assert info2.hits == info1.hits + 1
        # 缓存未命中次数不变
        assert info2.misses == info1.misses

    def test_cache_miss_different_params(self):
        """不同参数应产生新的缓存条目。"""
        ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-01",
            enable_password="TestPass123",
            vlan_id=10,
        )
        info1 = ConfigGenerator._cached_generate.cache_info()
        # 不同 hostname
        ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-02",
            enable_password="TestPass123",
            vlan_id=10,
        )
        info2 = ConfigGenerator._cached_generate.cache_info()
        # 未命中次数 +1
        assert info2.misses == info1.misses + 1

    def test_password_validation_not_cached(self):
        """密码校验失败返回错误提示，不进入缓存。"""
        # 密码过短
        r1 = ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-01",
            enable_password="short",
        )
        assert r1.startswith("# 密码长度必须至少8位")
        # 密码为空
        r2 = ConfigGenerator.generate_access_switch_config(
            vendor="ruijie",
            hostname="SW-ACCESS-01",
            enable_password="",
        )
        assert r2.startswith("# 必须提供enable特权密码")
        # 缓存未命中次数应为 0（校验失败不调用 _cached_generate）
        info = ConfigGenerator._cached_generate.cache_info()
        assert info.misses == 0

    def test_frozenset_kwargs_hashable(self):
        """frozenset(kwargs.items()) 可作为 lru_cache 的哈希键。"""
        # 验证 frozenset 可哈希
        kwargs = {"vendor": "ruijie", "hostname": "SW-01", "vlan_id": 10}
        frozen = frozenset(kwargs.items())
        # 应能作为字典键
        d = {frozen: "test"}
        assert d[frozen] == "test"
        # 相同内容产生相同 frozenset
        frozen2 = frozenset(kwargs.items())
        assert frozen == frozen2

    def test_all_four_vendors_cached(self):
        """四个厂商配置生成均走缓存。"""
        vendors = ["ruijie", "huawei", "h3c", "cisco"]
        for vendor in vendors:
            ConfigGenerator.generate_access_switch_config(
                vendor=vendor,
                hostname=f"SW-{vendor.upper()}-01",
                enable_password="TestPass123",
                vlan_id=10,
            )
        info = ConfigGenerator._cached_generate.cache_info()
        # 4 次未命中（每个厂商各一次）
        assert info.misses == 4

    def test_cache_info_available(self):
        """cache_info() 可正常调用，返回命名元组。"""
        info = ConfigGenerator._cached_generate.cache_info()
        assert hasattr(info, "hits")
        assert hasattr(info, "misses")
        assert hasattr(info, "maxsize")
        assert hasattr(info, "currsize")
        assert info.maxsize == 128
