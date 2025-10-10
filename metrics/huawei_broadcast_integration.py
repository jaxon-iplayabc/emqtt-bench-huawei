# coding: utf-8
"""
华为云广播集成测试脚本
同时运行广播发送和订阅测试，验证广播消息的端到端传输
作者: Jaxon
日期: 2024-12-19
"""
import os
import sys
import time
import argparse
import signal
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class HuaweiBroadcastIntegration:
    """华为云广播集成测试器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化集成测试器
        
        Args:
            config: 测试配置
        """
        self.config = config
        self.running = True
        self.processes = {}
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n[INFO] 收到退出信号 {signum}，正在停止所有进程...")
        self.running = False
        self._cleanup_processes()
        sys.exit(0)
    
    def _cleanup_processes(self):
        """清理所有进程"""
        print("[INFO] 正在清理进程...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"[INFO] 终止进程: {name}")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass
        
        self.processes.clear()
        print("[INFO] 进程清理完成")
    
    def _start_broadcast_sender(self) -> bool:
        """启动广播发送器"""
        try:
            # 构建命令
            cmd = [
                sys.executable, "broadcast.py",
                "--ak", self.config["huawei_ak"],
                "--sk", self.config["huawei_sk"],
                "--endpoint", self.config["huawei_endpoint"],
                "--region", self.config.get("huawei_region", "cn-north-4"),
                "--topic", self.config.get("broadcast_topic", "$oc/broadcast/test"),
                "--interval", str(self.config.get("broadcast_interval", 5)),
                "--duration", str(self.config.get("test_duration", 60))
            ]
            
            print(f"[INFO] 启动广播发送器: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes["broadcast_sender"] = process
            
            # 启动输出监控线程
            threading.Thread(
                target=self._monitor_process_output,
                args=("broadcast_sender", process),
                daemon=True
            ).start()
            
            print("[SUCCESS] 广播发送器已启动")
            return True
            
        except Exception as e:
            print(f"[ERROR] 启动广播发送器失败: {e}")
            return False
    
    def _start_subscribe_test(self) -> bool:
        """启动订阅测试"""
        try:
            # 构建命令
            cmd = [
                sys.executable, "huawei_subscribe_test.py",
                "--host", self.config["mqtt_host"],
                "--port", str(self.config["mqtt_port"]),
                "--device-prefix", self.config["device_prefix"],
                "--device-secret", self.config["device_secret"],
                "--duration", str(self.config.get("test_duration", 60))
            ]
            
            print(f"[INFO] 启动订阅测试: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes["subscribe_test"] = process
            
            # 启动输出监控线程
            threading.Thread(
                target=self._monitor_process_output,
                args=("subscribe_test", process),
                daemon=True
            ).start()
            
            print("[SUCCESS] 订阅测试已启动")
            return True
            
        except Exception as e:
            print(f"[ERROR] 启动订阅测试失败: {e}")
            return False
    
    def _monitor_process_output(self, name: str, process: subprocess.Popen):
        """监控进程输出"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"[{name.upper()}] {line.strip()}")
        except:
            pass
    
    def _wait_for_processes(self, timeout: int = None):
        """等待所有进程完成"""
        if timeout is None:
            timeout = self.config.get("test_duration", 60) + 10
        
        print(f"[INFO] 等待进程完成，超时时间: {timeout}秒")
        
        start_time = time.time()
        while self.running and (time.time() - start_time) < timeout:
            # 检查进程状态
            all_finished = True
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    all_finished = False
                    break
            
            if all_finished:
                print("[INFO] 所有进程已完成")
                break
            
            time.sleep(1)
        
        if (time.time() - start_time) >= timeout:
            print(f"[WARNING] 等待超时 ({timeout}秒)，强制停止")
            self._cleanup_processes()
    
    def run_integration_test(self):
        """运行集成测试"""
        print("=" * 60)
        print("🚀 华为云广播集成测试")
        print("=" * 60)
        
        # 显示配置信息
        print(f"[CONFIG] 华为云端点: {self.config['huawei_endpoint']}")
        print(f"[CONFIG] MQTT服务器: {self.config['mqtt_host']}:{self.config['mqtt_port']}")
        print(f"[CONFIG] 设备前缀: {self.config['device_prefix']}")
        print(f"[CONFIG] 广播主题: {self.config.get('broadcast_topic', '$oc/broadcast/test')}")
        print(f"[CONFIG] 广播间隔: {self.config.get('broadcast_interval', 5)}秒")
        print(f"[CONFIG] 测试时长: {self.config.get('test_duration', 60)}秒")
        print("=" * 60)
        
        try:
            # 启动广播发送器
            if not self._start_broadcast_sender():
                print("[ERROR] 无法启动广播发送器，测试终止")
                return False
            
            # 等待一下让广播发送器初始化
            time.sleep(2)
            
            # 启动订阅测试
            if not self._start_subscribe_test():
                print("[ERROR] 无法启动订阅测试，测试终止")
                self._cleanup_processes()
                return False
            
            # 等待所有进程完成
            self._wait_for_processes()
            
            print("\n" + "=" * 60)
            print("✅ 集成测试完成")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 集成测试异常: {e}")
            return False
        finally:
            self._cleanup_processes()

def load_config_from_file(config_file: str) -> Dict[str, Any]:
    """从配置文件加载配置"""
    import json
    
    if not os.path.exists(config_file):
        print(f"[ERROR] 配置文件不存在: {config_file}")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"[INFO] 已加载配置文件: {config_file}")
        return config
    except Exception as e:
        print(f"[ERROR] 加载配置文件失败: {e}")
        return {}

def create_default_config() -> Dict[str, Any]:
    """创建默认配置"""
    return {
        "mqtt_host": "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com",
        "mqtt_port": 1883,
        "device_prefix": "speaker",
        "device_secret": "12345678",
        "huawei_ak": os.environ.get("CLOUD_SDK_AK", ""),
        "huawei_sk": os.environ.get("CLOUD_SDK_SK", ""),
        "huawei_endpoint": "<YOUR ENDPOINT>",
        "huawei_region": "cn-north-4",
        "broadcast_topic": "$oc/broadcast/test",
        "broadcast_interval": 5,
        "test_duration": 60
    }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='华为云广播集成测试工具')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--mqtt-host', help='MQTT服务器地址')
    parser.add_argument('--mqtt-port', type=int, help='MQTT端口')
    parser.add_argument('--device-prefix', help='设备前缀')
    parser.add_argument('--device-secret', help='设备密钥')
    parser.add_argument('--huawei-ak', help='华为云访问密钥ID')
    parser.add_argument('--huawei-sk', help='华为云访问密钥Secret')
    parser.add_argument('--huawei-endpoint', help='华为云IoTDA端点')
    parser.add_argument('--broadcast-topic', default='$oc/broadcast/test', help='广播主题')
    parser.add_argument('--broadcast-interval', type=int, default=5, help='广播发送间隔(秒)')
    parser.add_argument('--test-duration', type=int, default=60, help='测试持续时间(秒)')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    
    if args.config:
        config = load_config_from_file(args.config)
    
    # 使用默认配置填充缺失项
    default_config = create_default_config()
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    # 命令行参数覆盖配置文件
    if args.mqtt_host:
        config["mqtt_host"] = args.mqtt_host
    if args.mqtt_port:
        config["mqtt_port"] = args.mqtt_port
    if args.device_prefix:
        config["device_prefix"] = args.device_prefix
    if args.device_secret:
        config["device_secret"] = args.device_secret
    if args.huawei_ak:
        config["huawei_ak"] = args.huawei_ak
    if args.huawei_sk:
        config["huawei_sk"] = args.huawei_sk
    if args.huawei_endpoint:
        config["huawei_endpoint"] = args.huawei_endpoint
    if args.broadcast_topic:
        config["broadcast_topic"] = args.broadcast_topic
    if args.broadcast_interval:
        config["broadcast_interval"] = args.broadcast_interval
    if args.test_duration:
        config["test_duration"] = args.test_duration
    
    # 验证必需参数
    required_params = ["mqtt_host", "device_prefix", "device_secret", "huawei_ak", "huawei_sk", "huawei_endpoint"]
    missing_params = [param for param in required_params if not config.get(param) or config[param] == "<YOUR ENDPOINT>"]
    
    if missing_params:
        print(f"[ERROR] 缺少必需参数: {', '.join(missing_params)}")
        print("[INFO] 请通过命令行参数或配置文件提供这些参数")
        sys.exit(1)
    
    # 创建并运行集成测试
    tester = HuaweiBroadcastIntegration(config)
    success = tester.run_integration_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
