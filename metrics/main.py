#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eMQTT-Bench 自动数据收集和报告生成器
用户运行main.py时直接执行数据收集任务，完成或中断时自动生成报告
作者: Jaxon
日期: 2024-12-19
"""

import sys
import os
import signal
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def get_huawei_template_path() -> str:
    """获取华为云模板文件的绝对路径"""
    # 获取main.py所在目录的父目录（项目根目录）
    main_dir = Path(__file__).parent
    project_root = main_dir
    template_path = project_root / "huawei_cloud_payload_template.json"
    return str(template_path.absolute())

from emqtt_test_manager import EMQTTTestManager, TestConfig, TestResult
from metrics_collector import PrometheusMetricsCollector, MetricsAnalyzer
from continuous_metrics_collector import ContinuousMetricsCollector
from enhanced_markdown_generator import EnhancedMarkdownGenerator
from test_data_manager import TestDataManager, TestData
from test_specific_filter import TestSpecificFilter
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
import json
import re

console = Console()

class AutoDataCollector:
    """自动数据收集器"""
    
    def __init__(self):
        self.test_manager = EMQTTTestManager()
        self.metrics_collector = PrometheusMetricsCollector()
        self.metrics_analyzer = MetricsAnalyzer()
        self.continuous_collector = ContinuousMetricsCollector()  # 新增持续收集器
        self.enhanced_generator = EnhancedMarkdownGenerator()  # 新增增强版报告生成器
        self.data_manager = TestDataManager()  # 新增测试数据管理器
        self.test_filter = TestSpecificFilter()  # 新增测试特定过滤器
        self.test_results: List[TestResult] = []
        self.continuous_data_files: List[str] = []  # 存储持续数据文件路径
        self.running = True
        self.start_time = datetime.now()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 定义无效数据过滤规则
        self.invalid_data_patterns = {
            # 零值指标（对测试无意义的指标）
            'zero_value_metrics': [
                'connection_idle', 'recv', 'connect_fail', 'pub_fail', 'pub_overrun',
                'connect_retried', 'sub_fail', 'reconnect_succ', 'sub', 'publish_latency',
                'pub_succ', 'connection_timeout', 'connection_refused', 'unreachable', 'pub'
            ],
            # Erlang VM系统指标（与MQTT测试性能无关）
            'erlang_vm_metrics': [
                'erlang_vm_memory_', 'erlang_vm_msacc_', 'erlang_vm_statistics_',
                'erlang_vm_dirty_', 'erlang_vm_ets_', 'erlang_vm_logical_',
                'erlang_vm_port_', 'erlang_vm_process_', 'erlang_vm_schedulers_',
                'erlang_vm_smp_', 'erlang_vm_thread_', 'erlang_vm_time_',
                'erlang_vm_wordsize_', 'erlang_vm_atom_', 'erlang_vm_allocators'
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
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        console.print("\n[yellow]收到中断信号，正在停止所有指标收集并生成报告...[/yellow]")
        self.running = False
        
        # 停止所有持续指标收集
        self.continuous_collector.stop_all_collections()
        
        # 保存所有测试的持续数据
        summaries = self.continuous_collector.get_all_summaries()
        for test_name, summary in summaries.items():
            if summary.get('total_collections', 0) > 0:
                self.continuous_collector.save_test_data(test_name)
        
        self.generate_final_report()
        sys.exit(0)
    
    def run_automatic_collection(self):
        """运行自动数据收集"""
        console.print("🚀 [bold blue]eMQTT-Bench 自动数据收集器[/bold blue]")
        console.print("=" * 60)
        console.print("✨ [yellow]自动执行测试、收集数据并生成报告[/yellow]")
        console.print("💡 [dim]按 Ctrl+C 可随时中断并生成报告[/dim]")
        console.print("")

        try:
            # 1. 加载或创建配置
            config = self._setup_configuration()

            # 2. 显示配置摘要
            self._show_config_summary(config)

            # 3. 确认开始收集
            if not Confirm.ask("是否开始自动数据收集?", default=True):
                console.print("[yellow]用户取消操作[/yellow]")
                return

            # 4. 选择测试项
            selected_tests = self._select_test_items(config)

            # 5. 执行测试和数据收集
            self._execute_tests_and_collect_data(config, selected_tests)

            # 5. 生成最终报告
            self.generate_final_report()

        except KeyboardInterrupt:
            console.print("\n[yellow]用户中断数据收集[/yellow]")
            self.generate_final_report()
        except Exception as e:
            console.print(f"\n[red]❌ 数据收集失败: {e}[/red]")
            self.generate_final_report()
            sys.exit(1)
    
    def _setup_configuration(self) -> TestConfig:
        """设置配置"""
        console.print(Panel.fit("[bold blue]📋 配置设置[/bold blue]"))
        
        # 尝试加载现有配置
        config_manager = self.test_manager.config_manager
        config = config_manager.load_config()
        
        # 显示当前配置内容
        self._display_current_config(config)
        
        # 询问是否使用当前配置
        if Confirm.ask("是否使用以上配置?", default=True):
            console.print("[green]✅ 使用当前配置[/green]")
            
            # 如果使用华为云认证，检查必要的华为云参数
            if config.use_huawei_auth:
                missing_params = []
                if not hasattr(config, 'huawei_ak') or not config.huawei_ak:
                    missing_params.append("华为云访问密钥ID (AK)")
                if not hasattr(config, 'huawei_sk') or not config.huawei_sk:
                    missing_params.append("华为云访问密钥Secret (SK)")
                if not hasattr(config, 'huawei_endpoint') or not config.huawei_endpoint:
                    missing_params.append("华为云IoTDA端点")
                
                if missing_params:
                    console.print(f"\n[yellow]⚠️ 检测到缺少华为云参数: {', '.join(missing_params)}[/yellow]")
                    console.print("[cyan]📝 请补充华为云认证参数:[/cyan]")
                    
                    config.huawei_ak = Prompt.ask("华为云访问密钥ID (AK)", default=getattr(config, 'huawei_ak', ''))
                    config.huawei_sk = Prompt.ask("华为云访问密钥Secret (SK)", default=getattr(config, 'huawei_sk', ''), password=True)
                    config.huawei_endpoint = Prompt.ask("华为云IoTDA端点", default=getattr(config, 'huawei_endpoint', ''))
                    config.huawei_region = Prompt.ask("华为云区域ID", default=getattr(config, 'huawei_region', 'cn-north-4'))
                    config.broadcast_topic = Prompt.ask("广播主题", default=getattr(config, 'broadcast_topic', '$oc/broadcast/test'))
                    config.broadcast_interval = IntPrompt.ask("广播发送间隔(秒)", default=getattr(config, 'broadcast_interval', 5))
                    
                    # 询问是否保存更新的配置
                    if Confirm.ask("是否保存更新的配置?", default=True):
                        try:
                            config_manager.save_config(config)
                            console.print("[green]✅ 配置已更新并保存[/green]")
                        except Exception as e:
                            console.print(f"[red]❌ 保存配置失败: {e}[/red]")
        else:
            # 快速配置调整
            console.print("\n[yellow]快速配置调整:[/yellow]")
            config.host = Prompt.ask("MQTT服务器地址", default=config.host)
            config.port = IntPrompt.ask("MQTT端口", default=config.port)
            config.client_count = IntPrompt.ask("客户端数量", default=config.client_count)
            config.test_duration = IntPrompt.ask("测试持续时间(秒)", default=config.test_duration)
            config.prometheus_port = IntPrompt.ask("Prometheus起始端口", default=config.prometheus_port)
            
            # MQTT配置
            console.print("\n[cyan]📡 MQTT配置:[/cyan]")
            config.qos = IntPrompt.ask("QoS等级 (0=最多一次, 1=至少一次, 2=恰好一次)", default=config.qos)
            
            # 显示QoS说明
            qos_descriptions = {
                0: "最多一次 (Fire and Forget) - 不保证消息送达",
                1: "至少一次 (At Least Once) - 保证消息送达，可能重复",
                2: "恰好一次 (Exactly Once) - 保证消息送达且不重复"
            }
            console.print(f"[dim]💡 当前QoS: {qos_descriptions.get(config.qos, '未知')}[/dim]")
            
            # 华为云认证配置
            console.print("\n[cyan]🔐 华为云IoT认证配置:[/cyan]")
            config.use_huawei_auth = Confirm.ask("是否使用华为云IoT认证?", default=config.use_huawei_auth)
            
            if config.use_huawei_auth:
                console.print("[yellow]📝 华为云认证参数设置:[/yellow]")
                config.device_prefix = Prompt.ask("设备ID前缀", default=config.device_prefix)
                config.huawei_secret = Prompt.ask("设备密钥", default=config.huawei_secret, password=True)
                
                # 华为云广播测试参数
                console.print("\n[yellow]📡 华为云广播测试参数:[/yellow]")
                console.print("[dim]💡 这些参数用于发送广播消息，让设备能够接收广播信息[/dim]")
                
                config.huawei_ak = Prompt.ask("华为云访问密钥ID (AK)", default=getattr(config, 'huawei_ak', ''))
                config.huawei_sk = Prompt.ask("华为云访问密钥Secret (SK)", default=getattr(config, 'huawei_sk', ''), password=True)
                config.huawei_endpoint = Prompt.ask("华为云IoTDA端点", default=getattr(config, 'huawei_endpoint', ''))
                config.huawei_region = Prompt.ask("华为云区域ID", default=getattr(config, 'huawei_region', 'cn-north-4'))
                config.broadcast_topic = Prompt.ask("广播主题", default=getattr(config, 'broadcast_topic', '$oc/broadcast/test'))
                config.broadcast_interval = IntPrompt.ask("广播发送间隔(秒)", default=getattr(config, 'broadcast_interval', 5))
                
                # 显示华为云配置说明
                console.print("\n[dim]💡 华为云配置说明:[/dim]")
                console.print("[dim]  • 设备ID前缀: 用于生成设备ID，如 'speaker' 会生成 speaker_000000001, speaker_000000002 等[/dim]")
                console.print("[dim]  • 设备密钥: 华为云IoT平台中设备的密钥，用于设备认证[/dim]")
                console.print("[dim]  • 华为云AK/SK: 用于调用华为云IoTDA API发送广播消息，让设备接收广播信息[/dim]")
                console.print("[dim]  • 华为云端点: 华为云IoTDA服务的API端点地址，用于发送广播消息[/dim]")
                console.print("[dim]  • 广播主题: 设备订阅的主题，用于接收广播消息[/dim]")
                console.print("[dim]  • 确保设备已在华为云IoT平台注册，且具有订阅权限[/dim]")
            else:
                console.print("[yellow]ℹ️ 将使用标准MQTT连接（无需华为云认证）[/yellow]")
            
            # 验证eMQTT-Bench路径
            console.print("\n[cyan]🔧 eMQTT-Bench配置:[/cyan]")
            while True:
                emqtt_path = Prompt.ask("eMQTT-Bench路径", default=config.emqtt_bench_path)
                if emqtt_path.startswith('.') or emqtt_path.startswith('/') :
                    if self._validate_emqtt_bench_path(emqtt_path):
                        config.emqtt_bench_path = emqtt_path
                        break
                    else:
                        console.print(f"[red]❌ 路径无效: {emqtt_path}[/red]")
                        console.print("[yellow]请确保路径指向有效的eMQTT-Bench可执行文件[/yellow]")
                else:
                    config.emqtt_bench_path = emqtt_path
                    break
            
            # 显示修改后的配置
            console.print("\n[yellow]修改后的配置:[/yellow]")
            self._display_current_config(config)
            
            # 询问是否保存配置
            if Confirm.ask("是否保存修改后的配置?", default=True):
                try:
                    config_manager.save_config(config)
                    console.print("[green]✅ 配置已保存到 emqtt_test_config.json[/green]")
                except Exception as e:
                    console.print(f"[red]❌ 保存配置失败: {e}[/red]")
            else:
                console.print("[yellow]⚠️ 配置未保存，下次运行时将使用默认配置[/yellow]")
        
        return config
    
    def _display_current_config(self, config: TestConfig):
        """显示当前配置内容"""
        console.print("\n[cyan]📋 当前配置内容:[/cyan]")
        
        # 创建配置表格
        from rich.table import Table
        config_table = Table(show_header=True, header_style="bold magenta")
        config_table.add_column("配置项", style="cyan", width=20)
        config_table.add_column("值", style="green", width=30)
        config_table.add_column("说明", style="dim", width=40)
        
        config_table.add_row("MQTT服务器", f"{config.host}:{config.port}", "MQTT服务器地址和端口")
        config_table.add_row("客户端数量", str(config.client_count), "同时连接的客户端数量")
        config_table.add_row("消息间隔", f"{config.msg_interval}ms", "消息发送间隔时间")
        config_table.add_row("测试持续时间", f"{config.test_duration}秒", "每个测试的持续时间")
        config_table.add_row("Prometheus端口", str(config.prometheus_port), "Prometheus指标起始端口")
        config_table.add_row("华为云认证", "是" if config.use_huawei_auth else "否", "是否使用华为云IoT认证")
        
        if config.use_huawei_auth:
            config_table.add_row("设备前缀", config.device_prefix, "华为云设备ID前缀")
            config_table.add_row("设备密钥", "***" if config.huawei_secret else "未配置", "华为云设备密钥")
            
            # 华为云广播参数
            huawei_ak = getattr(config, 'huawei_ak', '')
            huawei_sk = getattr(config, 'huawei_sk', '')
            huawei_endpoint = getattr(config, 'huawei_endpoint', '')
            
            if huawei_ak:
                config_table.add_row("华为云AK", huawei_ak[:8] + "..." if len(huawei_ak) > 8 else huawei_ak, "华为云访问密钥ID")
            else:
                config_table.add_row("华为云AK", "未配置", "华为云访问密钥ID")
            
            if huawei_sk:
                config_table.add_row("华为云SK", "***", "华为云访问密钥Secret")
            else:
                config_table.add_row("华为云SK", "未配置", "华为云访问密钥Secret")
            
            config_table.add_row("华为云端点", huawei_endpoint or "未配置", "华为云IoTDA端点")
            config_table.add_row("华为云区域", getattr(config, 'huawei_region', 'cn-north-4'), "华为云区域ID")
            config_table.add_row("广播主题", getattr(config, 'broadcast_topic', '$oc/broadcast/test'), "广播消息主题")
            config_table.add_row("广播间隔", f"{getattr(config, 'broadcast_interval', 5)}秒", "广播发送间隔")
        
        # 突出显示eMQTT-Bench路径
        config_table.add_row("📡 QoS等级", str(config.qos), "MQTT消息质量等级")
        config_table.add_row("🔧 eMQTT-Bench路径", config.emqtt_bench_path, "eMQTT-Bench可执行文件路径")
        
        console.print(config_table)
        console.print("")
    
    def _select_test_items(self, config: TestConfig) -> List[Dict[str, Any]]:
        """选择要运行的测试项"""
        console.print(Panel.fit("[bold blue]🧪 测试项选择[/bold blue]"))
        
        # 根据华为云认证状态定义测试项
        if config.use_huawei_auth:
            # 华为云测试模式：显示华为云的四种测试类型
            available_tests = [
                {
                    "name": "华为云连接测试",
                    "description": "测试华为云IoT平台连接功能",
                    "command": self._build_huawei_connection_test_command(config),
                    "port": config.prometheus_port,
                    "duration": config.test_duration,
                    "enabled": True
                },
                {
                    "name": "华为云发布测试",
                    "description": "测试华为云IoT平台消息发布功能",
                    "command": self._build_huawei_publish_test_command(config),
                    "port": config.prometheus_port + 1,
                    "duration": config.test_duration,
                    "enabled": True
                },
                {
                    "name": "华为云订阅测试",
                    "description": "测试华为云IoT平台消息订阅功能（同时启动广播发送器）",
                    "command": self._build_huawei_subscribe_test_command(config),
                    "port": config.prometheus_port + 2,
                    "duration": config.test_duration,
                    "enabled": True
                },
                {
                    "name": "华为云广播测试",
                    "description": "测试华为云IoT平台广播消息功能（发送+订阅）",
                    "command": self._build_huawei_broadcast_test_command(config),
                    "port": config.prometheus_port + 3,
                    "duration": config.test_duration,
                    "enabled": True
                }
            ]
        else:
            # 标准MQTT测试模式：显示标准的三种测试类型
            available_tests = [
                {
                    "name": "连接测试",
                    "description": "测试MQTT客户端连接功能",
                    "command": self._build_connection_test_command(config),
                    "port": config.prometheus_port,
                    "duration": config.test_duration,
                    "enabled": True
                },
                {
                    "name": "发布测试", 
                    "description": "测试MQTT消息发布功能",
                    "command": self._build_publish_test_command(config),
                    "port": config.prometheus_port + 1,
                    "duration": config.test_duration,
                    "enabled": True
                },
                {
                    "name": "订阅测试",
                    "description": "测试MQTT消息订阅功能",
                    "command": self._build_subscribe_test_command(config),
                    "port": config.prometheus_port + 2,
                    "duration": config.test_duration,
                    "enabled": True
                }
            ]
        
        # 显示测试模式说明
        if config.use_huawei_auth:
            console.print("\n[green]☁️ 华为云测试模式[/green]")
            console.print("[dim]使用华为云IoT平台认证和设备管理功能[/dim]")
        else:
            console.print("\n[blue]🔗 标准MQTT测试模式[/blue]")
            console.print("[dim]使用标准MQTT协议进行测试[/dim]")
        
        # 显示测试项选择菜单
        console.print("\n[cyan]📋 可用的测试项:[/cyan]")
        
        from rich.table import Table
        test_table = Table(show_header=True, header_style="bold magenta")
        test_table.add_column("序号", style="cyan", width=6)
        test_table.add_column("测试名称", style="green", width=15)
        test_table.add_column("描述", style="dim", width=40)
        test_table.add_column("端口", style="yellow", width=8)
        test_table.add_column("状态", style="blue", width=8)
        
        for i, test in enumerate(available_tests, 1):
            status = "✅ 启用" if test["enabled"] else "❌ 禁用"
            test_table.add_row(
                str(i),
                test["name"],
                test["description"],
                str(test["port"]),
                status
            )
        
        console.print(test_table)
        console.print("")
        
        # 询问用户选择
        console.print("[yellow]请选择要运行的测试项:[/yellow]")
        console.print("  [cyan]1.[/cyan] 运行所有测试")
        console.print("  [cyan]2.[/cyan] 自定义选择测试项")
        if config.use_huawei_auth:
            console.print("  [cyan]3.[/cyan] 快速测试（仅华为云连接测试）")
            console.print("  [cyan]4.[/cyan] 华为云广播测试（发送+订阅）")
        else:
            console.print("  [cyan]3.[/cyan] 快速测试（仅连接测试）")
        
        while True:
            if config.use_huawei_auth:
                choice = Prompt.ask("请选择 (1-4)", default="1")
            else:
                choice = Prompt.ask("请选择 (1-3)", default="1")
            
            if choice == "1":
                console.print("[green]✅ 将运行所有测试项[/green]")
                return available_tests
                
            elif choice == "2":
                return self._custom_select_tests(available_tests)
                
            elif choice == "3":
                if config.use_huawei_auth:
                    console.print("[green]✅ 将运行快速测试（仅华为云连接测试）[/green]")
                else:
                    console.print("[green]✅ 将运行快速测试（仅连接测试）[/green]")
                return [available_tests[0]]  # 只返回连接测试
                
            elif choice == "4" and config.use_huawei_auth:
                console.print("[green]✅ 将运行华为云广播测试（发送+订阅）[/green]")
                return [available_tests[3]]  # 只返回华为云广播测试
                
            else:
                if config.use_huawei_auth:
                    console.print("[red]❌ 无效选择，请输入 1-4[/red]")
                else:
                    console.print("[red]❌ 无效选择，请输入 1-3[/red]")
    
    def _custom_select_tests(self, available_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """自定义选择测试项"""
        console.print("\n[yellow]自定义选择测试项:[/yellow]")
        
        # 重新显示测试项列表
        console.print("\n[cyan]📋 可选择的测试项:[/cyan]")
        
        from rich.table import Table
        selection_table = Table(show_header=True, header_style="bold magenta")
        selection_table.add_column("序号", style="cyan", width=6)
        selection_table.add_column("测试名称", style="green", width=15)
        selection_table.add_column("描述", style="dim", width=40)
        selection_table.add_column("端口", style="yellow", width=8)
        
        for i, test in enumerate(available_tests, 1):
            selection_table.add_row(
                str(i),
                test["name"],
                test["description"],
                str(test["port"])
            )
        
        console.print(selection_table)
        console.print("")
        
        console.print("[yellow]请输入要运行的测试项序号:[/yellow]")
        console.print("  • 单个测试: [cyan]1[/cyan]")
        console.print("  • 多个测试: [cyan]1,3,4[/cyan]")
        console.print("  • 运行所有: [cyan]all[/cyan]")
        console.print("")
        
        while True:
            selection = Prompt.ask("测试项选择", default="all")
            
            if selection.lower() == "all":
                console.print("[green]✅ 将运行所有测试项[/green]")
                return available_tests
            
            try:
                # 解析用户输入
                indices = [int(x.strip()) for x in selection.split(",")]
                selected_tests = []
                
                for idx in indices:
                    if 1 <= idx <= len(available_tests):
                        selected_tests.append(available_tests[idx - 1])
                    else:
                        console.print(f"[red]❌ 无效序号: {idx} (有效范围: 1-{len(available_tests)})[/red]")
                        break
                else:
                    # 所有序号都有效
                    if selected_tests:
                        console.print(f"[green]✅ 已选择 {len(selected_tests)} 个测试项:[/green]")
                        for i, test in enumerate(selected_tests, 1):
                            console.print(f"  {i}. {test['name']} (端口: {test['port']})")
                        return selected_tests
                    else:
                        console.print("[red]❌ 未选择任何测试项[/red]")
                        
            except ValueError:
                console.print("[red]❌ 输入格式错误，请输入数字序号或 'all'[/red]")
                console.print("[dim]示例: 1 或 1,3,4 或 all[/dim]")
    
    def _validate_emqtt_bench_path(self, path: str) -> bool:
        """验证eMQTT-Bench路径是否有效"""
        try:
            import os
            from pathlib import Path
            
            # 检查路径是否存在
            if not os.path.exists(path):
                return False
            
            # 检查是否为文件
            if not os.path.isfile(path):
                return False
            
            # 检查是否可执行
            if not os.access(path, os.X_OK):
                return False
            
            # 检查文件名是否包含emqtt_bench
            filename = os.path.basename(path)
            if 'emqtt_bench' not in filename:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _check_port_availability(self, port: int) -> bool:
        """检查端口是否可用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0  # 端口可用返回True
        except Exception:
            return False
    
    def _find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """查找可用端口"""
        for i in range(max_attempts):
            port = start_port + i
            if self._check_port_availability(port):
                return port
        return start_port  # 如果找不到可用端口，返回原始端口
    
    def _kill_process_on_port(self, port: int) -> bool:
        """终止占用指定端口的进程"""
        try:
            import subprocess
            # 查找占用端口的进程
            result = subprocess.run(
                f"lsof -ti:{port}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        try:
                            subprocess.run(f"kill -9 {pid.strip()}", shell=True)
                            console.print(f"[yellow]⚠️ 已终止占用端口 {port} 的进程 PID: {pid.strip()}[/yellow]")
                        except Exception as e:
                            console.print(f"[red]❌ 无法终止进程 {pid}: {e}[/red]")
                return True
            return False
        except Exception as e:
            console.print(f"[red]❌ 检查端口占用失败: {e}[/red]")
            return False
    
    def _show_config_summary(self, config: TestConfig):
        """显示配置摘要"""
        table = Table(title="📊 数据收集配置")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("MQTT服务器", f"{config.host}:{config.port}")
        table.add_row("客户端数量", str(config.client_count))
        table.add_row("消息间隔", f"{config.msg_interval}ms")
        table.add_row("测试持续时间", f"{config.test_duration}秒")
        table.add_row("Prometheus端口", str(config.prometheus_port))
        table.add_row("华为云认证", "是" if config.use_huawei_auth else "否")
        
        console.print(table)
        console.print("")
    
    def _execute_tests_and_collect_data(self, config: TestConfig, selected_tests: List[Dict[str, Any]]):
        """执行测试并收集数据"""
        console.print(Panel.fit("[bold blue]🔄 开始执行测试和数据收集[/bold blue]"))
        
        # 显示将要执行的测试
        console.print(f"\n[cyan]📋 将执行 {len(selected_tests)} 个测试项:[/cyan]")
        for i, test in enumerate(selected_tests, 1):
            console.print(f"  {i}. {test['name']} (端口: {test['port']})")
        console.print("")
        
        # 使用选中的测试任务
        test_tasks = selected_tests
        
        # 执行测试任务
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            for i, task in enumerate(test_tasks):
                if not self.running:
                    break
                    
                task_progress = progress.add_task(
                    f"执行 {task['name']}...", 
                    total=task['duration']
                )
                
                # 执行测试
                result = self._execute_single_test(task, progress, task_progress)
                if result:
                    self.test_results.append(result)
                    # 保存测试数据
                    self._save_test_data(result, task)
                
                progress.update(task_progress, completed=task['duration'])
                console.print(f"[green]✅ {task['name']} 完成[/green]")
        
        console.print(f"\n[green]🎉 所有测试完成！共完成 {len(self.test_results)} 个测试[/green]")
    
    def _save_test_data(self, result: TestResult, task: Dict[str, Any]):
        """保存测试数据"""
        try:
            # 读取指标数据
            raw_metrics = []
            if result.metrics_file:
                import json
                with open(result.metrics_file, 'r', encoding='utf-8') as f:
                    raw_metrics = json.load(f)
            
            # 生成性能摘要（使用原始数据）
            performance_summary = self._generate_performance_summary(raw_metrics)
            
            # 获取配置信息
            config = self.test_manager.config_manager.config
            config_dict = {
                'host': config.host,
                'port': config.port,
                'client_count': config.client_count,
                'msg_interval': config.msg_interval,
                'test_duration': config.test_duration,
                'qos': config.qos,
                'use_huawei_auth': config.use_huawei_auth,
                'device_prefix': getattr(config, 'device_prefix', ''),
                'huawei_secret': getattr(config, 'huawei_secret', ''),
                'huawei_ak': getattr(config, 'huawei_ak', ''),
                'huawei_sk': getattr(config, 'huawei_sk', ''),
                'huawei_endpoint': getattr(config, 'huawei_endpoint', ''),
                'broadcast_topic': getattr(config, 'broadcast_topic', ''),
                'broadcast_interval': getattr(config, 'broadcast_interval', 5)
            }
            
            # 创建测试数据对象（使用原始数据）
            test_data = TestData(
                test_name=result.test_name,
                test_type=task.get('description', 'Unknown'),
                start_time=result.start_time.isoformat(),
                end_time=result.end_time.isoformat(),
                duration=result.duration,
                port=result.port,
                success=result.success,
                error_message=result.error_message,
                metrics_file=result.metrics_file,
                continuous_data_file=None,  # 持续数据文件路径
                config=config_dict,
                raw_metrics=raw_metrics,  # 使用原始数据
                performance_summary=performance_summary
            )
            
            # 保存到数据管理器
            saved_file = self.data_manager.save_test_data(test_data)
            console.print(f"[blue]💾 测试数据已保存: {saved_file}[/blue]")
            
        except Exception as e:
            console.print(f"[yellow]⚠️ 保存测试数据失败: {e}[/yellow]")
    
    def _filter_invalid_metrics(self, raw_metrics: List[Dict[str, Any]], test_name: str) -> List[Dict[str, Any]]:
        """过滤无效的指标数据"""
        if not raw_metrics:
            return []
        
        console.print(f"[blue]🔍 开始过滤 {test_name} 的无效数据...[/blue]")
        
        filtered_metrics = []
        removed_count = 0
        
        for metric in raw_metrics:
            metric_name = metric.get('name', '')
            metric_value = metric.get('value', 0)
            help_text = metric.get('help_text', '')
            
            # 检查是否应该过滤此指标
            should_remove = False
            removal_reason = ""
            
            # 1. 检查零值指标
            if metric_name in self.invalid_data_patterns['zero_value_metrics'] and metric_value == 0:
                should_remove = True
                removal_reason = "零值指标"
            
            # 2. 检查Erlang VM系统指标
            elif any(metric_name.startswith(pattern) for pattern in self.invalid_data_patterns['erlang_vm_metrics']):
                should_remove = True
                removal_reason = "Erlang VM系统指标"
            
            # 3. 检查直方图桶数据（保留有意义的桶）
            elif any(pattern in metric_name for pattern in self.invalid_data_patterns['histogram_buckets']):
                # 只保留非零值的桶数据
                if metric_value == 0:
                    should_remove = True
                    removal_reason = "零值直方图桶"
            
            # 4. 检查重复的help_text
            elif help_text in self.invalid_data_patterns['redundant_help_text']:
                should_remove = True
                removal_reason = "重复的help_text"
            
            # 5. 检查是否有实际意义的指标（保留关键性能指标）
            if not should_remove:
                # 保留关键性能指标
                key_metrics = [
                    'connect_succ', 'pub_succ', 'recv', 'publish_latency',
                    'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                    'e2e_latency', 'mqtt_client_subscribe_duration'
                ]
                
                # 如果是指标名称包含关键性能指标，或者值不为0，则保留
                if (any(key_metric in metric_name for key_metric in key_metrics) or 
                    metric_value != 0 or 
                    'duration' in metric_name or 
                    'latency' in metric_name):
                    filtered_metrics.append(metric)
                else:
                    should_remove = True
                    removal_reason = "无实际意义的指标"
            
            if should_remove:
                removed_count += 1
                if removed_count <= 5:  # 只显示前5个被移除的指标
                    console.print(f"[dim]  ❌ 移除 {metric_name}: {removal_reason} (值: {metric_value})[/dim]")
            else:
                filtered_metrics.append(metric)
        
        console.print(f"[green]✅ 数据过滤完成: 保留 {len(filtered_metrics)} 个指标，移除 {removed_count} 个无效指标[/green]")
        
        return filtered_metrics
    
    def _save_filtered_data(self, test_result: TestResult, filtered_metrics: List[Dict[str, Any]]) -> str:
        """保存过滤后的数据到新文件"""
        try:
            # 创建过滤后的数据结构
            filtered_data = {
                "test_name": test_result.test_name,
                "test_type": getattr(test_result, 'test_type', 'Unknown'),
                "start_time": test_result.start_time.isoformat(),
                "end_time": test_result.end_time.isoformat(),
                "duration": test_result.duration,
                "port": test_result.port,
                "success": test_result.success,
                "error_message": test_result.error_message,
                "filtered_metrics": filtered_metrics,
                "filter_info": {
                    "original_count": len(getattr(test_result, 'raw_metrics', [])),
                    "filtered_count": len(filtered_metrics),
                    "removed_count": len(getattr(test_result, 'raw_metrics', [])) - len(filtered_metrics),
                    "filter_timestamp": datetime.now().isoformat()
                }
            }
            
            # 生成过滤后的文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filtered_filename = f"filtered_{test_result.test_name}_{timestamp}.json"
            filtered_path = os.path.join("test_data", "filtered_data", filtered_filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filtered_path), exist_ok=True)
            
            # 保存过滤后的数据
            with open(filtered_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]💾 过滤后的数据已保存: {filtered_path}[/green]")
            return filtered_path
            
        except Exception as e:
            console.print(f"[red]❌ 保存过滤数据失败: {e}[/red]")
            return ""
    
    def _generate_performance_summary(self, raw_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成性能摘要"""
        if not raw_metrics:
            return {}
        
        # 按指标名称分组
        metrics_by_name = {}
        for metric in raw_metrics:
            name = metric.get('name', '')
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric.get('value', 0))
        
        # 计算统计信息
        summary = {}
        for name, values in metrics_by_name.items():
            if values:
                summary[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1] if values else 0
                }
        
        return summary
    
    def _auto_filter_all_test_data(self):
        """自动过滤所有测试数据"""
        try:
            console.print("[blue]🔍 检查需要过滤的测试数据...[/blue]")
            
            # 统计过滤信息
            total_tests = len(self.test_results)
            filtered_tests = 0
            total_original_metrics = 0
            total_filtered_metrics = 0
            total_removed_metrics = 0
            
            # 处理每个测试结果
            for result in self.test_results:
                if result.success and result.metrics_file:
                    console.print(f"[blue]📊 处理测试: {result.test_name}[/blue]")
                    
                    # 检查是否已经存在过滤后的文件
                    import glob
                    existing_files = glob.glob(f"test_data/filtered_data/filtered_{result.test_name}_*.json")
                    if existing_files:
                        console.print(f"[yellow]⚠️ 过滤文件已存在: {existing_files[0]}[/yellow]")
                        console.print(f"[dim]跳过重复过滤: {result.test_name}[/dim]")
                        continue
                    
                    try:
                        # 读取原始指标数据
                        import json
                        with open(result.metrics_file, 'r', encoding='utf-8') as f:
                            raw_metrics = json.load(f)
                        
                        # 使用新的测试特定过滤器
                        filtered_metrics = self.test_filter.filter_test_data(result.test_name, raw_metrics)
                        
                        # 保存过滤后的数据
                        filtered_file = self._save_filtered_data(result, filtered_metrics)
                        
                        if filtered_file:
                            filtered_tests += 1
                            original_count = len(raw_metrics)
                            filtered_count = len(filtered_metrics)
                            removed_count = original_count - filtered_count
                            
                            total_original_metrics += original_count
                            total_filtered_metrics += filtered_count
                            total_removed_metrics += removed_count
                            
                            reduction_percent = (removed_count / original_count * 100) if original_count > 0 else 0
                            
                            console.print(f"[green]✅ {result.test_name} 过滤完成[/green]")
                            console.print(f"[dim]  • 原始指标: {original_count}[/dim]")
                            console.print(f"[dim]  • 过滤后指标: {filtered_count}[/dim]")
                            console.print(f"[dim]  • 移除指标: {removed_count} ({reduction_percent:.1f}%)[/dim]")
                            console.print(f"[dim]  • 保存位置: {filtered_file}[/dim]")
                        else:
                            console.print(f"[yellow]⚠️ {result.test_name} 过滤失败[/yellow]")
                            
                    except Exception as e:
                        console.print(f"[red]❌ 处理 {result.test_name} 时出错: {e}[/red]")
            
            # 显示总体过滤统计
            if filtered_tests > 0:
                total_reduction_percent = (total_removed_metrics / total_original_metrics * 100) if total_original_metrics > 0 else 0
                
                console.print(f"\n[green]📊 数据过滤完成统计:[/green]")
                console.print(f"[dim]  • 处理测试数量: {filtered_tests}/{total_tests}[/dim]")
                console.print(f"[dim]  • 原始指标总数: {total_original_metrics}[/dim]")
                console.print(f"[dim]  • 过滤后指标总数: {total_filtered_metrics}[/dim]")
                console.print(f"[dim]  • 移除指标总数: {total_removed_metrics}[/dim]")
                console.print(f"[dim]  • 总体减少比例: {total_reduction_percent:.1f}%[/dim]")
                console.print(f"[dim]  • 过滤数据保存位置: test_data/filtered_data/[/dim]")
            else:
                console.print(f"[yellow]⚠️ 没有找到需要过滤的测试数据[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ 自动数据过滤失败: {e}[/red]")
    
    def _auto_filter_continuous_metrics(self):
        """自动过滤持续指标文件"""
        try:
            console.print("[blue]🔍 检查需要过滤的持续指标文件...[/blue]")
            
            # 使用测试特定过滤器处理持续指标文件
            # 根据当前工作目录确定正确的reports目录
            if os.path.basename(os.getcwd()) == "metrics":
                reports_dir = "reports"
            else:
                reports_dir = "metrics/reports"
            filtered_files = self.test_filter.auto_filter_all_continuous_files(reports_dir)
            
            if filtered_files:
                console.print(f"[green]✅ 持续指标过滤完成![/green]")
                console.print(f"[blue]📊 过滤统计:[/blue]")
                console.print(f"[dim]  • 处理文件数: {len(filtered_files)}[/dim]")
                console.print(f"[dim]  • 过滤后文件保存在: metrics/reports/filtered/[/dim]")
                
                # 显示过滤后的文件列表
                for file_path in filtered_files:
                    console.print(f"[dim]  • {os.path.basename(file_path)}[/dim]")
            else:
                console.print("[yellow]⚠️ 没有找到需要过滤的持续指标文件[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ 持续指标过滤失败: {e}[/red]")
            import traceback
            console.print(f"[dim]详细错误信息: {traceback.format_exc()}[/dim]")
    
    def _build_connection_test_command(self, config: TestConfig) -> str:
        """构建连接测试命令"""
        cmd = f"{config.emqtt_bench_path} conn -h {config.host} -p {config.port} -c {config.client_count} -i 10"
        
        if config.use_huawei_auth:
            cmd += f" --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
        
        cmd += f" --prometheus --restapi {config.prometheus_port} --qoe true"
        return cmd
    
    def _build_publish_test_command(self, config: TestConfig) -> str:
        """构建发布测试命令"""
        cmd = f"{config.emqtt_bench_path} pub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -I {config.msg_interval} -q {config.qos}"
        
        if config.use_huawei_auth:
            template_path = get_huawei_template_path()
            cmd += f" -t '$oc/devices/%d/sys/properties/report' --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth --message 'template://{template_path}'"
        else:
            cmd += " -t 'test/publish/%i'"
        
        cmd += f" --prometheus --restapi {config.prometheus_port + 1} --qoe true"
        return cmd
    
    def _build_subscribe_test_command(self, config: TestConfig) -> str:
        """构建订阅测试命令"""
        cmd = f"{config.emqtt_bench_path} sub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -t 'test/subscribe/%i' -q {config.qos}"
        cmd += f" --prometheus --restapi {config.prometheus_port + 2} --qoe true"
        return cmd
    
    def _build_huawei_connection_test_command(self, config: TestConfig) -> str:
        """构建华为云连接测试命令"""
        # 优化华为云连接测试参数
        cmd = f"{config.emqtt_bench_path} conn -h {config.host} -p {config.port} -c {config.client_count} -i 1"
        cmd += f" --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
        cmd += f" --prometheus --restapi {config.prometheus_port} --qoe true"
        return cmd
    
    def _build_huawei_publish_test_command(self, config: TestConfig) -> str:
        """构建华为云发布测试命令"""
        # 优化华为云发布测试参数
        cmd = f"{config.emqtt_bench_path} pub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -I {config.msg_interval} "
        cmd += f" -t '$oc/devices/%d/sys/properties/report' --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
        template_path = get_huawei_template_path()
        cmd += f" --message 'template://{template_path}' --prometheus --restapi {config.prometheus_port + 1} --qoe true"
        return cmd
    
    def _build_huawei_subscribe_test_command(self, config: TestConfig) -> str:
        """构建华为云订阅测试命令（集成广播发送和订阅测试）"""
        # 华为云订阅测试需要同时运行广播发送和订阅测试
        # 返回一个特殊的命令标识，用于在_execute_single_test中处理
        return f"huawei_subscribe_test:{config.prometheus_port + 2}"
    
    def _build_huawei_broadcast_test_command(self, config: TestConfig) -> str:
        """构建华为云广播测试命令（集成广播发送和订阅测试）"""
        # 这个测试将同时运行广播发送和订阅测试
        # 返回一个特殊的命令标识，用于在_execute_single_test中处理
        return f"huawei_broadcast_test:{config.prometheus_port + 3}"
    
    def _execute_huawei_broadcast_test(self, task: Dict[str, Any], progress, task_progress) -> TestResult:
        """执行华为云广播测试（集成广播发送和订阅测试）"""
        start_time = datetime.now()
        metrics_file = ""
        success = False
        error_message = ""
        
        try:
            console.print(f"[blue]🚀 开始华为云广播测试...[/blue]")
            
            # 获取配置
            config = self.test_manager.config_manager.config
            
            # 验证华为云广播参数
            missing_params = []
            if not hasattr(config, 'huawei_ak') or not config.huawei_ak:
                missing_params.append("华为云访问密钥ID (AK)")
            if not hasattr(config, 'huawei_sk') or not config.huawei_sk:
                missing_params.append("华为云访问密钥Secret (SK)")
            if not hasattr(config, 'huawei_endpoint') or not config.huawei_endpoint:
                missing_params.append("华为云IoTDA端点")
            
            if missing_params:
                error_message = f"缺少必需的华为云广播参数: {', '.join(missing_params)}"
                console.print(f"[red]❌ {error_message}[/red]")
                console.print("[yellow]💡 请重新运行配置，确保提供所有必需的华为云参数[/yellow]")
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 显示使用的参数（隐藏敏感信息）
            console.print(f"[blue]📋 使用华为云参数:[/blue]")
            console.print(f"[dim]  • AK: {config.huawei_ak[:8]}...[/dim]")
            console.print(f"[dim]  • SK: {'*' * len(config.huawei_sk)}[/dim]")
            console.print(f"[dim]  • 端点: {config.huawei_endpoint}[/dim]")
            console.print(f"[dim]  • 区域: {getattr(config, 'huawei_region', 'cn-north-4')}[/dim]")
            console.print(f"[dim]  • 广播主题: {getattr(config, 'broadcast_topic', '$oc/broadcast/test')}[/dim]")
            
            # 先启动订阅测试，确保设备已经订阅广播主题
            console.print("[blue]📥 启动订阅测试...[/blue]")
            subscribe_process = self._start_subscribe_test(config, task['port'])
            
            if not subscribe_process:
                error_message = "订阅测试启动失败"
                console.print(f"[red]❌ {error_message}[/red]")
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 等待订阅测试稳定，确保设备已经成功订阅广播主题
            console.print("[blue]⏳ 等待订阅测试稳定...[/blue]")
            time.sleep(5)  # 增加等待时间，确保订阅成功
            
            # 启动广播发送器
            console.print("[blue]📡 启动广播发送器...[/blue]")
            broadcast_process = self._start_broadcast_sender(config)
            
            if not broadcast_process:
                error_message = "广播发送器启动失败"
                console.print(f"[red]❌ {error_message}[/red]")
                self._cleanup_process(subscribe_process)
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 等待广播发送器稳定
            console.print("[blue]⏳ 等待广播发送器稳定...[/blue]")
            time.sleep(3)
            
            # 启动持续指标收集
            console.print(f"[blue]🔍 启动 {task['name']} 持续指标收集...[/blue]")
            self.continuous_collector.start_collection(
                test_name=task['name'],
                port=task['port'],
                interval=1.0
            )
            
            # 等待测试完成
            console.print(f"[blue]⏳ 等待测试完成 ({task['duration']}秒)...[/blue]")
            for i in range(task['duration']):
                if not self.running:
                    break
                
                # 检查进程状态
                if broadcast_process.poll() is not None or subscribe_process.poll() is not None:
                    console.print("[yellow]⚠️ 检测到进程提前退出[/yellow]")
                    break
                
                time.sleep(1)
                progress.update(task_progress, advance=1)
            
            # 停止持续指标收集
            console.print(f"[blue]⏹️ 停止 {task['name']} 持续指标收集...[/blue]")
            self.continuous_collector.stop_collection(task['name'])
            
            # 保存持续收集的数据
            continuous_data_file = self.continuous_collector.save_test_data(task['name'])
            if continuous_data_file:
                console.print(f"[green]💾 已保存 {task['name']} 持续指标数据: {continuous_data_file}[/green]")
                self.continuous_data_files.append(continuous_data_file)
            
            # 收集指标
            metrics_file = self._collect_metrics(task['port'], task['name'])
            
            # 清理进程
            console.print("[blue]🧹 清理测试进程...[/blue]")
            self._cleanup_process(broadcast_process)
            self._cleanup_process(subscribe_process)
            
            success = True
            console.print(f"[green]✅ {task['name']} 测试完成[/green]")
            
        except Exception as e:
            error_message = str(e)
            console.print(f"[red]❌ {task['name']} 执行异常: {error_message}[/red]")
            success = False
        
        end_time = datetime.now()
        return TestResult(
            test_name=task['name'],
            start_time=start_time,
            end_time=end_time,
            duration=(end_time - start_time).total_seconds(),
            port=task['port'],
            metrics_file=metrics_file,
            success=success,
            error_message=error_message if not success else None
        )
    
    def _start_broadcast_sender(self, config):
        """启动广播发送器"""
        try:
            import subprocess
            import sys
            
            # 构建广播发送命令
            cmd = [
                sys.executable, "broadcast.py",
                "--ak", config.huawei_ak,
                "--sk", config.huawei_sk,
                "--endpoint", config.huawei_endpoint,
                "--region", getattr(config, 'huawei_region', 'cn-north-4'),
                "--topic", getattr(config, 'broadcast_topic', '$oc/broadcast/test'),
                "--interval", str(getattr(config, 'broadcast_interval', 5)),
                "--duration", str(config.test_duration)
            ]
            
            console.print(f"[dim]广播发送命令: {' '.join(cmd)}[/dim]")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            console.print(f"[green]✅ 广播发送器已启动 (PID: {process.pid})[/green]")
            return process
            
        except Exception as e:
            console.print(f"[red]❌ 启动广播发送器失败: {e}[/red]")
            return None
    
    def _start_subscribe_test(self, config, port: int):
        """启动华为云订阅测试（使用emqtt_bench工具）"""
        try:
            import subprocess
            import sys
            
            # 构建华为云订阅测试命令，使用emqtt_bench工具
            cmd = f"{config.emqtt_bench_path} sub -h {config.host} -p {config.port} -c {config.client_count} -i 1 -q {config.qos}"
            cmd += f" -t '$oc/broadcast/test' --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
            cmd += f" --prometheus --restapi {port} --qoe true"
            
            console.print(f"[dim]华为云订阅测试命令: {cmd}[/dim]")
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            console.print(f"[green]✅ 华为云订阅测试已启动 (PID: {process.pid})[/green]")
            console.print(f"[dim]  服务器: {config.host}:{config.port}[/dim]")
            console.print(f"[dim]  设备前缀: {config.device_prefix}[/dim]")
            console.print(f"[dim]  订阅主题: $oc/broadcast/test[/dim]")
            console.print(f"[dim]  监听端口: {port}[/dim]")
            
            return process
            
        except Exception as e:
            console.print(f"[red]❌ 启动华为云订阅测试失败: {e}[/red]")
            return None
    
    def _cleanup_process(self, process):
        """清理进程"""
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                console.print(f"[green]✅ 进程 {process.pid} 已终止[/green]")
            except Exception as timeout_error:
                if "TimeoutExpired" in str(type(timeout_error)):
                    process.kill()
                    console.print(f"[yellow]⚠️ 进程 {process.pid} 已强制终止[/yellow]")
                else:
                    console.print(f"[red]❌ 清理进程失败: {timeout_error}[/red]")
    
    def _execute_huawei_subscribe_test(self, task: Dict[str, Any], progress, task_progress) -> TestResult:
        """执行华为云订阅测试（集成广播发送和订阅测试）"""
        start_time = datetime.now()
        metrics_file = ""
        success = False
        error_message = ""
        
        try:
            console.print(f"[blue]🚀 开始华为云订阅测试...[/blue]")
            
            # 获取配置
            config = self.test_manager.config_manager.config
            
            # 验证华为云广播参数
            missing_params = []
            if not hasattr(config, 'huawei_ak') or not config.huawei_ak:
                missing_params.append("华为云访问密钥ID (AK)")
            if not hasattr(config, 'huawei_sk') or not config.huawei_sk:
                missing_params.append("华为云访问密钥Secret (SK)")
            if not hasattr(config, 'huawei_endpoint') or not config.huawei_endpoint:
                missing_params.append("华为云IoTDA端点")
            
            if missing_params:
                error_message = f"缺少必需的华为云广播参数: {', '.join(missing_params)}"
                console.print(f"[red]❌ {error_message}[/red]")
                console.print("[yellow]💡 请重新运行配置，确保提供所有必需的华为云参数[/yellow]")
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 显示使用的参数（隐藏敏感信息）
            console.print(f"[blue]📋 使用华为云参数:[/blue]")
            console.print(f"[dim]  • AK: {config.huawei_ak[:8]}...[/dim]")
            console.print(f"[dim]  • SK: {'*' * len(config.huawei_sk)}[/dim]")
            console.print(f"[dim]  • 端点: {config.huawei_endpoint}[/dim]")
            console.print(f"[dim]  • 区域: {getattr(config, 'huawei_region', 'cn-north-4')}[/dim]")
            console.print(f"[dim]  • 广播主题: {getattr(config, 'broadcast_topic', '$oc/broadcast/test')}[/dim]")
            
            # 先启动订阅测试，确保设备已经订阅广播主题
            console.print("[blue]📥 启动订阅测试...[/blue]")
            subscribe_process = self._start_subscribe_test(config, task['port'])
            
            if not subscribe_process:
                error_message = "订阅测试启动失败"
                console.print(f"[red]❌ {error_message}[/red]")
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 等待订阅测试稳定，确保设备已经成功订阅广播主题
            console.print("[blue]⏳ 等待订阅测试稳定...[/blue]")
            time.sleep(5)  # 增加等待时间，确保订阅成功
            
            # 启动广播发送器
            console.print("[blue]📡 启动广播发送器...[/blue]")
            broadcast_process = self._start_broadcast_sender(config)
            
            if not broadcast_process:
                error_message = "广播发送器启动失败"
                console.print(f"[red]❌ {error_message}[/red]")
                self._cleanup_process(subscribe_process)
                return TestResult(
                    test_name=task['name'],
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=0,
                    port=task['port'],
                    metrics_file="",
                    success=False,
                    error_message=error_message
                )
            
            # 等待广播发送器稳定
            console.print("[blue]⏳ 等待广播发送器稳定...[/blue]")
            time.sleep(3)
            
            # 启动持续指标收集
            console.print(f"[blue]🔍 启动 {task['name']} 持续指标收集...[/blue]")
            self.continuous_collector.start_collection(
                test_name=task['name'],
                port=task['port'],
                interval=1.0
            )
            
            # 等待测试完成
            console.print(f"[blue]⏳ 等待测试完成 ({task['duration']}秒)...[/blue]")
            for i in range(task['duration']):
                if not self.running:
                    break
                
                # 检查进程状态
                if broadcast_process.poll() is not None or subscribe_process.poll() is not None:
                    console.print("[yellow]⚠️ 检测到进程提前退出[/yellow]")
                    break
                
                time.sleep(1)
                progress.update(task_progress, advance=1)
            
            # 停止持续指标收集
            console.print(f"[blue]⏹️ 停止 {task['name']} 持续指标收集...[/blue]")
            self.continuous_collector.stop_collection(task['name'])
            
            # 保存持续收集的数据
            continuous_data_file = self.continuous_collector.save_test_data(task['name'])
            if continuous_data_file:
                console.print(f"[green]💾 已保存 {task['name']} 持续指标数据: {continuous_data_file}[/green]")
                self.continuous_data_files.append(continuous_data_file)
            
            # 收集指标
            metrics_file = self._collect_metrics(task['port'], task['name'])
            
            # 清理进程
            console.print("[blue]🧹 清理测试进程...[/blue]")
            self._cleanup_process(broadcast_process)
            self._cleanup_process(subscribe_process)
            
            success = True
            console.print(f"[green]✅ {task['name']} 测试完成[/green]")
            
        except Exception as e:
            error_message = str(e)
            console.print(f"[red]❌ {task['name']} 执行异常: {error_message}[/red]")
            success = False
        
        end_time = datetime.now()
        return TestResult(
            test_name=task['name'],
            start_time=start_time,
            end_time=end_time,
            duration=(end_time - start_time).total_seconds(),
            port=task['port'],
            metrics_file=metrics_file,
            success=success,
            error_message=error_message if not success else None
        )
    
    def _execute_single_test(self, task: Dict[str, Any], progress, task_progress) -> TestResult:
        """执行单个测试"""
        start_time = datetime.now()
        metrics_file = ""
        process = None
        success = False
        error_message = ""
        
        # 检查是否为华为云广播测试
        if task['command'].startswith('huawei_broadcast_test:'):
            return self._execute_huawei_broadcast_test(task, progress, task_progress)
        
        # 检查是否为华为云订阅测试
        if task['command'].startswith('huawei_subscribe_test:'):
            return self._execute_huawei_subscribe_test(task, progress, task_progress)
        
        try:
            # 检查端口可用性
            if not self._check_port_availability(task['port']):
                console.print(f"[yellow]⚠️ 端口 {task['port']} 被占用，尝试释放...[/yellow]")
                if self._kill_process_on_port(task['port']):
                    time.sleep(2)  # 等待进程完全终止
                    if not self._check_port_availability(task['port']):
                        # 如果端口仍然被占用，尝试使用其他端口
                        new_port = self._find_available_port(task['port'])
                        if new_port != task['port']:
                            console.print(f"[yellow]⚠️ 使用替代端口: {new_port}[/yellow]")
                            # 更新命令中的端口
                            task['command'] = task['command'].replace(f"--restapi {task['port']}", f"--restapi {new_port}")
                            task['port'] = new_port
                        else:
                            error_message = f"无法找到可用端口，端口 {task['port']} 被占用"
                            console.print(f"[red]❌ {error_message}[/red]")
                            success = False
                            end_time = datetime.now()
                            return TestResult(
                                test_name=task['name'],
                                start_time=start_time,
                                end_time=end_time,
                                duration=(end_time - start_time).total_seconds(),
                                port=task['port'],
                                metrics_file="",
                                success=False,
                                error_message=error_message
                            )
            
            # 启动测试进程
            process = self.test_manager.process_manager.start_process(
                task['command'], 
                task['name']
            )
            
            # 等待进程启动并稳定
            time.sleep(3)
            
            # 启动持续指标收集
            console.print(f"[blue]🔍 启动 {task['name']} 持续指标收集...[/blue]")
            self.continuous_collector.start_collection(
                test_name=task['name'],
                port=task['port'],
                interval=1.0  # 每秒收集一次
            )
            
            # 检查进程是否仍在运行
            if process.poll() is not None:
                # 进程已经退出，获取错误信息
                stdout, stderr = process.communicate()
                error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
                stdout_output = stdout.decode('utf-8', errors='ignore') if stdout else ""
                
                # 分析错误信息
                if "eaddrinuse" in error_output.lower():
                    error_message = f"端口 {task['port']} 被占用，请检查是否有其他进程在使用该端口"
                elif "malformed_username_or_password" in error_output.lower():
                    error_message = "华为云认证失败，请检查设备ID和密钥配置"
                elif "connection" in error_output.lower() and "error" in error_output.lower():
                    error_message = f"连接错误: {error_output.strip()}"
                else:
                    error_message = f"进程异常退出: {error_output.strip() or stdout_output.strip()}"
                
                console.print(f"[red]❌ {task['name']} 进程异常退出: {error_message}[/red]")
                success = False
            else:
                # 进程正常运行，收集指标数据
                metrics_file = self._collect_metrics(task['port'], task['name'])
                
                # 继续等待测试完成，同时监控进程状态
                remaining_time = max(0, task['duration'] - 3)
                for i in range(int(remaining_time)):
                    if not self.running:
                        self.test_manager.process_manager.terminate_process(process)
                        break
                    
                    # 检查进程状态
                    if process.poll() is not None:
                        # 进程提前退出
                        stdout, stderr = process.communicate()
                        error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
                        if error_output:
                            error_message = f"进程提前退出: {error_output.strip()}"
                            console.print(f"[red]❌ {task['name']} 进程提前退出: {error_message}[/red]")
                        success = False
                        break
                    
                    time.sleep(1)
                    progress.update(task_progress, advance=1)
                
                # 停止持续指标收集
                console.print(f"[blue]⏹️ 停止 {task['name']} 持续指标收集...[/blue]")
                self.continuous_collector.stop_collection(task['name'])
                
                # 保存持续收集的数据
                continuous_data_file = self.continuous_collector.save_test_data(task['name'])
                if continuous_data_file:
                    console.print(f"[green]💾 已保存 {task['name']} 持续指标数据: {continuous_data_file}[/green]")
                    self.continuous_data_files.append(continuous_data_file)
                
                # 如果进程仍在运行，认为测试成功
                if process.poll() is None:
                    success = True
                    console.print(f"[green]✅ {task['name']} 测试完成[/green]")
                else:
                    # 进程已退出，检查退出码
                    return_code = process.returncode
                    if return_code != 0:
                        stdout, stderr = process.communicate()
                        error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
                        error_message = f"进程异常退出 (退出码: {return_code}): {error_output.strip()}"
                        console.print(f"[red]❌ {task['name']} 测试失败: {error_message}[/red]")
                        success = False
                    else:
                        success = True
                        console.print(f"[green]✅ {task['name']} 测试成功完成[/green]")
            
            end_time = datetime.now()
            
            return TestResult(
                test_name=task['name'],
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                port=task['port'],
                metrics_file=metrics_file,
                success=success,
                error_message=error_message if not success else None
            )
            
        except Exception as e:
            end_time = datetime.now()
            error_message = str(e)
            console.print(f"[red]❌ {task['name']} 执行异常: {error_message}[/red]")
            
            return TestResult(
                test_name=task['name'],
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                port=task['port'],
                metrics_file=metrics_file,
                success=False,
                error_message=error_message
            )
        finally:
            # 确保进程在测试完成后被正确清理
            if process is not None:
                try:
                    if process.poll() is None:  # 进程仍在运行
                        console.print(f"[yellow]🧹 清理测试进程 {process.pid} 和端口 {task['port']}...[/yellow]")
                        self.test_manager.process_manager.terminate_process(process)
                        
                        # 等待进程完全终止
                        time.sleep(2)
                        
                        # 验证端口是否已释放
                        if not self._check_port_availability(task['port']):
                            console.print(f"[yellow]⚠️ 端口 {task['port']} 仍被占用，尝试强制清理...[/yellow]")
                            self._kill_process_on_port(task['port'])
                            time.sleep(1)
                            
                            # 再次验证
                            if self._check_port_availability(task['port']):
                                console.print(f"[green]✅ 端口 {task['port']} 已成功释放[/green]")
                            else:
                                console.print(f"[red]❌ 端口 {task['port']} 仍被占用，可能需要手动清理[/red]")
                        else:
                            console.print(f"[green]✅ 端口 {task['port']} 已成功释放[/green]")
                    else:
                        console.print(f"[green]✅ 测试进程已自然退出[/green]")
                except Exception as cleanup_error:
                    console.print(f"[red]❌ 清理进程时发生错误: {cleanup_error}[/red]")
                    # 尝试强制清理端口
                    try:
                        self._kill_process_on_port(task['port'])
                    except Exception:
                        pass
    
    def _collect_metrics(self, port: int, test_name: str) -> str:
        """收集指标数据"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                console.print(f"[blue]🔍 尝试收集 {test_name} 指标 (尝试 {attempt + 1}/{max_retries})...[/blue]")
                
                # 等待指标稳定
                time.sleep(retry_delay)
                
                # 收集指标
                metrics = self.metrics_collector.fetch_metrics(port)
                
                if metrics:
                    # 确保reports目录存在
                    import os
                    os.makedirs("reports", exist_ok=True)
                    
                    # 保存指标文件到reports文件夹
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    metrics_file = f"metrics_{test_name.lower().replace(' ', '_')}_{timestamp}.json"
                    metrics_path = os.path.join("reports", metrics_file)
                    
                    # 转换为可序列化格式
                    metrics_data = []
                    for metric in metrics:
                        metrics_data.append({
                            'timestamp': metric.timestamp,
                            'name': metric.name,
                            'value': metric.value,
                            'labels': metric.labels,
                            'help_text': metric.help_text,
                            'metric_type': metric.metric_type
                        })
                    
                    # 保存到文件
                    import json
                    with open(metrics_path, 'w', encoding='utf-8') as f:
                        json.dump(metrics_data, f, indent=2, ensure_ascii=False)
                    
                    console.print(f"[green]✅ 指标已保存: {metrics_path} (收集到 {len(metrics)} 个指标)[/green]")
                    return metrics_path
                else:
                    console.print(f"[yellow]⚠️ 第 {attempt + 1} 次尝试未收集到 {test_name} 的指标数据[/yellow]")
                    if attempt < max_retries - 1:
                        console.print(f"[dim]等待 {retry_delay} 秒后重试...[/dim]")
                    
            except Exception as e:
                console.print(f"[red]❌ 第 {attempt + 1} 次尝试收集 {test_name} 指标失败: {e}[/red]")
                if attempt < max_retries - 1:
                    console.print(f"[dim]等待 {retry_delay} 秒后重试...[/dim]")
        
        console.print(f"[red]❌ 经过 {max_retries} 次尝试，无法收集 {test_name} 的指标数据[/red]")
        return ""
    
    def generate_final_report(self):
        """生成最终报告"""
        console.print("\n" + "="*80)
        console.print("📊 [bold blue]eMQTT-Bench 测试报告生成[/bold blue]")
        console.print("="*80)
        console.print("🎯 [dim]正在生成完整的测试分析报告，包含所有关键指标和性能评估...[/dim]")
        console.print("")
        
        try:
            # 创建时间戳报告目录
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.current_report_dir = f"reports/{timestamp}"
            os.makedirs(self.current_report_dir, exist_ok=True)
            console.print(f"[blue]📁 创建报告目录: {self.current_report_dir}[/blue]")
            
            # 自动执行数据过滤操作
            console.print("[blue]🧹 自动执行数据过滤操作...[/blue]")
            self._auto_filter_all_test_data()
            
            # 自动过滤持续指标文件
            console.print("[blue]🧹 自动过滤持续指标文件...[/blue]")
            self._auto_filter_continuous_metrics()
            
            # 生成HTML报告
            console.print("[blue]📄 生成HTML可视化报告...[/blue]")
            html_report_file = self._generate_html_report()
            
            # 生成Markdown详细分析报告
            console.print("[blue]📝 生成Markdown详细分析报告...[/blue]")
            markdown_report_file = self._generate_markdown_report()
            
            # 生成增强版持续数据分析报告
            if self.continuous_data_files:
                console.print("[blue]📊 生成增强版持续数据分析报告...[/blue]")
                enhanced_report_file = self.enhanced_generator.generate_continuous_analysis_report(
                    continuous_data_files=self.continuous_data_files,
                    test_results=self.test_results,
                    start_time=self.start_time
                )
                console.print(f"[green]✅ 增强版持续数据分析报告: {enhanced_report_file}[/green]")
            else:
                console.print("[yellow]⚠️ 无持续数据文件，跳过增强版报告生成[/yellow]")
            
            # 生成数据管理报告
            console.print("[blue]📊 生成测试数据管理报告...[/blue]")
            data_report_file = self.data_manager.generate_data_report(report_dir=self.current_report_dir)
            console.print(f"[green]✅ 测试数据管理报告: {data_report_file}[/green]")
            
            # 显示报告摘要
            self._show_report_summary()
            
            # 显示报告生成完成信息
            console.print("\n" + "="*80)
            console.print("🎉 [bold green]报告生成完成！[/bold green]")
            console.print("="*80)
            
            # 创建报告文件汇总表格
            report_summary_table = Table(title="📋 生成的报告文件", show_header=True, header_style="bold magenta")
            report_summary_table.add_column("报告类型", style="cyan", width=20)
            report_summary_table.add_column("文件路径", style="green", width=50)
            report_summary_table.add_column("状态", style="yellow", width=10)
            
            report_summary_table.add_row("HTML可视化报告", html_report_file, "✅ 已生成")
            report_summary_table.add_row("Markdown详细分析", markdown_report_file, "✅ 已生成")
            report_summary_table.add_row("测试数据管理报告", data_report_file, "✅ 已生成")
            
            console.print(report_summary_table)
            
            # 显示数据统计信息
            console.print(f"\n[bold]📊 数据统计摘要:[/bold]")
            console.print(f"   📁 指标文件数量: [blue]{len([r for r in self.test_results if r.metrics_file])} 个[/blue]")
            console.print(f"   📂 报告保存位置: [blue]{self.current_report_dir}/ 文件夹[/blue]")
            console.print(f"   💾 测试数据保存位置: [blue]test_data/ 文件夹[/blue]")
            console.print(f"   🧹 过滤数据保存位置: [blue]test_data/filtered_data/ 文件夹[/blue]")
            console.print(f"   ⏱️ 总耗时: [blue]{(datetime.now() - self.start_time).total_seconds():.1f} 秒[/blue]")
            
            # 显示使用建议
            console.print(f"\n[bold]💡 使用建议:[/bold]")
            console.print(f"   🌐 在浏览器中打开HTML报告查看可视化图表")
            console.print(f"   📝 查看Markdown报告获取详细分析")
            console.print(f"   📊 使用数据管理报告了解测试数据详情")
            console.print(f"   🔍 所有原始数据已保存在test_data目录中")
            
        except Exception as e:
            console.print(f"[red]❌ 生成报告失败: {e}[/red]")
            # 记录详细错误信息
            import traceback
            console.print(f"[dim]详细错误信息: {traceback.format_exc()}[/dim]")
    
    def _generate_html_report(self) -> str:
        """生成增强版HTML报告"""
        # 收集所有指标数据
        all_metrics_data = self._collect_all_metrics_data()
        
        # 使用增强版报告生成器，指定报告保存到时间戳目录
        from enhanced_report_generator import EnhancedReportGenerator
        report_generator = EnhancedReportGenerator(
            test_results=self.test_results,
            all_metrics_data=all_metrics_data,
            start_time=self.start_time,
            reports_dir=self.current_report_dir
        )
        
        report_file = report_generator.generate_enhanced_report()
        return report_file
    
    def _generate_markdown_report(self) -> str:
        """生成Markdown详细分析报告"""
        # 收集所有指标数据
        all_metrics_data = self._collect_all_metrics_data()
        
        # 使用Markdown报告生成器
        from simple_markdown_generator import MarkdownReportGenerator
        markdown_generator = MarkdownReportGenerator(
            test_results=self.test_results,
            all_metrics_data=all_metrics_data,
            start_time=self.start_time,
            reports_dir=self.current_report_dir
        )
        
        markdown_file = markdown_generator.generate_markdown_report()
        return markdown_file
    
    def _collect_all_metrics_data(self) -> Dict[str, Any]:
        """收集所有测试的指标数据"""
        all_metrics_data = {}
        
        for result in self.test_results:
            if result.metrics_file and result.success:
                try:
                    import json
                    with open(result.metrics_file, 'r', encoding='utf-8') as f:
                        metrics_data = json.load(f)
                    
                    all_metrics_data[result.test_name] = {
                        'test_info': {
                            'port': result.port,
                            'duration': result.duration,
                            'start_time': result.start_time.isoformat(),
                            'end_time': result.end_time.isoformat(),
                            'metrics_file': result.metrics_file
                        },
                        'metrics': metrics_data
                    }
                except Exception as e:
                    console.print(f"[yellow]⚠️ 无法读取 {result.metrics_file}: {e}[/yellow]")
                    all_metrics_data[result.test_name] = {
                        'test_info': {
                            'port': result.port,
                            'duration': result.duration,
                            'start_time': result.start_time.isoformat(),
                            'end_time': result.end_time.isoformat(),
                            'metrics_file': result.metrics_file
                        },
                        'metrics': []
                    }
            else:
                all_metrics_data[result.test_name] = {
                    'test_info': {
                        'port': result.port,
                        'duration': result.duration,
                        'start_time': result.start_time.isoformat(),
                        'end_time': result.end_time.isoformat(),
                        'metrics_file': result.metrics_file
                    },
                    'metrics': []
                }
        
        return all_metrics_data
    
    def _show_report_summary(self):
        """显示报告摘要"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        console.print("\n" + "="*80)
        console.print("📊 [bold blue]测试执行摘要[/bold blue]")
        console.print("="*80)
        
        # 基本摘要表格
        table = Table(title="📊 测试执行统计", show_header=True, header_style="bold magenta")
        table.add_column("统计项目", style="cyan", width=20)
        table.add_column("数值", style="green", width=15)
        table.add_column("状态", style="yellow", width=15)
        table.add_column("说明", style="dim", width=30)
        
        table.add_row("总测试数", str(total_tests), "📊 测试", "执行的测试项目总数")
        table.add_row("成功测试", str(successful_tests), "✅ 成功" if successful_tests > 0 else "❌ 无成功", "成功完成的测试数量")
        table.add_row("失败测试", str(failed_tests), "⚠️ 需关注" if failed_tests > 0 else "✅ 无失败", "执行失败的测试数量")
        table.add_row("成功率", f"{success_rate:.1f}%", "🟢 优秀" if success_rate >= 90 else "🟡 良好" if success_rate >= 70 else "🔴 需改进", "测试执行成功率")
        table.add_row("总耗时", f"{(datetime.now() - self.start_time).total_seconds():.1f} 秒", "⏱️ 时间", "从开始到结束的总时间")
        table.add_row("指标文件", str(len([r for r in self.test_results if r.metrics_file])), "📁 数据", "收集到的指标文件数量")
        
        console.print(table)
        
        # 详细测试结果展示
        if self.test_results:
            console.print("\n" + "="*80)
            console.print("📋 [bold blue]详细测试结果[/bold blue]")
            console.print("="*80)
            
            # 创建详细测试结果表格
            detailed_table = Table(title="📋 详细测试结果", show_header=True, header_style="bold magenta")
            detailed_table.add_column("序号", style="cyan", width=6)
            detailed_table.add_column("测试名称", style="green", width=20)
            detailed_table.add_column("状态", style="yellow", width=10)
            detailed_table.add_column("端口", style="blue", width=8)
            detailed_table.add_column("持续时间", style="magenta", width=12)
            detailed_table.add_column("指标文件", style="red", width=15)
            
            for i, result in enumerate(self.test_results, 1):
                status_icon = "✅ 成功" if result.success else "❌ 失败"
                metrics_status = "✅ 有" if result.metrics_file else "❌ 无"
                
                detailed_table.add_row(
                    str(i),
                    result.test_name,
                    status_icon,
                    str(result.port),
                    f"{result.duration:.1f}s",
                    metrics_status
                )
            
            console.print(detailed_table)
            
            # 显示每个测试的详细信息
            for i, result in enumerate(self.test_results, 1):
                status_icon = "✅" if result.success else "❌"
                status_color = "green" if result.success else "red"
                
                console.print(f"\n[bold]{i}. {result.test_name}[/bold] {status_icon}")
                console.print(f"   [dim]端口:[/dim] {result.port}")
                console.print(f"   [dim]持续时间:[/dim] {result.duration:.2f} 秒")
                console.print(f"   [dim]开始时间:[/dim] {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                console.print(f"   [dim]结束时间:[/dim] {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if result.metrics_file:
                    console.print(f"   [dim]指标文件:[/dim] {result.metrics_file}")
                    
                    # 显示关键指标
                    self._show_test_metrics(result)
                else:
                    console.print(f"   [yellow]⚠️ 无指标文件[/yellow]")
                
                if result.error_message:
                    console.print(f"   [red]❌ 错误信息: {result.error_message}[/red]")
        
        # 显示测试配置信息
        self._show_test_configuration()
        
        # 指标数据统计
        self._show_metrics_summary()
        
        # 添加性能评估和建议
        self._show_performance_assessment()

    def _show_test_metrics(self, result):
        """显示单个测试的关键指标"""
        try:
            import json
            with open(result.metrics_file, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            
            if not metrics_data:
                console.print(f"   [yellow]⚠️ 指标文件为空[/yellow]")
                return
            
            # 分类显示关键指标
            connection_metrics = []
            mqtt_metrics = []
            performance_metrics = []
            error_metrics = []
            system_metrics = []
            throughput_metrics = []
            latency_metrics = []
            
            # 定义关键指标优先级
            critical_metrics = [
                'connect_succ', 'connect_fail', 'pub_succ', 'pub_fail', 'sub_succ', 'sub_fail',
                'publish_latency', 'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                'e2e_latency', 'mqtt_client_subscribe_duration', 'connection_idle', 'recv',
                'connect_retried', 'reconnect_succ', 'connection_timeout', 'connection_refused',
                'unreachable', 'pub_overrun'
            ]
            
            for metric in metrics_data:
                if isinstance(metric, dict):
                    name = metric.get('name', '')
                    value = metric.get('value', 0)
                    name_lower = name.lower()
                    
                    # 按类别分类指标
                    if any(keyword in name_lower for keyword in ['connect', 'connection']):
                        connection_metrics.append((name, value))
                    elif any(keyword in name_lower for keyword in ['mqtt', 'publish', 'subscribe', 'message', 'pub', 'sub', 'handshake']):
                        mqtt_metrics.append((name, value))
                    elif any(keyword in name_lower for keyword in ['latency', 'duration', 'time']):
                        performance_metrics.append((name, value))
                        if 'latency' in name_lower:
                            latency_metrics.append((name, value))
                    elif any(keyword in name_lower for keyword in ['error', 'fail', 'exception', 'timeout', 'refused', 'unreachable']):
                        error_metrics.append((name, value))
                    elif any(keyword in name_lower for keyword in ['cpu', 'memory', 'disk', 'network', 'system', 'erlang']):
                        system_metrics.append((name, value))
                    elif any(keyword in name_lower for keyword in ['throughput', 'rate', 'succ', 'recv']):
                        throughput_metrics.append((name, value))
            
            # 显示关键指标表格
            self._display_metrics_table(result.test_name, {
                '连接指标': connection_metrics,
                'MQTT指标': mqtt_metrics,
                '性能指标': performance_metrics,
                '错误指标': error_metrics,
                '系统指标': system_metrics,
                '吞吐量指标': throughput_metrics,
                '延迟指标': latency_metrics
            })
            
            # 显示总指标数
            total_metrics = len(metrics_data)
            console.print(f"   [dim]📊 总指标数: {total_metrics}[/dim]")
            
        except Exception as e:
            console.print(f"   [red]❌ 读取指标文件失败: {e}[/red]")
    
    def _show_test_configuration(self):
        """显示测试配置信息"""
        console.print("\n" + "="*60)
        console.print("⚙️ [bold blue]测试配置信息[/bold blue]")
        console.print("="*60)
        
        try:
            # 获取配置信息
            config = self.test_manager.config_manager.config
            
            # 创建配置表格
            config_table = Table(title="📋 测试配置详情", show_header=True, header_style="bold magenta")
            config_table.add_column("配置项", style="cyan", width=20)
            config_table.add_column("值", style="green", width=30)
            config_table.add_column("说明", style="dim", width=40)
            
            # 基本配置
            config_table.add_row("MQTT服务器", f"{config.host}:{config.port}", "MQTT服务器地址和端口")
            config_table.add_row("客户端数量", str(config.client_count), "同时连接的客户端数量")
            config_table.add_row("消息间隔", f"{config.msg_interval}ms", "消息发送间隔时间")
            config_table.add_row("测试持续时间", f"{config.test_duration}秒", "每个测试的持续时间")
            config_table.add_row("QoS等级", str(config.qos), "MQTT消息质量等级")
            config_table.add_row("Prometheus端口", str(config.prometheus_port), "Prometheus指标起始端口")
            
            # 华为云配置
            config_table.add_row("华为云认证", "是" if config.use_huawei_auth else "否", "是否使用华为云IoT认证")
            
            if config.use_huawei_auth:
                config_table.add_row("设备前缀", config.device_prefix, "华为云设备ID前缀")
                config_table.add_row("设备密钥", "***" if config.huawei_secret else "未配置", "华为云设备密钥")
                
                # 华为云广播参数
                huawei_ak = getattr(config, 'huawei_ak', '')
                huawei_sk = getattr(config, 'huawei_sk', '')
                huawei_endpoint = getattr(config, 'huawei_endpoint', '')
                
                if huawei_ak:
                    config_table.add_row("华为云AK", huawei_ak[:8] + "..." if len(huawei_ak) > 8 else huawei_ak, "华为云访问密钥ID")
                else:
                    config_table.add_row("华为云AK", "未配置", "华为云访问密钥ID")
                
                if huawei_sk:
                    config_table.add_row("华为云SK", "***", "华为云访问密钥Secret")
                else:
                    config_table.add_row("华为云SK", "未配置", "华为云访问密钥Secret")
                
                config_table.add_row("华为云端点", huawei_endpoint or "未配置", "华为云IoTDA端点")
                config_table.add_row("华为云区域", getattr(config, 'huawei_region', 'cn-north-4'), "华为云区域ID")
                config_table.add_row("广播主题", getattr(config, 'broadcast_topic', '$oc/broadcast/test'), "广播消息主题")
                config_table.add_row("广播间隔", f"{getattr(config, 'broadcast_interval', 5)}秒", "广播发送间隔")
            
            # eMQTT-Bench配置
            config_table.add_row("eMQTT-Bench路径", config.emqtt_bench_path, "eMQTT-Bench可执行文件路径")
            
            console.print(config_table)
            
            # 显示配置说明
            console.print(f"\n[bold]📝 配置说明:[/bold]")
            console.print(f"   • [cyan]QoS等级:[/cyan] {self._get_qos_description(config.qos)}")
            console.print(f"   • [cyan]测试模式:[/cyan] {'华为云IoT平台测试' if config.use_huawei_auth else '标准MQTT测试'}")
            console.print(f"   • [cyan]监控方式:[/cyan] Prometheus + REST API")
            console.print(f"   • [cyan]数据收集:[/cyan] 持续指标收集 + 实时分析")
            
            # 显示测试环境信息
            console.print(f"\n[bold]🌐 测试环境信息:[/bold]")
            console.print(f"   • [cyan]开始时间:[/cyan] {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            console.print(f"   • [cyan]结束时间:[/cyan] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            console.print(f"   • [cyan]总耗时:[/cyan] {(datetime.now() - self.start_time).total_seconds():.1f} 秒")
            console.print(f"   • [cyan]测试数量:[/cyan] {len(self.test_results)} 个")
            console.print(f"   • [cyan]成功数量:[/cyan] {len([r for r in self.test_results if r.success])} 个")
            
        except Exception as e:
            console.print(f"[red]❌ 显示配置信息失败: {e}[/red]")
    
    def _get_qos_description(self, qos: int) -> str:
        """获取QoS等级描述"""
        qos_descriptions = {
            0: "最多一次 (Fire and Forget) - 不保证消息送达",
            1: "至少一次 (At Least Once) - 保证消息送达，可能重复",
            2: "恰好一次 (Exactly Once) - 保证消息送达且不重复"
        }
        return qos_descriptions.get(qos, "未知QoS等级")
    
    def _display_metrics_table(self, test_name: str, metrics_categories: Dict[str, List]):
        """显示指标分类表格"""
        # 创建指标表格
        metrics_table = Table(title=f"📊 {test_name} - 详细指标分析", show_header=True, header_style="bold magenta")
        metrics_table.add_column("指标类别", style="cyan", width=15)
        metrics_table.add_column("指标名称", style="green", width=25)
        metrics_table.add_column("数值", style="yellow", width=12)
        metrics_table.add_column("状态", style="blue", width=10)
        
        # 定义状态评估函数
        def get_metric_status(name: str, value: float) -> str:
            name_lower = name.lower()
            if 'succ' in name_lower and value > 0:
                return "✅ 良好"
            elif 'fail' in name_lower and value == 0:
                return "✅ 良好"
            elif 'latency' in name_lower:
                if value <= 100:
                    return "✅ 优秀"
                elif value <= 500:
                    return "⚠️ 一般"
                else:
                    return "❌ 较差"
            elif 'duration' in name_lower:
                if value <= 50:
                    return "✅ 优秀"
                elif value <= 200:
                    return "⚠️ 一般"
                else:
                    return "❌ 较差"
            elif 'error' in name_lower or 'fail' in name_lower or 'timeout' in name_lower:
                if value == 0:
                    return "✅ 良好"
                else:
                    return "❌ 需关注"
            else:
                return "📊 正常"
        
        # 填充表格数据
        for category, metrics in metrics_categories.items():
            if metrics:
                # 按重要性排序（关键指标优先）
                critical_metrics = [m for m in metrics if m[0] in [
                    'connect_succ', 'connect_fail', 'pub_succ', 'pub_fail', 'sub_succ', 'sub_fail',
                    'publish_latency', 'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                    'e2e_latency', 'mqtt_client_subscribe_duration'
                ]]
                other_metrics = [m for m in metrics if m[0] not in [
                    'connect_succ', 'connect_fail', 'pub_succ', 'pub_fail', 'sub_succ', 'sub_fail',
                    'publish_latency', 'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                    'e2e_latency', 'mqtt_client_subscribe_duration'
                ]]
                
                # 先显示关键指标
                for name, value in critical_metrics[:3]:  # 最多显示3个关键指标
                    status = get_metric_status(name, value)
                    metrics_table.add_row(category, name, f"{value:.2f}", status)
                
                # 再显示其他重要指标
                for name, value in other_metrics[:2]:  # 最多显示2个其他指标
                    status = get_metric_status(name, value)
                    metrics_table.add_row(category, name, f"{value:.2f}", status)
        
        console.print(metrics_table)

    def _show_metrics_summary(self):
        """显示指标数据统计摘要"""
        console.print("\n" + "="*60)
        console.print("📈 [bold blue]指标数据统计[/bold blue]")
        console.print("="*60)
        
        # 收集所有指标数据
        all_metrics_data = self._collect_all_metrics_data()
        
        if not all_metrics_data:
            console.print("[yellow]⚠️ 无指标数据[/yellow]")
            return
        
        # 统计各类指标
        total_metrics = 0
        mqtt_metrics_count = 0
        connection_metrics_count = 0
        performance_metrics_count = 0
        error_metrics_count = 0
        system_metrics_count = 0
        
        for test_name, test_data in all_metrics_data.items():
            metrics = test_data.get('metrics', [])
            total_metrics += len(metrics)
            
            for metric in metrics:
                if isinstance(metric, dict):
                    name = metric.get('name', '').lower()
                    
                    if any(keyword in name for keyword in ['mqtt', 'publish', 'subscribe', 'message', 'pub', 'sub', 'handshake']):
                        mqtt_metrics_count += 1
                    elif any(keyword in name for keyword in ['connect', 'connection']):
                        connection_metrics_count += 1
                    elif any(keyword in name for keyword in ['latency', 'throughput', 'rate', 'duration', 'time']):
                        performance_metrics_count += 1
                    elif any(keyword in name for keyword in ['error', 'fail', 'exception', 'timeout']):
                        error_metrics_count += 1
                    elif any(keyword in name for keyword in ['cpu', 'memory', 'disk', 'network', 'system']):
                        system_metrics_count += 1
        
        # 显示统计表格
        metrics_table = Table(title="📊 指标分类统计")
        metrics_table.add_column("指标类型", style="cyan", width=15)
        metrics_table.add_column("数量", style="green", width=10)
        metrics_table.add_column("占比", style="yellow", width=10)
        
        if total_metrics > 0:
            metrics_table.add_row("总指标数", str(total_metrics), "100.0%")
            metrics_table.add_row("MQTT指标", str(mqtt_metrics_count), f"{mqtt_metrics_count/total_metrics*100:.1f}%")
            metrics_table.add_row("连接指标", str(connection_metrics_count), f"{connection_metrics_count/total_metrics*100:.1f}%")
            metrics_table.add_row("性能指标", str(performance_metrics_count), f"{performance_metrics_count/total_metrics*100:.1f}%")
            metrics_table.add_row("错误指标", str(error_metrics_count), f"{error_metrics_count/total_metrics*100:.1f}%")
            metrics_table.add_row("系统指标", str(system_metrics_count), f"{system_metrics_count/total_metrics*100:.1f}%")
        
        console.print(metrics_table)
        
        # 显示关键指标汇总
        console.print(f"\n[bold]🔍 关键指标汇总:[/bold]")
        
        # 创建关键指标汇总表格
        summary_table = Table(title="📊 关键指标汇总对比", show_header=True, header_style="bold magenta")
        summary_table.add_column("测试名称", style="cyan", width=20)
        summary_table.add_column("连接成功率", style="green", width=12)
        summary_table.add_column("发布成功率", style="green", width=12)
        summary_table.add_column("订阅成功率", style="green", width=12)
        summary_table.add_column("平均延迟(ms)", style="yellow", width=12)
        summary_table.add_column("错误率", style="red", width=10)
        summary_table.add_column("整体状态", style="blue", width=10)
        
        for test_name, test_data in all_metrics_data.items():
            metrics = test_data.get('metrics', [])
            if metrics:
                # 查找关键指标
                key_metrics = {}
                for metric in metrics:
                    if isinstance(metric, dict):
                        name = metric.get('name', '')
                        value = metric.get('value', 0)
                        key_metrics[name] = value
                
                # 计算关键指标
                connect_succ = key_metrics.get('connect_succ', 0)
                connect_fail = key_metrics.get('connect_fail', 0)
                pub_succ = key_metrics.get('pub_succ', 0)
                pub_fail = key_metrics.get('pub_fail', 0)
                sub_succ = key_metrics.get('sub_succ', 0)
                sub_fail = key_metrics.get('sub_fail', 0)
                publish_latency = key_metrics.get('publish_latency', 0)
                
                # 计算成功率
                total_connects = connect_succ + connect_fail
                total_pubs = pub_succ + pub_fail
                total_subs = sub_succ + sub_fail
                
                connect_success_rate = (connect_succ / total_connects * 100) if total_connects > 0 else 0
                pub_success_rate = (pub_succ / total_pubs * 100) if total_pubs > 0 else 0
                sub_success_rate = (sub_succ / total_subs * 100) if total_subs > 0 else 0
                
                # 计算错误率
                total_errors = connect_fail + pub_fail + sub_fail
                total_operations = total_connects + total_pubs + total_subs
                error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0
                
                # 评估整体状态
                if connect_success_rate >= 95 and pub_success_rate >= 95 and error_rate <= 5:
                    overall_status = "✅ 优秀"
                elif connect_success_rate >= 90 and pub_success_rate >= 90 and error_rate <= 10:
                    overall_status = "⚠️ 良好"
                else:
                    overall_status = "❌ 需关注"
                
                # 添加到表格
                summary_table.add_row(
                    test_name,
                    f"{connect_success_rate:.1f}%" if total_connects > 0 else "N/A",
                    f"{pub_success_rate:.1f}%" if total_pubs > 0 else "N/A",
                    f"{sub_success_rate:.1f}%" if total_subs > 0 else "N/A",
                    f"{publish_latency:.1f}" if publish_latency > 0 else "N/A",
                    f"{error_rate:.1f}%",
                    overall_status
                )
        
        console.print(summary_table)
        
        # 显示详细的关键指标
        console.print(f"\n[bold]📋 详细关键指标:[/bold]")
        for test_name, test_data in all_metrics_data.items():
            metrics = test_data.get('metrics', [])
            if metrics:
                # 查找关键指标
                key_metrics = {}
                for metric in metrics:
                    if isinstance(metric, dict):
                        name = metric.get('name', '')
                        value = metric.get('value', 0)
                        
                        # 扩展关键指标列表
                        if name in [
                            'connect_succ', 'connect_fail', 'pub_succ', 'pub_fail', 'sub_succ', 'sub_fail',
                            'publish_latency', 'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                            'e2e_latency', 'mqtt_client_subscribe_duration', 'connection_idle', 'recv',
                            'connect_retried', 'reconnect_succ', 'connection_timeout', 'connection_refused',
                            'unreachable', 'pub_overrun'
                        ]:
                            key_metrics[name] = value
                
                if key_metrics:
                    # 按类别分组显示
                    connection_metrics = {k: v for k, v in key_metrics.items() if 'connect' in k.lower()}
                    mqtt_metrics = {k: v for k, v in key_metrics.items() if any(x in k.lower() for x in ['pub', 'sub', 'mqtt'])}
                    performance_metrics = {k: v for k, v in key_metrics.items() if any(x in k.lower() for x in ['latency', 'duration', 'time'])}
                    error_metrics = {k: v for k, v in key_metrics.items() if any(x in k.lower() for x in ['fail', 'error', 'timeout', 'refused', 'unreachable'])}
                    
                    console.print(f"   [bold]{test_name}:[/bold]")
                    if connection_metrics:
                        console.print(f"     [blue]🔗 连接:[/blue] {', '.join([f'{k}={v}' for k, v in connection_metrics.items()])}")
                    if mqtt_metrics:
                        console.print(f"     [green]📡 MQTT:[/green] {', '.join([f'{k}={v}' for k, v in mqtt_metrics.items()])}")
                    if performance_metrics:
                        console.print(f"     [yellow]⚡ 性能:[/yellow] {', '.join([f'{k}={v}' for k, v in performance_metrics.items()])}")
                    if error_metrics:
                        console.print(f"     [red]🚨 错误:[/red] {', '.join([f'{k}={v}' for k, v in error_metrics.items()])}")

    def _show_performance_assessment(self):
        """显示性能评估和建议"""
        console.print("\n" + "="*60)
        console.print("🎯 [bold blue]性能评估和建议[/bold blue]")
        console.print("="*60)
        
        # 收集所有测试的性能数据
        all_metrics_data = self._collect_all_metrics_data()
        
        if not all_metrics_data:
            console.print("[yellow]⚠️ 无性能数据可供评估[/yellow]")
            return
        
        # 计算整体性能指标
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 分析各项性能指标
        performance_analysis = self._analyze_performance_metrics(all_metrics_data)
        
        # 显示性能评估表格
        assessment_table = Table(title="📊 性能评估结果", show_header=True, header_style="bold magenta")
        assessment_table.add_column("评估项目", style="cyan", width=20)
        assessment_table.add_column("当前值", style="green", width=15)
        assessment_table.add_column("标准值", style="yellow", width=15)
        assessment_table.add_column("状态", style="blue", width=12)
        assessment_table.add_column("建议", style="red", width=25)
        
        # 连接性能评估
        avg_connect_latency = performance_analysis.get('avg_connect_latency', 0)
        if avg_connect_latency > 0:
            connect_status = "✅ 优秀" if avg_connect_latency <= 100 else "⚠️ 一般" if avg_connect_latency <= 500 else "❌ 较差"
            connect_advice = "保持当前配置" if avg_connect_latency <= 100 else "检查网络延迟" if avg_connect_latency <= 500 else "优化网络配置"
            assessment_table.add_row("连接延迟", f"{avg_connect_latency:.1f}ms", "≤100ms", connect_status, connect_advice)
        
        # 发布性能评估
        avg_pub_latency = performance_analysis.get('avg_pub_latency', 0)
        if avg_pub_latency > 0:
            pub_status = "✅ 优秀" if avg_pub_latency <= 50 else "⚠️ 一般" if avg_pub_latency <= 200 else "❌ 较差"
            pub_advice = "性能良好" if avg_pub_latency <= 50 else "考虑优化QoS" if avg_pub_latency <= 200 else "检查消息大小"
            assessment_table.add_row("发布延迟", f"{avg_pub_latency:.1f}ms", "≤50ms", pub_status, pub_advice)
        
        # 成功率评估
        overall_success_rate = performance_analysis.get('overall_success_rate', success_rate)
        success_status = "✅ 优秀" if overall_success_rate >= 95 else "⚠️ 良好" if overall_success_rate >= 90 else "❌ 需关注"
        success_advice = "系统稳定" if overall_success_rate >= 95 else "监控运行" if overall_success_rate >= 90 else "检查配置"
        assessment_table.add_row("整体成功率", f"{overall_success_rate:.1f}%", "≥95%", success_status, success_advice)
        
        # 错误率评估
        error_rate = performance_analysis.get('error_rate', 0)
        error_status = "✅ 优秀" if error_rate <= 1 else "⚠️ 一般" if error_rate <= 5 else "❌ 较差"
        error_advice = "错误率正常" if error_rate <= 1 else "关注错误日志" if error_rate <= 5 else "排查错误原因"
        assessment_table.add_row("错误率", f"{error_rate:.1f}%", "≤1%", error_status, error_advice)
        
        # 吞吐量评估
        avg_throughput = performance_analysis.get('avg_throughput', 0)
        if avg_throughput > 0:
            throughput_status = "✅ 优秀" if avg_throughput >= 1000 else "⚠️ 一般" if avg_throughput >= 500 else "❌ 较低"
            throughput_advice = "吞吐量良好" if avg_throughput >= 1000 else "可优化并发" if avg_throughput >= 500 else "增加客户端数"
            assessment_table.add_row("平均吞吐量", f"{avg_throughput:.0f}/s", "≥1000/s", throughput_status, throughput_advice)
        
        console.print(assessment_table)
        
        # 显示优化建议
        self._show_optimization_recommendations(performance_analysis)
        
        # 显示整体评估结论
        self._show_overall_assessment(performance_analysis, success_rate)
    
    def _analyze_performance_metrics(self, all_metrics_data: Dict[str, Any]) -> Dict[str, float]:
        """分析性能指标"""
        analysis = {
            'avg_connect_latency': 0,
            'avg_pub_latency': 0,
            'overall_success_rate': 0,
            'error_rate': 0,
            'avg_throughput': 0,
            'total_operations': 0,
            'total_errors': 0
        }
        
        total_connect_latency = 0
        total_pub_latency = 0
        total_operations = 0
        total_errors = 0
        total_success = 0
        test_count = 0
        
        for test_name, test_data in all_metrics_data.items():
            metrics = test_data.get('metrics', [])
            if not metrics:
                continue
                
            test_count += 1
            
            # 提取指标值
            key_metrics = {}
            for metric in metrics:
                if isinstance(metric, dict):
                    name = metric.get('name', '')
                    value = metric.get('value', 0)
                    key_metrics[name] = value
            
            # 计算连接延迟
            connect_duration = key_metrics.get('mqtt_client_connect_duration', 0)
            if connect_duration > 0:
                total_connect_latency += connect_duration
            
            # 计算发布延迟
            pub_latency = key_metrics.get('publish_latency', 0)
            if pub_latency > 0:
                total_pub_latency += pub_latency
            
            # 计算操作数和错误数
            connect_succ = key_metrics.get('connect_succ', 0)
            connect_fail = key_metrics.get('connect_fail', 0)
            pub_succ = key_metrics.get('pub_succ', 0)
            pub_fail = key_metrics.get('pub_fail', 0)
            sub_succ = key_metrics.get('sub_succ', 0)
            sub_fail = key_metrics.get('sub_fail', 0)
            
            test_operations = connect_succ + connect_fail + pub_succ + pub_fail + sub_succ + sub_fail
            test_errors = connect_fail + pub_fail + sub_fail
            test_success = connect_succ + pub_succ + sub_succ
            
            total_operations += test_operations
            total_errors += test_errors
            total_success += test_success
        
        # 计算平均值
        if test_count > 0:
            analysis['avg_connect_latency'] = total_connect_latency / test_count
            analysis['avg_pub_latency'] = total_pub_latency / test_count
        
        if total_operations > 0:
            analysis['overall_success_rate'] = (total_success / total_operations) * 100
            analysis['error_rate'] = (total_errors / total_operations) * 100
            analysis['avg_throughput'] = total_success / total_operations * 1000  # 假设测试持续时间为1000秒
        
        analysis['total_operations'] = total_operations
        analysis['total_errors'] = total_errors
        
        return analysis
    
    def _show_optimization_recommendations(self, performance_analysis: Dict[str, float]):
        """显示优化建议"""
        console.print(f"\n[bold]💡 优化建议:[/bold]")
        
        recommendations = []
        
        # 基于性能分析生成建议
        avg_connect_latency = performance_analysis.get('avg_connect_latency', 0)
        avg_pub_latency = performance_analysis.get('avg_pub_latency', 0)
        error_rate = performance_analysis.get('error_rate', 0)
        overall_success_rate = performance_analysis.get('overall_success_rate', 0)
        
        if avg_connect_latency > 500:
            recommendations.append("🔧 连接延迟过高，建议检查网络配置和服务器性能")
        
        if avg_pub_latency > 200:
            recommendations.append("📡 发布延迟较高，建议优化消息大小和QoS设置")
        
        if error_rate > 5:
            recommendations.append("🚨 错误率较高，建议检查网络稳定性和认证配置")
        
        if overall_success_rate < 90:
            recommendations.append("⚠️ 整体成功率偏低，建议检查MQTT服务器配置")
        
        # 通用建议
        recommendations.extend([
            "📊 建议定期监控关键性能指标",
            "🔄 考虑在不同时间段进行压力测试",
            "📈 根据业务需求调整客户端数量和消息频率",
            "🛡️ 确保网络连接稳定性和安全性"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            console.print(f"   {i}. {rec}")
    
    def _show_overall_assessment(self, performance_analysis: Dict[str, float], success_rate: float):
        """显示整体评估结论"""
        console.print(f"\n[bold]🎯 整体评估结论:[/bold]")
        
        # 计算综合评分
        score = 0
        max_score = 100
        
        # 成功率评分 (40分)
        if success_rate >= 95:
            score += 40
        elif success_rate >= 90:
            score += 30
        elif success_rate >= 80:
            score += 20
        else:
            score += 10
        
        # 延迟评分 (30分)
        avg_connect_latency = performance_analysis.get('avg_connect_latency', 0)
        avg_pub_latency = performance_analysis.get('avg_pub_latency', 0)
        
        if avg_connect_latency <= 100 and avg_pub_latency <= 50:
            score += 30
        elif avg_connect_latency <= 500 and avg_pub_latency <= 200:
            score += 20
        else:
            score += 10
        
        # 错误率评分 (30分)
        error_rate = performance_analysis.get('error_rate', 0)
        if error_rate <= 1:
            score += 30
        elif error_rate <= 5:
            score += 20
        else:
            score += 10
        
        # 显示评分结果
        if score >= 90:
            console.print(f"   [green]🏆 综合评分: {score}/{max_score} - 优秀[/green]")
            console.print(f"   [green]🎉 系统性能表现优秀，各项指标均达到预期标准[/green]")
        elif score >= 70:
            console.print(f"   [yellow]⭐ 综合评分: {score}/{max_score} - 良好[/yellow]")
            console.print(f"   [yellow]👍 系统性能表现良好，建议关注部分指标优化[/yellow]")
        elif score >= 50:
            console.print(f"   [orange]⚠️ 综合评分: {score}/{max_score} - 一般[/orange]")
            console.print(f"   [orange]🔧 系统性能需要改进，建议优化配置和网络环境[/orange]")
        else:
            console.print(f"   [red]❌ 综合评分: {score}/{max_score} - 需关注[/red]")
            console.print(f"   [red]🚨 系统性能需要重点关注，建议全面检查配置和网络[/red]")

def filter_existing_data():
    """过滤现有的raw_data文件"""
    console.print("🧹 [bold blue]数据过滤工具[/bold blue]")
    console.print("=" * 60)
    console.print("✨ [yellow]过滤现有raw_data文件中的无效数据[/yellow]")
    console.print("")
    
    # 创建数据收集器实例
    collector = AutoDataCollector()
    
    # 查找所有raw_data文件
    raw_data_dir = "test_data/raw_data"
    if not os.path.exists(raw_data_dir):
        console.print(f"[red]❌ 目录不存在: {raw_data_dir}[/red]")
        return
    
    raw_data_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
    
    if not raw_data_files:
        console.print(f"[yellow]⚠️ 在 {raw_data_dir} 中未找到JSON文件[/yellow]")
        return
    
    console.print(f"[cyan]📁 找到 {len(raw_data_files)} 个raw_data文件:[/cyan]")
    for i, file in enumerate(raw_data_files, 1):
        console.print(f"  {i}. {file}")
    console.print("")
    
    # 询问是否处理所有文件
    if Confirm.ask("是否过滤所有raw_data文件?", default=True):
        console.print("[green]✅ 开始过滤所有文件...[/green]")
        
        for file in raw_data_files:
            file_path = os.path.join(raw_data_dir, file)
            console.print(f"\n[blue]🔍 处理文件: {file}[/blue]")
            
            try:
                # 读取原始数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取测试信息
                test_name = data.get('test_name', 'Unknown')
                raw_metrics = data.get('raw_metrics', [])
                
                # 过滤数据
                filtered_metrics = collector._filter_invalid_metrics(raw_metrics, test_name)
                
                # 创建过滤后的数据结构
                filtered_data = {
                    "test_name": test_name,
                    "test_type": data.get('test_type', 'Unknown'),
                    "start_time": data.get('start_time', ''),
                    "end_time": data.get('end_time', ''),
                    "duration": data.get('duration', 0),
                    "port": data.get('port', 0),
                    "success": data.get('success', False),
                    "error_message": data.get('error_message', None),
                    "config": data.get('config', {}),
                    "filtered_metrics": filtered_metrics,
                    "filter_info": {
                        "original_count": len(raw_metrics),
                        "filtered_count": len(filtered_metrics),
                        "removed_count": len(raw_metrics) - len(filtered_metrics),
                        "filter_timestamp": datetime.now().isoformat(),
                        "source_file": file
                    }
                }
                
                # 保存过滤后的数据
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filtered_filename = f"filtered_{test_name}_{timestamp}.json"
                filtered_path = os.path.join("test_data", "filtered_data", filtered_filename)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(filtered_path), exist_ok=True)
                
                with open(filtered_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, indent=2, ensure_ascii=False)
                
                # 显示统计信息
                original_count = len(raw_metrics)
                filtered_count = len(filtered_metrics)
                removed_count = original_count - filtered_count
                reduction_percent = (removed_count / original_count * 100) if original_count > 0 else 0
                
                console.print(f"[green]✅ 过滤完成: {file}[/green]")
                console.print(f"[dim]  • 原始指标: {original_count}[/dim]")
                console.print(f"[dim]  • 过滤后指标: {filtered_count}[/dim]")
                console.print(f"[dim]  • 移除指标: {removed_count} ({reduction_percent:.1f}%)[/dim]")
                console.print(f"[dim]  • 保存位置: {filtered_path}[/dim]")
                
            except Exception as e:
                console.print(f"[red]❌ 处理文件 {file} 失败: {e}[/red]")
        
        console.print(f"\n[green]🎉 数据过滤完成！[/green]")
        console.print(f"[blue]📁 过滤后的数据保存在: test_data/filtered_data/[/blue]")
    else:
        console.print("[yellow]用户取消操作[/yellow]")

def filter_continuous_metrics():
    """过滤持续指标文件的主函数"""
    console.print("[blue]🔍 开始过滤持续指标文件...[/blue]")
    
    # 创建测试特定过滤器实例
    test_filter = TestSpecificFilter()
    
    # 自动过滤所有持续指标文件
    filtered_files = test_filter.auto_filter_all_continuous_files("metrics/reports")
    
    if filtered_files:
        console.print(f"[green]✅ 持续指标过滤完成![/green]")
        console.print(f"[blue]📊 过滤统计:[/blue]")
        console.print(f"[dim]  • 处理文件数: {len(filtered_files)}[/dim]")
        console.print(f"[dim]  • 过滤后文件保存在: metrics/reports/filtered/[/dim]")
        
        # 显示过滤后的文件列表
        for file_path in filtered_files:
            console.print(f"[dim]  • {os.path.basename(file_path)}[/dim]")
    else:
        console.print("[yellow]⚠️ 没有找到需要过滤的持续指标文件[/yellow]")

def main():
    """主函数"""
    console.print("🚀 [bold blue]eMQTT-Bench 数据收集和过滤工具[/bold blue]")
    console.print("=" * 60)
    console.print("请选择操作:")
    console.print("  [cyan]1.[/cyan] 运行自动数据收集（包含数据过滤）")
    console.print("  [cyan]2.[/cyan] 仅过滤现有raw_data文件")
    console.print("  [cyan]3.[/cyan] 过滤持续指标文件")
    console.print("")
    
    choice = Prompt.ask("请选择 (1-3)", default="1")
    
    if choice == "1":
        collector = AutoDataCollector()
        collector.run_automatic_collection()
    elif choice == "2":
        filter_existing_data()
    elif choice == "3":
        filter_continuous_metrics()
    else:
        console.print("[red]❌ 无效选择[/red]")

if __name__ == "__main__":
    main()
