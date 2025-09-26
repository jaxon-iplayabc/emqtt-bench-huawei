# emqtt-bench changelog

## 压测结果显示系统设计实现 (2025-01-27) - by Jaxon

### 重大功能更新
- **综合压测结果显示系统**：
  - 创建了完整的压测结果显示系统 `benchmark_display_system.py`
  - 提供实时监控、Web仪表盘和详细报告生成三种显示模式
  - 支持连接、发布、订阅等多种测试类型的指标展示
  - 集成Prometheus指标收集和华为云IoT平台支持

### 核心功能实现
- **实时监控显示**：
  - 实时性能指标展示：连接成功率、消息吞吐量、延迟等
  - 直观的状态指示器：颜色编码显示性能状态
  - 自动性能评级：A+到D的评分系统
  - 智能优化建议：基于当前性能提供改进建议

- **Web仪表盘**：
  - 响应式Web界面，支持多设备访问
  - 实时数据更新（每5秒自动刷新）
  - 交互式图表和数据可视化
  - 历史数据查看和趋势分析

- **详细报告生成**：
  - 性能摘要和关键指标统计
  - 趋势分析和对比分析
  - 优化建议和性能评估
  - HTML格式的专业报告

### 监控指标体系
- **连接性能指标**：
  - 连接成功率、失败率、重连次数
  - 连接超时、被拒绝、网络不可达统计
  - 活跃连接数监控

- **消息性能指标**：
  - 发送/接收消息数统计
  - 消息失败率和溢出监控
  - 订阅成功/失败统计

- **延迟性能指标**：
  - 发布延迟、连接延迟、握手延迟
  - 端到端延迟监控
  - 延迟分布分析

- **系统性能指标**：
  - CPU、内存、网络使用率
  - 错误率统计和分析

### 技术实现特点
- **多数据源支持**：
  - Prometheus指标作为主要数据源
  - QoE (Quality of Experience) 数据集成
  - 支持多端口并行监控

- **智能分析系统**：
  - 基于阈值的性能评估
  - 自动生成优化建议
  - 综合评分系统（A-F等级）
  - 关键洞察和趋势分析

- **用户友好设计**：
  - 命令行实时显示
  - Web仪表盘自动打开
  - 一键报告生成
  - 快速启动脚本

### 新增文件
- **`benchmark_display_system.py`**: 核心显示系统实现
- **`display_example.py`**: 使用示例和演示脚本
- **`display_config.json`**: 配置文件和使用说明
- **`DISPLAY_SYSTEM_GUIDE.md`**: 详细使用指南
- **`quick_display.sh`**: 快速启动脚本

### 使用方法
```bash
# 实时监控模式
python benchmark_display_system.py --mode live --test-type conn

# Web仪表盘模式
python benchmark_display_system.py --mode web --web-port 8080

# 报告生成模式
python benchmark_display_system.py --mode report --output report.html

# 快速启动脚本
./quick_display.sh -t conn -m live -c 10 -i 100
```

### 性能评估标准
- **连接成功率评级**: A+ (95-100%) 到 D (<70%)
- **延迟性能评级**: 优秀 (<100ms) 到 较差 (>1000ms)
- **错误率评级**: 优秀 (0%) 到 较差 (>5%)

### 预期效果
通过实施这个显示系统，eMQTT-Bench将获得：
1. **专业性提升** - 从基础压测工具升级为专业性能分析平台
2. **用户体验改善** - 直观的指标展示和实时监控能力
3. **决策支持增强** - 基于数据的性能优化建议
4. **竞争优势** - 在MQTT压测工具领域建立技术领先地位

## 文档冗余清理和代码同步优化 (2025-01-27) - by Jaxon

### 文档整合优化
- **创建统一华为云指南**：
  - 创建了 `HUAWEI_CLOUD_GUIDE.md` 作为华为云使用的唯一权威文档
  - 整合了所有华为云相关功能的使用说明和最佳实践
  - 提供了完整的使用场景和故障排查指南

- **删除冗余文档**：
  - 删除了 `HUAWEI_CLOUD_SUCCESS_GUIDE.md`
  - 删除了 `HUAWEI_CLOUD_WORKING_SOLUTION.md`
  - 删除了 `HUAWEI_CLOUD_PREFIX_SOLUTION.md`
  - 删除了 `HUAWEI_AUTH_CORRECTION.md`
  - 减少了文档维护成本和用户困惑

### 代码与文档同步
- **更新版本要求**：
  - 将 README.md 中的 Erlang/OTP 版本要求从 "22.3+" 更新为 "27.2+"
  - 与 rebar.config 中的实际要求保持一致

- **统一参数描述**：
  - 统一了华为云认证参数的描述格式
  - 明确说明不需要 `huawei:` 前缀，使用 `--huawei-auth` 自动判断
  - 更新了所有示例命令以反映最新的代码实现

- **完善功能描述**：
  - 在 README.md 中更新了华为云支持部分
  - 添加了 `--device-id` 参数的说明
  - 统一了文档间的交叉引用

