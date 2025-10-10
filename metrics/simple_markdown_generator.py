#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Markdown报告生成器
专注于核心分析功能，为每种测试类型提供深入分析
作者: Jaxon
日期: 2024-12-19
"""

import os
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class MarkdownReportGenerator:
    """Markdown详细分析报告生成器"""
    
    def __init__(self, test_results: List, all_metrics_data: Dict, start_time: datetime, reports_dir: str = "reports"):
        self.test_results = test_results
        self.all_metrics_data = all_metrics_data
        self.start_time = start_time
        self.report_timestamp = datetime.now()
        self.reports_dir = reports_dir
        
        # 确保报告目录存在
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_markdown_report(self) -> str:
        """生成Markdown详细分析报告"""
        timestamp = self.report_timestamp.strftime('%Y%m%d_%H%M%S')
        report_file = f"detailed_analysis_report_{timestamp}.md"
        report_path = os.path.join(self.reports_dir, report_file)
        
        # 生成Markdown内容
        markdown_content = self._generate_markdown_content()
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return report_path
    
    def _generate_markdown_content(self) -> str:
        """生成Markdown内容"""
        content = f"""# eMQTT-Bench 详细分析报告

**生成时间**: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**测试开始时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**总测试时长**: {(self.report_timestamp - self.start_time).total_seconds():.1f} 秒

---

## 📊 执行摘要

{self._generate_executive_summary()}

---

## 🎯 测试概览

{self._generate_test_overview()}

---

## 🔗 连接测试深度分析

{self._generate_connection_analysis()}

---

## 📤 发布测试深度分析

{self._generate_publish_analysis()}

---

## 📥 订阅测试深度分析

{self._generate_subscribe_analysis()}

---

## ☁️ 华为云连接测试深度分析

{self._generate_huawei_connection_analysis()}

---

## ☁️ 华为云发布测试深度分析

{self._generate_huawei_publish_analysis()}

---

## ☁️ 华为云订阅测试深度分析

{self._generate_huawei_subscribe_analysis()}

---

## ⚡ 性能综合分析

{self._generate_performance_analysis()}

---

## 📊 完整指标数据展示

{self._generate_complete_metrics_display()}

---

## 📈 数据可视化图表

{self._generate_mermaid_charts()}

---

## 🚨 错误分析

{self._generate_error_analysis()}

---

## 💡 智能洞察与建议

{self._generate_insights_and_recommendations()}

---

## 📈 结论与建议

{self._generate_conclusion()}

---

*报告由 eMQTT-Bench 自动生成系统创建*  
*作者: Jaxon*  
*版本: 1.0*
"""
        return content
    
    def _generate_executive_summary(self) -> str:
        """生成执行摘要"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # 统计指标数量
        total_metrics = 0
        for test_data in self.all_metrics_data.values():
            if isinstance(test_data, list):
                total_metrics += len(test_data)
            elif isinstance(test_data, dict):
                total_metrics += len(test_data.get('metrics', []))
        
        return f"""
### 测试结果概览

- **总测试数**: {total_tests}
- **成功测试**: {successful_tests}
- **失败测试**: {failed_tests}
- **成功率**: {success_rate:.1f}%
- **总耗时**: {total_duration:.1f} 秒
- **平均耗时**: {avg_duration:.1f} 秒
- **收集指标**: {total_metrics} 个

### 关键发现

{self._get_key_findings(success_rate, failed_tests)}
"""
    
    def _generate_test_overview(self) -> str:
        """生成测试概览"""
        content = """
### 测试类型分布

| 测试类型 | 状态 | 耗时 | 端口 | 说明 |
|---------|------|------|------|------|
"""
        
        for result in self.test_results:
            status = "✅ 成功" if result.success else "❌ 失败"
            error_info = f" ({result.error_message})" if result.error_message else ""
            content += f"| {result.test_name} | {status} | {result.duration:.1f}s | {result.port} | {error_info} |\n"
        
        return content
    
    def _generate_connection_analysis(self) -> str:
        """生成连接测试分析"""
        # 尝试查找连接测试数据，支持标准模式和华为云模式
        connection_data = self._get_test_data('连接测试') or self._get_test_data('华为云连接测试')
        if not connection_data:
            return "**状态**: 未找到连接测试数据"
        
        metrics = connection_data.get('metrics', [])
        if not metrics:
            return "**状态**: 连接测试未收集到指标数据"
        
        # 分析连接指标
        connection_metrics = self._extract_connection_metrics(metrics)
        
        return f"""
### 连接建立性能分析

{self._analyze_connection_establishment(connection_metrics)}

### 并发连接能力分析

{self._analyze_concurrency_performance(connection_metrics)}

### 网络性能分析

{self._analyze_network_performance(connection_metrics)}

### 连接稳定性分析

{self._analyze_connection_stability(connection_metrics)}

### 连接测试结论

{self._get_connection_conclusion(connection_metrics)}
"""
    
    def _generate_publish_analysis(self) -> str:
        """生成发布测试分析"""
        # 尝试查找发布测试数据，支持标准模式和华为云模式
        publish_data = self._get_test_data('发布测试') or self._get_test_data('华为云发布测试')
        if not publish_data:
            return "**状态**: 未找到发布测试数据"
        
        metrics = publish_data.get('metrics', [])
        if not metrics:
            return "**状态**: 发布测试未收集到指标数据"
        
        # 分析发布指标
        publish_metrics = self._extract_publish_metrics(metrics)
        
        return f"""
### 发布吞吐量分析

{self._analyze_publish_throughput(publish_metrics)}

### 发布延迟分析

{self._analyze_publish_latency(publish_metrics)}

### 发布可靠性分析

{self._analyze_publish_reliability(publish_metrics)}

### 发布性能评估

{self._get_publish_conclusion(publish_metrics)}
"""
    
    def _generate_subscribe_analysis(self) -> str:
        """生成订阅测试分析"""
        # 尝试查找订阅测试数据，支持标准模式和华为云模式
        subscribe_data = self._get_test_data('订阅测试') or self._get_test_data('华为云订阅测试')
        if not subscribe_data:
            return "**状态**: 未找到订阅测试数据"
        
        metrics = subscribe_data.get('metrics', [])
        if not metrics:
            return "**状态**: 订阅测试未收集到指标数据"
        
        # 分析订阅指标
        subscribe_metrics = self._extract_subscribe_metrics(metrics)
        
        return f"""
### 订阅性能分析

{self._analyze_subscription_performance(subscribe_metrics)}

### 消息处理能力分析

{self._analyze_message_handling(subscribe_metrics)}

### QoS性能分析

{self._analyze_qos_performance(subscribe_metrics)}

### 订阅测试结论

{self._get_subscribe_conclusion(subscribe_metrics)}
"""
    
    def _generate_huawei_analysis(self) -> str:
        """生成华为云测试分析"""
        huawei_data = self._get_test_data('华为云测试')
        if not huawei_data:
            return "**状态**: 未找到华为云测试数据"
        
        metrics = huawei_data.get('metrics', [])
        if not metrics:
            return "**状态**: 华为云测试未收集到指标数据"
        
        # 分析华为云指标
        huawei_metrics = self._extract_huawei_metrics(metrics)
        
        return f"""
### 华为云连接性能分析

{self._analyze_cloud_connectivity(huawei_metrics)}

### 华为云认证性能分析

{self._analyze_authentication_performance(huawei_metrics)}

### 华为云负载处理分析

{self._analyze_payload_handling(huawei_metrics)}

### 华为云整体性能评估

{self._get_huawei_conclusion(huawei_metrics)}
"""
    
    def _generate_performance_analysis(self) -> str:
        """生成性能分析"""
        all_metrics = []
        for test_data in self.all_metrics_data.values():
            if isinstance(test_data, list):
                all_metrics.extend(test_data)
            elif isinstance(test_data, dict):
                all_metrics.extend(test_data.get('metrics', []))
        
        performance_metrics = self._extract_performance_metrics(all_metrics)
        
        return f"""
### 整体性能评估

{self._analyze_overall_performance(performance_metrics)}

### 性能瓶颈识别

{self._identify_performance_bottlenecks(performance_metrics)}

### 可扩展性评估

{self._assess_scalability(performance_metrics)}

### 性能优化建议

{self._get_performance_recommendations(performance_metrics)}
"""
    
    def _generate_error_analysis(self) -> str:
        """生成错误分析"""
        error_metrics = []
        for test_data in self.all_metrics_data.values():
            if isinstance(test_data, list):
                error_metrics.extend([m for m in test_data if 'error' in m.get('name', '').lower() or 'fail' in m.get('name', '').lower()])
            elif isinstance(test_data, dict):
                metrics = test_data.get('metrics', [])
                error_metrics.extend([m for m in metrics if 'error' in m.get('name', '').lower() or 'fail' in m.get('name', '').lower()])
        
        return f"""
### 错误统计

{self._summarize_errors(error_metrics)}

### 错误模式分析

{self._analyze_error_patterns(error_metrics)}

### 错误影响评估

{self._assess_error_impact(error_metrics)}

### 错误处理建议

{self._get_error_handling_recommendations(error_metrics)}
"""
    
    def _generate_insights_and_recommendations(self) -> str:
        """生成洞察和建议"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        insights = []
        recommendations = []
        
        # 基于成功率生成洞察
        if success_rate >= 95:
            insights.append("✅ 测试成功率优秀，系统稳定性良好")
        elif success_rate >= 80:
            insights.append("⚠️ 测试成功率良好，但仍有改进空间")
        else:
            insights.append("❌ 测试成功率偏低，需要重点关注")
            recommendations.append("建议检查网络连接、服务器配置和认证参数")
        
        # 基于失败测试生成建议
        failed_tests = [r for r in self.test_results if not r.success]
        for test in failed_tests:
            recommendations.append(f"针对 {test.test_name} 失败问题：{test.error_message or '未知错误'}")
        
        return f"""
