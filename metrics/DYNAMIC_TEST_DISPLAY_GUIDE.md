# 动态测试显示指南

## 概述

系统现在支持根据用户是否选择华为云认证，动态显示不同的测试类型。无论用户选择什么测试，都只会显示三种测试类型，确保界面简洁统一。

## 功能特性

### 🔄 **动态测试显示**

根据 `config.use_huawei_auth` 配置，系统会自动显示对应的测试类型：

#### 标准MQTT测试模式 (`use_huawei_auth = False`)

**显示模式**: 🔗 标准MQTT测试模式
**测试类型**:
1. **连接测试** (端口: prometheus_port)
2. **发布测试** (端口: prometheus_port + 1)  
3. **订阅测试** (端口: prometheus_port + 2)

#### 华为云测试模式 (`use_huawei_auth = True`)

**显示模式**: ☁️ 华为云测试模式
**测试类型**:
1. **华为云连接测试** (端口: prometheus_port)
2. **华为云发布测试** (端口: prometheus_port + 1)
3. **华为云订阅测试** (端口: prometheus_port + 2)

## 界面显示逻辑

### 📋 **测试选择界面**

```
🧪 测试项选择
═══════════════════════════════════════════════════════════

☁️ 华为云测试模式
使用华为云IoT平台认证和设备管理功能

📋 可用的测试项:
┌────┬─────────────────┬─────────────────────────────────────┬──────┬────────┐
│序号│ 测试名称        │ 描述                               │ 端口 │ 状态   │
├────┼─────────────────┼─────────────────────────────────────┼──────┼────────┤
│ 1  │ 华为云连接测试  │ 测试华为云IoT平台连接功能          │ 9090 │ ✅ 启用│
│ 2  │ 华为云发布测试  │ 测试华为云IoT平台消息发布功能      │ 9091 │ ✅ 启用│
│ 3  │ 华为云订阅测试  │ 测试华为云IoT平台消息订阅功能      │ 9092 │ ✅ 启用│
└────┴─────────────────┴─────────────────────────────────────┴──────┴────────┘

请选择要运行的测试项:
  1. 运行所有测试
  2. 自定义选择测试项
  3. 快速测试（仅华为云连接测试）
```

### 🎯 **快速测试选项**

根据测试模式动态显示：

- **标准MQTT模式**: "快速测试（仅连接测试）"
- **华为云模式**: "快速测试（仅华为云连接测试）"

## 端口分配策略

### 标准MQTT测试模式
| 测试类型 | 端口 | 描述 |
|---------|------|------|
| 连接测试 | prometheus_port | 标准MQTT连接测试 |
| 发布测试 | prometheus_port + 1 | 标准MQTT发布测试 |
| 订阅测试 | prometheus_port + 2 | 标准MQTT订阅测试 |

### 华为云测试模式
| 测试类型 | 端口 | 描述 |
|---------|------|------|
| 华为云连接测试 | prometheus_port | 华为云连接测试 |
| 华为云发布测试 | prometheus_port + 1 | 华为云发布测试 |
| 华为云订阅测试 | prometheus_port + 2 | 华为云订阅测试 |

## 代码实现

### 核心逻辑

```python
def _select_test_items(self, config: TestConfig) -> List[Dict[str, Any]]:
    """选择要运行的测试项"""
    # 根据华为云认证状态定义测试项
    if config.use_huawei_auth:
        # 华为云测试模式：显示华为云的三种测试类型
        available_tests = [
            {"name": "华为云连接测试", "port": config.prometheus_port, ...},
            {"name": "华为云发布测试", "port": config.prometheus_port + 1, ...},
            {"name": "华为云订阅测试", "port": config.prometheus_port + 2, ...}
        ]
    else:
        # 标准MQTT测试模式：显示标准的三种测试类型
        available_tests = [
            {"name": "连接测试", "port": config.prometheus_port, ...},
            {"name": "发布测试", "port": config.prometheus_port + 1, ...},
            {"name": "订阅测试", "port": config.prometheus_port + 2, ...}
        ]
```

### 界面显示

```python
# 显示测试模式说明
if config.use_huawei_auth:
    console.print("\n[green]☁️ 华为云测试模式[/green]")
    console.print("[dim]使用华为云IoT平台认证和设备管理功能[/dim]")
else:
    console.print("\n[blue]🔗 标准MQTT测试模式[/blue]")
    console.print("[dim]使用标准MQTT协议进行测试[/dim]")
```

## 优势

### 🎯 **用户体验优化**
1. **界面简洁**: 始终只显示三种测试类型，避免界面混乱
2. **逻辑清晰**: 根据认证模式自动显示对应测试
3. **操作简单**: 用户无需关心复杂的测试配置

### 🔧 **技术优势**
1. **代码复用**: 相同的端口分配逻辑
2. **配置驱动**: 基于配置自动切换测试模式
3. **扩展性强**: 易于添加新的测试模式

### 📊 **测试覆盖**
1. **全面覆盖**: 每种模式都包含连接、发布、订阅测试
2. **专业分析**: 针对不同模式的专业分析逻辑
3. **灵活选择**: 支持全量测试、自定义选择、快速测试

## 使用场景

### 标准MQTT测试
- 测试标准MQTT服务器
- 验证MQTT协议功能
- 性能基准测试

### 华为云测试
- 测试华为云IoT平台集成
- 验证设备认证和连接
- 测试华为云特定功能

## 配置示例

### 标准MQTT配置
```json
{
  "use_huawei_auth": false,
  "host": "mqtt.example.com",
  "port": 1883,
  "prometheus_port": 9090
}
```

### 华为云配置
```json
{
  "use_huawei_auth": true,
  "host": "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com",
  "port": 1883,
  "prometheus_port": 9090,
  "device_prefix": "speaker",
  "huawei_secret": "12345678"
}
```

---

*本指南说明了动态测试显示功能的实现和使用方法。*
