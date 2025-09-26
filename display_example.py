#!/usr/bin/env python3
"""
eMQTT-Bench 压测结果显示系统使用示例
作者: Jaxon
日期: 2025-01-27
"""

import time
import subprocess
import threading
from benchmark_display_system import MetricsCollector, RealTimeDisplay, WebDashboard, ReportGenerator
from rich.console import Console

console = Console()

def run_emqtt_bench_test():
    """运行eMQTT-Bench测试"""
    console.print("[blue]🚀 启动 eMQTT-Bench 连接测试...[/blue]")
    
    # 华为云连接测试命令
    cmd = [
        "./emqtt_bench", "conn",
        "-h", "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com",
        "-p", "1883",
        "-c", "10",  # 10个客户端
        "-i", "100",  # 100ms间隔
        "--prefix", "speaker",
        "-P", "12345678",
        "--huawei-auth",
        "--prometheus",
        "--restapi", "9090"
    ]
    
    try:
        # 启动eMQTT-Bench
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        console.print("[green]✅ eMQTT-Bench 已启动，Prometheus监控端口: 9090[/green]")
        return process
    except Exception as e:
        console.print(f"[red]❌ 启动 eMQTT-Bench 失败: {e}[/red]")
        return None

def demo_live_display():
    """演示实时显示功能"""
    console.print("\n[cyan]📊 演示实时显示功能[/cyan]")
    
    # 创建指标收集器
    collector = MetricsCollector([9090])
    
    # 创建实时显示
    display = RealTimeDisplay(collector)
    
    console.print("[yellow]按 Ctrl+C 停止实时显示[/yellow]")
    
    try:
        display.start_live_display("conn", refresh_interval=2.0)
    except KeyboardInterrupt:
        console.print("\n[yellow]实时显示已停止[/yellow]")

def demo_web_dashboard():
    """演示Web仪表盘功能"""
    console.print("\n[cyan]🌐 演示Web仪表盘功能[/cyan]")
    
    # 创建指标收集器
    collector = MetricsCollector([9090])
    
    # 创建Web仪表盘
    dashboard = WebDashboard(collector, port=8080)
    
    console.print("[yellow]Web仪表盘将在浏览器中自动打开[/yellow]")
    console.print("[yellow]按 Ctrl+C 停止Web仪表盘[/yellow]")
    
    try:
        dashboard.start_dashboard()
    except KeyboardInterrupt:
        console.print("\n[yellow]Web仪表盘已停止[/yellow]")

def demo_report_generation():
    """演示报告生成功能"""
    console.print("\n[cyan]📋 演示报告生成功能[/cyan]")
    
    # 创建指标收集器
    collector = MetricsCollector([9090])
    
    # 收集一些数据
    console.print("[blue]正在收集指标数据...[/blue]")
    for i in range(5):
        collector.collect_metrics("conn")
        time.sleep(2)
        console.print(f"[green]已收集 {i+1}/5 组数据[/green]")
    
    # 生成报告
    generator = ReportGenerator(collector)
    report_file = generator.generate_report()
    
    console.print(f"[green]✅ 报告已生成: {report_file}[/green]")

def main():
    """主演示函数"""
    console.print("[bold blue]🎯 eMQTT-Bench 压测结果显示系统演示[/bold blue]")
    console.print("=" * 60)
    
    # 启动eMQTT-Bench测试
    emqtt_process = run_emqtt_bench_test()
    if not emqtt_process:
        return
    
    # 等待eMQTT-Bench启动
    console.print("[yellow]等待 eMQTT-Bench 启动完成...[/yellow]")
    time.sleep(5)
    
    try:
        while True:
            console.print("\n[bold cyan]请选择演示功能:[/bold cyan]")
            console.print("1. 实时显示 (Live Display)")
            console.print("2. Web仪表盘 (Web Dashboard)")
            console.print("3. 生成报告 (Generate Report)")
            console.print("4. 退出 (Exit)")
            
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                demo_live_display()
            elif choice == "2":
                demo_web_dashboard()
            elif choice == "3":
                demo_report_generation()
            elif choice == "4":
                break
            else:
                console.print("[red]无效选择，请重新输入[/red]")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]演示已中断[/yellow]")
    finally:
        # 停止eMQTT-Bench进程
        if emqtt_process:
            emqtt_process.terminate()
            console.print("[yellow]eMQTT-Bench 进程已停止[/yellow]")

if __name__ == "__main__":
    main()