### 文档结构优化
- **建立清晰的文档层次**：
  - `HUAWEI_CLOUD_GUIDE.md` - 华为云完整使用指南
  - `DEVICE_ID_GUIDE.md` - 设备ID参数使用指南
  - `HUAWEI_ERLANG_AUTH_GUIDE.md` - 认证机制技术参考
  - `HUAWEI_CLOUD_TEST_GUIDE.md` - 测试指南

- **改进用户体验**：
  - 提供了快速开始示例
  - 添加了常见问题解答
  - 统一了命令格式和参数说明

### 技术改进
- **参数描述标准化**：
  - 统一了所有华为云认证参数的描述
  - 明确了参数优先级和默认值
  - 提供了完整的参数参考

- **示例命令更新**：
  - 所有示例都使用最新的参数格式
  - 移除了过时的 `huawei:` 前缀示例
  - 添加了更多实用的使用场景

## 连接测试指标专业分析 (2024-12-19) - by Jaxon

### 专业产品设计分析
- **连接测试指标维度分析**：
  - 从专业产品设计者角度深入分析了连接测试的核心指标维度
  - 识别了5大关键指标类别：连接建立性能、并发连接能力、网络性能、系统资源消耗、错误分析
  - 分析了当前项目指标收集的现状和优化空间
  - 提供了专业的产品设计建议和可视化方案

### 新增设计文档
- **连接测试仪表盘设计**：
  - 创建了`connection_test_dashboard_design.md`专业设计文档
  - 详细设计了连接测试的专业化指标展示方案
  - 包含完整的可视化设计规范和交互设计规范
  - 提供了移动端适配和响应式设计方案
  - 设计了分层展示架构：核心KPI面板、实时监控面板、详细分析面板

- **指标优化建议**：
  - 创建了`connection_test_metrics_recommendations.md`优化建议文档
  - 提供了具体的指标计算方法和数据收集优化建议
  - 包含实时数据处理和告警系统的技术实现方案
  - 提供了分阶段实施建议和预期效果评估

### 核心指标优化建议
- **连接建立性能指标**：
  - 连接成功率计算和可视化展示
  - 平均连接时间统计和趋势分析
  - 连接建立速率监控
  - 连接时间分布统计（P50、P90、P95、P99）

- **并发连接能力指标**：
  - 最大并发连接数监控
  - 连接数增长曲线分析
  - 连接稳定性评估
  - 连接池状态监控

- **网络性能指标**：
  - TCP握手延迟分析
  - MQTT握手延迟监控
  - 网络往返时间统计
  - 网络质量综合评估

- **系统资源消耗指标**：
  - 内存使用率分析和趋势监控
  - CPU使用率实时监控
  - 文件描述符使用情况
  - 网络带宽使用监控

- **错误分析与诊断**：
  - 错误类型分布分析
  - 错误时间线追踪
  - 错误影响评估
  - 自动诊断建议生成

### 可视化设计规范
- **颜色规范**：定义了成功、警告、错误、信息、中性状态的标准化颜色
- **动画效果**：设计了数据更新、状态变化、加载状态、错误提示的动画效果
- **响应式设计**：提供了桌面端、平板端、手机端的适配方案
- **交互设计**：包含时间范围选择、指标对比、钻取分析、实时刷新等功能

### 技术实现建议
- **数据收集优化**：提供了增强的指标收集器架构设计
- **实时数据处理**：设计了WebSocket实时数据推送方案
- **告警系统**：定义了智能告警规则和阈值配置
- **报告生成**：提供了综合报告生成器的实现方案

### 实施计划
- **阶段1**：基础指标增强（1-2周）
- **阶段2**：可视化优化（2-3周）
- **阶段3**：高级功能（3-4周）
- **阶段4**：集成优化（1-2周）

## 连接测试专业分析功能实施 (2024-12-19) - by Jaxon

### 核心功能实现
- **连接测试指标收集器**：
  - 创建了`connection_test_metrics_collector.py`专业指标收集器
  - 实时收集连接建立性能、并发能力、网络性能等核心指标
  - 支持系统资源监控和错误分析
  - 提供性能摘要和指标导出功能

- **专业仪表盘系统**：
  - 创建了`connection_test_dashboard.py`专业仪表盘
  - 提供直观的指标展示和实时监控
  - 包含连接建立性能、并发连接能力、网络性能分析等面板
  - 支持Web服务器和静态HTML报告生成

- **增强报告生成器**：
  - 在`enhanced_report_generator.py`中新增连接测试分析功能
  - 添加专门的连接测试标签页
  - 实现智能性能评估和优化建议生成
  - 提供综合评分系统（A-F等级）

### 集成工具
- **连接测试集成器**：
  - 创建了`connection_test_integration.py`集成脚本
  - 提供完整的连接测试分析流程
  - 支持实时监控和报告生成
  - 包含Web服务器启动功能

- **快速演示工具**：
  - 创建了`quick_connection_test.py`快速演示脚本
  - 使用模拟数据展示连接测试功能
  - 适合快速体验和功能演示