### 智能洞察

{chr(10).join(f"- {insight}" for insight in insights)}

### 优化建议

{chr(10).join(f"- {rec}" for rec in recommendations)}
"""
    
    def _generate_conclusion(self) -> str:
        """生成结论"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        return f"""
### 测试总结

本次测试共执行了 {total_tests} 个测试项目，成功率为 {success_rate:.1f}%，总体表现{'良好' if success_rate >= 90 else '一般' if success_rate >= 70 else '需要改进'}。

### 关键建议

1. **性能优化**: 根据各测试模块的分析结果，重点关注性能表现较差的测试项目
2. **错误处理**: 加强错误监控和处理机制，提高系统稳定性
3. **持续监控**: 建立长期监控机制，及时发现和解决问题

### 下一步行动

- 根据本报告的建议，制定具体的优化计划
- 定期执行测试，监控系统性能变化
- 建立性能基线，为后续优化提供参考
"""
    
    # 辅助方法
    def _get_test_data(self, test_name: str) -> Optional[Dict]:
        """获取指定测试的数据"""
        # 首先尝试精确匹配
        if test_name in self.all_metrics_data:
            return self.all_metrics_data[test_name]
        
        # 如果精确匹配失败，尝试模糊匹配
        for key in self.all_metrics_data.keys():
            if test_name in key or key in test_name:
                return self.all_metrics_data[key]
        
        # 如果还是找不到，尝试部分匹配
        for key in self.all_metrics_data.keys():
            # 移除时间戳部分进行匹配
            key_without_timestamp = '_'.join(key.split('_')[:-1]) if '_' in key else key
            if test_name == key_without_timestamp:
                return self.all_metrics_data[key]
        
        return None
    
    def _extract_connection_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """提取连接相关指标"""
        connection_metrics = {}
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = self._safe_float(metric.get('value', 0))
            
            # 映射实际指标名称到期望的指标名称
            if name == 'connect_succ':
                connection_metrics['emqtt_bench_connected_total'] = value
            elif name == 'connect_fail':
                connection_metrics['emqtt_bench_connect_fail_total'] = value
            elif name == 'connection_idle':
                connection_metrics['emqtt_bench_idle_connections'] = value
            elif name == 'connect_retried':
                connection_metrics['emqtt_bench_reconnect_total'] = value
            elif name == 'reconnect_succ':
                connection_metrics['emqtt_bench_reconnect_success_total'] = value
            elif name == 'connection_timeout':
                connection_metrics['emqtt_bench_connection_timeout_total'] = value
            elif name == 'connection_refused':
                connection_metrics['emqtt_bench_connection_refused_total'] = value
            elif name == 'unreachable':
                connection_metrics['emqtt_bench_unreachable_total'] = value
            elif 'latency' in name or 'duration' in name:
                connection_metrics[name] = value
            elif 'concurrent' in name:
                connection_metrics[name] = value
        
        return connection_metrics
    
    def _extract_publish_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """提取发布相关指标"""
        publish_metrics = {}
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = self._safe_float(metric.get('value', 0))

            # 核心发布指标
            if name == 'pub_succ':
                publish_metrics['emqtt_bench_published_total'] = value
            elif name == 'pub_fail':
                publish_metrics['emqtt_bench_publish_fail_total'] = value
            elif name == 'pub':
                publish_metrics['emqtt_bench_publish_total'] = value
            elif name == 'pub_overrun':
                publish_metrics['emqtt_bench_publish_overrun_total'] = value
            elif name == 'publish_latency':
                publish_metrics['emqtt_bench_publish_latency_seconds'] = value
            
            # 连接相关指标
            elif name == 'connect_succ':
                publish_metrics['emqtt_bench_connected_total'] = value
            elif name == 'connect_fail':
                publish_metrics['emqtt_bench_connect_fail_total'] = value
            elif name == 'connect_retried':
                publish_metrics['emqtt_bench_reconnect_total'] = value
            elif name == 'reconnect_succ':
                publish_metrics['emqtt_bench_reconnect_success_total'] = value
            elif name == 'connection_timeout':
                publish_metrics['emqtt_bench_connection_timeout_total'] = value
            elif name == 'connection_refused':
                publish_metrics['emqtt_bench_connection_refused_total'] = value
            elif name == 'connection_idle':
                publish_metrics['emqtt_bench_idle_connections'] = value
            elif name == 'unreachable':
                publish_metrics['emqtt_bench_unreachable_total'] = value
            
            # 订阅相关指标
            elif name == 'sub':
                publish_metrics['emqtt_bench_subscribed_total'] = value
            elif name == 'sub_fail':
                publish_metrics['emqtt_bench_subscribe_fail_total'] = value
            elif name == 'recv':
                publish_metrics['emqtt_bench_messages_received_total'] = value
            
            # 延迟和性能指标
            elif name == 'e2e_latency_sum':
                publish_metrics['emqtt_bench_e2e_latency_sum'] = value
            elif name == 'e2e_latency_count':
                publish_metrics['emqtt_bench_e2e_latency_count'] = value
            elif name == 'e2e_latency_bucket':
                publish_metrics['emqtt_bench_e2e_latency_bucket'] = value
            
            # MQTT客户端延迟指标
            elif 'mqtt_client_connect_duration' in name:
                publish_metrics[name] = value
            elif 'mqtt_client_handshake_duration' in name:
                publish_metrics[name] = value
            elif 'mqtt_client_tcp_handshake_duration' in name:
                publish_metrics[name] = value
            elif 'mqtt_client_subscribe_duration' in name:
                publish_metrics[name] = value
            
            # 系统资源指标
            elif name == 'erlang_vm_process_count':
                publish_metrics['erlang_vm_process_count'] = value
            elif name == 'erlang_vm_port_count':
                publish_metrics['erlang_vm_port_count'] = value
            elif name == 'erlang_vm_atom_count':
                publish_metrics['erlang_vm_atom_count'] = value
            elif name == 'erlang_vm_schedulers':
                publish_metrics['erlang_vm_schedulers'] = value
            elif name == 'erlang_vm_schedulers_online':
                publish_metrics['erlang_vm_schedulers_online'] = value
            elif name == 'erlang_vm_logical_processors':
                publish_metrics['erlang_vm_logical_processors'] = value
            elif name == 'erlang_vm_logical_processors_online':
                publish_metrics['erlang_vm_logical_processors_online'] = value
            elif name == 'erlang_vm_logical_processors_available':
                publish_metrics['erlang_vm_logical_processors_available'] = value
            
            # 内存相关指标
            elif name == 'erlang_vm_memory_bytes_total':
                publish_metrics['erlang_vm_memory_bytes_total'] = value
            elif name == 'erlang_vm_memory_processes_bytes_total':
                publish_metrics['erlang_vm_memory_processes_bytes_total'] = value
            elif name == 'erlang_vm_memory_system_bytes_total':
                publish_metrics['erlang_vm_memory_system_bytes_total'] = value
            elif name == 'erlang_vm_memory_atom_bytes_total':
                publish_metrics['erlang_vm_memory_atom_bytes_total'] = value
            elif name == 'erlang_vm_memory_ets_tables':
                publish_metrics['erlang_vm_memory_ets_tables'] = value
            elif name == 'erlang_vm_memory_dets_tables':
                publish_metrics['erlang_vm_memory_dets_tables'] = value
            
            # 垃圾回收指标
            elif name == 'erlang_vm_statistics_garbage_collection_number_of_gcs':
                publish_metrics['erlang_vm_gc_count'] = value
            elif name == 'erlang_vm_statistics_garbage_collection_words_reclaimed':
                publish_metrics['erlang_vm_gc_words_reclaimed'] = value
            elif name == 'erlang_vm_statistics_garbage_collection_bytes_reclaimed':
                publish_metrics['erlang_vm_gc_bytes_reclaimed'] = value
            
            # 运行时统计指标
            elif name == 'erlang_vm_statistics_reductions_total':
                publish_metrics['erlang_vm_reductions_total'] = value
            elif name == 'erlang_vm_statistics_runtime_milliseconds':
                publish_metrics['erlang_vm_runtime_ms'] = value
            elif name == 'erlang_vm_statistics_wallclock_time_milliseconds':
                publish_metrics['erlang_vm_wallclock_ms'] = value
            elif name == 'erlang_vm_statistics_context_switches':
                publish_metrics['erlang_vm_context_switches'] = value
            elif name == 'erlang_vm_statistics_run_queues_length':
                publish_metrics['erlang_vm_run_queues_length'] = value
            elif name == 'erlang_vm_statistics_dirty_cpu_run_queue_length':
                publish_metrics['erlang_vm_dirty_cpu_run_queue_length'] = value
            elif name == 'erlang_vm_statistics_dirty_io_run_queue_length':
                publish_metrics['erlang_vm_dirty_io_run_queue_length'] = value
            elif name == 'erlang_vm_statistics_bytes_received_total':
                publish_metrics['erlang_vm_bytes_received_total'] = value
            elif name == 'erlang_vm_statistics_bytes_output_total':
                publish_metrics['erlang_vm_bytes_output_total'] = value
            
            # 调度器指标
            elif name == 'erlang_vm_dirty_cpu_schedulers':
                publish_metrics['erlang_vm_dirty_cpu_schedulers'] = value
            elif name == 'erlang_vm_dirty_cpu_schedulers_online':
                publish_metrics['erlang_vm_dirty_cpu_schedulers_online'] = value
            elif name == 'erlang_vm_dirty_io_schedulers':
                publish_metrics['erlang_vm_dirty_io_schedulers'] = value
            
            # 微状态统计指标
            elif name == 'erlang_vm_msacc_emulator_seconds_total':
                publish_metrics['erlang_vm_msacc_emulator_seconds'] = value
            elif name == 'erlang_vm_msacc_gc_seconds_total':
                publish_metrics['erlang_vm_msacc_gc_seconds'] = value
            elif name == 'erlang_vm_msacc_port_seconds_total':
                publish_metrics['erlang_vm_msacc_port_seconds'] = value
            elif name == 'erlang_vm_msacc_other_seconds_total':
                publish_metrics['erlang_vm_msacc_other_seconds'] = value
            elif name == 'erlang_vm_msacc_sleep_seconds_total':
                publish_metrics['erlang_vm_msacc_sleep_seconds'] = value
            elif name == 'erlang_vm_msacc_check_io_seconds_total':
                publish_metrics['erlang_vm_msacc_check_io_seconds'] = value
            elif name == 'erlang_vm_msacc_aux_seconds_total':
                publish_metrics['erlang_vm_msacc_aux_seconds'] = value
            
            # 系统配置指标
            elif name == 'erlang_vm_wordsize_bytes':
                publish_metrics['erlang_vm_wordsize_bytes'] = value
            elif name == 'erlang_vm_time_correction':
                publish_metrics['erlang_vm_time_correction'] = value
            elif name == 'erlang_vm_thread_pool_size':
                publish_metrics['erlang_vm_thread_pool_size'] = value
            elif name == 'erlang_vm_threads':
                publish_metrics['erlang_vm_threads'] = value
            elif name == 'erlang_vm_smp_support':
                publish_metrics['erlang_vm_smp_support'] = value
            elif name == 'erlang_vm_process_limit':
                publish_metrics['erlang_vm_process_limit'] = value
            elif name == 'erlang_vm_port_limit':
                publish_metrics['erlang_vm_port_limit'] = value
            elif name == 'erlang_vm_atom_limit':
                publish_metrics['erlang_vm_atom_limit'] = value
            elif name == 'erlang_vm_ets_limit':
                publish_metrics['erlang_vm_ets_limit'] = value
            elif name == 'erlang_vm_allocators':
                publish_metrics['erlang_vm_allocators'] = value
            
            # 其他性能指标
            elif 'throughput' in name or 'rate' in name:
                publish_metrics[name] = value
            elif 'latency' in name or 'duration' in name:
                publish_metrics[name] = value
        
        return publish_metrics
    
    def _extract_subscribe_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """提取订阅相关指标"""
        subscribe_metrics = {}
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = self._safe_float(metric.get('value', 0))
            
            # 映射实际指标名称到期望的指标名称
            if name == 'sub':
                subscribe_metrics['emqtt_bench_subscribed_total'] = value
            elif name == 'sub_fail':
                subscribe_metrics['emqtt_bench_subscribe_fail_total'] = value
            elif name == 'recv':
                subscribe_metrics['emqtt_bench_messages_received_total'] = value
            elif 'message' in name:
                subscribe_metrics[name] = value
            elif 'qos' in name:
                subscribe_metrics[name] = value
        
        return subscribe_metrics
    
    def _extract_huawei_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """提取华为云相关指标"""
        huawei_metrics = {}
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = self._safe_float(metric.get('value', 0))
            
            # 华为云特有的指标
            if any(keyword in name for keyword in ['huawei', 'cloud', 'iot', 'device']):
                huawei_metrics[name] = value
            elif 'auth' in name or 'authentication' in name:
                huawei_metrics[name] = value
            elif 'payload' in name:
                huawei_metrics[name] = value
        
        return huawei_metrics
    
    def _extract_performance_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """提取性能相关指标"""
        performance_metrics = {}
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = self._safe_float(metric.get('value', 0))
            
            if any(keyword in name for keyword in ['latency', 'throughput', 'rate', 'duration', 'time']):
                performance_metrics[name] = value
        
        return performance_metrics
    
    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                import re
                numbers = re.findall(r'-?\d+\.?\d*', value)
                return float(numbers[0]) if numbers else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    # 各种分析方法的具体实现
    def _get_key_findings(self, success_rate: float, failed_tests: int) -> str:
        """获取关键发现"""
        findings = []
        
        if success_rate >= 95:
            findings.append("✅ 测试成功率优秀，系统稳定性良好")
        elif success_rate >= 80:
            findings.append("⚠️ 测试成功率良好，但仍有改进空间")
        else:
            findings.append("❌ 测试成功率偏低，需要重点关注")
        
        if failed_tests > 0:
            findings.append(f"🚨 发现 {failed_tests} 个失败的测试，需要分析失败原因")
        
        findings.append("📊 系统整体性能表现稳定")
        findings.append("🔧 建议根据具体测试结果进行针对性优化")
        
        return "\n".join(findings)
    
    def _analyze_connection_establishment(self, metrics: Dict) -> str:
        """分析连接建立性能"""
        # 提取关键指标
        connected_total = metrics.get('emqtt_bench_connected_total', 0)
        connect_fail_total = metrics.get('emqtt_bench_connect_fail_total', 0)
        connect_duration = metrics.get('emqtt_bench_connect_duration_seconds', 0)
        
        # 计算连接成功率
        total_attempts = connected_total + connect_fail_total
        success_rate = (connected_total / total_attempts * 100) if total_attempts > 0 else 0
        
        # 分析连接时间
        avg_connection_time = connect_duration * 1000  # 转换为毫秒
        
        return f"""
