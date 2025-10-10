#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown详细分析报告生成器
为每种测试类型提供深入的数据分析和专业洞察
作者: Jaxon
日期: 2024-12-19
"""

import os
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import math
from utils import safe_divide, safe_percentage, safe_float, validate_metrics_data

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
        
        # 分析数据
        self.analysis_data = self._analyze_all_data()
    
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
    
    def _analyze_all_data(self) -> Dict[str, Any]:
        """分析所有测试数据"""
        analysis = {
            'overview': self._analyze_overview(),
            'connection_test': self._analyze_connection_test(),
            'publish_test': self._analyze_publish_test(),
            'subscribe_test': self._analyze_subscribe_test(),
            'huawei_test': self._analyze_huawei_test(),
            'performance_analysis': self._analyze_performance(),
            'error_analysis': self._analyze_errors(),
            'system_analysis': self._analyze_system_resources(),
            'insights': self._generate_insights(),
            'recommendations': self._generate_recommendations()
        }
        return analysis
    
    def _analyze_overview(self) -> Dict[str, Any]:
        """分析测试概览"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        # 使用安全函数计算成功率和平均持续时间
        success_rate = safe_percentage(successful_tests, total_tests)
        
        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = safe_divide(total_duration, total_tests)
        
        # 统计指标数量
        total_metrics = 0
        for test_data in self.all_metrics_data.values():
            if isinstance(test_data, list):
                total_metrics += len(test_data)
            elif isinstance(test_data, dict):
                total_metrics += len(test_data.get('metrics', []))
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'total_duration': total_duration,
            'avg_duration': avg_duration,
            'total_metrics': total_metrics,
            'test_types': [r.test_name for r in self.test_results]
        }
    
    def _analyze_connection_test(self) -> Dict[str, Any]:
        """深入分析连接测试"""
        connection_data = self._get_test_data('连接测试')
        if not connection_data:
            return {'status': 'no_data', 'message': '未找到连接测试数据'}
        
        metrics = connection_data.get('metrics', [])
        if not metrics:
            return {'status': 'no_metrics', 'message': '连接测试未收集到指标数据'}
        
        # 提取连接相关指标
        connection_metrics = self._extract_connection_metrics(metrics)
        
        analysis = {
            'status': 'analyzed',
            'connection_establishment': self._analyze_connection_establishment(connection_metrics),
            'concurrency_analysis': self._analyze_concurrency(connection_metrics),
            'network_performance': self._analyze_network_performance(connection_metrics),
            'stability_analysis': self._analyze_connection_stability(connection_metrics),
            'performance_grade': self._calculate_connection_grade(connection_metrics)
        }
        
        return analysis
    
    def _analyze_publish_test(self) -> Dict[str, Any]:
        """深入分析发布测试"""
        publish_data = self._get_test_data('发布测试')
        if not publish_data:
            return {'status': 'no_data', 'message': '未找到发布测试数据'}
        
        metrics = publish_data.get('metrics', [])
        if not metrics:
            return {'status': 'no_metrics', 'message': '发布测试未收集到指标数据'}
        
        # 提取发布相关指标
        publish_metrics = self._extract_publish_metrics(metrics)
        
        analysis = {
            'status': 'analyzed',
            'throughput_analysis': self._analyze_publish_throughput(publish_metrics),
            'latency_analysis': self._analyze_publish_latency(publish_metrics),
            'reliability_analysis': self._analyze_publish_reliability(publish_metrics),
            'scalability_analysis': self._analyze_publish_scalability(publish_metrics),
            'performance_grade': self._calculate_publish_grade(publish_metrics)
        }
        
        return analysis
    
    def _analyze_subscribe_test(self) -> Dict[str, Any]:
        """深入分析订阅测试"""
        subscribe_data = self._get_test_data('订阅测试')
        if not subscribe_data:
            return {'status': 'no_data', 'message': '未找到订阅测试数据'}
        
        metrics = subscribe_data.get('metrics', [])
        if not metrics:
            return {'status': 'no_metrics', 'message': '订阅测试未收集到指标数据'}
        
        # 提取订阅相关指标
        subscribe_metrics = self._extract_subscribe_metrics(metrics)
        
        analysis = {
            'status': 'analyzed',
            'subscription_analysis': self._analyze_subscription_performance(subscribe_metrics),
            'message_handling': self._analyze_message_handling(subscribe_metrics),
            'qos_analysis': self._analyze_qos_performance(subscribe_metrics),
            'performance_grade': self._calculate_subscribe_grade(subscribe_metrics)
        }
        
        return analysis
    
    def _analyze_huawei_test(self) -> Dict[str, Any]:
        """深入分析华为云测试"""
        huawei_data = self._get_test_data('华为云测试')
        if not huawei_data:
            return {'status': 'no_data', 'message': '未找到华为云测试数据'}
        
        metrics = huawei_data.get('metrics', [])
        if not metrics:
            return {'status': 'no_metrics', 'message': '华为云测试未收集到指标数据'}
        
        # 提取华为云相关指标
        huawei_metrics = self._extract_huawei_metrics(metrics)
        
        analysis = {
            'status': 'analyzed',
            'cloud_connectivity': self._analyze_cloud_connectivity(huawei_metrics),
            'authentication_analysis': self._analyze_authentication(huawei_metrics),
            'payload_analysis': self._analyze_payload_handling(huawei_metrics),
            'cloud_performance': self._analyze_cloud_performance(huawei_metrics),
            'performance_grade': self._calculate_huawei_grade(huawei_metrics)
        }
        
        return analysis