### 核心指标维度
- **连接建立性能**：
  - 连接成功率计算和可视化
  - 平均连接时间统计和趋势分析
  - 连接建立速率监控
  - 连接时间分布统计（P50、P90、P95、P99）

- **并发连接能力**：
  - 最大并发连接数监控
  - 连接数增长曲线分析
  - 连接稳定性评估
  - 连接池状态监控

- **网络性能指标**：
  - TCP握手延迟分析
  - MQTT握手延迟监控
  - 网络往返时间统计
  - 网络质量综合评估

- **系统资源消耗**：
  - 内存使用率分析和趋势监控
  - CPU使用率实时监控
  - 文件描述符使用情况
  - 网络带宽使用监控

- **错误分析与诊断**：
  - 错误类型分布分析
  - 错误时间线追踪
  - 错误影响评估
  - 自动诊断建议生成

### 专业可视化设计
- **分层展示架构**：
  - 核心KPI面板：连接成功率、平均连接时间、连接建立速率、当前连接数
  - 实时监控面板：连接数趋势图、延迟监控图、错误率监控图
  - 详细分析面板：性能分析、错误分析、资源使用分析

- **交互式数据探索**：
  - 时间范围选择器支持不同时间粒度查看
  - 指标对比功能支持多测试结果对比
  - 钻取分析功能支持点击图表查看详细数据
  - 实时刷新支持1秒、5秒、10秒等刷新频率

- **智能分析系统**：
  - 基于阈值的性能评估
  - 自动生成优化建议
  - 综合评分系统（A-F等级）
  - 关键洞察和趋势分析

### 技术实现特点
- **数据收集优化**：
  - 增强的指标收集器架构设计
  - 支持多种数据格式和来源
  - 实时数据处理和缓存机制
  - 错误处理和恢复机制

- **实时数据处理**：
  - WebSocket实时数据推送方案
  - 多线程数据收集和处理
  - 内存优化的数据存储
  - 自动数据清理和归档

- **报告生成系统**：
  - 综合报告生成器实现
  - 支持多种输出格式（HTML、JSON、PDF）
  - 自定义报告模板
  - 批量报告生成

### 使用指南
- **快速开始**：
  - 创建了`CONNECTION_TEST_GUIDE.md`详细使用指南
  - 包含快速演示、实际测试、配置选项等说明
  - 提供故障排除和最佳实践建议
  - 支持扩展开发和自定义功能

- **多种使用方式**：
  - 集成到现有测试流程
  - 独立运行分析工具
  - 快速演示和功能体验
  - Web仪表盘实时监控

### 预期效果
通过实施这些功能，eMQTT-Bench将获得：
1. **专业性提升** - 从基础压测工具升级为专业性能分析平台
2. **用户体验改善** - 直观的指标展示和实时监控能力
3. **决策支持增强** - 基于数据的性能优化建议
4. **竞争优势** - 在MQTT压测工具领域建立技术领先地位

## 端口清理和进程管理优化 (2024-12-19) - by Jaxon

### 问题修复
- **端口9090未释放问题修复**：
  - 修复了测试结束后REST API端口9090没有被正确释放的问题
  - 在`_execute_single_test`方法中添加了`finally`块确保进程清理
  - 改进了进程终止逻辑，增加了优雅终止和强制终止的机制
  - 添加了端口释放验证，确保端口在测试完成后被正确释放
  - 增强了错误处理，即使清理失败也会尝试强制清理端口

### 新增功能
- **端口清理工具**：
  - 新增`scripts/cleanup_ports.py`端口清理工具
  - 支持清理指定端口、所有常用端口、eMQTT-Bench进程
  - 提供交互式和命令行两种使用方式
  - 支持强制清理模式，无需用户确认
  - 显示清理前后的端口占用状态

- **便捷清理脚本**：
  - 新增`cleanup_ports.sh`便捷清理脚本
  - 支持多种清理模式：指定端口、所有端口、进程清理
  - 提供彩色输出和友好的用户界面
  - 集成Python清理工具，提供统一的清理接口

### 改进内容
- **进程管理器优化**：
  - 改进了`ProcessManager.terminate_process`方法
  - 增加了进程终止的等待时间和验证机制
  - 添加了更详细的日志输出，便于调试
  - 改进了异常处理，处理`ProcessLookupError`等特殊情况

- **测试执行流程优化**：
  - 在测试完成后自动清理进程和端口
  - 添加了端口占用检查和自动释放机制
  - 改进了错误信息显示，提供更清晰的反馈
  - 增强了测试的健壮性，确保资源正确释放

### 使用方法
```bash
# 清理指定端口
./cleanup_ports.sh port 9090

# 清理所有常用端口
./cleanup_ports.sh all

# 清理所有eMQTT-Bench进程
./cleanup_ports.sh processes

# 强制清理所有
./cleanup_ports.sh force

# 交互式清理
./cleanup_ports.sh
```

## 增强版HTML报告系统修复 (2024-12-19) - by Jaxon

