# 数据过滤功能指南

## 📊 概述

本指南介绍了eMQTT-Bench项目中的数据过滤功能，该功能可以自动识别和移除raw_data文件中的无效数据，生成清洁的、仅包含有用指标的数据文件。

## 🎯 功能特点

### 自动数据过滤
- **零值指标过滤**: 移除值为0且对测试无意义的指标
- **Erlang VM指标过滤**: 移除与MQTT测试性能无关的系统指标
- **重复help_text过滤**: 移除冗余的描述信息
- **直方图桶数据优化**: 只保留有意义的桶数据

### 智能保留机制
- **关键性能指标**: 自动保留连接成功率、发布成功率等关键指标
- **延迟和持续时间指标**: 保留所有包含"duration"和"latency"的指标
- **非零值指标**: 保留所有非零值的指标

### 自动过滤流程
- **测试完成后自动触发**: 在测试执行完成后，系统会自动执行数据过滤操作
- **批量处理**: 一次性处理所有测试结果的数据
- **统计信息显示**: 显示详细的过滤统计信息，包括原始数量、过滤后数量、移除比例等
- **自动保存**: 过滤后的数据自动保存到 `test_data/filtered_data/` 目录

## 🔧 使用方法

### 1. 运行自动数据收集（包含过滤）
```bash
cd metrics
python3 main.py
# 选择选项 1: 运行自动数据收集（包含数据过滤）
```

**自动过滤流程：**
- 测试执行完成后，系统会自动执行数据过滤操作
- 在生成最终报告之前，会处理所有测试结果的数据
- 自动保存过滤后的数据到 `test_data/filtered_data/` 目录
- 显示详细的过滤统计信息

### 2. 仅过滤现有raw_data文件
```bash
cd metrics
python3 main.py
# 选择选项 2: 仅过滤现有raw_data文件
```

### 3. 测试数据过滤功能
```bash
cd metrics
python3 simple_filter_test.py
```

### 4. 测试自动过滤功能
```bash
cd metrics
python3 test_auto_filter.py
```

## 📁 文件结构

### 原始数据文件
```
test_data/raw_data/
├── 华为云连接测试_20250930_232907.json
├── 华为云发布测试_20250930_233015.json
├── 华为云订阅测试_20250930_233127.json
└── 华为云广播测试_20250930_233239.json
```

### 过滤后数据文件
```
test_data/filtered_data/
├── filtered_华为云连接测试_20241219_143022.json
├── filtered_华为云发布测试_20241219_143025.json
├── filtered_华为云订阅测试_20241219_143028.json
└── filtered_华为云广播测试_20241219_143031.json
```

## 📊 过滤规则详解

### 1. 零值指标过滤
移除以下零值指标：
- `connection_idle`, `recv`, `connect_fail`, `pub_fail`
- `pub_overrun`, `connect_retried`, `sub_fail`
- `reconnect_succ`, `sub`, `publish_latency`
- `pub_succ`, `connection_timeout`, `connection_refused`
- `unreachable`, `pub`

### 2. Erlang VM系统指标过滤
移除以下系统指标：
- `erlang_vm_memory_*` - 内存使用指标
- `erlang_vm_msacc_*` - 微状态统计
- `erlang_vm_statistics_*` - 系统统计
- `erlang_vm_dirty_*` - 脏调度器指标
- `erlang_vm_ets_*` - ETS表指标
- `erlang_vm_logical_*` - 逻辑处理器指标
- `erlang_vm_port_*` - 端口指标
- `erlang_vm_process_*` - 进程指标
- `erlang_vm_schedulers_*` - 调度器指标
- `erlang_vm_smp_*` - SMP支持指标
- `erlang_vm_thread_*` - 线程指标
- `erlang_vm_time_*` - 时间指标
- `erlang_vm_wordsize_*` - 字长指标
- `erlang_vm_atom_*` - 原子指标
- `erlang_vm_allocators` - 分配器指标

### 3. 重复help_text过滤
移除重复的描述信息：
- `connection_idle connection_idle`
- `recv recv`
- `connect_fail connect_fail`
- 等等...

### 4. 关键指标保留
自动保留以下关键指标：
- `connect_succ` - 连接成功数
- `pub_succ` - 发布成功数
- `recv` - 接收消息数
- `publish_latency` - 发布延迟
- `mqtt_client_connect_duration` - 连接持续时间
- `mqtt_client_handshake_duration` - 握手持续时间
- `e2e_latency` - 端到端延迟
- `mqtt_client_subscribe_duration` - 订阅持续时间

## 📈 过滤效果统计

### 典型过滤结果
- **原始指标数量**: 1442个
- **过滤后指标数量**: 约200-300个
- **数据减少比例**: 70-80%
- **文件大小减少**: 60-70%

### 保留的指标类型
1. **连接性能指标**: 连接成功率、连接延迟
2. **消息传输指标**: 发布成功率、接收消息数
3. **延迟指标**: 端到端延迟、发布延迟
4. **持续时间指标**: 连接持续时间、握手持续时间

## 🔍 过滤后数据结构

```json
{
  "test_name": "华为云连接测试",
  "test_type": "测试华为云IoT平台连接功能",
  "start_time": "2025-09-30T23:27:59.316039",
  "end_time": "2025-09-30T23:29:02.393921",
  "duration": 63.077882,
  "port": 9090,
  "success": true,
  "error_message": null,
  "config": { ... },
  "filtered_metrics": [
    {
      "timestamp": "2025-09-30T23:28:04.351819",
      "name": "connect_succ",
      "value": 10.0,
      "labels": {"port": "9090"},
      "help_text": "connect_succ connect_succ",
      "metric_type": "connect_succ counter"
    }
  ],
  "filter_info": {
    "original_count": 1442,
    "filtered_count": 287,
    "removed_count": 1155,
    "filter_timestamp": "2024-12-19T14:30:22.123456",
    "source_file": "华为云连接测试_20250930_232907.json"
  }
}
```

## 🚀 使用建议

### 1. 数据分析
- 使用过滤后的数据进行性能分析
- 重点关注保留的关键性能指标
- 结合原始数据进行对比分析

### 2. 报告生成
- 过滤后的数据更适合生成报告
- 减少报告文件大小
- 提高报告生成速度

### 3. 存储优化
- 过滤后的数据文件更小
- 便于长期存储和传输
- 减少存储成本

## ⚠️ 注意事项

1. **备份原始数据**: 过滤前请确保原始数据已备份
2. **验证过滤结果**: 检查过滤后的数据是否包含所需指标
3. **自定义过滤规则**: 可根据需要修改过滤规则
4. **性能影响**: 大量数据过滤可能消耗一定时间

## 🔧 自定义过滤规则

如需自定义过滤规则，请修改`main.py`中的`invalid_data_patterns`配置：

```python
self.invalid_data_patterns = {
    'zero_value_metrics': [...],  # 零值指标列表
    'erlang_vm_metrics': [...],   # Erlang VM指标列表
    'histogram_buckets': [...],   # 直方图桶列表
    'redundant_help_text': [...]  # 重复help_text列表
}
```

## 📞 技术支持

如有问题或建议，请联系：
- 作者: Jaxon
- 日期: 2024-12-19
- 项目: eMQTT-Bench 数据过滤功能
