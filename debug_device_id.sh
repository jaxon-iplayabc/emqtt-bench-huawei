#!/bin/bash
# 调试 device_id 参数问题

echo "=== 调试 Device ID 参数 ==="
echo ""

echo "1. 使用 -u 参数（成功）："
echo "========================"
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --limit 1 \
    --log_to console

echo ""
echo "2. 使用 --device-id 参数（失败）："
echo "================================"
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --limit 1 \
    --log_to console

echo ""
echo "3. 使用两者结合（测试优先级）："
echo "==============================="
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'fake-device' \
    --device-id 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --limit 1 \
    --log_to console
