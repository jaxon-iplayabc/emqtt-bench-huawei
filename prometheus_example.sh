#!/bin/bash
# eMQTT-Bench Prometheus 监控示例脚本
# 作者: Jaxon
# 日期: 2024-12-19

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== eMQTT-Bench Prometheus 监控示例 ===${NC}"
echo ""

# 交互式选择测试类型
show_menu() {
    echo -e "${YELLOW}请选择要运行的测试类型:${NC}"
    echo "1) 连接测试 (Connection Test)"
    echo "2) 发布测试 (Publish Test)"
    echo "3) 订阅测试 (Subscribe Test)"
    echo "4) 华为云 IoT 平台测试 (Huawei Cloud IoT Test)"
    echo "5) 运行所有测试 (Run All Tests)"
    echo "6) 自定义测试 (Custom Test)"
    echo "0) 退出 (Exit)"
    echo ""
}

# 获取用户选择
get_user_choice() {
    while true; do
        show_menu
        read -p "请输入选择 (0-6): " choice
        case $choice in
            1|2|3|4|5|6|0)
                return $choice
                ;;
            *)
                echo -e "${RED}无效选择，请输入 0-6 之间的数字${NC}"
                echo ""
                ;;
        esac
    done
}

# 配置参数
HOST="${MQTT_HOST:-016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com}"
PORT="${MQTT_PORT:-1883}"
CLIENT_COUNT="${CLIENT_COUNT:-5}"
MSG_INTERVAL="${MSG_INTERVAL:-1000}"
PROMETHEUS_PORT="${PROMETHEUS_PORT:-8080}"

# 华为云配置参数
HUAWEI_HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
HUAWEI_SECRET="12345678"
DEVICE_PREFIX="speaker"

echo -e "${YELLOW}配置参数:${NC}"
echo "  MQTT服务器: $HOST:$PORT"
echo "  客户端数量: $CLIENT_COUNT"
echo "  消息间隔: ${MSG_INTERVAL}ms"
echo "  Prometheus端口: $PROMETHEUS_PORT"
echo ""
echo -e "${YELLOW}华为云配置:${NC}"
echo "  华为云服务器: $HUAWEI_HOST"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  设备密钥: $HUAWEI_SECRET"
echo ""

# 检查 emqtt_bench 是否存在
if [ ! -f "./emqtt_bench" ]; then
    echo -e "${RED}错误: 未找到 emqtt_bench 可执行文件${NC}"
    echo "请确保在项目根目录下运行此脚本"
    exit 1
fi

# 函数：启动压测并监控
start_benchmark_with_monitoring() {
    local test_name="$1"
    local test_cmd="$2"
    local duration="$3"
    
    echo -e "${BLUE}开始测试: $test_name${NC}"
    echo "命令: $test_cmd"
    echo "持续时间: ${duration}秒"
    echo ""
    
    # 启动压测
    eval "$test_cmd" &
    local bench_pid=$!
    
    # 等待指定时间
    sleep "$duration"
    
    # 停止压测
    kill $bench_pid 2>/dev/null
    wait $bench_pid 2>/dev/null
    
    echo -e "${GREEN}测试 $test_name 完成${NC}"
    echo ""
}

# 函数：收集 Prometheus 指标
collect_metrics() {
    local test_name="$1"
    local port="$2"
    
    echo -e "${YELLOW}收集 $test_name 的指标数据...${NC}"
    
    # 等待指标稳定
    sleep 2
    
    # 获取指标数据
    local metrics_file="metrics_${test_name}_$(date +%Y%m%d_%H%M%S).txt"
    curl -s "http://localhost:$port/metrics" > "$metrics_file"
    
    if [ -f "$metrics_file" ] && [ -s "$metrics_file" ]; then
        echo "指标数据已保存到: $metrics_file"
        
        # 显示关键指标
        echo -e "${BLUE}关键指标摘要:${NC}"
        grep -E '^mqtt_bench_(connected|publish_sent|publish_failed|connect_failed)' "$metrics_file" | \
            while read line; do
                echo "  $line"
            done
    else
        echo -e "${RED}警告: 无法获取指标数据${NC}"
    fi
    echo ""
}

