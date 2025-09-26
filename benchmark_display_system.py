#!/usr/bin/env python3
"""
eMQTT-Bench 压测结果显示系统
提供实时监控、详细分析和可视化展示
作者: Jaxon
日期: 2025-01-27
"""

import json
import time
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np

console = Console()

@dataclass
class BenchmarkMetrics:
    """压测指标数据结构"""
    timestamp: str
    test_type: str  # conn, pub, sub
    connection_metrics: Dict[str, float]
    message_metrics: Dict[str, float]
    latency_metrics: Dict[str, float]
    error_metrics: Dict[str, float]
    system_metrics: Dict[str, float]

@dataclass
class TestConfig:
    """测试配置"""
    host: str
    port: int
    client_count: int
    message_interval: int
    test_duration: int
    prometheus_port: int

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, prometheus_ports: List[int]):
        self.prometheus_ports = prometheus_ports
        self.session = requests.Session()
        self.session.timeout = 5
        self.metrics_history: List[BenchmarkMetrics] = []
        
    def collect_metrics(self, test_type: str = "conn") -> Optional[BenchmarkMetrics]:
        """收集当前指标数据"""
        try:
            # 从Prometheus端点收集指标
            prometheus_data = {}
            for port in self.prometheus_ports:
                try:
                    response = self.session.get(f"http://localhost:{port}/metrics")
                    if response.status_code == 200:
                        prometheus_data[port] = self._parse_prometheus_metrics(response.text)
                except requests.RequestException:
                    continue
            
            if not prometheus_data:
                return None
                
            # 解析指标数据
            metrics = self._extract_metrics(prometheus_data, test_type)
            if metrics:
                self.metrics_history.append(metrics)
                # 保持最近1000条记录
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            console.print(f"[red]收集指标时出错: {e}[/red]")
            return None
    
    def _parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, float]:
        """解析Prometheus格式的指标"""
        metrics = {}
        for line in metrics_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 解析指标行: name{labels} value
            parts = line.split()
            if len(parts) >= 2:
                name_part = parts[0]
                value_str = parts[1]
                
                # 提取指标名称（去掉标签部分）
                if '{' in name_part:
                    name = name_part.split('{')[0]
                else:
                    name = name_part
                
                try:
                    value = float(value_str)
                    metrics[name] = value
                except ValueError:
                    continue
        
        return metrics
    
    def _extract_metrics(self, prometheus_data: Dict[int, Dict[str, float]], test_type: str) -> Optional[BenchmarkMetrics]:
        """从Prometheus数据中提取关键指标"""
        # 合并所有端口的数据
        all_metrics = {}
        for port_data in prometheus_data.values():
            all_metrics.update(port_data)
        
        if not all_metrics:
            return None
        
        # 提取连接指标
        connection_metrics = {
            'connect_succ': all_metrics.get('connect_succ', 0),
            'connect_fail': all_metrics.get('connect_fail', 0),
            'connect_retried': all_metrics.get('connect_retried', 0),
            'reconnect_succ': all_metrics.get('reconnect_succ', 0),
            'connection_refused': all_metrics.get('connection_refused', 0),
            'connection_timeout': all_metrics.get('connection_timeout', 0),
            'unreachable': all_metrics.get('unreachable', 0)
        }
        
        # 提取消息指标
        message_metrics = {
            'pub': all_metrics.get('pub', 0),
            'pub_fail': all_metrics.get('pub_fail', 0),
            'pub_succ': all_metrics.get('pub_succ', 0),
            'recv': all_metrics.get('recv', 0),
            'sub': all_metrics.get('sub', 0),
            'sub_fail': all_metrics.get('sub_fail', 0),
            'pub_overrun': all_metrics.get('pub_overrun', 0)
        }
        
        # 提取延迟指标
        latency_metrics = {
            'publish_latency': all_metrics.get('publish_latency', 0),
            'mqtt_client_tcp_handshake_duration': all_metrics.get('mqtt_client_tcp_handshake_duration', 0),
            'mqtt_client_handshake_duration': all_metrics.get('mqtt_client_handshake_duration', 0),
            'mqtt_client_connect_duration': all_metrics.get('mqtt_client_connect_duration', 0),
            'mqtt_client_subscribe_duration': all_metrics.get('mqtt_client_subscribe_duration', 0),
            'e2e_latency': all_metrics.get('e2e_latency', 0)
        }
        
        # 计算系统指标（模拟）
        system_metrics = {
            'cpu_usage': 0,  # 需要从系统监控获取
            'memory_usage': 0,  # 需要从系统监控获取
            'network_usage': 0,  # 需要从系统监控获取
            'active_connections': connection_metrics['connect_succ'] - connection_metrics['connect_fail']
        }
        
        return BenchmarkMetrics(
            timestamp=datetime.now().isoformat(),
            test_type=test_type,
            connection_metrics=connection_metrics,
            message_metrics=message_metrics,
            latency_metrics=latency_metrics,
            error_metrics={
                'total_errors': connection_metrics['connect_fail'] + message_metrics['pub_fail'] + message_metrics['sub_fail'],
                'error_rate': 0  # 需要计算
            },
            system_metrics=system_metrics
        )

