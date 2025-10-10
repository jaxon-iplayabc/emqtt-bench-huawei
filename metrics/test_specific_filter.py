#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定数据过滤器
根据不同的测试类型，自动过滤掉无效的数据指标
作者: Jaxon
日期: 2025-01-01
"""

import json
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
from rich.console import Console

console = Console()

class TestSpecificFilter:
    """测试特定数据过滤器"""
    
    def __init__(self):
        self.console = Console()
        
        # 定义每种测试类型的无效数据规则
        self.test_specific_rules = {
            "华为云连接测试": {
                "invalid_metrics": [
                    # 连接测试中pub相关的指标无意义
                    "pub_fail", "pub_overrun", "pub_succ", "pub",
                    # 订阅相关的指标无意义
                    "sub_fail", "sub", "reconnect_succ",
                    # 发布延迟在连接测试中无意义
                    "publish_latency"
                ],
                "keep_metrics": [
                    "connect_succ", "connect_fail", "connect_retried",
                    "connection_timeout", "connection_refused", "unreachable",
                    "connection_idle", "recv"
                ]
            },
            "华为云发布测试": {
                "invalid_metrics": [
                    # 发布测试中订阅相关的指标无意义
                    "sub_fail", "sub", "reconnect_succ",
                    # 连接重试在发布测试中通常无意义
                    "connect_retried"
                ],
                "keep_metrics": [
                    "pub_succ", "pub_fail", "pub_overrun", "pub",
                    "publish_latency", "connect_succ", "connect_fail",
                    "connection_timeout", "connection_refused", "unreachable",
                    "connection_idle", "recv"
                ]
            },
            "华为云订阅测试": {
                "invalid_metrics": [
                    # 订阅测试中发布相关的指标无意义
                    "pub_fail", "pub_overrun", "pub_succ", "pub",
                    "publish_latency"
                ],
                "keep_metrics": [
                    "sub_fail", "sub", "reconnect_succ",
                    "connect_succ", "connect_fail", "connect_retried",
                    "connection_timeout", "connection_refused", "unreachable",
                    "connection_idle", "recv"
                ]
            },
            "华为云广播测试": {
                "invalid_metrics": [
                    # 广播测试中某些特定指标可能无意义
                    "connect_retried"  # 广播测试通常不需要重连
                ],
                "keep_metrics": [
                    "pub_succ", "pub_fail", "pub_overrun", "pub",
                    "publish_latency", "sub_fail", "sub", "reconnect_succ",
                    "connect_succ", "connect_fail",
                    "connection_timeout", "connection_refused", "unreachable",
                    "connection_idle", "recv"
                ]
            }
        }
        
        # 通用无效数据规则
        self.common_invalid_patterns = {
            # Erlang VM系统指标（与MQTT测试性能无关）
            'erlang_vm_metrics': [
                'erlang_vm_memory_', 'erlang_vm_msacc_', 'erlang_vm_statistics_',
                'erlang_vm_dirty_', 'erlang_vm_ets_', 'erlang_vm_logical_',
                'erlang_vm_port_', 'erlang_vm_process_', 'erlang_vm_schedulers',
                'erlang_vm_smp_', 'erlang_vm_threads', 'erlang_vm_time_',
                'erlang_vm_wordsize_', 'erlang_vm_atom_', 'erlang_vm_allocators',
                'erlang_vm_thread_pool_size', 'erlang_vm_thread_pool_'
            ],
            # 直方图桶数据（通常包含大量零值桶）
            'histogram_buckets': [
                '_bucket', '_count', '_sum'
            ],
            # 重复的help_text
            'redundant_help_text': [
                'connection_idle connection_idle', 'recv recv', 'connect_fail connect_fail',
                'pub_fail pub_fail', 'pub_overrun pub_overrun', 'connect_retried connect_retried',
                'connect_succ connect_succ', 'sub_fail sub_fail', 'reconnect_succ reconnect_succ',
                'sub sub', 'publish_latency publish_latency', 'pub_succ pub_succ',
                'connection_timeout connection_timeout', 'connection_refused connection_refused',
                'unreachable unreachable', 'pub pub'
            ]
        }
    
    def filter_test_data(self, test_name: str, raw_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据测试类型过滤数据"""
        if not raw_metrics:
            return []
        
        self.console.print(f"[blue]🔍 开始过滤 {test_name} 的无效数据...[/blue]")
        
        # 获取测试特定的过滤规则
        test_rules = self.test_specific_rules.get(test_name, {})
        invalid_metrics = test_rules.get("invalid_metrics", [])
        keep_metrics = test_rules.get("keep_metrics", [])
        
        filtered_metrics = []
        removed_count = 0
        removed_details = []
        
        for metric in raw_metrics:
            metric_name = metric.get('name', '')
            metric_value = metric.get('value', 0)
            help_text = metric.get('help_text', '')
            
            # 检查是否应该过滤此指标
            should_remove = False
            removal_reason = ""
            
            # 1. 检查测试特定的无效指标
            if metric_name in invalid_metrics:
                should_remove = True
                removal_reason = f"测试特定无效指标 ({test_name})"
            
            # 2. 检查Erlang VM系统指标
            elif any(metric_name.startswith(pattern) for pattern in self.common_invalid_patterns['erlang_vm_metrics']):
                should_remove = True
                removal_reason = "Erlang VM系统指标"
            
            # 3. 检查直方图桶数据（保留有意义的桶）
            elif any(pattern in metric_name for pattern in self.common_invalid_patterns['histogram_buckets']):
                if metric_value == 0:
                    should_remove = True
                    removal_reason = "零值直方图桶"
            
            # 4. 检查重复的help_text
            elif help_text in self.common_invalid_patterns['redundant_help_text']:
                should_remove = True
                removal_reason = "重复的help_text"
            
            # 5. 检查零值且不在保留列表中的指标
            elif metric_value == 0 and metric_name not in keep_metrics:
                should_remove = True
                removal_reason = "零值且非关键指标"
            
            # 6. 检查是否有实际意义的指标
            if not should_remove:
                # 保留关键性能指标
                key_metrics = [
                    'connect_succ', 'pub_succ', 'recv', 'publish_latency',
                    'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                    'e2e_latency', 'mqtt_client_subscribe_duration'
                ]
                
                # 如果是指标名称包含关键性能指标，或者值不为0，则保留
                if not (any(key_metric in metric_name for key_metric in key_metrics) or 
                       metric_value != 0 or 
                       'duration' in metric_name or 
                       'latency' in metric_name or
                       metric_name in keep_metrics):
                    should_remove = True
                    removal_reason = "无实际意义的指标"
            
            if should_remove:
                removed_count += 1
                removed_details.append(f"{metric_name}: {removal_reason} (值: {metric_value})")
                if removed_count <= 10:  # 只显示前10个被移除的指标
                    self.console.print(f"[dim]  ❌ 移除 {metric_name}: {removal_reason} (值: {metric_value})[/dim]")
            else:
                filtered_metrics.append(metric)
        
        # 显示过滤统计
        self.console.print(f"[green]✅ 数据过滤完成: 保留 {len(filtered_metrics)} 个指标，移除 {removed_count} 个无效指标[/green]")
        
        # 显示过滤详情（如果移除的指标不多）
        if removed_count <= 20:
            self.console.print(f"[dim]移除的指标详情:[/dim]")
            for detail in removed_details[:10]:
                self.console.print(f"[dim]  • {detail}[/dim]")
        
        return filtered_metrics
    
    def filter_continuous_metrics_file(self, file_path: str) -> str:
        """过滤持续指标文件"""
        try:
            self.console.print(f"[blue]📊 处理文件: {os.path.basename(file_path)}[/blue]")
            
            # 读取原始数据
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            if not raw_data:
                self.console.print(f"[yellow]⚠️ 文件为空: {file_path}[/yellow]")
                return None
            
            # 获取测试名称
            test_name = raw_data[0].get('test_name', 'Unknown') if raw_data else 'Unknown'
            
            # 过滤每个时间点的数据
            filtered_data = []
            total_original_metrics = 0
            total_filtered_metrics = 0
            
            for data_point in raw_data:
                metrics = data_point.get('metrics', [])
                total_original_metrics += len(metrics)
                
                # 过滤指标
                filtered_metrics = self.filter_test_data(test_name, metrics)
                total_filtered_metrics += len(filtered_metrics)
                
                # 创建过滤后的数据点
                filtered_point = data_point.copy()
                filtered_point['metrics'] = filtered_metrics
                filtered_point['filter_info'] = {
                    "original_count": len(metrics),
                    "filtered_count": len(filtered_metrics),
                    "removed_count": len(metrics) - len(filtered_metrics),
                    "filter_timestamp": datetime.now().isoformat()
                }
                filtered_data.append(filtered_point)
            
            # 生成过滤后的文件名
            base_name = os.path.basename(file_path)
            name_parts = base_name.split('_')
            if len(name_parts) >= 3:
                filtered_filename = f"filtered_{name_parts[0]}_{name_parts[1]}_{name_parts[2]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                filtered_filename = f"filtered_{base_name}"
            
            # 保存过滤后的数据
            # 根据当前工作目录确定正确的路径
            if os.path.basename(os.getcwd()) == "metrics":
                # 如果在metrics目录中运行，直接使用reports/filtered
                filtered_path = os.path.join("reports", "filtered", filtered_filename)
            else:
                # 如果在项目根目录运行，使用metrics/reports/filtered
                filtered_path = os.path.join("metrics", "reports", "filtered", filtered_filename)
            os.makedirs(os.path.dirname(filtered_path), exist_ok=True)
            
            with open(filtered_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            
            # 显示过滤统计
            removed_count = total_original_metrics - total_filtered_metrics
            self.console.print(f"[green]✅ 文件过滤完成: {os.path.basename(file_path)}[/green]")
            self.console.print(f"[dim]  • 原始指标总数: {total_original_metrics}[/dim]")
            self.console.print(f"[dim]  • 过滤后指标数: {total_filtered_metrics}[/dim]")
            self.console.print(f"[dim]  • 移除指标数: {removed_count}[/dim]")
            self.console.print(f"[dim]  • 过滤后文件: {filtered_path}[/dim]")
            
            return filtered_path
            
        except Exception as e:
            self.console.print(f"[red]❌ 过滤文件失败 {file_path}: {e}[/red]")
            return None
    
    def auto_filter_all_continuous_files(self, reports_dir: str = None) -> List[str]:
        """自动过滤所有持续指标文件"""
        self.console.print("[blue]🔍 开始自动过滤所有持续指标文件...[/blue]")
        
        # 根据当前工作目录确定正确的reports目录
        if reports_dir is None:
            if os.path.basename(os.getcwd()) == "metrics":
                reports_dir = "reports"
            else:
                reports_dir = "metrics/reports"
        
        # 查找所有持续指标文件
        pattern = os.path.join(reports_dir, "continuous_metrics_*.json")
        continuous_files = glob.glob(pattern)
        
        # 如果没找到，尝试查找包含中文的文件
        if not continuous_files:
            pattern = os.path.join(reports_dir, "continuous_metrics_*测试*.json")
            continuous_files = glob.glob(pattern)
        
        if not continuous_files:
            self.console.print(f"[yellow]⚠️ 未找到持续指标文件: {pattern}[/yellow]")
            return []
        
        self.console.print(f"[blue]📁 找到 {len(continuous_files)} 个持续指标文件[/blue]")
        
        filtered_files = []
        total_original_metrics = 0
        total_filtered_metrics = 0
        
        for file_path in continuous_files:
            # 检查是否已经存在过滤后的文件
            base_name = os.path.basename(file_path)
            name_parts = base_name.split('_')
            if len(name_parts) >= 3:
                test_type = f"{name_parts[2]}_{name_parts[3]}" if len(name_parts) > 3 else name_parts[2]
                filtered_pattern = os.path.join("metrics", "reports", "filtered", f"filtered_continuous_metrics_{test_type}_*.json")
                existing_files = glob.glob(filtered_pattern)
                
                if existing_files:
                    self.console.print(f"[yellow]⚠️ 过滤文件已存在: {existing_files[0]}[/yellow]")
                    self.console.print(f"[dim]跳过重复过滤: {base_name}[/dim]")
                    continue
            
            # 过滤文件
            filtered_file = self.filter_continuous_metrics_file(file_path)
            if filtered_file:
                filtered_files.append(filtered_file)
                
                # 统计指标数量
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_data = json.load(f)
                    with open(filtered_file, 'r', encoding='utf-8') as f:
                        filtered_data = json.load(f)
                    
                    original_count = sum(len(dp.get('metrics', [])) for dp in original_data)
                    filtered_count = sum(len(dp.get('metrics', [])) for dp in filtered_data)
                    
                    total_original_metrics += original_count
                    total_filtered_metrics += filtered_count
                    
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ 统计指标数量失败: {e}[/yellow]")
        
        # 显示总体统计
        removed_count = total_original_metrics - total_filtered_metrics
        self.console.print(f"[green]🎉 所有文件过滤完成![/green]")
        self.console.print(f"[blue]📊 总体统计:[/blue]")
        self.console.print(f"[dim]  • 处理文件数: {len(filtered_files)}[/dim]")
        self.console.print(f"[dim]  • 原始指标总数: {total_original_metrics}[/dim]")
        self.console.print(f"[dim]  • 过滤后指标数: {total_filtered_metrics}[/dim]")
        self.console.print(f"[dim]  • 移除指标数: {removed_count}[/dim]")
        self.console.print(f"[dim]  • 过滤后文件保存在: metrics/reports/filtered/[/dim]")
        
        return filtered_files

def main():
    """主函数"""
    filter_processor = TestSpecificFilter()
    
    # 自动过滤所有持续指标文件
    filtered_files = filter_processor.auto_filter_all_continuous_files()
    
    if filtered_files:
        console.print(f"[green]✅ 成功过滤 {len(filtered_files)} 个文件[/green]")
        for file_path in filtered_files:
            console.print(f"[dim]  • {file_path}[/dim]")
    else:
        console.print("[yellow]⚠️ 没有找到需要过滤的文件[/yellow]")

if __name__ == "__main__":
    main()
