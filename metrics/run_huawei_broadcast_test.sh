#!/bin/bash
# 华为云广播测试快速启动脚本
# 作者: Jaxon
# 日期: 2024-12-19

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "华为云广播测试快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -c, --config FILE       使用指定的配置文件"
    echo "  -i, --interactive       交互式配置模式"
    echo "  -d, --demo              演示模式（使用模拟数据）"
    echo "  -s, --single           单次发送模式"
    echo "  -l, --loop             循环发送模式"
    echo "  -t, --test             运行完整集成测试"
    echo ""
    echo "示例:"
    echo "  $0 --interactive        # 交互式配置"
    echo "  $0 --config config.json # 使用配置文件"
    echo "  $0 --demo              # 演示模式"
    echo "  $0 --single            # 单次发送广播"
    echo "  $0 --loop              # 循环发送广播"
    echo "  $0 --test              # 完整集成测试"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查必要的包
    python3 -c "import paho.mqtt.client, huaweicloudsdkcore, huaweicloudsdkiotda" 2>/dev/null || {
        print_warning "缺少必要的Python包，正在安装..."
        pip3 install paho-mqtt huaweicloudsdkcore huaweicloudsdkiotda
    }
}

# 创建默认配置文件
create_default_config() {
    local config_file="huawei_broadcast_config.json"
    
    if [ ! -f "$config_file" ]; then
        print_info "创建默认配置文件: $config_file"
        cat > "$config_file" << EOF
{
  "mqtt_host": "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com",
  "mqtt_port": 1883,
  "device_prefix": "speaker",
  "device_secret": "12345678",
  "huawei_ak": "YOUR_ACCESS_KEY",
  "huawei_sk": "YOUR_SECRET_KEY",
  "huawei_endpoint": "YOUR_IOTDA_ENDPOINT",
  "huawei_region": "cn-north-4",
  "broadcast_topic": "\$oc/broadcast/test",
  "broadcast_interval": 5,
  "test_duration": 60
}
EOF
        print_success "默认配置文件已创建，请编辑 $config_file 填入正确的参数"
    fi
}

# 交互式配置
interactive_config() {
    print_info "开始交互式配置..."
    
    read -p "请输入MQTT服务器地址: " mqtt_host
    read -p "请输入MQTT端口 (默认1883): " mqtt_port
    mqtt_port=${mqtt_port:-1883}
    
    read -p "请输入设备前缀: " device_prefix
    read -p "请输入设备密钥: " device_secret
    
    read -p "请输入华为云访问密钥ID: " huawei_ak
    read -p "请输入华为云访问密钥Secret: " huawei_sk
    read -p "请输入华为云IoTDA端点: " huawei_endpoint
    
    read -p "请输入广播发送间隔(秒，默认5): " broadcast_interval
    broadcast_interval=${broadcast_interval:-5}
    
    read -p "请输入测试持续时间(秒，默认60): " test_duration
    test_duration=${test_duration:-60}
    
    # 创建配置文件
    cat > "huawei_broadcast_config.json" << EOF
{
  "mqtt_host": "$mqtt_host",
  "mqtt_port": $mqtt_port,
  "device_prefix": "$device_prefix",
  "device_secret": "$device_secret",
  "huawei_ak": "$huawei_ak",
  "huawei_sk": "$huawei_sk",
  "huawei_endpoint": "$huawei_endpoint",
  "huawei_region": "cn-north-4",
  "broadcast_topic": "\$oc/broadcast/test",
  "broadcast_interval": $broadcast_interval,
  "test_duration": $test_duration
}
EOF
    
    print_success "配置已保存到 huawei_broadcast_config.json"
}

# 演示模式
demo_mode() {
    print_info "启动演示模式..."
    print_warning "演示模式使用模拟数据，不会实际发送广播消息"
    
    # 创建演示配置
    cat > "demo_config.json" << EOF
{
  "mqtt_host": "localhost",
  "mqtt_port": 1883,
  "device_prefix": "demo_device",
  "device_secret": "demo_secret",
  "huawei_ak": "demo_ak",
  "huawei_sk": "demo_sk",
  "huawei_endpoint": "demo_endpoint",
  "huawei_region": "cn-north-4",
  "broadcast_topic": "\$oc/broadcast/test",
  "broadcast_interval": 5,
  "test_duration": 30
}
EOF
    
    print_info "演示配置已创建，运行集成测试..."
    python3 huawei_broadcast_integration.py --config demo_config.json
}

