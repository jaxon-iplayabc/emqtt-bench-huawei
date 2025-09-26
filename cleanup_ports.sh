#!/bin/bash
# eMQTT-Bench 端口清理脚本
# 用于清理测试后遗留的端口占用

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 eMQTT-Bench 端口清理工具${NC}"
echo -e "${BLUE}================================${NC}"

# 检查Python脚本是否存在
CLEANUP_SCRIPT="$SCRIPT_DIR/scripts/cleanup_ports.py"
if [ ! -f "$CLEANUP_SCRIPT" ]; then
    echo -e "${RED}❌ 清理脚本不存在: $CLEANUP_SCRIPT${NC}"
    exit 1
fi

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装或不在PATH中${NC}"
    exit 1
fi

# 显示当前端口占用情况
echo -e "${YELLOW}📊 当前端口占用情况:${NC}"
common_ports=(8080 8081 8082 8083 8084 9090 9091 9092 9093 9094)
for port in "${common_ports[@]}"; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo -e "${RED}⚠️ 端口 $port: 被进程 $pid 占用${NC}"
    else
        echo -e "${GREEN}✅ 端口 $port: 可用${NC}"
    fi
done

echo ""

# 根据参数执行不同的清理操作
case "${1:-}" in
    "port"|"-p")
        if [ -n "$2" ]; then
            echo -e "${YELLOW}🔧 清理指定端口: $2${NC}"
            python3 "$CLEANUP_SCRIPT" --port "$2" --force
        else
            echo -e "${RED}❌ 请指定端口号${NC}"
            echo "用法: $0 port <端口号>"
            exit 1
        fi
        ;;
    "all"|"-a")
        echo -e "${YELLOW}🧹 清理所有常用测试端口${NC}"
        python3 "$CLEANUP_SCRIPT" --all-ports --force
        ;;
    "processes"|"-e")
        echo -e "${YELLOW}🧹 清理所有eMQTT-Bench进程${NC}"
        python3 "$CLEANUP_SCRIPT" --emqtt-processes --force
        ;;
    "force"|"-f")
        echo -e "${YELLOW}🧹 强制清理所有相关进程和端口${NC}"
        python3 "$CLEANUP_SCRIPT" --force
        ;;
    "help"|"-h"|"--help")
        echo -e "${YELLOW}用法:${NC}"
        echo "  $0                    # 交互式清理所有"
        echo "  $0 port <端口号>      # 清理指定端口"
        echo "  $0 all               # 清理所有常用端口"
        echo "  $0 processes         # 清理所有eMQTT-Bench进程"
        echo "  $0 force             # 强制清理所有"
        echo "  $0 help              # 显示帮助"
        echo ""
        echo -e "${YELLOW}示例:${NC}"
        echo "  $0 port 9090         # 清理端口9090"
        echo "  $0 all               # 清理所有常用端口"
        echo "  $0 force             # 强制清理所有"
        ;;
    *)
        # 默认：交互式清理
        echo -e "${YELLOW}🔧 开始交互式清理...${NC}"
        python3 "$CLEANUP_SCRIPT"
        ;;
esac

echo ""
echo -e "${GREEN}✅ 清理操作完成${NC}"
