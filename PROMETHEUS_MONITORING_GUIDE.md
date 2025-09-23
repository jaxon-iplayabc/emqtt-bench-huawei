# eMQTT-Bench Prometheus 监控指南

## 概述

eMQTT-Bench 提供了强大的 Prometheus 监控功能，可以实时收集和展示压测过程中的各种性能指标。本指南将详细介绍如何配置和使用这些监控功能。

## 功能特性

### 1. 实时指标收集
- **连接统计**: 连接数、连接成功率、连接失败数
- **消息统计**: 发布消息数、订阅消息数、消息吞吐量
- **延迟统计**: TCP握手延迟、MQTT握手延迟、连接延迟、订阅延迟
- **QoE指标**: 端到端质量体验指标

### 2. HTTP API 端点
- **REST API**: 提供 `/metrics` 端点供 Prometheus 抓取
- **灵活配置**: 支持自定义监听地址和端口
- **标准格式**: 输出标准的 Prometheus 文本格式

## 配置选项

### 基本配置

```bash
# 启用 Prometheus 监控
--prometheus

# 启用 REST API 端点
--restapi 8080                    # 监听所有接口的8080端口
--restapi 127.0.0.1:8080         # 监听指定IP和端口
```

### 完整示例

```bash
# 发布测试 + Prometheus 监控
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "Speaker" \
    --device-id "Speaker-%09.9i" \
    -P "huawei:12345678" \
    --huawei-auth \
    -s 256 \
    --prometheus \
    --restapi 8080 \
    --qoe true
```

## 监控指标详解

### 1. 连接相关指标

| 指标名称 | 类型 | 描述 |
|---------|------|------|
| `mqtt_bench_connected` | Counter | 已建立的连接数 |
| `mqtt_bench_connect_failed` | Counter | 连接失败数 |
| `mqtt_bench_disconnected` | Counter | 断开连接数 |

### 2. 消息相关指标

| 指标名称 | 类型 | 描述 |
|---------|------|------|
| `mqtt_bench_publish_sent` | Counter | 已发送的发布消息数 |
| `mqtt_bench_publish_received` | Counter | 已接收的发布消息数 |
| `mqtt_bench_subscribe_sent` | Counter | 已发送的订阅消息数 |
| `mqtt_bench_subscribe_received` | Counter | 已接收的订阅消息数 |

### 3. 延迟相关指标

| 指标名称 | 类型 | 描述 |
|---------|------|------|
| `mqtt_client_tcp_handshake_duration` | Histogram | TCP握手延迟 (ms) |
| `mqtt_client_handshake_duration` | Histogram | MQTT握手延迟 (ms) |
| `mqtt_client_connect_duration` | Histogram | 连接建立延迟 (ms) |
| `mqtt_client_subscribe_duration` | Histogram | 订阅延迟 (ms) |

### 4. QoE 质量指标

| 指标名称 | 类型 | 描述 |
|---------|------|------|
| `mqtt_bench_qoe_*` | Various | 端到端质量体验指标 |

## 使用方法

### 1. 启动监控

```bash
# 启动带监控的压测
./emqtt_bench pub \
    -c 50 \
    -I 1000 \
    -t "test/topic" \
    --prometheus \
    --restapi 8080
```

### 2. 访问指标

```bash
# 直接访问指标端点
curl http://localhost:8080/metrics

# 查看特定指标
curl http://localhost:8080/metrics | grep mqtt_bench_connected
```

### 3. 集成 Prometheus

在 `prometheus.yml` 中添加配置：

```yaml
scrape_configs:
  - job_name: 'emqtt-bench'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 5s
    metrics_path: /metrics
```

### 4. Grafana 仪表板

可以创建 Grafana 仪表板来可视化这些指标：

