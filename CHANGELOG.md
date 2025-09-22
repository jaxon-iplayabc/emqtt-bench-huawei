# emqtt-bench changelog

## --prefix 参数支持华为云设备ID (2024-11-19) - by Jaxon

### 新功能
- **支持使用 --prefix 参数设置华为云设备ID前缀**：
  - 设备ID格式：`{prefix}-{9位数字}`（如：Speaker-000000001）
  - 优先级：`-u` 参数 > `--prefix` 参数 > 默认格式
  - 简化了华为云测试命令，无需复杂的 `-u` 模板

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