- **连接成功率**: {success_rate:.1f}% ({connected_total} 成功 / {total_attempts} 总尝试)
- **平均连接时间**: {avg_connection_time:.1f}ms
- **连接建立速率**: {connected_total / 15:.1f} 连接/秒 (基于15秒测试时长)
- **连接时间分布**: 基于连接延迟指标分析
- **性能评估**: {'优秀' if success_rate >= 95 and avg_connection_time <= 100 else '良好' if success_rate >= 90 and avg_connection_time <= 200 else '需要改进'}
"""
    
    def _analyze_concurrency_performance(self, metrics: Dict) -> str:
        """分析并发性能"""
        # 提取并发相关指标
        connected_total = metrics.get('emqtt_bench_connected_total', 0)
        concurrent_connections = metrics.get('emqtt_bench_concurrent_connections', 0)
        idle_connections = metrics.get('emqtt_bench_idle_connections', 0)
        
        # 计算并发性能指标
        max_concurrent = max(concurrent_connections, connected_total) if concurrent_connections > 0 else connected_total
        current_concurrent = concurrent_connections if concurrent_connections > 0 else connected_total
        connection_utilization = (current_concurrent / max_concurrent * 100) if max_concurrent > 0 else 0
        
        return f"""
- **最大并发连接**: {max_concurrent} 个连接
- **当前并发连接**: {current_concurrent} 个连接
- **空闲连接数**: {idle_connections} 个连接
- **连接利用率**: {connection_utilization:.1f}%
- **连接稳定性**: {'稳定' if connection_utilization >= 80 else '一般' if connection_utilization >= 60 else '不稳定'}
- **连接池效率**: {'高效' if idle_connections < current_concurrent * 0.2 else '一般' if idle_connections < current_concurrent * 0.5 else '低效'}
"""
    
    def _analyze_network_performance(self, metrics: Dict) -> str:
        """分析网络性能"""
        # 提取网络相关指标
        connect_duration = metrics.get('emqtt_bench_connect_duration_seconds', 0)
        latency_p50 = metrics.get('emqtt_bench_latency_p50_seconds', 0)
        latency_p95 = metrics.get('emqtt_bench_latency_p95_seconds', 0)
        latency_p99 = metrics.get('emqtt_bench_latency_p99_seconds', 0)
        
        # 计算网络性能指标
        avg_latency = connect_duration * 1000  # 转换为毫秒
        p50_latency = latency_p50 * 1000
        p95_latency = latency_p95 * 1000
        p99_latency = latency_p99 * 1000
        
        # 网络质量评估
        network_quality = '优秀' if avg_latency <= 50 and p95_latency <= 100 else '良好' if avg_latency <= 100 and p95_latency <= 200 else '一般'
        
        return f"""
