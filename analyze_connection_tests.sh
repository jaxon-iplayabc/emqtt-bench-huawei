#!/bin/bash

# eMQTT-Bench 连接测试数据分析脚本
# 用于分析Prometheus指标数据并生成丰富的可视化报表

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 eMQTT-Bench 连接测试数据分析器${NC}"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 python3${NC}"
    exit 1
fi

# 检查必要的Python包
echo -e "${YELLOW}📦 检查Python依赖包...${NC}"
python3 -c "import pandas, matplotlib, seaborn, numpy" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  正在安装必要的Python包...${NC}"
    pip3 install pandas matplotlib seaborn numpy
}

# 检查分析脚本
if [ ! -f "connection_test_analyzer.py" ]; then
    echo -e "${RED}❌ 错误: 未找到 connection_test_analyzer.py${NC}"
    exit 1
fi

# 查找指标文件
echo -e "${YELLOW}🔍 查找Prometheus指标文件...${NC}"
METRICS_FILES=($(ls metrics_connection_*.txt 2>/dev/null || true))

if [ ${#METRICS_FILES[@]} -eq 0 ]; then
    echo -e "${RED}❌ 错误: 未找到任何 metrics_connection_*.txt 文件${NC}"
    echo "请确保在项目根目录下运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ 找到 ${#METRICS_FILES[@]} 个指标文件:${NC}"
for file in "${METRICS_FILES[@]}"; do
    echo "  - $file"
done

# 设置输出目录
OUTPUT_DIR="connection_test_reports_$(date +%Y%m%d_%H%M%S)"

echo -e "${YELLOW}📊 开始分析数据...${NC}"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 运行分析
python3 connection_test_analyzer.py "${METRICS_FILES[@]}" -o "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 分析完成！${NC}"
    echo -e "${BLUE}📁 报告文件保存在: $OUTPUT_DIR${NC}"
    echo -e "${BLUE}🌐 HTML报告: $OUTPUT_DIR/connection_test_report.html${NC}"
    echo ""
    
    # 尝试打开HTML报告
    if command -v open &> /dev/null; then
        echo -e "${YELLOW}🔗 正在打开HTML报告...${NC}"
        open "$OUTPUT_DIR/connection_test_report.html"
    elif command -v xdg-open &> /dev/null; then
        echo -e "${YELLOW}🔗 正在打开HTML报告...${NC}"
        xdg-open "$OUTPUT_DIR/connection_test_report.html"
    else
        echo -e "${YELLOW}💡 提示: 可以手动打开 $OUTPUT_DIR/connection_test_report.html 查看报告${NC}"
    fi
else
    echo -e "${RED}❌ 分析失败${NC}"
    exit 1
fi
