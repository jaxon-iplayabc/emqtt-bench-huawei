#!/usr/bin/env python3
# 测试当前时间的设备认证

import sys
sys.path.append('./huawei')
from utils import get_client_id, get_password
from paho.mqtt import client as mqtt

device_id = "Speaker-000000001"
secret = "12345678"
host = "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
port = 1883

# 生成认证信息
client_id = get_client_id(device_id)
password = get_password(secret)

print(f"设备ID: {device_id}")
print(f"ClientID: {client_id}")
print(f"Username: {device_id}")
print(f"Password: {password}")

# 测试连接
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ 连接成功！")
    else:
        print(f"✗ 连接失败，错误码: {rc}")
    client.disconnect()

client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.username_pw_set(device_id, password)

print("\n测试连接...")
try:
    client.connect(host, port, keepalive=60)
    client.loop_forever()
except Exception as e:
    print(f"✗ 连接异常: {e}")