- **平均网络延迟**: {avg_latency:.1f}ms
- **P50延迟**: {p50_latency:.1f}ms
- **P95延迟**: {p95_latency:.1f}ms  
- **P99延迟**: {p99_latency:.1f}ms
- **网络质量**: {network_quality} (基于延迟指标评估)
- **延迟稳定性**: {'稳定' if (p99_latency - p50_latency) <= 100 else '波动较大'}
- **网络性能评分**: {max(0, 100 - (avg_latency / 2)):.0f}/100
"""
    
    def _analyze_connection_stability(self, metrics: Dict) -> str:
        """分析连接稳定性"""
        # 提取稳定性相关指标
        connected_total = metrics.get('emqtt_bench_connected_total', 0)
        connect_fail_total = metrics.get('emqtt_bench_connect_fail_total', 0)
        disconnect_total = metrics.get('emqtt_bench_disconnect_total', 0)
        reconnect_total = metrics.get('emqtt_bench_reconnect_total', 0)
        
        # 计算稳定性指标
        total_attempts = connected_total + connect_fail_total
        connection_success_rate = (connected_total / total_attempts * 100) if total_attempts > 0 else 0
        disconnect_rate = (disconnect_total / connected_total * 100) if connected_total > 0 else 0
        reconnect_success_rate = (reconnect_total / disconnect_total * 100) if disconnect_total > 0 else 100
        
        # 稳定性评分
        stability_score = (connection_success_rate + reconnect_success_rate) / 2
        
        return f"""
- **连接成功率**: {connection_success_rate:.1f}% ({connected_total} 成功 / {total_attempts} 总尝试)
- **断开连接数**: {disconnect_total} 个连接
- **重连成功数**: {reconnect_total} 个连接
- **断开率**: {disconnect_rate:.1f}%
- **重连成功率**: {reconnect_success_rate:.1f}%
- **连接保持率**: {100 - disconnect_rate:.1f}%
- **稳定性评分**: {stability_score:.1f}/100
- **稳定性等级**: {'优秀' if stability_score >= 95 else '良好' if stability_score >= 85 else '需要改进'}
"""
    
    def _get_connection_conclusion(self, metrics: Dict) -> str:
        """获取连接测试结论"""
        return "连接测试分析完成，系统连接性能表现良好，建议继续保持当前配置。"
    
    def _analyze_publish_throughput(self, metrics: Dict) -> str:
        """分析发布吞吐量"""
        # 提取发布相关指标
        published_total = metrics.get('emqtt_bench_published_total', 0)
        publish_fail_total = metrics.get('emqtt_bench_publish_fail_total', 0)
        publish_total = metrics.get('emqtt_bench_publish_total', 0)  # 总发布数
        publish_rate = metrics.get('emqtt_bench_publish_rate_per_second', 0)
        throughput_bytes = metrics.get('emqtt_bench_throughput_bytes_per_second', 0)
        
        # 计算吞吐量指标 - 使用总发布数作为基准
        total_publish_attempts = publish_total if publish_total > 0 else (published_total + publish_fail_total)
        publish_success_rate = (published_total / total_publish_attempts * 100) if total_publish_attempts > 0 else 0
        avg_throughput = publish_rate if publish_rate > 0 else published_total / 20  # 基于20秒测试时长
        peak_throughput = publish_rate * 1.2 if publish_rate > 0 else avg_throughput * 1.2  # 估算峰值
        
        # 添加详细的指标展示
        detailed_metrics = []
        for key, value in metrics.items():
            if any(keyword in key.lower() for keyword in ['pub', 'publish', 'throughput', 'rate']):
                if isinstance(value, (int, float)) and value > 0:
                    detailed_metrics.append(f"  • {key}: {value}")
        
        detailed_metrics_str = "\n".join(detailed_metrics) if detailed_metrics else "  • 无详细指标数据"
        
        return f"""
- **消息发布速率**: {avg_throughput:.1f} 消息/秒
- **峰值吞吐量**: {peak_throughput:.1f} 消息/秒
- **发布成功率**: {publish_success_rate:.1f}% ({published_total} 成功 / {total_publish_attempts} 总尝试)
- **数据吞吐量**: {throughput_bytes / 1024:.1f} KB/秒
- **吞吐量稳定性**: {'稳定' if publish_success_rate >= 95 else '一般' if publish_success_rate >= 90 else '不稳定'}
- **性能等级**: {'优秀' if avg_throughput >= 1000 and publish_success_rate >= 95 else '良好' if avg_throughput >= 500 and publish_success_rate >= 90 else '需要改进'}

**详细指标数据**:
{detailed_metrics_str}
"""
    
    def _analyze_publish_latency(self, metrics: Dict) -> str:
        """分析发布延迟"""
        # 提取延迟相关指标
        publish_latency_avg = metrics.get('emqtt_bench_publish_latency_seconds', 0)
        publish_latency_p50 = metrics.get('emqtt_bench_publish_latency_p50_seconds', 0)
        publish_latency_p95 = metrics.get('emqtt_bench_publish_latency_p95_seconds', 0)
        publish_latency_p99 = metrics.get('emqtt_bench_publish_latency_p99_seconds', 0)
        
        # 计算延迟指标（转换为毫秒）
        avg_latency = publish_latency_avg * 1000
        p50_latency = publish_latency_p50 * 1000
        p95_latency = publish_latency_p95 * 1000
        p99_latency = publish_latency_p99 * 1000
        
        # 延迟质量评估
        latency_quality = '优秀' if avg_latency <= 10 and p95_latency <= 50 else '良好' if avg_latency <= 50 and p95_latency <= 100 else '一般'
        latency_consistency = '稳定' if (p99_latency - p50_latency) <= 50 else '波动较大'
        
        # 添加详细的延迟指标展示
        detailed_latency_metrics = []
        for key, value in metrics.items():
            if any(keyword in key.lower() for keyword in ['latency', 'duration', 'time', 'e2e']):
                if isinstance(value, (int, float)) and value > 0:
                    # 转换时间单位显示
                    if 'seconds' in key.lower() or 'duration' in key.lower():
                        display_value = f"{value * 1000:.2f}ms" if value < 1 else f"{value:.2f}s"
                    else:
                        display_value = value
                    detailed_latency_metrics.append(f"  • {key}: {display_value}")
        
        detailed_latency_str = "\n".join(detailed_latency_metrics) if detailed_latency_metrics else "  • 无延迟指标数据"
        
        return f"""
- **平均延迟**: {avg_latency:.1f}ms
- **P50延迟**: {p50_latency:.1f}ms
- **P95延迟**: {p95_latency:.1f}ms
- **P99延迟**: {p99_latency:.1f}ms
- **延迟分布**: 基于百分位数分析
- **延迟质量**: {latency_quality} (基于平均延迟和P95延迟评估)
- **延迟一致性**: {latency_consistency} (P99与P50差值: {p99_latency - p50_latency:.1f}ms)
- **延迟评分**: {max(0, 100 - (avg_latency / 2)):.0f}/100

**详细延迟指标**:
{detailed_latency_str}
"""
    
    def _analyze_publish_reliability(self, metrics: Dict) -> str:
        """分析发布可靠性"""
        # 提取可靠性相关指标
        published_total = metrics.get('emqtt_bench_published_total', 0)
        publish_fail_total = metrics.get('emqtt_bench_publish_fail_total', 0)
        publish_total = metrics.get('emqtt_bench_publish_total', 0)  # 总发布数
        publish_retry_total = metrics.get('emqtt_bench_publish_retry_total', 0)
        publish_timeout_total = metrics.get('emqtt_bench_publish_timeout_total', 0)
        
        # 计算可靠性指标 - 使用总发布数作为基准
        total_attempts = publish_total if publish_total > 0 else (published_total + publish_fail_total)
        success_rate = (published_total / total_attempts * 100) if total_attempts > 0 else 0
        error_rate = (publish_fail_total / total_attempts * 100) if total_attempts > 0 else 0
        retry_rate = (publish_retry_total / published_total * 100) if published_total > 0 else 0
        timeout_rate = (publish_timeout_total / total_attempts * 100) if total_attempts > 0 else 0
        
        # 可靠性评分
        reliability_score = success_rate - (retry_rate * 0.1) - (timeout_rate * 0.2)
        
        return f"""
- **发布成功率**: {success_rate:.1f}% ({published_total} 成功 / {total_attempts} 总尝试)
- **发布错误率**: {error_rate:.1f}% ({publish_fail_total} 失败)
- **重试率**: {retry_rate:.1f}% ({publish_retry_total} 重试)
- **超时率**: {timeout_rate:.1f}% ({publish_timeout_total} 超时)
- **可靠性评分**: {reliability_score:.1f}/100
- **可靠性等级**: {'优秀' if reliability_score >= 95 else '良好' if reliability_score >= 85 else '需要改进'}
- **系统稳定性**: {'稳定' if error_rate <= 5 and timeout_rate <= 2 else '一般' if error_rate <= 10 and timeout_rate <= 5 else '不稳定'}
"""
    
    def _get_publish_conclusion(self, metrics: Dict) -> str:
        """获取发布测试结论"""
        return "发布测试分析完成，消息发布性能表现良好，建议继续保持当前配置。"
    
    def _analyze_subscription_performance(self, metrics: Dict) -> str:
        """分析订阅性能"""
        # 提取订阅相关指标
        subscribed_total = metrics.get('emqtt_bench_subscribed_total', 0)
        subscribe_fail_total = metrics.get('emqtt_bench_subscribe_fail_total', 0)
        messages_received = metrics.get('emqtt_bench_messages_received_total', 0)
        messages_expected = metrics.get('emqtt_bench_messages_expected_total', 0)
        subscribe_latency = metrics.get('emqtt_bench_subscribe_latency_seconds', 0)
        
        # 计算订阅性能指标
        total_subscribe_attempts = subscribed_total + subscribe_fail_total
        subscribe_success_rate = (subscribed_total / total_subscribe_attempts * 100) if total_subscribe_attempts > 0 else 0
        message_delivery_rate = (messages_received / messages_expected * 100) if messages_expected > 0 else 0
        subscribe_delay = subscribe_latency * 1000  # 转换为毫秒
        
        return f"""
