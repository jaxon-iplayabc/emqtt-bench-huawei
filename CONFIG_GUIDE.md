# eMQTT-Bench 配置指南

## 🚀 新功能：用户自定义配置

现在 `prometheus_example.sh` 脚本支持用户自定义所有华为云配置参数，不再需要硬编码！

## 📋 支持的配置参数

### 华为云IoT平台配置
- **HUAWEI_HOST**: 华为云IoT服务器地址
- **HUAWEI_PORT**: 华为云IoT端口 (默认: 1883)
- **DEVICE_PREFIX**: 设备前缀 (默认: speaker)
- **HUAWEI_SECRET**: 设备密钥 (默认: 12345678)

### 其他配置参数
- **CLIENT_COUNT**: 客户端数量 (默认: 5)
- **MSG_INTERVAL**: 消息间隔毫秒数 (默认: 1000)
- **PROMETHEUS_PORT**: Prometheus起始端口 (默认: 9090)

## 🔧 使用方法

### 首次运行
```bash
./prometheus_example.sh
```

脚本会提示您输入所有配置参数：
```
🚀 eMQTT-Bench Prometheus 监控工具
====================================
✨ 新功能: 支持用户自定义华为云配置参数
📁 配置保存: 自动保存配置到 emqtt_bench_config.conf
🔄 配置加载: 下次运行时自动加载保存的配置

🔧 开始配置参数...

请输入华为云IoT平台配置信息:

华为云IoT服务器地址 (默认: 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com): 
华为云IoT端口 (默认: 1883): 
设备前缀 (默认: speaker): 
设备密钥 (默认: 12345678): 

✅ 华为云配置已设置:
  服务器: your-server.com:1883
  设备前缀: your_device
  设备密钥: your_secret

📝 其他配置参数 (按回车使用默认值):

客户端数量 (默认: 5): 
消息间隔(ms) (默认: 1000): 
Prometheus起始端口 (默认: 9090): 

📋 当前配置参数:
  MQTT服务器: localhost:1883
  客户端数量: 5
  消息间隔: 1000ms
  Prometheus端口: 9090

☁️  华为云配置:
  服务器: your-server.com:1883
  设备前缀: your_device
  设备密钥: your_secret

是否确认使用以上配置? (y/n/s保存配置): 
```

### 后续运行
```bash
./prometheus_example.sh
```

如果发现配置文件，会询问是否加载：
```
📁 发现配置文件 emqtt_bench_config.conf
是否加载保存的配置? (y/n): y
✅ 配置已加载
```

## 💾 配置文件

配置会自动保存到 `emqtt_bench_config.conf` 文件中：

```bash
# eMQTT-Bench 配置文件
# 生成时间: 2025-09-23 17:45:00

# 华为云配置
HUAWEI_HOST="your-iot-server.com"
HUAWEI_PORT="1883"
DEVICE_PREFIX="your_device"
HUAWEI_SECRET="your_secret"

# 其他配置
CLIENT_COUNT="5"
MSG_INTERVAL="1000"
PROMETHEUS_PORT="9090"
```

## 🎯 配置选项说明

### 配置确认时的选项
- **y**: 确认配置，开始测试
- **n**: 重新配置参数
- **s**: 保存当前配置到文件

### 华为云配置示例
```bash
# 生产环境示例
HUAWEI_HOST="your-production-iot.cn-north-4.myhuaweicloud.com"
HUAWEI_PORT="8883"  # SSL端口
DEVICE_PREFIX="prod_device"
HUAWEI_SECRET="your_production_secret"

# 测试环境示例
HUAWEI_HOST="your-test-iot.cn-north-4.myhuaweicloud.com"
HUAWEI_PORT="1883"  # 非SSL端口
DEVICE_PREFIX="test_device"
HUAWEI_SECRET="your_test_secret"
```

## 🔄 配置管理

### 手动编辑配置文件
您可以直接编辑 `emqtt_bench_config.conf` 文件来修改配置：

```bash
# 编辑配置文件
nano emqtt_bench_config.conf

# 或者使用其他编辑器
vim emqtt_bench_config.conf
```

### 删除配置文件
如果您想重新配置所有参数，可以删除配置文件：

```bash
rm emqtt_bench_config.conf
```

下次运行脚本时会重新提示输入配置。

## 🚨 注意事项

1. **安全性**: 配置文件包含敏感信息（如设备密钥），请妥善保管
2. **端口冲突**: 确保Prometheus端口范围没有被其他服务占用
3. **网络连接**: 确保能够访问指定的华为云IoT服务器
4. **权限**: 确保脚本有执行权限：`chmod +x prometheus_example.sh`

## 🆘 故障排除

### 配置文件损坏
如果配置文件格式错误，删除配置文件重新创建：
```bash
rm emqtt_bench_config.conf
./prometheus_example.sh
```

### 端口被占用
如果Prometheus端口被占用，脚本会自动检测并询问是否杀死占用进程，或者您可以：
1. 选择不同的起始端口
2. 手动杀死占用端口的进程
3. 等待端口自动释放

### 华为云连接失败
检查以下配置：
1. 服务器地址是否正确
2. 端口是否正确（1883或8883）
3. 设备密钥是否正确
4. 网络连接是否正常

## 📞 支持

如果遇到问题，请检查：
1. 脚本执行权限
2. 配置文件格式
3. 网络连接
4. 华为云IoT平台状态
