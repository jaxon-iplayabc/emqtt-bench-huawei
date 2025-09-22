# 华为云 IoT 平台 emqtt-bench 测试方案 ✅

## 已验证的工作方案

### ✅ 成功的命令格式

经过调试和修复，以下命令格式已验证可以成功连接华为云：

```bash
# 使用 -u 参数（推荐）
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://./huawei_cloud_payload_template.json' \
    --limit 5
```

### 多设备并发测试

```bash
# 测试10个设备
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 10 \
    -i 100 \
    -I 1000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%09.9i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://./huawei_cloud_payload_template.json'
```

## 关键修复

### 1. 时间戳生成修复 ✅
- **问题**：Erlang 使用 UTC 时间，Python 使用本地时间
- **修复**：将 `calendar:universal_time()` 改为 `calendar:local_time()`
- **文件**：`src/huawei_auth.erl`

### 2. 认证逻辑
- 华为云要求：
  - ClientID: `{device_id}_0_0_{timestamp}`
  - Username: `{device_id}`（必须与设备ID相同）
  - Password: HMAC-SHA256(timestamp, secret)

## 使用建议

### 1. 基础测试
```bash
# 单设备测试
./emqtt_bench pub \
    -h <host> \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256
```

### 2. 性能测试
```bash
# 100个设备并发
./emqtt_bench pub \
    -h <host> \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 5000 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%09.9i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://./huawei_cloud_payload_template.json'
```

### 3. 使用真实数据
```bash
# 先生成测试 payload
cd huawei && python3 payload_generator.py && cd ..

# 使用生成的数据
./emqtt_bench pub \
    -h <host> \
    -p 1883 \
    -c 50 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-%09.9i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://huawei/huawei_cloud_payload_example.json'
```

## 注意事项

1. **设备ID格式**：必须是 `{prefix}-{9位数字}`，如 `Speaker-000000001`
2. **使用 `-u` 参数**：目前推荐使用 `-u` 参数而不是 `--device-id`
3. **时间同步**：确保系统时间准确（误差不超过1小时）
4. **设备注册**：确保设备已在华为云平台注册

## 故障排查

如果遇到 `bad_username_or_password` 错误：

1. 检查设备是否已注册
2. 确认设备密钥正确
3. 验证系统时间准确
4. 使用 Python 脚本测试：
   ```bash
   cd huawei
   python3 test_real_device.py
   ```

## 测试脚本

提供的测试脚本：
- `quick_test_huawei.sh` - 快速单设备测试
- `huawei_cloud_full_test.sh` - 完整功能测试
- `diagnose_huawei_auth.sh` - 认证问题诊断

## 总结

华为云 IoT 平台的 emqtt-bench 集成已基本完成：
- ✅ Erlang 原生认证实现
- ✅ 支持大规模设备并发测试
- ✅ 支持真实 payload 模板
- ✅ 性能监控和 QoE 跟踪

推荐使用 `-u` 参数配合 `--huawei-auth` 进行测试。
