# Device ID 参数使用指南

## 概述

emqtt-bench 现在支持在 topic 中使用 `%d` 变量来表示设备ID (device ID)。这个功能特别适合华为云 IoT 平台等需要在 topic 中包含设备标识的场景。

## 功能特性

### 1. 新增的 Topic 变量
- `%d` - device ID，默认使用 username 的值，也可以通过 `--device-id` 选项明确指定

### 2. 完整的 Topic 变量列表
- `%u` - username (用户名)
- `%c` - client ID (客户端ID)
- `%i` - client sequence number (客户端序列号)
- `%d` - device ID (设备ID) **[新增]**
- `%s` - message sequence number (消息序列号，仅在 pub 中可用)
- `%rand_N` - 随机数，范围 1 到 N

### 3. 命令行选项
```
--device-id <string>  设备ID，用于 topic 渲染（默认使用 username），支持 '%i' 变量
```

## 使用示例

### 示例 1：使用默认行为（device_id = username）

```bash
./emqtt_bench pub \
    -h localhost \
    -p 1883 \
    -c 10 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'Speaker-%i' \
    -s 256
```

在这个例子中：
- username = `Speaker-1`, `Speaker-2`, ... `Speaker-10`
- device_id 将自动使用 username 的值
- 实际的 topic 将是：`$oc/devices/Speaker-1/sys/properties/report` 等

### 示例 2：明确指定 device_id

```bash
./emqtt_bench pub \
    -h localhost \
    -p 1883 \
    -c 10 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'user-%i' \
    --device-id 'Device-%i' \
    -s 256
```

在这个例子中：
- username = `user-1`, `user-2`, ... `user-10`
- device_id = `Device-1`, `Device-2`, ... `Device-10`
- 实际的 topic 将是：`$oc/devices/Device-1/sys/properties/report` 等

### 示例 3：华为云 IoT 平台完整示例

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://huawei_cloud_payload_template.json'
```

### 示例 4：混合使用多个变量

```bash
./emqtt_bench pub \
    -h localhost \
    -p 1883 \
    -c 5 \
    -t 'factory/%u/devices/%d/status/%i' \
    -u 'line-%rand_3' \
    --device-id 'sensor-%i' \
    -s 100
```

这将生成类似以下的 topic：
- `factory/line-2/devices/sensor-1/status/1`
- `factory/line-1/devices/sensor-2/status/2`
- `factory/line-3/devices/sensor-3/status/3`

## 高级用法

### 1. 在订阅中使用

```bash
./emqtt_bench sub \
    -h localhost \
    -p 1883 \
    -c 10 \
    -t '$oc/devices/%d/sys/+/+' \
    -u 'Speaker-%i'
```

### 2. 结合 topics_payload 文件

在 `topics_payload.json` 文件中使用 %d：

```json
{
    "topics": [
        {
            "name": "$oc/devices/%d/sys/properties/report",
            "interval_ms": "1000",
            "QoS": 1,
            "payload": {...}
        }
    ]
}
```

### 3. 固定设备ID与变量username

```bash
./emqtt_bench pub \
    -h localhost \
    -p 1883 \
    -c 100 \
    -t 'devices/%d/data' \
    -u 'user-%rand_1000' \
    --device-id 'MainDevice' \
    -s 256
```

所有客户端将使用相同的 device_id (`MainDevice`)，但有不同的 username。

## 实现细节

1. **默认行为**：如果没有指定 `--device-id`，`%d` 将被替换为 username 的值
2. **变量支持**：`--device-id` 选项支持 `%i` 和 `%rand_N` 变量
3. **处理顺序**：先处理 `--device-id` 中的变量，然后在 topic 渲染时使用结果

## 与华为云认证的配合

当使用 `--huawei-auth` 时：
- ClientID 会自动使用华为云格式（基于 username 或 device_id）
- 密码会使用 HMAC-SHA256 算法生成
- device_id 可用于 topic 构建，提供更灵活的设备管理

## 注意事项

1. device_id 中的变量（如 %i）是在连接建立时解析的，不会在每条消息中变化
2. 如果同时使用 %u 和 %d，且没有指定 --device-id，它们将显示相同的值
3. device_id 主要用于 topic 渲染，不影响 MQTT 连接的 username 或 clientid

## 故障排查

如果 topic 中的 %d 没有被正确替换：
1. 检查是否正确拼写了 `--device-id` 选项
2. 确认 username 是否已正确设置（当使用默认行为时）
3. 使用 `--log_to console` 查看详细的连接和发布信息
