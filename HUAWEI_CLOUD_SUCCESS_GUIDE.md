# 华为云 IoT 平台测试成功指南 ✅

## 测试环境确认

您提供的华为云环境已成功测试通过：
- **服务器**: 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com
- **端口**: 1883
- **设备前缀**: Speaker
- **设备密钥**: 12345678

## 快速开始

### 1. 最简单的测试命令

```bash
# 单个设备测试
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 1 \
    -t '$oc/devices/%u/sys/properties/report' \
    -u 'Speaker-000000001' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 256 \
    --limit 5
```

✅ **测试结果**：成功连接并发送消息！

### 2. 多设备并发测试

```bash
# 100个设备并发
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 100 \
    -i 10 \
    -I 5000 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'Speaker-%09.9i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    -s 512
```

### 3. 使用真实数据测试

```bash
# 先生成测试数据
cd huawei && python3 payload_generator.py && cd ..

# 使用生成的数据
./emqtt_bench pub \
    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \
    -p 1883 \
    -c 50 \
    -t '$oc/devices/%d/sys/properties/report' \
    --device-id 'Speaker-%09.9i' \
    -P 'huawei:12345678' \
    --huawei-auth \
    --message 'template://huawei/huawei_cloud_payload_example.json'
```

## 关键参数说明

### 认证参数
- `--huawei-auth` - 启用华为云认证模式（必须）
- `-P 'huawei:12345678'` - 密码格式，12345678 是您的设备密钥
- `-u` 或 `--device-id` - 设备ID，格式为 `Speaker-XXXXXXXXX`（9位数字）

### Topic 变量
- `%u` - username（在华为云模式下等于 device_id）
- `%d` - device_id
- `%i` - 客户端序号
- `%09.9i` - 9位数字格式的序号（000000001, 000000002...）

## 设备ID格式

华为云要求设备ID格式为：`{prefix}-{9位数字}`

示例：
- Speaker-000000001
- Speaker-000000002
- Speaker-000000100

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

### 启用性能监控
```bash
... --prometheus --restapi 8080
```
然后访问 http://localhost:8080/metrics

### 启用 QoE 跟踪
```bash
... --qoe true --qoelog huawei_test.qoe
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

## 测试脚本

提供了多个测试脚本供您使用：
- `quick_test_huawei.sh` - 快速测试单个设备
- `huawei_cloud_full_test.sh` - 完整功能测试
- `test_huawei_real_env.sh` - 真实环境测试套件

## Python 测试工具

如需更详细的调试信息，可使用 Python 脚本：
```bash
cd huawei
python3 test_real_device.py
```

## 总结

华为云 IoT 平台的 emqtt-bench 集成已完全可用：
- ✅ Erlang 原生认证实现
- ✅ 支持大规模设备并发测试
- ✅ 灵活的设备ID管理
- ✅ 完整的性能监控支持

祝您测试顺利！🚀
