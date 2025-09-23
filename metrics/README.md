# eMQTT-Bench Prometheus 指标收集工具

这是一个用于收集和分析 eMQTT-Bench Prometheus 指标数据的 Python 工具。

## 功能特性

- 🔍 **指标收集**: 从多个端口收集 Prometheus 格式的指标数据
- 📊 **数据分析**: 自动过滤和分析 eMQTT-Bench 相关指标
- 💾 **数据导出**: 支持 JSON 和 CSV 格式导出
- 📈 **实时监控**: 实时监控指标变化
- 🎯 **华为云支持**: 专门支持华为云 IoT 平台测试指标

## 安装和设置

### 1. 激活虚拟环境
```bash
cd metrics/
source .venv/bin/activate
```

### 2. 安装依赖
```bash
uv sync
```

## 使用方法

### 基本命令

#### 收集指标数据
```bash
# 收集默认端口 (8080-8083) 的指标
uv run metrics_collector.py collect

# 收集指定端口的指标
uv run metrics_collector.py collect --ports 8080 8081

# 指定主机地址
uv run metrics_collector.py collect --host 192.168.1.100

# 只导出 JSON 格式
uv run metrics_collector.py collect --format json

# 显示指标摘要
uv run metrics_collector.py collect --summary
```

#### 实时监控
```bash
# 监控端口 8080
uv run metrics_collector.py monitor --port 8080

# 监控指定间隔和持续时间
uv run metrics_collector.py monitor --port 8080 --interval 3 --duration 60
```

#### 分析已保存的数据
```bash
# 分析 JSON 文件
uv run metrics_collector.py analyze metrics_data/metrics_20241219_143022.json
```

### 使用示例

#### 1. 华为云 IoT 平台测试监控
```bash
# 启动华为云测试 (在项目根目录)
./prometheus_example.sh

# 在另一个终端收集指标
uv run metrics_collector.py collect --ports 8083 --summary
```

#### 2. 实时监控所有测试
```bash
# 监控所有端口
uv run metrics_collector.py monitor --port 8080 --interval 5
```

#### 3. 批量收集和分析
```bash
# 收集所有端口数据并导出
uv run metrics_collector.py collect --ports 8080 8081 8082 8083 --format both --summary
```

## 指标说明

### 连接相关指标
- `mqtt_bench_connected`: 已建立的连接数
- `mqtt_bench_connect_failed`: 连接失败数
- `mqtt_bench_disconnected`: 断开连接数

### 消息相关指标
- `mqtt_bench_publish_sent`: 已发送的发布消息数
- `mqtt_bench_publish_received`: 已接收的发布消息数
- `mqtt_bench_publish_failed`: 发布失败数
- `mqtt_bench_subscribe_sent`: 已发送的订阅消息数
- `mqtt_bench_subscribe_received`: 已接收的订阅消息数

### 延迟相关指标
- `mqtt_client_tcp_handshake_duration`: TCP握手延迟
- `mqtt_client_handshake_duration`: MQTT握手延迟
- `mqtt_client_connect_duration`: 连接建立延迟
- `mqtt_client_subscribe_duration`: 订阅延迟

## 输出文件

### JSON 格式
```json
{
  "8080": [
    {
      "timestamp": "2024-12-19T14:30:22.123456",
      "name": "mqtt_bench_connected",
      "value": 100.0,
      "labels": {"port": "8080"},
      "help_text": "Number of connected clients",
      "metric_type": "counter"
    }
  ]
}
```

### CSV 格式
```csv
timestamp,port,name,value,labels,help_text,metric_type
2024-12-19T14:30:22.123456,8080,mqtt_bench_connected,100.0,"{""port"": ""8080""}",Number of connected clients,counter
```

## 编程接口

### 基本使用
```python
from metrics_collector import PrometheusMetricsCollector, MetricsAnalyzer

# 创建收集器
collector = PrometheusMetricsCollector("http://localhost")

# 收集指标
metrics = collector.fetch_metrics(8080)

# 分析指标
analyzer = MetricsAnalyzer()
filtered = analyzer.filter_mqtt_bench_metrics(metrics)
summary = analyzer.get_metric_summary(filtered)
```

### 运行示例
```bash
uv run example_usage.py
```

## 与 eMQTT-Bench 集成

### 1. 启动 eMQTT-Bench 测试
```bash
# 在项目根目录
./prometheus_example.sh
```

### 2. 收集指标
```bash
# 在 metrics 目录
uv run metrics_collector.py collect --summary
```

### 3. 实时监控
```bash
uv run metrics_collector.py monitor --port 8080
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   ```
   错误: 无法连接到 http://localhost:8080/metrics: Connection refused
   ```
   - 确保 eMQTT-Bench 正在运行
   - 检查端口是否正确
   - 确认使用了 `--prometheus` 和 `--restapi` 参数

2. **没有找到指标**
   ```
   未找到 eMQTT-Bench 指标数据
   ```
   - 确保使用了 `--prometheus` 参数
   - 检查测试是否正在运行
   - 等待一段时间让指标数据积累

3. **权限错误**
   ```
   Permission denied
   ```
   - 确保有写入输出目录的权限
   - 检查文件路径是否正确

## 扩展功能

### 自定义指标过滤
```python
# 只关注特定指标
custom_metrics = ['mqtt_bench_connected', 'mqtt_bench_publish_sent']
filtered = [m for m in metrics if m.name in custom_metrics]
```

### 数据可视化
```python
import matplotlib.pyplot as plt

# 绘制连接数趋势
timestamps = [m.timestamp for m in metrics if m.name == 'mqtt_bench_connected']
values = [m.value for m in metrics if m.name == 'mqtt_bench_connected']
plt.plot(timestamps, values)
plt.show()
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具！

## 许可证

MIT License