# 测试函数定义
run_connection_test() {
    echo -e "${GREEN}=== 连接测试 ===${NC}"
    start_benchmark_with_monitoring "连接测试" \
        "./emqtt_bench conn \
            -h $HOST \
            -p $PORT \
            -c $CLIENT_COUNT \
            -i 10 \
            --prometheus \
            --restapi $PROMETHEUS_PORT \
            --qoe true" \
        30
    collect_metrics "connection" $PROMETHEUS_PORT
}

run_publish_test() {
    echo -e "${GREEN}=== 发布测试 ===${NC}"
    start_benchmark_with_monitoring "发布测试" \
        "./emqtt_bench pub \
            -h $HOST \
            -p $PORT \
            -c $CLIENT_COUNT \
            -i 10 \
            -I $MSG_INTERVAL \
            -t 'test/topic/%i' \
            --prometheus \
            --restapi $((PROMETHEUS_PORT + 1)) \
            --qoe true" \
        30
    collect_metrics "publish" $((PROMETHEUS_PORT + 1))
}

run_subscribe_test() {
    echo -e "${GREEN}=== 订阅测试 ===${NC}"
    start_benchmark_with_monitoring "订阅测试" \
        "./emqtt_bench sub \
            -h $HOST \
            -p $PORT \
            -c $CLIENT_COUNT \
            -i 10 \
            -t 'test/topic/%i' \
            --prometheus \
            --restapi $((PROMETHEUS_PORT + 2)) \
            --qoe true" \
        30
    collect_metrics "subscribe" $((PROMETHEUS_PORT + 2))
}

run_huawei_test() {
    echo -e "${GREEN}=== 华为云 IoT 平台测试 ===${NC}"
    start_benchmark_with_monitoring "华为云发布测试" \
        "./emqtt_bench pub \
            -h $HUAWEI_HOST \
            -p 1883 \
            -c 5 \
            -i 10 \
            -I 1000 \
            -t '$oc/devices/%d/sys/properties/report' \
            --prefix '$DEVICE_PREFIX' \
            -P '$HUAWEI_SECRET' \
            --huawei-auth \
            --message 'template://./huawei_cloud_payload_template.json' \
            --prometheus \
            --restapi $((PROMETHEUS_PORT + 3)) \
            --qoe true" \
        30
    collect_metrics "huawei_publish" $((PROMETHEUS_PORT + 3))
}

run_custom_test() {
    echo -e "${GREEN}=== 自定义测试 ===${NC}"
    echo -e "${YELLOW}自定义测试配置:${NC}"
    
    # 获取用户输入
    read -p "客户端数量 (默认: $CLIENT_COUNT): " custom_clients
    custom_clients=${custom_clients:-$CLIENT_COUNT}
    
    read -p "消息间隔ms (默认: $MSG_INTERVAL): " custom_interval
    custom_interval=${custom_interval:-$MSG_INTERVAL}
    
    read -p "测试持续时间秒 (默认: 30): " custom_duration
    custom_duration=${custom_duration:-30}
    
    read -p "Topic (默认: test/custom/%i): " custom_topic
    custom_topic=${custom_topic:-"test/custom/%i"}
    
    echo ""
    echo -e "${BLUE}自定义测试参数:${NC}"
    echo "  客户端数量: $custom_clients"
    echo "  消息间隔: ${custom_interval}ms"
    echo "  持续时间: ${custom_duration}秒"
    echo "  Topic: $custom_topic"
    echo ""
    
    start_benchmark_with_monitoring "自定义测试" \
        "./emqtt_bench pub \
            -h $HOST \
            -p $PORT \
            -c $custom_clients \
            -i 10 \
            -I $custom_interval \
            -t '$custom_topic' \
            --prometheus \
            --restapi $((PROMETHEUS_PORT + 4)) \
            --qoe true" \
        $custom_duration
    collect_metrics "custom" $((PROMETHEUS_PORT + 4))
}

