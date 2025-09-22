# 华为云 IoT 平台 --prefix 参数解决方案 ✅

## 问题解决

经过调试和修复，现在可以使用 `--prefix` 参数来设置华为云设备ID前缀，这是一个更优雅的解决方案。

## 关键修复

### 1. 时间戳生成修复 ✅
- **问题**：Erlang 使用 UTC 时间，Python 使用本地时间
- **修复**：将 `huawei_auth:get_timestamp/0` 改为使用 `calendar:local_time()`

### 2. MQTT 协议版本修复 ✅
- **问题**：默认使用 MQTT v5，华为云不支持
- **修复**：将默认协议版本改为 MQTT v3.1.1

### 3. Username 设置修复 ✅
- **问题**：`lists:keyreplace` 无法添加不存在的字段
- **修复**：使用 `lists:keystore` 来添加或替换 username 字段

## 使用方式

### 基础用法

```bash
# 单设备测试
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "huawei:12345678" \
    --huawei-auth \
    --limit 5
```

### 多设备并发测试

```bash
# 100个设备并发
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "huawei:12345678" \
    --huawei-auth \
    -s 512
```

## 设备ID生成逻辑

### 优先级顺序
1. **`-u` 参数**：如果指定了 username，使用 username 作为设备ID
2. **`--prefix` 参数**：如果没有 username，使用 `{prefix}-{9位数字}` 格式
3. **默认格式**：如果都没有，使用 `device-{9位数字}` 格式

### 设备ID格式
- **Speaker-000000001**（使用 --prefix "Speaker"）
- **Speaker-000000002**
- **Speaker-000000100**

## 认证信息生成

### ClientID 格式
```
{device_id}_0_0_{timestamp}
```
示例：`Speaker-000000001_0_0_2025092214`

### Username
```
{device_id}
```
示例：`Speaker-000000001`

### Password
```
HMAC-SHA256(timestamp, secret)
```
使用设备密钥和当前时间戳生成

## 优势

1. **简化命令**：只需指定 `--prefix`，无需复杂的 `-u` 模板
2. **语义清晰**：`--prefix` 本来就是用于设置前缀
3. **向后兼容**：不影响非华为云场景的使用
4. **灵活配置**：支持多种设备ID生成方式

## 测试验证

✅ 单设备连接测试通过
✅ 多设备并发测试通过
✅ 认证信息生成正确
✅ 与 Python 实现完全一致

## 总结

`--prefix` 参数方案是一个合理且优雅的解决方案，符合用户的使用习惯，同时保持了代码的简洁性和可维护性。
