#!/bin/bash
# 华为云 Device ID 使用示例
# 演示如何使用新的 %d 变量进行华为云 IoT 平台测试
# 作者: Jaxon
# 日期: 2024-11-18

echo "=== 华为云 Device ID 使用示例 ==="
echo ""

# 设置华为云参数
HUAWEI_HOST="${HUAWEI_IOT_HOST:-mqtt.huaweicloud.com}"
HUAWEI_PORT="${HUAWEI_IOT_PORT:-1883}"
DEVICE_PREFIX="${DEVICE_PREFIX:-Speaker}"
SECRET="${DEVICE_SECRET:-12345678}"

echo "华为云配置："
echo "  MQTT服务器: $HUAWEI_HOST:$HUAWEI_PORT"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  设备密钥: $SECRET"
echo ""

echo "示例 1：基本用法（device_id = username）"
echo "----------------------------------------"
cat << 'EOF'
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 10 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256

说明：
- %d 将被替换为 'Speaker-1', 'Speaker-2', ... 'Speaker-10'
- 实际 topic: $oc/devices/Speaker-1/sys/properties/report
EOF
echo ""

echo "示例 2：分离用户名和设备ID"
echo "----------------------------------------"
cat << 'EOF'
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'mqtt-user-%i' \
    --device-id 'SmartSpeaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://huawei_cloud_payload_template.json'

说明：
- 用户名: mqtt-user-1, mqtt-user-2, ...
- 设备ID: SmartSpeaker-1, SmartSpeaker-2, ...
- 实际 topic: $oc/devices/SmartSpeaker-1/sys/properties/report
EOF
echo ""

echo "示例 3：使用随机设备ID"
echo "----------------------------------------"
cat << 'EOF'
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 50 \
    -I 3000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'user-%i' \
    --device-id 'Device-%rand_1000' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --topics-payload huawei_cloud_topics.json

说明：
- 每个客户端的设备ID是随机的，范围 Device-1 到 Device-1000
- 适合模拟大量不同设备的场景
EOF
echo ""

echo "示例 4：订阅设备消息"
echo "----------------------------------------"
cat << 'EOF'
./emqtt_bench sub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 10 \
    -t '$oc/devices/%d/sys/messages/down' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -q 1

说明：
- 订阅每个设备的下行消息
- %d 被替换为对应的设备ID
EOF
echo ""

echo "示例 5：混合场景 - 多工厂多设备"
echo "----------------------------------------"
cat << 'EOF'
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 1000 \
    -I 10000 \
    -t 'factory/%rand_5/devices/%d/telemetry' \
    -u 'operator-%i' \
    --device-id 'sensor-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 512

说明：
- 模拟 5 个工厂，每个工厂有多个传感器
- topic 示例: factory/3/devices/sensor-1/telemetry
EOF
echo ""

echo "提示："
echo "1. %d 变量在 topic 中非常有用，特别是华为云要求的格式"
echo "2. device_id 可以独立于 username 设置，提供更大的灵活性"
echo "3. 结合 --huawei-auth 使用时，ClientID 会自动生成正确格式"
echo "4. 查看 DEVICE_ID_GUIDE.md 了解更多高级用法"
