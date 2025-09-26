#!/usr/bin/env python3
"""
连接测试功能集成脚本
将新的连接测试指标收集器和仪表盘集成到主系统中
作者: Jaxon
日期: 2024-12-19
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from connection_test_metrics_collector import ConnectionTestMetricsCollector
from connection_test_dashboard import ConnectionTestDashboard
from enhanced_report_generator import EnhancedReportGenerator
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()

class ConnectionTestIntegration:
    """连接测试功能集成器"""
    
    def __init__(self):
        self.metrics_collector = None
        self.dashboard = None
        self.running = False
        self.start_time = None
        
    def run_connection_test_analysis(self, prometheus_port: int = 9090, 
                                   collection_interval: float = 1.0,
                                   test_duration: int = 60):
        """运行连接测试分析"""
        console.print("🎯 [bold blue]eMQTT-Bench 连接测试专业分析[/bold blue]")
        console.print("=" * 60)
        
        try:
            # 1. 启动指标收集器
            console.print(Panel.fit("[bold blue]📊 启动连接测试指标收集器[/bold blue]"))
            self.metrics_collector = ConnectionTestMetricsCollector(prometheus_port)
            self.metrics_collector.start_collection(collection_interval)
            self.start_time = datetime.now()
            self.running = True
            
            # 2. 显示实时监控信息
            self._show_real_time_monitoring(test_duration)
            
            # 3. 停止收集并生成报告
            console.print("\n📊 [bold blue]生成连接测试分析报告[/bold blue]")
            self._generate_analysis_reports()
            
        except KeyboardInterrupt:
            console.print("\n⏹️ [yellow]用户中断测试[/yellow]")
        except Exception as e:
            console.print(f"\n❌ [red]连接测试分析失败: {e}[/red]")
        finally:
            self._cleanup()
    
    def _show_real_time_monitoring(self, test_duration: int):
        """显示实时监控信息"""
        console.print(f"⏱️ [green]开始实时监控 (持续 {test_duration} 秒)[/green]")
        console.print("💡 [dim]按 Ctrl+C 可提前结束监控[/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("连接测试监控中...", total=test_duration)
            
            start_time = time.time()
            while self.running and (time.time() - start_time) < test_duration:
                # 显示实时统计
                if self.metrics_collector and self.metrics_collector.metrics_history:
                    latest_metrics = self.metrics_collector.metrics_history[-1]
                    progress.update(
                        task,
                        description=f"连接测试监控中... 成功率: {self.metrics_collector.performance_stats.get('connection_success_rate', 0):.1f}%"
                    )
                
                time.sleep(1)
                progress.advance(task)
    
    def _generate_analysis_reports(self):
        """生成分析报告"""
        if not self.metrics_collector:
            console.print("❌ [red]没有收集到指标数据[/red]")
            return
        
        # 1. 获取性能摘要
        performance_summary = self.metrics_collector.get_performance_summary()
        
        # 2. 导出指标数据
        metrics_file = self.metrics_collector.export_metrics()
        
        # 3. 生成专业仪表盘
        console.print("🎨 [blue]生成专业连接测试仪表盘...[/blue]")
        dashboard = ConnectionTestDashboard(performance_summary)
        dashboard_file = dashboard.generate_dashboard()
        
        # 4. 显示结果摘要
        self._show_results_summary(performance_summary, metrics_file, dashboard_file)
        
        # 5. 询问是否启动Web服务器
        if Confirm.ask("是否启动Web服务器查看实时仪表盘?", default=True):
            self._start_web_dashboard(dashboard, performance_summary)
    
    def _show_results_summary(self, performance_summary: Dict, metrics_file: str, dashboard_file: str):
        """显示结果摘要"""
        console.print("\n📊 [bold green]连接测试分析结果摘要[/bold green]")
        
        # 创建结果表格
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("指标", style="cyan", width=20)
        table.add_column("值", style="green", width=15)
        table.add_column("状态", style="yellow", width=10)
        
        # 添加关键指标
        performance_stats = performance_summary.get('performance_stats', {})
        
        success_rate = performance_stats.get('connection_success_rate', 0)
        table.add_row(
            "连接成功率",
            f"{success_rate:.1f}%",
            "✅ 优秀" if success_rate >= 95 else "⚠️ 需关注" if success_rate >= 90 else "❌ 较差"
        )
        
        avg_time = performance_stats.get('avg_connection_time', 0)
        table.add_row(
            "平均连接时间",
            f"{avg_time:.1f}ms",
            "✅ 优秀" if avg_time <= 100 else "⚠️ 需关注" if avg_time <= 200 else "❌ 较差"
        )
        
        connection_rate = performance_stats.get('connection_rate', 0)
        table.add_row(
            "连接建立速率",
            f"{connection_rate:.1f}/s",
            "✅ 优秀" if connection_rate >= 1000 else "⚠️ 一般" if connection_rate >= 500 else "❌ 较低"
        )
        
        max_concurrent = performance_stats.get('max_concurrent_connections', 0)
        table.add_row(
            "最大并发连接",
            f"{max_concurrent}",
            "✅ 良好" if max_concurrent > 0 else "❌ 无数据"
        )
        
        error_rate = performance_stats.get('error_rate', 0)
        table.add_row(
            "错误率",
            f"{error_rate:.1f}%",
            "✅ 优秀" if error_rate <= 1 else "⚠️ 需关注" if error_rate <= 5 else "❌ 较高"
        )
        
        console.print(table)
        
        # 显示文件信息
        console.print(f"\n📁 [blue]生成的文件:[/blue]")
        console.print(f"   📊 指标数据: [green]{metrics_file}[/green]")
        console.print(f"   🎨 仪表盘: [green]{dashboard_file}[/green]")
    
    def _start_web_dashboard(self, dashboard: ConnectionTestDashboard, performance_summary: Dict):
        """启动Web仪表盘"""
        console.print("🌐 [blue]启动Web仪表盘服务器...[/blue]")
        
        try:
            if dashboard.start_web_server():
                console.print("✅ [green]Web仪表盘已启动[/green]")
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
    
    def _cleanup(self):
        """清理资源"""
        self.running = False
        if self.metrics_collector:
            self.metrics_collector.stop_collection()
            console.print("🧹 [blue]指标收集器已停止[/blue]")

def main():
    """主函数"""
    integration = ConnectionTestIntegration()
    
    # 获取用户输入
    console.print("🎯 [bold blue]eMQTT-Bench 连接测试专业分析工具[/bold blue]")
    console.print("=" * 60)
    
    # 配置参数
    prometheus_port = IntPrompt.ask(
        "请输入Prometheus端口", 
        default=9090
    )
    
    collection_interval = float(Prompt.ask(
        "请输入指标收集间隔(秒)", 
        default="1.0"
    ))
    
    test_duration = IntPrompt.ask(
        "请输入测试持续时间(秒)", 
        default=60
    )
    
    # 显示配置摘要
    console.print(f"\n📋 [blue]配置摘要:[/blue]")
    console.print(f"   🔌 Prometheus端口: {prometheus_port}")
    console.print(f"   ⏱️ 收集间隔: {collection_interval}秒")
    console.print(f"   ⏰ 测试时长: {test_duration}秒")
    
    if not Confirm.ask("是否开始连接测试分析?", default=True):
        console.print("[yellow]用户取消操作[/yellow]")
        return
    
    # 运行分析
    integration.run_connection_test_analysis(
        prometheus_port=prometheus_port,
        collection_interval=collection_interval,
        test_duration=test_duration
    )

if __name__ == "__main__":
    main()
