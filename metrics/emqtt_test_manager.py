#!/usr/bin/env python3
"""
eMQTT-Bench 集成测试管理器
集成配置管理、测试执行、数据收集和报表生成功能
作者: Jaxon
日期: 2024-12-19
"""

import os
import sys
import json
import time
import subprocess
import signal
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

def get_huawei_template_path() -> str:
    """获取华为云模板文件的绝对路径"""
    # 获取当前文件所在目录的父目录（项目根目录）
    current_dir = Path(__file__).parent
    project_root = current_dir
    template_path = project_root / "huawei_cloud_payload_template.json"
    return str(template_path.absolute())
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import print as rprint
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

console = Console()

@dataclass
class TestConfig:
    """测试配置"""
    # 基础配置
    host: str = "localhost"  # 统一的MQTT服务器地址
    port: int = 1883         # 统一的MQTT端口
    client_count: int = 5
    msg_interval: int = 1000
    prometheus_port: int = 9090
    
    # 华为云配置
    device_prefix: str = "speaker"
    huawei_secret: str = "12345678"
    use_huawei_auth: bool = False  # 是否使用华为云认证
    
    # 华为云广播测试参数
    huawei_ak: str = ""  # 华为云访问密钥ID
    huawei_sk: str = ""  # 华为云访问密钥Secret
    huawei_endpoint: str = ""  # 华为云IoTDA端点
    huawei_region: str = "cn-north-4"  # 华为云区域ID
    broadcast_topic: str = "$oc/broadcast/test"  # 广播主题
    broadcast_interval: int = 5  # 广播发送间隔（秒）
    
    # MQTT配置
    qos: int = 1  # QoS等级，默认为1
    
    # 测试配置
    test_duration: int = 30
    emqtt_bench_path: str = "emqtt_bench"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestConfig':
        return cls(**data)

@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    port: int
    metrics_file: str
    success: bool
    error_message: Optional[str] = None