run_all_tests() {
    echo -e "${GREEN}=== 运行所有测试 ===${NC}"
    run_connection_test
    run_publish_test
    run_subscribe_test
    run_huawei_test
}

# 主程序逻辑
get_user_choice
choice=$?

case $choice in
    1)
        run_connection_test
        ;;
    2)
        run_publish_test
        ;;
    3)
        run_subscribe_test
        ;;
    4)
        run_huawei_test
        ;;
    5)
        run_all_tests
        ;;
    6)
        run_custom_test
        ;;
    0)
        echo -e "${YELLOW}退出程序${NC}"
        exit 0
        ;;
esac

# 生成测试报告
generate_report() {
    echo -e "${GREEN}=== 生成测试报告 ===${NC}"
    report_file="benchmark_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# eMQTT-Bench 压测报告

**测试时间**: $(date)
**测试环境**: $HOST:$PORT
**客户端数量**: $CLIENT_COUNT
**消息间隔**: ${MSG_INTERVAL}ms

## 测试配置

- MQTT服务器: $HOST:$PORT
- 客户端数量: $CLIENT_COUNT
- 消息间隔: ${MSG_INTERVAL}ms
- Prometheus端口范围: $PROMETHEUS_PORT - $((PROMETHEUS_PORT + 4))

## 测试结果

EOF

    # 根据实际运行的测试添加结果
    case $choice in
        1)
            cat >> "$report_file" << EOF
### 1. 连接测试
- 端口: $PROMETHEUS_PORT
- 指标文件: metrics_connection_*.txt

EOF
            ;;
        2)
            cat >> "$report_file" << EOF
### 1. 发布测试
- 端口: $((PROMETHEUS_PORT + 1))
- 指标文件: metrics_publish_*.txt

EOF
            ;;
        3)
            cat >> "$report_file" << EOF
### 1. 订阅测试
- 端口: $((PROMETHEUS_PORT + 2))
- 指标文件: metrics_subscribe_*.txt

EOF
            ;;
        4)
            cat >> "$report_file" << EOF
### 1. 华为云 IoT 平台测试
- 端口: $((PROMETHEUS_PORT + 3))
- 指标文件: metrics_huawei_publish_*.txt
- 服务器: $HUAWEI_HOST
- 设备前缀: $DEVICE_PREFIX
- 设备密钥: $HUAWEI_SECRET

EOF
            ;;
        5)
            cat >> "$report_file" << EOF
### 1. 连接测试
- 端口: $PROMETHEUS_PORT
- 指标文件: metrics_connection_*.txt

### 2. 发布测试
- 端口: $((PROMETHEUS_PORT + 1))
- 指标文件: metrics_publish_*.txt

### 3. 订阅测试
- 端口: $((PROMETHEUS_PORT + 2))
- 指标文件: metrics_subscribe_*.txt

### 4. 华为云 IoT 平台测试
- 端口: $((PROMETHEUS_PORT + 3))
- 指标文件: metrics_huawei_publish_*.txt
- 服务器: $HUAWEI_HOST
- 设备前缀: $DEVICE_PREFIX
- 设备密钥: $HUAWEI_SECRET

EOF
            ;;
        6)
            cat >> "$report_file" << EOF
### 1. 自定义测试
- 端口: $((PROMETHEUS_PORT + 4))
- 指标文件: metrics_custom_*.txt
- 客户端数量: ${custom_clients:-$CLIENT_COUNT}
- 消息间隔: ${custom_interval:-$MSG_INTERVAL}ms
- 持续时间: ${custom_duration:-30}秒
- Topic: ${custom_topic:-"test/custom/%i"}

