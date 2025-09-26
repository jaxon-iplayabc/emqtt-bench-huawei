#!/usr/bin/env python3
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

from emqtt_test_manager import EMQTTTestManager, TestConfig, TestResult
from metrics_collector import PrometheusMetricsCollector, MetricsAnalyzer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()

class AutoDataCollector:
    """自动数据收集器"""
    
    def __init__(self):
        self.test_manager = EMQTTTestManager()
        self.metrics_collector = PrometheusMetricsCollector()
        self.metrics_analyzer = MetricsAnalyzer()
        self.test_results: List[TestResult] = []
        self.running = True
        self.start_time = datetime.now()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        console.print("\n[yellow]收到中断信号，正在生成报告...[/yellow]")
        self.running = False
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
        else:
            # 快速配置调整
            console.print("\n[yellow]快速配置调整:[/yellow]")
            config.host = Prompt.ask("MQTT服务器地址", default=config.host)
            config.port = IntPrompt.ask("MQTT端口", default=config.port)
            config.client_count = IntPrompt.ask("客户端数量", default=config.client_count)
            config.test_duration = IntPrompt.ask("测试持续时间(秒)", default=config.test_duration)
            config.prometheus_port = IntPrompt.ask("Prometheus起始端口", default=config.prometheus_port)
            
            # 华为云认证配置
            console.print("\n[cyan]🔐 华为云IoT认证配置:[/cyan]")
            config.use_huawei_auth = Confirm.ask("是否使用华为云IoT认证?", default=config.use_huawei_auth)
            
            if config.use_huawei_auth:
                console.print("[yellow]📝 华为云认证参数设置:[/yellow]")
                config.device_prefix = Prompt.ask("设备ID前缀", default=config.device_prefix)
                config.huawei_secret = Prompt.ask("设备密钥", default=config.huawei_secret, password=True)
                
                # 显示华为云配置说明
                console.print("\n[dim]💡 华为云配置说明:[/dim]")
                console.print("[dim]  • 设备ID前缀: 用于生成设备ID，如 'speaker' 会生成 speaker_000000001, speaker_000000002 等[/dim]")
                console.print("[dim]  • 设备密钥: 华为云IoT平台中设备的密钥[/dim]")
                console.print("[dim]  • 确保设备已在华为云IoT平台注册[/dim]")
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
            config_table.add_row("设备密钥", config.huawei_secret, "华为云设备密钥")
        
        # 突出显示eMQTT-Bench路径
        config_table.add_row("🔧 eMQTT-Bench路径", config.emqtt_bench_path, "eMQTT-Bench可执行文件路径")
        
        console.print(config_table)
        console.print("")
    
    def _select_test_items(self, config: TestConfig) -> List[Dict[str, Any]]:
        """选择要运行的测试项"""
        console.print(Panel.fit("[bold blue]🧪 测试项选择[/bold blue]"))
        
        # 定义所有可用的测试项
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
        
        # 如果启用华为云认证，添加华为云测试
        if config.use_huawei_auth:
            available_tests.append({
                "name": "华为云测试",
                "description": "测试华为云IoT平台连接和消息发布",
                "command": self._build_huawei_test_command(config),
                "port": config.prometheus_port + 3,
                "duration": config.test_duration,
                "enabled": True
            })
        
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
        console.print("  [cyan]3.[/cyan] 快速测试（仅连接测试）")
        
        while True:
            choice = Prompt.ask("请选择 (1-3)", default="1")
            
            if choice == "1":
                console.print("[green]✅ 将运行所有测试项[/green]")
                return available_tests
                
            elif choice == "2":
                return self._custom_select_tests(available_tests)
                
            elif choice == "3":
                console.print("[green]✅ 将运行快速测试（仅连接测试）[/green]")
                return [available_tests[0]]  # 只返回连接测试
                
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
                
                progress.update(task_progress, completed=task['duration'])
                console.print(f"[green]✅ {task['name']} 完成[/green]")
        
        console.print(f"\n[green]🎉 所有测试完成！共完成 {len(self.test_results)} 个测试[/green]")
    
    def _build_connection_test_command(self, config: TestConfig) -> str:
        """构建连接测试命令"""
        cmd = f"{config.emqtt_bench_path} conn -h {config.host} -p {config.port} -c {config.client_count} -i 10"
        
        if config.use_huawei_auth:
            cmd += f" --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
        
        cmd += f" --prometheus --restapi {config.prometheus_port} --qoe true"
        return cmd
    
    def _build_publish_test_command(self, config: TestConfig) -> str:
        """构建发布测试命令"""
        cmd = f"{config.emqtt_bench_path} pub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -I {config.msg_interval}"
        
        if config.use_huawei_auth:
            cmd += f" -t '$oc/devices/%d/sys/properties/report' --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth --message 'template://./huawei_cloud_payload_template.json'"
        else:
            cmd += " -t 'test/publish/%i'"
        
        cmd += f" --prometheus --restapi {config.prometheus_port + 1} --qoe true"
        return cmd
    
    def _build_subscribe_test_command(self, config: TestConfig) -> str:
        """构建订阅测试命令"""
        cmd = f"{config.emqtt_bench_path} sub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -t 'test/subscribe/%i'"
        cmd += f" --prometheus --restapi {config.prometheus_port + 2} --qoe true"
        return cmd
    
    def _build_huawei_test_command(self, config: TestConfig) -> str:
        """构建华为云测试命令"""
        cmd = f"{config.emqtt_bench_path} pub -h {config.host} -p {config.port} -c {config.client_count} -i 10 -I {config.msg_interval}"
        cmd += f" -t '$oc/devices/%d/sys/properties/report' --prefix '{config.device_prefix}' -P '{config.huawei_secret}' --huawei-auth"
        cmd += f" --message 'template://./huawei_cloud_payload_template.json' --prometheus --restapi {config.prometheus_port + 3} --qoe true"
        return cmd
    
    def _execute_single_test(self, task: Dict[str, Any], progress, task_progress) -> TestResult:
        """执行单个测试"""
        start_time = datetime.now()
        metrics_file = ""
        process = None
        success = False
        error_message = ""
        
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
        console.print("\n" + "="*60)
        console.print("📊 [bold blue]生成最终报告[/bold blue]")
        console.print("="*60)
        
        try:
            # 生成HTML报告
            report_file = self._generate_html_report()
            
            # 显示报告摘要
            self._show_report_summary()
            
            console.print(f"\n🎉 [green]报告生成完成！[/green]")
            console.print(f"📄 HTML报告: [blue]{report_file}[/blue]")
            console.print(f"📁 指标文件: [blue]{len([r for r in self.test_results if r.metrics_file])} 个[/blue]")
            console.print(f"📂 报告保存位置: [blue]reports/ 文件夹[/blue]")
            console.print(f"⏱️ 总耗时: [blue]{(datetime.now() - self.start_time).total_seconds():.1f} 秒[/blue]")
            
        except Exception as e:
                console.print(f"[red]❌ 生成报告失败: {e}[/red]")
    
    def _generate_html_report(self) -> str:
        """生成增强版HTML报告"""
        # 收集所有指标数据
        all_metrics_data = self._collect_all_metrics_data()
        
        # 使用增强版报告生成器，指定报告保存到reports文件夹
        from enhanced_report_generator import EnhancedReportGenerator
        report_generator = EnhancedReportGenerator(
            test_results=self.test_results,
            all_metrics_data=all_metrics_data,
            start_time=self.start_time,
            reports_dir="reports"
        )
        
        report_file = report_generator.generate_enhanced_report()
        return report_file
    
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
        table = Table(title="📊 数据收集摘要")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("总测试数", str(len(self.test_results)))
        table.add_row("成功测试", str(len([r for r in self.test_results if r.success])))
        table.add_row("失败测试", str(len([r for r in self.test_results if not r.success])))
        table.add_row("总耗时", f"{(datetime.now() - self.start_time).total_seconds():.1f} 秒")
        table.add_row("指标文件", str(len([r for r in self.test_results if r.metrics_file])))
        
        console.print(table)

def main():
    """主函数"""
    collector = AutoDataCollector()
    collector.run_automatic_collection()

if __name__ == "__main__":
    main()
