#!/bin/bash

# 华为云发布测试脚本
# 专门用于测试华为云发布功能

echo "🚀 华为云发布测试脚本"
echo "===================="

# 检查必要文件
if [ ! -f "emqtt_bench" ]; then
    echo "❌ emqtt_bench 可执行文件不存在"
    exit 1
fi

if [ ! -f "huawei_cloud_payload_template.json" ]; then
    echo "❌ 华为云模板文件不存在"
    exit 1
fi

# 读取配置
CONFIG_FILE="emqtt_test_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 提取配置参数
HOST=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('host', 'localhost'))")
PORT=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('port', 1883))")
CLIENT_COUNT=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('client_count', 10))")
MSG_INTERVAL=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('msg_interval', 500))")
DEVICE_PREFIX=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('device_prefix', 'speaker'))")
DEVICE_SECRET=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('huawei_secret', ''))")
PROMETHEUS_PORT=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('prometheus_port', 9090))")

echo "📋 测试参数:"
echo "  - 服务器: $HOST:$PORT"
echo "  - 客户端数量: $CLIENT_COUNT"
echo "  - 消息间隔: ${MSG_INTERVAL}ms"
echo "  - 设备前缀: $DEVICE_PREFIX"
echo "  - Prometheus端口: $((PROMETHEUS_PORT + 1))"

# 构建测试命令
CMD="./emqtt_bench pub -h $HOST -p $PORT -c $CLIENT_COUNT -i 10 -I $MSG_INTERVAL -q 1"
CMD="$CMD -t '\$oc/devices/%d/sys/properties/report'"
CMD="$CMD --prefix '$DEVICE_PREFIX' -P '$DEVICE_SECRET' --huawei-auth"
CMD="$CMD --message 'template://$(pwd)/huawei_cloud_payload_template.json'"
CMD="$CMD --prometheus --restapi $((PROMETHEUS_PORT + 1)) --qoe true"

echo ""
echo "🔧 执行命令:"
echo "$CMD"
echo ""

# 执行测试
eval $CMD

echo ""
echo "✅ 华为云发布测试完成"
