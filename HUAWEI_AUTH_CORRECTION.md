# 华为云认证机制修正说明

## 修正内容

### 华为云 IoT 平台认证要求

根据华为云 IoT 平台的要求，MQTT 连接认证参数必须满足：

1. **MQTT Username** = Device ID（设备ID）
2. **MQTT ClientID** = Device ID_0_密码签名类型_时间戳
3. **MQTT Password** = HMAC-SHA256(时间戳, 设备密钥)

### 代码逻辑修正

当使用 `--huawei-auth` 选项时，emqtt-bench 现在会自动处理认证参数：

1. **自动使用 device_id 作为 username**
   - 如果指定了 `--device-id`，则使用该值作为 MQTT username
   - 如果未指定 `--device-id`，则使用 `-u/--username` 的值作为 device_id

2. **ClientID 自动生成**
   - 格式：`{device_id}_0_{签名类型}_{时间戳}`

3. **密码自动生成**
   - 使用 HMAC-SHA256 算法

## 使用示例

### 示例 1：基本用法（username 即 device_id）

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256
```

在此示例中：
- `-u 'Speaker-%i'` 既是 username 也是 device_id
- MQTT 连接时，username = `Speaker-1`, `Speaker-2`, ...
- ClientID = `Speaker-1_0_0_2024111813`, ...
- Topic 中的 `%u` 会被替换为 `Speaker-1`, ...

### 示例 2：使用独立的 device_id（推荐）

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -t '$oc/devices/%d/sys/properties/report' \
    -u 'ignored-value' \
    --device-id 'SmartSpeaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256
```

在此示例中：
- `--device-id 'SmartSpeaker-%i'` 指定了设备ID
- 当使用 `--huawei-auth` 时，`-u` 的值会被忽略
- MQTT 连接时，username = `SmartSpeaker-1`, `SmartSpeaker-2`, ...
- ClientID = `SmartSpeaker-1_0_0_2024111813`, ...
- Topic 中的 `%d` 会被替换为 `SmartSpeaker-1`, ...

### 示例 3：最佳实践

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 1000 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'HuaweiDevice-%i' \
    -P 'huawei:your-device-secret' \
    --huawei-auth \
    --message 'template://huawei_cloud_payload_template.json'
```

注意：当使用 `--huawei-auth` 时，不需要指定 `-u` 参数，因为 username 会自动使用 device_id 的值。

## 认证流程图

```
用户输入                    -->  内部处理                -->  MQTT 连接参数
--device-id 'Device-%i'         device_id = Device-1         username = Device-1
--huawei-auth                   生成时间戳                   clientid = Device-1_0_0_2024111813
-P 'huawei:secret'             计算 HMAC-SHA256             password = <计算结果>
```

## 注意事项

1. **向后兼容**：如果不指定 `--device-id`，系统会使用 `-u` 的值作为 device_id
2. **Topic 变量**：
   - 使用 `%d` 表示 device_id
   - 使用 `%u` 表示 username（在华为云认证时，两者相同）
3. **时间同步**：确保系统时间准确，误差不超过 1 小时

## 错误示例（避免）

```bash
# 错误：华为云认证时，username 和 device_id 不一致会导致认证失败
./emqtt_bench pub \
    -u 'user-%i' \              # 这个值在华为云认证时会被忽略
    --device-id 'device-%i' \   # 实际使用的 username
    --huawei-auth
```

## 总结

华为云 IoT 平台要求 MQTT 的 username 必须是设备ID。使用 `--huawei-auth` 选项时，emqtt-bench 会自动确保这一点，让您的测试更加简单和准确。
