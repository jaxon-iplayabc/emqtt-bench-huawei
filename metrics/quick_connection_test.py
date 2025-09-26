#!/usr/bin/env python3
"""
快速连接测试脚本
快速体验连接测试专业分析功能
作者: Jaxon
日期: 2024-12-19
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from connection_test_dashboard import ConnectionTestDashboard
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

def generate_sample_connection_test_data():
    """生成示例连接测试数据"""
    console.print("📊 [blue]生成示例连接测试数据...[/blue]")
    
    # 生成模拟的指标历史数据
    metrics_history = []
    base_time = datetime.now() - timedelta(minutes=5)
    
    for i in range(60):  # 5分钟的数据，每秒一个数据点
        timestamp = base_time + timedelta(seconds=i)
        
        # 模拟连接数增长
        concurrent_connections = min(1000, 50 + i * 15)
        successful_connections = 95 + i * 2
        failed_connections = max(0, 5 - i // 10)
        
        # 模拟连接时间（逐渐优化）
        avg_connection_time = max(20, 100 - i * 1.2)
        
        # 模拟系统资源使用
        cpu_usage = 30 + (i % 20) * 2
        memory_usage = 40 + (i % 15) * 1.5
        
        metrics_history.append({
            'timestamp': timestamp.isoformat(),
            'total_attempts': successful_connections + failed_connections,
            'successful_connections': successful_connections,
            'failed_connections': failed_connections,
            'concurrent_connections': concurrent_connections,
            'connection_rate': 50 + i * 2,
            'error_types': {
                '连接失败': failed_connections,
                '发布失败': max(0, 2 - i // 20),
                '订阅失败': max(0, 1 - i // 30)
            },
            'system_resources': {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'memory_used_gb': 2.1 + (i % 10) * 0.1,
                'memory_total_gb': 8.0,
                'file_descriptors_count': 1250 + i * 5,
                'file_descriptors_percent': 30 + (i % 5)
            },
            'avg_connection_time': avg_connection_time
        })
    
    # 计算测试摘要
    test_summary = {
        'test_duration': 300.0,  # 5分钟
        'total_metrics_collected': 60,
        'performance_stats': {
            'connection_success_rate': 98.5,
            'avg_connection_time': 45.2,
            'connection_rate': 1250.0,
            'error_rate': 1.5,
            'max_concurrent_connections': 1000,
            'current_concurrent_connections': 1000
        },
        'connection_time_stats': {
            'min': 20.5,
            'max': 100.8,
            'mean': 45.2,
            'median': 42.1,
            'p90': 78.5,
            'p95': 95.2,
            'p99': 125.6
        },
        'error_summary': {
            '连接失败': 5,
            '发布失败': 2,
            '订阅失败': 1
        },
        'system_resource_summary': {
            'cpu_usage': {'avg': 45.2, 'max': 78.5, 'min': 30.0},
            'memory_usage': {'avg': 55.1, 'max': 70.2, 'min': 40.0}
        }
    }
    
    return {
        'test_summary': test_summary,
        'metrics_history': metrics_history
    }

def run_quick_connection_test():
    """运行快速连接测试"""
    console.print("🚀 [bold blue]eMQTT-Bench 快速连接测试演示[/bold blue]")
    console.print("=" * 60)
    console.print("✨ [yellow]使用模拟数据演示连接测试专业分析功能[/yellow]")
    console.print("")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        # 生成示例数据
        task1 = progress.add_task("生成示例连接测试数据...", total=100)
        for i in range(100):
            time.sleep(0.02)
            progress.advance(task1)
        
        # 生成仪表盘
        task2 = progress.add_task("生成专业连接测试仪表盘...", total=100)
        sample_data = generate_sample_connection_test_data()
        
        for i in range(100):
            time.sleep(0.01)
            progress.advance(task2)
    
    # 生成仪表盘
    console.print("🎨 [blue]生成专业连接测试仪表盘...[/blue]")
    dashboard = ConnectionTestDashboard(sample_data)
    dashboard_file = dashboard.generate_dashboard()
    
    # 显示结果
    console.print("\n✅ [bold green]快速连接测试演示完成![/bold green]")
    console.print("")
    
    # 显示关键指标
    performance_stats = sample_data['test_summary']['performance_stats']
    console.print("📊 [blue]关键指标摘要:[/blue]")
    console.print(f"   🎯 连接成功率: [green]{performance_stats['connection_success_rate']:.1f}%[/green]")
    console.print(f"   ⚡ 平均连接时间: [green]{performance_stats['avg_connection_time']:.1f}ms[/green]")
    console.print(f"   🚀 连接建立速率: [green]{performance_stats['connection_rate']:.1f}/s[/green]")
    console.print(f"   🔗 最大并发连接: [green]{performance_stats['max_concurrent_connections']}[/green]")
    console.print(f"   ❌ 错误率: [green]{performance_stats['error_rate']:.1f}%[/green]")
    
    console.print(f"\n📁 [blue]生成的文件:[/blue]")
    console.print(f"   🎨 专业仪表盘: [green]{dashboard_file}[/green]")
    
    # 询问是否启动Web服务器
    console.print("")
    if console.input("🌐 是否启动Web服务器查看仪表盘? (y/N): ").lower() in ['y', 'yes']:
        console.print("🌐 [blue]启动Web仪表盘服务器...[/blue]")
        try:
            if dashboard.start_web_server():
                console.print("✅ [green]Web仪表盘已启动，浏览器将自动打开[/green]")
                console.print("💡 [dim]按 Ctrl+C 停止服务器[/dim]")
                
                # 保持服务器运行
                while True:
                    time.sleep(1)
            else:
                console.print("❌ [red]Web服务器启动失败[/red]")
        except KeyboardInterrupt:
            console.print("\n⏹️ [yellow]停止Web服务器[/yellow]")
        finally:
            dashboard.stop_web_server()
    else:
        console.print("💡 [dim]您可以直接打开生成的HTML文件查看仪表盘[/dim]")

def main():
    """主函数"""
    try:
        run_quick_connection_test()
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]用户中断演示[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]演示失败: {e}[/red]")

if __name__ == "__main__":
    main()
