# eMQTT-Bench 压测结果收集指南

## 概述

本指南详细介绍如何收集、分析和保存 eMQTT-Bench 的压测结果，包括多种数据收集方式和结果分析方法。

## 结果收集方式

### 1. 控制台输出

#### 基本统计信息
压测过程中，eMQTT-Bench 会在控制台实时显示统计信息：

```bash
# 启用控制台输出（默认）
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --log_to console
```

**输出示例**：
```
client(100), connected(100), failed(0), publish(1000), publish_failed(0)
client(100), connected(100), failed(0), publish(2000), publish_failed(0)
client(100), connected(100), failed(0), publish(3000), publish_failed(0)
```

#### 统计信息说明
- `client(N)`: 当前客户端数量
- `connected(N)`: 已连接客户端数量  
- `failed(N)`: 连接失败数量
- `publish(N)`: 已发布消息数量
- `publish_failed(N)`: 发布失败数量

### 2. QoE (Quality of Experience) 监控

#### 启用 QoE 跟踪
```bash
# 启用内存中的 QoE 跟踪
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --qoe true

# 启用 QoE 日志记录到文件
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --qoe true --qoelog /tmp/qoe.log
```

#### QoE 指标说明
- **TCP 握手延迟**: 建立 TCP 连接的时间
- **MQTT 握手延迟**: MQTT 协议握手的时间
- **连接延迟**: 完整连接建立的时间
- **订阅延迟**: 订阅操作完成的时间
- **发布延迟**: 消息发布的时间

#### QoE 输出示例
```
tcp, avg: 15ms, P95: 25ms, Max: 45ms
handshake, avg: 8ms, P95: 12ms, Max: 20ms  
connect, avg: 23ms, P95: 35ms, Max: 65ms
subscribe, avg: 5ms, P95: 8ms, Max: 15ms
publish, avg: 2ms, P95: 3ms, Max: 8ms
```

### 3. Prometheus 指标收集

#### 启用 Prometheus 监控
```bash
# 启用 Prometheus 指标收集
./emqtt_bench pub \
    -c 100 \
    -I 1000 \
    -t "test/topic" \
    --prometheus \
    --restapi 8080
```

#### 访问指标数据
```bash
# 获取所有指标
curl http://localhost:8080/metrics

# 获取特定指标
curl http://localhost:8080/metrics | grep mqtt_bench_connected
curl http://localhost:8080/metrics | grep mqtt_bench_publish_sent
```

### 4. 日志文件收集

#### 重定向控制台输出
```bash
# 保存控制台输出到文件
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" > benchmark_results.log 2>&1

# 同时显示在控制台和保存到文件
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" 2>&1 | tee benchmark_results.log
```

#### 关闭控制台输出
```bash
# 静默运行，只收集数据
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --log_to null
```

## 华为云 IoT 平台测试结果收集

### 1. 完整测试脚本

```bash
#!/bin/bash
# 华为云压测结果收集脚本

HOST="your-huawei-iot-host"
SECRET="your-device-secret"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="benchmark_results_$TIMESTAMP"

# 创建结果目录
mkdir -p "$RESULTS_DIR"

echo "=== 华为云 IoT 压测开始 ==="
echo "结果保存目录: $RESULTS_DIR"
echo "开始时间: $(date)"

# 测试1: 连接测试
echo "测试1: 连接测试"
./emqtt_bench conn \
    -h "$HOST" \
    -p 1883 \
    -c 1000 \
    -i 10 \
    --prefix "TestDevice" \
    --device-id "TestDevice-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    --prometheus \
    --restapi 8080 \
    --qoe true \
    --qoelog "$RESULTS_DIR/connection_qoe.log" \
    > "$RESULTS_DIR/connection_test.log" 2>&1 &

CONN_PID=$!
sleep 60
kill $CONN_PID 2>/dev/null

# 测试2: 发布测试
echo "测试2: 发布测试"
./emqtt_bench pub \
    -h "$HOST" \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --prefix "TestDevice" \
    --device-id "TestDevice-%09.9i" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 512 \
    --prometheus \
    --restapi 8081 \
    --qoe true \
    --qoelog "$RESULTS_DIR/publish_qoe.log" \
    > "$RESULTS_DIR/publish_test.log" 2>&1 &

PUB_PID=$!
sleep 60
kill $PUB_PID 2>/dev/null

# 收集 Prometheus 指标
echo "收集 Prometheus 指标..."
curl -s http://localhost:8080/metrics > "$RESULTS_DIR/connection_metrics.txt"
curl -s http://localhost:8081/metrics > "$RESULTS_DIR/publish_metrics.txt"

echo "测试完成！"
echo "结果保存在: $RESULTS_DIR"
```

### 2. 结果分析脚本