class ProcessManager:
    """进程管理器"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        console.print("\n[yellow]收到退出信号，正在清理进程...[/yellow]")
        self.cleanup_all()
        sys.exit(0)
    
    def start_process(self, command: str, description: str = "") -> subprocess.Popen:
        """启动进程"""
        try:
            console.print(f"[blue]启动进程: {description}[/blue]")
            console.print(f"[dim]命令: {command}[/dim]")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.processes.append(process)
            console.print(f"[green]✅ 进程已启动: PID {process.pid}[/green]")
            return process
            
        except Exception as e:
            console.print(f"[red]❌ 启动进程失败: {e}[/red]")
            raise
    
    def wait_for_process(self, process: subprocess.Popen, timeout: int = 30) -> bool:
        """等待进程完成"""
        try:
            process.wait(timeout=timeout)
            return process.returncode == 0
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]⏰ 进程超时，正在终止...[/yellow]")
            self.terminate_process(process)
            return False
    
    def terminate_process(self, process: subprocess.Popen):
        """终止进程"""
        try:
            if process.poll() is None:  # 进程仍在运行
                console.print(f"[yellow]🔄 正在终止进程 {process.pid}...[/yellow]")
                
                # 优雅终止
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                time.sleep(3)  # 增加等待时间
                
                # 强制终止
                if process.poll() is None:
                    console.print(f"[yellow]⚠️ 进程 {process.pid} 未响应SIGTERM，使用SIGKILL强制终止...[/yellow]")
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    time.sleep(1)
                
                # 验证进程是否已终止
                if process.poll() is None:
                    console.print(f"[red]❌ 进程 {process.pid} 仍在使用中[/red]")
                else:
                    console.print(f"[green]✅ 进程 {process.pid} 已成功终止[/green]")
        except ProcessLookupError:
            console.print(f"[green]✅ 进程 {process.pid} 已不存在[/green]")
        except Exception as e:
            console.print(f"[red]❌ 终止进程失败: {e}[/red]")
    
    def cleanup_all(self):
        """清理所有进程"""
        console.print("[yellow]🧹 清理所有进程...[/yellow]")
        
        for process in self.processes:
            if process.poll() is None:  # 进程仍在运行
                self.terminate_process(process)
        
        self.processes.clear()
        console.print("[green]✅ 所有进程已清理[/green]")

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "emqtt_test_config.json"):
        self.config_file = Path(config_file)
        self.config: Optional[TestConfig] = None
    
    def load_config(self) -> TestConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = TestConfig.from_dict(data)
                console.print(f"[green]✅ 配置已加载: {self.config_file}[/green]")
                return self.config
            except Exception as e:
                console.print(f"[red]❌ 加载配置失败: {e}[/red]")
        
        # 创建默认配置
        self.config = TestConfig()
        return self.config
    
    def save_config(self, config: TestConfig):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ 配置已保存: {self.config_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ 保存配置失败: {e}[/red]")
    
    def interactive_config(self) -> TestConfig:
        """交互式配置"""
        console.print(Panel.fit("[bold blue]eMQTT-Bench 测试配置[/bold blue]"))
        
        config = TestConfig()
        
        # 基础配置
        console.print("\n[bold yellow]📝 基础配置[/bold yellow]")
        config.host = Prompt.ask("MQTT服务器地址", default=config.host)
        config.port = IntPrompt.ask("MQTT端口", default=config.port)
        config.client_count = IntPrompt.ask("客户端数量", default=config.client_count)
        config.msg_interval = IntPrompt.ask("消息间隔(ms)", default=config.msg_interval)
        config.prometheus_port = IntPrompt.ask("Prometheus起始端口", default=config.prometheus_port)
        
        # 华为云配置
        console.print("\n[bold yellow]☁️ 华为云配置[/bold yellow]")
        config.use_huawei_auth = Confirm.ask("是否使用华为云认证?", default=config.use_huawei_auth)
        if config.use_huawei_auth:
            config.device_prefix = Prompt.ask("设备前缀", default=config.device_prefix)
            config.huawei_secret = Prompt.ask("设备密钥", default=config.huawei_secret)
        
        # 测试配置
        console.print("\n[bold yellow]⚙️ 测试配置[/bold yellow]")
        config.test_duration = IntPrompt.ask("测试持续时间(秒)", default=config.test_duration)
        config.emqtt_bench_path = Prompt.ask("emqtt_bench路径", default=config.emqtt_bench_path)
        
        # 显示配置摘要
        self._show_config_summary(config)
        
        # 确认配置
        if Confirm.ask("是否确认使用以上配置?"):
            if Confirm.ask("是否保存配置?"):
                self.save_config(config)
            return config
        else:
            return self.interactive_config()
    
    def _show_config_summary(self, config: TestConfig):
        """显示配置摘要"""
        table = Table(title="配置摘要")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("MQTT服务器", f"{config.host}:{config.port}")
        table.add_row("客户端数量", str(config.client_count))
        table.add_row("消息间隔", f"{config.msg_interval}ms")
        table.add_row("Prometheus端口", str(config.prometheus_port))
        table.add_row("华为云认证", "是" if config.use_huawei_auth else "否")
        if config.use_huawei_auth:
            table.add_row("设备前缀", config.device_prefix)
            table.add_row("设备密钥", config.huawei_secret)
        table.add_row("测试持续时间", f"{config.test_duration}秒")
        
        console.print(table)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
    
    def collect_metrics(self, port: int, test_name: str) -> str:
        """收集指标数据"""
        url = f"{self.base_url}:{port}/metrics"
        metrics_file = f"metrics_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            console.print(f"[blue]🔍 收集指标: {test_name} (端口: {port})[/blue]")
            
            # 等待指标稳定
            time.sleep(2)
            
            response = self.session.get(url)
            response.raise_for_status()
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            console.print(f"[green]✅ 指标已保存: {metrics_file}[/green]")
            return metrics_file
            
        except Exception as e:
            console.print(f"[red]❌ 收集指标失败: {e}[/red]")
            return ""
    
    def parse_metrics(self, metrics_file: str) -> Dict[str, Any]:
        """解析指标数据"""
        metrics = {}
        
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析基本计数器指标
            counter_patterns = {
                'connect_succ': r'connect_succ\s+(\d+)',
                'connect_fail': r'connect_fail\s+(\d+)',
                'connect_retried': r'connect_retried\s+(\d+)',
                'connection_timeout': r'connection_timeout\s+(\d+)',
                'connection_refused': r'connection_refused\s+(\d+)',
                'unreachable': r'unreachable\s+(\d+)',
            }
            
            for metric_name, pattern in counter_patterns.items():
                import re
                match = re.search(pattern, content)
                if match:
                    metrics[metric_name] = int(match.group(1))
                else:
                    metrics[metric_name] = 0
            
            # 解析直方图指标
            histogram_patterns = {
                'mqtt_client_handshake_duration': {
                    'count': r'mqtt_client_handshake_duration_count\s+(\d+)',
                    'sum': r'mqtt_client_handshake_duration_sum\s+(\d+)',
                },
                'mqtt_client_connect_duration': {
                    'count': r'mqtt_client_connect_duration_count\s+(\d+)',
                    'sum': r'mqtt_client_connect_duration_sum\s+(\d+)',
                }
            }
            
            for metric_name, patterns in histogram_patterns.items():
                metrics[metric_name] = {}
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        metrics[metric_name][key] = int(match.group(1))
                    else:
                        metrics[metric_name][key] = 0
            
            return metrics
            
        except Exception as e:
            console.print(f"[red]❌ 解析指标失败: {e}[/red]")
            return {}

class TestExecutor:
    """测试执行器"""
    
    def __init__(self, config: TestConfig, process_manager: ProcessManager, metrics_collector: MetricsCollector):
        self.config = config
        self.process_manager = process_manager
        self.metrics_collector = metrics_collector
        self.results: List[TestResult] = []
    
    def run_connection_test(self) -> TestResult:
        """运行连接测试"""
        test_name = "connection"
        port = self.config.prometheus_port
        
        # 构建基础命令
        command = f"""{self.config.emqtt_bench_path} conn \
            -h {self.config.host} \
            -p {self.config.port} \
            -c {self.config.client_count} \
            -i 10 \
            --prometheus \
            --restapi {port} \
            --qoe true"""
        
        # 如果使用华为云认证，添加相关参数
        if self.config.use_huawei_auth:
            command += f""" \
            --prefix "{self.config.device_prefix}" \
            -P '{self.config.huawei_secret}' \
            --huawei-auth"""
        
        return self._run_test(test_name, command, port)
    
    def run_publish_test(self) -> TestResult:
        """运行发布测试"""
        test_name = "publish"
        port = self.config.prometheus_port + 1
        
        # 构建基础命令
        command = f"""{self.config.emqtt_bench_path} pub \
            -h {self.config.host} \
            -p {self.config.port} \
            -c {self.config.client_count} \
            -i 10 \
            -I {self.config.msg_interval} \
            --prometheus \
            --restapi {port} \
            --qoe true"""
        
        # 根据是否使用华为云认证设置不同的topic和参数
        if self.config.use_huawei_auth:
            template_path = get_huawei_template_path()
            command += f""" \
            -t '$oc/devices/%d/sys/properties/report' \
            --prefix "{self.config.device_prefix}" \
            -P '{self.config.huawei_secret}' \
            --huawei-auth \
            --message 'template://{template_path}'"""
        else:
            command += f""" \
            -t 'test/topic/%i' \
            -s 256"""
        
        return self._run_test(test_name, command, port)
    
    def run_subscribe_test(self) -> TestResult:
        """运行订阅测试"""
        test_name = "subscribe"
        port = self.config.prometheus_port + 2
        
        # 构建基础命令
        command = f"""{self.config.emqtt_bench_path} sub \
            -h {self.config.host} \
            -p {self.config.port} \
            -c {self.config.client_count} \
            -i 10 \
            --prometheus \
            --restapi {port} \
            --qoe true"""
        
        # 根据是否使用华为云认证设置不同的topic
        if self.config.use_huawei_auth:
            command += f""" \
            -t '$oc/devices/%d/sys/properties/report' \
            --prefix "{self.config.device_prefix}" \
            -P '{self.config.huawei_secret}' \
            --huawei-auth"""
        else:
            command += f""" \
            -t 'test/topic/%i'"""
        
        return self._run_test(test_name, command, port)
    
    def run_huawei_test(self) -> TestResult:
        """运行华为云测试（已合并到其他测试中）"""
        console.print("[yellow]⚠️ 华为云测试已合并到其他测试中，请使用发布测试并启用华为云认证[/yellow]")
        return self.run_publish_test()
    
    def run_custom_test(self, custom_config: Dict[str, Any]) -> TestResult:
        """运行自定义测试"""
        test_name = "custom"
        port = self.config.prometheus_port + 4
        
        clients = custom_config.get('clients', self.config.client_count)
        interval = custom_config.get('interval', self.config.msg_interval)
        topic = custom_config.get('topic', 'test/custom/%i')
        duration = custom_config.get('duration', self.config.test_duration)
        
        command = f"""{self.config.emqtt_bench_path} pub \
            -h {self.config.host} \
            -p {self.config.port} \
            -c {clients} \
            -i 10 \
            -I {interval} \
            -t '{topic}' \
            --prometheus \
            --restapi {port} \
            --qoe true"""
        
        return self._run_test(test_name, command, port, duration)
    
    def _run_test(self, test_name: str, command: str, port: int, duration: Optional[int] = None) -> TestResult:
        """运行测试"""
        if duration is None:
            duration = self.config.test_duration
        
        start_time = datetime.now()
        
        try:
            console.print(f"\n[bold blue]🚀 开始测试: {test_name}[/bold blue]")
            console.print(f"[dim]命令: {command}[/dim]")
            console.print(f"[dim]持续时间: {duration}秒[/dim]")
            
            # 启动进程
            process = self.process_manager.start_process(command, f"{test_name}测试")
            
            # 等待测试完成
            success = self.process_manager.wait_for_process(process, duration)
            
            # 收集指标
            metrics_file = self.metrics_collector.collect_metrics(port, test_name)
            
            end_time = datetime.now()
            test_duration = (end_time - start_time).total_seconds()
            
            result = TestResult(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                duration=test_duration,
                port=port,
                metrics_file=metrics_file,
                success=success
            )
            
            if success:
                console.print(f"[green]✅ 测试 {test_name} 完成[/green]")
            else:
                console.print(f"[red]❌ 测试 {test_name} 失败[/red]")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            end_time = datetime.now()
            test_duration = (end_time - start_time).total_seconds()
            
            result = TestResult(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                duration=test_duration,
                port=port,
                metrics_file="",
                success=False,
                error_message=str(e)
            )
            
            console.print(f"[red]❌ 测试 {test_name} 异常: {e}[/red]")
            self.results.append(result)
            return result

class ReportGenerator:
    """报表生成器"""
    
    def __init__(self, config: TestConfig, results: List[TestResult]):
        self.config = config
        self.results = results
        self.metrics_collector = MetricsCollector()
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        console.print(f"[blue]📊 生成测试报告: {report_file}[/blue]")
        
        # 收集所有指标数据
        all_metrics = {}
        for result in self.results:
            if result.metrics_file and Path(result.metrics_file).exists():
                metrics = self.metrics_collector.parse_metrics(result.metrics_file)
                all_metrics[result.test_name] = metrics
        
        # 生成HTML报告
        html_content = self._generate_html_report(all_metrics)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]✅ 报告已生成: {report_file}[/green]")
        return report_file
    
    def _generate_html_report(self, all_metrics: Dict[str, Dict[str, Any]]) -> str:
        """生成HTML报告内容"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eMQTT-Bench 测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .test-result {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ border-left: 4px solid #28a745; }}
        .failed {{ border-left: 4px solid #dc3545; }}
        .metrics {{ background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 eMQTT-Bench 测试报告</h1>
        
        <div class="summary">
            <h2>📋 测试摘要</h2>
            <p><strong>测试时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>MQTT服务器:</strong> {self.config.host}:{self.config.port}</p>
            <p><strong>客户端数量:</strong> {self.config.client_count}</p>
            <p><strong>消息间隔:</strong> {self.config.msg_interval}ms</p>
            <p><strong>华为云认证:</strong> {"是" if self.config.use_huawei_auth else "否"}</p>
            {f'<p><strong>设备前缀:</strong> {self.config.device_prefix}</p>' if self.config.use_huawei_auth else ''}
        </div>
        
        <h2>📊 测试结果</h2>
"""
        
        # 添加测试结果
        for result in self.results:
            status_class = "success" if result.success else "failed"
            status_text = "✅ 成功" if result.success else "❌ 失败"
            
            html += f"""
        <div class="test-result {status_class}">
            <h3>{result.test_name.upper()} 测试 {status_text}</h3>
            <p><strong>端口:</strong> {result.port}</p>
            <p><strong>持续时间:</strong> {result.duration:.2f}秒</p>
            <p><strong>开始时间:</strong> {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>结束时间:</strong> {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>指标文件:</strong> {result.metrics_file}</p>
"""
            
            if result.error_message:
                html += f"<p><strong>错误信息:</strong> {result.error_message}</p>"
            
            # 添加指标数据
            if result.test_name in all_metrics:
                metrics = all_metrics[result.test_name]
                html += "<div class='metrics'><strong>关键指标:</strong><br>"
                for key, value in metrics.items():
                    if isinstance(value, dict):
                        html += f"{key}: {value}<br>"
                    else:
                        html += f"{key}: {value}<br>"
                html += "</div>"
            
            html += "</div>"
        
        html += """
        <h2>📈 指标说明</h2>
        <table>
            <tr><th>指标名称</th><th>说明</th></tr>
            <tr><td>connect_succ</td><td>成功连接数</td></tr>
            <tr><td>connect_fail</td><td>连接失败数</td></tr>
            <tr><td>connect_retried</td><td>重试连接数</td></tr>
            <tr><td>connection_timeout</td><td>连接超时数</td></tr>
            <tr><td>connection_refused</td><td>连接被拒绝数</td></tr>
            <tr><td>unreachable</td><td>不可达连接数</td></tr>
            <tr><td>mqtt_client_handshake_duration</td><td>MQTT握手延迟</td></tr>
            <tr><td>mqtt_client_connect_duration</td><td>连接建立延迟</td></tr>
        </table>
        
        <h2>🔧 使用方法</h2>
        <h3>查看实时指标</h3>
        <pre>
# 查看连接测试指标
curl http://localhost:9090/metrics

# 查看发布测试指标  
curl http://localhost:9091/metrics

# 查看订阅测试指标
curl http://localhost:9092/metrics

# 查看华为云测试指标
curl http://localhost:9093/metrics
        </pre>
        
        <h3>使用Python分析器</h3>
        <pre>
# 分析指标数据
python3 connection_test_analyzer.py metrics_*.txt

# 或使用URL直接分析
python3 connection_test_analyzer.py localhost:9090/metrics
        </pre>
        
        <div class="timestamp">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>由 eMQTT-Bench 集成测试管理器自动生成</p>
        </div>
    </div>
</body>
</html>
"""
        return html

class EMQTTTestManager:
    """eMQTT-Bench 集成测试管理器"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.process_manager = ProcessManager()
        self.metrics_collector = MetricsCollector()
        self.test_executor: Optional[TestExecutor] = None
        self.report_generator: Optional[ReportGenerator] = None
    
    def run(self):
        """运行测试管理器"""
        console.print(Panel.fit("[bold blue]🚀 eMQTT-Bench 集成测试管理器[/bold blue]"))
        
        # 加载或创建配置
        config = self._setup_config()
        
        # 创建测试执行器
        self.test_executor = TestExecutor(config, self.process_manager, self.metrics_collector)
        
        # 运行测试
        self._run_tests()
        
        # 生成报告
        self._generate_final_report()
        
        console.print("\n[green]✅ 所有测试完成！[/green]")
    
    def _setup_config(self) -> TestConfig:
        """设置配置"""
        # 尝试加载现有配置
        config = self.config_manager.load_config()
        
        if Confirm.ask("是否使用现有配置?"):
            self.config_manager._show_config_summary(config)
            if not Confirm.ask("确认使用此配置?"):
                config = self.config_manager.interactive_config()
        else:
            config = self.config_manager.interactive_config()
        
        return config
    
    def _run_tests(self):
        """运行测试"""
        console.print("\n[bold yellow]请选择要运行的测试:[/bold yellow]")
        
        tests = [
            ("连接测试", "connection"),
            ("发布测试", "publish"), 
            ("订阅测试", "subscribe"),
            ("自定义测试", "custom"),
            ("运行所有测试", "all")
        ]
        
        for i, (name, _) in enumerate(tests, 1):
            console.print(f"{i}) {name}")
        
        choice = IntPrompt.ask("请选择 (1-5)", choices=[str(i) for i in range(1, 6)])
        
        if choice == 1:
            self.test_executor.run_connection_test()
        elif choice == 2:
            self.test_executor.run_publish_test()
        elif choice == 3:
            self.test_executor.run_subscribe_test()
        elif choice == 4:
            self._run_custom_test()
        elif choice == 5:
            self._run_all_tests()
    
    def _run_custom_test(self):
        """运行自定义测试"""
        console.print("\n[bold yellow]自定义测试配置:[/bold yellow]")
        
        custom_config = {
            'clients': IntPrompt.ask("客户端数量", default=self.test_executor.config.client_count),
            'interval': IntPrompt.ask("消息间隔(ms)", default=self.test_executor.config.msg_interval),
            'topic': Prompt.ask("Topic", default="test/custom/%i"),
            'duration': IntPrompt.ask("持续时间(秒)", default=self.test_executor.config.test_duration)
        }
        
        self.test_executor.run_custom_test(custom_config)
    
    def _run_all_tests(self):
        """运行所有测试"""
        console.print("\n[bold blue]🔄 运行所有测试[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task1 = progress.add_task("连接测试...", total=100)
            self.test_executor.run_connection_test()
            progress.update(task1, completed=100)
            
            task2 = progress.add_task("发布测试...", total=100)
            self.test_executor.run_publish_test()
            progress.update(task2, completed=100)
            
            task3 = progress.add_task("订阅测试...", total=100)
            self.test_executor.run_subscribe_test()
            progress.update(task3, completed=100)
    
    def _generate_final_report(self):
        """生成最终报告"""
        if self.test_executor and self.test_executor.results:
            self.report_generator = ReportGenerator(
                self.test_executor.config, 
                self.test_executor.results
            )
            report_file = self.report_generator.generate_report()
            
            console.print(f"\n[green]📊 测试报告已生成: {report_file}[/green]")
            console.print(f"[blue]🌐 在浏览器中打开: file://{Path(report_file).absolute()}[/blue]")

@click.command()
@click.option('--config', '-c', help='配置文件路径')
@click.option('--interactive', '-i', is_flag=True, help='交互式配置')
def main(config: Optional[str], interactive: bool):
    """eMQTT-Bench 集成测试管理器"""
    try:
        manager = EMQTTTestManager()
        if config:
            manager.config_manager.config_file = Path(config)
        manager.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断，正在清理...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ 运行失败: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
