#!/bin/bash
# 测试 device_id 参数功能
# 作者: Jaxon
# 日期: 2024-11-18

echo "=== 测试 device_id 参数功能 ==="
echo ""

# 设置测试参数
HOST="${MQTT_HOST:-localhost}"
PORT="${MQTT_PORT:-1883}"

echo "测试配置："
echo "  MQTT服务器: $HOST:$PORT"
echo ""

echo "1. 使用默认行为（device_id = username）"
echo "   Topic: \$oc/devices/%d/sys/properties/report"
echo "   Username: Speaker-%i"
echo "   结果: device_id 将使用 'Speaker-%i'"
echo ""
echo "   命令示例："
echo "   ./emqtt_bench pub \\"
echo "       -h $HOST -p $PORT \\"
echo "       -c 3 -I 1000 \\"
echo "       -t '\$oc/devices/%d/sys/properties/report' \\"
echo "       -u 'Speaker-%i' \\"
echo "       -s 100 \\"
echo "       --limit 1"
echo ""

echo "2. 明确指定 device_id"
echo "   Topic: \$oc/devices/%d/sys/properties/report"
echo "   Username: user-%i"
echo "   Device ID: Device-%i"
echo "   结果: device_id 将使用 'Device-%i'"
echo ""
echo "   命令示例："
echo "   ./emqtt_bench pub \\"
echo "       -h $HOST -p $PORT \\"
echo "       -c 3 -I 1000 \\"
echo "       -t '\$oc/devices/%d/sys/properties/report' \\"
echo "       -u 'user-%i' \\"
echo "       --device-id 'Device-%i' \\"
echo "       -s 100 \\"
echo "       --limit 1"
echo ""

echo "3. 华为云场景示例"
echo "   结合 --huawei-auth 使用："
echo "   ./emqtt_bench pub \\"
echo "       -h mqtt.huaweicloud.com -p 1883 \\"
echo "       -c 100 -I 1000 \\"
echo "       -t '\$oc/devices/%d/sys/properties/report' \\"
echo "       -u 'Speaker-%i' \\"
echo "       -P 'huawei:12345678' \\"
echo "       --huawei-auth \\"
echo "       -s 256"
echo ""

echo "4. 所有支持的 Topic 变量："
echo "   %u - username"
echo "   %c - client ID"
echo "   %i - client sequence number"
echo "   %d - device ID (新增)"
echo "   %s - message sequence number (仅 pub)"
echo "   %rand_N - 随机数 (1 到 N)"
echo ""

echo "运行简单测试..."
# 测试1：默认行为
echo "测试1：device_id 默认使用 username"
./emqtt_bench pub \
    -h "$HOST" -p "$PORT" \
    -c 1 -I 1000 \
    -t 'test/devices/%d/data' \
    -u 'TestDevice-001' \
    -s 50 \
    --limit 1 \
    --log_to console &

PID1=$!
sleep 2
kill $PID1 2>/dev/null

echo ""
echo "测试2：明确指定 device_id"
./emqtt_bench pub \
    -h "$HOST" -p "$PORT" \
    -c 1 -I 1000 \
    -t 'test/devices/%d/data' \
    -u 'User-001' \
    --device-id 'Device-001' \
    -s 50 \
    --limit 1 \
    --log_to console &

PID2=$!
sleep 2
kill $PID2 2>/dev/null

echo ""
echo "测试完成！"
