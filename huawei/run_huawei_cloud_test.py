#!/usr/bin/env python3
# coding=utf-8

import subprocess
import sys
import os
import argparse
import json
from payload_generator import generate_huawei_cloud_payload
from utils import get_client_id, get_password

def create_dynamic_payload_file():
    """
    创建一个动态payload文件，每次都包含不同的随机值
    """
    payload = generate_huawei_cloud_payload()
    filename = 'temp_huawei_payload.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(payload)
    
    return filename, len(payload)


def run_emqtt_bench_test(args):
    """
    运行emqtt-bench测试华为云
    """
    # 生成客户端ID和密码
    client_id = get_client_id(args.device_prefix + '-000000001')
    password = get_password(args.secret)
    
    # 华为云topic格式
    topic = f"$oc/devices/{args.device_prefix}-%i/sys/properties/report"
    
    # 创建动态payload文件
    payload_file, payload_size = create_dynamic_payload_file()
    
    # 构建emqtt_bench命令
    cmd = [
        '../emqtt_bench', 'pub',
        '-h', args.host,
        '-p', str(args.port),
        '-c', str(args.count),
        '-i', str(args.interval),
        '-I', str(args.msg_interval),
        '-t', topic,
        '-u', args.device_prefix + '-%i',  # 用户名使用设备ID模板
        '-P', password,
        '-q', str(args.qos),
        '--message', f'template://{payload_file}'
    ]
    
    # 添加SSL选项
    if args.ssl:
        cmd.append('--ssl')
        if args.cacertfile:
            cmd.extend(['--cacertfile', args.cacertfile])
    
    # 添加其他选项
    if args.clean:
        cmd.append('-C')
    
    if args.keepalive:
        cmd.extend(['-k', str(args.keepalive)])
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"Topic模板: {topic}")
    print(f"Payload大小: {payload_size} 字节")
    print(f"设备ID前缀: {args.device_prefix}")
    print(f"客户端数量: {args.count}")
    print(f"消息发送间隔: {args.msg_interval}ms")
    
    try:
        # 执行命令
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"执行失败: {e}")
        sys.exit(1)
    finally:
        # 清理临时文件
        if os.path.exists(payload_file):
            os.remove(payload_file)


def main():
    parser = argparse.ArgumentParser(description='使用emqtt-bench测试华为云IoT平台')
    
    # 基本参数
    parser.add_argument('--host', default='localhost', 
                        help='华为云MQTT服务器地址 (默认: localhost)')
    parser.add_argument('-p', '--port', type=int, default=1883,
                        help='MQTT端口 (默认: 1883)')
    parser.add_argument('-c', '--count', type=int, default=10,
                        help='客户端数量 (默认: 10)')
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help='连接间隔(ms) (默认: 10)')
    parser.add_argument('-I', '--msg-interval', type=int, default=1000,
                        help='消息发送间隔(ms) (默认: 1000)')
    
    # 设备相关参数
    parser.add_argument('--device-prefix', required=True,
                        help='设备ID前缀，例如: Speaker')
    parser.add_argument('--secret', default='12345678',
                        help='设备密钥 (默认: 12345678)')
    
    # MQTT参数
    parser.add_argument('-q', '--qos', type=int, default=1, choices=[0, 1, 2],
                        help='QoS级别 (默认: 1)')
    parser.add_argument('-C', '--clean', action='store_true',
                        help='Clean session')
    parser.add_argument('-k', '--keepalive', type=int, default=300,
                        help='Keep alive时间(秒) (默认: 300)')
    
    # SSL/TLS参数
    parser.add_argument('--ssl', action='store_true',
                        help='使用SSL/TLS连接')
    parser.add_argument('--cacertfile', 
                        help='CA证书文件路径')
    
    args = parser.parse_args()
    
    # 运行测试
    run_emqtt_bench_test(args)


if __name__ == "__main__":
    main()
