# eMQTT-Bench 压测结果显示系统使用指南

## 📋 概述

eMQTT-Bench 压测结果显示系统是一个专门为 eMQTT-Bench 压测工具设计的综合监控和展示解决方案。它提供了实时监控、Web仪表盘和详细报告生成功能，帮助用户全面了解压测过程中的性能表现。

## 🚀 主要功能

### 1. 实时监控显示
- **实时性能指标**: 连接成功率、消息吞吐量、延迟等关键指标
- **状态指示器**: 直观的颜色编码状态显示
- **性能评级**: 自动计算性能评分和等级
- **优化建议**: 基于当前性能提供改进建议

### 2. Web仪表盘
- **响应式界面**: 支持多设备访问
- **实时数据更新**: 自动刷新显示最新数据
- **交互式图表**: 直观的数据可视化
- **历史数据查看**: 支持查看历史性能趋势

### 3. 详细报告生成
- **性能摘要**: 关键指标的统计摘要
- **趋势分析**: 性能变化趋势分析
- **对比分析**: 与历史测试结果对比
- **优化建议**: 基于分析结果的改进建议

## 📊 监控指标说明

### 连接性能指标
- **connect_succ**: 成功建立的连接数
- **connect_fail**: 连接失败数
- **connect_retried**: 重连尝试次数
- **connection_refused**: 连接被拒绝数
- **connection_timeout**: 连接超时数
- **unreachable**: 网络不可达错误数

### 消息性能指标
- **pub**: 发送的消息总数
- **recv**: 接收的消息总数
- **pub_fail**: 发送失败的消息数
- **sub**: 成功订阅数
- **sub_fail**: 订阅失败数
- **pub_overrun**: 消息溢出数

### 延迟性能指标
- **publish_latency**: 消息发布延迟
- **mqtt_client_connect_duration**: 连接建立延迟
- **mqtt_client_handshake_duration**: 握手延迟
- **e2e_latency**: 端到端延迟

## 🛠️ 安装和配置

### 1. 环境要求
```bash
# Python 3.8+
pip install requests rich matplotlib pandas numpy
```

### 2. 启动 eMQTT-Bench
```bash
# 启动带Prometheus监控的eMQTT-Bench
./emqtt_bench conn \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 10 \
    -i 100 \
    --prefix speaker \
    -P 12345678 \
    --huawei-auth \
    --prometheus \
    --restapi 9090
```

## 📖 使用方法

### 1. 实时监控模式
```bash
# 基本用法
python benchmark_display_system.py --mode live --test-type conn

# 指定监控端口
python benchmark_display_system.py --mode live --ports 9090 9091 9092

# 自定义刷新间隔
python benchmark_display_system.py --mode live --refresh-interval 2.0
```

**实时监控界面说明:**
- 🟢 绿色: 性能良好
- 🟡 黄色: 性能一般，需要关注
- 🔴 红色: 性能较差，需要优化

### 2. Web仪表盘模式
```bash
# 启动Web仪表盘
python benchmark_display_system.py --mode web --web-port 8080

# 访问地址
http://localhost:8080
```

**Web仪表盘功能:**
- 自动打开浏览器
- 实时数据更新（每5秒）
- 响应式设计，支持移动设备
- 多指标卡片式展示

### 3. 报告生成模式
```bash
# 生成HTML报告
python benchmark_display_system.py --mode report --output my_report.html

# 使用默认文件名
python benchmark_display_system.py --mode report
```

**报告内容包括:**
- 测试配置信息
- 性能指标摘要
- 趋势分析图表
- 优化建议

## 🎯 使用示例

### 完整演示流程
```bash
# 1. 运行演示脚本
python display_example.py

# 2. 选择演示功能
# - 实时显示
# - Web仪表盘  
# - 报告生成
```

### 自定义监控配置
```python
from benchmark_display_system import MetricsCollector, RealTimeDisplay

# 创建指标收集器
collector = MetricsCollector([9090, 9091, 9092])

# 创建实时显示
display = RealTimeDisplay(collector)

# 启动监控
display.start_live_display("conn", refresh_interval=1.0)
```

## 📈 性能评估标准

### 连接成功率评级
- **A+ (95-100%)**: 优秀
- **A (90-95%)**: 良好
- **B (80-90%)**: 一般
- **C (70-80%)**: 较差
- **D (<70%)**: 需要优化

### 延迟性能评级
- **优秀 (<100ms)**: 延迟很低
- **良好 (100-500ms)**: 延迟可接受
- **一般 (500-1000ms)**: 延迟较高
- **较差 (>1000ms)**: 延迟过高

### 错误率评级
- **优秀 (0%)**: 无错误
- **良好 (0-1%)**: 错误率很低
- **一般 (1-5%)**: 错误率可接受
- **较差 (>5%)**: 错误率过高

## 🔧 故障排除

### 常见问题

1. **无法连接到Prometheus端点**
   ```
   错误: 无法连接到 http://localhost:9090/metrics
   解决: 确保eMQTT-Bench已启动并启用了--prometheus和--restapi参数
   ```

2. **Web仪表盘无法访问**
   ```
   错误: 端口被占用
   解决: 使用--web-port参数指定其他端口
   ```

3. **指标数据为空**
   ```
   错误: No metrics available
   解决: 等待eMQTT-Bench启动完成，或检查Prometheus端口配置
   ```

### 调试模式
```bash
# 启用详细日志
python benchmark_display_system.py --mode live --verbose

# 检查端口连通性
curl http://localhost:9090/metrics
```

## 📚 高级功能

### 1. 自定义指标阈值
修改 `display_config.json` 中的 `performance_thresholds` 配置:

```json
{
  "performance_thresholds": {
    "connection_success_rate": {
      "excellent": 99,
      "good": 95,
      "warning": 80,
      "critical": 50
    }
  }
}
```

### 2. 集成到CI/CD
```bash
# 在CI/CD中生成报告
python benchmark_display_system.py --mode report --output ci_report.html

# 检查性能是否达标
if [ $? -eq 0 ]; then
    echo "性能测试通过"
else
    echo "性能测试失败"
    exit 1
fi
```

### 3. 批量测试分析
```python
# 分析多个测试结果
from benchmark_display_system import ReportGenerator, MetricsCollector

collector = MetricsCollector([9090])
# 收集多个测试的数据
for test in tests:
    collector.collect_metrics(test.type)

generator = ReportGenerator(collector)
generator.generate_report("batch_analysis.html")
```

## 🤝 贡献和支持

### 报告问题
如果您在使用过程中遇到问题，请提供以下信息:
- 操作系统版本
- Python版本
- eMQTT-Bench版本
- 错误日志
- 复现步骤

### 功能建议
欢迎提出新功能建议，包括:
- 新的监控指标
- 改进的用户界面
- 额外的报告格式
- 性能优化建议

## 📄 许可证

本项目遵循 Apache 2.0 许可证。

## 👨‍💻 作者

**Jaxon** - 项目创建者和维护者

---

*最后更新: 2025年1月27日*

