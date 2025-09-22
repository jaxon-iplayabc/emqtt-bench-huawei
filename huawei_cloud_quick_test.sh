#!/bin/bash
# 华为云 IoT 平台快速测试脚本
# 作者: Jaxon
# 日期: 2024-11-18

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 华为云 IoT 平台性能测试 ===${NC}"
echo ""

# 默认参数
HOST="${HUAWEI_IOT_HOST:-localhost}"
PORT="${HUAWEI_IOT_PORT:-1883}"
DEVICE_PREFIX="${DEVICE_PREFIX:-Speaker}"
SECRET="${DEVICE_SECRET:-12345678}"
CLIENT_COUNT="${CLIENT_COUNT:-10}"
MSG_INTERVAL="${MSG_INTERVAL:-1000}"

# 显示配置
echo -e "${YELLOW}测试配置:${NC}"
echo "  MQTT服务器: $HOST:$PORT"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  客户端数量: $CLIENT_COUNT"
echo "  消息间隔: ${MSG_INTERVAL}ms"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3${NC}"
    exit 1
fi

# 生成测试 payload
echo -e "${YELLOW}生成测试数据...${NC}"
cd huawei
python3 payload_generator.py > /dev/null 2>&1
cd ..

# 运行测试
echo -e "${GREEN}开始测试...${NC}"
echo ""

# 方法1: 使用 emqtt_bench 原生命令
echo -e "${YELLOW}方法1: 使用 topics_payload 配置${NC}"
./emqtt_bench pub \
    -h "$HOST" \
    -p "$PORT" \
    -c "$CLIENT_COUNT" \
    -i 10 \
    --topics-payload huawei_cloud_topics.json \
    --prefix "$DEVICE_PREFIX" \
    -u "$DEVICE_PREFIX-%i" \
    -P "$(python3 -c "from huawei.utils import get_password; print(get_password('$SECRET'))")" \
    --log_to console

# 提示其他测试方法
echo ""
echo -e "${GREEN}测试完成！${NC}"
echo ""
echo -e "${YELLOW}更多测试选项:${NC}"
echo "1. 使用 Python 脚本进行动态测试:"
echo "   cd huawei && python3 run_huawei_cloud_test.py --host $HOST --device-prefix $DEVICE_PREFIX -c 100"
echo ""
echo "2. 启用 SSL/TLS:"
echo "   添加 --ssl --cacertfile /path/to/ca.pem"
echo ""
echo "3. 启用性能监控:"
echo "   添加 --prometheus --restapi 8080"
echo ""
echo "4. 查看详细指南:"
echo "   cat HUAWEI_CLOUD_TEST_GUIDE.md"
