# 数据过滤功能使用说明

## 概述

本系统提供了智能的数据过滤功能，能够根据不同的测试类型自动过滤掉无效的数据指标，大幅减少文件大小并提高数据分析效率。

## 功能特点

### 🎯 智能过滤规则
- **连接测试**: 自动移除pub相关指标（pub_fail, pub_overrun, pub_succ等）
- **发布测试**: 自动移除sub相关指标（sub_fail, sub, reconnect_succ等）
- **订阅测试**: 自动移除pub相关指标（pub_fail, pub_overrun, pub_succ等）
- **广播测试**: 自动移除无意义指标（connect_retried等）

### 🧹 通用过滤规则
- 移除Erlang VM系统指标（与MQTT测试性能无关）
- 移除零值直方图桶数据
- 移除重复的help_text
- 移除零值且非关键指标

### 📊 过滤效果
- **文件大小减少**: 约97%（从33MB减少到650KB-1MB）
- **指标数量减少**: 从83,636个指标减少到2,204-3,248个指标
- **保留关键指标**: 连接成功率、发布成功率、接收数量、延迟等

## 使用方法

### 方法1: 集成到主程序
运行主程序时，数据过滤会自动执行：

```bash
cd /Users/admin/Workspace/python/emqtt-bench-huawei/metrics
python3 main.py
# 选择选项1: 运行自动数据收集（包含数据过滤）
```

### 方法2: 独立过滤持续指标文件
专门过滤持续指标文件：

```bash
cd /Users/admin/Workspace/python/emqtt-bench-huawei/metrics
python3 filter_continuous_metrics.py
```

### 方法3: 使用主程序的过滤选项
```bash
cd /Users/admin/Workspace/python/emqtt-bench-huawei/metrics
python3 main.py
# 选择选项3: 过滤持续指标文件
```

## 输出文件

### 过滤后的文件位置
- **持续指标文件**: `metrics/reports/filtered/`
- **测试数据文件**: `test_data/filtered_data/`

### 文件命名规则
- 持续指标: `filtered_continuous_metrics_测试类型_时间戳.json`
- 测试数据: `filtered_测试名称_时间戳.json`

## 过滤统计信息

每个过滤后的文件都包含详细的过滤统计信息：

```json
{
  "filter_info": {
    "original_count": 83636,
    "filtered_count": 3248,
    "removed_count": 80388,
    "filter_timestamp": "2025-01-01T18:49:43.123456"
  }
}
```

## 技术实现

### 核心组件
1. **TestSpecificFilter**: 测试特定过滤器类
2. **过滤规则配置**: 每种测试类型的无效数据规则
3. **自动集成**: 集成到main.py的测试流程中

### 过滤逻辑
1. 根据测试名称识别测试类型
2. 应用测试特定的过滤规则
3. 应用通用过滤规则
4. 保留关键性能指标
5. 生成过滤统计信息

## 配置自定义过滤规则

可以在 `test_specific_filter.py` 中修改过滤规则：

```python
self.test_specific_rules = {
    "华为云连接测试": {
        "invalid_metrics": [
            "pub_fail", "pub_overrun", "pub_succ", "pub",
            "sub_fail", "sub", "reconnect_succ",
            "publish_latency"
        ],
        "keep_metrics": [
            "connect_succ", "connect_fail", "connect_retried",
            "connection_timeout", "connection_refused", "unreachable",
            "connection_idle", "recv"
        ]
    }
    # ... 其他测试类型
}
```

## 注意事项

1. **备份原始数据**: 过滤操作会创建新文件，原始数据不会被修改
2. **重复过滤**: 系统会检查是否已存在过滤后的文件，避免重复处理
3. **文件编码**: 支持中文文件名和内容
4. **性能优化**: 过滤过程会显示详细的进度信息

## 故障排除

### 常见问题
1. **找不到文件**: 确保reports目录中存在continuous_metrics_*.json文件
2. **权限错误**: 确保有写入权限创建filtered目录
3. **编码问题**: 使用python3而不是python2

### 调试模式
可以单独运行过滤器进行调试：

```python
from test_specific_filter import TestSpecificFilter
filter_processor = TestSpecificFilter()
filtered_files = filter_processor.auto_filter_all_continuous_files("reports")
```

## 更新日志

- **2025-01-01**: 初始版本，支持四种测试类型的智能过滤
- 实现了97%的数据压缩率
- 集成到主程序自动化流程
- 支持中文文件名处理
