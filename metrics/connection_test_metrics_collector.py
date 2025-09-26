#!/usr/bin/env python3
"""
连接测试专用指标收集器
专注于连接建立性能、并发能力、网络性能等核心指标
作者: Jaxon
日期: 2024-12-19
"""

import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import statistics
import threading
from collections import defaultdict, deque

@dataclass
class ConnectionMetrics:
    """连接指标数据类"""
    timestamp: datetime
    total_attempts: int
    successful_connections: int
    failed_connections: int
    connection_times: List[float]
    concurrent_connections: int
    max_concurrent: int
    connection_rate: float
    error_types: Dict[str, int]
    system_resources: Dict[str, float]

class ConnectionTestMetricsCollector:
    """连接测试专用指标收集器"""
    
    def __init__(self, prometheus_port: int = 9090):
        self.prometheus_port = prometheus_port
        self.metrics_history: deque = deque(maxlen=1000)  # 保留最近1000个数据点
        self.connection_times: List[float] = []
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()
        self.last_metrics_time = self.start_time
        self.collection_thread = None
        self.running = False
        
        # 性能统计
        self.performance_stats = {
            'connection_success_rate': 0.0,
            'avg_connection_time': 0.0,
            'connection_rate': 0.0,
            'max_concurrent_connections': 0,
            'current_concurrent_connections': 0,
            'error_rate': 0.0,
            'system_resource_usage': {}
        }
    
    def start_collection(self, interval: float = 1.0):
        """开始收集指标"""
        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, 
            args=(interval,), 
            daemon=True
        )
        self.collection_thread.start()
        print(f"🔍 连接测试指标收集器已启动 (端口: {self.prometheus_port}, 间隔: {interval}s)")
    
    def stop_collection(self):
        """停止收集指标"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=2)
        print("⏹️ 连接测试指标收集器已停止")
    
    def _collection_loop(self, interval: float):
        """指标收集循环"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                    self._update_performance_stats(metrics)
                
                time.sleep(interval)
            except Exception as e:
                print(f"❌ 指标收集错误: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> Optional[ConnectionMetrics]:
        """收集单次指标数据"""
        try:
            # 从Prometheus端点获取指标
            prometheus_metrics = self._fetch_prometheus_metrics()
            if not prometheus_metrics:
                return None
            
            # 解析连接相关指标
            connection_data = self._parse_connection_metrics(prometheus_metrics)
            
            # 获取系统资源使用情况
            system_resources = self._get_system_resources()
            
            # 计算连接时间统计
            connection_times = self._extract_connection_times(prometheus_metrics)
            
            # 计算错误类型分布
            error_types = self._extract_error_types(prometheus_metrics)
            
            # 计算连接速率
            connection_rate = self._calculate_connection_rate()
            
            return ConnectionMetrics(
                timestamp=datetime.now(),
                total_attempts=connection_data.get('total_attempts', 0),
                successful_connections=connection_data.get('successful_connections', 0),
                failed_connections=connection_data.get('failed_connections', 0),
                connection_times=connection_times,
                concurrent_connections=connection_data.get('concurrent_connections', 0),
                max_concurrent=connection_data.get('max_concurrent', 0),
                connection_rate=connection_rate,
                error_types=error_types,
                system_resources=system_resources
            )
            
        except Exception as e:
            print(f"❌ 收集指标时出错: {e}")
            return None
    
    def _fetch_prometheus_metrics(self) -> Optional[str]:
        """从Prometheus端点获取指标"""
        try:
            url = f"http://localhost:{self.prometheus_port}/metrics"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ Prometheus端点响应异常: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 无法连接到Prometheus端点: {e}")
            return None
    
    def _parse_connection_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """解析连接相关指标"""
        connection_data = {
            'total_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'concurrent_connections': 0,
            'max_concurrent': 0
        }
        
        lines = metrics_text.split('\n')
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            # 解析连接成功指标
            if 'mqtt_bench_connected' in line and 'counter' in line:
                try:
                    value = float(line.split()[-1])
                    connection_data['successful_connections'] = int(value)
                    connection_data['total_attempts'] += int(value)
                except (ValueError, IndexError):
                    pass
            
            # 解析连接失败指标
            elif 'connect_fail' in line and 'counter' in line:
                try:
                    value = float(line.split()[-1])
                    connection_data['failed_connections'] = int(value)
                    connection_data['total_attempts'] += int(value)
                except (ValueError, IndexError):
                    pass
            
            # 解析当前连接数
            elif 'connection_idle' in line and 'gauge' in line:
                try:
                    value = float(line.split()[-1])
                    connection_data['concurrent_connections'] = int(value)
                except (ValueError, IndexError):
                    pass
        
        return connection_data
    
    def _extract_connection_times(self, metrics_text: str) -> List[float]:
        """提取连接时间数据"""
        connection_times = []
        lines = metrics_text.split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            # 查找延迟相关指标
            if any(keyword in line for keyword in ['duration', 'latency', 'time']):
                try:
                    value = float(line.split()[-1])
                    if 0 < value < 10000:  # 合理的连接时间范围 (0-10秒)
                        connection_times.append(value)
                except (ValueError, IndexError):
                    pass
        
        return connection_times
    
    def _extract_error_types(self, metrics_text: str) -> Dict[str, int]:
        """提取错误类型分布"""
        error_types = defaultdict(int)
        lines = metrics_text.split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            # 解析各种错误类型
            if 'connect_fail' in line:
                try:
                    value = int(float(line.split()[-1]))
                    error_types['连接失败'] = value
                except (ValueError, IndexError):
                    pass
            elif 'pub_fail' in line:
                try:
                    value = int(float(line.split()[-1]))
                    error_types['发布失败'] = value
                except (ValueError, IndexError):
                    pass
            elif 'sub_fail' in line:
                try:
                    value = int(float(line.split()[-1]))
                    error_types['订阅失败'] = value
                except (ValueError, IndexError):
                    pass
        
        return dict(error_types)
    
    def _calculate_connection_rate(self) -> float:
        """计算连接建立速率"""
        if len(self.metrics_history) < 2:
            return 0.0
        
        # 计算最近两个数据点之间的连接速率
        recent_metrics = list(self.metrics_history)[-2:]
        if len(recent_metrics) == 2:
            time_diff = (recent_metrics[1].timestamp - recent_metrics[0].timestamp).total_seconds()
            connection_diff = recent_metrics[1].successful_connections - recent_metrics[0].successful_connections
            
            if time_diff > 0:
                return connection_diff / time_diff
        
        return 0.0
    
    def _get_system_resources(self) -> Dict[str, float]:
        """获取系统资源使用情况"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 文件描述符使用情况
            try:
                fd_count = len(psutil.Process().open_files())
                fd_limit = psutil.Process().rlimit(psutil.RLIMIT_NOFILE)[1]
                fd_percent = (fd_count / fd_limit) * 100 if fd_limit > 0 else 0
            except (OSError, AttributeError):
                fd_count = 0
                fd_percent = 0
            
            # 网络统计
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory_percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'file_descriptors_count': fd_count,
                'file_descriptors_percent': fd_percent,
                'network_bytes_sent': network_bytes_sent,
                'network_bytes_recv': network_bytes_recv
            }
        except Exception as e:
            print(f"⚠️ 获取系统资源信息失败: {e}")
            return {}
    
    def _update_performance_stats(self, metrics: ConnectionMetrics):
        """更新性能统计"""
        # 计算连接成功率
        if metrics.total_attempts > 0:
            self.performance_stats['connection_success_rate'] = (
                metrics.successful_connections / metrics.total_attempts * 100
            )
        
        # 计算平均连接时间
        if metrics.connection_times:
            self.performance_stats['avg_connection_time'] = statistics.mean(metrics.connection_times)
        
        # 更新连接速率
        self.performance_stats['connection_rate'] = metrics.connection_rate
        
        # 更新并发连接数
        self.performance_stats['current_concurrent_connections'] = metrics.concurrent_connections
        self.performance_stats['max_concurrent_connections'] = max(
            self.performance_stats['max_concurrent_connections'],
            metrics.concurrent_connections
        )
        
        # 计算错误率
        if metrics.total_attempts > 0:
            self.performance_stats['error_rate'] = (
                metrics.failed_connections / metrics.total_attempts * 100
            )
        
        # 更新系统资源使用情况
        self.performance_stats['system_resource_usage'] = metrics.system_resources
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        # 计算统计信息
        connection_times = []
        for metrics in self.metrics_history:
            connection_times.extend(metrics.connection_times)
        
        # 计算连接时间分布
        time_stats = {}
        if connection_times:
            time_stats = {
                'min': min(connection_times),
                'max': max(connection_times),
                'mean': statistics.mean(connection_times),
                'median': statistics.median(connection_times),
                'p90': self._calculate_percentile(connection_times, 90),
                'p95': self._calculate_percentile(connection_times, 95),
                'p99': self._calculate_percentile(connection_times, 99)
            }
        
        # 计算错误类型汇总
        total_errors = defaultdict(int)
        for metrics in self.metrics_history:
            for error_type, count in metrics.error_types.items():
                total_errors[error_type] += count
        
        return {
            'test_duration': (datetime.now() - self.start_time).total_seconds(),
            'total_metrics_collected': len(self.metrics_history),
            'performance_stats': self.performance_stats,
            'connection_time_stats': time_stats,
            'error_summary': dict(total_errors),
            'system_resource_summary': self._get_system_resource_summary()
        }
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _get_system_resource_summary(self) -> Dict[str, Any]:
        """获取系统资源摘要"""
        if not self.metrics_history:
            return {}
        
        cpu_values = []
        memory_values = []
        
        for metrics in self.metrics_history:
            if 'cpu_usage_percent' in metrics.system_resources:
                cpu_values.append(metrics.system_resources['cpu_usage_percent'])
            if 'memory_usage_percent' in metrics.system_resources:
                memory_values.append(metrics.system_resources['memory_usage_percent'])
        
        summary = {}
        if cpu_values:
            summary['cpu_usage'] = {
                'avg': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            }
        
        if memory_values:
            summary['memory_usage'] = {
                'avg': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            }
        
        return summary
    
    def export_metrics(self, output_file: str = None) -> str:
        """导出指标数据"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"connection_test_metrics_{timestamp}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'test_summary': self.get_performance_summary(),
            'metrics_history': [
                {
                    'timestamp': metrics.timestamp.isoformat(),
                    'total_attempts': metrics.total_attempts,
                    'successful_connections': metrics.successful_connections,
                    'failed_connections': metrics.failed_connections,
                    'concurrent_connections': metrics.concurrent_connections,
                    'connection_rate': metrics.connection_rate,
                    'error_types': metrics.error_types,
                    'system_resources': metrics.system_resources,
                    'connection_times_count': len(metrics.connection_times),
                    'avg_connection_time': statistics.mean(metrics.connection_times) if metrics.connection_times else 0
                }
                for metrics in self.metrics_history
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 连接测试指标已导出到: {output_file}")
        return output_file

def main():
    """测试函数"""
    collector = ConnectionTestMetricsCollector(9090)
    
    try:
        collector.start_collection(interval=2.0)
        
        # 运行30秒进行测试
        time.sleep(30)
        
        # 获取性能摘要
        summary = collector.get_performance_summary()
        print("\n📊 连接测试性能摘要:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
        # 导出指标
        output_file = collector.export_metrics()
        print(f"\n💾 指标数据已保存到: {output_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    finally:
        collector.stop_collection()

if __name__ == "__main__":
    main()
