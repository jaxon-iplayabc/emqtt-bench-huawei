# 华为云广播测试指南

## 概述

本指南介绍如何使用华为云IoTDA广播功能进行端到端测试。系统包含三个主要组件：

1. **广播发送器** (`broadcast.py`) - 循环发送广播消息到指定主题
2. **订阅测试器** (`huawei_subscribe_test.py`) - 订阅广播主题并接收消息
3. **集成测试器** (`huawei_broadcast_integration.py`) - 同时运行发送和订阅测试

## 功能特性

- ✅ 支持循环发送广播消息
- ✅ 支持设备订阅广播主题
- ✅ 支持端到端消息传输验证
- ✅ 支持实时消息统计
- ✅ 支持优雅的进程管理
- ✅ 支持配置文件管理

## 快速开始

### 1. 环境准备

确保已安装必要的Python包：

```bash
pip install paho-mqtt huaweicloudsdkcore huaweicloudsdkiotda
```

### 2. 配置华为云参数

编辑 `huawei_broadcast_config.json` 文件：

```json
{
  "mqtt_host": "你的MQTT服务器地址",
  "mqtt_port": 1883,
  "device_prefix": "你的设备前缀",
  "device_secret": "你的设备密钥",
  "huawei_ak": "你的访问密钥ID",
  "huawei_sk": "你的访问密钥Secret",
  "huawei_endpoint": "你的IoTDA端点",
  "huawei_region": "cn-north-4",
  "broadcast_topic": "$oc/broadcast/test",
  "broadcast_interval": 5,
  "test_duration": 60
}
```

### 3. 运行集成测试

```bash
# 使用配置文件
python huawei_broadcast_integration.py --config huawei_broadcast_config.json

# 或使用命令行参数
python huawei_broadcast_integration.py \
  --mqtt-host "你的MQTT服务器" \
  --device-prefix "你的设备前缀" \
  --device-secret "你的设备密钥" \
  --huawei-ak "你的AK" \
  --huawei-sk "你的SK" \
  --huawei-endpoint "你的端点"
```

## 详细使用说明

### 广播发送器 (broadcast.py)

单独运行广播发送器：

```bash
# 循环发送广播
python broadcast.py \
  --ak "你的AK" \
  --sk "你的SK" \
  --endpoint "你的端点" \
  --topic "$oc/broadcast/test" \
  --interval 5 \
  --duration 60

# 单次发送广播
python broadcast.py \
  --ak "你的AK" \
  --sk "你的SK" \
  --endpoint "你的端点" \
  --topic "$oc/broadcast/test" \
  --once
```

**参数说明：**
- `--ak`: 华为云访问密钥ID
- `--sk`: 华为云访问密钥Secret
- `--endpoint`: 华为云IoTDA端点
- `--region`: 华为云区域ID (默认: cn-north-4)
- `--topic`: 广播主题 (默认: $oc/broadcast/test)
- `--interval`: 发送间隔秒数 (默认: 5)
- `--duration`: 运行持续时间秒数 (默认: 无限运行)
- `--once`: 只发送一次广播

### 订阅测试器 (huawei_subscribe_test.py)

单独运行订阅测试：

```bash
python huawei_subscribe_test.py \
  --host "你的MQTT服务器" \
  --port 1883 \
  --device-prefix "你的设备前缀" \
  --device-secret "你的设备密钥" \
  --duration 60
```

**参数说明：**
- `--host`: MQTT服务器地址
- `--port`: MQTT端口 (默认: 1883)
- `--device-prefix`: 设备前缀
- `--device-secret`: 设备密钥
- `--duration`: 运行持续时间秒数 (默认: 无限运行)

### 集成测试器 (huawei_broadcast_integration.py)

运行完整的端到端测试：

```bash
# 使用配置文件
python huawei_broadcast_integration.py --config huawei_broadcast_config.json

# 使用命令行参数
python huawei_broadcast_integration.py \
  --mqtt-host "你的MQTT服务器" \
  --device-prefix "你的设备前缀" \
  --device-secret "你的设备密钥" \
  --huawei-ak "你的AK" \
  --huawei-sk "你的SK" \
  --huawei-endpoint "你的端点" \
  --broadcast-topic "$oc/broadcast/test" \
  --broadcast-interval 5 \
  --test-duration 60
```

