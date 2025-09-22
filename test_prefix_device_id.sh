#!/bin/bash
# 测试使用 --prefix 参数设置设备ID前缀

echo "=== 测试 --prefix 参数用于华为云设备ID ==="
echo ""

HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
PORT="1883"
SECRET="12345678"

echo "测试 1：仅使用 --prefix 参数"
echo "============================="
echo "期望：设备ID = Speaker-000000001"
echo ""
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --limit 3 \
    --log_to console

echo ""
echo "测试 2：使用 --prefix 多设备"
echo "=========================="
echo "期望：设备ID = Speaker-000000001 到 Speaker-000000005"
echo ""
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 5 \
    -i 200 \
    -I 2000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 256 \
    --limit 2

echo ""
echo "测试 3：同时使用 --prefix 和 -u（验证优先级）"
echo "=========================================="
echo "期望：username 优先，设备ID = TestDevice-000000001"
echo ""
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -u "TestDevice-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --limit 2 \
    --log_to console

echo ""
echo "测试 4：都不指定（默认格式）"
echo "========================="
echo "期望：设备ID = device-000000001"
echo ""
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --limit 2 \
    --log_to console

echo ""
echo "测试完成！"
echo ""
echo "总结："
echo "1. --prefix 参数可以用于设置华为云设备ID前缀"
echo "2. 优先级：-u (username) > --prefix > 默认格式"
echo "3. 设备ID格式：{prefix}-{9位数字}"
