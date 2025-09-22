#!/bin/bash
# 测试不同的连接方式

echo "=== 华为云连接测试 ==="
echo ""

HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
PORT="1883"
DEVICE_ID="Speaker-000000001"
SECRET="12345678"

echo "方法1：仅使用 -u 参数（向后兼容）"
echo "================================"
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u "$DEVICE_ID" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 100 \
    --limit 2 \
    --log_to console

echo ""
echo "如果上面失败，尝试不使用 Erlang 认证："
echo ""

echo "方法2：使用 Python 生成密码"
echo "=========================="
PASSWORD=$(python3 -c "from huawei.utils import get_password; print(get_password('$SECRET'))")
CLIENT_ID=$(python3 -c "from huawei.utils import get_client_id; print(get_client_id('$DEVICE_ID'))")

echo "生成的认证信息："
echo "  ClientID: $CLIENT_ID"
echo "  Password: $PASSWORD"
echo ""

./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u "$DEVICE_ID" \
    -P "$PASSWORD" \
    --clientid "$CLIENT_ID" \
    -s 100 \
    --limit 2 \
    --log_to console
