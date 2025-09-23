# 华为云 IoT 平台 emqtt-bench 最终使用指南 ✅

## 最新简化格式

经过优化，现在华为云认证格式更加简洁直观：

### 基础命令格式

```bash
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    --prefix "Speaker" \
    -P "12345678" \
    --huawei-auth \
    --limit 5
```

### 关键改进

1. **去掉 `"huawei:"` 前缀**：
   - ❌ 旧格式：`-P "huawei:12345678"`
   - ✅ 新格式：`-P "12345678"`

2. **通过 `--huawei-auth` 自动判断**：
   - 当 `--huawei-auth` 存在时，自动使用华为云认证
   - 当 `--huawei-auth` 不存在时，使用普通MQTT认证

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

### 3. 使用真实数据模板

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

### 4. 性能监控测试

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

## 设备ID生成规则

### 优先级顺序
1. **`-u` 参数**：如果指定，使用 username 作为设备ID
2. **`--prefix` 参数**：使用 `{prefix}-{9位数字}` 格式
3. **默认格式**：使用 `device-{9位数字}` 格式

### 示例
- `--prefix "Speaker"` → Speaker-000000001, Speaker-000000002, ...
- `--prefix "Device"` → Device-000000001, Device-000000002, ...
- 无 prefix → device-000000001, device-000000002, ...

## 认证信息自动生成

当使用 `--huawei-auth` 时，系统自动生成：

- **ClientID**: `{device_id}_0_0_{timestamp}`
- **Username**: `{device_id}`
- **Password**: `HMAC-SHA256(timestamp, secret)`

## 优势总结

1. **更简洁**：去掉 `"huawei:"` 前缀，命令更简洁
2. **更直观**：通过 `--huawei-auth` 明确表示认证方式
3. **更一致**：密码格式与其他MQTT客户端保持一致
4. **更安全**：避免在命令行中暴露认证方式前缀
5. **更灵活**：支持多种设备ID生成方式

## 兼容性

- ✅ 完全向后兼容
- ✅ 支持所有现有功能
- ✅ 支持大规模并发测试
- ✅ 支持性能监控和QoE跟踪

## 测试验证

所有功能已通过测试验证：
- ✅ 单设备连接
- ✅ 多设备并发
- ✅ 真实数据模板
- ✅ 性能监控
- ✅ 与Python实现完全一致
