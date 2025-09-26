# eMQTT-Bench 集成测试管理器

一个完整的 eMQTT-Bench 测试解决方案，集成了配置管理、测试执行、数据收集和报表生成功能。

## 🚀 新功能亮点

- **一键测试**: 一个命令完成配置、测试、数据收集和报表生成
- **智能配置**: 交互式配置界面，支持配置保存和加载
- **进程管理**: 自动进程管理，支持 Ctrl+C 优雅退出
- **实时监控**: 实时指标收集和状态监控
- **丰富报表**: 自动生成 HTML 测试报告
- **华为云优化**: 专门优化华为云 IoT 平台测试

## 🎯 快速开始

### 方法一：一键启动（推荐）

```bash
# 进入 metrics 目录
cd metrics/

# 一键运行所有测试
./quick_test.sh
```

### 方法二：使用 uv

```bash
# 安装依赖
uv sync

# 运行测试管理器
uv run python emqtt_test_manager.py

# 或使用简化版本
uv run python main.py
```

### 方法三：使用 Python

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试
python emqtt_test_manager.py
```

## 📋 功能特性

### 1. 集成测试管理器 (`emqtt_test_manager.py`)

完整的测试管理解决方案：

- **配置管理**: 交互式配置，支持保存和加载
- **测试执行**: 支持连接、发布、订阅、华为云、自定义测试
- **进程管理**: 自动进程跟踪和清理
- **数据收集**: 自动收集 Prometheus 指标
- **报表生成**: 生成详细的 HTML 测试报告

### 2. 快速启动器 (`main.py`)

简化版本，专注于核心功能：

```python
from emqtt_test_manager import EMQTTTestManager

# 创建并运行测试管理器
manager = EMQTTTestManager()
manager.run()
```

### 3. 指标收集器 (`metrics_collector.py`)

专业的指标收集和分析工具：

- **实时收集**: 从 Prometheus 端点实时收集指标
- **数据分析**: 解析和统计关键性能指标
- **数据导出**: 支持 JSON 和 CSV 格式导出
- **批量处理**: 支持批量收集多个端点的指标

## 🛠️ 使用方法

### 交互式配置

运行测试管理器后，会引导您完成配置：

1. **基础配置**:
   - MQTT服务器地址和端口
   - 客户端数量
   - 消息间隔
   - Prometheus端口

2. **华为云配置**:
   - 华为云IoT服务器地址
   - 设备前缀
   - 设备密钥

3. **测试配置**:
   - 测试持续时间
   - emqtt_bench路径

### 测试类型

支持以下测试类型：

1. **连接测试**: 测试MQTT连接建立
2. **发布测试**: 测试消息发布性能
3. **订阅测试**: 测试消息订阅性能
4. **华为云测试**: 专门测试华为云IoT平台
5. **自定义测试**: 用户自定义参数测试
6. **全部测试**: 运行所有测试类型

### 命令行选项

```bash
# 使用自定义配置文件
uv run python emqtt_test_manager.py --config my_config.json

# 交互式配置
uv run python emqtt_test_manager.py --interactive
```

## 📊 输出结果

### 1. 指标数据文件

- `metrics_connection_YYYYMMDD_HHMMSS.txt`: 连接测试指标
- `metrics_publish_YYYYMMDD_HHMMSS.txt`: 发布测试指标
- `metrics_subscribe_YYYYMMDD_HHMMSS.txt`: 订阅测试指标
- `metrics_huawei_publish_YYYYMMDD_HHMMSS.txt`: 华为云测试指标

### 2. 配置文件

- `emqtt_test_config.json`: 测试配置（自动保存）

### 3. 测试报告

- `test_report_YYYYMMDD_HHMMSS.html`: 详细的HTML测试报告

## 🔧 配置说明

### 配置文件格式

```json
{
  "host": "localhost",
  "port": 1883,
  "client_count": 5,
  "msg_interval": 1000,
  "prometheus_port": 9090,
  "device_prefix": "speaker",
  "huawei_secret": "12345678",
  "use_huawei_auth": false,
  "test_duration": 30,
  "emqtt_bench_path": "./emqtt_bench"
}
```

### 环境变量

- `HOST`: MQTT服务器地址
- `PORT`: MQTT端口
- `CLIENT_COUNT`: 客户端数量
- `MSG_INTERVAL`: 消息间隔(ms)
- `PROMETHEUS_PORT`: Prometheus起始端口
- `USE_HUAWEI_AUTH`: 是否使用华为云认证

## 📈 指标说明

### 连接相关指标

- `connect_succ`: 成功连接数
- `connect_fail`: 连接失败数
- `connect_retried`: 重试连接数
- `connection_timeout`: 连接超时数
- `connection_refused`: 连接被拒绝数
- `unreachable`: 不可达连接数

### 性能相关指标

- `mqtt_client_handshake_duration`: MQTT握手延迟
- `mqtt_client_connect_duration`: 连接建立延迟
- `mqtt_client_tcp_handshake_duration`: TCP握手延迟

## 🛡️ 安全特性

- **进程管理**: 自动跟踪和清理所有测试进程
- **信号处理**: 支持 Ctrl+C 优雅退出
- **错误恢复**: 自动处理进程异常和端口冲突
- **资源清理**: 测试结束后自动清理所有资源

## 🔍 故障排除

### 常见问题

1. **emqtt_bench 未找到**:
   ```bash
   # 确保在项目根目录运行
   ls -la emqtt_bench
   ```

2. **端口被占用**:
   ```bash
   # 检查端口占用
   lsof -i :9090
   
   # 或使用进程管理器清理
   ./process_manager.sh cleanup
   ```

3. **权限问题**:
   ```bash
   # 确保脚本有执行权限
   chmod +x quick_test.sh
   ```

### 调试模式

```bash
# 启用详细输出
uv run python emqtt_test_manager.py --debug
```

## 📚 相关文档

- [进程管理指南](../PROCESS_MANAGEMENT_GUIDE.md)
- [配置指南](../CONFIG_GUIDE.md)
- [Prometheus监控指南](../PROMETHEUS_MONITORING_GUIDE.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

*作者: Jaxon*  
*最后更新: 2024-12-19*