#!/usr/bin/env python3
"""
eMQTT-Bench Prometheus Metrics Collector
抓取和分析 eMQTT-Bench 的 Prometheus 指标数据
作者: Jaxon
日期: 2024-12-19
"""

import requests
import time
import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

console = Console()

@dataclass
class MetricData:
    """指标数据结构"""
    timestamp: str
    name: str
    value: float
    labels: Dict[str, str]
    help_text: str
    metric_type: str

class PrometheusMetricsCollector:
    """Prometheus 指标收集器"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
    def fetch_metrics(self, port: int) -> List[MetricData]:
        """从指定端口抓取指标数据"""
        url = f"{self.base_url}:{port}/metrics"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return self._parse_metrics(response.text, port)
        except requests.RequestException as e:
            console.print(f"[red]错误: 无法连接到 {url}: {e}[/red]")
            return []
    
    def _parse_metrics(self, metrics_text: str, port: int) -> List[MetricData]:
        """解析 Prometheus 格式的指标数据"""
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
            metric = self._parse_metric_line(line, current_help, current_type, port)
            if metric:
                metrics.append(metric)
        
        return metrics
    
    def _parse_metric_line(self, line: str, help_text: str, metric_type: str, port: int) -> Optional[MetricData]:
        """解析单个指标行"""
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
        
        # 添加端口标签
        labels['port'] = str(port)
        
        try:
            value = float(value_str)
        except ValueError:
            return None
        
        return MetricData(
            timestamp=datetime.now().isoformat(),
            name=name,
            value=value,
            labels=labels,
            help_text=help_text,
            metric_type=metric_type
        )
    
    def collect_all_metrics(self, ports: List[int]) -> Dict[int, List[MetricData]]:
        """收集多个端口的指标数据"""
        all_metrics = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for port in ports:
                task = progress.add_task(f"收集端口 {port} 的指标...", total=None)
                metrics = self.fetch_metrics(port)
                all_metrics[port] = metrics
                progress.update(task, description=f"端口 {port}: 收集到 {len(metrics)} 个指标")
        
        return all_metrics

class MetricsAnalyzer:
    """指标数据分析器"""
    
    def __init__(self):
        self.mqtt_bench_metrics = [
            'mqtt_bench_connected',
            'mqtt_bench_connect_failed', 
            'mqtt_bench_disconnected',
            'mqtt_bench_publish_sent',
            'mqtt_bench_publish_received',
            'mqtt_bench_publish_failed',
            'mqtt_bench_subscribe_sent',
            'mqtt_bench_subscribe_received'
        ]
        
        self.latency_metrics = [
            'mqtt_client_tcp_handshake_duration',
            'mqtt_client_handshake_duration',
            'mqtt_client_connect_duration',
            'mqtt_client_subscribe_duration'
        ]
    
    def filter_mqtt_bench_metrics(self, metrics: List[MetricData]) -> List[MetricData]:
        """过滤出 eMQTT-Bench 相关的指标"""
        return [m for m in metrics if m.name in self.mqtt_bench_metrics or m.name in self.latency_metrics]
    
    def get_metric_summary(self, metrics: List[MetricData]) -> Dict[str, Dict]:
        """获取指标摘要"""
        summary = {}
        
        for metric in metrics:
            if metric.name not in summary:
                summary[metric.name] = {
                    'help': metric.help_text,
                    'type': metric.metric_type,
                    'values': [],
                    'labels': set()
                }
            
            summary[metric.name]['values'].append(metric.value)
            summary[metric.name]['labels'].update(metric.labels.keys())
        
        # 计算统计信息
        for name, data in summary.items():
            values = data['values']
            if values:
                data['count'] = len(values)
                data['sum'] = sum(values)
                data['avg'] = sum(values) / len(values)
                data['min'] = min(values)
                data['max'] = max(values)
                data['labels'] = list(data['labels'])
        
        return summary
    
    def display_summary_table(self, summary: Dict[str, Dict], port: int):
        """显示指标摘要表格"""
        table = Table(title=f"端口 {port} - eMQTT-Bench 指标摘要")
        table.add_column("指标名称", style="cyan")
        table.add_column("类型", style="green")
        table.add_column("数量", justify="right")
        table.add_column("总和", justify="right")
        table.add_column("平均值", justify="right")
        table.add_column("最小值", justify="right")
        table.add_column("最大值", justify="right")
        
        for name, data in summary.items():
            table.add_row(
                name,
                data['type'],
                str(data.get('count', 0)),
                f"{data.get('sum', 0):.2f}",
                f"{data.get('avg', 0):.2f}",
                f"{data.get('min', 0):.2f}",
                f"{data.get('max', 0):.2f}"
            )
        
        console.print(table)

class MetricsExporter:
    """指标数据导出器"""
    
    def __init__(self, output_dir: str = "metrics_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, all_metrics: Dict[int, List[MetricData]], filename: Optional[str] = None):
        """导出为 JSON 格式"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        # 转换为可序列化的格式
        export_data = {}
        for port, metrics in all_metrics.items():
            export_data[str(port)] = [asdict(metric) for metric in metrics]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]指标数据已导出到: {filepath}[/green]")
        return filepath
    
    def export_to_csv(self, all_metrics: Dict[int, List[MetricData]], filename: Optional[str] = None):
        """导出为 CSV 格式"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'port', 'name', 'value', 'labels', 'help_text', 'metric_type'])
            
            for port, metrics in all_metrics.items():
                for metric in metrics:
                    writer.writerow([
                        metric.timestamp,
                        port,
                        metric.name,
                        metric.value,
                        json.dumps(metric.labels, ensure_ascii=False),
                        metric.help_text,
                        metric.metric_type
                    ])
        
        console.print(f"[green]指标数据已导出到: {filepath}[/green]")
        return filepath

@click.group()
def cli():
    """eMQTT-Bench Prometheus 指标收集工具"""
    pass

@cli.command()
@click.option('--ports', '-p', multiple=True, type=int, default=[8080, 8081, 8082, 8083],
              help='要收集指标的端口列表')
@click.option('--host', '-h', default='localhost', help='目标主机地址')
@click.option('--output-dir', '-o', default='metrics_data', help='输出目录')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'both']), default='both',
              help='输出格式')
@click.option('--summary', '-s', is_flag=True, help='显示指标摘要')
def collect(ports, host, output_dir, format, summary):
    """收集 eMQTT-Bench 的 Prometheus 指标数据"""
    
    console.print(Panel.fit(
        f"[bold blue]eMQTT-Bench 指标收集器[/bold blue]\n"
        f"目标主机: {host}\n"
        f"端口列表: {list(ports)}\n"
        f"输出目录: {output_dir}\n"
        f"输出格式: {format}",
        title="配置信息"
    ))
    
    # 创建收集器
    collector = PrometheusMetricsCollector(host)
    analyzer = MetricsAnalyzer()
    exporter = MetricsExporter(output_dir)
    
    # 收集指标
    console.print("\n[bold]开始收集指标数据...[/bold]")
    all_metrics = collector.collect_all_metrics(list(ports))
    
    # 过滤和分析
    filtered_metrics = {}
    for port, metrics in all_metrics.items():
        filtered = analyzer.filter_mqtt_bench_metrics(metrics)
        filtered_metrics[port] = filtered
        
        if summary and filtered:
            summary_data = analyzer.get_metric_summary(filtered)
            analyzer.display_summary_table(summary_data, port)
    
    # 导出数据
    if format in ['json', 'both']:
        exporter.export_to_json(filtered_metrics)
    
    if format in ['csv', 'both']:
        exporter.export_to_csv(filtered_metrics)
    
    # 显示统计信息
    total_metrics = sum(len(metrics) for metrics in filtered_metrics.values())
    console.print(f"\n[green]收集完成! 总共收集到 {total_metrics} 个 eMQTT-Bench 指标[/green]")

@cli.command()
@click.option('--port', '-p', type=int, default=8080, help='监控端口')
@click.option('--host', '-h', default='localhost', help='目标主机地址')
@click.option('--interval', '-i', type=int, default=5, help='监控间隔(秒)')
@click.option('--duration', '-d', type=int, help='监控持续时间(秒)')
def monitor(port, host, interval, duration):
    """实时监控 eMQTT-Bench 指标"""
    
    console.print(Panel.fit(
        f"[bold blue]eMQTT-Bench 实时监控[/bold blue]\n"
        f"目标: {host}:{port}\n"
        f"间隔: {interval}秒\n"
        f"持续时间: {duration or '无限'}",
        title="监控配置"
    ))
    
    collector = PrometheusMetricsCollector(host)
    analyzer = MetricsAnalyzer()
    
    start_time = time.time()
    
    try:
        while True:
            # 收集指标
            metrics = collector.fetch_metrics(port)
            filtered = analyzer.filter_mqtt_bench_metrics(metrics)
            
            if filtered:
                summary = analyzer.get_metric_summary(filtered)
                
                # 显示关键指标
                console.print(f"\n[bold]时间: {datetime.now().strftime('%H:%M:%S')}[/bold]")
                
                key_metrics = ['mqtt_bench_connected', 'mqtt_bench_publish_sent', 'mqtt_bench_publish_failed']
                for metric_name in key_metrics:
                    if metric_name in summary:
                        data = summary[metric_name]
                        console.print(f"  {metric_name}: {data.get('sum', 0):.0f}")
            else:
                console.print(f"[yellow]未找到 eMQTT-Bench 指标数据[/yellow]")
            
            # 检查是否超时
            if duration and (time.time() - start_time) >= duration:
                break
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]监控已停止[/yellow]")

@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
def analyze(json_file):
    """分析已保存的指标数据"""
    
    console.print(f"[bold]分析文件: {json_file}[/bold]")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analyzer = MetricsAnalyzer()
    
    for port_str, metrics_data in data.items():
        port = int(port_str)
        metrics = [MetricData(**m) for m in metrics_data]
        filtered = analyzer.filter_mqtt_bench_metrics(metrics)
        
        if filtered:
            summary = analyzer.get_metric_summary(filtered)
            analyzer.display_summary_table(summary, port)

if __name__ == '__main__':
    cli()
