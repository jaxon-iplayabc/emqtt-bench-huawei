#!/bin/bash
# eMQTT-Bench 指标收集快速开始脚本
# 作者: Jaxon
# 日期: 2024-12-19

echo "=== eMQTT-Bench 指标收集快速开始 ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "metrics_collector.py" ]; then
    echo "错误: 请在 metrics 目录下运行此脚本"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "安装依赖..."
uv sync

echo ""
echo "=== 使用方法 ==="
echo ""
echo "1. 基本指标收集:"
echo "   uv run metrics_collector.py collect --summary"
echo ""
echo "2. 实时监控:"
echo "   uv run metrics_collector.py monitor --port 9090"
echo ""
echo "3. 华为云测试监控:"
echo "   uv run metrics_collector.py collect --ports 9093 --summary"
echo ""
echo "4. 运行示例:"
echo "   uv run example_usage.py"
echo ""
echo "=== 开始使用 ==="
echo ""

# 检查是否有 eMQTT-Bench 在运行
echo "检查 eMQTT-Bench 服务..."
if curl -s http://localhost:9090/metrics > /dev/null 2>&1; then
    echo "✅ 发现端口 9090 的 eMQTT-Bench 服务"
    echo ""
    echo "开始收集指标..."
    uv run metrics_collector.py collect --ports 9090 --summary
else
    echo "❌ 未发现 eMQTT-Bench 服务"
    echo ""
    echo "请先启动 eMQTT-Bench 测试:"
    echo "  cd .."
    echo "  ./prometheus_example.sh"
    echo ""
    echo "然后在另一个终端运行:"
    echo "  cd metrics"
    echo "  ./quick_start.sh"
fi
