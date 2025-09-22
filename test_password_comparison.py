#!/usr/bin/env python3
# 测试密码生成的详细过程

import sys
import hmac
import hashlib
sys.path.append('./huawei')
from utils import get_timeStamp, get_password

secret = "12345678"
timestamp = get_timeStamp()

print("=== Python 密码生成过程 ===")
print(f"设备密钥: {secret}")
print(f"时间戳: {timestamp}")

# 手动计算密码
secret_key = timestamp.encode('utf-8')
secret_bytes = secret.encode('utf-8')
password_hmac = hmac.new(secret_key, secret_bytes, digestmod=hashlib.sha256)
password_hex = password_hmac.hexdigest()

print(f"密钥字节: {secret_key}")
print(f"秘密字节: {secret_bytes}")
print(f"HMAC 结果: {password_hex}")

# 使用 utils 函数
utils_password = get_password(secret)
print(f"\nutils.get_password 结果: {utils_password}")
print(f"两者是否相等: {password_hex == utils_password}")