### 修复内容
- **完整指标数据标签页修复**：
  - 修复了"完整指标数据"部分显示空白的问题
  - 改进了数据提取逻辑，直接从原始数据中提取指标
  - 支持不同的数据结构格式（list和dict）
  - 添加了空数据处理，显示友好的提示信息
  - 实现了指标排序，按测试名称和指标名称排序
  - 完善了表格显示，包含所有必要的列

- **性能趋势分析标签页修复**：
  - 修复了"性能趋势分析"部分显示空白的问题
  - 添加了trendsChart的JavaScript初始化代码
  - 实现了多Y轴的趋势图表（延迟、吞吐量、CPU使用率）
  - 增加了趋势统计面板和趋势判断逻辑
  - 添加了趋势分析说明和分析建议
  - 改进了空数据处理，显示友好的提示信息

### 技术改进
- **数据格式处理**：支持多种数据结构的指标数据
- **空数据处理**：友好的提示信息，避免空白显示
- **图表初始化**：完整的JavaScript图表配置
- **多Y轴支持**：支持不同量级的指标同时显示
- **趋势计算**：自动分析性能指标的变化趋势

## 自动数据收集和报告生成功能 (2024-12-19) - by Jaxon

### 重大功能更新
- **重构 main.py 为自动数据收集器**：
  - 用户运行 `uv run main.py` 时直接执行数据收集任务
  - 支持 Ctrl+C 中断并自动生成报告
  - 集成测试执行、指标收集和报告生成于一体
  - 提供美观的进度条和实时状态显示

### 新增功能
- **AutoDataCollector 类**：
  - 自动执行连接测试、发布测试、订阅测试
  - 支持华为云IoT平台测试（可选）
  - 实时收集Prometheus指标数据
  - 自动生成HTML格式的详细报告

- **智能配置管理**：
  - 支持加载现有配置文件
  - 提供快速配置调整选项
  - 默认配置适用于大多数场景
  - 配置文件：`emqtt_test_config.json`

- **优雅的中断处理**：
  - 支持 Ctrl+C 随时中断测试
  - 中断时自动清理进程和生成报告
  - 保存已完成的测试结果

### 报告生成
- **增强HTML报告特性**：
  - **多标签页界面**: 概览、测试详情、指标数据、数据分析四个标签页
  - **完整指标展示**: 显示所有收集到的指标数据，包括名称、值、类型、标签和说明
  - **交互式功能**: 搜索指标、按类型过滤、展开/折叠分类
  - **数据分析**: 性能指标分析、指标分类统计、关键指标高亮、测试对比
  - **现代化UI**: 美观的渐变背景、响应式设计、悬停效果
  - **详细统计**: 总体统计、成功率、耗时分析、指标分布
  - 美观的响应式设计
  - 详细的测试结果摘要
  - 指标数据统计表格
  - 测试成功/失败状态显示
  - 时间戳和持续时间记录

- **数据文件**：
  - JSON格式的指标数据文件
  - 按测试类型和时间戳命名
  - 包含完整的Prometheus指标信息

### 使用方法
```bash
# 进入metrics目录
cd metrics/

# 运行自动数据收集器
uv run main.py

# 测试功能是否正常
uv run test_auto_collector.py
```

### 技术改进
- 使用Rich库提供美观的控制台输出
- 集成信号处理确保优雅退出
- 支持多端口Prometheus指标收集
- 自动进程管理和清理
- 错误处理和异常恢复

## 文档和代码一致性修正 (2025-09-24) - by Jaxon

### 修正内容
- **添加了缺失的 `--device-id` 参数**：
  - 在代码中正式添加了 `--device-id` 选项定义
  - 支持在topic渲染中使用设备ID，默认使用username
  - 支持 `%i` 变量以便为不同客户端生成不同的设备ID
- **修正华为云认证密码格式描述**：
  - 统一文档中的密码格式为 `-P '设备密钥'`
  - 移除了过时的 `huawei:` 前缀描述
  - 代码已经支持 `--huawei-auth` 自动生成认证密码
- **修正MQTT协议版本默认值**：
  - 将README.md中的默认版本从5修正为3
  - 与实际代码中的默认值保持一致
  - 符合华为云IoT平台的要求（不支持MQTT v5）

### 文档更新
- 更新了 `README.md` 中的参数说明
- 修正了 `HUAWEI_ERLANG_AUTH_GUIDE.md` 中的示例
- 更新了 `HUAWEI_CLOUD_SUCCESS_GUIDE.md` 中的参数说明
- 确保所有文档与实际代码实现保持一致

## 配置优化：统一Host参数 (2024-12-19) - by Jaxon

### 重大改进
- **统一Host配置**：
  - 将 `mqtt_host` 和 `huawei_host` 合并为统一的 `host` 参数
  - 将 `mqtt_port` 和 `huawei_port` 合并为统一的 `port` 参数
  - 新增 `use_huawei_auth` 布尔标志来控制是否使用华为云认证
  - 简化了配置结构，提高了灵活性

### 配置变更
- **旧配置格式**：
  ```json
  {
    "mqtt_host": "localhost",
    "mqtt_port": 1883,
    "huawei_host": "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com",
    "huawei_port": 1883
  }
  ```
