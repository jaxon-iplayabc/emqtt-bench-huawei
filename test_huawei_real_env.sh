#!/bin/bash
# 华为云真实环境测试脚本
# 使用用户提供的华为云 IoT 平台信息进行测试

echo "=== 华为云 IoT 平台真实环境测试 ==="
echo ""

# 华为云环境参数
HUAWEI_HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
HUAWEI_PORT="1883"
DEVICE_PREFIX="Speaker"
DEVICE_SECRET="12345678"

echo "华为云配置信息："
echo "  服务器: $HUAWEI_HOST"
echo "  端口: $HUAWEI_PORT"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  设备密钥: $DEVICE_SECRET"
echo ""

echo "测试 1：单个设备连接测试"
echo "========================="
echo "设备ID: Speaker-000000001"
echo ""

./emqtt_bench pub \
    -h "$HUAWEI_HOST" \
    -p "$HUAWEI_PORT" \
    -c 1 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'Speaker-000000001' \
    -P "huawei:$DEVICE_SECRET" \
    --huawei-auth \
    -s 256 \
    --limit 3 \
    --log_to console

echo ""
echo "测试 2：多设备并发测试（10个设备）"
echo "================================="
echo "设备ID: Speaker-000000001 到 Speaker-000000010"
echo ""

./emqtt_bench pub \
    -h "$HUAWEI_HOST" \
    -p "$HUAWEI_PORT" \
    -c 10 \
    -i 100 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "$DEVICE_PREFIX-%09.9i" \
    -P "huawei:$DEVICE_SECRET" \
    --huawei-auth \
    -s 256 \
    --limit 5

echo ""
echo "测试 3：使用真实的华为云 payload"
echo "================================"
echo "发送符合华为云格式的设备属性数据"
echo ""

# 先生成 payload 文件
cd huawei
python3 payload_generator.py > /dev/null 2>&1
cd ..

./emqtt_bench pub \
    -h "$HUAWEI_HOST" \
    -p "$HUAWEI_PORT" \
    -c 5 \
    -i 200 \
    -I 10000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "$DEVICE_PREFIX-%09.9i" \
    -P "huawei:$DEVICE_SECRET" \
    --huawei-auth \
    --message 'template://huawei/huawei_cloud_payload_example.json' \
    --limit 3

echo ""
echo "测试 4：性能基准测试（100个设备）"
echo "================================"
echo "模拟100个设备同时上报数据"
echo ""

./emqtt_bench pub \
    -h "$HUAWEI_HOST" \
    -p "$HUAWEI_PORT" \
    -c 100 \
    -i 10 \
    -I 30000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "$DEVICE_PREFIX-%09.9i" \
    -P "huawei:$DEVICE_SECRET" \
    --huawei-auth \
    -s 512 \
    --limit 10 \
    --prometheus \
    --qoe true

echo ""
echo "测试 5：订阅下行消息"
echo "===================="
echo "订阅设备的下行消息"
echo ""

./emqtt_bench sub \
    -h "$HUAWEI_HOST" \
    -p "$HUAWEI_PORT" \
    -c 5 \
    -i 100 \
    -t '$oc/devices/%d/sys/messages/down' \
    --prefix "$DEVICE_PREFIX" \
    --device-id "$DEVICE_PREFIX-%09.9i" \
    -P "huawei:$DEVICE_SECRET" \
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
echo "注意事项："
echo "1. 确保设备已在华为云 IoT 平台注册"
echo "2. 设备ID格式为 ${DEVICE_PREFIX}-XXXXXXXXX（9位数字）"
echo "3. 如遇到认证失败，请检查："
echo "   - 设备是否已注册"
echo "   - 密钥是否正确"
echo "   - 系统时间是否准确（误差不超过1小时）"
