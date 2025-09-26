#!/bin/bash
# eMQTT-Bench 进程管理脚本
# 确保测试结束时正确清理所有进程

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 全局变量
EMQTT_BENCH_PIDS=()
CLEANUP_FUNCTIONS=()
TRAP_SET=false

# 设置信号处理
setup_signal_handlers() {
    if [ "$TRAP_SET" = true ]; then
        return
    fi
    
    echo -e "${BLUE}🔧 设置信号处理器...${NC}"
    
    # 捕获各种退出信号
    trap 'cleanup_all; exit 130' INT    # Ctrl+C
    trap 'cleanup_all; exit 143' TERM   # SIGTERM
    trap 'cleanup_all; exit 0' EXIT    # 正常退出
    
    TRAP_SET=true
    echo -e "${GREEN}✅ 信号处理器已设置${NC}"
}

# 注册清理函数
register_cleanup() {
    local cleanup_func="$1"
    CLEANUP_FUNCTIONS+=("$cleanup_func")
    echo -e "${YELLOW}📝 注册清理函数: $cleanup_func${NC}"
}

# 注册eMQTT-Bench进程
register_emqtt_bench() {
    local pid="$1"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        EMQTT_BENCH_PIDS+=("$pid")
        echo -e "${GREEN}📝 注册eMQTT-Bench进程: PID $pid${NC}"
    else
        echo -e "${RED}❌ 无效的进程ID: $pid${NC}"
    fi
}