- **新配置格式**：
  ```json
  {
    "host": "localhost",
    "port": 1883,
    "use_huawei_auth": false
  }
  ```

### 功能优化
- **智能测试选择**：
  - 所有测试类型（连接、发布、订阅、自定义）现在都支持华为云认证
  - 通过 `use_huawei_auth` 标志自动切换认证模式
  - 移除了单独的"华为云测试"选项，简化了用户界面
- **动态参数配置**：
  - 华为云认证模式下自动使用华为云topic和payload模板
  - 标准模式下使用通用MQTT topic和参数
  - 根据认证模式自动调整测试参数

### 用户体验改进
- **更简洁的配置界面**：减少了重复的服务器配置项
- **更灵活的使用方式**：同一个配置可以测试不同的MQTT服务器
- **更清晰的逻辑**：通过认证标志明确区分测试模式

## Prometheus 监控和压测结果收集指南 (2024-12-19) - by Jaxon

### 脚本优化
- **优化 prometheus_example.sh 脚本**：
  - 直接内置华为云IoT平台配置参数，无需设置环境变量
  - 默认客户端数量调整为5个，适合快速测试
  - 华为云测试参数：服务器、设备前缀、密钥已预设
  - 使用华为云payload模板文件进行真实数据测试
  - **新增交互式菜单**：用户可选择运行特定测试类型
  - **新增自定义测试选项**：支持用户自定义客户端数量、消息间隔、持续时间等参数
  - **智能报告生成**：根据实际运行的测试生成相应的测试报告

### Python 指标收集工具
- **新增 metrics/ 目录**：
  - 完整的 Python 项目，使用 uv 进行依赖管理
  - `metrics_collector.py`: 主要的指标收集和分析工具
  - `example_usage.py`: 使用示例和演示代码
  - `quick_start.sh`: 快速开始脚本
  - 支持 JSON 和 CSV 格式数据导出
  - 实时监控和批量收集功能
  - 专门优化华为云 IoT 平台指标收集

### 新增文档
- **Prometheus 监控指南** (`PROMETHEUS_MONITORING_GUIDE.md`)：
  - 详细介绍如何配置和使用 Prometheus 监控功能
  - 包含完整的指标说明和配置示例
  - 提供 Grafana 仪表板配置建议
  - 涵盖华为云 IoT 平台监控场景
- **压测结果收集指南** (`BENCHMARK_RESULTS_COLLECTION.md`)：
  - 多种结果收集方式：控制台输出、QoE 监控、Prometheus 指标、日志文件
  - 华为云 IoT 平台测试结果收集脚本
  - 结果分析和报告生成工具
  - 最佳实践和故障排除指南
- **Prometheus 示例脚本** (`prometheus_example.sh`)：
  - 完整的 Prometheus 监控示例脚本
  - 支持连接、发布、订阅测试
  - 自动生成测试报告和指标收集
  - 支持华为云 IoT 平台测试

### 功能说明
- **Prometheus 指标收集**：
  - 连接统计：连接数、连接成功率、连接失败数
  - 消息统计：发布消息数、订阅消息数、消息吞吐量
  - 延迟统计：TCP握手延迟、MQTT握手延迟、连接延迟、订阅延迟
  - QoE指标：端到端质量体验指标
- **HTTP API 端点**：
  - 提供 `/metrics` 端点供 Prometheus 抓取
  - 支持自定义监听地址和端口
  - 输出标准的 Prometheus 文本格式
- **结果收集方式**：
  - 控制台实时统计输出
  - QoE 质量体验监控和日志记录
  - Prometheus 指标导出
  - 日志文件保存和分析

### 使用方法
```bash
# 启用 Prometheus 监控
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --prometheus --restapi 8080

# 启用 QoE 监控
./emqtt_bench pub -c 100 -I 1000 -t "test/topic" --qoe true --qoelog /tmp/qoe.log

# 运行完整示例
./prometheus_example.sh
```

## 随机值占位符增强 (2024-11-19) - by Jaxon

### 新功能
- **扩展随机值占位符支持**：
  - `%RAND_INT_100%`: 生成0-100的随机整数
  - `%RAND_INT_1000%`: 生成0-1000的随机整数  
  - `%RAND_INT_10000%`: 生成0-10000的随机整数
  - `%RAND_INT_100000%`: 生成0-100000的随机整数
  - `%RAND_BOOL%`: 生成true/false随机布尔值
  - `%RAND_SSID%`: 生成WiFi_XXXX格式的随机SSID
- **更新华为云payload模板**：
  - 使用新的随机值占位符替换固定值
  - 模拟真实设备数据变化

### Bug 修复
- **修复 %d 变量在华为云模式下的解析问题**：
  - 问题：Topic中出现 `undefined`，因为 `%d` 变量没有正确解析
  - 修复：在 `feed_var` 函数中添加华为云认证模式下的设备ID生成逻辑
- **修复 %RAND_BOOL% 占位符替换问题**：
  - 问题：`binary:replace` 函数默认只替换第一个匹配项，导致多个 `%RAND_BOOL%` 中只有第一个被替换
  - 修复：在 `maps:fold` 函数中添加 `[global]` 选项，确保所有占位符都被替换