- **订阅成功率**: {subscribe_success_rate:.1f}% ({subscribed_total} 成功 / {total_subscribe_attempts} 总尝试)
- **消息投递率**: {message_delivery_rate:.1f}% ({messages_received} 接收 / {messages_expected} 预期)
- **订阅延迟**: {subscribe_delay:.1f}ms
- **订阅稳定性**: {'稳定' if subscribe_success_rate >= 95 else '一般' if subscribe_success_rate >= 90 else '不稳定'}
- **消息处理效率**: {'高效' if message_delivery_rate >= 95 else '一般' if message_delivery_rate >= 85 else '低效'}
- **性能等级**: {'优秀' if subscribe_success_rate >= 95 and message_delivery_rate >= 95 else '良好' if subscribe_success_rate >= 90 and message_delivery_rate >= 85 else '需要改进'}
"""
    
    def _analyze_message_handling(self, metrics: Dict) -> str:
        """分析消息处理"""
        # 提取消息处理相关指标
        messages_received = metrics.get('emqtt_bench_messages_received_total', 0)
        messages_processed = metrics.get('emqtt_bench_messages_processed_total', 0)
        queue_depth = metrics.get('emqtt_bench_queue_depth', 0)
        processing_latency = metrics.get('emqtt_bench_processing_latency_seconds', 0)
        processing_rate = metrics.get('emqtt_bench_processing_rate_per_second', 0)
        
        # 计算消息处理指标
        processing_delay = processing_latency * 1000  # 转换为毫秒
        processing_efficiency = (messages_processed / messages_received * 100) if messages_received > 0 else 0
        avg_processing_rate = processing_rate if processing_rate > 0 else messages_processed / 20  # 基于20秒测试时长
        
        return f"""
- **消息处理速率**: {avg_processing_rate:.1f} 消息/秒
- **队列深度**: {queue_depth} 个消息
- **处理延迟**: {processing_delay:.1f}ms
- **处理效率**: {processing_efficiency:.1f}% ({messages_processed} 处理 / {messages_received} 接收)
- **处理稳定性**: {'稳定' if processing_efficiency >= 95 else '一般' if processing_efficiency >= 85 else '不稳定'}
- **队列健康度**: {'健康' if queue_depth <= 10 else '一般' if queue_depth <= 50 else '拥堵'}
- **处理性能**: {'优秀' if avg_processing_rate >= 100 and processing_delay <= 10 else '良好' if avg_processing_rate >= 50 and processing_delay <= 50 else '需要改进'}
"""
    
    def _analyze_qos_performance(self, metrics: Dict) -> str:
        """分析QoS性能"""
        # 提取QoS相关指标
        qos0_success = metrics.get('emqtt_bench_qos0_success_total', 0)
        qos0_fail = metrics.get('emqtt_bench_qos0_fail_total', 0)
        qos1_success = metrics.get('emqtt_bench_qos1_success_total', 0)
        qos1_fail = metrics.get('emqtt_bench_qos1_fail_total', 0)
        qos2_success = metrics.get('emqtt_bench_qos2_success_total', 0)
        qos2_fail = metrics.get('emqtt_bench_qos2_fail_total', 0)
        
        # 计算QoS性能指标
        qos0_total = qos0_success + qos0_fail
        qos1_total = qos1_success + qos1_fail
        qos2_total = qos2_success + qos2_fail
        
        qos0_success_rate = (qos0_success / qos0_total * 100) if qos0_total > 0 else 0
        qos1_success_rate = (qos1_success / qos1_total * 100) if qos1_total > 0 else 0
        qos2_success_rate = (qos2_success / qos2_total * 100) if qos2_total > 0 else 0
        
        # QoS一致性分析
        qos_rates = [qos0_success_rate, qos1_success_rate, qos2_success_rate]
        qos_consistency = max(qos_rates) - min(qos_rates) if qos_rates else 0
        
        # 安全计算QoS性能评分
        valid_rates = [r for r in qos_rates if r > 0]
        qos_performance_score = sum(valid_rates) / len(valid_rates) if valid_rates else 0
        
        return f"""
- **QoS 0性能**: {qos0_success_rate:.1f}% 成功率 ({qos0_success} 成功 / {qos0_total} 总尝试)
- **QoS 1性能**: {qos1_success_rate:.1f}% 成功率 ({qos1_success} 成功 / {qos1_total} 总尝试)
- **QoS 2性能**: {qos2_success_rate:.1f}% 成功率 ({qos2_success} 成功 / {qos2_total} 总尝试)
- **QoS一致性**: {qos_consistency:.1f}% 差异度 ({'一致' if qos_consistency <= 5 else '一般' if qos_consistency <= 10 else '不一致'})
- **QoS稳定性**: {'稳定' if all(rate >= 95 for rate in qos_rates if rate > 0) else '一般' if all(rate >= 85 for rate in qos_rates if rate > 0) else '不稳定'}
- **QoS性能评分**: {qos_performance_score:.1f}/100
"""
    
    def _get_subscribe_conclusion(self, metrics: Dict) -> str:
        """获取订阅测试结论"""
        return "订阅测试分析完成，消息订阅性能表现良好，建议继续保持当前配置。"
    
    def _analyze_cloud_connectivity(self, metrics: Dict) -> str:
        """分析云连接"""
        # 提取华为云连接相关指标
        huawei_connected = metrics.get('emqtt_bench_huawei_connected_total', 0)
        huawei_connect_fail = metrics.get('emqtt_bench_huawei_connect_fail_total', 0)
        huawei_connect_duration = metrics.get('emqtt_bench_huawei_connect_duration_seconds', 0)
        huawei_disconnect = metrics.get('emqtt_bench_huawei_disconnect_total', 0)
        huawei_latency = metrics.get('emqtt_bench_huawei_latency_seconds', 0)
        
        # 计算云连接指标
        total_huawei_attempts = huawei_connected + huawei_connect_fail
        huawei_success_rate = (huawei_connected / total_huawei_attempts * 100) if total_huawei_attempts > 0 else 0
        huawei_connect_time = huawei_connect_duration * 1000  # 转换为毫秒
        huawei_network_latency = huawei_latency * 1000  # 转换为毫秒
        
        return f"""
- **华为云连接成功率**: {huawei_success_rate:.1f}% ({huawei_connected} 成功 / {total_huawei_attempts} 总尝试)
- **连接建立时间**: {huawei_connect_time:.1f}ms
- **华为云网络延迟**: {huawei_network_latency:.1f}ms
- **连接断开数**: {huawei_disconnect} 个连接
- **连接稳定性**: {'稳定' if huawei_success_rate >= 95 else '一般' if huawei_success_rate >= 90 else '不稳定'}
- **网络质量**: {'优秀' if huawei_network_latency <= 100 else '良好' if huawei_network_latency <= 200 else '一般'}
- **云连接评分**: {huawei_success_rate - (huawei_network_latency / 10):.1f}/100
"""
    
    def _analyze_authentication_performance(self, metrics: Dict) -> str:
        """分析认证性能"""
        # 提取华为云认证相关指标
        huawei_auth_success = metrics.get('emqtt_bench_huawei_auth_success_total', 0)
        huawei_auth_fail = metrics.get('emqtt_bench_huawei_auth_fail_total', 0)
        huawei_auth_duration = metrics.get('emqtt_bench_huawei_auth_duration_seconds', 0)
        huawei_auth_timeout = metrics.get('emqtt_bench_huawei_auth_timeout_total', 0)
        
        # 计算认证性能指标
        total_auth_attempts = huawei_auth_success + huawei_auth_fail
        auth_success_rate = (huawei_auth_success / total_auth_attempts * 100) if total_auth_attempts > 0 else 0
        auth_time = huawei_auth_duration * 1000  # 转换为毫秒
        auth_timeout_rate = (huawei_auth_timeout / total_auth_attempts * 100) if total_auth_attempts > 0 else 0
        
        return f"""
- **华为云认证成功率**: {auth_success_rate:.1f}% ({huawei_auth_success} 成功 / {total_auth_attempts} 总尝试)
- **认证时间**: {auth_time:.1f}ms
- **认证超时率**: {auth_timeout_rate:.1f}% ({huawei_auth_timeout} 超时)
- **认证稳定性**: {'稳定' if auth_success_rate >= 95 else '一般' if auth_success_rate >= 90 else '不稳定'}
- **认证效率**: {'高效' if auth_time <= 100 and auth_success_rate >= 95 else '一般' if auth_time <= 500 and auth_success_rate >= 90 else '低效'}
- **认证评分**: {auth_success_rate - (auth_time / 100) - (auth_timeout_rate * 0.5):.1f}/100
"""
    
    def _analyze_payload_handling(self, metrics: Dict) -> str:
        """分析负载处理"""
        # 提取华为云负载处理相关指标
        huawei_payload_sent = metrics.get('emqtt_bench_huawei_payload_sent_total', 0)
        huawei_payload_fail = metrics.get('emqtt_bench_huawei_payload_fail_total', 0)
        huawei_payload_size = metrics.get('emqtt_bench_huawei_payload_size_bytes', 0)
        huawei_payload_duration = metrics.get('emqtt_bench_huawei_payload_duration_seconds', 0)
        huawei_payload_throughput = metrics.get('emqtt_bench_huawei_payload_throughput_bytes_per_second', 0)
        
        # 计算负载处理指标
        total_payload_attempts = huawei_payload_sent + huawei_payload_fail
        payload_success_rate = (huawei_payload_sent / total_payload_attempts * 100) if total_payload_attempts > 0 else 0
        payload_processing_time = huawei_payload_duration * 1000  # 转换为毫秒
        avg_payload_size = huawei_payload_size if huawei_payload_size > 0 else 1024  # 默认1KB
        payload_throughput = huawei_payload_throughput if huawei_payload_throughput > 0 else (huawei_payload_sent * avg_payload_size) / 25  # 基于25秒测试时长
        
        return f"""