# 清理所有eMQTT-Bench进程
cleanup_emqtt_bench() {
    echo -e "${YELLOW}🧹 清理eMQTT-Bench进程...${NC}"
    
    if [ ${#EMQTT_BENCH_PIDS[@]} -eq 0 ]; then
        echo -e "${YELLOW}ℹ️  没有注册的eMQTT-Bench进程${NC}"
    else
        for pid in "${EMQTT_BENCH_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}🔄 正在终止进程 $pid...${NC}"
                kill -TERM "$pid" 2>/dev/null
                
                # 等待进程优雅退出
                local count=0
                while kill -0 "$pid" 2>/dev/null && [ $count -lt 5 ]; do
                    sleep 1
                    count=$((count + 1))
                done
                
                # 如果进程仍然存在，强制终止
                if kill -0 "$pid" 2>/dev/null; then
                    echo -e "${RED}⚠️  强制终止进程 $pid${NC}"
                    kill -KILL "$pid" 2>/dev/null
                else
                    echo -e "${GREEN}✅ 进程 $pid 已优雅退出${NC}"
                fi
            else
                echo -e "${YELLOW}ℹ️  进程 $pid 已不存在${NC}"
            fi
        done
    fi
    
    # 清理所有eMQTT-Bench相关进程
    echo -e "${YELLOW}🔍 查找并清理所有eMQTT-Bench相关进程...${NC}"
    local remaining_pids=$(pgrep -f "emqtt_bench" 2>/dev/null)
    if [ -n "$remaining_pids" ]; then
        echo -e "${YELLOW}发现剩余进程: $remaining_pids${NC}"
        echo "$remaining_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        echo "$remaining_pids" | xargs kill -KILL 2>/dev/null
        echo -e "${GREEN}✅ 所有eMQTT-Bench进程已清理${NC}"
    else
        echo -e "${GREEN}✅ 没有发现剩余的eMQTT-Bench进程${NC}"
    fi
}

# 清理端口占用
cleanup_ports() {
    echo -e "${YELLOW}🧹 清理端口占用...${NC}"
    
    # 清理常用端口
    local ports=(8080 8081 8082 8083 8084 9090 9091 9092 9093 9094)
    
    for port in "${ports[@]}"; do
        local pid=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}🔄 清理端口 $port (PID: $pid)${NC}"
            kill -TERM "$pid" 2>/dev/null
            sleep 1
            kill -KILL "$pid" 2>/dev/null
        fi
    done
    
    echo -e "${GREEN}✅ 端口清理完成${NC}"
}

# 执行所有清理函数
cleanup_all() {
    echo -e "${BLUE}🧹 开始清理所有资源...${NC}"
    
    # 执行注册的清理函数
    for cleanup_func in "${CLEANUP_FUNCTIONS[@]}"; do
        if [ -n "$cleanup_func" ]; then
            echo -e "${YELLOW}🔄 执行清理函数: $cleanup_func${NC}"
            eval "$cleanup_func"
        fi
    done
    
    # 清理eMQTT-Bench进程
    cleanup_emqtt_bench
    
    # 清理端口
    cleanup_ports
    
    echo -e "${GREEN}✅ 所有资源清理完成${NC}"
}

# 启动eMQTT-Bench并注册进程
start_emqtt_bench() {
    local command="$1"
    local description="${2:-eMQTT-Bench测试}"
    
    echo -e "${BLUE}🚀 启动: $description${NC}"
    echo -e "${YELLOW}📝 命令: $command${NC}"
    
    # 启动进程
    eval "$command" &
    local pid=$!
    
    # 注册进程
    register_emqtt_bench "$pid"
    
    echo -e "${GREEN}✅ 进程已启动: PID $pid${NC}"
    return $pid
}

# 等待用户输入或进程结束
wait_for_completion() {
    local timeout="${1:-0}"
    
    if [ $timeout -gt 0 ]; then
        echo -e "${YELLOW}⏰ 等待 $timeout 秒或按 Ctrl+C 退出...${NC}"
        sleep $timeout
    else
        echo -e "${YELLOW}⏰ 按 Ctrl+C 退出或等待进程自然结束...${NC}"
        # 等待所有注册的进程结束
        for pid in "${EMQTT_BENCH_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                wait "$pid"
            fi
        done
    fi
}

# 显示进程状态
show_status() {
    echo -e "${BLUE}📊 当前进程状态:${NC}"
    
    if [ ${#EMQTT_BENCH_PIDS[@]} -eq 0 ]; then
        echo -e "${YELLOW}ℹ️  没有注册的进程${NC}"
    else
        for pid in "${EMQTT_BENCH_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${GREEN}✅ 进程 $pid 正在运行${NC}"
            else
                echo -e "${RED}❌ 进程 $pid 已结束${NC}"
            fi
        done
    fi
    
    # 显示端口占用情况
    echo -e "${BLUE}🔌 端口占用情况:${NC}"
    local ports=(8080 8081 8082 8083 8084 9090 9091 9092 9093 9094)
    for port in "${ports[@]}"; do
        local pid=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}端口 $port: PID $pid${NC}"
        fi
    done
}

# 主函数
main() {
    echo -e "${BLUE}🚀 eMQTT-Bench 进程管理器${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # 设置信号处理
    setup_signal_handlers
    
    # 注册默认清理函数
    register_cleanup "cleanup_ports"
    
    # 如果提供了参数，执行相应的操作
    case "${1:-}" in
        "cleanup")
            cleanup_all
            ;;
        "status")
            show_status
            ;;
        "start")
            if [ -n "$2" ]; then
                start_emqtt_bench "$2" "$3"
                wait_for_completion "${4:-0}"
            else
                echo -e "${RED}❌ 请提供启动命令${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${YELLOW}用法:${NC}"
            echo "  $0 start <command> [description] [timeout]  # 启动进程并管理"
            echo "  $0 cleanup                                  # 清理所有进程"
            echo "  $0 status                                   # 显示状态"
            echo ""
            echo -e "${YELLOW}示例:${NC}"
            echo "  $0 start './emqtt_bench pub -c 1 -I 1000 -t test/topic --prometheus --restapi 9090' '发布测试' 30"
            echo "  $0 cleanup"
            echo "  $0 status"
            ;;
    esac
}

# 如果直接运行此脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
