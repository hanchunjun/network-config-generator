import ipaddress
import re
from typing import Tuple, Optional, List

class IPValidator:
    """IP地址验证器"""

    @staticmethod
    def validate_ip(ip_str: str) -> Tuple[bool, Optional[str]]:
        """
        验证IP地址的有效性

        返回:
            (是否有效, 错误消息)
        """
        if not ip_str:
            return False, "IP地址不能为空"

        # 检查格式
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, ip_str):
            return False, "IP地址格式不正确，请输入如 192.168.1.1"

        # 检查前导零
        parts = ip_str.split(".")
        for part in parts:
            if len(part) > 1 and part.startswith("0"):
                return False, f"IP地址段 '{part}' 包含无效的前导零"

            try:
                value = int(part)
                if not (0 <= value <= 255):
                    return False, f"IP地址段 '{part}' 超出范围(0-255)"
            except ValueError:
                return False, f"IP地址段 '{part}' 不是有效的数字"

        # 检查保留地址
        try:
            ip_obj = ipaddress.IPv4Address(ip_str)
            if ip_obj.is_loopback:
                return False, "不能使用回环地址(127.0.0.1)"
            elif ip_obj.is_multicast:
                return False, "不能使用组播地址"
            elif ip_obj.is_reserved:
                return False, "不能使用保留地址"
        except ipaddress.AddressValueError as e:
            return False, f"IP地址无效: {str(e)}"

        return True, None


class DeviceValidator:
    """设备信息验证器"""

    @staticmethod
    def validate_device_data(device_data: dict, existing_ips: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        验证设备数据

        Args:
            device_data: 设备数据字典
            existing_ips: 现有IP列表（用于检查重复）

        Returns:
            (是否有效, 错误消息)
        """
        if existing_ips is None:
            existing_ips = []

        # 验证IP地址
        ip = device_data.get("ip", "")
        is_valid, error = IPValidator.validate_ip(ip)
        if not is_valid:
            return False, error

        # 检查IP是否重复
        if ip in existing_ips:
            return False, f"IP地址 {ip} 已存在，请勿重复添加"

        # 验证厂商
        vendor = device_data.get("vendor", "")
        valid_vendors = ["锐捷", "华为", "H3C", "思科"]
        if vendor not in valid_vendors:
            return False, f"厂商 '{vendor}' 不在支持列表中"

        # 验证设备类型
        device_type = device_data.get("device_type", "")
        valid_types = ["核心交换机", "接入交换机", "路由器", "AC控制器", "防火墙", "负载均衡", "服务器"]
        if device_type not in valid_types:
            return False, f"设备类型 '{device_type}' 不在支持列表中"

        # 验证用户名
        username = device_data.get("username", "")
        if not username:
            return False, "用户名不能为空"
        if len(username) > 64:
            return False, "用户名长度不能超过64个字符"

        # 验证协议
        protocol = device_data.get("protocol", "")
        valid_protocols = ["ssh", "telnet"]
        if protocol not in valid_protocols:
            return False, f"协议 '{protocol}' 不支持"

        # 验证密码（可选，但为空时警告）
        password = device_data.get("password", "")
        if not password:
            # 密码为空，但允许继续（调用者决定是否确认）
            pass

        return True, None


class ProjectValidator:
    """项目验证器"""

    @staticmethod
    def validate_project_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        验证项目名称

        Returns:
            (是否有效, 错误消息)
        """
        if not name:
            return False, "项目名称不能为空"

        if len(name) < 2:
            return False, "项目名称至少需要2个字符"

        if len(name) > 50:
            return False, "项目名称不能超过50个字符"

        # 检查非法字符
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            if char in name:
                return False, f"项目名称不能包含非法字符 '{char}'"

        return True, None

    @staticmethod
    def validate_project_path(path: str) -> Tuple[bool, Optional[str]]:
        """
        验证项目路径（防止路径遍历攻击）

        Returns:
            (是否有效, 错误消息)
        """
        if not path:
            return False, "项目路径不能为空"

        # 防止路径遍历攻击
        if ".." in path:
            return False, "路径不能包含 '..'（防止路径遍历）"

        # 防止符号链接攻击
        try:
            real_path = os.path.realpath(path)
            # 确保解析后的路径不包含 ..
            if ".." in real_path:
                return False, "路径包含无效的符号链接"
        except Exception:
            pass

        try:
            import os
            # 检查路径是否存在
            if os.path.exists(path):
                if not os.path.isdir(path):
                    return False, "路径不是目录"
                if not os.access(path, os.W_OK):
                    return False, "目录不可写"

            # 检查路径格式
            if len(path) > 260:
                return False, "路径长度不能超过260个字符"

            return True, None
        except Exception as e:
            return False, f"路径验证失败: {str(e)}"