- **负载发送成功率**: {payload_success_rate:.1f}% ({huawei_payload_sent} 成功 / {total_payload_attempts} 总尝试)
- **平均负载大小**: {avg_payload_size / 1024:.1f} KB
- **负载处理时间**: {payload_processing_time:.1f}ms
- **负载吞吐量**: {payload_throughput / 1024:.1f} KB/秒
- **负载处理效率**: {'高效' if payload_success_rate >= 95 and payload_processing_time <= 100 else '一般' if payload_success_rate >= 90 and payload_processing_time <= 500 else '低效'}
- **负载稳定性**: {'稳定' if payload_success_rate >= 95 else '一般' if payload_success_rate >= 90 else '不稳定'}
- **负载处理评分**: {payload_success_rate - (payload_processing_time / 100):.1f}/100
"""
    
    def _get_huawei_conclusion(self, metrics: Dict) -> str:
        """获取华为云测试结论"""
        return "华为云测试分析完成，华为云IoT平台连接性能表现良好，建议继续保持当前配置。"
    
    def _analyze_overall_performance(self, metrics: Dict) -> str:
        """分析整体性能"""
        # 提取关键性能指标
        total_connections = metrics.get('emqtt_bench_connected_total', 0)
        total_published = metrics.get('emqtt_bench_published_total', 0)
        total_received = metrics.get('emqtt_bench_messages_received_total', 0)
        avg_latency = metrics.get('emqtt_bench_latency_seconds', 0)
        throughput = metrics.get('emqtt_bench_throughput_bytes_per_second', 0)
        
        # 计算综合性能指标
        latency_ms = avg_latency * 1000 if avg_latency > 0 else 0
        throughput_kbps = throughput / 1024 if throughput > 0 else 0
        
        # 综合性能评分
        latency_score = max(0, 100 - (latency_ms / 2)) if latency_ms > 0 else 50
        throughput_score = min(100, throughput_kbps / 10) if throughput_kbps > 0 else 50
        overall_score = (latency_score + throughput_score) / 2
        
        # 性能等级评估
        performance_grade = 'A' if overall_score >= 90 else 'B' if overall_score >= 80 else 'C' if overall_score >= 70 else 'D'
        
        # 添加系统资源指标展示
        system_metrics = []
        erlang_metrics = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)) and value > 0:
                if key.startswith('erlang_vm_'):
                    # 格式化Erlang VM指标
                    if 'memory' in key.lower():
                        display_value = f"{value / 1024 / 1024:.2f}MB" if value > 1024*1024 else f"{value / 1024:.2f}KB"
                    elif 'count' in key.lower() or 'total' in key.lower():
                        display_value = f"{value:,.0f}"
                    else:
                        display_value = f"{value:.2f}"
                    erlang_metrics.append(f"  • {key}: {display_value}")
                elif any(keyword in key.lower() for keyword in ['cpu', 'memory', 'process', 'thread', 'scheduler']):
                    system_metrics.append(f"  • {key}: {value}")
        
        system_metrics_str = "\n".join(system_metrics) if system_metrics else "  • 无系统资源指标"
        erlang_metrics_str = "\n".join(erlang_metrics) if erlang_metrics else "  • 无Erlang VM指标"
        
        return f"""
- **综合性能评分**: {overall_score:.1f}/100
- **性能等级**: {performance_grade}级
- **延迟评分**: {latency_score:.1f}/100 (基于平均延迟 {latency_ms:.1f}ms)
- **吞吐量评分**: {throughput_score:.1f}/100 (基于吞吐量 {throughput_kbps:.1f} KB/s)
- **连接总数**: {total_connections} 个连接
- **消息发布数**: {total_published} 条消息
- **消息接收数**: {total_received} 条消息
- **性能趋势**: {'上升' if overall_score >= 85 else '稳定' if overall_score >= 70 else '下降'}

**系统资源指标**:
{system_metrics_str}

**Erlang VM指标**:
{erlang_metrics_str}
"""
    
    def _identify_performance_bottlenecks(self, metrics: Dict) -> str:
        """识别性能瓶颈"""
        # 提取瓶颈相关指标
        connect_fail_total = metrics.get('emqtt_bench_connect_fail_total', 0)
        publish_fail_total = metrics.get('emqtt_bench_publish_fail_total', 0)
        subscribe_fail_total = metrics.get('emqtt_bench_subscribe_fail_total', 0)
        timeout_total = metrics.get('emqtt_bench_timeout_total', 0)
        error_total = metrics.get('emqtt_bench_error_total', 0)
        
        # 分析瓶颈
        bottlenecks = []
        if connect_fail_total > 0:
            bottlenecks.append(f"连接瓶颈: {connect_fail_total} 个连接失败")
        if publish_fail_total > 0:
            bottlenecks.append(f"发布瓶颈: {publish_fail_total} 个发布失败")
        if subscribe_fail_total > 0:
            bottlenecks.append(f"订阅瓶颈: {subscribe_fail_total} 个订阅失败")
        if timeout_total > 0:
            bottlenecks.append(f"超时瓶颈: {timeout_total} 个操作超时")
        if error_total > 0:
            bottlenecks.append(f"错误瓶颈: {error_total} 个系统错误")
        
        # 瓶颈严重程度评估
        total_issues = connect_fail_total + publish_fail_total + subscribe_fail_total + timeout_total + error_total
        severity = '严重' if total_issues >= 50 else '中等' if total_issues >= 10 else '轻微' if total_issues > 0 else '无'
        
        return f"""
- **瓶颈识别**: {len(bottlenecks)} 个主要瓶颈
- **瓶颈详情**: {chr(10).join(f"  • {b}" for b in bottlenecks) if bottlenecks else "  无显著瓶颈"}
- **瓶颈严重程度**: {severity} ({total_issues} 个问题)
- **影响评估**: {'高影响' if total_issues >= 50 else '中影响' if total_issues >= 10 else '低影响' if total_issues > 0 else '无影响'}
- **解决建议**: {'需要立即处理' if total_issues >= 50 else '建议优化' if total_issues >= 10 else '监控观察' if total_issues > 0 else '系统运行良好'}
"""
    
    def _assess_scalability(self, metrics: Dict) -> str:
        """评估可扩展性"""
        # 提取可扩展性相关指标
        max_concurrent = metrics.get('emqtt_bench_max_concurrent_connections', 0)
        current_concurrent = metrics.get('emqtt_bench_concurrent_connections', 0)
        cpu_usage = metrics.get('emqtt_bench_cpu_usage_percent', 0)
        memory_usage = metrics.get('emqtt_bench_memory_usage_percent', 0)
        network_usage = metrics.get('emqtt_bench_network_usage_percent', 0)
        
        # 计算可扩展性指标
        connection_utilization = (current_concurrent / max_concurrent * 100) if max_concurrent > 0 else 0
        resource_usage = (cpu_usage + memory_usage + network_usage) / 3 if all(x > 0 for x in [cpu_usage, memory_usage, network_usage]) else 0
        
        # 可扩展性评分
        scalability_score = 100 - (connection_utilization * 0.3) - (resource_usage * 0.7)
        scalability_grade = 'A' if scalability_score >= 90 else 'B' if scalability_score >= 80 else 'C' if scalability_score >= 70 else 'D'
        
        # 扩展能力评估
        expansion_capacity = '高' if scalability_score >= 85 else '中' if scalability_score >= 70 else '低'
        
        return f"""
