#!/usr/bin/env python3
# 调试 prefix 生成的设备ID

import sys
sys.path.append('./huawei')
from utils import get_client_id, get_password

# 测试不同的设备ID格式
test_cases = [
    ("Speaker-000000001", "正确的9位数字格式"),
    ("Speaker-1", "错误的1位数字格式"),
    ("Speaker-000000000", "9位但从0开始"),
]

for device_id, description in test_cases:
    print(f"\n测试 {description}:")
    print(f"  设备ID: {device_id}")
    
    try:
        client_id = get_client_id(device_id)
        password = get_password("12345678")
        print(f"  ClientID: {client_id}")
        print(f"  Password: {password[:40]}...")
        print("  ✓ 生成成功")
    except Exception as e:
        print(f"  ✗ 生成失败: {e}")

print("\n结论：设备ID必须遵循华为云的格式要求")