- **修复设备ID生成中的递归调用问题**：
  - 问题：`get_huawei_device_id` 函数中调用 `feed_var` 导致递归调用
  - 修复：直接处理简单的变量替换，避免递归调用

## --prefix 参数支持华为云设备ID (2024-11-19) - by Jaxon

### 新功能
- **支持使用 --prefix 参数设置华为云设备ID前缀**：
  - 设备ID格式：`{prefix}-{9位数字}`（如：Speaker-000000001）
  - 优先级：`-u` 参数 > `--prefix` 参数 > 默认格式
  - 简化了华为云测试命令，无需复杂的 `-u` 模板
- **简化华为云认证密码格式**：
  - 去掉 `-P` 参数中的 `"huawei:"` 前缀
  - 通过 `--huawei-auth` 参数自动判断是否使用华为云认证
  - 新格式：`-P "12345678"` 而不是 `-P "huawei:12345678"`
  - 添加了 `--device-id` 参数支持，用于topic渲染中的设备ID

### Bug 修复
- **修复华为云认证时间戳问题**：
  - 问题：Erlang 模块使用 UTC 时间，而 Python 使用本地时间，导致时间戳不一致
  - 修复：将 `huawei_auth:get_timestamp/0` 改为使用 `calendar:local_time()`
- **修复 MQTT 协议版本问题**：
  - 问题：默认使用 MQTT v5，华为云不支持
  - 修复：将默认协议版本改为 MQTT v3.1.1
- **修复 Username 设置问题**：
  - 问题：`lists:keyreplace` 无法添加不存在的字段
  - 修复：使用 `lists:keystore` 来添加或替换 username 字段

## 华为云集成更新 (2024-11-18) - by Jaxon

### 新增功能

#### Device ID 参数支持
- Topic 新增 `%d` 变量支持，用于表示设备ID
- 添加 `--device-id` 命令行选项，可明确指定设备ID
- device_id 默认使用 username 的值，提供灵活性
- 支持在 device_id 中使用 `%i` 和 `%rand_N` 变量
- 新增文档 `DEVICE_ID_GUIDE.md` 详细说明使用方法

#### 华为云认证逻辑修正
- **重要修正**：华为云认证时，MQTT username 现在正确使用 device_id
- 当使用 `--huawei-auth` 时：
  - 如果指定了 `--device-id`，MQTT username 使用 device_id 的值
  - 如果未指定 `--device-id`，MQTT username 使用 `-u` 的值
  - 这确保符合华为云要求：username 必须是设备ID
- 新增文档 `HUAWEI_AUTH_CORRECTION.md` 说明认证机制

### 原有新增功能
- 添加华为云 IoT 平台设备属性上报支持
  - Topic 格式：`$oc/devices/{device_id}/sys/properties/report`
  - 支持复杂的 JSON 数组 payload 格式
- 新增 Python 辅助脚本
  - `huawei/payload_generator.py`：生成符合华为云格式的随机测试数据
  - `huawei/run_huawei_cloud_test.py`：简化华为云测试的包装脚本
- 新增配置文件
  - `huawei_cloud_topics.json`：华为云设备属性上报的 topics_payload 配置
  - `huawei_cloud_payload_template.json`：payload 模板文件
- 新增文档
  - `HUAWEI_CLOUD_TEST_GUIDE.md`：详细的华为云测试指南
  - `HUAWEI_ERLANG_AUTH_GUIDE.md`：Erlang 原生认证使用指南

### 改进
- 增强了对华为云设备认证机制的支持
- 提供了多种测试方法和场景示例
- **新增 Erlang 原生实现华为云认证**
  - 添加 `src/huawei_auth.erl` 模块
  - 支持 `--huawei-auth` 命令行选项
  - 密码支持 `huawei:<secret>` 格式，自动生成 HMAC-SHA256 加密密码
  - ClientID 自动生成符合华为云格式
  - 无需依赖 Python，提高性能和易用性

## 0.5.0

- Fix TCP connection crash when `SSLKEYLOGFILE` is set (for QUIC).
- Allow topic placeholder in `topic_spec.json`
- Add support for `%rand_N` placeholder for `pub` command. For example, `topic/%rand_1000` will result in a topic with random number in the rage of `[1, 1000]` as suffix.

## 0.4.34

* new tls1.3 opt for Key exchange alg: `-keyex-algs` 
* short opt `-s` is now for `--size` only, it was shared by `--shortids`
* update usages in README.md

## 0.4.33

* fix: prometheus metrics observation with qoe enabled 
* Add more histogram buckets 

## 0.4.32

* QoE: Fix csv dump, represent `invalid_elapsed` as `""` instead of `-1`
* TLS: support `--ciphers` and `--signature-algs`

## 0.4.31

* New `--ssl-version` to enforce TLS version and implies ssl is enabled.
* QoE logging now logs TCP handshake latency during TLS handshake ( emqtt 1.14.0).
* QoE logging now logs each publish msg' end to end latency if `--payload-hdrs=ts` is set by both subscriber and publisher. 
* Dump TLS secrets per connecion to SSLKEYLOGFILE specifed by envvar SSLKEYLOGFILE for TLS traffic decryption.  (TLS and QUIC)
* Now build release for arm64.
* Now build release for el7 with newer build image.