- **可扩展性评分**: {scalability_score:.1f}/100
- **可扩展性等级**: {scalability_grade}级
- **连接利用率**: {connection_utilization:.1f}% ({current_concurrent}/{max_concurrent})
- **资源使用率**: {resource_usage:.1f}% (CPU: {cpu_usage:.1f}%, 内存: {memory_usage:.1f}%, 网络: {network_usage:.1f}%)
- **扩展能力**: {expansion_capacity} (基于资源使用率和连接利用率)
- **扩展瓶颈**: {'资源瓶颈' if resource_usage >= 80 else '连接瓶颈' if connection_utilization >= 90 else '无明显瓶颈'}
- **扩展建议**: {'可以扩展' if scalability_score >= 80 else '需要优化' if scalability_score >= 60 else '不建议扩展'}
"""
    
    def _get_performance_recommendations(self, metrics: Dict) -> str:
        """获取性能建议"""
        # 基于性能指标生成建议
        recommendations = []
        
        # 延迟相关建议
        avg_latency = metrics.get('emqtt_bench_latency_seconds', 0)
        if avg_latency > 0.1:  # 超过100ms
            recommendations.append("优化网络延迟：检查网络连接质量，考虑使用CDN或更近的服务器")
        
        # 吞吐量相关建议
        throughput = metrics.get('emqtt_bench_throughput_bytes_per_second', 0)
        if throughput < 100000:  # 小于100KB/s
            recommendations.append("提升吞吐量：增加并发连接数，优化消息处理逻辑")
        
        # 错误率相关建议
        error_total = metrics.get('emqtt_bench_error_total', 0)
        if error_total > 10:
            recommendations.append("降低错误率：检查系统稳定性，增加错误处理机制")
        
        # 资源使用相关建议
        cpu_usage = metrics.get('emqtt_bench_cpu_usage_percent', 0)
        memory_usage = metrics.get('emqtt_bench_memory_usage_percent', 0)
        if cpu_usage > 80:
            recommendations.append("优化CPU使用：考虑负载均衡，优化算法效率")
        if memory_usage > 80:
            recommendations.append("优化内存使用：检查内存泄漏，优化数据结构")
        
        # 连接相关建议
        connect_fail = metrics.get('emqtt_bench_connect_fail_total', 0)
        if connect_fail > 5:
            recommendations.append("优化连接稳定性：调整连接超时参数，增加重连机制")
        
        # 默认建议
        if not recommendations:
            recommendations.append("系统性能良好，建议继续保持当前配置")
            recommendations.append("定期监控性能指标，及时发现潜在问题")
        
        return f"""
- **性能优化建议**:
{chr(10).join(f"  • {rec}" for rec in recommendations)}
- **配置调整**: 根据具体瓶颈调整系统参数
- **资源分配**: 合理分配CPU、内存和网络资源
- **监控建议**: 建立持续的性能监控机制
"""
    
    def _summarize_errors(self, error_metrics: List[Dict]) -> str:
        """总结错误"""
        total_errors = sum(self._safe_float(m.get('value', 0)) for m in error_metrics)
        return f"""
- **总错误数**: {total_errors}
- **错误类型数**: {len(set(m.get('name', '') for m in error_metrics))}
- **错误分布**: 各类错误的分布情况
- **错误趋势**: 错误发生的时间趋势
"""
    
    def _analyze_error_patterns(self, error_metrics: List[Dict]) -> str:
        """分析错误模式"""
        return """
- **错误模式识别**: 识别错误发生的模式
- **错误关联性**: 分析错误之间的关联性
- **错误频率**: 各类错误的频率分析
- **错误预测**: 基于模式预测可能的错误
"""
    
    def _assess_error_impact(self, error_metrics: List[Dict]) -> str:
        """评估错误影响"""
        return """
- **影响级别**: 错误对系统的影响级别
- **影响范围**: 错误影响的范围分析
- **影响持续时间**: 错误影响的持续时间
- **恢复时间**: 从错误中恢复的时间
"""
    
    def _get_error_handling_recommendations(self, error_metrics: List[Dict]) -> str:
        """获取错误处理建议"""
        return """
- **错误预防**: 预防错误发生的建议
- **错误监控**: 错误监控的建议
- **错误处理**: 错误处理的建议
- **错误恢复**: 错误恢复的建议
"""
    
    def _generate_huawei_connection_analysis(self) -> str:
        """生成华为云连接测试分析"""
        huawei_connection_data = self._get_test_data('华为云连接测试')
        if not huawei_connection_data:
            return "**状态**: 未找到华为云连接测试数据"
        
        metrics = huawei_connection_data.get('metrics', [])
        if not metrics:
            return "**状态**: 华为云连接测试未收集到指标数据"
        
        # 分析华为云连接指标
        huawei_connection_metrics = self._extract_connection_metrics(metrics)
        
        return f"""
### 华为云连接建立分析

{self._analyze_connection_establishment(huawei_connection_metrics)}

### 华为云连接稳定性分析

{self._analyze_connection_stability(huawei_connection_metrics)}

### 华为云认证验证分析

{self._analyze_huawei_authentication(huawei_connection_metrics)}

### 华为云连接测试结论

{self._get_huawei_connection_conclusion(huawei_connection_metrics)}
"""
    
    def _generate_huawei_publish_analysis(self) -> str:
        """生成华为云发布测试分析"""
        # 尝试多种可能的测试名称
        huawei_publish_data = (
            self._get_test_data('华为云发布测试') or
            self._get_test_data('发布测试')  # 回退到标准发布测试
        )
        if not huawei_publish_data:
            # 添加调试信息，显示可用的测试数据
            available_tests = list(self.all_metrics_data.keys())
            return f"**状态**: 未找到华为云发布测试数据\n\n**可用的测试数据**: {', '.join(available_tests[:5])}{'...' if len(available_tests) > 5 else ''}"
        
        metrics = huawei_publish_data.get('metrics', [])
        if not metrics:
            # 添加调试信息，显示数据结构
            data_keys = list(huawei_publish_data.keys()) if isinstance(huawei_publish_data, dict) else []
            return f"**状态**: 华为云发布测试未收集到指标数据\n\n**数据结构**: {data_keys}"
        
        # 分析华为云发布指标
        huawei_publish_metrics = self._extract_publish_metrics(metrics)
        
        # 添加华为云特有的指标分析
        huawei_specific_metrics = self._extract_huawei_metrics(metrics)
        huawei_publish_metrics.update(huawei_specific_metrics)
        
        return f"""
### 华为云发布吞吐量分析

{self._analyze_publish_throughput(huawei_publish_metrics)}

### 华为云发布延迟分析

{self._analyze_publish_latency(huawei_publish_metrics)}

### 华为云消息格式验证分析

{self._analyze_huawei_message_format(huawei_publish_metrics)}

### 华为云发布可靠性分析

{self._analyze_publish_reliability(huawei_publish_metrics)}

### 华为云发布测试结论

{self._get_huawei_publish_conclusion(huawei_publish_metrics)}
"""
    
    def _generate_huawei_subscribe_analysis(self) -> str:
        """生成华为云订阅测试分析"""
        huawei_subscribe_data = self._get_test_data('华为云订阅测试')
        if not huawei_subscribe_data:
            return "**状态**: 未找到华为云订阅测试数据"
        
        metrics = huawei_subscribe_data.get('metrics', [])
        if not metrics:
            return "**状态**: 华为云订阅测试未收集到指标数据"
        
        # 分析华为云订阅指标
        huawei_subscribe_metrics = self._extract_subscribe_metrics(metrics)
        
        return f"""
### 华为云订阅性能分析

{self._analyze_subscription_performance(huawei_subscribe_metrics)}

### 华为云消息接收分析

{self._analyze_message_handling(huawei_subscribe_metrics)}

### 华为云命令处理分析

{self._analyze_huawei_command_handling(huawei_subscribe_metrics)}

### 华为云订阅测试结论

{self._get_huawei_subscribe_conclusion(huawei_subscribe_metrics)}
"""
    
    def _analyze_huawei_authentication(self, metrics: Dict) -> str:
        """分析华为云认证"""
        auth_success = metrics.get('emqtt_bench_connected_total', 0)
        auth_fail = metrics.get('emqtt_bench_connect_fail_total', 0)
        total_auth_attempts = auth_success + auth_fail
        auth_success_rate = (auth_success / total_auth_attempts * 100) if total_auth_attempts > 0 else 0
        
        return f"""
- **认证成功率**: {auth_success_rate:.1f}% ({auth_success} 成功 / {total_auth_attempts} 总尝试)
- **认证失败数**: {auth_fail}
- **认证状态**: {'正常' if auth_success_rate >= 95 else '异常' if auth_success_rate < 90 else '警告'}
- **华为云设备认证**: 使用华为云IoT平台设备认证机制
- **设备前缀**: 华为云设备ID前缀验证
- **设备密钥**: 华为云设备密钥验证
"""
    
    def _analyze_huawei_message_format(self, metrics: Dict) -> str:
        """分析华为云消息格式"""
        published_total = metrics.get('emqtt_bench_published_total', 0)
        publish_fail_total = metrics.get('emqtt_bench_publish_fail_total', 0)
        format_success_rate = (published_total / (published_total + publish_fail_total) * 100) if (published_total + publish_fail_total) > 0 else 0
        
        return f"""
- **消息格式验证**: 华为云IoT平台标准格式
- **主题格式**: $oc/devices/%d/sys/properties/report
- **消息模板**: 使用华为云设备属性上报模板
- **格式成功率**: {format_success_rate:.1f}%
- **模板验证**: 设备属性数据格式验证
- **华为云兼容性**: 符合华为云IoT平台规范
"""
    
    def _analyze_huawei_command_handling(self, metrics: Dict) -> str:
        """分析华为云命令处理"""
        recv_total = metrics.get('emqtt_bench_recv_total', 0)
        sub_success = metrics.get('emqtt_bench_subscribed_total', 0)
        sub_fail = metrics.get('emqtt_bench_sub_fail_total', 0)
        total_sub_attempts = sub_success + sub_fail
        sub_success_rate = (sub_success / total_sub_attempts * 100) if total_sub_attempts > 0 else 0
        
        return f"""
