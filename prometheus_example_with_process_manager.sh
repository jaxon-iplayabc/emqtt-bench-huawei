#!/bin/bash
# eMQTT-Bench Prometheus 监控示例脚本 (带进程管理)
# 支持交互式选择测试类型和用户自定义配置，确保进程正确清理

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 引入进程管理器
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/process_manager.sh"

echo -e "${BLUE}🚀 eMQTT-Bench Prometheus 监控工具 (带进程管理)${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${YELLOW}✨ 新功能: 自动进程管理和清理${NC}"
echo -e "${YELLOW}🛡️  安全退出: 支持Ctrl+C优雅退出${NC}"
echo -e "${YELLOW}🧹 自动清理: 测试结束后自动清理所有进程和端口${NC}"
echo ""

# 配置参数
HOST="${MQTT_HOST:-localhost}"
PORT="${MQTT_PORT:-1883}"
CLIENT_COUNT="${CLIENT_COUNT:-5}"
MSG_INTERVAL="${MSG_INTERVAL:-1000}"
PROMETHEUS_PORT="${PROMETHEUS_PORT:-9090}"

# 华为云配置参数 (Hardcoded)
HUAWEI_HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
HUAWEI_SECRET="12345678"
DEVICE_PREFIX="speaker"

# 配置保存和加载功能
CONFIG_FILE="emqtt_bench_config.conf"

# 获取华为云配置参数
get_huawei_config() {
    echo -e "${YELLOW}请输入华为云IoT平台配置信息:${NC}"
    echo ""
    
    # 华为云服务器地址
    read -p "华为云IoT服务器地址 (默认: $HUAWEI_HOST): " input_host
    HUAWEI_HOST="${input_host:-$HUAWEI_HOST}"
    
    # 华为云端口
    read -p "华为云IoT端口 (默认: 1883): " input_port
    HUAWEI_PORT="${input_port:-1883}"
    
    # 设备前缀
    read -p "设备前缀 (默认: $DEVICE_PREFIX): " input_prefix
    DEVICE_PREFIX="${input_prefix:-$DEVICE_PREFIX}"
    
    # 设备密钥
    read -p "设备密钥 (默认: $HUAWEI_SECRET): " input_secret
    HUAWEI_SECRET="${input_secret:-$HUAWEI_SECRET}"
    
    echo ""
    echo -e "${GREEN}✅ 华为云配置已设置:${NC}"
    echo "  服务器: $HUAWEI_HOST:$HUAWEI_PORT"
    echo "  设备前缀: $DEVICE_PREFIX"
    echo "  设备密钥: $HUAWEI_SECRET"
    echo ""
}

# 获取其他配置参数
get_other_config() {
    echo -e "${YELLOW}📝 其他配置参数 (按回车使用默认值):${NC}"
    echo ""
    
    # 客户端数量
    read -p "客户端数量 (默认: $CLIENT_COUNT): " input_clients
    if [ ! -z "$input_clients" ]; then
        CLIENT_COUNT="$input_clients"
    fi
    
    # 消息间隔
    read -p "消息间隔(ms) (默认: $MSG_INTERVAL): " input_interval
    if [ ! -z "$input_interval" ]; then
        MSG_INTERVAL="$input_interval"
    fi
    
    # Prometheus端口
    read -p "Prometheus起始端口 (默认: $PROMETHEUS_PORT): " input_prom_port
    if [ ! -z "$input_prom_port" ]; then
        PROMETHEUS_PORT="$input_prom_port"
    fi
    
    echo ""
}

# 保存配置
save_config() {
    cat > "$CONFIG_FILE" << EOF
# eMQTT-Bench 配置文件
# 生成时间: $(date)

# 华为云配置
HUAWEI_HOST="$HUAWEI_HOST"
HUAWEI_PORT="$HUAWEI_PORT"
DEVICE_PREFIX="$DEVICE_PREFIX"
HUAWEI_SECRET="$HUAWEI_SECRET"

# 其他配置
CLIENT_COUNT="$CLIENT_COUNT"
MSG_INTERVAL="$MSG_INTERVAL"
PROMETHEUS_PORT="$PROMETHEUS_PORT"
EOF
    echo -e "${GREEN}✅ 配置已保存到 $CONFIG_FILE${NC}"
}

# 加载配置
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}📁 发现配置文件 $CONFIG_FILE${NC}"
        read -p "是否加载保存的配置? (y/n): " load_choice
        if [[ $load_choice =~ ^[Yy]$ ]]; then
            source "$CONFIG_FILE"
            echo -e "${GREEN}✅ 配置已加载${NC}"
            return 0
        fi
    fi
    return 1
}