```python
#!/usr/bin/env python3
# 压测结果分析脚本

import re
import json
import matplotlib.pyplot as plt
from datetime import datetime

def parse_benchmark_log(log_file):
    """解析压测日志文件"""
    results = {
        'timestamps': [],
        'clients': [],
        'connected': [],
        'failed': [],
        'published': [],
        'publish_failed': []
    }
    
    with open(log_file, 'r') as f:
        for line in f:
            # 解析统计行
            match = re.search(r'client\((\d+)\), connected\((\d+)\), failed\((\d+)\), publish\((\d+)\), publish_failed\((\d+)\)', line)
            if match:
                results['clients'].append(int(match.group(1)))
                results['connected'].append(int(match.group(2)))
                results['failed'].append(int(match.group(3)))
                results['published'].append(int(match.group(4)))
                results['publish_failed'].append(int(match.group(5)))
                results['timestamps'].append(datetime.now())
    
    return results

def parse_qoe_log(qoe_file):
    """解析 QoE 日志文件"""
    qoe_data = {}
    
    with open(qoe_file, 'r') as f:
        for line in f:
            # 解析 QoE 统计行
            match = re.search(r'(\w+), avg: (\d+)ms, P95: (\d+)ms, Max: (\d+)ms', line)
            if match:
                metric = match.group(1)
                qoe_data[metric] = {
                    'avg': int(match.group(2)),
                    'p95': int(match.group(3)),
                    'max': int(match.group(4))
                }
    
    return qoe_data

def generate_report(results_dir):
    """生成测试报告"""
    report = {
        'test_time': datetime.now().isoformat(),
        'results_dir': results_dir
    }
    
    # 解析连接测试结果
    conn_log = f"{results_dir}/connection_test.log"
    if os.path.exists(conn_log):
        conn_results = parse_benchmark_log(conn_log)
        report['connection_test'] = {
            'max_clients': max(conn_results['clients']) if conn_results['clients'] else 0,
            'max_connected': max(conn_results['connected']) if conn_results['connected'] else 0,
            'total_failed': sum(conn_results['failed']) if conn_results['failed'] else 0
        }
    
    # 解析发布测试结果
    pub_log = f"{results_dir}/publish_test.log"
    if os.path.exists(pub_log):
        pub_results = parse_benchmark_log(pub_log)
        report['publish_test'] = {
            'max_clients': max(pub_results['clients']) if pub_results['clients'] else 0,
            'total_published': max(pub_results['published']) if pub_results['published'] else 0,
            'total_failed': sum(pub_results['publish_failed']) if pub_results['publish_failed'] else 0
        }
    
    # 解析 QoE 数据
    qoe_files = ['connection_qoe.log', 'publish_qoe.log']
    for qoe_file in qoe_files:
        qoe_path = f"{results_dir}/{qoe_file}"
        if os.path.exists(qoe_path):
            qoe_data = parse_qoe_log(qoe_path)
            report[qoe_file.replace('.log', '')] = qoe_data
    
    # 保存报告
    report_file = f"{results_dir}/test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"测试报告已生成: {report_file}")
    return report

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) != 2:
        print("用法: python3 analyze_results.py <results_directory>")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    if not os.path.exists(results_dir):
        print(f"错误: 目录 {results_dir} 不存在")
        sys.exit(1)
    
    report = generate_report(results_dir)
    print("分析完成！")
```

## 数据导出和分析

### 1. CSV 格式导出

```bash
# 导出 QoE 数据为 CSV
./emqtt_bench pub \
    -c 100 \
    -I 1000 \
    -t "test/topic" \
    --qoe dump \
    --qoelog /tmp/qoe.log

# 这会生成 qoe.log.csv 文件
```

### 2. JSON 格式导出

```bash
# 使用 jq 处理 Prometheus 指标
curl -s http://localhost:8080/metrics | \
    grep -E '^mqtt_bench_' | \
    jq -R 'split(" ") | {metric: .[0], value: .[1]}' > metrics.json
```

### 3. 实时监控脚本

```bash
#!/bin/bash
# 实时监控脚本

while true; do
    echo "=== $(date) ==="
    
    # 获取当前指标
    curl -s http://localhost:8080/metrics | grep -E '^mqtt_bench_(connected|publish_sent|publish_failed)' | \
        while read line; do
            echo "$line"
        done
    
    echo ""
    sleep 5
done
```

## 最佳实践

### 1. 结果收集策略
- **多维度收集**: 同时使用控制台输出、QoE 日志和 Prometheus 指标
- **时间戳记录**: 为所有测试添加时间戳，便于对比分析
- **目录组织**: 按测试类型和时间组织结果文件

### 2. 数据保存
```bash
# 创建结构化的结果目录
mkdir -p "benchmark_results/$(date +%Y%m%d)/connection_test"
mkdir -p "benchmark_results/$(date +%Y%m%d)/publish_test"
mkdir -p "benchmark_results/$(date +%Y%m%d)/metrics"
```

### 3. 自动化分析
- 使用脚本自动解析日志文件
- 生成标准化的测试报告
- 设置告警阈值和异常检测

### 4. 长期存储
- 定期归档历史测试数据
- 建立测试结果数据库
- 维护性能基线数据

## 总结

通过合理配置和使用 eMQTT-Bench 的结果收集功能，您可以：

1. **全面监控** 压测过程中的各项指标
2. **深度分析** 系统性能瓶颈和优化点
3. **历史对比** 不同版本和配置的性能差异
4. **趋势预测** 系统容量和性能变化趋势

建议根据实际需求选择合适的收集方式，并建立标准化的分析流程。