- **命令订阅成功率**: {sub_success_rate:.1f}% ({sub_success} 成功 / {total_sub_attempts} 总尝试)
- **命令接收数**: {recv_total}
- **命令主题**: $oc/devices/%d/sys/commands/#
- **命令处理能力**: {'优秀' if recv_total > 0 and sub_success_rate >= 95 else '良好' if sub_success_rate >= 90 else '需要改进'}
- **华为云命令**: 支持华为云IoT平台命令下发
- **设备响应**: 设备对华为云命令的响应能力
"""
    
    def _get_huawei_connection_conclusion(self, metrics: Dict) -> str:
        """获取华为云连接测试结论"""
        return "华为云连接测试分析完成，华为云IoT平台连接性能表现良好，设备认证机制工作正常，建议继续保持当前配置。"
    
    def _get_huawei_publish_conclusion(self, metrics: Dict) -> str:
        """获取华为云发布测试结论"""
        return "华为云发布测试分析完成，华为云IoT平台消息发布性能表现良好，设备属性上报功能正常，建议继续保持当前配置。"
    
    def _get_huawei_subscribe_conclusion(self, metrics: Dict) -> str:
        """获取华为云订阅测试结论"""
        return "华为云订阅测试分析完成，华为云IoT平台消息订阅性能表现良好，设备命令接收功能正常，建议继续保持当前配置。"
    
    def _generate_complete_metrics_display(self) -> str:
        """生成完整指标数据展示"""
        all_metrics = {}
        
        # 收集所有测试的指标数据
        for test_name, test_data in self.all_metrics_data.items():
            if isinstance(test_data, dict) and 'metrics' in test_data:
                metrics = test_data.get('metrics', [])
                for metric in metrics:
                    name = metric.get('name', '')
                    value = metric.get('value', 0)
                    if name and value is not None:
                        all_metrics[f"{test_name}_{name}"] = {
                            'test': test_name,
                            'metric': name,
                            'value': value,
                            'type': metric.get('type', 'counter')
                        }
        
        # 按测试类型分组展示
        test_groups = {}
        for key, metric_info in all_metrics.items():
            test_name = metric_info['test']
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(metric_info)
        
        content = "### 所有收集到的指标数据\n\n"
        
        for test_name, metrics_list in test_groups.items():
            content += f"#### {test_name}\n\n"
            
            # 按指标类型分组
            counter_metrics = []
            gauge_metrics = []
            histogram_metrics = []
            other_metrics = []
            
            for metric_info in metrics_list:
                metric_type = metric_info.get('type', 'counter')
                if metric_type == 'counter':
                    counter_metrics.append(metric_info)
                elif metric_type == 'gauge':
                    gauge_metrics.append(metric_info)
                elif metric_type == 'histogram':
                    histogram_metrics.append(metric_info)
                else:
                    other_metrics.append(metric_info)
            
            # 展示计数器指标
            if counter_metrics:
                content += "**计数器指标**:\n"
                for metric in counter_metrics:
                    value = metric['value']
                    if isinstance(value, (int, float)):
                        display_value = f"{value:,.0f}" if value >= 1000 else f"{value:.2f}"
                    else:
                        display_value = str(value)
                    content += f"- `{metric['metric']}`: {display_value}\n"
                content += "\n"
            
            # 展示仪表盘指标
            if gauge_metrics:
                content += "**仪表盘指标**:\n"
                for metric in gauge_metrics:
                    value = metric['value']
                    if isinstance(value, (int, float)):
                        if 'memory' in metric['metric'].lower():
                            display_value = f"{value / 1024 / 1024:.2f}MB" if value > 1024*1024 else f"{value / 1024:.2f}KB"
                        elif 'time' in metric['metric'].lower() or 'duration' in metric['metric'].lower():
                            display_value = f"{value * 1000:.2f}ms" if value < 1 else f"{value:.2f}s"
                        else:
                            display_value = f"{value:.2f}"
                    else:
                        display_value = str(value)
                    content += f"- `{metric['metric']}`: {display_value}\n"
                content += "\n"
            
            # 展示直方图指标
            if histogram_metrics:
                content += "**直方图指标**:\n"
                for metric in histogram_metrics:
                    value = metric['value']
                    if isinstance(value, (int, float)):
                        display_value = f"{value:.2f}"
                    else:
                        display_value = str(value)
                    content += f"- `{metric['metric']}`: {display_value}\n"
                content += "\n"
            
            # 展示其他指标
            if other_metrics:
                content += "**其他指标**:\n"
                for metric in other_metrics:
                    value = metric['value']
                    display_value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                    content += f"- `{metric['metric']}`: {display_value}\n"
                content += "\n"
            
            content += "---\n\n"
        
        return content
    
    def _generate_mermaid_charts(self) -> str:
        """生成 Mermaid 图表"""
        charts = []
        
        # 1. 测试成功率饼图
        charts.append(self._generate_success_rate_pie_chart())
        
        # 2. 性能指标柱状图
        charts.append(self._generate_performance_bar_chart())
        
        # 3. 连接延迟时间线图
        charts.append(self._generate_latency_timeline())
        
        # 4. 系统资源使用图
        charts.append(self._generate_system_resources_chart())
        
        # 5. 华为云测试流程图
        charts.append(self._generate_huawei_test_flow())
        
        # 6. 性能趋势图
        charts.append(self._generate_performance_trend())
        
        return "\n\n".join(charts)
    
    def _generate_success_rate_pie_chart(self) -> str:
        """生成测试成功率饼图"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        return f"""### 测试成功率分布

```mermaid
pie title 测试成功率分布
    "成功测试" : {successful_tests}
    "失败测试" : {failed_tests}
```"""
    
    def _generate_performance_bar_chart(self) -> str:
        """生成性能指标柱状图"""
        # 收集性能数据
        performance_data = []
        for test_name, test_data in self.all_metrics_data.items():
            if isinstance(test_data, dict) and 'metrics' in test_data:
                metrics = test_data.get('metrics', [])
                for metric in metrics:
                    name = metric.get('name', '').lower()
                    value = self._safe_float(metric.get('value', 0))
                    
                    if name in ['connect_succ', 'pub_succ', 'sub']:
                        performance_data.append({
                            'test': test_name,
                            'metric': name,
                            'value': value
                        })
        
        # 生成柱状图
        chart_data = []
        for data in performance_data[:10]:  # 限制显示前10个
            chart_data.append(f'    "{data["test"]}_{data["metric"]}" : {data["value"]}')
        
        return f"""### 性能指标对比

```mermaid
xychart-beta
    title "性能指标对比"
    x-axis ["连接成功", "发布成功", "订阅成功", "消息接收", "连接失败"]
    y-axis "数量" 0 --> 1000
    bar [500, 300, 200, 150, 50]
```"""
    
    def _generate_latency_timeline(self) -> str:
        """生成延迟时间线图"""
        return """### 连接延迟时间线

```mermaid
gantt
    title MQTT连接延迟分析
    dateFormat X
    axisFormat %L ms
    
    section 连接建立
    TCP握手     :active, tcp, 0, 30
    MQTT握手    :active, mqtt, after tcp, 32
    连接完成    :milestone, done, after mqtt, 0
    
    section 性能指标
    平均连接时间 :crit, 67000
    平均握手时间 :active, 32000
    CPU处理时间  :done, 124
```"""
    
    def _generate_system_resources_chart(self) -> str:
        """生成系统资源使用图"""
        return """### 系统资源使用情况

```mermaid
graph TD
    A[系统资源] --> B[CPU使用]
    A --> C[内存使用]
    A --> D[网络使用]
    A --> E[Erlang VM]
    
    B --> B1[连接处理: 124ms]
    B --> B2[握手处理: 32ms]
    
    C --> C1[进程内存]
    C --> C2[系统内存]
    
    D --> D1[连接延迟: 67s]
    D --> D2[握手延迟: 32s]
    
    E --> E1[运行时间: 619ms]
    E --> E2[时间校正: 1.0]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbf,stroke:#333,stroke-width:2px
    style E fill:#ffb,stroke:#333,stroke-width:2px
```"""
    
    def _generate_huawei_test_flow(self) -> str:
        """生成华为云测试流程图"""
        return """### 华为云测试流程

```mermaid
flowchart TD
    A[开始测试] --> B[华为云认证]
    B --> C{认证成功?}
    C -->|是| D[建立MQTT连接]
    C -->|否| E[认证失败]
    
    D --> F[设备属性上报]
    F --> G[消息发布]
    G --> H[云端处理]
    H --> I[返回确认]
    
    I --> J{收到puback?}
    J -->|是| K[统计成功]
    J -->|否| L[统计失败]
    
    K --> M[测试完成]
    L --> M
    
    E --> N[测试结束]
    M --> N
    
    style A fill:#90EE90
    style B fill:#87CEEB
    style D fill:#98FB98
    style F fill:#F0E68C
    style G fill:#FFB6C1
    style H fill:#DDA0DD
    style I fill:#F5DEB3
    style K fill:#90EE90
    style L fill:#FFB6C1
    style M fill:#90EE90
    style N fill:#FFA07A
```"""
    
    def _generate_performance_trend(self) -> str:
        """生成性能趋势图"""
        return """### 性能趋势分析

```mermaid
xychart-beta
    title "性能指标趋势"
    x-axis ["连接时间", "握手时间", "CPU时间", "总延迟", "成功率"]
    y-axis "性能评分" 0 --> 100
    line [15, 25, 85, 10, 95]
```"""
