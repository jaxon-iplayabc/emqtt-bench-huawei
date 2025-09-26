# eMQTT-Bench 压测报告

**测试时间**: Tue Sep 23 17:32:15 CST 2025
**测试环境**: 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com:1883
**客户端数量**: 5
**消息间隔**: 1000ms

## 测试配置

- MQTT服务器: 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com:1883
- 客户端数量: 5
- 消息间隔: 1000ms
- Prometheus端口范围: 9090 - 9094

## 测试结果

### 1. 连接测试
- 端口: 9090
- 指标文件: metrics_connection_*.txt

## 指标说明

### 连接相关指标
- `mqtt_bench_connected`: 已建立的连接数
- `mqtt_bench_connect_failed`: 连接失败数
- `mqtt_bench_disconnected`: 断开连接数

### 消息相关指标
- `mqtt_bench_publish_sent`: 已发送的发布消息数
- `mqtt_bench_publish_received`: 已接收的发布消息数
- `mqtt_bench_subscribe_sent`: 已发送的订阅消息数
- `mqtt_bench_subscribe_received`: 已接收的订阅消息数

### 延迟相关指标
- `mqtt_client_tcp_handshake_duration`: TCP握手延迟
- `mqtt_client_handshake_duration`: MQTT握手延迟
- `mqtt_client_connect_duration`: 连接建立延迟
- `mqtt_client_subscribe_duration`: 订阅延迟

## 使用方法

### 查看实时指标
```bash
# 查看连接测试指标
curl http://localhost:9090/metrics

# 查看发布测试指标
curl http://localhost:9091/metrics

# 查看订阅测试指标
curl http://localhost:9092/metrics

# 查看华为云测试指标
curl http://localhost:9093/metrics

# 查看自定义测试指标
curl http://localhost:9094/metrics
```

### 使用 Python 工具收集指标
```bash
cd metrics/
uv run metrics_collector.py collect --summary
```

### 集成 Prometheus
在 `prometheus.yml` 中添加以下配置：

```yaml
scrape_configs:
  - job_name: 'emqtt-bench-connection'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-publish'
    static_configs:
      - targets: ['localhost:9091']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-subscribe'
    static_configs:
      - targets: ['localhost:9092']
    scrape_interval: 5s
    
  - job_name: 'emqtt-bench-huawei'
    static_configs:
      - targets: ['localhost:9093']
    scrape_interval: 5s
```

## 文件清单

- -rw-r--r--  1 admin  staff  125443 Sep 23 17:20 metrics_connection_20250923_172051.txt
- -rw-r--r--  1 admin  staff  125473 Sep 23 17:32 metrics_connection_20250923_173215.txt