EOF
            ;;
    esac

    cat >> "$report_file" << EOF
## 指标说明

### 连接相关指标
- \`mqtt_bench_connected\`: 已建立的连接数
- \`mqtt_bench_connect_failed\`: 连接失败数
- \`mqtt_bench_disconnected\`: 断开连接数

### 消息相关指标
- \`mqtt_bench_publish_sent\`: 已发送的发布消息数
- \`mqtt_bench_publish_received\`: 已接收的发布消息数
- \`mqtt_bench_subscribe_sent\`: 已发送的订阅消息数
- \`mqtt_bench_subscribe_received\`: 已接收的订阅消息数

### 延迟相关指标
- \`mqtt_client_tcp_handshake_duration\`: TCP握手延迟
- \`mqtt_client_handshake_duration\`: MQTT握手延迟
- \`mqtt_client_connect_duration\`: 连接建立延迟
- \`mqtt_client_subscribe_duration\`: 订阅延迟

## 使用方法

### 查看实时指标
\`\`\`bash
# 查看连接测试指标
curl http://localhost:$PROMETHEUS_PORT/metrics

# 查看发布测试指标
curl http://localhost:$((PROMETHEUS_PORT + 1))/metrics

# 查看订阅测试指标
curl http://localhost:$((PROMETHEUS_PORT + 2))/metrics

# 查看华为云测试指标
curl http://localhost:$((PROMETHEUS_PORT + 3))/metrics

# 查看自定义测试指标
curl http://localhost:$((PROMETHEUS_PORT + 4))/metrics
\`\`\`

### 使用 Python 工具收集指标
\`\`\`bash
cd metrics/
uv run metrics_collector.py collect --summary
\`\`\`

### 集成 Prometheus
在 \`prometheus.yml\` 中添加以下配置：

\`\`\`yaml
scrape_configs:
  - job_name: 'emqtt-bench-connection'
    static_configs:
      - targets: ['localhost:$PROMETHEUS_PORT']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-publish'
    static_configs:
      - targets: ['localhost:$((PROMETHEUS_PORT + 1))']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-subscribe'
    static_configs:
      - targets: ['localhost:$((PROMETHEUS_PORT + 2))']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-huawei'
    static_configs:
      - targets: ['localhost:$((PROMETHEUS_PORT + 3))']
    scrape_interval: 5s
\`\`\`

## 文件清单

$(ls -la metrics_*.txt 2>/dev/null | sed 's/^/- /')

EOF

    echo "测试报告已生成: $report_file"
}

# 调用报告生成函数
generate_report

# 显示文件清单
echo -e "${YELLOW}生成的文件:${NC}"
ls -la metrics_*.txt 2>/dev/null | while read line; do
    echo "  $line"
done
echo "  $report_file"

echo ""
echo -e "${GREEN}=== 测试完成 ===${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo "1. 查看测试报告: cat $report_file"
echo "2. 分析指标数据: 查看 metrics_*.txt 文件"
echo "3. 使用 Python 工具: cd metrics/ && uv run metrics_collector.py collect --summary"
echo "4. 集成 Prometheus: 配置 prometheus.yml"
echo "5. 创建 Grafana 仪表板: 可视化监控数据"
echo ""
echo -e "${BLUE}提示: 使用环境变量自定义测试参数${NC}"
echo "  export MQTT_HOST=your-mqtt-server"
echo "  export CLIENT_COUNT=500"
echo "  export MSG_INTERVAL=500"
echo ""
echo -e "${BLUE}当前华为云配置:${NC}"
echo "  服务器: $HUAWEI_HOST"
echo "  设备前缀: $DEVICE_PREFIX"
echo "  设备密钥: $HUAWEI_SECRET"
echo ""
echo -e "${GREEN}感谢使用 eMQTT-Bench Prometheus 监控工具！${NC}"
