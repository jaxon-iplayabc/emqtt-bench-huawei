#!/bin/bash
# 华为云 Erlang 认证功能演示脚本
# 作者: Jaxon
# 日期: 2024-11-18

echo "=== 华为云 Erlang 认证功能演示 ==="
echo ""

# 设置默认参数
HOST="${HUAWEI_IOT_HOST:-localhost}"
PORT="${HUAWEI_IOT_PORT:-1883}"
DEVICE_PREFIX="${DEVICE_PREFIX:-Speaker}"
SECRET="${DEVICE_SECRET:-12345678}"

echo "配置信息："
echo "  MQTT服务器: $HOST:$PORT"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  设备密钥: $SECRET"
echo ""

echo "1. 使用 Erlang 原生认证（推荐）"
echo "   命令示例："
echo "   ./emqtt_bench pub \\"
echo "       -h $HOST \\"
echo "       -p $PORT \\"
echo "       -c 10 \\"
echo "       -I 1000 \\"
echo "       -t '\$oc/devices/%u/sys/properties/report' \\"
echo "       -u '$DEVICE_PREFIX-%i' \\"
echo "       -P 'huawei:$SECRET' \\"
echo "       --huawei-auth \\"
echo "       -s 256"
echo ""

echo "2. 对比：使用 Python 生成密码（传统方式）"
echo "   密码生成："
echo "   python3 -c \"from huawei.utils import get_password; print(get_password('$SECRET'))\""
echo ""

echo "3. 运行简单测试："
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u "$DEVICE_PREFIX-%i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 100 \
    --limit 5 \
    --log_to console

echo ""
echo "测试完成！"
echo ""
echo "提示："
echo "- 使用 --huawei-auth 启用华为云认证"
echo "- 密码格式: -P 'huawei:<设备密钥>'"
echo "- 支持 %i、%u、%c 等变量"
echo "- 查看更多信息: cat HUAWEI_ERLANG_AUTH_GUIDE.md"
