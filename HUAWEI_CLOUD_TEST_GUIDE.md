# 华为云 IoT 平台性能测试指南

本指南介绍如何使用 emqtt-bench 对华为云 IoT 平台进行性能测试。

## 一、华为云设备属性上报测试

### 1. Topic 格式
```
$oc/devices/{device_id}/sys/properties/report
```

**新功能**：现在支持使用 `%d` 变量来表示 device_id：
```
$oc/devices/%d/sys/properties/report
```

### 2. Payload 格式
华为云要求的 payload 是一个 JSON 数组，包含多个服务数据：
- 电池状态 (battery)
- 存储信息 (storage)
- 设置信息 (settings)
- 文件报告 (report_file)
- WiFi 信息 (wifi)
- 播放状态 (playing)

## 二、测试方法

### 方法一：使用 Python 脚本（推荐）

我们提供了一个 Python 脚本来简化测试过程：

```bash
cd huawei
python3 run_huawei_cloud_test.py \
    --host <华为云MQTT地址> \
    --port 1883 \
    --device-prefix Speaker \
    --secret 12345678 \
    -c 100 \
    -I 1000 \
    --ssl \
    --cacertfile /path/to/ca.pem
```

参数说明：
- `--host`: 华为云 MQTT 服务器地址
- `--port`: MQTT 端口（默认 1883，SSL 为 8883）
- `--device-prefix`: 设备ID前缀
- `--secret`: 设备密钥
- `-c`: 客户端数量
- `-I`: 消息发送间隔（毫秒）
- `--ssl`: 启用 SSL/TLS
- `--cacertfile`: CA 证书路径

### 方法二：直接使用 emqtt-bench

1. **使用静态 payload 文件**

首先创建一个 payload 文件：
```bash
python3 huawei/payload_generator.py
```

然后运行测试：
```bash
# 传统方式（手动构建 topic）
./emqtt_bench pub \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 1000 \
    -t '$oc/devices/Speaker-%i/sys/properties/report' \
    -u 'Speaker-%i' \
    -P $(python3 -c "from huawei.utils import get_password; print(get_password('12345678'))") \
    -q 1 \
    --message 'template://huawei_cloud_payload_example.json'

# 新方式（使用 %d 变量）
./emqtt_bench pub \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -q 1 \
    --message 'template://huawei_cloud_payload_example.json'
```

2. **使用 topics_payload 配置文件**

```bash
./emqtt_bench pub \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 100 \
    -i 10 \
    --topics-payload huawei_cloud_topics.json \
    -u 'Speaker-%i' \
    -P $(python3 -c "from huawei.utils import get_password; print(get_password('12345678'))")
```

## 三、华为云认证机制

### 1. ClientID 格式
```
设备ID_0_密码签名类型_时间戳
```

例如：`Speaker-000000001_0_0_2024010112`

### 2. 密码生成
使用 HMAC-SHA256 算法，以时间戳为密钥对设备密钥进行加密。

Python 实现：
```python
from huawei.utils import get_client_id, get_password

# 生成 ClientID
client_id = get_client_id("Speaker-000000001")

# 生成密码
password = get_password("12345678")
```

## 四、性能测试场景

### 场景1：连接性能测试
测试设备大规模连接能力：
```bash
./emqtt_bench conn \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 10000 \
    -i 10 \
    --prefix 'Speaker' \
    -u 'Speaker-%i' \
    -P <password>
```

### 场景2：持续上报测试
模拟设备持续上报属性：
```bash
python3 huawei/run_huawei_cloud_test.py \
    --host <华为云MQTT地址> \
    --device-prefix Speaker \
    -c 1000 \
    -I 5000 \
    --ssl
```

### 场景3：压力测试
高频率消息发送：
```bash
python3 huawei/run_huawei_cloud_test.py \
    --host <华为云MQTT地址> \
    --device-prefix Speaker \
    -c 500 \
    -I 100 \
    -q 0
```

## 五、监控和分析

### 1. 启用 Prometheus 监控
```bash
./emqtt_bench pub \
    ... \
    --prometheus \
    --restapi 8080
```

然后访问 `http://localhost:8080/metrics` 查看指标。

### 2. 启用 QoE 跟踪
```bash
./emqtt_bench pub \
    ... \
    --qoe true \
    --qoelog huawei_test.qoe
```

### 3. 导出 QoE 数据
```bash
./emqtt_bench pub --qoe dump --qoelog huawei_test.qoe
```

## 六、注意事项

1. **时间戳格式**：华为云要求的时间戳格式为 `YYYYMMDDTHHmmSSZ`（UTC时间）

2. **设备数量限制**：注意华为云平台的设备数量限制和流量限制

3. **SSL/TLS**：生产环境建议使用 SSL/TLS 加密连接

4. **消息大小**：注意 payload 大小，避免超过平台限制

5. **QoS 级别**：建议使用 QoS 1 确保消息可靠性

## 七、故障排查

1. **连接失败**
   - 检查设备ID和密钥是否正确
   - 检查时间戳是否在有效范围内
   - 检查网络连接和防火墙设置

2. **认证失败**
   - 确认使用了正确的 ClientID 格式
   - 检查密码生成算法是否正确
   - 确认时间同步

3. **消息发送失败**
   - 检查 topic 格式是否正确
   - 验证 payload JSON 格式
   - 检查 QoS 设置

## 八、扩展功能

如需支持更复杂的随机数据生成，可以修改 `huawei/payload_generator.py` 文件，添加自定义的数据生成逻辑。