```json
{
  "dashboard": {
    "title": "eMQTT-Bench 性能监控",
    "panels": [
      {
        "title": "连接数",
        "type": "graph",
        "targets": [
          {
            "expr": "mqtt_bench_connected"
          }
        ]
      },
      {
        "title": "消息吞吐量",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(mqtt_bench_publish_sent[1m])"
          }
        ]
      }
    ]
  }
}
```

## 高级配置

### 1. 自定义监听地址

```bash
# 只监听本地回环
--restapi 127.0.0.1:8080

# 监听所有网络接口
--restapi 0.0.0.0:8080
```

### 2. 结合 QoE 监控

```bash
# 启用 QoE 跟踪和日志
--prometheus \
--qoe true \
--qoelog /tmp/qoe.log
```

### 3. 多实例监控

```bash
# 实例1
./emqtt_bench pub --prometheus --restapi 8080 &

# 实例2  
./emqtt_bench pub --prometheus --restapi 8081 &

# 实例3
./emqtt_bench pub --prometheus --restapi 8082 &
```

## 实际应用场景

### 1. 华为云 IoT 平台测试

```bash
#!/bin/bash
# 华为云压测 + 监控

HOST="your-huawei-iot-host"
SECRET="your-device-secret"

./emqtt_bench pub \
    -h "$HOST" \
    -p 1883 \
    -c 1000 \
    -i 10 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "TestDevice" \
    --device-id "TestDevice-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 512 \
    --prometheus \
    --restapi 8080 \
    --qoe true \
    --qoelog /tmp/huawei_qoe.log
```

### 2. 性能基准测试

```bash
#!/bin/bash
# 性能基准测试脚本

echo "开始性能基准测试..."

# 测试1: 1000个连接
./emqtt_bench conn \
    -c 1000 \
    -i 10 \
    --prometheus \
    --restapi 8080 &

sleep 60
kill %1

# 测试2: 消息发布
./emqtt_bench pub \
    -c 100 \
    -I 100 \
    -t "benchmark/topic" \
    --prometheus \
    --restapi 8081 &

sleep 60  
kill %1

echo "基准测试完成，查看指标："
echo "连接测试: http://localhost:8080/metrics"
echo "发布测试: http://localhost:8081/metrics"
```

## 故障排除

### 1. 常见问题

**问题**: 无法访问 `/metrics` 端点
```bash
# 检查端口是否被占用
netstat -tlnp | grep 8080

# 检查防火墙设置
sudo ufw status
```

**问题**: 指标数据不更新
```bash
# 检查 Prometheus 是否启用
curl http://localhost:8080/metrics | head -20

# 检查应用日志
./emqtt_bench pub --prometheus --restapi 8080 --log_to console
```

### 2. 性能优化

```bash
# 减少监控开销
--prometheus \
--restapi 8080 \
--log_to null  # 关闭控制台日志

# 调整抓取间隔
# 在 prometheus.yml 中设置较长的 scrape_interval
```

## 最佳实践

### 1. 监控策略
- 使用独立的监控端口，避免与业务端口冲突
- 设置合理的抓取间隔（5-15秒）
- 结合 QoE 日志进行深度分析

### 2. 告警配置
```yaml
# prometheus.yml 告警规则
groups:
  - name: emqtt-bench
    rules:
      - alert: HighConnectionFailureRate
        expr: rate(mqtt_bench_connect_failed[5m]) > 0.1
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "连接失败率过高"
```

### 3. 数据保留
- 设置合适的数据保留策略
- 定期导出重要指标数据
- 使用 QoE 日志进行离线分析

## 总结

eMQTT-Bench 的 Prometheus 监控功能为 MQTT 性能测试提供了强大的可观测性。通过合理配置和使用这些功能，您可以：

1. **实时监控** 压测过程中的关键指标
2. **深度分析** 系统性能和瓶颈
3. **可视化展示** 测试结果和趋势
4. **告警通知** 异常情况

建议在生产环境测试前，先在开发环境充分验证监控配置的有效性。