## 0.4.30

* Enhanced QoE trackings, add supports for commands `conn` and `pub`.
* Write QoE event logs to disklog for post processing with `--qoe true --qoelog logfile`
* Dump QoE disklog to csv file with combined opts `--qoe dump --qoelog logfile`
  
## 0.4.29

* Fix OOM issue.

## 0.4.28

* release: fix and re-enable no-quic build

## 0.4.27

* Add bench `cacertfile` option for completeness.

## 0.4.26

* Upgrade emqtt to 1.13.4 so initial CONNECT packet send failures will not cause client to shutdown/crash.

## 0.4.13

* Add `--retry-interval` option to `pub` command and use `0` as default value (0 means disable resend).

## 0.4.5

* Default value for `--inflight` option is changed from `0` (no back-pressure) to `1`.
  i.e. `max-inflight` is `1` by default for QoS 1 and 2 messages.

## 0.4.4

Main changes comparing to 0.4.0

* Release on otp 24.2.1
* Multiple source IP address support (to get around the 64K source port limit)
* Reports publisher overrun for QoS 1 (when the ack is received after the interval set by `--interval_of_msg` option)

## 0.4 (2019-07-29)

Use the new Erlang MQTT v5.0 client

## 0.3 (2016-01-29)

emqtt_bench_sub: support to subscribe multiple topics (#9)

## 0.2 (2015-10-08)

emqtt_bench_pub, emqtt_bench_sub scripts

## 0.1 (2015-04-23)

first public release



## [2025-09-23] - 连接测试数据分析器

### 新增
- 创建了专门的连接测试数据分析器 \`connection_test_analyzer.py\`
- 添加了 \`analyze_connection_tests.sh\` - 连接测试分析快速启动脚本
- 支持多文件Prometheus指标数据对比分析
- 自动生成专业的HTML报告，包含统计图表和详细分析
- 支持直方图数据解析和统计计算
- 生成多种可视化图表：成功率对比、性能趋势、错误分析、系统资源使用

### 功能特点
- 解析Prometheus文本格式指标数据
- 计算连接成功率、平均握手时间、平均连接时间等关键指标
- 生成丰富的可视化图表：柱状图、趋势图、错误分析图
- 创建响应式HTML报告，支持移动端查看
- 提供详细的性能分析和建议
- 支持命令行参数，可自定义输出目录

### 使用示例
\`\`\`bash
# 分析单个文件
python3 connection_test_analyzer.py metrics_connection_20250923_172051.txt

# 分析多个文件进行对比
python3 connection_test_analyzer.py metrics_connection_*.txt

# 使用快速启动脚本
./analyze_connection_tests.sh
\`\`\`


## [2025-09-23] - 用户自定义配置功能

### 新增
- 华为云配置参数改为用户输入方式，包括：
  - HUAWEI_HOST (华为云IoT服务器地址)
  - HUAWEI_PORT (华为云IoT端口)
  - DEVICE_PREFIX (设备前缀)
  - HUAWEI_SECRET (设备密钥)
- 添加了配置保存和加载功能
- 支持其他参数的用户自定义：客户端数量、消息间隔、Prometheus端口
- 配置确认功能，用户可以在开始测试前确认所有参数

### 改进
- 交互式配置界面，提供默认值选项
- 自动保存配置到 \`emqtt_bench_config.conf\` 文件
- 下次运行时自动检测并询问是否加载保存的配置
- 配置确认时支持重新配置或保存配置选项
- 更友好的用户界面和提示信息

### 使用方式
\`\`\`bash
# 首次运行 - 需要输入配置
./prometheus_example.sh

# 后续运行 - 自动加载保存的配置
./prometheus_example.sh
\`\`\`

### 配置文件格式
\`\`\`bash
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
\`\`\`

## [2024-12-19] - 进程管理和URL连接修复

### 新增
- **进程管理脚本** (`process_manager.sh`):
  - 自动进程注册和跟踪功能
  - 信号处理机制，支持Ctrl+C优雅退出
  - 端口清理功能，自动清理被占用的端口
  - 进程状态监控，实时显示进程和端口状态
  - 批量清理功能，一键清理所有相关进程
- **集成版Prometheus脚本** (`prometheus_example_with_process_manager.sh`):
  - 集成进程管理功能的安全版本
  - 支持Ctrl+C优雅退出，自动清理所有进程和端口
  - 进程监控和状态显示功能
  - 错误恢复和异常处理机制
- **URL连接修复**:
  - 修复了Python脚本中URL格式问题（"No connection adapters were found"错误）
  - 自动添加http://协议前缀
  - 支持localhost:port格式的URL输入

### 改进
- 增强错误处理和异常恢复能力
- 添加端口冲突检测和自动解决
- 优化进程清理策略：优雅终止 -> 等待退出 -> 强制终止
- 支持自定义清理函数注册
- 添加进程状态实时监控

### 工具
- 创建 `test_process_manager.sh` 用于测试进程管理功能
- 创建 `test_metrics_endpoint.py` 用于测试Prometheus端点连接
- 创建 `fixed_connection_analyzer.py` 修复URL格式问题的分析器
- 更新 `connection_test_analyzer.py` 支持URL输入

### 文档
- 创建 `PROCESS_MANAGEMENT_GUIDE.md` 详细说明进程管理功能
- 添加故障排除指南和最佳实践
- 提供CI/CD集成示例
- 包含自动化脚本示例

### 使用方法
```bash
# 使用进程管理器启动测试
./process_manager.sh start './emqtt_bench pub -c 1 -I 1000 -t test/topic --prometheus --restapi 9090' '发布测试' 30

# 查看进程状态
./process_manager.sh status

# 清理所有进程
./process_manager.sh cleanup

# 使用集成版脚本（推荐）
./prometheus_example_with_process_manager.sh

# 测试URL连接
python3 test_metrics_endpoint.py localhost:9090/metrics
```

## [2025-09-26] - 报告文件组织优化

### 重大改进
- **报告文件统一管理**: 将main.py生成的报告统一保存到`reports/`文件夹中
- **文件结构优化**: 所有HTML报告和指标文件都保存在专门的reports目录下
- **路径管理改进**: 自动创建reports目录，确保报告文件有序存放

### 技术实现
- **修改enhanced_report_generator.py**: 添加reports_dir参数支持，默认保存到reports文件夹
- **修改main.py**: 更新报告生成逻辑，指定报告保存路径为reports文件夹
- **指标文件管理**: 将指标JSON文件也保存到reports文件夹中
- **用户界面优化**: 在报告摘要中显示报告保存位置信息

### 文件结构变化
```
metrics/
├── reports/                    # 新增：报告文件目录
│   ├── enhanced_collection_report_*.html  # HTML报告
│   └── metrics_*.json         # 指标数据文件
├── main.py                    # 修改：支持reports目录
└── enhanced_report_generator.py # 修改：支持自定义保存路径
```

### 使用方法
```bash
# 运行main.py后，所有报告将自动保存到reports文件夹
cd metrics/
uv run main.py

# 查看生成的报告
ls reports/
```

## [2024-12-19] - 集成测试管理器

### 重大更新
- **完全集成**: 将 `mqtt-stress-tool.sh` 的所有功能集成到 Python 中
- **一键测试**: 用户只需要运行一个命令就能完成配置、测试、数据收集和报表生成
- **统一管理**: 所有功能统一在 `metrics/` 目录的 Python 项目中

### 新增核心文件
- **`metrics/emqtt_test_manager.py`**: 主测试管理器，集成所有功能
- **`metrics/main.py`**: 简化版启动器
- **`metrics/quick_test.sh`**: 一键启动脚本
- **`demo_integrated_tool.py`**: 功能演示脚本

### 功能特性
- **智能配置管理**: 
  - 交互式配置界面
  - 配置自动保存和加载
  - 支持华为云IoT平台参数配置
- **完整测试执行**:
  - 连接测试、发布测试、订阅测试
  - 华为云IoT平台专门测试
  - 自定义测试参数
  - 批量运行所有测试
- **自动进程管理**:
  - 自动进程跟踪和清理
  - 支持Ctrl+C优雅退出
  - 端口冲突检测和解决
- **实时数据收集**:
  - 自动收集Prometheus指标
  - 实时监控测试状态
  - 多端口并行收集
- **丰富报表生成**:
  - 自动生成HTML测试报告
  - 包含详细指标分析
  - 支持多测试结果对比

### 使用方法
```bash
# 方法一：一键启动（推荐）
cd metrics/
./quick_test.sh

# 方法二：使用 uv
uv run python emqtt_test_manager.py

# 方法三：使用 Python
python emqtt_test_manager.py
```

### 输出文件
- `metrics_connection_YYYYMMDD_HHMMSS.txt`: 连接测试指标
- `metrics_publish_YYYYMMDD_HHMMSS.txt`: 发布测试指标
- `metrics_subscribe_YYYYMMDD_HHMMSS.txt`: 订阅测试指标
- `metrics_huawei_publish_YYYYMMDD_HHMMSS.txt`: 华为云测试指标
- `emqtt_test_config.json`: 测试配置（自动保存）
- `test_report_YYYYMMDD_HHMMSS.html`: 详细HTML测试报告

### 技术改进
- **依赖管理**: 更新 `pyproject.toml`，添加 `psutil` 依赖
- **CLI接口**: 使用 `click` 和 `rich` 提供美观的命令行界面
- **错误处理**: 完善的异常处理和错误恢复机制
- **配置管理**: JSON格式配置文件，支持环境变量覆盖

### 用户体验提升
- **Rich界面**: 使用 Rich 库提供美观的终端界面
- **进度显示**: 实时显示测试进度和状态
- **交互式配置**: 友好的配置向导
- **一键操作**: 从配置到报表，一个命令完成所有操作
