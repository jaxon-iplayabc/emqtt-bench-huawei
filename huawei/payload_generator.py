#!/usr/bin/env python3
# coding=utf-8

import json
import random
import time
from datetime import datetime

def generate_huawei_cloud_payload():
    """
    生成华为云设备属性上报的payload
    """
    
    # WiFi SSID 列表
    wifi_ssids = [
        "TP-LINK_BBB3", "TP-LINK_AAA1", "TP-LINK_CCC2", "HUAWEI_WIFI",
        "XIAOMI_ROUTER", "NETGEAR_5G", "ASUS_AC68U", "LINKSYS_E4200",
        "D-LINK_DIR", "TENDA_AC15", "MERCURY_MW", "FAST_FW"
    ]
    
    # 获取当前时间戳（华为云格式：YYYYMMDDTHHmmSSZ）
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    payload = [
        {
            "serviceId": "BasicData",
            "properties": {
                "battery": {
                    "electricity": random.randint(20, 100),
                    "charging": random.choice([True, False])
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "storage": {
                    "sd_free": random.randint(1000, 4000),
                    "sd_total": random.randint(3000, 4000)
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "settings": {
                    "autoUpgrade": random.choice([True, False]),
                    "log": random.choice([True, False]),
                    "vol": random.randint(0, 15)
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "report_file": {
                    "num": random.randint(0, 10)
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "wifi": {
                    "rssi": random.randint(-80, -30),
                    "ssid": random.choice(wifi_ssids)
                }
            },
            "eventTime": timestamp
        },
        {
            "serviceId": "BasicData",
            "properties": {
                "playing": {
                    "id": random.randint(100000000, 999999999),
                    "current": random.randint(0, 500),
                    "total": random.randint(100, 500)
                }
            },
            "eventTime": timestamp
        }
    ]
    
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':'))


def save_payload_template():
    """
    保存一个示例payload到文件，用于emqtt_bench的template功能
    """
    # 生成一个示例
    payload = generate_huawei_cloud_payload()
    
    with open('huawei_cloud_payload_example.json', 'w', encoding='utf-8') as f:
        f.write(payload)
    
    print(f"示例payload已保存到: huawei_cloud_payload_example.json")
    print(f"Payload大小: {len(payload)} 字节")
    

if __name__ == "__main__":
    # 生成示例
    example_payload = generate_huawei_cloud_payload()
    print("生成的示例Payload:")
    print(json.dumps(json.loads(example_payload), indent=2, ensure_ascii=False))
    
    # 保存到文件
    save_payload_template()
