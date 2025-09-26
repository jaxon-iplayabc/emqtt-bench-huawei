#!/bin/bash
# eMQTT-Bench 压测结果显示系统快速启动脚本
# 作者: Jaxon
# 日期: 2025-01-27

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查依赖
check_dependencies() {
    print_message $BLUE "🔍 检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_message $RED "❌ Python3 未安装"
        exit 1
    fi
    
    # 检查pip包
    local packages=("requests" "rich" "matplotlib" "pandas" "numpy")
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            print_message $YELLOW "⚠️  安装缺失的包: $package"
            pip3 install $package
        fi
    done
    
    print_message $GREEN "✅ 依赖检查完成"
}

# 检查eMQTT-Bench
check_emqtt_bench() {
    print_message $BLUE "🔍 检查 eMQTT-Bench..."
    
    if [ ! -f "./emqtt_bench" ]; then
        print_message $RED "❌ eMQTT-Bench 可执行文件不存在"
        print_message $YELLOW "请确保在正确的目录中运行此脚本"
        exit 1
    fi
    
    print_message $GREEN "✅ eMQTT-Bench 检查完成"
}

# 启动eMQTT-Bench
start_emqtt_bench() {
    local test_type=${1:-"conn"}
    local client_count=${2:-"10"}
    local interval=${3:-"100"}
    
    print_message $BLUE "🚀 启动 eMQTT-Bench $test_type 测试..."
    
    case $test_type in
        "conn")
            ./emqtt_bench conn \
                -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
                -p 1883 \
                -c $client_count \
                -i $interval \
                --prefix speaker \
                -P 12345678 \
                --huawei-auth \
                --prometheus \
                --restapi 9090 &
            ;;
        "pub")
            ./emqtt_bench pub \
                -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
                -p 1883 \
                -c $client_count \
                -I $interval \
                -t '$oc/devices/%u/sys/properties/report' \
                --prefix speaker \
                -P 12345678 \
                --huawei-auth \
                --prometheus \
                --restapi 9091 &
            ;;
        "sub")
            ./emqtt_bench sub \
                -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
                -p 1883 \
                -c $client_count \
                -i $interval \
                -t '$oc/devices/%u/sys/properties/report' \
                --prefix speaker \
                -P 12345678 \
                --huawei-auth \
                --prometheus \
                --restapi 9092 &
            ;;
        *)
            print_message $RED "❌ 不支持的测试类型: $test_type"
            exit 1
            ;;
    esac
    
    local emqtt_pid=$!
    echo $emqtt_pid > emqtt_bench.pid
    
    print_message $GREEN "✅ eMQTT-Bench 已启动 (PID: $emqtt_pid)"
    print_message $YELLOW "等待5秒让服务启动完成..."
    sleep 5
}

# 启动显示系统
start_display_system() {
    local mode=${1:-"live"}
    local test_type=${2:-"conn"}
    
    print_message $BLUE "📊 启动显示系统 ($mode 模式)..."
    
    case $mode in
        "live")
            python3 benchmark_display_system.py --mode live --test-type $test_type
            ;;
        "web")
            python3 benchmark_display_system.py --mode web --web-port 8080
            ;;
        "report")
            python3 benchmark_display_system.py --mode report
            ;;
        *)
            print_message $RED "❌ 不支持的显示模式: $mode"
            exit 1
            ;;
    esac
}

# 停止eMQTT-Bench
stop_emqtt_bench() {
    if [ -f "emqtt_bench.pid" ]; then
        local pid=$(cat emqtt_bench.pid)
        if kill -0 $pid 2>/dev/null; then
            print_message $YELLOW "🛑 停止 eMQTT-Bench (PID: $pid)..."
            kill $pid
            rm emqtt_bench.pid
            print_message $GREEN "✅ eMQTT-Bench 已停止"
        else
            print_message $YELLOW "⚠️  eMQTT-Bench 进程不存在"
            rm emqtt_bench.pid
        fi
    fi
}

# 清理函数
cleanup() {
    print_message $YELLOW "🧹 清理资源..."
    stop_emqtt_bench
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 显示帮助信息
show_help() {
    echo "eMQTT-Bench 压测结果显示系统快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --test-type TYPE     测试类型 (conn|pub|sub) [默认: conn]"
    echo "  -m, --mode MODE         显示模式 (live|web|report) [默认: live]"
    echo "  -c, --clients COUNT     客户端数量 [默认: 10]"
    echo "  -i, --interval MS       间隔时间(毫秒) [默认: 100]"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                                    # 启动连接测试的实时显示"
    echo "  $0 -t pub -m web                     # 启动发布测试的Web仪表盘"
    echo "  $0 -t sub -c 20 -i 50               # 启动20个客户端的订阅测试"
    echo "  $0 -m report                         # 生成测试报告"
    echo ""
}

# 主函数
main() {
    local test_type="conn"
    local mode="live"
    local client_count="10"
    local interval="100"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--test-type)
                test_type="$2"
                shift 2
                ;;
            -m|--mode)
                mode="$2"
                shift 2
                ;;
            -c|--clients)
                client_count="$2"
                shift 2
                ;;
            -i|--interval)
                interval="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_message $RED "❌ 未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_message $BLUE "🎯 eMQTT-Bench 压测结果显示系统"
    print_message $BLUE "=================================="
    print_message $BLUE "测试类型: $test_type"
    print_message $BLUE "显示模式: $mode"
    print_message $BLUE "客户端数: $client_count"
    print_message $BLUE "间隔时间: ${interval}ms"
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 检查eMQTT-Bench
    check_emqtt_bench
    
    # 如果不是报告模式，启动eMQTT-Bench
    if [ "$mode" != "report" ]; then
        start_emqtt_bench $test_type $client_count $interval
    fi
    
    # 启动显示系统
    start_display_system $mode $test_type
}

# 运行主函数
main "$@"