class RealTimeDisplay:
    """实时显示系统"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.running = False
        
    def start_live_display(self, test_type: str = "conn", refresh_interval: float = 1.0):
        """启动实时显示"""
        self.running = True
        
        def update_display():
            while self.running:
                try:
                    metrics = self.collector.collect_metrics(test_type)
                    if metrics:
                        self._display_metrics(metrics)
                    time.sleep(refresh_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[red]显示更新错误: {e}[/red]")
                    time.sleep(refresh_interval)
        
        # 启动显示线程
        display_thread = threading.Thread(target=update_display, daemon=True)
        display_thread.start()
        
        try:
            # 主线程等待
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            console.print("\n[yellow]实时显示已停止[/yellow]")
    
    def _display_metrics(self, metrics: BenchmarkMetrics):
        """显示指标数据"""
        # 清屏
        console.clear()
        
        # 创建布局
        layout = Layout()
        layout.split_column(
            Layout(Panel(self._create_header(metrics), title="eMQTT-Bench 实时监控", border_style="blue"), size=3),
            Layout(self._create_metrics_table(metrics), size=15),
            Layout(self._create_status_panel(metrics), size=8)
        )
        
        console.print(layout)
    
    def _create_header(self, metrics: BenchmarkMetrics) -> Text:
        """创建头部信息"""
        timestamp = datetime.fromisoformat(metrics.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        test_type_map = {"conn": "连接测试", "pub": "发布测试", "sub": "订阅测试"}
        test_name = test_type_map.get(metrics.test_type, metrics.test_type)
        
        return Text(f"测试类型: {test_name} | 时间: {timestamp} | 状态: 运行中", style="bold white")
    
    def _create_metrics_table(self, metrics: BenchmarkMetrics) -> Table:
        """创建指标表格"""
        table = Table(title="实时性能指标", box=box.ROUNDED)
        
        # 添加列
        table.add_column("指标类别", style="cyan", no_wrap=True)
        table.add_column("指标名称", style="magenta")
        table.add_column("当前值", style="green", justify="right")
        table.add_column("状态", style="yellow")
        
        # 连接指标
        conn_metrics = metrics.connection_metrics
        success_rate = self._calculate_success_rate(conn_metrics['connect_succ'], conn_metrics['connect_fail'])
        table.add_row(
            "连接性能",
            "连接成功率",
            f"{success_rate:.1f}%",
            "🟢" if success_rate > 95 else "🟡" if success_rate > 80 else "🔴"
        )
        table.add_row(
            "",
            "成功连接数",
            f"{int(conn_metrics['connect_succ'])}",
            "🟢"
        )
        table.add_row(
            "",
            "失败连接数",
            f"{int(conn_metrics['connect_fail'])}",
            "🔴" if conn_metrics['connect_fail'] > 0 else "🟢"
        )
        table.add_row(
            "",
            "活跃连接数",
            f"{int(metrics.system_metrics['active_connections'])}",
            "🟢"
        )
        
        # 消息指标
        msg_metrics = metrics.message_metrics
        table.add_row(
            "消息性能",
            "发送消息数",
            f"{int(msg_metrics['pub'])}",
            "🟢"
        )
        table.add_row(
            "",
            "接收消息数",
            f"{int(msg_metrics['recv'])}",
            "🟢"
        )
        table.add_row(
            "",
            "发送失败数",
            f"{int(msg_metrics['pub_fail'])}",
            "🔴" if msg_metrics['pub_fail'] > 0 else "🟢"
        )
        table.add_row(
            "",
            "消息丢失数",
            f"{int(msg_metrics['pub_overrun'])}",
            "🔴" if msg_metrics['pub_overrun'] > 0 else "🟢"
        )
        
        # 延迟指标
        latency_metrics = metrics.latency_metrics
        avg_latency = latency_metrics['publish_latency']
        table.add_row(
            "延迟性能",
            "平均延迟",
            f"{avg_latency:.1f}ms",
            "🟢" if avg_latency < 100 else "🟡" if avg_latency < 500 else "🔴"
        )
        table.add_row(
            "",
            "连接延迟",
            f"{latency_metrics['mqtt_client_connect_duration']:.1f}ms",
            "🟢" if latency_metrics['mqtt_client_connect_duration'] < 1000 else "🟡"
        )
        table.add_row(
            "",
            "端到端延迟",
            f"{latency_metrics['e2e_latency']:.1f}ms",
            "🟢" if latency_metrics['e2e_latency'] < 200 else "🟡"
        )
        
        return table
    
    def _create_status_panel(self, metrics: BenchmarkMetrics) -> Panel:
        """创建状态面板"""
        # 计算性能评级
        rating = self._calculate_performance_rating(metrics)
        
        # 创建状态文本
        status_text = f"""