# 配置确认
confirm_config() {
    echo -e "${YELLOW}📋 当前配置参数:${NC}"
    echo "  MQTT服务器: $HOST:$PORT"
    echo "  客户端数量: $CLIENT_COUNT"
    echo "  消息间隔: ${MSG_INTERVAL}ms"
    echo "  Prometheus端口: $PROMETHEUS_PORT"
    echo ""
    echo -e "${YELLOW}☁️  华为云配置:${NC}"
    echo "  服务器: $HUAWEI_HOST:$HUAWEI_PORT"
    echo "  设备前缀: $DEVICE_PREFIX"
    echo "  设备密钥: $HUAWEI_SECRET"
    echo ""
    
    while true; do
        read -p "是否确认使用以上配置? (y/n/s保存配置): " confirm
        case $confirm in
            [Yy]* ) 
                echo -e "${GREEN}✅ 配置已确认，开始测试...${NC}"
                echo ""
                break
                ;;
            [Nn]* ) 
                echo -e "${YELLOW}请重新配置参数...${NC}"
                echo ""
                get_huawei_config
                get_other_config
                ;;
            [Ss]* ) 
                save_config
                echo ""
                ;;
            * ) 
                echo -e "${RED}请输入 y(确认)、n(重新配置) 或 s(保存配置)${NC}"
                ;;
        esac
    done
}

# 启动带监控的基准测试
start_benchmark_with_monitoring() {
    local test_name="$1"
    local command="$2"
    local duration="${3:-30}"
    
    echo -e "${BLUE}🚀 启动测试: $test_name${NC}"
    echo -e "${YELLOW}📝 命令: $command${NC}"
    echo -e "${YELLOW}⏰ 持续时间: ${duration}秒${NC}"
    echo ""
    
    # 使用进程管理器启动
    start_emqtt_bench "$command" "$test_name"
    local bench_pid=$?
    
    # 等待测试完成
    echo -e "${GREEN}✅ 测试已启动，PID: $bench_pid${NC}"
    echo -e "${YELLOW}💡 按 Ctrl+C 可以提前结束测试${NC}"
    echo ""
    
    wait_for_completion "$duration"
    
    echo -e "${GREEN}✅ 测试 '$test_name' 已完成${NC}"
    echo ""
}

# 运行连接测试
run_connection_test() {
    echo -e "${BLUE}🔗 运行连接测试${NC}"
    start_benchmark_with_monitoring "连接测试" \
        "./emqtt_bench conn -h $HOST -p $PORT -c $CLIENT_COUNT --prometheus --restapi $PROMETHEUS_PORT" \
        30
}

# 运行发布测试
run_publish_test() {
    echo -e "${BLUE}📤 运行发布测试${NC}"
    start_benchmark_with_monitoring "发布测试" \
        "./emqtt_bench pub -h $HOST -p $PORT -c $CLIENT_COUNT -i 10 -I $MSG_INTERVAL -t 'test/topic' --prometheus --restapi $((PROMETHEUS_PORT + 1))" \
        30
}

# 运行订阅测试
run_subscribe_test() {
    echo -e "${BLUE}📥 运行订阅测试${NC}"
    start_benchmark_with_monitoring "订阅测试" \
        "./emqtt_bench sub -h $HOST -p $PORT -c $CLIENT_COUNT -t 'test/topic' --prometheus --restapi $((PROMETHEUS_PORT + 2))" \
        30
}

# 运行华为云测试
run_huawei_test() {
    echo -e "${BLUE}☁️  运行华为云IoT平台测试${NC}"
    start_benchmark_with_monitoring "华为云发布测试" \
        "./emqtt_bench pub \
            -h $HUAWEI_HOST \
            -p $HUAWEI_PORT \
            -c $CLIENT_COUNT \
            -i 10 \
            -I $MSG_INTERVAL \
            -t '\$oc/devices/%d/sys/properties/report' \
            --prefix '$DEVICE_PREFIX' \
            -P '$HUAWEI_SECRET' \
            --huawei-auth \
            --message 'template://./huawei_cloud_payload_template.json' \
            --prometheus \
            --restapi $((PROMETHEUS_PORT + 3)) \
            --qoe true" \
        30
}

# 运行所有测试
run_all_tests() {
    echo -e "${BLUE}🔄 运行所有测试${NC}"
    run_connection_test
    run_publish_test
    run_subscribe_test
    run_huawei_test
}

