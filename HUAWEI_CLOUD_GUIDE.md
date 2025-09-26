# 华为云 IoT 平台 emqtt-bench 完整使用指南

## 概述

本指南介绍如何使用 emqtt-bench 对华为云 IoT 平台进行性能测试。emqtt-bench 已深度集成华为云 IoT 平台的认证机制，支持大规模设备并发测试。

## 快速开始

### 基础命令格式

```bash
./emqtt_bench pub \
    -h <华为云MQTT服务器地址> \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    --limit 5
```

### 关键参数说明

- `--huawei-auth`: 启用华为云认证模式（**必须**）
- `-P "12345678"`: 设备密钥（**不需要** `huawei:` 前缀）
- `--prefix "Speaker"`: 设备ID前缀
- `-t '$oc/devices/%u/sys/properties/report'`: 华为云标准topic格式

## 华为云认证机制

### 认证参数自动生成

当使用 `--huawei-auth` 时，系统自动生成：

- **ClientID**: `{device_id}_0_0_{timestamp}`
- **Username**: `{device_id}`（与设备ID相同）
- **Password**: `HMAC-SHA256(timestamp, secret)`

### 设备ID生成规则

**优先级顺序**：
1. `-u` 参数：如果指定，使用 username 作为设备ID
2. `--prefix` 参数：使用 `{prefix}-{9位数字}` 格式
3. 默认格式：使用 `device-{9位数字}` 格式

**示例**：
- `--prefix "Speaker"` → Speaker-000000001, Speaker-000000002, ...
- `--prefix "Device"` → Device-000000001, Device-000000002, ...
- 无 prefix → device-000000001, device-000000002, ...

## 使用场景

### 1. 单设备测试

```bash
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    --limit 10
```

### 2. 多设备并发测试

```bash
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    -s 512
```

### 3. 使用独立设备ID

```bash
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 50 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'SmartSpeaker-%i' \
    -P "12345678" \
    --huawei-auth \
    -s 256
```

### 4. 使用真实数据模板

```bash
# 先生成测试数据
cd huawei && python3 payload_generator.py && cd ..

# 使用生成的数据
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 50 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    --message 'template://huawei/huawei_cloud_payload_example.json'
```

### 5. 性能监控测试

```bash
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1000 \
    -i 5 \
    -I 10000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    --prometheus \
    --qoe true
```

## Topic 变量支持

### 支持的变量

- `%u`: username（在华为云模式下等于 device_id）
- `%d`: device_id（设备ID）
- `%i`: 客户端序号
- `%c`: client_id
- `%s`: 消息序号（仅在 pub 中可用）
- `%rand_N`: 随机数，范围 1 到 N

### 设备ID变量

- `%i`: 客户端序号
- `%rand_N`: 随机数

**示例**：
```bash
--device-id 'Device-%i'        # Device-1, Device-2, ...
--device-id 'Sensor-%rand_100' # Sensor-1, Sensor-45, ...
```

## 性能测试建议

### 小规模测试（1-100设备）
```bash
./emqtt_bench pub -h <host> -c 10 -I 5000 ...
```

### 中等规模测试（100-1000设备）
```bash
./emqtt_bench pub -h <host> -c 500 -i 10 -I 10000 ...
```

### 大规模测试（1000+设备）
```bash
./emqtt_bench pub -h <host> -c 5000 -i 5 -I 30000 ...
```

## 监控和分析

### 启用 Prometheus 监控
```bash
./emqtt_bench pub \
    ... \
    --prometheus \
    --restapi 8080
```
然后访问 http://localhost:8080/metrics

### 启用 QoE 跟踪
```bash
./emqtt_bench pub \
    ... \
    --qoe true \
    --qoelog huawei_test.qoe
```

### 导出 QoE 数据
```bash
./emqtt_bench pub --qoe dump --qoelog huawei_test.qoe
```

## SSL/TLS 支持

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 8883 \
    --ssl \
    --cacertfile /path/to/ca.pem \
    -c 100 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    -s 256
```

## 故障排查

### 认证失败
- 确认设备已在华为云平台注册
- 检查设备密钥是否正确
- 确保系统时间准确（误差<1小时）

### 连接失败
- 检查网络连接
- 确认服务器地址和端口
- 查看防火墙设置

### 常见错误

1. **`bad_username_or_password`**
   - 检查设备是否已注册
   - 确认设备密钥正确
   - 验证系统时间准确

2. **`connection_refused`**
   - 检查服务器地址和端口
   - 确认网络连接正常

3. **Topic 中出现 `undefined`**
   - 检查 topic 变量是否正确
   - 确认设备ID生成逻辑

## 最佳实践

1. **时间同步**：确保系统时间准确，华为云使用时间戳进行认证
2. **设备ID格式**：使用 `{prefix}-{9位数字}` 格式
3. **密钥安全**：妥善保管设备密钥，避免泄露
4. **批量测试**：使用 `%i` 变量可以批量创建不同的设备
5. **监控**：生产环境建议启用 Prometheus 监控

## 兼容性

- ✅ 完全向后兼容
- ✅ 支持所有现有功能
- ✅ 支持大规模并发测试
- ✅ 支持性能监控和QoE跟踪

## 技术实现

### Erlang 原生认证
- 无需依赖 Python 脚本
- 性能更优，无进程调用开销
- 支持 `--huawei-auth` 自动认证

### 认证算法
- 使用 HMAC-SHA256 算法
- 时间戳格式：YYYYMMDDHH（本地时间）
- ClientID 格式：`{device_id}_0_0_{timestamp}`

## 相关文档

- [设备ID使用指南](DEVICE_ID_GUIDE.md)
- [Prometheus监控指南](PROMETHEUS_MONITORING_GUIDE.md)
- [连接测试指南](CONNECTION_TEST_GUIDE.md)
- [压测结果收集指南](BENCHMARK_RESULTS_COLLECTION.md)
