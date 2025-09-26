#!/bin/bash
# eMQTT-Bench 快速测试启动脚本
# 一键运行所有测试功能

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 eMQTT-Bench 快速测试启动器${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${YELLOW}✨ 一个命令完成所有测试功能${NC}"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 检查uv是否安装
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✅ 使用 uv 运行测试${NC}"
    echo ""
    # 检查虚拟环境
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ 激活虚拟环境${NC}"
        source .venv/bin/activate
    fi
    
    # 使用uv运行
    uv run python main.py "$@"
else
    echo -e "${YELLOW}⚠️  uv 未安装，使用 python3 运行${NC}"
    echo -e "${YELLOW}💡 建议安装 uv: pip install uv${NC}"
    echo ""
    
    # 检查虚拟环境
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ 激活虚拟环境${NC}"
        source .venv/bin/activate
    fi
    
    # 使用python3运行
    python3 main.py "$@"
fi

echo ""
echo -e "${GREEN}✅ 测试完成${NC}"
echo -e "${YELLOW}📊 查看生成的HTML报告了解详细结果${NC}"
