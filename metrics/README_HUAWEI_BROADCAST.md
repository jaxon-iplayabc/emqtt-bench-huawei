# 华为云广播测试系统

## 概述

这是一个完整的华为云IoTDA广播测试系统，支持端到端消息传输验证。系统包含三个核心组件：

1. **广播发送器** - 循环发送广播消息到指定主题
2. **订阅测试器** - 订阅广播主题并接收消息
3. **集成测试器** - 同时运行发送和订阅测试

## 功能特性

- ✅ 支持循环发送广播消息
- ✅ 支持设备订阅广播主题
- ✅ 支持端到端消息传输验证
- ✅ 支持实时消息统计
- ✅ 支持优雅的进程管理
- ✅ 支持配置文件管理
- ✅ 支持多种运行模式

## 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip3 install paho-mqtt huaweicloudsdkcore huaweicloudsdkiotda
```

### 2. 配置参数

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

### 3. 运行测试

```bash
# 方法1: 使用快速启动脚本（推荐）
./run_huawei_broadcast_test.sh --interactive  # 交互式配置
./run_huawei_broadcast_test.sh --test        # 完整集成测试

# 方法2: 直接运行集成测试
python3 huawei_broadcast_integration.py --config huawei_broadcast_config.json

# 方法3: 查看使用示例
python3 example_usage.py
```

## 核心组件

### 广播发送器 (broadcast.py)

循环发送广播消息到指定主题：

```bash
# 循环发送
python3 broadcast.py --ak "你的AK" --sk "你的SK" --endpoint "你的端点" --interval 5 --duration 60

# 单次发送
python3 broadcast.py --ak "你的AK" --sk "你的SK" --endpoint "你的端点" --once
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

订阅广播主题并接收消息：

```bash
python3 huawei_subscribe_test.py \
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

同时运行广播发送和订阅测试：

```bash
# 使用配置文件
python3 huawei_broadcast_integration.py --config huawei_broadcast_config.json

# 使用命令行参数
python3 huawei_broadcast_integration.py \
  --mqtt-host "你的MQTT服务器" \
  --device-prefix "你的设备前缀" \
  --device-secret "你的设备密钥" \
  --huawei-ak "你的AK" \
  --huawei-sk "你的SK" \
  --huawei-endpoint "你的端点"
```

## 快速启动脚本

### run_huawei_broadcast_test.sh

提供多种运行模式：

```bash
# 显示帮助
./run_huawei_broadcast_test.sh --help

# 交互式配置
./run_huawei_broadcast_test.sh --interactive

# 演示模式
./run_huawei_broadcast_test.sh --demo

# 单次发送
./run_huawei_broadcast_test.sh --single

# 循环发送
./run_huawei_broadcast_test.sh --loop

# 完整测试
./run_huawei_broadcast_test.sh --test

# 使用配置文件
./run_huawei_broadcast_test.sh --config your_config.json
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

```bash
# 设置环境变量启用调试
export MQTT_LOG_LEVEL=DEBUG
python3 huawei_subscribe_test.py [参数...]
```

## 文件结构

```
metrics/
├── broadcast.py                          # 广播发送器
├── huawei_subscribe_test.py              # 订阅测试器
├── huawei_broadcast_integration.py       # 集成测试器
├── huawei_broadcast_config.json          # 配置文件模板
├── run_huawei_broadcast_test.sh          # 快速启动脚本
├── example_usage.py                       # 使用示例
├── HUAWEI_BROADCAST_TEST_GUIDE.md        # 详细使用指南
└── README_HUAWEI_BROADCAST.md            # 本文件
```

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
python3 huawei_subscribe_test.py --device-prefix "device1" --device-secret "secret1" &

# 终端2  
python3 huawei_subscribe_test.py --device-prefix "device2" --device-secret "secret2" &

# 终端3
python3 broadcast.py --ak "AK" --sk "SK" --endpoint "ENDPOINT"
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

## 更新日志

查看 `CHANGELOG.md` 了解最新更新和功能改进。

---

**作者**: Jaxon  
**日期**: 2024-12-19  
**版本**: 1.0.0
