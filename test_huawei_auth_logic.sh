#!/bin/bash
# 测试华为云认证逻辑
# 验证 username 是否正确使用 device_id

echo "=== 华为云认证逻辑测试 ==="
echo ""
echo "华为云要求：MQTT username 必须是 device_id"
echo ""

# 测试服务器（使用本地或测试环境）
HOST="${TEST_HOST:-localhost}"
PORT="${TEST_PORT:-1883}"

echo "测试 1：仅使用 -u 参数（向后兼容）"
echo "----------------------------------------"
echo "命令："
echo "./emqtt_bench pub \\"
echo "    -h $HOST -p $PORT \\"
echo "    -c 1 -I 1000 \\"
echo "    -t '\$oc/devices/%u/sys/properties/report' \\"
echo "    -u 'TestDevice-001' \\"
echo "    -P 'huawei:12345678' \\"
echo "    --huawei-auth \\"
echo "    -s 50 --limit 1"
echo ""
echo "预期结果："
echo "- MQTT username = TestDevice-001"
echo "- MQTT clientid = TestDevice-001_0_0_<timestamp>"
echo "- Topic = \$oc/devices/TestDevice-001/sys/properties/report"
echo ""

# 运行测试
./emqtt_bench pub \
    -h "$HOST" -p "$PORT" \
    -c 1 -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'TestDevice-001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 50 --limit 1 \
    --log_to console &

PID1=$!
sleep 2
kill $PID1 2>/dev/null

echo ""
echo "测试 2：使用 --device-id 参数（推荐方式）"
echo "----------------------------------------"
echo "命令："
echo "./emqtt_bench pub \\"
echo "    -h $HOST -p $PORT \\"
echo "    -c 1 -I 1000 \\"
echo "    -t '\$oc/devices/%d/sys/properties/report' \\"
echo "    --device-id 'SmartSpeaker-001' \\"
echo "    -P 'huawei:12345678' \\"
echo "    --huawei-auth \\"
echo "    -s 50 --limit 1"
echo ""
echo "预期结果："
echo "- MQTT username = SmartSpeaker-001（自动使用 device_id）"
echo "- MQTT clientid = SmartSpeaker-001_0_0_<timestamp>"
echo "- Topic = \$oc/devices/SmartSpeaker-001/sys/properties/report"
echo ""

# 运行测试
./emqtt_bench pub \
    -h "$HOST" -p "$PORT" \
    -c 1 -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'SmartSpeaker-001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 50 --limit 1 \
    --log_to console &

PID2=$!
sleep 2
kill $PID2 2>/dev/null

echo ""
echo "测试 3：验证 %u 和 %d 在华为认证时的行为"
echo "----------------------------------------"
echo "命令："
echo "./emqtt_bench pub \\"
echo "    -h $HOST -p $PORT \\"
echo "    -c 1 -I 1000 \\"
echo "    -t 'test/%u/device/%d/data' \\"
echo "    -u 'ignored-username' \\"
echo "    --device-id 'ActualDevice-001' \\"
echo "    -P 'huawei:12345678' \\"
echo "    --huawei-auth \\"
echo "    -s 50 --limit 1"
echo ""
echo "预期结果："
echo "- MQTT username = ActualDevice-001（使用 device_id，忽略 -u）"
echo "- Topic 中 %u = ActualDevice-001（因为 username 被替换为 device_id）"
echo "- Topic 中 %d = ActualDevice-001"
echo "- 最终 Topic = test/ActualDevice-001/device/ActualDevice-001/data"
echo ""

# 运行测试
./emqtt_bench pub \
    -h "$HOST" -p "$PORT" \
    -c 1 -I 1000 \
    -t 'test/%u/device/%d/data' \
    -u 'ignored-username' \
    --device-id 'ActualDevice-001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 50 --limit 1 \
    --log_to console &

PID3=$!
sleep 2
kill $PID3 2>/dev/null

echo ""
echo "测试完成！"
echo ""
echo "重要说明："
echo "1. 使用 --huawei-auth 时，MQTT username 总是等于 device_id"
echo "2. 如果指定了 --device-id，会使用它的值"
echo "3. 如果没有指定 --device-id，会使用 -u 的值作为 device_id"
echo "4. 这确保了符合华为云的认证要求"
