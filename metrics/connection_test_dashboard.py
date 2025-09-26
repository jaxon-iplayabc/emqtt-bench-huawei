#!/usr/bin/env python3
"""
连接测试专业仪表盘
提供直观的连接测试指标展示和实时监控
作者: Jaxon
日期: 2024-12-19
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

class ConnectionTestDashboard:
    """连接测试专业仪表盘"""
    
    def __init__(self, metrics_data: Dict[str, Any], port: int = 8080):
        self.metrics_data = metrics_data
        self.port = port
        self.server = None
        self.server_thread = None
        
    def generate_dashboard(self) -> str:
        """生成连接测试仪表盘HTML"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dashboard_file = f"connection_test_dashboard_{timestamp}.html"
        
        # 分析指标数据
        analysis = self._analyze_metrics_data()
        
        # 生成HTML内容
        html_content = self._generate_html_template(analysis)
        
        # 保存仪表盘
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🎯 连接测试仪表盘已生成: {dashboard_file}")
        return dashboard_file
    
    def _analyze_metrics_data(self) -> Dict[str, Any]:
        """分析指标数据"""
        analysis = {
            'test_summary': {},
            'connection_performance': {},
            'concurrency_metrics': {},
            'network_performance': {},
            'system_resources': {},
            'error_analysis': {},
            'trend_data': {},
            'recommendations': []
        }
        
        # 分析测试摘要
        if 'test_summary' in self.metrics_data:
            test_summary = self.metrics_data['test_summary']
            analysis['test_summary'] = {
                'test_duration': test_summary.get('test_duration', 0),
                'total_metrics_collected': test_summary.get('total_metrics_collected', 0),
                'performance_stats': test_summary.get('performance_stats', {}),
                'connection_time_stats': test_summary.get('connection_time_stats', {}),
                'error_summary': test_summary.get('error_summary', {}),
                'system_resource_summary': test_summary.get('system_resource_summary', {})
            }
        
        # 分析连接性能
        performance_stats = analysis['test_summary'].get('performance_stats', {})
        analysis['connection_performance'] = {
            'success_rate': performance_stats.get('connection_success_rate', 0),
            'avg_connection_time': performance_stats.get('avg_connection_time', 0),
            'connection_rate': performance_stats.get('connection_rate', 0),
            'error_rate': performance_stats.get('error_rate', 0),
            'max_concurrent': performance_stats.get('max_concurrent_connections', 0),
            'current_concurrent': performance_stats.get('current_concurrent_connections', 0)
        }
        
        # 分析并发指标
        analysis['concurrency_metrics'] = {
            'max_concurrent_connections': performance_stats.get('max_concurrent_connections', 0),
            'current_concurrent_connections': performance_stats.get('current_concurrent_connections', 0),
            'connection_growth_curve': self._generate_connection_growth_curve(),
            'connection_stability': self._calculate_connection_stability()
        }
        
        # 分析网络性能
        connection_time_stats = analysis['test_summary'].get('connection_time_stats', {})
        analysis['network_performance'] = {
            'avg_connection_time': connection_time_stats.get('mean', 0),
            'min_connection_time': connection_time_stats.get('min', 0),
            'max_connection_time': connection_time_stats.get('max', 0),
            'p90_connection_time': connection_time_stats.get('p90', 0),
            'p95_connection_time': connection_time_stats.get('p95', 0),
            'p99_connection_time': connection_time_stats.get('p99', 0),
            'connection_time_distribution': self._generate_connection_time_distribution()
        }
        
        # 分析系统资源
        system_summary = analysis['test_summary'].get('system_resource_summary', {})
        analysis['system_resources'] = {
            'cpu_usage': system_summary.get('cpu_usage', {}),
            'memory_usage': system_summary.get('memory_usage', {}),
            'resource_efficiency': self._calculate_resource_efficiency(system_summary)
        }
        
        # 分析错误情况
        error_summary = analysis['test_summary'].get('error_summary', {})
        analysis['error_analysis'] = {
            'error_types': error_summary,
            'total_errors': sum(error_summary.values()),
            'error_rate': performance_stats.get('error_rate', 0),
            'error_timeline': self._generate_error_timeline()
        }
        
        # 生成趋势数据
        analysis['trend_data'] = self._generate_trend_data()
        
        # 生成优化建议
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_connection_growth_curve(self) -> List[Dict]:
        """生成连接数增长曲线数据"""
        growth_data = []
        
        if 'metrics_history' in self.metrics_data:
            metrics_history = self.metrics_data['metrics_history']
            for i, metrics in enumerate(metrics_history):
                growth_data.append({
                    'time': i,
                    'concurrent_connections': metrics.get('concurrent_connections', 0),
                    'successful_connections': metrics.get('successful_connections', 0)
                })
        
        return growth_data
    
    def _calculate_connection_stability(self) -> Dict[str, float]:
        """计算连接稳定性"""
        if 'metrics_history' not in self.metrics_data:
            return {'stability_score': 0, 'avg_connection_duration': 0}
        
        metrics_history = self.metrics_data['metrics_history']
        if not metrics_history:
            return {'stability_score': 0, 'avg_connection_duration': 0}
        
        # 计算连接数变化的标准差
        concurrent_values = [m.get('concurrent_connections', 0) for m in metrics_history]
        if len(concurrent_values) > 1:
            import statistics
            stability_score = 100 - min(100, statistics.stdev(concurrent_values) * 10)
        else:
            stability_score = 100
        
        # 计算平均连接持续时间（基于连接时间统计）
        connection_times = []
        for metrics in metrics_history:
            if 'avg_connection_time' in metrics and metrics['avg_connection_time'] > 0:
                connection_times.append(metrics['avg_connection_time'])
        
        avg_connection_duration = statistics.mean(connection_times) if connection_times else 0
        
        return {
            'stability_score': stability_score,
            'avg_connection_duration': avg_connection_duration
        }
    
    def _generate_connection_time_distribution(self) -> List[Dict]:
        """生成连接时间分布数据"""
        distribution = []
        
        if 'metrics_history' in self.metrics_data:
            metrics_history = self.metrics_data['metrics_history']
            connection_times = []
            
            for metrics in metrics_history:
                if 'avg_connection_time' in metrics and metrics['avg_connection_time'] > 0:
                    connection_times.append(metrics['avg_connection_time'])
            
            if connection_times:
                # 创建时间分布区间
                min_time = min(connection_times)
                max_time = max(connection_times)
                interval = (max_time - min_time) / 10 if max_time > min_time else 1
                
                for i in range(10):
                    start = min_time + i * interval
                    end = min_time + (i + 1) * interval
                    count = sum(1 for t in connection_times if start <= t < end)
                    distribution.append({
                        'range': f"{start:.1f}-{end:.1f}ms",
                        'count': count,
                        'percentage': (count / len(connection_times)) * 100
                    })
        
        return distribution
    
    def _calculate_resource_efficiency(self, system_summary: Dict) -> Dict[str, Any]:
        """计算资源使用效率"""
        efficiency = {
            'cpu_efficiency': 0,
            'memory_efficiency': 0,
            'overall_efficiency': 0
        }
        
        cpu_usage = system_summary.get('cpu_usage', {})
        memory_usage = system_summary.get('memory_usage', {})
        
        if cpu_usage:
            avg_cpu = cpu_usage.get('avg', 0)
            efficiency['cpu_efficiency'] = max(0, 100 - avg_cpu)  # 效率 = 100 - 使用率
        
        if memory_usage:
            avg_memory = memory_usage.get('avg', 0)
            efficiency['memory_efficiency'] = max(0, 100 - avg_memory)
        
        # 计算整体效率
        if efficiency['cpu_efficiency'] > 0 and efficiency['memory_efficiency'] > 0:
            efficiency['overall_efficiency'] = (
                efficiency['cpu_efficiency'] + efficiency['memory_efficiency']
            ) / 2
        
        return efficiency
    
    def _generate_error_timeline(self) -> List[Dict]:
        """生成错误时间线数据"""
        error_timeline = []
        
        if 'metrics_history' in self.metrics_data:
            metrics_history = self.metrics_data['metrics_history']
            for i, metrics in enumerate(metrics_history):
                total_errors = sum(metrics.get('error_types', {}).values())
                error_timeline.append({
                    'time': i,
                    'error_count': total_errors,
                    'error_rate': (total_errors / max(1, metrics.get('total_attempts', 1))) * 100
                })
        
        return error_timeline
    
    def _generate_trend_data(self) -> Dict[str, List]:
        """生成趋势数据"""
        trend_data = {
            'timeline': [],
            'connection_success_rate': [],
            'connection_time': [],
            'concurrent_connections': [],
            'error_rate': []
        }
        
        if 'metrics_history' in self.metrics_data:
            metrics_history = self.metrics_data['metrics_history']
            for i, metrics in enumerate(metrics_history):
                trend_data['timeline'].append(i)
                
                # 计算成功率
                total_attempts = metrics.get('total_attempts', 0)
                successful = metrics.get('successful_connections', 0)
                success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
                trend_data['connection_success_rate'].append(success_rate)
                
                # 连接时间
                trend_data['connection_time'].append(metrics.get('avg_connection_time', 0))
                
                # 并发连接数
                trend_data['concurrent_connections'].append(metrics.get('concurrent_connections', 0))
                
                # 错误率
                failed = metrics.get('failed_connections', 0)
                error_rate = (failed / total_attempts * 100) if total_attempts > 0 else 0
                trend_data['error_rate'].append(error_rate)
        
        return trend_data
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """生成优化建议"""
        recommendations = []
        
        # 基于连接成功率的建议
        success_rate = analysis['connection_performance'].get('success_rate', 0)
        if success_rate < 95:
            recommendations.append({
                'type': 'warning',
                'title': '连接成功率偏低',
                'description': f'当前连接成功率为 {success_rate:.1f}%，建议检查网络连接质量和服务器配置',
                'priority': 'high'
            })
        
        # 基于连接时间的建议
        avg_connection_time = analysis['connection_performance'].get('avg_connection_time', 0)
        if avg_connection_time > 100:
            recommendations.append({
                'type': 'performance',
                'title': '连接时间较长',
                'description': f'平均连接时间为 {avg_connection_time:.1f}ms，建议优化网络配置或服务器性能',
                'priority': 'medium'
            })
        
        # 基于系统资源的建议
        system_resources = analysis['system_resources']
        cpu_usage = system_resources.get('cpu_usage', {})
        memory_usage = system_resources.get('memory_usage', {})
        
        if cpu_usage.get('avg', 0) > 80:
            recommendations.append({
                'type': 'resource',
                'title': 'CPU使用率较高',
                'description': f'平均CPU使用率为 {cpu_usage.get("avg", 0):.1f}%，建议优化系统性能或增加计算资源',
                'priority': 'medium'
            })
        
        if memory_usage.get('avg', 0) > 80:
            recommendations.append({
                'type': 'resource',
                'title': '内存使用率较高',
                'description': f'平均内存使用率为 {memory_usage.get("avg", 0):.1f}%，建议优化内存使用或增加内存容量',
                'priority': 'medium'
            })
        
        # 基于错误分析的建议
        error_analysis = analysis['error_analysis']
        total_errors = error_analysis.get('total_errors', 0)
        if total_errors > 0:
            error_types = error_analysis.get('error_types', {})
            if '连接失败' in error_types and error_types['连接失败'] > 0:
                recommendations.append({
                    'type': 'error',
                    'title': '连接失败较多',
                    'description': f'检测到 {error_types["连接失败"]} 次连接失败，建议检查网络连接和服务器状态',
                    'priority': 'high'
                })
        
        # 如果没有问题，添加成功建议
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'title': '系统运行良好',
                'description': '连接测试各项指标正常，系统运行状态良好',
                'priority': 'low'
            })
        
        return recommendations
    
    def _generate_html_template(self, analysis: Dict) -> str:
        """生成HTML模板"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eMQTT-Bench 连接测试专业仪表盘</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-card .icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
            display: block;
        }}
        
        .stat-card .value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #7f8c8d;
            font-size: 1em;
            font-weight: 500;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .panel {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }}
        
        .panel:hover {{
            transform: translateY(-2px);
        }}
        
        .panel-header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .panel-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin: 0;
        }}
        
        .panel-content {{
            padding: 25px;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        
        .recommendations {{
            margin: 20px 0;
        }}
        
        .recommendation {{
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .recommendation.success {{
            background: linear-gradient(135deg, #d5f4e6, #a8e6cf);
            border-left: 5px solid #27ae60;
            color: #155724;
        }}
        
        .recommendation.warning {{
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border-left: 5px solid #f39c12;
            color: #856404;
        }}
        
        .recommendation.performance {{
            background: linear-gradient(135deg, #cce5ff, #99d6ff);
            border-left: 5px solid #3498db;
            color: #004085;
        }}
        
        .recommendation.resource {{
            background: linear-gradient(135deg, #f8d7da, #fab1a0);
            border-left: 5px solid #e74c3c;
            color: #721c24;
        }}
        
        .recommendation.error {{
            background: linear-gradient(135deg, #f8d7da, #fd79a8);
            border-left: 5px solid #e84393;
            color: #721c24;
        }}
        
        .recommendation-icon {{
            font-size: 1.5em;
            margin-right: 15px;
        }}
        
        .recommendation-content h4 {{
            margin: 0 0 5px 0;
            font-size: 1.1em;
        }}
        
        .recommendation-content p {{
            margin: 0;
            font-size: 0.95em;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 50px;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .dashboard-grid {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 页面头部 -->
        <div class="header">
            <h1>🎯 eMQTT-Bench 连接测试专业仪表盘</h1>
            <div class="subtitle">专业的MQTT连接性能分析与监控</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="icon">📊</span>
                    <div class="value">{analysis['test_summary'].get('test_duration', 0):.1f}s</div>
                    <div class="label">测试时长</div>
                </div>
                <div class="stat-card">
                    <span class="icon">🔗</span>
                    <div class="value">{analysis['connection_performance'].get('success_rate', 0):.1f}%</div>
                    <div class="label">连接成功率</div>
                </div>
                <div class="stat-card">
                    <span class="icon">⚡</span>
                    <div class="value">{analysis['connection_performance'].get('avg_connection_time', 0):.1f}ms</div>
                    <div class="label">平均连接时间</div>
                </div>
                <div class="stat-card">
                    <span class="icon">🚀</span>
                    <div class="value">{analysis['connection_performance'].get('connection_rate', 0):.1f}/s</div>
                    <div class="label">连接建立速率</div>
                </div>
            </div>
        </div>
        
        <!-- 连接性能概览 -->
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📈 连接性能趋势</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="connectionTrendChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🔗 并发连接能力</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="concurrencyChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 网络性能分析 -->
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🌐 网络性能分析</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="networkPerformanceChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">💻 系统资源使用</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="systemResourcesChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 错误分析 -->
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">🚨 错误分析与诊断</h3>
            </div>
            <div class="panel-content">
                <div class="chart-container">
                    <canvas id="errorAnalysisChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- 优化建议 -->
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">💡 性能优化建议</h3>
            </div>
            <div class="panel-content">
                <div class="recommendations">
                    {self._generate_recommendations_html(analysis['recommendations'])}
                </div>
            </div>
        </div>
        
        <!-- 页面底部 -->
        <div class="footer">
            <p>📊 报告由 eMQTT-Bench 连接测试专业仪表盘生成</p>
            <p>🕒 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🔧 基于专业连接测试指标分析</p>
        </div>
    </div>
    
    <script>
        // 初始化图表
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
        }});
        
        function initializeCharts() {{
            // 连接性能趋势图
            const connectionTrendCtx = document.getElementById('connectionTrendChart');
            if (connectionTrendCtx) {{
                new Chart(connectionTrendCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(analysis['trend_data']['timeline'])},
                        datasets: [{{
                            label: '连接成功率 (%)',
                            data: {json.dumps(analysis['trend_data']['connection_success_rate'])},
                            borderColor: '#27ae60',
                            backgroundColor: 'rgba(39, 174, 96, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        }}, {{
                            label: '连接时间 (ms)',
                            data: {json.dumps(analysis['trend_data']['connection_time'])},
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: '成功率 (%)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '连接时间 (ms)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }}
                        }}
                    }}
                }});
            }}
            
            // 并发连接能力图
            const concurrencyCtx = document.getElementById('concurrencyChart');
            if (concurrencyCtx) {{
                new Chart(concurrencyCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps([item['time'] for item in analysis['concurrency_metrics']['connection_growth_curve']])},
                        datasets: [{{
                            label: '并发连接数',
                            data: {json.dumps([item['concurrent_connections'] for item in analysis['concurrency_metrics']['connection_growth_curve']])},
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: '连接数'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
            
            // 网络性能分析图
            const networkCtx = document.getElementById('networkPerformanceChart');
            if (networkCtx) {{
                new Chart(networkCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['平均时间', 'P90时间', 'P95时间', 'P99时间'],
                        datasets: [{{
                            label: '连接时间 (ms)',
                            data: [
                                {analysis['network_performance'].get('avg_connection_time', 0):.1f},
                                {analysis['network_performance'].get('p90_connection_time', 0):.1f},
                                {analysis['network_performance'].get('p95_connection_time', 0):.1f},
                                {analysis['network_performance'].get('p99_connection_time', 0):.1f}
                            ],
                            backgroundColor: [
                                'rgba(39, 174, 96, 0.8)',
                                'rgba(52, 152, 219, 0.8)',
                                'rgba(243, 156, 18, 0.8)',
                                'rgba(231, 76, 60, 0.8)'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: '时间 (ms)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
            
            // 系统资源使用图
            const systemCtx = document.getElementById('systemResourcesChart');
            if (systemCtx) {{
                const cpuUsage = {analysis['system_resources'].get('cpu_usage', {}).get('avg', 0):.1f};
                const memoryUsage = {analysis['system_resources'].get('memory_usage', {}).get('avg', 0):.1f};
                
                new Chart(systemCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['CPU使用率', '内存使用率'],
                        datasets: [{{
                            data: [cpuUsage, memoryUsage],
                            backgroundColor: ['#e74c3c', '#3498db'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
            
            // 错误分析图
            const errorCtx = document.getElementById('errorAnalysisChart');
            if (errorCtx) {{
                const errorTypes = {json.dumps(analysis['error_analysis'].get('error_types', {}))};
                const labels = Object.keys(errorTypes);
                const data = Object.values(errorTypes);
                
                new Chart(errorCtx, {{
                    type: 'pie',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            data: data,
                            backgroundColor: [
                                '#e74c3c',
                                '#f39c12',
                                '#3498db',
                                '#9b59b6',
                                '#1abc9c'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
        }}
    </script>
</body>
</html>
"""
    
    def _generate_recommendations_html(self, recommendations: List[Dict]) -> str:
        """生成建议HTML"""
        if not recommendations:
            return '<div class="recommendation success"><span class="recommendation-icon">✅</span><div class="recommendation-content"><h4>系统运行正常</h4><p>没有检测到需要优化的项目</p></div></div>'
        
        html = ""
        for rec in recommendations:
            icon_map = {
                'success': '✅',
                'warning': '⚠️',
                'performance': '⚡',
                'resource': '💻',
                'error': '❌'
            }
            icon = icon_map.get(rec['type'], '💡')
            
            html += f"""
            <div class="recommendation {rec['type']}">
                <span class="recommendation-icon">{icon}</span>
                <div class="recommendation-content">
                    <h4>{rec['title']}</h4>
                    <p>{rec['description']}</p>
                </div>
            </div>
            """
        return html
    
    def start_web_server(self):
        """启动Web服务器"""
        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    
                    # 生成仪表盘HTML
                    analysis = self._analyze_metrics_data()
                    html_content = self._generate_html_template(analysis)
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # 禁用日志输出
        
        try:
            self.server = HTTPServer(('localhost', self.port), DashboardHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            print(f"🌐 连接测试仪表盘已启动: http://localhost:{self.port}")
            print("💡 按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            webbrowser.open(f'http://localhost:{self.port}')
            
            return True
        except Exception as e:
            print(f"❌ 启动Web服务器失败: {e}")
            return False
    
    def stop_web_server(self):
        """停止Web服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("⏹️ Web服务器已停止")

def main():
    """测试函数"""
    # 模拟指标数据
    sample_data = {
        'test_summary': {
            'test_duration': 120.5,
            'total_metrics_collected': 60,
            'performance_stats': {
                'connection_success_rate': 98.5,
                'avg_connection_time': 45.2,
                'connection_rate': 1250.0,
                'error_rate': 1.5,
                'max_concurrent_connections': 4850,
                'current_concurrent_connections': 4850
            },
            'connection_time_stats': {
                'min': 12.5,
                'max': 156.8,
                'mean': 45.2,
                'median': 42.1,
                'p90': 78.5,
                'p95': 95.2,
                'p99': 125.6
            },
            'error_summary': {
                '连接失败': 15,
                '发布失败': 3,
                '订阅失败': 2
            },
            'system_resource_summary': {
                'cpu_usage': {'avg': 45.2, 'max': 78.5, 'min': 12.3},
                'memory_usage': {'avg': 62.1, 'max': 85.2, 'min': 45.8}
            }
        },
        'metrics_history': []
    }
    
    # 生成模拟历史数据
    for i in range(60):
        sample_data['metrics_history'].append({
            'timestamp': (datetime.now() - timedelta(seconds=60-i)).isoformat(),
            'total_attempts': 100 + i * 2,
            'successful_connections': 98 + i * 2,
            'failed_connections': 2,
            'concurrent_connections': min(4850, 100 + i * 80),
            'connection_rate': 1200 + i * 5,
            'error_types': {'连接失败': 1 if i % 10 == 0 else 0},
            'system_resources': {
                'cpu_usage_percent': 40 + i * 0.5,
                'memory_usage_percent': 60 + i * 0.3
            },
            'avg_connection_time': 40 + i * 0.2
        })
    
    dashboard = ConnectionTestDashboard(sample_data)
    
    try:
        # 生成静态仪表盘
        dashboard_file = dashboard.generate_dashboard()
        print(f"📊 静态仪表盘已生成: {dashboard_file}")
        
        # 启动Web服务器
        if dashboard.start_web_server():
            # 保持服务器运行
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    finally:
        dashboard.stop_web_server()

if __name__ == "__main__":
    main()
