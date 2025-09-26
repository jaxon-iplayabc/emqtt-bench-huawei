# eMQTT-Bench 自动数据收集器使用指南

## 概述

自动数据收集器是一个全新的功能，让用户只需运行一个命令就能完成所有测试、数据收集和报告生成。无需手动配置复杂的参数，系统会自动处理整个过程。

## 🚀 快速开始

### 1. 基本使用

```bash
# 进入metrics目录
cd metrics/

# 运行自动数据收集器
uv run main.py
```

### 2. 测试功能

```bash
# 测试所有组件是否正常工作
uv run test_auto_collector.py
```

## 📋 功能特性

### ✨ 自动化流程
- **一键启动**：运行 `main.py` 即可开始
- **智能配置**：自动加载配置或使用默认设置
- **自动测试**：依次执行连接、发布、订阅测试
- **实时收集**：自动收集Prometheus指标数据
- **自动报告**：测试完成后生成HTML报告

### 🛡️ 优雅中断
- **Ctrl+C 支持**：随时中断测试
- **自动清理**：中断时自动清理所有进程
- **保存结果**：已完成的测试结果会被保存
- **生成报告**：中断时也会生成部分报告

### 📊 报告生成
- **HTML格式**：美观的网页报告
- **详细统计**：测试结果、指标数据、时间统计
- **响应式设计**：支持各种屏幕尺寸
- **数据文件**：JSON格式的原始指标数据

## ⚙️ 配置说明

### 默认配置
系统使用以下默认配置：

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

### 配置选项
- **host**: MQTT服务器地址
- **port**: MQTT端口
- **client_count**: 客户端数量
- **msg_interval**: 消息间隔(毫秒)
- **prometheus_port**: Prometheus起始端口
- **test_duration**: 每个测试的持续时间(秒)
- **use_huawei_auth**: 是否使用华为云认证

### 华为云配置
如果启用华为云认证，系统会：
- 使用华为云IoT平台地址
- 应用华为云认证参数
- 执行华为云特定的测试

## 🔄 工作流程

### 1. 启动阶段
```
🚀 eMQTT-Bench 自动数据收集器
============================================================
✨ 自动执行测试、收集数据并生成报告
💡 按 Ctrl+C 可随时中断并生成报告
```

### 2. 配置阶段
- 加载现有配置文件
- 询问是否使用默认配置
- 显示配置摘要
- 确认开始收集

### 3. 测试执行阶段
- 连接测试 (端口: 9090)
- 发布测试 (端口: 9091)
- 订阅测试 (端口: 9092)
- 华为云测试 (端口: 9093, 可选)

### 4. 数据收集阶段
- 等待指标稳定
- 收集Prometheus指标
- 保存JSON格式数据
- 显示收集状态

### 5. 报告生成阶段
- 生成HTML报告
- 显示统计摘要
- 保存所有文件

## 📁 输出文件

### HTML报告
- 文件名：`auto_collection_report_YYYYMMDD_HHMMSS.html`
- 内容：测试结果、指标统计、时间信息
- 格式：美观的网页格式

### 指标数据文件
- 文件名：`metrics_测试类型_YYYYMMDD_HHMMSS.json`
- 内容：完整的Prometheus指标数据
- 格式：JSON格式，便于后续分析

### 示例文件
```
auto_collection_report_20241219_143022.html
metrics_connection_test_20241219_143015.json
metrics_publish_test_20241219_143025.json
metrics_subscribe_test_20241219_143035.json
```

## 🎯 使用场景

### 1. 快速性能测试
```bash
# 使用默认配置快速测试
cd metrics/
uv run main.py
# 选择 "是否使用默认配置?" -> y
# 选择 "是否开始自动数据收集?" -> y
```

### 2. 华为云IoT测试
```bash
# 修改配置文件启用华为云认证
# 编辑 emqtt_test_config.json
{
  "use_huawei_auth": true,
  "device_prefix": "your_device",
  "huawei_secret": "your_secret"
}

# 运行测试
uv run main.py
```

### 3. 自定义配置测试
```bash
# 运行并自定义配置
uv run main.py
# 选择 "是否使用默认配置?" -> n
# 输入自定义参数
```

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用
```
错误: 端口 9090 已被占用
解决: 修改配置文件中的 prometheus_port 参数
```

#### 2. emqtt_bench 未找到
```
错误: 未找到 emqtt_bench 可执行文件
解决: 确保在项目根目录运行，或修改配置文件中的 emqtt_bench_path
```

#### 3. 依赖包缺失
```
错误: 无法导入 rich 模块
解决: 运行 uv sync 安装依赖
```

### 调试模式
```bash
# 运行测试脚本检查环境
uv run test_auto_collector.py
```

## 📈 性能优化

### 建议配置
- **轻量测试**：client_count=5, test_duration=30
- **中等测试**：client_count=50, test_duration=60
- **压力测试**：client_count=500, test_duration=120

### 资源监控
- 监控CPU和内存使用
- 观察网络连接数
- 检查磁盘空间

## 🎉 最佳实践

### 1. 测试前准备
- 确保MQTT服务器运行正常
- 检查网络连接
- 验证emqtt_bench可执行文件

### 2. 测试过程中
- 不要关闭终端窗口
- 避免同时运行多个测试实例
- 监控系统资源使用

### 3. 测试后分析
- 查看HTML报告了解整体情况
- 分析JSON数据文件进行深度分析
- 对比不同测试的结果

## 📞 技术支持

如果遇到问题，请：
1. 运行 `uv run test_auto_collector.py` 检查环境
2. 查看生成的错误日志
3. 检查配置文件格式
4. 确认依赖包安装完整

---

**作者**: Jaxon  
**日期**: 2024-12-19  
**版本**: 1.0.0