性能评级: {rating['grade']} ({rating['score']}/100)
连接稳定性: {'优秀' if rating['connection_stability'] > 0.95 else '良好' if rating['connection_stability'] > 0.8 else '需要改进'}
消息吞吐量: {'高' if rating['throughput'] > 1000 else '中等' if rating['throughput'] > 100 else '低'}
延迟表现: {'优秀' if rating['latency'] < 100 else '良好' if rating['latency'] < 500 else '需要优化'}

建议: {rating['recommendation']}
        """.strip()
        
        return Panel(status_text, title="性能评估", border_style="green")
    
    def _calculate_success_rate(self, success: float, failed: float) -> float:
        """计算成功率"""
        total = success + failed
        return (success / total * 100) if total > 0 else 0
    
    def _calculate_performance_rating(self, metrics: BenchmarkMetrics) -> Dict[str, Any]:
        """计算性能评级"""
        # 连接稳定性评分 (0-30分)
        success_rate = self._calculate_success_rate(
            metrics.connection_metrics['connect_succ'],
            metrics.connection_metrics['connect_fail']
        )
        connection_score = min(30, success_rate * 0.3)
        
        # 消息吞吐量评分 (0-30分)
        throughput = metrics.message_metrics['pub'] + metrics.message_metrics['recv']
        throughput_score = min(30, throughput / 1000 * 30)
        
        # 延迟性能评分 (0-40分)
        avg_latency = metrics.latency_metrics['publish_latency']
        latency_score = max(0, 40 - (avg_latency / 100 * 40))
        
        total_score = connection_score + throughput_score + latency_score
        
        # 确定等级
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B+"
        elif total_score >= 60:
            grade = "B"
        elif total_score >= 50:
            grade = "C"
        else:
            grade = "D"
        
        # 生成建议
        recommendations = []
        if success_rate < 95:
            recommendations.append("检查网络连接和服务器配置")
        if avg_latency > 500:
            recommendations.append("优化网络延迟或减少并发连接数")
        if throughput < 100:
            recommendations.append("增加消息发送频率或优化消息大小")
        
        recommendation = "; ".join(recommendations) if recommendations else "性能表现良好"
        
        return {
            'score': int(total_score),
            'grade': grade,
            'connection_stability': success_rate / 100,
            'throughput': throughput,
            'latency': avg_latency,
            'recommendation': recommendation
        }

class WebDashboard:
    """Web仪表盘"""
    
    def __init__(self, collector: MetricsCollector, port: int = 8080):
        self.collector = collector
        self.port = port
        self.server = None
        
    def start_dashboard(self):
        """启动Web仪表盘"""
        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self._serve_dashboard()
                elif self.path == '/api/metrics':
                    self._serve_metrics_api()
                elif self.path.startswith('/api/history'):
                    self._serve_history_api()
                else:
                    self.send_error(404)
            
            def _serve_dashboard(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html_content = self._generate_dashboard_html()
                self.wfile.write(html_content.encode('utf-8'))
            
            def _serve_metrics_api(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                metrics = self.collector.collect_metrics()
                if metrics:
                    response = asdict(metrics)
                else:
                    response = {"error": "No metrics available"}
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            def _serve_history_api(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 返回最近100条历史数据
                history = self.collector.metrics_history[-100:] if self.collector.metrics_history else []
                response = [asdict(metric) for metric in history]
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            def log_message(self, format, *args):
                # 禁用默认日志输出
                pass
        
        try:
            self.server = HTTPServer(('localhost', self.port), DashboardHandler)
            console.print(f"[green]Web仪表盘已启动: http://localhost:{self.port}[/green]")
            
            # 自动打开浏览器
            webbrowser.open(f'http://localhost:{self.port}')
            
            self.server.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Web仪表盘已停止[/yellow]")
        except Exception as e:
            console.print(f"[red]启动Web仪表盘失败: {e}[/red]")
    
    def _generate_dashboard_html(self) -> str:
        """生成仪表盘HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eMQTT-Bench 压测监控仪表盘</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            padding: 30px; 
        }
        .metric-card { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-title { 
            font-size: 1.3em; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 15px; 
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .metric-item { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .metric-label { color: #7f8c8d; }
        .metric-value { 
            font-weight: bold; 
            color: #2c3e50; 
        }
        .status-good { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .chart-container { 
            margin: 20px 0; 
            height: 300px; 
            position: relative;
        }
        .loading { 
            text-align: center; 
            padding: 50px; 
            color: #7f8c8d; 
        }
        .refresh-info { 
            text-align: center; 
            padding: 20px; 
            color: #7f8c8d; 
            font-size: 0.9em; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 eMQTT-Bench 压测监控</h1>
            <p>实时性能指标监控与分析</p>
        </div>
        
        <div class="metrics-grid" id="metricsGrid">
            <div class="loading">
                <h3>正在加载指标数据...</h3>
                <p>请确保 eMQTT-Bench 正在运行并启用了 Prometheus 监控</p>
            </div>
        </div>
        
        <div class="refresh-info">
            数据每5秒自动刷新 | 最后更新: <span id="lastUpdate">-</span>
        </div>
    </div>

    <script>
        let metricsData = null;
        let charts = {};

        // 页面加载完成后开始获取数据
        document.addEventListener('DOMContentLoaded', function() {
            loadMetrics();
            setInterval(loadMetrics, 5000); // 每5秒刷新一次
        });

        async function loadMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                metricsData = data;
                updateDisplay();
                updateLastUpdateTime();
            } catch (error) {
                console.error('加载指标失败:', error);
                showError('无法连接到监控服务');
            }
        }

        function updateDisplay() {
            if (!metricsData) return;

            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = '';

            // 连接性能卡片
            const connectionCard = createMetricCard('连接性能', [
                { label: '成功连接', value: formatNumber(metricsData.connection_metrics.connect_succ), status: 'good' },
                { label: '失败连接', value: formatNumber(metricsData.connection_metrics.connect_fail), status: 'error' },
                { label: '重连次数', value: formatNumber(metricsData.connection_metrics.connect_retried), status: 'warning' },
                { label: '连接超时', value: formatNumber(metricsData.connection_metrics.connection_timeout), status: 'error' },
                { label: '连接被拒', value: formatNumber(metricsData.connection_metrics.connection_refused), status: 'error' }
            ]);
            grid.appendChild(connectionCard);

            // 消息性能卡片
            const messageCard = createMetricCard('消息性能', [
                { label: '发送消息', value: formatNumber(metricsData.message_metrics.pub), status: 'good' },
                { label: '接收消息', value: formatNumber(metricsData.message_metrics.recv), status: 'good' },
                { label: '发送失败', value: formatNumber(metricsData.message_metrics.pub_fail), status: 'error' },
                { label: '订阅成功', value: formatNumber(metricsData.message_metrics.sub), status: 'good' },
                { label: '订阅失败', value: formatNumber(metricsData.message_metrics.sub_fail), status: 'error' },
                { label: '消息溢出', value: formatNumber(metricsData.message_metrics.pub_overrun), status: 'error' }
            ]);
            grid.appendChild(messageCard);

            // 延迟性能卡片
            const latencyCard = createMetricCard('延迟性能', [
                { label: '平均延迟', value: formatLatency(metricsData.latency_metrics.publish_latency), status: getLatencyStatus(metricsData.latency_metrics.publish_latency) },
                { label: '连接延迟', value: formatLatency(metricsData.latency_metrics.mqtt_client_connect_duration), status: getLatencyStatus(metricsData.latency_metrics.mqtt_client_connect_duration) },
                { label: '握手延迟', value: formatLatency(metricsData.latency_metrics.mqtt_client_handshake_duration), status: getLatencyStatus(metricsData.latency_metrics.mqtt_client_handshake_duration) },
                { label: '订阅延迟', value: formatLatency(metricsData.latency_metrics.mqtt_client_subscribe_duration), status: getLatencyStatus(metricsData.latency_metrics.mqtt_client_subscribe_duration) },
                { label: '端到端延迟', value: formatLatency(metricsData.latency_metrics.e2e_latency), status: getLatencyStatus(metricsData.latency_metrics.e2e_latency) }
            ]);
            grid.appendChild(latencyCard);

            // 系统性能卡片
            const systemCard = createMetricCard('系统性能', [
                { label: '活跃连接', value: formatNumber(metricsData.system_metrics.active_connections), status: 'good' },
                { label: '总错误数', value: formatNumber(metricsData.error_metrics.total_errors), status: metricsData.error_metrics.total_errors > 0 ? 'error' : 'good' },
                { label: '错误率', value: formatPercentage(metricsData.error_metrics.error_rate), status: metricsData.error_metrics.error_rate > 5 ? 'error' : 'good' }
            ]);
            grid.appendChild(systemCard);
        }

        function createMetricCard(title, metrics) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            
            const titleEl = document.createElement('div');
            titleEl.className = 'metric-title';
            titleEl.textContent = title;
            card.appendChild(titleEl);

            metrics.forEach(metric => {
                const item = document.createElement('div');
                item.className = 'metric-item';
                
                const label = document.createElement('span');
                label.className = 'metric-label';
                label.textContent = metric.label;
                
                const value = document.createElement('span');
                value.className = `metric-value status-${metric.status}`;
                value.textContent = metric.value;
                
                item.appendChild(label);
                item.appendChild(value);
                card.appendChild(item);
            });

            return card;
        }

        function formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return Math.round(num).toString();
        }

        function formatLatency(ms) {
            if (ms >= 1000) {
                return (ms / 1000).toFixed(2) + 's';
            }
            return ms.toFixed(1) + 'ms';
        }

        function formatPercentage(percent) {
            return percent.toFixed(1) + '%';
        }

        function getLatencyStatus(ms) {
            if (ms < 100) return 'good';
            if (ms < 500) return 'warning';
            return 'error';
        }

        function updateLastUpdateTime() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
        }

        function showError(message) {
            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = `
                <div class="loading">
                    <h3 style="color: #e74c3c;">❌ ${message}</h3>
                    <p>请检查 eMQTT-Bench 是否正在运行，以及 Prometheus 监控是否已启用</p>
                </div>
            `;
        }
    </script>
</body>
</html>
        """

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成详细测试报告"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"benchmark_report_{timestamp}.html"
        
        # 收集当前指标
        current_metrics = self.collector.collect_metrics()
        if not current_metrics:
            console.print("[red]无法获取指标数据，请确保 eMQTT-Bench 正在运行[/red]")
            return ""
        
        # 分析历史数据
        analysis = self._analyze_metrics_history()
        
        # 生成HTML报告
        html_content = self._generate_report_html(current_metrics, analysis)
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]测试报告已生成: {output_file}[/green]")
        return output_file
    
    def _analyze_metrics_history(self) -> Dict[str, Any]:
        """分析历史指标数据"""
        if not self.collector.metrics_history:
            return {}
        
        # 计算趋势和统计信息
        history = self.collector.metrics_history
        
        # 连接成功率趋势
        success_rates = []
        for metrics in history:
            success_rate = self._calculate_success_rate(
                metrics.connection_metrics['connect_succ'],
                metrics.connection_metrics['connect_fail']
            )
            success_rates.append(success_rate)
        
        # 消息吞吐量趋势
        throughputs = []
        for metrics in history:
            throughput = metrics.message_metrics['pub'] + metrics.message_metrics['recv']
            throughputs.append(throughput)
        
        # 延迟趋势
        latencies = []
        for metrics in history:
            latencies.append(metrics.latency_metrics['publish_latency'])
        
        return {
            'success_rate_trend': success_rates,
            'throughput_trend': throughputs,
            'latency_trend': latencies,
            'avg_success_rate': np.mean(success_rates) if success_rates else 0,
            'avg_throughput': np.mean(throughputs) if throughputs else 0,
            'avg_latency': np.mean(latencies) if latencies else 0,
            'max_success_rate': np.max(success_rates) if success_rates else 0,
            'max_throughput': np.max(throughputs) if throughputs else 0,
            'max_latency': np.max(latencies) if latencies else 0
        }
    
    def _calculate_success_rate(self, success: float, failed: float) -> float:
        """计算成功率"""
        total = success + failed
        return (success / total * 100) if total > 0 else 0
    
    def _generate_report_html(self, current_metrics: BenchmarkMetrics, analysis: Dict[str, Any]) -> str:
        """生成报告HTML"""
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eMQTT-Bench 压测报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background: #f5f5f5;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
            color: white; 
            padding: 40px; 
            text-align: center; 
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px; 
            margin-bottom: 20px;
        }}
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .metric-card {{ 
            background: #f8f9fa; 
            border-radius: 8px; 
            padding: 20px; 
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 5px;
        }}
        .metric-label {{ 
            color: #7f8c8d; 
            font-size: 0.9em;
        }}
        .status-good {{ color: #27ae60; }}
        .status-warning {{ color: #f39c12; }}
        .status-error {{ color: #e74c3c; }}
        .summary {{ 
            background: #ecf0f1; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .recommendations {{ 
            background: #e8f5e8; 
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid #27ae60;
        }}
        .footer {{ 
            background: #2c3e50; 
            color: white; 
            text-align: center; 
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 eMQTT-Bench 压测报告</h1>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 测试概览</h2>
                <div class="summary">
                    <p><strong>测试类型:</strong> {current_metrics.test_type.upper()}</p>
                    <p><strong>测试时间:</strong> {current_metrics.timestamp}</p>
                    <p><strong>数据收集点:</strong> {len(self.collector.metrics_history)} 个</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔗 连接性能</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value status-good">{int(current_metrics.connection_metrics['connect_succ'])}</div>
                        <div class="metric-label">成功连接数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-error">{int(current_metrics.connection_metrics['connect_fail'])}</div>
                        <div class="metric-label">失败连接数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-warning">{int(current_metrics.connection_metrics['connect_retried'])}</div>
                        <div class="metric-label">重连次数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-good">{int(current_metrics.system_metrics['active_connections'])}</div>
                        <div class="metric-label">活跃连接数</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📨 消息性能</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value status-good">{int(current_metrics.message_metrics['pub'])}</div>
                        <div class="metric-label">发送消息数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-good">{int(current_metrics.message_metrics['recv'])}</div>
                        <div class="metric-label">接收消息数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-error">{int(current_metrics.message_metrics['pub_fail'])}</div>
                        <div class="metric-label">发送失败数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-error">{int(current_metrics.message_metrics['pub_overrun'])}</div>
                        <div class="metric-label">消息溢出数</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>⏱️ 延迟性能</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value status-good">{current_metrics.latency_metrics['publish_latency']:.1f}ms</div>
                        <div class="metric-label">平均发布延迟</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-good">{current_metrics.latency_metrics['mqtt_client_connect_duration']:.1f}ms</div>
                        <div class="metric-label">连接建立延迟</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value status-good">{current_metrics.latency_metrics['e2e_latency']:.1f}ms</div>
                        <div class="metric-label">端到端延迟</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 性能分析</h2>
                <div class="summary">
                    <p><strong>平均连接成功率:</strong> {analysis.get('avg_success_rate', 0):.1f}%</p>
                    <p><strong>平均消息吞吐量:</strong> {analysis.get('avg_throughput', 0):.0f} msg/s</p>
                    <p><strong>平均延迟:</strong> {analysis.get('avg_latency', 0):.1f}ms</p>
                    <p><strong>最大延迟:</strong> {analysis.get('max_latency', 0):.1f}ms</p>
                </div>
            </div>
            
            <div class="section">
                <h2>💡 优化建议</h2>
                <div class="recommendations">
                    <ul>
                        <li>如果连接失败率较高，建议检查网络连接和服务器配置</li>
                        <li>如果延迟较高，建议优化网络环境或减少并发连接数</li>
                        <li>如果消息丢失率较高，建议调整消息发送频率或增加重试机制</li>
                        <li>定期监控系统资源使用情况，确保有足够的CPU和内存</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>报告由 eMQTT-Bench 压测工具生成 | 作者: Jaxon</p>
        </div>
    </div>
</body>
</html>
        """

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="eMQTT-Bench 压测结果显示系统")
    parser.add_argument("--mode", choices=["live", "web", "report"], default="live", 
                       help="显示模式: live(实时), web(Web仪表盘), report(生成报告)")
    parser.add_argument("--ports", nargs="+", type=int, default=[9090, 9091, 9092, 9093, 9094],
                       help="Prometheus监控端口列表")
    parser.add_argument("--test-type", choices=["conn", "pub", "sub"], default="conn",
                       help="测试类型")
    parser.add_argument("--web-port", type=int, default=8080,
                       help="Web仪表盘端口")
    parser.add_argument("--output", type=str,
                       help="报告输出文件路径")
    
    args = parser.parse_args()
    
    # 创建指标收集器
    collector = MetricsCollector(args.ports)
    
    console.print(f"[blue]🚀 eMQTT-Bench 压测结果显示系统启动[/blue]")
    console.print(f"[cyan]监控端口: {args.ports}[/cyan]")
    console.print(f"[cyan]测试类型: {args.test_type}[/cyan]")
    
    try:
        if args.mode == "live":
            # 实时显示模式
            display = RealTimeDisplay(collector)
            display.start_live_display(args.test_type)
            
        elif args.mode == "web":
            # Web仪表盘模式
            dashboard = WebDashboard(collector, args.web_port)
            dashboard.start_dashboard()
            
        elif args.mode == "report":
            # 报告生成模式
            generator = ReportGenerator(collector)
            generator.generate_report(args.output)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已退出[/yellow]")
    except Exception as e:
        console.print(f"[red]程序运行出错: {e}[/red]")

if __name__ == "__main__":
    main()

