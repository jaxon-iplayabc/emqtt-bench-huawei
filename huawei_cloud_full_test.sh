#!/bin/bash
# 华为云 IoT 平台完整测试示例
# 作者: Jaxon
# 日期: 2024-11-18

echo "=== 华为云 IoT 平台性能测试 ==="
echo ""

# 华为云配置
HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
PORT="1883"
DEVICE_PREFIX="Speaker"
SECRET="12345678"

echo "服务器配置："
echo "  地址: $HOST:$PORT"
echo "  设备前缀: $DEVICE_PREFIX"
echo ""

echo "测试 1：单设备测试（验证连接）"
echo "=============================="
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 3000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u "${DEVICE_PREFIX}-000000001" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 256 \
    --limit 5 \
    --log_to console

echo ""
echo "测试 2：10个设备并发测试"
echo "======================="
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 10 \
    -i 100 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "${DEVICE_PREFIX}-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 512 \
    --limit 10

echo ""
echo "测试 3：使用真实 payload（100个设备）"
echo "===================================="
# 生成测试 payload
cd huawei
python3 payload_generator.py > /dev/null 2>&1
cd ..

./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 100 \
    -i 10 \
    -I 10000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "${DEVICE_PREFIX}-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --message 'template://huawei/huawei_cloud_payload_example.json' \
    --limit 5 \
    -q 1

echo ""
echo "测试 4：启用性能监控（50个设备）"
echo "==============================="
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 50 \
    -i 20 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "${DEVICE_PREFIX}-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 1024 \
    --limit 20 \
    --prometheus \
    --qoe true \
    --log_to console

echo ""
echo "测试 5：订阅测试（5个设备）"
echo "=========================="
./emqtt_bench sub \
    -h "$HOST" \
    -p "$PORT" \
    -c 5 \
    -i 200 \
    -t '$oc/devices/%d/sys/messages/down' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "${DEVICE_PREFIX}-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -q 1 &

SUB_PID=$!
echo "订阅进程 PID: $SUB_PID"
echo "运行30秒后停止..."
sleep 30
kill $SUB_PID 2>/dev/null

echo ""
echo "所有测试完成！"
echo ""
echo "测试总结："
echo "- ✓ 单设备连接测试"
echo "- ✓ 多设备并发测试"
echo "- ✓ 真实 payload 测试"
echo "- ✓ 性能监控测试"
echo "- ✓ 订阅功能测试"
echo ""
echo "提示："
echo "1. 设备ID格式：${DEVICE_PREFIX}-XXXXXXXXX（9位数字）"
echo "2. 使用 --huawei-auth 自动处理认证"
echo "3. 使用 %d 表示 device_id，%u 表示 username"
echo "4. 在华为云认证模式下，username 会自动使用 device_id"
