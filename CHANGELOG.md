# emqtt-bench changelog

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