## 测试流程

1. **启动广播发送器** - 开始循环发送广播消息到 `$oc/broadcast/test` 主题
2. **启动订阅测试器** - 设备订阅 `$oc/broadcast/test` 主题
3. **消息传输验证** - 验证设备能够接收到广播消息
4. **统计信息显示** - 显示发送和接收的消息统计
5. **优雅退出** - 按 Ctrl+C 或达到时间限制后优雅退出

## 输出示例

### 广播发送器输出
```
[INFO] 华为云客户端创建成功，区域: cn-north-4
[INFO] 开始循环发送广播
[INFO] 主题: $oc/broadcast/test
[INFO] 间隔: 5秒
[INFO] 持续时间: 60秒
[SUCCESS] 广播发送成功: $oc/broadcast/test
[SUCCESS] 广播发送成功: $oc/broadcast/test
...
[INFO] 广播发送结束，共发送 12 条消息
```

### 订阅测试器输出
```
[INFO] MQTT客户端创建成功
[INFO] 开始华为云订阅测试
[SUCCESS] 连接成功: your-mqtt-server:1883
[SUCCESS] 订阅成功: $oc/broadcast/test
[2024-12-19 10:30:15] 收到广播消息 #1:
  主题: $oc/broadcast/test
  QoS: 1
  内容: {
    "timestamp": 1703043015.123,
    "datetime": "2024-12-19T10:30:15.123456",
    "message_id": 1,
    "content": "广播消息 #1",
    "source": "broadcast_sender"
  }
[STATS] 已接收 10 条消息，平均速率: 2.00 条/秒
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查MQTT服务器地址和端口
   - 验证设备前缀和密钥
   - 确认网络连接正常

2. **认证失败**
   - 检查华为云AK/SK是否正确
   - 验证IoTDA端点是否正确
   - 确认区域设置是否正确

3. **订阅失败**
   - 检查设备是否有订阅权限
   - 验证主题名称是否正确
   - 确认QoS设置是否合适

4. **消息接收不到**
   - 确认广播发送器是否正常运行
   - 检查主题名称是否一致
   - 验证设备订阅状态

### 调试模式

启用详细日志输出：

```bash
# 设置环境变量启用调试
export MQTT_LOG_LEVEL=DEBUG
python huawei_subscribe_test.py [参数...]
```

## 性能优化

### 调整参数

1. **广播间隔** - 根据测试需求调整 `broadcast_interval`
2. **测试时长** - 根据测试场景设置 `test_duration`
3. **QoS等级** - 根据需要调整消息质量等级

### 监控指标

- 消息发送速率
- 消息接收速率
- 连接成功率
- 消息延迟

## 扩展功能

### 自定义消息格式

修改 `broadcast.py` 中的消息结构：

```python
message = {
    'timestamp': time.time(),
    'datetime': datetime.now().isoformat(),
    'message_id': message_count + 1,
    'content': f'自定义消息 #{message_count + 1}',
    'source': 'broadcast_sender',
    'custom_field': 'custom_value'  # 添加自定义字段
}
```

### 多设备测试

同时运行多个订阅测试器：

```bash
# 终端1
python huawei_subscribe_test.py --device-prefix "device1" --device-secret "secret1" &

# 终端2  
python huawei_subscribe_test.py --device-prefix "device2" --device-secret "secret2" &

# 终端3
python broadcast.py --ak "AK" --sk "SK" --endpoint "ENDPOINT"
```

## 注意事项

1. **安全性** - 不要在代码中硬编码敏感信息，使用环境变量或配置文件
2. **资源管理** - 长时间运行时注意监控系统资源使用情况
3. **网络稳定性** - 确保网络连接稳定，避免消息丢失
4. **权限管理** - 确保设备有足够的权限进行订阅和接收消息

## 技术支持

如有问题，请检查：

1. 华为云IoTDA控制台配置
2. 设备注册和认证状态
3. 网络连接和防火墙设置
4. 日志输出和错误信息

---

**作者**: Jaxon  
**日期**: 2024-12-19  
**版本**: 1.0.0
