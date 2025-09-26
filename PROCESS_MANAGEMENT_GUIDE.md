# eMQTT-Bench 进程管理指南

本文档详细说明了如何使用进程管理功能来确保eMQTT-Bench测试结束时正确清理所有进程。

## 🚀 新增功能

### 1. 进程管理器 (`process_manager.sh`)

一个强大的进程管理脚本，提供以下功能：

- **自动进程注册**: 自动跟踪所有启动的eMQTT-Bench进程
- **信号处理**: 捕获Ctrl+C、SIGTERM等信号，确保优雅退出
- **端口清理**: 自动清理被占用的端口
- **状态监控**: 实时显示进程和端口状态
- **批量清理**: 一键清理所有相关进程

### 2. 集成版Prometheus脚本 (`prometheus_example_with_process_manager.sh`)

在原有功能基础上集成了进程管理：

- **安全退出**: 支持Ctrl+C优雅退出
- **自动清理**: 测试结束后自动清理所有进程和端口
- **进程监控**: 实时显示进程状态
- **错误恢复**: 自动处理进程异常情况

## 📋 使用方法

### 基本用法

#### 1. 使用进程管理器启动测试

```bash
# 启动单个测试
./process_manager.sh start './emqtt_bench pub -c 1 -I 1000 -t test/topic --prometheus --restapi 9090' '发布测试' 30

# 查看进程状态
./process_manager.sh status

# 清理所有进程
./process_manager.sh cleanup
```

#### 2. 使用集成版脚本

```bash
# 运行完整的交互式测试
./prometheus_example_with_process_manager.sh
```

### 高级用法

#### 1. 在自定义脚本中使用进程管理

```bash
#!/bin/bash
# 引入进程管理器
source "./process_manager.sh"

# 设置信号处理
setup_signal_handlers

# 启动测试
start_emqtt_bench "./emqtt_bench conn -h localhost -p 1883 -c 5 --prometheus --restapi 9090" "连接测试"

# 等待完成
wait_for_completion 30

# 自动清理（在脚本退出时）
```

#### 2. 注册自定义清理函数

```bash
# 自定义清理函数
my_cleanup() {
    echo "执行自定义清理..."
    # 清理临时文件
    rm -f /tmp/test_*.log
    # 其他清理操作
}

# 注册清理函数
register_cleanup "my_cleanup"
```

## 🛡️ 安全特性

### 1. 信号处理

脚本会自动捕获以下信号：

- **SIGINT (Ctrl+C)**: 优雅退出，清理所有进程
- **SIGTERM**: 终止信号，执行清理后退出
- **EXIT**: 正常退出时自动清理

### 2. 进程清理策略

1. **优雅终止**: 首先发送SIGTERM信号
2. **等待退出**: 等待5秒让进程自然退出
3. **强制终止**: 如果进程仍在运行，发送SIGKILL信号
4. **端口清理**: 清理所有被占用的端口

### 3. 错误处理

- **进程检查**: 启动前检查进程是否有效
- **端口检查**: 自动检测和清理端口冲突
- **异常恢复**: 处理进程异常退出情况

## 📊 监控功能

### 1. 进程状态监控

```bash
# 显示所有注册的进程状态
./process_manager.sh status
```

输出示例：
```
📊 当前进程状态:
✅ 进程 12345 正在运行
❌ 进程 12346 已结束

🔌 端口占用情况:
端口 9090: PID 12345
端口 9091: PID 12346
```

### 2. 实时监控

在测试运行期间，可以随时查看状态：

```bash
# 在另一个终端中运行
./process_manager.sh status
```

## 🔧 配置选项

### 1. 环境变量

```bash
# 设置默认端口范围
export PROMETHEUS_PORT=9090

# 设置清理超时时间
export CLEANUP_TIMEOUT=5
```

### 2. 配置文件

进程管理器会自动创建配置文件来保存设置：

```bash
# 配置文件位置
~/.emqtt_bench_process_manager.conf
```

## 🚨 故障排除

### 1. 进程无法清理

如果遇到进程无法清理的情况：

```bash
# 手动查找并清理
ps aux | grep emqtt_bench
kill -9 <PID>

# 或使用进程管理器强制清理
./process_manager.sh cleanup
```

### 2. 端口被占用

```bash
# 查看端口占用
lsof -i :9090

# 清理特定端口
./process_manager.sh cleanup
```

### 3. 信号处理失效

如果信号处理不工作：

```bash
# 检查脚本权限
chmod +x process_manager.sh

# 重新加载脚本
source ./process_manager.sh
```

## 📝 最佳实践

### 1. 测试前准备

```bash
# 1. 检查端口占用
./process_manager.sh status

# 2. 清理旧进程
./process_manager.sh cleanup

# 3. 启动新测试
./process_manager.sh start "your_command" "test_name" 30
```

### 2. 测试中监控

```bash
# 在测试运行期间，定期检查状态
watch -n 5 './process_manager.sh status'
```

### 3. 测试后清理

```bash
# 测试完成后，确保清理所有资源
./process_manager.sh cleanup

# 验证清理结果
./process_manager.sh status
```

## 🔄 集成到现有工作流

### 1. CI/CD集成

```yaml
# GitHub Actions示例
- name: Run eMQTT-Bench tests
  run: |
    ./process_manager.sh start "./emqtt_bench conn -h ${{ env.MQTT_HOST }} -p ${{ env.MQTT_PORT }} -c 10 --prometheus --restapi 9090" "CI测试" 60
    
- name: Cleanup processes
  if: always()
  run: |
    ./process_manager.sh cleanup
```

### 2. 自动化脚本

```bash
#!/bin/bash
# 自动化测试脚本

source "./process_manager.sh"
setup_signal_handlers

# 运行多个测试
tests=(
    "连接测试:./emqtt_bench conn -h localhost -p 1883 -c 5 --prometheus --restapi 9090"
    "发布测试:./emqtt_bench pub -h localhost -p 1883 -c 5 -I 1000 -t test/topic --prometheus --restapi 9091"
    "订阅测试:./emqtt_bench sub -h localhost -p 1883 -c 5 -t test/topic --prometheus --restapi 9092"
)

for test in "${tests[@]}"; do
    IFS=':' read -r name command <<< "$test"
    echo "运行测试: $name"
    start_emqtt_bench "$command" "$name"
    wait_for_completion 30
done

echo "所有测试完成"
```

## 📚 相关文档

- [Prometheus监控指南](./PROMETHEUS_MONITORING_GUIDE.md)
- [配置指南](./CONFIG_GUIDE.md)
- [基准测试结果收集](./BENCHMARK_RESULTS_COLLECTION.md)

---

*作者: Jaxon*  
*最后更新: 2024-12-19*
