#!/usr/bin/env python3
"""
eMQTT-Bench 指标收集使用示例
作者: Jaxon
日期: 2024-12-19
"""

import time
import json
from metrics_collector import PrometheusMetricsCollector, MetricsAnalyzer, MetricsExporter

def example_basic_collection():
    """基本指标收集示例"""
    print("=== 基本指标收集示例 ===")
    
    # 创建收集器
    collector = PrometheusMetricsCollector("http://localhost")
    
    # 收集单个端口的指标
    metrics = collector.fetch_metrics(8080)
    print(f"从端口 8080 收集到 {len(metrics)} 个指标")
    
    # 显示前几个指标
    for i, metric in enumerate(metrics[:5]):
        print(f"  {i+1}. {metric.name}: {metric.value}")

def example_multi_port_collection():
    """多端口指标收集示例"""
    print("\n=== 多端口指标收集示例 ===")
    
    collector = PrometheusMetricsCollector("http://localhost")
    analyzer = MetricsAnalyzer()
    
    # 收集多个端口的指标
    ports = [8080, 8081, 8082, 8083]
    all_metrics = collector.collect_all_metrics(ports)
    
    # 分析每个端口的指标
    for port, metrics in all_metrics.items():
        filtered = analyzer.filter_mqtt_bench_metrics(metrics)
        print(f"端口 {port}: 收集到 {len(metrics)} 个指标，其中 {len(filtered)} 个是 eMQTT-Bench 相关指标")
        
        if filtered:
            summary = analyzer.get_metric_summary(filtered)
            print(f"  关键指标:")
            for name, data in summary.items():
                if 'sum' in data:
                    print(f"    {name}: {data['sum']:.0f}")

def example_export_data():
    """数据导出示例"""
    print("\n=== 数据导出示例 ===")
    
    collector = PrometheusMetricsCollector("http://localhost")
    exporter = MetricsExporter("example_output")
    
    # 收集数据
    ports = [8080, 8081]
    all_metrics = collector.collect_all_metrics(ports)
    
    # 导出为 JSON
    json_file = exporter.export_to_json(all_metrics, "example_metrics.json")
    print(f"JSON 文件已保存: {json_file}")
    
    # 导出为 CSV
    csv_file = exporter.export_to_csv(all_metrics, "example_metrics.csv")
    print(f"CSV 文件已保存: {csv_file}")

def example_real_time_monitoring():
    """实时监控示例"""
    print("\n=== 实时监控示例 ===")
    print("开始监控端口 8080，按 Ctrl+C 停止...")
    
    collector = PrometheusMetricsCollector("http://localhost")
    analyzer = MetricsAnalyzer()
    
    try:
        for i in range(10):  # 监控10次
            metrics = collector.fetch_metrics(8080)
            filtered = analyzer.filter_mqtt_bench_metrics(metrics)
            
            if filtered:
                summary = analyzer.get_metric_summary(filtered)
                
                # 显示关键指标
                connected = summary.get('mqtt_bench_connected', {}).get('sum', 0)
                published = summary.get('mqtt_bench_publish_sent', {}).get('sum', 0)
                failed = summary.get('mqtt_bench_publish_failed', {}).get('sum', 0)
                
                print(f"第 {i+1} 次监控:")
                print(f"  连接数: {connected:.0f}")
                print(f"  发布消息数: {published:.0f}")
                print(f"  失败数: {failed:.0f}")
            else:
                print(f"第 {i+1} 次监控: 未找到 eMQTT-Bench 指标")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

def example_huawei_cloud_metrics():
    """华为云 IoT 平台指标监控示例"""
    print("\n=== 华为云 IoT 平台指标监控示例 ===")
    
    collector = PrometheusMetricsCollector("http://localhost")
    analyzer = MetricsAnalyzer()
    
    # 华为云测试通常使用端口 8083
    huawei_port = 8083
    
    print(f"监控华为云测试端口: {huawei_port}")
    
    metrics = collector.fetch_metrics(huawei_port)
    filtered = analyzer.filter_mqtt_bench_metrics(metrics)
    
    if filtered:
        summary = analyzer.get_metric_summary(filtered)
        
        print("华为云 IoT 平台测试指标:")
        for name, data in summary.items():
            if 'sum' in data and data['sum'] > 0:
                print(f"  {name}: {data['sum']:.0f}")
    else:
        print("未找到华为云测试指标，请确保华为云测试正在运行")

if __name__ == "__main__":
    print("eMQTT-Bench 指标收集示例")
    print("=" * 50)
    
    # 运行示例
    example_basic_collection()
    example_multi_port_collection()
    example_export_data()
    example_real_time_monitoring()
    example_huawei_cloud_metrics()
    
    print("\n示例运行完成!")