# 单次发送模式
single_send_mode() {
    print_info "单次发送模式..."
    
    if [ ! -f "huawei_broadcast_config.json" ]; then
        print_error "配置文件不存在，请先运行 --interactive 或 --config 创建配置"
        exit 1
    fi
    
    # 从配置文件读取参数
    local ak=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_ak'])")
    local sk=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_sk'])")
    local endpoint=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_endpoint'])")
    
    if [ "$ak" = "YOUR_ACCESS_KEY" ] || [ "$sk" = "YOUR_SECRET_KEY" ] || [ "$endpoint" = "YOUR_IOTDA_ENDPOINT" ]; then
        print_error "请先编辑配置文件，填入正确的华为云参数"
        exit 1
    fi
    
    python3 broadcast.py --ak "$ak" --sk "$sk" --endpoint "$endpoint" --once
}

# 循环发送模式
loop_send_mode() {
    print_info "循环发送模式..."
    
    if [ ! -f "huawei_broadcast_config.json" ]; then
        print_error "配置文件不存在，请先运行 --interactive 或 --config 创建配置"
        exit 1
    fi
    
    # 从配置文件读取参数
    local ak=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_ak'])")
    local sk=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_sk'])")
    local endpoint=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['huawei_endpoint'])")
    local interval=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['broadcast_interval'])")
    local duration=$(python3 -c "import json; print(json.load(open('huawei_broadcast_config.json'))['test_duration'])")
    
    if [ "$ak" = "YOUR_ACCESS_KEY" ] || [ "$sk" = "YOUR_SECRET_KEY" ] || [ "$endpoint" = "YOUR_IOTDA_ENDPOINT" ]; then
        print_error "请先编辑配置文件，填入正确的华为云参数"
        exit 1
    fi
    
    python3 broadcast.py --ak "$ak" --sk "$sk" --endpoint "$endpoint" --interval "$interval" --duration "$duration"
}

# 完整集成测试
full_test_mode() {
    print_info "运行完整集成测试..."
    
    if [ ! -f "huawei_broadcast_config.json" ]; then
        print_error "配置文件不存在，请先运行 --interactive 创建配置"
        exit 1
    fi
    
    python3 huawei_broadcast_integration.py --config huawei_broadcast_config.json
}

# 主函数
main() {
    print_info "华为云广播测试快速启动脚本"
    print_info "作者: Jaxon"
    print_info "日期: 2024-12-19"
    echo ""
    
    # 检查Python环境
    check_python
    
    # 解析命令行参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--config)
            if [ -z "$2" ]; then
                print_error "请指定配置文件路径"
                exit 1
            fi
            print_info "使用配置文件: $2"
            python3 huawei_broadcast_integration.py --config "$2"
            ;;
        -i|--interactive)
            interactive_config
            ;;
        -d|--demo)
            demo_mode
            ;;
        -s|--single)
            single_send_mode
            ;;
        -l|--loop)
            loop_send_mode
            ;;
        -t|--test)
            full_test_mode
            ;;
        "")
            # 没有参数，显示帮助
            show_help
            echo ""
            print_info "请选择运行模式："
            echo "1) 交互式配置"
            echo "2) 演示模式"
            echo "3) 单次发送"
            echo "4) 循环发送"
            echo "5) 完整测试"
            echo "6) 退出"
            echo ""
            read -p "请选择 (1-6): " choice
            
            case "$choice" in
                1) interactive_config ;;
                2) demo_mode ;;
                3) single_send_mode ;;
                4) loop_send_mode ;;
                5) full_test_mode ;;
                6) print_info "退出" ; exit 0 ;;
                *) print_error "无效选择" ; exit 1 ;;
            esac
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
