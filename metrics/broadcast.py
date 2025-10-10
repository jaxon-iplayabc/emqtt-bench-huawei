# coding: utf-8
"""
华为云IoTDA广播消息发送脚本
支持循环发送广播消息到指定主题
作者: Jaxon
日期: 2024-12-19
"""
import json
import os
import time
import argparse
import signal
import sys
from datetime import datetime

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.auth.credentials import DerivedCredentials
from huaweicloudsdkcore.region.region import Region as coreRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkiotda.v5 import *
import base64

class BroadcastSender:
    """华为云广播消息发送器"""
    
    def __init__(self, ak: str, sk: str, endpoint: str, region: str = "cn-north-4"):
        """
        初始化广播发送器
        
        Args:
            ak: 访问密钥ID
            sk: 访问密钥Secret
            endpoint: 华为云IoTDA端点
            region: 区域ID
        """
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.region = region
        self.client = None
        self.running = True
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n[INFO] 收到退出信号 {signum}，正在停止广播发送...")
        self.running = False
    
    def _create_client(self):
        """创建华为云客户端"""
        try:
            credentials = BasicCredentials(self.ak, self.sk).with_derived_predicate(
                DerivedCredentials.get_default_derived_predicate()
            )
            
            self.client = IoTDAClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(coreRegion(id=self.region, endpoint=self.endpoint)) \
                .build()
            
            print(f"[INFO] 华为云客户端创建成功，区域: {self.region}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建华为云客户端失败: {e}")
            return False
    
    def send_broadcast(self, topic: str, message: dict) -> bool:
        """
        发送广播消息
        
        Args:
            topic: 广播主题
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        if not self.client:
            print("[ERROR] 客户端未初始化")
            return False
        
        try:
            # 编码消息
            message_json = json.dumps(message, ensure_ascii=False)
            message_b64 = base64.b64encode(message_json.encode('utf-8')).decode('utf-8')
            
            # 创建广播请求
            request = BroadcastMessageRequest()
            request.body = DeviceBroadcastRequest(
                message=message_b64,
                topic_full_name=topic
            )
            
            # 发送广播
            response = self.client.broadcast_message(request)
            print(f"[SUCCESS] 广播发送成功: {topic}")
            print(f"[INFO] 响应: {response}")
            return True
            
        except exceptions.ClientRequestException as e:
            print(f"[ERROR] 广播发送失败:")
            print(f"  状态码: {e.status_code}")
            print(f"  请求ID: {e.request_id}")
            print(f"  错误码: {e.error_code}")
            print(f"  错误信息: {e.error_msg}")
            return False
        except Exception as e:
            print(f"[ERROR] 广播发送异常: {e}")
            return False
    
    def start_loop(self, topic: str, interval: int = 5, duration: int = None):
        """
        开始循环发送广播
        
        Args:
            topic: 广播主题
            interval: 发送间隔（秒）
            duration: 运行持续时间（秒），None表示无限运行
        """
        if not self._create_client():
            return
        
        print(f"[INFO] 开始循环发送广播")
        print(f"[INFO] 主题: {topic}")
        print(f"[INFO] 间隔: {interval}秒")
        print(f"[INFO] 持续时间: {'无限' if duration is None else f'{duration}秒'}")
        print(f"[INFO] 按 Ctrl+C 停止发送")
        
        start_time = time.time()
        message_count = 0
        
        try:
            while self.running:
                # 检查是否超时
                if duration and (time.time() - start_time) >= duration:
                    print(f"[INFO] 达到运行时间限制 {duration}秒，停止发送")
                    break
                
                # 创建消息
                message = {
                    'timestamp': time.time(),
                    'datetime': datetime.now().isoformat(),
                    'message_id': message_count + 1,
                    'content': f'广播消息 #{message_count + 1}',
                    'source': 'broadcast_sender'
                }
                
                # 发送广播
                success = self.send_broadcast(topic, message)
                if success:
                    message_count += 1
                
                # 等待下次发送
                if self.running:
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            print(f"\n[INFO] 用户中断，停止发送")
        finally:
            print(f"[INFO] 广播发送结束，共发送 {message_count} 条消息")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='华为云IoTDA广播消息发送工具')
    parser.add_argument('--ak', help='华为云访问密钥ID')
    parser.add_argument('--sk', help='华为云访问密钥Secret')
    parser.add_argument('--endpoint', help='华为云IoTDA端点')
    parser.add_argument('--region', default='cn-north-4', help='华为云区域ID (默认: cn-north-4)')
    parser.add_argument('--topic', default='$oc/broadcast/test', help='广播主题 (默认: $oc/broadcast/test)')
    parser.add_argument('--interval', type=int, default=5, help='发送间隔秒数 (默认: 5)')
    parser.add_argument('--duration', type=int, help='运行持续时间秒数 (默认: 无限运行)')
    parser.add_argument('--once', action='store_true', help='只发送一次广播')
    
    args = parser.parse_args()
    
    # 检查必需参数
    if not args.ak or not args.sk or not args.endpoint:
        print("[ERROR] 缺少必需参数: --ak, --sk, --endpoint")
        print("[INFO] 请提供华为云访问密钥和端点信息")
        sys.exit(1)
    
    # 创建广播发送器
    sender = BroadcastSender(args.ak, args.sk, args.endpoint, args.region)
    
    if args.once:
        # 单次发送
        print("[INFO] 单次发送模式")
        message = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'content': '单次广播消息',
            'source': 'broadcast_sender'
        }
        success = sender.send_broadcast(args.topic, message)
        sys.exit(0 if success else 1)
    else:
        # 循环发送
        sender.start_loop(args.topic, args.interval, args.duration)

if __name__ == "__main__":
    main()