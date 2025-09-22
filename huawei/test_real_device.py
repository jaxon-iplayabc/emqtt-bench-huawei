#!/usr/bin/env python3
# coding=utf-8
"""
华为云 IoT 平台真实设备测试
使用 Python 直接测试设备连接
"""

import sys
import json
from datetime import datetime
from paho.mqtt import client as mqtt
from utils import get_client_id, get_password

# 华为云配置
MQTT_SERVER = '016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com'
MQTT_PORT = 1883
DEVICE_ID = 'Speaker-000000001'
DEVICE_SECRET = '12345678'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ 设备连接成功！")
        print(f"  设备ID: {DEVICE_ID}")
        print(f"  服务器: {MQTT_SERVER}:{MQTT_PORT}")
        
        # 订阅下行消息
        topic = f"$oc/devices/{DEVICE_ID}/sys/messages/down"
        client.subscribe(topic, qos=1)
        print(f"✓ 已订阅主题: {topic}")
    else:
        print(f"✗ 连接失败，错误码: {rc}")
        print(f"  错误说明: {get_error_message(rc)}")

def on_disconnect(client, userdata, rc):
    print(f"设备断开连接，代码: {rc}")

def on_publish(client, userdata, mid):
    print(f"✓ 消息发送成功 (消息ID: {mid})")

def on_message(client, userdata, msg):
    print(f"收到下行消息:")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode('utf-8')}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"订阅确认 (QoS: {granted_qos})")

def get_error_message(rc):
    errors = {
        1: "协议版本不正确",
        2: "客户端标识符无效",
        3: "服务器不可用",
        4: "用户名或密码错误",
        5: "未授权"
    }
    return errors.get(rc, "未知错误")

def create_test_payload():
    """创建测试数据"""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return json.dumps([
        {
            "serviceId": "BasicData",
            "properties": {
                "battery": {
                    "electricity": 75,
                    "charging": True
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "wifi": {
                    "rssi": -55,
                    "ssid": "HuaweiTest"
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "settings": {
                    "autoUpgrade": True,
                    "log": True,
                    "vol": 10
                }
            },
            "eventTime": timestamp
        }
    ], ensure_ascii=False)

def main():
    print("=== 华为云 IoT 设备测试 ===")
    print(f"服务器: {MQTT_SERVER}:{MQTT_PORT}")
    print(f"设备ID: {DEVICE_ID}")
    
    # 生成认证信息
    client_id = get_client_id(DEVICE_ID)
    password = get_password(DEVICE_SECRET)
    
    print(f"\n认证信息:")
    print(f"  ClientID: {client_id}")
    print(f"  Username: {DEVICE_ID}")
    print(f"  Password: {password[:20]}...")
    
    # 创建 MQTT 客户端
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    
    # 设置用户名和密码
    client.username_pw_set(DEVICE_ID, password)
    
    # 连接服务器
    print(f"\n连接到服务器...")
    try:
        client.connect(MQTT_SERVER, MQTT_PORT, keepalive=120)
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 启动循环
    client.loop_start()
    
    # 等待连接完成
    import time
    time.sleep(2)
    
    # 发送测试数据
    topic = f"$oc/devices/{DEVICE_ID}/sys/properties/report"
    print(f"\n发送测试数据到: {topic}")
    
    for i in range(5):
        payload = create_test_payload()
        result = client.publish(topic, payload, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"  第 {i+1} 条消息已发送")
        else:
            print(f"  第 {i+1} 条消息发送失败")
        time.sleep(3)
    
    # 保持连接一段时间以接收可能的下行消息
    print("\n等待下行消息（30秒）...")
    time.sleep(30)
    
    # 断开连接
    client.loop_stop()
    client.disconnect()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
