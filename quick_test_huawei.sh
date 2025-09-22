#!/bin/bash
# 华为云快速测试脚本
# 测试单个设备的连接和消息发送

echo "=== 华为云单设备快速测试 ==="
echo ""

# 华为云参数
HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
PORT="1883"
DEVICE_ID="Speaker-000000001"
SECRET="12345678"

echo "测试配置："
echo "  服务器: $HOST:$PORT"
echo "  设备ID: $DEVICE_ID"
echo ""

# 生成测试时间戳
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "1. 基本连接测试"
echo "==============="
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 2000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id "$DEVICE_ID" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 100 \
    --limit 5 \
    --log_to console

echo ""
echo "2. 发送真实设备数据"
echo "=================="

# 创建一个简单的测试 payload
cat > test_payload.json << EOF
[
    {
        "serviceId": "BasicData",
        "properties": {
            "battery": {
                "electricity": 85,
                "charging": false
            }
        },
        "eventTime": "$(date -u +%Y%m%dT%H%M%SZ)"
    },
    {
        "serviceId": "BasicData",
        "properties": {
            "wifi": {
                "rssi": -65,
                "ssid": "TestNetwork"
            }
        },
        "eventTime": "$(date -u +%Y%m%dT%H%M%SZ)"
    }
]
EOF

echo "使用自定义 payload 发送消息..."
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 3000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id "$DEVICE_ID" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --message 'template://test_payload.json' \
    --limit 3 \
    -q 1 \
    --log_to console

# 清理临时文件
rm -f test_payload.json

echo ""
echo "测试完成！"
echo ""
echo "如果看到 'connect_succ' 和 'pub' 计数，说明连接成功并发送了消息。"
echo "如果看到 'connect_fail'，请检查："
echo "- 设备是否已在华为云平台注册"
echo "- 设备密钥是否正确"
echo "- 网络连接是否正常"