# 自定义测试
run_custom_test() {
    echo -e "${BLUE}⚙️  自定义测试${NC}"
    echo -e "${YELLOW}请输入自定义测试命令:${NC}"
    read -p "命令: " custom_command
    read -p "持续时间(秒): " custom_duration
    
    if [ -n "$custom_command" ]; then
        start_benchmark_with_monitoring "自定义测试" "$custom_command" "${custom_duration:-30}"
    else
        echo -e "${RED}❌ 未输入命令${NC}"
    fi
}

# 交互式选择测试类型
show_menu() {
    echo -e "${YELLOW}请选择要运行的测试类型:${NC}"
    echo "1) 连接测试 (Connection Test)"
    echo "2) 发布测试 (Publish Test)"
    echo "3) 订阅测试 (Subscribe Test)"
    echo "4) 华为云 IoT 平台测试 (Huawei Cloud IoT Test)"
    echo "5) 运行所有测试 (Run All Tests)"
    echo "6) 自定义测试 (Custom Test)"
    echo "7) 显示进程状态 (Show Status)"
    echo "8) 清理所有进程 (Cleanup All)"
    echo "0) 退出 (Exit)"
    echo ""
}

# 获取用户选择
get_user_choice() {
    while true; do
        show_menu
        read -p "请输入选择 (0-8): " choice
        case $choice in
            1|2|3|4|5|6|7|8|0)
                return $choice
                ;;
            *)
                echo -e "${RED}无效选择，请输入 0-8 之间的数字${NC}"
                echo ""
                ;;
        esac
    done
}

# 生成测试报告
generate_report() {
    local report_file="benchmark_report_$(date +%Y%m%d_%H%M%S).md"
    
    echo -e "${BLUE}📊 生成测试报告...${NC}"
    
    cat > "$report_file" << EOF
# eMQTT-Bench 测试报告

**生成时间**: $(date)
**测试配置**:
- MQTT服务器: $HOST:$PORT
- 客户端数量: $CLIENT_COUNT
- 消息间隔: ${MSG_INTERVAL}ms
- Prometheus端口: $PROMETHEUS_PORT

**华为云配置**:
- 服务器: $HUAWEI_HOST:$HUAWEI_PORT
- 设备前缀: $DEVICE_PREFIX
- 设备密钥: $HUAWEI_SECRET

## 测试结果

### Prometheus指标端点
EOF

    # 添加Prometheus端点信息
    for i in {0..3}; do
        local port=$((PROMETHEUS_PORT + i))
        echo "- http://localhost:$port/metrics" >> "$report_file"
    done

    cat >> "$report_file" << EOF

## 使用方法

1. 查看实时指标:
   \`\`\`bash
   curl http://localhost:$PROMETHEUS_PORT/metrics
   \`\`\`

2. 使用Python分析器:
   \`\`\`bash
   python3 connection_test_analyzer.py localhost:$PROMETHEUS_PORT/metrics
   \`\`\`

3. 清理所有进程:
   \`\`\`bash
   ./process_manager.sh cleanup
   \`\`\`

---
*报告由 eMQTT-Bench Prometheus 监控工具自动生成*
EOF

    echo -e "${GREEN}✅ 报告已生成: $report_file${NC}"
}

# 主程序逻辑
main() {
    # 设置进程管理
    setup_signal_handlers
    
    # 尝试加载保存的配置
    if ! load_config; then
        # 如果没有加载配置，则获取用户输入
        echo -e "${YELLOW}🔧 开始配置参数...${NC}"
        echo ""
        
        # 获取华为云配置
        get_huawei_config
        
        # 获取其他配置
        get_other_config
    fi
    
    # 确认配置
    confirm_config
    
    # 主循环
    while true; do
        get_user_choice
        choice=$?
        
        case $choice in
            1) run_connection_test ;;
            2) run_publish_test ;;
            3) run_subscribe_test ;;
            4) run_huawei_test ;;
            5) run_all_tests ;;
            6) run_custom_test ;;
            7) show_status ;;
            8) cleanup_all ;;
            0) 
                echo -e "${YELLOW}退出程序${NC}"
                break
                ;;
        esac
        
        # 询问是否继续
        if [ $choice -ne 0 ]; then
            echo ""
            read -p "是否继续其他测试? (y/n): " continue_choice
            if [[ ! $continue_choice =~ ^[Yy]$ ]]; then
                break
            fi
            echo ""
        fi
    done
    
    # 生成测试报告
    generate_report
    
    echo -e "${GREEN}✅ 程序结束，所有进程已自动清理${NC}"
}

# 运行主程序
main "$@"
