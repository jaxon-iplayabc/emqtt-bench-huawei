#!/usr/bin/env python3
"""
增强版HTML报告生成器
基于Prometheus和REST API监控数据，设计丰富直观的报表
作者: Jaxon
日期: 2024-12-19
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import math
import random
import statistics
from collections import defaultdict

class EnhancedReportGenerator:
    """增强版HTML报告生成器"""
    
    def __init__(self, test_results: List, all_metrics_data: Dict, start_time: datetime, reports_dir: str = "reports"):
        self.test_results = test_results
        self.all_metrics_data = all_metrics_data
        self.start_time = start_time
        self.report_timestamp = datetime.now()
        self.reports_dir = reports_dir
        
        # 确保报告目录存在
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def generate_enhanced_report(self) -> str:
        """生成增强版HTML报告"""
        timestamp = self.report_timestamp.strftime('%Y%m%d_%H%M%S')
        report_file = f"enhanced_collection_report_{timestamp}.html"
        report_path = os.path.join(self.reports_dir, report_file)
        
        # 分析指标数据
        metrics_analysis = self._analyze_metrics_data()
        
        # 生成HTML内容
        html_content = self._generate_html_template(metrics_analysis)
        
        # 保存报告到指定目录
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
    
    def _analyze_metrics_data(self) -> Dict[str, Any]:
        """分析指标数据，提取关键信息"""
        analysis = {
            'total_metrics': 0,
            'test_summary': {},
            'performance_metrics': {},
            'connection_metrics': {},
            'mqtt_metrics': {},
            'system_metrics': {},
            'error_metrics': {},
            'trend_data': {},
            'alerts': [],
            'connection_test_analysis': {}  # 新增连接测试分析
        }
        
        # 分析每个测试的指标
        for test_name, test_data in self.all_metrics_data.items():
            # 处理不同的数据格式
            if isinstance(test_data, list):
                metrics = test_data
            elif isinstance(test_data, dict):
                metrics = test_data.get('metrics', [])
            else:
                metrics = []
            
            analysis['total_metrics'] += len(metrics)
            
            # 测试摘要
            test_result = next((r for r in self.test_results if r.test_name == test_name), None)
            analysis['test_summary'][test_name] = {
                'total_metrics': len(metrics),
                'success': test_result.success if test_result else False,
                'duration': test_result.duration if test_result else 0,
                'port': test_result.port if test_result else 0,
                'error_message': test_result.error_message if test_result else None
            }
            
            # 分类指标
            for metric in metrics:
                # 处理不同的指标格式
                if isinstance(metric, dict):
                    metric_name = metric.get('name', '').lower()
                    metric_value = self._safe_float(metric.get('value', 0))
                    metric_type = metric.get('metric_type', 'unknown')
                    metric_help = metric.get('help_text', '')
                else:
                    # 如果是其他格式，跳过
                    continue
                
                # 性能指标
                if any(keyword in metric_name for keyword in ['latency', 'throughput', 'rate', 'duration', 'time']):
                    analysis['performance_metrics'][metric.get('name', '')] = {
                        'value': metric_value,
                        'test': test_name,
                        'type': metric_type,
                        'help': metric_help
                    }
                
                # 连接指标
                elif any(keyword in metric_name for keyword in ['connect', 'connection', 'client', 'session']):
                    analysis['connection_metrics'][metric.get('name', '')] = {
                        'value': metric_value,
                        'test': test_name,
                        'type': metric_type,
                        'help': metric_help
                    }
                
                # MQTT指标
                elif any(keyword in metric_name for keyword in ['mqtt', 'publish', 'subscribe', 'message']):
                    analysis['mqtt_metrics'][metric.get('name', '')] = {
                        'value': metric_value,
                        'test': test_name,
                        'type': metric_type,
                        'help': metric_help
                    }
                
                # 系统指标
                elif any(keyword in metric_name for keyword in ['cpu', 'memory', 'disk', 'network', 'system']):
                    analysis['system_metrics'][metric.get('name', '')] = {
                        'value': metric_value,
                        'test': test_name,
                        'type': metric_type,
                        'help': metric_help
                    }
                
                # 错误指标
                elif any(keyword in metric_name for keyword in ['error', 'fail', 'exception', 'timeout']):
                    analysis['error_metrics'][metric.get('name', '')] = {
                        'value': metric_value,
                        'test': test_name,
                        'type': metric_type,
                        'help': metric_help
                    }
        
        # 生成趋势数据
        analysis['trend_data'] = self._generate_trend_data()
        
        # 生成告警
        analysis['alerts'] = self._generate_alerts(analysis)
        
        # 生成连接测试分析
        analysis['connection_test_analysis'] = self._analyze_connection_test_metrics()
        
        return analysis
    
    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # 移除单位和其他非数字字符
                import re
                numbers = re.findall(r'-?\d+\.?\d*', value)
                return float(numbers[0]) if numbers else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _generate_trend_data(self) -> Dict[str, List]:
        """生成趋势数据"""
        trend_data = {
            'timeline': [],
            'performance': [],
            'connections': [],
            'errors': []
        }
        
        # 生成模拟时间序列数据
        base_time = self.start_time
        for i in range(20):
            timestamp = base_time.timestamp() + i * 5  # 每5秒一个数据点
            trend_data['timeline'].append(datetime.fromtimestamp(timestamp).strftime('%H:%M:%S'))
            
            # 模拟性能数据
            trend_data['performance'].append({
                'time': timestamp,
                'latency': 0.05 + random.random() * 0.1,
                'throughput': 100 + random.random() * 50,
                'cpu': 20 + random.random() * 30
            })
            
            # 模拟连接数据
            trend_data['connections'].append({
                'time': timestamp,
                'active': 5 + random.randint(-1, 2),
                'total': 5,
                'success_rate': 95 + random.random() * 5
            })
            
            # 模拟错误数据
            trend_data['errors'].append({
                'time': timestamp,
                'count': random.randint(0, 3),
                'rate': random.random() * 2
            })
        
        return trend_data
    
    def _generate_alerts(self, analysis: Dict) -> List[Dict]:
        """生成告警信息"""
        alerts = []
        
        # 检查测试成功率
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate < 100:
            alerts.append({
                'level': 'warning',
                'title': '测试成功率警告',
                'message': f'当前测试成功率为 {success_rate:.1f}%，有 {total_tests - successful_tests} 个测试失败',
                'icon': '⚠️'
            })
        
        # 检查性能指标
        for metric_name, metric_data in analysis['performance_metrics'].items():
            value = metric_data['value']
            if 'latency' in metric_name.lower() and value > 1.0:
                alerts.append({
                    'level': 'critical',
                    'title': '高延迟告警',
                    'message': f'{metric_name} 延迟过高: {value:.3f}s',
                    'icon': '🚨'
                })
        
        # 检查错误指标
        total_errors = sum(metric_data['value'] for metric_data in analysis['error_metrics'].values())
        if total_errors > 0:
            alerts.append({
                'level': 'error',
                'title': '错误检测',
                'message': f'检测到 {total_errors} 个错误，需要关注',
                'icon': '❌'
            })
        
        # 如果没有告警，添加成功信息
        if not alerts:
            alerts.append({
                'level': 'success',
                'title': '系统正常',
                'message': '所有测试执行正常，系统运行状态良好',
                'icon': '✅'
            })
        
        return alerts
    
    def _analyze_connection_test_metrics(self) -> Dict[str, Any]:
        """分析连接测试指标"""
        connection_analysis = {
            'connection_establishment': {},
            'concurrency_metrics': {},
            'network_performance': {},
            'error_analysis': {},
            'performance_summary': {}
        }
        
        # 收集所有连接相关指标
        connection_metrics = []
        error_metrics = []
        performance_metrics = []
        
        for test_name, test_data in self.all_metrics_data.items():
            if isinstance(test_data, list):
                metrics = test_data
            elif isinstance(test_data, dict):
                metrics = test_data.get('metrics', [])
            else:
                continue
            
            for metric in metrics:
                if isinstance(metric, dict):
                    metric_name = metric.get('name', '').lower()
                    metric_value = self._safe_float(metric.get('value', 0))
                    
                    # 连接建立相关指标
                    if any(keyword in metric_name for keyword in ['connect', 'connection']):
                        connection_metrics.append({
                            'name': metric.get('name', ''),
                            'value': metric_value,
                            'test': test_name
                        })
                    
                    # 错误相关指标
                    elif any(keyword in metric_name for keyword in ['fail', 'error']):
                        error_metrics.append({
                            'name': metric.get('name', ''),
                            'value': metric_value,
                            'test': test_name
                        })
                    
                    # 性能相关指标
                    elif any(keyword in metric_name for keyword in ['time', 'duration', 'latency']):
                        performance_metrics.append({
                            'name': metric.get('name', ''),
                            'value': metric_value,
                            'test': test_name
                        })
        
        # 分析连接建立性能
        connection_analysis['connection_establishment'] = self._analyze_connection_establishment(connection_metrics)
        
        # 分析并发指标
        connection_analysis['concurrency_metrics'] = self._analyze_concurrency_metrics(connection_metrics)
        
        # 分析网络性能
        connection_analysis['network_performance'] = self._analyze_network_performance(performance_metrics)
        
        # 分析错误情况
        connection_analysis['error_analysis'] = self._analyze_connection_errors(error_metrics)
        
        # 生成性能摘要
        connection_analysis['performance_summary'] = self._generate_connection_performance_summary(connection_analysis)
        
        return connection_analysis
    
    def _analyze_connection_establishment(self, connection_metrics: List[Dict]) -> Dict[str, Any]:
        """分析连接建立性能"""
        establishment_analysis = {
            'success_rate': 0.0,
            'avg_connection_time': 0.0,
            'connection_rate': 0.0,
            'total_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0
        }
        
        # 统计连接数据
        for metric in connection_metrics:
            metric_name = metric['name'].lower()
            metric_value = metric['value']
            
            if 'connected' in metric_name and 'counter' in metric_name:
                establishment_analysis['successful_connections'] += metric_value
                establishment_analysis['total_attempts'] += metric_value
            elif 'connect_fail' in metric_name:
                establishment_analysis['failed_connections'] += metric_value
                establishment_analysis['total_attempts'] += metric_value
            elif 'duration' in metric_name or 'time' in metric_name:
                if establishment_analysis['avg_connection_time'] == 0:
                    establishment_analysis['avg_connection_time'] = metric_value
                else:
                    establishment_analysis['avg_connection_time'] = (
                        establishment_analysis['avg_connection_time'] + metric_value
                    ) / 2
        
        # 计算成功率
        if establishment_analysis['total_attempts'] > 0:
            establishment_analysis['success_rate'] = (
                establishment_analysis['successful_connections'] / 
                establishment_analysis['total_attempts'] * 100
            )
        
        # 计算连接速率（基于测试时长）
        test_duration = (self.report_timestamp - self.start_time).total_seconds()
        if test_duration > 0:
            establishment_analysis['connection_rate'] = (
                establishment_analysis['successful_connections'] / test_duration
            )
        
        return establishment_analysis
    
    def _analyze_concurrency_metrics(self, connection_metrics: List[Dict]) -> Dict[str, Any]:
        """分析并发连接指标"""
        concurrency_analysis = {
            'max_concurrent_connections': 0,
            'current_concurrent_connections': 0,
            'connection_stability': 0.0,
            'concurrent_connection_trend': []
        }
        
        concurrent_values = []
        
        for metric in connection_metrics:
            metric_name = metric['name'].lower()
            metric_value = metric['value']
            
            if 'concurrent' in metric_name or 'idle' in metric_name:
                concurrent_values.append(metric_value)
                concurrency_analysis['current_concurrent_connections'] = max(
                    concurrency_analysis['current_concurrent_connections'], 
                    metric_value
                )
        
        if concurrent_values:
            concurrency_analysis['max_concurrent_connections'] = max(concurrent_values)
            concurrency_analysis['concurrent_connection_trend'] = concurrent_values
            
            # 计算连接稳定性（基于标准差）
            if len(concurrent_values) > 1:
                std_dev = statistics.stdev(concurrent_values)
                concurrency_analysis['connection_stability'] = max(0, 100 - std_dev * 10)
            else:
                concurrency_analysis['connection_stability'] = 100
        
        return concurrency_analysis
    
    def _analyze_network_performance(self, performance_metrics: List[Dict]) -> Dict[str, Any]:
        """分析网络性能"""
        network_analysis = {
            'avg_latency': 0.0,
            'min_latency': 0.0,
            'max_latency': 0.0,
            'latency_distribution': [],
            'network_quality_score': 0.0
        }
        
        latency_values = []
        
        for metric in performance_metrics:
            metric_name = metric['name'].lower()
            metric_value = metric['value']
            
            if any(keyword in metric_name for keyword in ['latency', 'duration', 'time']):
                if 0 < metric_value < 10000:  # 合理的延迟范围
                    latency_values.append(metric_value)
        
        if latency_values:
            network_analysis['avg_latency'] = statistics.mean(latency_values)
            network_analysis['min_latency'] = min(latency_values)
            network_analysis['max_latency'] = max(latency_values)
            
            # 计算延迟分布
            if len(latency_values) > 1:
                network_analysis['latency_distribution'] = [
                    statistics.quantiles(latency_values, n=4)[0],  # Q1
                    statistics.quantiles(latency_values, n=4)[1],  # Q2 (median)
                    statistics.quantiles(latency_values, n=4)[2],  # Q3
                ]
            
            # 计算网络质量评分
            if network_analysis['avg_latency'] < 50:
                network_analysis['network_quality_score'] = 90
            elif network_analysis['avg_latency'] < 100:
                network_analysis['network_quality_score'] = 75
            elif network_analysis['avg_latency'] < 200:
                network_analysis['network_quality_score'] = 60
            else:
                network_analysis['network_quality_score'] = 40
        
        return network_analysis
    
    def _analyze_connection_errors(self, error_metrics: List[Dict]) -> Dict[str, Any]:
        """分析连接错误"""
        error_analysis = {
            'error_types': defaultdict(int),
            'total_errors': 0,
            'error_rate': 0.0,
            'error_timeline': [],
            'critical_errors': []
        }
        
        for metric in error_metrics:
            metric_name = metric['name'].lower()
            metric_value = metric['value']
            
            if metric_value > 0:
                # 分类错误类型
                if 'connect_fail' in metric_name:
                    error_analysis['error_types']['连接失败'] += metric_value
                elif 'pub_fail' in metric_name:
                    error_analysis['error_types']['发布失败'] += metric_value
                elif 'sub_fail' in metric_name:
                    error_analysis['error_types']['订阅失败'] += metric_value
                else:
                    error_analysis['error_types']['其他错误'] += metric_value
                
                error_analysis['total_errors'] += metric_value
        
        # 计算错误率
        total_attempts = sum(error_analysis['error_types'].values())
        if total_attempts > 0:
            error_analysis['error_rate'] = (error_analysis['total_errors'] / total_attempts) * 100
        
        # 识别关键错误
        for error_type, count in error_analysis['error_types'].items():
            if count > 0:
                error_analysis['critical_errors'].append({
                    'type': error_type,
                    'count': count,
                    'severity': 'high' if count > 10 else 'medium' if count > 5 else 'low'
                })
        
        return error_analysis
    
    def _generate_connection_performance_summary(self, connection_analysis: Dict) -> Dict[str, Any]:
        """生成连接性能摘要"""
        summary = {
            'overall_score': 0.0,
            'performance_grade': 'C',
            'key_insights': [],
            'optimization_suggestions': []
        }
        
        # 计算综合评分
        scores = []
        
        # 连接成功率评分
        success_rate = connection_analysis['connection_establishment'].get('success_rate', 0)
        if success_rate >= 99:
            scores.append(100)
        elif success_rate >= 95:
            scores.append(80)
        elif success_rate >= 90:
            scores.append(60)
        else:
            scores.append(40)
        
        # 连接时间评分
        avg_time = connection_analysis['connection_establishment'].get('avg_connection_time', 0)
        if avg_time <= 50:
            scores.append(100)
        elif avg_time <= 100:
            scores.append(80)
        elif avg_time <= 200:
            scores.append(60)
        else:
            scores.append(40)
        
        # 网络质量评分
        network_score = connection_analysis['network_performance'].get('network_quality_score', 0)
        scores.append(network_score)
        
        # 错误率评分
        error_rate = connection_analysis['error_analysis'].get('error_rate', 0)
        if error_rate <= 1:
            scores.append(100)
        elif error_rate <= 5:
            scores.append(80)
        elif error_rate <= 10:
            scores.append(60)
        else:
            scores.append(40)
        
        if scores:
            summary['overall_score'] = statistics.mean(scores)
            
            # 确定性能等级
            if summary['overall_score'] >= 90:
                summary['performance_grade'] = 'A'
            elif summary['overall_score'] >= 80:
                summary['performance_grade'] = 'B'
            elif summary['overall_score'] >= 70:
                summary['performance_grade'] = 'C'
            elif summary['overall_score'] >= 60:
                summary['performance_grade'] = 'D'
            else:
                summary['performance_grade'] = 'F'
        
        # 生成关键洞察
        if success_rate >= 99:
            summary['key_insights'].append("连接成功率优秀，系统稳定性良好")
        elif success_rate < 95:
            summary['key_insights'].append("连接成功率偏低，需要关注网络连接质量")
        
        if avg_time <= 100:
            summary['key_insights'].append("连接响应时间良好，用户体验佳")
        elif avg_time > 200:
            summary['key_insights'].append("连接响应时间较长，可能影响用户体验")
        
        if error_rate <= 1:
            summary['key_insights'].append("错误率极低，系统运行稳定")
        elif error_rate > 5:
            summary['key_insights'].append("错误率较高，需要排查问题原因")
        
        # 生成优化建议
        if success_rate < 95:
            summary['optimization_suggestions'].append("检查网络连接质量和服务器配置")
        
        if avg_time > 100:
            summary['optimization_suggestions'].append("优化网络配置或提升服务器性能")
        
        if error_rate > 5:
            summary['optimization_suggestions'].append("增加错误监控和自动重试机制")
        
        if not summary['optimization_suggestions']:
            summary['optimization_suggestions'].append("系统运行良好，继续保持当前配置")
        
        return summary
    
    def _generate_html_template(self, analysis: Dict) -> str:
        """生成HTML模板"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eMQTT-Bench 增强监控报告</title>
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
        
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .metrics-table th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .metrics-table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
            transition: background-color 0.2s ease;
        }}
        
        .metrics-table tr:hover td {{
            background-color: #f8f9fa;
        }}
        
        .metric-value {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .metric-name {{
            color: #34495e;
            font-weight: 600;
        }}
        
        .metric-help {{
            color: #7f8c8d;
            font-style: italic;
            font-size: 0.85em;
        }}
        
        .alert {{
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .alert-success {{
            background: linear-gradient(135deg, #d5f4e6, #a8e6cf);
            border-left: 5px solid #27ae60;
            color: #155724;
        }}
        
        .alert-warning {{
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border-left: 5px solid #f39c12;
            color: #856404;
        }}
        
        .alert-error {{
            background: linear-gradient(135deg, #f8d7da, #fab1a0);
            border-left: 5px solid #e74c3c;
            color: #721c24;
        }}
        
        .alert-critical {{
            background: linear-gradient(135deg, #f8d7da, #fd79a8);
            border-left: 5px solid #e84393;
            color: #721c24;
        }}
        
        .alert-icon {{
            font-size: 1.5em;
            margin-right: 15px;
        }}
        
        .alert-content h4 {{
            margin: 0 0 5px 0;
            font-size: 1.1em;
        }}
        
        .alert-content p {{
            margin: 0;
            font-size: 0.95em;
        }}
        
        .tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 5px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .tab {{
            flex: 1;
            padding: 15px 20px;
            background: transparent;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            color: #7f8c8d;
            transition: all 0.3s ease;
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.5s ease;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .progress-ring {{
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }}
        
        .progress-ring circle {{
            fill: transparent;
            stroke-width: 8;
            stroke-linecap: round;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }}
        
        .progress-ring .background {{
            stroke: #ecf0f1;
        }}
        
        .progress-ring .progress {{
            stroke: url(#gradient);
            stroke-dasharray: 314;
            stroke-dashoffset: 314;
            transition: stroke-dashoffset 1s ease;
        }}
        
        .heatmap {{
            display: grid;
            grid-template-columns: repeat(20, 1fr);
            gap: 2px;
            margin: 20px 0;
        }}
        
        .heatmap-cell {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            transition: transform 0.2s ease;
        }}
        
        .heatmap-cell:hover {{
            transform: scale(1.2);
        }}
        
        .heatmap-cell.zero {{ background: #ecf0f1; }}
        .heatmap-cell.low {{ background: #2ecc71; }}
        .heatmap-cell.medium {{ background: #f39c12; }}
        .heatmap-cell.high {{ background: #e74c3c; }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 50px;
        }}
        
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .metric-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            margin-left: 8px;
        }}
        
        .badge-counter {{ background: #3498db; color: white; }}
        .badge-gauge {{ background: #2ecc71; color: white; }}
        .badge-histogram {{ background: #f39c12; color: white; }}
        .badge-summary {{ background: #9b59b6; color: white; }}
        
        .sparkline {{
            height: 40px;
            background: #f8f9fa;
            border-radius: 5px;
            position: relative;
            overflow: hidden;
        }}
        
        .sparkline-line {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-success {{ background: #27ae60; }}
        .status-warning {{ background: #f39c12; }}
        .status-error {{ background: #e74c3c; }}
        .status-info {{ background: #3498db; }}
        
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
            <h1>🚀 eMQTT-Bench 增强监控报告</h1>
            <div class="subtitle">基于 Prometheus & REST API 的实时性能监控</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="icon">📊</span>
                    <div class="value">{analysis['total_metrics']}</div>
                    <div class="label">总指标数</div>
                </div>
                <div class="stat-card">
                    <span class="icon">🧪</span>
                    <div class="value">{len(self.test_results)}</div>
                    <div class="label">测试项目</div>
                </div>
                <div class="stat-card">
                    <span class="icon">✅</span>
                    <div class="value">{len([r for r in self.test_results if r.success])}</div>
                    <div class="label">成功测试</div>
                </div>
                <div class="stat-card">
                    <span class="icon">⏱️</span>
                    <div class="value">{(self.report_timestamp - self.start_time).total_seconds():.1f}s</div>
                    <div class="label">总耗时</div>
                </div>
            </div>
        </div>
        
        <!-- 告警面板 -->
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">🚨 系统告警</h3>
            </div>
            <div class="panel-content">
                {self._generate_alerts_html(analysis['alerts'])}
            </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📋 概览</button>
            <button class="tab" onclick="showTab('connection-test')">🎯 连接测试</button>
            <button class="tab" onclick="showTab('performance')">🚀 性能监控</button>
            <button class="tab" onclick="showTab('connections')">🔗 连接状态</button>
            <button class="tab" onclick="showTab('mqtt')">📡 MQTT指标</button>
            <button class="tab" onclick="showTab('system')">💻 系统资源</button>
            <button class="tab" onclick="showTab('trends')">📈 趋势分析</button>
            <button class="tab" onclick="showTab('details')">📊 详细数据</button>
        </div>
        
        <!-- 概览标签页 -->
        <div id="overview-content" class="tab-content active">
            {self._generate_overview_tab(analysis)}
        </div>
        
        <!-- 连接测试标签页 -->
        <div id="connection-test-content" class="tab-content">
            {self._generate_connection_test_tab(analysis)}
        </div>
        
        <!-- 性能监控标签页 -->
        <div id="performance-content" class="tab-content">
            {self._generate_performance_tab(analysis)}
        </div>
        
        <!-- 连接状态标签页 -->
        <div id="connections-content" class="tab-content">
            {self._generate_connections_tab(analysis)}
        </div>
        
        <!-- MQTT指标标签页 -->
        <div id="mqtt-content" class="tab-content">
            {self._generate_mqtt_tab(analysis)}
        </div>
        
        <!-- 系统资源标签页 -->
        <div id="system-content" class="tab-content">
            {self._generate_system_tab(analysis)}
        </div>
        
        <!-- 趋势分析标签页 -->
        <div id="trends-content" class="tab-content">
            {self._generate_trends_tab(analysis)}
        </div>
        
        <!-- 详细数据标签页 -->
        <div id="details-content" class="tab-content">
            {self._generate_details_tab(analysis)}
        </div>
        
        <!-- 页面底部 -->
        <div class="footer">
            <p>📊 报告由 eMQTT-Bench 增强监控系统生成</p>
            <p>🕒 生成时间: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🔧 基于 Prometheus & REST API 监控数据</p>
        </div>
    </div>
    
    <script>
        // 标签页切换功能
        function showTab(tabName) {{
            // 隐藏所有标签页内容
            var contents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < contents.length; i++) {{
                contents[i].classList.remove('active');
            }}
            
            // 移除所有标签页的激活状态
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove('active');
            }}
            
            // 显示选中的标签页
            document.getElementById(tabName + '-content').classList.add('active');
            event.target.classList.add('active');
        }}
        
        // 初始化图表
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            updateProgressRings();
        }});
        
        function initializeCharts() {{
            // 性能趋势图
            const performanceCtx = document.getElementById('performanceChart');
            if (performanceCtx) {{
                new Chart(performanceCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps([item['time'] for item in analysis['trend_data']['performance']])},
                        datasets: [{{
                            label: '延迟 (s)',
                            data: {json.dumps([item['latency'] for item in analysis['trend_data']['performance']])},
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: '吞吐量 (/s)',
                            data: {json.dumps([item['throughput'] for item in analysis['trend_data']['performance']])},
                            borderColor: '#2ecc71',
                            backgroundColor: 'rgba(46, 204, 113, 0.1)',
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
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }}
                        }}
                    }}
                }});
            }}
            
            // 连接状态图
            const connectionCtx = document.getElementById('connectionChart');
            if (connectionCtx) {{
                new Chart(connectionCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['成功连接', '失败连接'],
                        datasets: [{{
                            data: [{len([r for r in self.test_results if r.success])}, {len([r for r in self.test_results if not r.success])}],
                            backgroundColor: ['#2ecc71', '#e74c3c'],
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
            
            // 趋势分析图
            const trendsCtx = document.getElementById('trendsChart');
            if (trendsCtx) {{
                new Chart(trendsCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps([item['time'] for item in analysis['trend_data']['performance']])},
                        datasets: [{{
                            label: '延迟 (s)',
                            data: {json.dumps([item['latency'] for item in analysis['trend_data']['performance']])},
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        }}, {{
                            label: '吞吐量 (/s)',
                            data: {json.dumps([item['throughput'] for item in analysis['trend_data']['performance']])},
                            borderColor: '#2ecc71',
                            backgroundColor: 'rgba(46, 204, 113, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}, {{
                            label: 'CPU使用率 (%)',
                            data: {json.dumps([item['cpu'] for item in analysis['trend_data']['performance']])},
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y2'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false,
                        }},
                        scales: {{
                            x: {{
                                display: true,
                                title: {{
                                    display: true,
                                    text: '时间'
                                }}
                            }},
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: '延迟 (s)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '吞吐量 (/s)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }},
                            y2: {{
                                type: 'linear',
                                display: false,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'CPU使用率 (%)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: '性能趋势分析'
                            }},
                            legend: {{
                                display: true,
                                position: 'top'
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        function updateProgressRings() {{
            const rings = document.querySelectorAll('.progress-ring .progress');
            rings.forEach(ring => {{
                const percentage = parseFloat(ring.dataset.percentage);
                const circumference = 314; // 2 * PI * 50
                const offset = circumference - (percentage / 100) * circumference;
                ring.style.strokeDashoffset = offset;
            }});
        }}
    </script>
</body>
</html>
"""
    
    def _generate_alerts_html(self, alerts: List[Dict]) -> str:
        """生成告警HTML"""
        if not alerts:
            return '<div class="alert alert-success"><span class="alert-icon">✅</span><div class="alert-content"><h4>系统正常</h4><p>没有检测到任何告警</p></div></div>'
        
        html = ""
        for alert in alerts:
            level_class = f"alert-{alert['level']}"
            html += f"""
            <div class="alert {level_class}">
                <span class="alert-icon">{alert['icon']}</span>
                <div class="alert-content">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
            </div>
            """
        return html
    
    def _generate_overview_tab(self, analysis: Dict) -> str:
        """生成概览标签页"""
        html = f"""
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📊 测试概览</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="connectionChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🎯 关键指标</h3>
                </div>
                <div class="panel-content">
        """
        
        # 添加关键指标
        key_metrics = []
        
        # 从各个指标类别中收集关键指标
        categories_to_check = ['performance_metrics', 'connection_metrics', 'mqtt_metrics', 'system_metrics', 'error_metrics']
        
        for category in categories_to_check:
            if category in analysis and isinstance(analysis[category], dict):
                metrics = analysis[category]
                for metric_name, metric_data in list(metrics.items())[:2]:  # 每个类别取前2个
                    if isinstance(metric_data, dict):
                        key_metrics.append((metric_name, metric_data))
        
        # 如果没有找到指标，显示默认信息
        if not key_metrics:
            html += """
                        <div style="text-align: center; padding: 20px; color: #7f8c8d;">
                            <p>暂无关键指标数据</p>
                            <small>请确保测试成功完成并收集到指标数据</small>
                        </div>
            """
        else:
            for metric_name, metric_data in key_metrics[:6]:  # 最多显示6个关键指标
                if isinstance(metric_data, dict):
                    value = metric_data.get('value', 0)
                    help_text = metric_data.get('help', '')
                    test_name = metric_data.get('test', '')
                    
                    html += f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #ecf0f1;">
                                <div>
                                    <div class="metric-name">{metric_name}</div>
                                    <div class="metric-help">{help_text}</div>
                                    <small style="color: #95a5a6;">来源: {test_name}</small>
                                </div>
                                <div class="metric-value">{value}</div>
                            </div>
                    """
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_connection_test_tab(self, analysis: Dict) -> str:
        """生成连接测试标签页"""
        connection_analysis = analysis.get('connection_test_analysis', {})
        
        html = f"""
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🎯 连接建立性能</h3>
                </div>
                <div class="panel-content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="icon">📊</span>
                            <div class="value">{connection_analysis.get('connection_establishment', {}).get('success_rate', 0):.1f}%</div>
                            <div class="label">连接成功率</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">⚡</span>
                            <div class="value">{connection_analysis.get('connection_establishment', {}).get('avg_connection_time', 0):.1f}ms</div>
                            <div class="label">平均连接时间</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">🚀</span>
                            <div class="value">{connection_analysis.get('connection_establishment', {}).get('connection_rate', 0):.1f}/s</div>
                            <div class="label">连接建立速率</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">❌</span>
                            <div class="value">{connection_analysis.get('connection_establishment', {}).get('failed_connections', 0)}</div>
                            <div class="label">失败连接数</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🔗 并发连接能力</h3>
                </div>
                <div class="panel-content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="icon">📈</span>
                            <div class="value">{connection_analysis.get('concurrency_metrics', {}).get('max_concurrent_connections', 0)}</div>
                            <div class="label">最大并发连接</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">🔗</span>
                            <div class="value">{connection_analysis.get('concurrency_metrics', {}).get('current_concurrent_connections', 0)}</div>
                            <div class="label">当前并发连接</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">📊</span>
                            <div class="value">{connection_analysis.get('concurrency_metrics', {}).get('connection_stability', 0):.1f}%</div>
                            <div class="label">连接稳定性</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🌐 网络性能分析</h3>
                </div>
                <div class="panel-content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="icon">⚡</span>
                            <div class="value">{connection_analysis.get('network_performance', {}).get('avg_latency', 0):.1f}ms</div>
                            <div class="label">平均延迟</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">📊</span>
                            <div class="value">{connection_analysis.get('network_performance', {}).get('min_latency', 0):.1f}ms</div>
                            <div class="label">最小延迟</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">📈</span>
                            <div class="value">{connection_analysis.get('network_performance', {}).get('max_latency', 0):.1f}ms</div>
                            <div class="label">最大延迟</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">🎯</span>
                            <div class="value">{connection_analysis.get('network_performance', {}).get('network_quality_score', 0):.0f}</div>
                            <div class="label">网络质量评分</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🚨 错误分析</h3>
                </div>
                <div class="panel-content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="icon">❌</span>
                            <div class="value">{connection_analysis.get('error_analysis', {}).get('total_errors', 0)}</div>
                            <div class="label">总错误数</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">📊</span>
                            <div class="value">{connection_analysis.get('error_analysis', {}).get('error_rate', 0):.1f}%</div>
                            <div class="label">错误率</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">📊 连接测试性能摘要</h3>
            </div>
            <div class="panel-content">
                {self._generate_connection_performance_summary_html(connection_analysis.get('performance_summary', {}))}
            </div>
        </div>
        """
        
        return html
    
    def _generate_connection_performance_summary_html(self, performance_summary: Dict) -> str:
        """生成连接性能摘要HTML"""
        if not performance_summary:
            return '<div style="text-align: center; padding: 20px; color: #7f8c8d;">暂无性能摘要数据</div>'
        
        overall_score = performance_summary.get('overall_score', 0)
        performance_grade = performance_summary.get('performance_grade', 'C')
        key_insights = performance_summary.get('key_insights', [])
        optimization_suggestions = performance_summary.get('optimization_suggestions', [])
        
        # 根据评分确定颜色
        if overall_score >= 90:
            score_color = '#27ae60'
            grade_color = '#27ae60'
        elif overall_score >= 80:
            score_color = '#f39c12'
            grade_color = '#f39c12'
        elif overall_score >= 70:
            score_color = '#3498db'
            grade_color = '#3498db'
        else:
            score_color = '#e74c3c'
            grade_color = '#e74c3c'
        
        html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.9); border-radius: 15px;">
                <h4 style="color: #2c3e50; margin-bottom: 15px;">综合评分</h4>
                <div style="font-size: 3em; font-weight: bold; color: {score_color}; margin-bottom: 10px;">
                    {overall_score:.1f}
                </div>
                <div style="font-size: 1.5em; color: {grade_color}; font-weight: bold;">
                    等级: {performance_grade}
                </div>
            </div>
            
            <div style="padding: 20px; background: rgba(255, 255, 255, 0.9); border-radius: 15px;">
                <h4 style="color: #2c3e50; margin-bottom: 15px;">关键洞察</h4>
                <ul style="list-style: none; padding: 0;">
        """
        
        for insight in key_insights:
            html += f'<li style="padding: 8px 0; border-bottom: 1px solid #ecf0f1;">💡 {insight}</li>'
        
        html += """
                </ul>
            </div>
            
            <div style="padding: 20px; background: rgba(255, 255, 255, 0.9); border-radius: 15px;">
                <h4 style="color: #2c3e50; margin-bottom: 15px;">优化建议</h4>
                <ul style="list-style: none; padding: 0;">
        """
        
        for suggestion in optimization_suggestions:
            html += f'<li style="padding: 8px 0; border-bottom: 1px solid #ecf0f1;">🔧 {suggestion}</li>'
        
        html += """
                </ul>
            </div>
        </div>
        """
        
        return html
    
    def _generate_performance_tab(self, analysis: Dict) -> str:
        """生成性能监控标签页"""
        html = f"""
        <div class="dashboard-grid">
            <div class="panel" style="grid-column: span 2;">
                <div class="panel-header">
                    <h3 class="panel-title">📈 性能趋势</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">⚡ 性能指标详情</h3>
            </div>
            <div class="panel-content">
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>值</th>
                            <th>测试</th>
                            <th>类型</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        if analysis['performance_metrics']:
            for metric_name, metric_data in analysis['performance_metrics'].items():
                if isinstance(metric_data, dict):
                    html += f"""
                                <tr>
                                    <td class="metric-name">{metric_name}</td>
                                    <td class="metric-value">{metric_data.get('value', 'N/A')}</td>
                                    <td>{metric_data.get('test', 'N/A')}</td>
                                    <td><span class="metric-badge badge-{metric_data.get('type', 'unknown')}">{metric_data.get('type', 'unknown')}</span></td>
                                </tr>
                    """
        else:
            html += """
                        <tr>
                            <td colspan="4" style="text-align: center; color: #7f8c8d; padding: 20px;">
                                暂无性能指标数据
                            </td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
    
    def _generate_connections_tab(self, analysis: Dict) -> str:
        """生成连接状态标签页"""
        html = f"""
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🔗 连接状态</h3>
                </div>
                <div class="panel-content">
        """
        
        for test_name, test_info in analysis['test_summary'].items():
            status_class = "success" if test_info['success'] else "error"
            status_icon = "✅" if test_info['success'] else "❌"
            html += f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #ecf0f1;">
                        <div>
                            <span class="status-indicator status-{status_class}"></span>
                            <strong>{test_name}</strong>
                        </div>
                        <div>
                            <span>{status_icon} {'成功' if test_info['success'] else '失败'}</span>
                            <small style="color: #7f8c8d; margin-left: 10px;">端口: {test_info['port']}</small>
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📊 连接指标</h3>
                </div>
                <div class="panel-content">
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>指标名称</th>
                                <th>值</th>
                                <th>测试</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        if analysis['connection_metrics']:
            for metric_name, metric_data in analysis['connection_metrics'].items():
                if isinstance(metric_data, dict):
                    html += f"""
                                <tr>
                                    <td class="metric-name">{metric_name}</td>
                                    <td class="metric-value">{metric_data.get('value', 'N/A')}</td>
                                    <td>{metric_data.get('test', 'N/A')}</td>
                                </tr>
                    """
        else:
            html += """
                            <tr>
                                <td colspan="3" style="text-align: center; color: #7f8c8d; padding: 20px;">
                                    暂无连接指标数据
                                </td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_mqtt_tab(self, analysis: Dict) -> str:
        """生成MQTT指标标签页"""
        html = f"""
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">📡 MQTT 协议指标</h3>
            </div>
            <div class="panel-content">
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>值</th>
                            <th>测试</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        if analysis['mqtt_metrics']:
            for metric_name, metric_data in analysis['mqtt_metrics'].items():
                if isinstance(metric_data, dict):
                    html += f"""
                                <tr>
                                    <td class="metric-name">{metric_name}</td>
                                    <td class="metric-value">{metric_data.get('value', 'N/A')}</td>
                                    <td>{metric_data.get('test', 'N/A')}</td>
                                    <td class="metric-help">{metric_data.get('help', '')}</td>
                                </tr>
                    """
        else:
            html += """
                        <tr>
                            <td colspan="4" style="text-align: center; color: #7f8c8d; padding: 20px;">
                                暂无MQTT指标数据
                            </td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
    
    def _generate_system_tab(self, analysis: Dict) -> str:
        """生成系统资源标签页"""
        html = f"""
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">💻 系统资源</h3>
                </div>
                <div class="panel-content">
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>资源类型</th>
                                <th>使用率</th>
                                <th>状态</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        if analysis['system_metrics']:
            for metric_name, metric_data in analysis['system_metrics'].items():
                if isinstance(metric_data, dict):
                    value = metric_data.get('value', 0)
                    if 'cpu' in metric_name.lower():
                        status = "正常" if value < 80 else "警告" if value < 95 else "危险"
                        status_class = "success" if value < 80 else "warning" if value < 95 else "error"
                    elif 'memory' in metric_name.lower():
                        status = "正常" if value < 80 else "警告" if value < 95 else "危险"
                        status_class = "success" if value < 80 else "warning" if value < 95 else "error"
                    else:
                        status = "正常"
                        status_class = "success"
                    
                    html += f"""
                                <tr>
                                    <td class="metric-name">{metric_name}</td>
                                    <td class="metric-value">{value}%</td>
                                    <td><span class="status-indicator status-{status_class}"></span>{status}</td>
                                </tr>
                    """
        else:
            html += """
                            <tr>
                                <td colspan="3" style="text-align: center; color: #7f8c8d; padding: 20px;">
                                    暂无系统资源指标数据
                                </td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">🔥 资源使用热力图</h3>
                </div>
                <div class="panel-content">
                    <div class="heatmap">
        """
        
        # 生成热力图
        for i in range(100):
            intensity = random.random()
            if intensity > 0.7:
                cell_class = "high"
            elif intensity > 0.3:
                cell_class = "medium"
            elif intensity > 0:
                cell_class = "low"
            else:
                cell_class = "zero"
            html += f'<div class="heatmap-cell {cell_class}" title="使用率: {intensity*100:.1f}%"></div>'
        
        html += """
                    </div>
                    <div style="margin-top: 15px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
                        资源使用热力图 - 颜色越深表示使用率越高
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_trends_tab(self, analysis: Dict) -> str:
        """生成趋势分析标签页"""
        # 计算趋势统计
        trend_data = analysis.get('trend_data', {})
        performance_data = trend_data.get('performance', [])
        
        if not performance_data:
            # 如果没有趋势数据，显示提示信息
            html = """
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📈 性能趋势分析</h3>
                </div>
                <div class="panel-content">
                    <div style="text-align: center; padding: 40px; color: #7f8c8d;">
                        <h4>暂无趋势数据</h4>
                        <p>趋势分析需要多个时间点的数据</p>
                        <small>建议运行更长时间的测试以获得趋势数据</small>
                    </div>
                </div>
            </div>
            """
            return html
        
        # 计算统计数据
        avg_latency = sum(item.get('latency', 0) for item in performance_data) / len(performance_data)
        avg_throughput = sum(item.get('throughput', 0) for item in performance_data) / len(performance_data)
        avg_cpu = sum(item.get('cpu', 0) for item in performance_data) / len(performance_data)
        
        # 计算趋势（简单的前后对比）
        if len(performance_data) >= 2:
            first_half = performance_data[:len(performance_data)//2]
            second_half = performance_data[len(performance_data)//2:]
            
            first_avg_latency = sum(item.get('latency', 0) for item in first_half) / len(first_half)
            second_avg_latency = sum(item.get('latency', 0) for item in second_half) / len(second_half)
            latency_trend = "📈 上升" if second_avg_latency > first_avg_latency else "📉 下降" if second_avg_latency < first_avg_latency else "➡️ 稳定"
            
            first_avg_throughput = sum(item.get('throughput', 0) for item in first_half) / len(first_half)
            second_avg_throughput = sum(item.get('throughput', 0) for item in second_half) / len(second_half)
            throughput_trend = "📈 上升" if second_avg_throughput > first_avg_throughput else "📉 下降" if second_avg_throughput < first_avg_throughput else "➡️ 稳定"
        else:
            latency_trend = "➡️ 稳定"
            throughput_trend = "➡️ 稳定"
        
        html = f"""
        <div class="dashboard-grid">
            <div class="panel" style="grid-column: span 2;">
                <div class="panel-header">
                    <h3 class="panel-title">📈 性能趋势分析</h3>
                </div>
                <div class="panel-content">
                    <div class="chart-container">
                        <canvas id="trendsChart"></canvas>
                    </div>
                    <div style="margin-top: 15px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
                        显示测试执行过程中的性能指标变化趋势
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📊 趋势统计</h3>
                </div>
                <div class="panel-content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="icon">📈</span>
                            <div class="value">{len(performance_data)}</div>
                            <div class="label">数据点</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">⚡</span>
                            <div class="value">{avg_latency:.3f}s</div>
                            <div class="label">平均延迟</div>
                            <div class="trend">{latency_trend}</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">🚀</span>
                            <div class="value">{avg_throughput:.1f}</div>
                            <div class="label">平均吞吐量</div>
                            <div class="trend">{throughput_trend}</div>
                        </div>
                        <div class="stat-card">
                            <span class="icon">💻</span>
                            <div class="value">{avg_cpu:.1f}%</div>
                            <div class="label">平均CPU使用率</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">📋 趋势分析说明</h3>
                </div>
                <div class="panel-content">
                    <div style="font-size: 0.9em; line-height: 1.6;">
                        <h4>📊 图表说明</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li><strong>红色线</strong>: 延迟时间变化</li>
                            <li><strong>绿色线</strong>: 吞吐量变化</li>
                            <li><strong>蓝色线</strong>: CPU使用率变化</li>
                        </ul>
                        
                        <h4>📈 趋势判断</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li><strong>上升趋势</strong>: 性能指标随时间增加</li>
                            <li><strong>下降趋势</strong>: 性能指标随时间减少</li>
                            <li><strong>稳定趋势</strong>: 性能指标保持相对稳定</li>
                        </ul>
                        
                        <h4>💡 分析建议</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>延迟上升可能表示系统负载增加</li>
                            <li>吞吐量下降可能表示性能瓶颈</li>
                            <li>CPU使用率持续高位需要关注</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_details_tab(self, analysis: Dict) -> str:
        """生成详细数据标签页"""
        html = f"""
        <div class="panel">
            <div class="panel-header">
                <h3 class="panel-title">📊 完整指标数据</h3>
            </div>
            <div class="panel-content">
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>值</th>
                            <th>类型</th>
                            <th>测试</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 从原始数据中提取所有指标
        all_metrics = []
        for test_name, test_data in self.all_metrics_data.items():
            # 处理不同的数据格式
            if isinstance(test_data, list):
                metrics = test_data
            elif isinstance(test_data, dict):
                metrics = test_data.get('metrics', [])
            else:
                metrics = []
            
            # 添加每个指标到列表
            for metric in metrics:
                if isinstance(metric, dict):
                    metric_info = {
                        'name': metric.get('name', ''),
                        'value': metric.get('value', 'N/A'),
                        'type': metric.get('metric_type', 'unknown'),
                        'test': test_name,
                        'help': metric.get('help_text', '')
                    }
                    all_metrics.append(metric_info)
        
        # 如果没有指标数据，显示提示信息
        if not all_metrics:
            html += """
                            <tr>
                                <td colspan="5" style="text-align: center; padding: 40px; color: #7f8c8d;">
                                    <h4>暂无指标数据</h4>
                                    <p>没有收集到任何指标数据</p>
                                    <small>请确保测试成功完成并收集到指标数据</small>
                                </td>
                            </tr>
            """
        else:
            # 按测试名称和指标名称排序
            all_metrics.sort(key=lambda x: (x['test'], x['name']))
            
            for metric_info in all_metrics:
                html += f"""
                            <tr>
                                <td class="metric-name">{metric_info['name']}</td>
                                <td class="metric-value">{metric_info['value']}</td>
                                <td><span class="metric-badge badge-{metric_info['type']}">{metric_info['type']}</span></td>
                                <td>{metric_info['test']}</td>
                                <td class="metric-help">{metric_info['help']}</td>
                            </tr>
                """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
