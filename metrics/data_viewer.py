# coding: utf-8
"""
测试数据查看器
用于查看和管理保存的测试数据，方便后续开发和分析
作者: Jaxon
日期: 2024-12-19
"""
import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from test_data_manager import TestDataManager, TestData

console = Console()

class DataViewer:
    """测试数据查看器"""
    
    def __init__(self):
        self.data_manager = TestDataManager()
    
    def show_main_menu(self):
        """显示主菜单"""
        while True:
            console.print("\n" + "="*60)
            console.print("📊 [bold blue]测试数据查看器[/bold blue]")
            console.print("="*60)
            
            console.print("\n[cyan]请选择操作:[/cyan]")
            console.print("  [green]1.[/green] 查看所有测试记录")
            console.print("  [green]2.[/green] 查看特定测试详情")
            console.print("  [green]3.[/green] 导出测试数据")
            console.print("  [green]4.[/green] 数据分析")
            console.print("  [green]5.[/green] 清理旧数据")
            console.print("  [green]6.[/green] 查看数据统计")
            console.print("  [green]0.[/green] 退出")
            
            choice = Prompt.ask("请选择", default="1")
            
            if choice == "1":
                self.show_all_tests()
            elif choice == "2":
                self.show_test_details()
            elif choice == "3":
                self.export_data()
            elif choice == "4":
                self.analyze_data()
            elif choice == "5":
                self.cleanup_data()
            elif choice == "6":
                self.show_data_statistics()
            elif choice == "0":
                console.print("[yellow]退出数据查看器[/yellow]")
                break
            else:
                console.print("[red]❌ 无效选择，请重新输入[/red]")
    
    def show_all_tests(self):
        """显示所有测试记录"""
        console.print("\n[blue]📋 所有测试记录[/blue]")
        
        all_tests = self.data_manager.get_all_tests()
        if not all_tests:
            console.print("[yellow]⚠️ 暂无测试数据[/yellow]")
            return
        
        # 创建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("测试名称", style="green", width=20)
        table.add_column("类型", style="blue", width=15)
        table.add_column("开始时间", style="yellow", width=20)
        table.add_column("持续时间", style="magenta", width=10)
        table.add_column("状态", style="red", width=8)
        table.add_column("端口", style="dim", width=6)
        
        for test in all_tests:
            status = "✅ 成功" if test['success'] else "❌ 失败"
            start_time = test['start_time'][:19] if len(test['start_time']) > 19 else test['start_time']
            
            table.add_row(
                str(test['id']),
                test['test_name'],
                test['test_type'],
                start_time,
                f"{test['duration']:.1f}s",
                status,
                str(test['port'])
            )
        
        console.print(table)
        console.print(f"\n[dim]共 {len(all_tests)} 条测试记录[/dim]")
    
    def show_test_details(self):
        """显示特定测试详情"""
        test_id = Prompt.ask("请输入测试ID")
        
        try:
            test_id = int(test_id)
            test_data = self.data_manager.load_test_data(test_id)
            
            if not test_data:
                console.print("[red]❌ 未找到指定的测试数据[/red]")
                return
            
            # 显示测试基本信息
            console.print(f"\n[blue]📊 测试详情 - {test_data.test_name}[/blue]")
            
            info_table = Table(show_header=True, header_style="bold magenta")
            info_table.add_column("属性", style="cyan", width=20)
            info_table.add_column("值", style="green", width=40)
            
            info_table.add_row("测试名称", test_data.test_name)
            info_table.add_row("测试类型", test_data.test_type)
            info_table.add_row("开始时间", test_data.start_time)
            info_table.add_row("结束时间", test_data.end_time)
            info_table.add_row("持续时间", f"{test_data.duration:.1f} 秒")
            info_table.add_row("端口", str(test_data.port))
            info_table.add_row("成功状态", "✅ 成功" if test_data.success else "❌ 失败")
            
            if test_data.error_message:
                info_table.add_row("错误信息", test_data.error_message)
            
            console.print(info_table)
            
            # 显示配置信息
            if test_data.config:
                console.print(f"\n[blue]⚙️ 测试配置[/blue]")
                config_table = Table(show_header=True, header_style="bold magenta")
                config_table.add_column("配置项", style="cyan", width=20)
                config_table.add_column("值", style="green", width=30)
                
                for key, value in test_data.config.items():
                    if key in ['huawei_sk', 'huawei_secret']:
                        # 隐藏敏感信息
                        config_table.add_row(key, "***" if value else "")
                    else:
                        config_table.add_row(key, str(value))
                
                console.print(config_table)
            
            # 显示性能摘要
            if test_data.performance_summary:
                console.print(f"\n[blue]📈 性能摘要[/blue]")
                perf_table = Table(show_header=True, header_style="bold magenta")
                perf_table.add_column("指标名称", style="cyan", width=20)
                perf_table.add_column("数量", style="green", width=8)
                perf_table.add_column("最小值", style="yellow", width=10)
                perf_table.add_column("最大值", style="yellow", width=10)
                perf_table.add_column("平均值", style="yellow", width=10)
                perf_table.add_column("最新值", style="magenta", width=10)
                
                for metric_name, stats in test_data.performance_summary.items():
                    perf_table.add_row(
                        metric_name,
                        str(stats['count']),
                        f"{stats['min']:.2f}",
                        f"{stats['max']:.2f}",
                        f"{stats['avg']:.2f}",
                        f"{stats['latest']:.2f}"
                    )
                
                console.print(perf_table)
            
            # 显示原始指标数量
            console.print(f"\n[blue]📊 原始指标数据: {len(test_data.raw_metrics)} 条[/blue]")
            
        except ValueError:
            console.print("[red]❌ 测试ID必须是数字[/red]")
        except Exception as e:
            console.print(f"[red]❌ 查看测试详情失败: {e}[/red]")
    
    def export_data(self):
        """导出测试数据"""
        console.print("\n[blue]📤 导出测试数据[/blue]")
        
        # 获取所有测试
        all_tests = self.data_manager.get_all_tests()
        if not all_tests:
            console.print("[yellow]⚠️ 暂无测试数据可导出[/yellow]")
            return
        
        # 显示测试列表
        console.print("\n[cyan]可导出的测试:[/cyan]")
        for test in all_tests[:10]:  # 只显示前10个
            status = "✅" if test['success'] else "❌"
            console.print(f"  {test['id']}. {test['test_name']} ({test['test_type']}) {status}")
        
        if len(all_tests) > 10:
            console.print(f"  ... 还有 {len(all_tests) - 10} 个测试")
        
        # 选择导出范围
        console.print("\n[cyan]选择导出范围:[/cyan]")
        console.print("  [green]1.[/green] 导出所有测试")
        console.print("  [green]2.[/green] 导出特定测试")
        console.print("  [green]3.[/green] 导出最近10个测试")
        
        choice = Prompt.ask("请选择", default="1")
        
        test_ids = []
        if choice == "1":
            test_ids = [test['id'] for test in all_tests]
        elif choice == "2":
            test_id_input = Prompt.ask("请输入测试ID（多个用逗号分隔）")
            try:
                test_ids = [int(x.strip()) for x in test_id_input.split(',')]
            except ValueError:
                console.print("[red]❌ 测试ID格式错误[/red]")
                return
        elif choice == "3":
            test_ids = [test['id'] for test in all_tests[:10]]
        
        if not test_ids:
            console.print("[yellow]⚠️ 未选择任何测试[/yellow]")
            return
        
        # 选择导出格式
        console.print("\n[cyan]选择导出格式:[/cyan]")
        console.print("  [green]1.[/green] JSON格式")
        console.print("  [green]2.[/green] CSV格式")
        console.print("  [green]3.[/green] Excel格式")
        
        format_choice = Prompt.ask("请选择", default="1")
        format_map = {"1": "json", "2": "csv", "3": "excel"}
        export_format = format_map.get(format_choice, "json")
        
        try:
            # 导出数据
            export_file = self.data_manager.export_test_data(test_ids, export_format)
            console.print(f"[green]✅ 数据已导出到: {export_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ 导出失败: {e}[/red]")
    
    def analyze_data(self):
        """数据分析"""
        console.print("\n[blue]📊 数据分析[/blue]")
        
        all_tests = self.data_manager.get_all_tests()
        if not all_tests:
            console.print("[yellow]⚠️ 暂无测试数据可分析[/yellow]")
            return
        
        # 基本统计
        total_tests = len(all_tests)
        successful_tests = len([t for t in all_tests if t['success']])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 按测试类型统计
        test_types = {}
        for test in all_tests:
            test_type = test['test_type']
            if test_type not in test_types:
                test_types[test_type] = {'total': 0, 'success': 0}
            test_types[test_type]['total'] += 1
            if test['success']:
                test_types[test_type]['success'] += 1
        
        # 显示分析结果
        console.print(f"\n[blue]📈 数据分析结果[/blue]")
        
        # 基本统计表格
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("统计项", style="cyan", width=15)
        stats_table.add_column("数值", style="green", width=10)
        stats_table.add_column("百分比", style="yellow", width=10)
        
        stats_table.add_row("总测试数", str(total_tests), "100%")
        stats_table.add_row("成功测试", str(successful_tests), f"{successful_tests/total_tests*100:.1f}%")
        stats_table.add_row("失败测试", str(failed_tests), f"{failed_tests/total_tests*100:.1f}%")
        stats_table.add_row("成功率", f"{success_rate:.1f}%", "")
        
        console.print(stats_table)
        
        # 按类型统计表格
        if test_types:
            console.print(f"\n[blue]📊 按测试类型统计[/blue]")
            type_table = Table(show_header=True, header_style="bold magenta")
            type_table.add_column("测试类型", style="cyan", width=20)
            type_table.add_column("总次数", style="green", width=8)
            type_table.add_column("成功次数", style="green", width=8)
            type_table.add_column("失败次数", style="red", width=8)
            type_table.add_column("成功率", style="yellow", width=10)
            
            for test_type, stats in test_types.items():
                success_rate = stats['success'] / stats['total'] * 100
                type_table.add_row(
                    test_type,
                    str(stats['total']),
                    str(stats['success']),
                    str(stats['total'] - stats['success']),
                    f"{success_rate:.1f}%"
                )
            
            console.print(type_table)
        
        # 性能评估
        console.print(f"\n[blue]🎯 性能评估[/blue]")
        if success_rate >= 95:
            console.print("[green]🎉 测试执行优秀！系统性能表现良好[/green]")
        elif success_rate >= 80:
            console.print("[yellow]⚠️ 测试执行良好，但仍有改进空间[/yellow]")
        else:
            console.print("[red]❌ 测试执行需要关注，建议检查配置和网络连接[/red]")
    
    def cleanup_data(self):
        """清理旧数据"""
        console.print("\n[blue]🧹 清理旧数据[/blue]")
        
        days = Prompt.ask("请输入要保留的天数", default="30")
        try:
            days = int(days)
            if days < 1:
                console.print("[red]❌ 保留天数必须大于0[/red]")
                return
            
            if Confirm.ask(f"确定要清理 {days} 天前的数据吗？"):
                self.data_manager.cleanup_old_data(days)
                console.print(f"[green]✅ 已清理 {days} 天前的数据[/green]")
            else:
                console.print("[yellow]取消清理操作[/yellow]")
                
        except ValueError:
            console.print("[red]❌ 天数必须是数字[/red]")
        except Exception as e:
            console.print(f"[red]❌ 清理失败: {e}[/red]")
    
    def show_data_statistics(self):
        """显示数据统计"""
        console.print("\n[blue]📊 数据统计[/blue]")
        
        # 检查数据目录
        data_dir = Path("test_data")
        if not data_dir.exists():
            console.print("[yellow]⚠️ 数据目录不存在[/yellow]")
            return
        
        # 统计文件数量
        stats = {
            'raw_data': len(list((data_dir / "raw_data").glob("*.json"))),
            'metrics': len(list((data_dir / "metrics").glob("*.csv"))),
            'analysis': len(list((data_dir / "analysis").glob("*.json"))),
            'database_size': (data_dir / "database" / "test_data.db").stat().st_size if (data_dir / "database" / "test_data.db").exists() else 0
        }
        
        # 显示统计表格
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("数据类型", style="cyan", width=15)
        stats_table.add_column("文件数量", style="green", width=10)
        stats_table.add_column("说明", style="dim", width=30)
        
        stats_table.add_row("原始数据", str(stats['raw_data']), "JSON格式的完整测试数据")
        stats_table.add_row("指标数据", str(stats['metrics']), "CSV格式的指标数据")
        stats_table.add_row("分析报告", str(stats['analysis']), "JSON格式的性能摘要")
        stats_table.add_row("数据库大小", f"{stats['database_size']/1024:.1f} KB", "SQLite数据库文件")
        
        console.print(stats_table)
        
        # 显示数据目录结构
        console.print(f"\n[blue]📁 数据目录结构[/blue]")
        console.print(f"  📂 {data_dir.absolute()}")
        console.print(f"    📂 raw_data/ - 原始测试数据")
        console.print(f"    📂 metrics/ - 指标数据")
        console.print(f"    📂 analysis/ - 分析报告")
        console.print(f"    📂 database/ - SQLite数据库")
        console.print(f"    📄 data_index.json - 数据索引")

def main():
    """主函数"""
    viewer = DataViewer()
    viewer.show_main_menu()

if __name__ == "__main__":
    main()
