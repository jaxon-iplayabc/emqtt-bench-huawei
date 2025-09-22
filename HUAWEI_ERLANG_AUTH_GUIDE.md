# 华为云 Erlang 认证使用指南

本文档介绍如何使用 emqtt-bench 的原生 Erlang 实现来进行华为云 IoT 平台的认证，无需调用 Python 脚本。

## 一、功能概述

### 新增 Erlang 模块
- `src/huawei_auth.erl` - 实现华为云认证算法的 Erlang 模块
  - `get_password/1` - 生成华为云密码
  - `get_client_id/1` - 生成华为云 ClientID
  - `get_timestamp/0` - 生成时间戳

### 修改的文件
- `src/emqtt_bench.erl` - 添加华为云认证支持
  - 新增 `--huawei-auth` 选项
  - 密码支持 `huawei:<secret>` 格式
  - ClientID 自动生成华为云格式

## 二、使用方法

### 1. 基本用法

使用华为云认证进行发布测试：

```bash
# 推荐方式：使用 --device-id 和 %d
./emqtt_bench pub \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 100 \
    -I 1000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256

# 向后兼容方式：仅使用 -u
./emqtt_bench pub \
    -h <华为云MQTT地址> \
    -p 1883 \
    -c 100 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256
```

参数说明：
- `-P 'huawei:12345678'` - 使用华为云密码格式，`12345678` 是设备密钥
- `--huawei-auth` - 启用华为云认证（自动处理 username = device_id）
- `--device-id 'Speaker-%i'` - 设备ID（推荐使用）
- `-u 'Speaker-%i'` - 当不指定 --device-id 时，作为设备ID使用

**重要**：华为云要求 MQTT username 必须是设备ID。使用 `--huawei-auth` 时会自动确保这一点。

### 2. 认证机制说明

#### ClientID 格式
```
设备ID_0_密码签名类型_时间戳
```
例如：`Speaker-000000001_0_0_2024111812`

#### 密码生成算法
使用 HMAC-SHA256，以时间戳（YYYYMMDDHH）为密钥对设备密钥进行加密。

### 3. 使用示例

#### 连接测试
```bash
./emqtt_bench conn \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 1000 \
    --prefix 'Speaker' \
    -u 'Speaker-%i' \
    -P 'huawei:你的设备密钥' \
    --huawei-auth
```

#### 订阅测试
```bash
./emqtt_bench sub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    -t '$oc/devices/+/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:你的设备密钥' \
    --huawei-auth
```

#### 发布测试（使用 payload 文件）
```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 50 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:你的设备密钥' \
    --huawei-auth \
    --message 'template://huawei_cloud_payload_template.json'
```

### 4. 与 Python 实现的对比

| 功能 | Python 实现 | Erlang 实现 |
|------|------------|-------------|
| 调用方式 | 需要调用 Python 脚本 | 原生支持 |
| 性能 | 有进程调用开销 | 无额外开销 |
| 使用复杂度 | 需要 Python 环境 | 直接使用 |
| 密码格式 | 手动生成后传入 | `huawei:<secret>` 自动生成 |

### 5. SSL/TLS 支持

```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 8883 \
    --ssl \
    --cacertfile /path/to/ca.pem \
    -c 100 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256
```

### 6. 性能监控

启用 Prometheus 监控：
```bash
./emqtt_bench pub \
    ... \
    --huawei-auth \
    --prometheus \
    --restapi 8080
```

### 7. 注意事项

1. **时间同步**：确保系统时间准确，华为云使用时间戳进行认证
2. **设备ID格式**：设备ID（用户名）应符合华为云要求
3. **密钥安全**：妥善保管设备密钥，避免泄露
4. **批量测试**：使用 `%i` 变量可以批量创建不同的设备

### 8. 故障排查

如果遇到认证失败：
1. 检查时间是否同步（误差不能超过1小时）
2. 确认设备密钥是否正确
3. 验证设备ID格式是否符合要求
4. 查看 emqtt_bench 的错误输出

### 9. 高级用法

结合 topics_payload 使用：
```bash
./emqtt_bench pub \
    -h mqtt.huaweicloud.com \
    -p 1883 \
    -c 100 \
    --topics-payload huawei_cloud_topics.json \
    -u 'Speaker-%i' \
    -P 'huawei:12345678' \
    --huawei-auth
```

## 三、实现细节

### huawei_auth.erl 模块

主要函数：
```erlang
%% 生成密码
get_password(Secret) ->
    Timestamp = get_timestamp(),
    Mac = crypto:mac(hmac, sha256, Timestamp, Secret),
    bin_to_hex(Mac).

%% 生成 ClientID
get_client_id(DeviceId) ->
    Timestamp = get_timestamp(),
    iolist_to_binary([DeviceId, "_0_0_", Timestamp]).

%% 生成时间戳（YYYYMMDDHH）
get_timestamp() ->
    {{Year, Month, Day}, {Hour, _, _}} = calendar:universal_time(),
    iolist_to_binary(
        io_lib:format("~4..0B~2..0B~2..0B~2..0B", [Year, Month, Day, Hour])
    ).
```

### emqtt_bench.erl 修改

1. 添加了 `--huawei-auth` 选项
2. 密码处理支持 `huawei:<secret>` 格式
3. ClientID 生成集成华为云格式

## 四、总结

使用 Erlang 原生实现的华为云认证功能，避免了对 Python 的依赖，提高了性能和易用性。通过简单的命令行选项即可完成华为云 IoT 平台的认证配置。
