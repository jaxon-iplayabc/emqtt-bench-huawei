#!/usr/bin/env python3
"""
通用持续指标收集器
为所有测试类型提供持续的数据收集功能
作者: Jaxon
日期: 2025-09-28
"""

import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
from pathlib import Path
import requests
from rich.console import Console

console = Console()

@dataclass
class ContinuousMetricData:
    """持续指标数据结构"""
    timestamp: str
    test_name: str
    port: int
    metrics: List[Dict[str, Any]]
    performance_stats: Dict[str, Any]
    system_resources: Dict[str, Any]

class ContinuousMetricsCollector:
    """通用持续指标收集器"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 5
        
        # 收集状态
        self.running = False
        self.collection_threads: Dict[str, threading.Thread] = {}
        self.metrics_history: Dict[str, deque] = {}
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # 配置
        self.max_history_points = 1000  # 每个测试最多保留1000个数据点
        self.default_interval = 1.0  # 默认收集间隔1秒
        
    def start_collection(self, test_name: str, port: int, interval: float = None) -> bool:
        """开始为指定测试收集指标"""
        if interval is None:
            interval = self.default_interval
            
        if test_name in self.collection_threads:
            console.print(f"[yellow]⚠️ 测试 {test_name} 的指标收集已在运行[/yellow]")
            return False
            
        # 初始化测试数据存储
        self.metrics_history[test_name] = deque(maxlen=self.max_history_points)
        self.performance_stats[test_name] = {
            'start_time': datetime.now(),
            'total_metrics_collected': 0,
            'last_collection_time': None,
            'collection_errors': 0
        }
        
        # 启动收集线程
        self.running = True
        thread = threading.Thread(
            target=self._collection_loop,
            args=(test_name, port, interval),
            daemon=True
        )
        self.collection_threads[test_name] = thread
        thread.start()
        
        console.print(f"🔍 [green]开始持续收集 {test_name} 指标 (端口: {port}, 间隔: {interval}s)[/green]")
        return True
    
    def stop_collection(self, test_name: str) -> bool:
        """停止指定测试的指标收集"""
        if test_name not in self.collection_threads:
            console.print(f"[yellow]⚠️ 测试 {test_name} 的指标收集未在运行[/yellow]")
            return False
            
        # 标记停止
        self.running = False
        
        # 等待线程结束
        thread = self.collection_threads[test_name]
        thread.join(timeout=2)
        
        # 清理
        del self.collection_threads[test_name]
        # if test_name in self.metrics_history:
        #     del self.metrics_history[test_name]
        # if test_name in self.performance_stats:
        #     del self.performance_stats[test_name]
            
        console.print(f"⏹️ [blue]停止收集 {test_name} 指标[/blue]")
        return True
    
    def stop_all_collections(self):
        """停止所有测试的指标收集"""
        test_names = list(self.collection_threads.keys())
        for test_name in test_names:
            self.stop_collection(test_name)
        console.print("⏹️ [blue]已停止所有指标收集[/blue]")
    
    def _collection_loop(self, test_name: str, port: int, interval: float):
        """指标收集循环"""
        while self.running and test_name in self.collection_threads:
            try:
                # 收集指标
                metrics_data = self._collect_single_metrics(test_name, port)
                if metrics_data:
                    # 存储到历史数据
                    self.metrics_history[test_name].append(metrics_data)
                    
                    # 更新性能统计
                    self._update_performance_stats(test_name, metrics_data)
                    
                    # 显示收集状态
                    if len(self.metrics_history[test_name]) % 10 == 0:  # 每10次显示一次
                        console.print(f"📊 [dim]{test_name}: 已收集 {len(self.metrics_history[test_name])} 个数据点[/dim]")
                
                time.sleep(interval)
                
            except Exception as e:
                console.print(f"❌ [red]{test_name} 指标收集错误: {e}[/red]")
                if test_name in self.performance_stats:
                    self.performance_stats[test_name]['collection_errors'] += 1
                time.sleep(interval)
    
    def _collect_single_metrics(self, test_name: str, port: int) -> Optional[ContinuousMetricData]:
        """收集单次指标数据"""
        try:
            # 从Prometheus端点获取指标
            url = f"{self.base_url}:{port}/metrics"
            response = self.session.get(url)
            response.raise_for_status()

            # 解析指标
            metrics = self._parse_metrics(response.text)
            # print('[DEBUG]', test_name, response.text)
            if not metrics:
                return None
            
            # 获取系统资源
            system_resources = self._get_system_resources()
            
            # 计算性能统计
            performance_stats = self._calculate_performance_stats(metrics)
            
            return ContinuousMetricData(
                timestamp=datetime.now().isoformat(),
                test_name=test_name,
                port=port,
                metrics=metrics,
                performance_stats=performance_stats,
                system_resources=system_resources
            )
            
        except Exception as e:
            console.print(f"❌ [red]收集 {test_name} 指标失败: {e}[/red]")
            return None
    
    def _parse_metrics(self, metrics_text: str) -> List[Dict[str, Any]]:
        """解析Prometheus格式的指标数据"""
        metrics = []
        current_help = ""
        current_type = ""
        
        for line in metrics_text.strip().split('\n'):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                if line.startswith('# HELP'):
                    current_help = line[7:].strip()
                elif line.startswith('# TYPE'):
                    current_type = line[7:].strip()
                continue
            
            # 解析指标行
            metric = self._parse_metric_line(line, current_help, current_type)
            if metric:
                metrics.append(metric)
        
        return metrics
    
    def _parse_metric_line(self, line: str, help_text: str, metric_type: str) -> Optional[Dict[str, Any]]:
        """解析单个指标行"""
        import re
        
        # 匹配指标格式: name{labels} value
        pattern = r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+(.+)$'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        name = match.group(1)
        labels_str = match.group(2) or ""
        value_str = match.group(3)
        
        # 解析标签
        labels = {}
        if labels_str:
            for label_pair in labels_str.split(','):
                if '=' in label_pair:
                    key, val = label_pair.split('=', 1)
                    labels[key.strip()] = val.strip().strip('"')
        
        # 解析值
        try:
            value = float(value_str)
        except ValueError:
            value = 0.0
        
        return {
            'name': name,
            'value': value,
            'labels': labels,
            'help_text': help_text,
            'metric_type': metric_type
        }
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict() if hasattr(psutil.net_io_counters(), '_asdict') else {}
            }
        except ImportError:
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0,
                'network_io': {}
            }
    
    def _calculate_performance_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算性能统计"""
        stats = {
            'total_metrics': len(metrics),
            'connection_metrics': 0,
            'publish_metrics': 0,
            'subscribe_metrics': 0,
            'error_metrics': 0,
            'latency_metrics': 0,
            'system_metrics': 0
        }
        
        for metric in metrics:
            name = metric.get('name', '').lower()
            
            # 连接相关指标（精确匹配）
            if name in ['connect_succ', 'connect_retried', 'reconnect_succ', 'connection_idle']:
                stats['connection_metrics'] += 1
            # 发布相关指标
            elif name in ['pub', 'pub_succ', 'pub_overrun', 'publish_latency']:
                stats['publish_metrics'] += 1
            # 订阅相关指标
            elif name in ['sub', 'recv']:
                stats['subscribe_metrics'] += 1
            # 错误相关指标
            elif name in ['connect_fail', 'pub_fail', 'sub_fail', 'unreachable', 
                          'connection_refused', 'connection_timeout']:
                stats['error_metrics'] += 1
            # 延迟相关指标（直方图）
            elif 'duration' in name or 'latency' in name or name == 'e2e_latency':
                stats['latency_metrics'] += 1
            # 系统资源指标
            elif name.startswith('erlang_vm_') or name.startswith('system_'):
                stats['system_metrics'] += 1
        
        return stats
    
    def _update_performance_stats(self, test_name: str, metrics_data: ContinuousMetricData):
        """更新性能统计"""
        if test_name not in self.performance_stats:
            return
            
        stats = self.performance_stats[test_name]
        stats['total_metrics_collected'] += 1
        stats['last_collection_time'] = metrics_data.timestamp
    
    def get_test_history(self, test_name: str) -> List[ContinuousMetricData]:
        """获取指定测试的历史数据"""
        if test_name not in self.metrics_history:
            return []
        return list(self.metrics_history[test_name])
    
    def get_test_summary(self, test_name: str) -> Dict[str, Any]:
        """获取指定测试的摘要信息"""
        if test_name not in self.performance_stats:
            return {}
            
        stats = self.performance_stats[test_name]
        history = self.get_test_history(test_name)
        
        return {
            'test_name': test_name,
            'start_time': stats['start_time'],
            'total_collections': stats['total_metrics_collected'],
            'last_collection': stats['last_collection_time'],
            'collection_errors': stats['collection_errors'],
            'history_points': len(history),
            'is_running': test_name in self.collection_threads
        }
    
    def save_test_data(self, test_name: str, output_dir: str = "reports") -> str:
        """保存测试数据到文件"""
        if test_name not in self.metrics_history:
            return ""
            
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取历史数据
        history = self.get_test_history(test_name)
        if not history:
            return ""
        
        # 转换为可序列化格式
        serializable_data = []
        for data_point in history:
            serializable_data.append({
                'timestamp': data_point.timestamp,
                'test_name': data_point.test_name,
                'port': data_point.port,
                'metrics': data_point.metrics,
                'performance_stats': data_point.performance_stats,
                'system_resources': data_point.system_resources
            })
        
        # 保存到文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"continuous_metrics_{test_name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"💾 [green]已保存 {test_name} 持续指标数据: {filepath} ({len(history)} 个数据点)[/green]")
        return filepath
    
    def get_all_summaries(self) -> Dict[str, Dict[str, Any]]:
        """获取所有测试的摘要信息"""
        summaries = {}
        for test_name in self.performance_stats:
            summaries[test_name] = self.get_test_summary(test_name)
        return summaries
