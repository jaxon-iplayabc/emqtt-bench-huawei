#!/bin/bash
# 华为云认证问题诊断脚本

echo "=== 华为云 IoT 认证诊断 ==="
echo ""

# 配置
HOST="016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
PORT="1883"
DEVICE_ID="Speaker-000000001"
SECRET="12345678"

echo "1. 检查系统时间"
echo "==============="
echo "当前系统时间: $(date)"
echo "UTC 时间: $(date -u)"
echo "时间戳格式: $(date +%Y%m%d%H)"
echo ""

echo "2. 检查网络连接"
echo "==============="
echo "Ping 华为云服务器..."
ping -c 3 $HOST || echo "警告: 无法 ping 通服务器，但可能是防火墙限制"
echo ""

echo "3. 测试不同的认证方式"
echo "===================="

echo "方式1: 使用 Python 脚本直接连接"
echo "------------------------------"
cat > test_mqtt_connection.py << 'EOF'
import sys
import time
import socket
sys.path.append('./huawei')
from utils import get_client_id, get_password

device_id = "Speaker-000000001"
secret = "12345678"
host = "016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com"
port = 1883

# 生成认证信息
client_id = get_client_id(device_id)
password = get_password(secret)

print(f"设备ID: {device_id}")
print(f"ClientID: {client_id}")
print(f"密码: {password}")
print(f"密码长度: {len(password)}")

# 测试 TCP 连接
print(f"\n测试 TCP 连接到 {host}:{port}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    if result == 0:
        print("✓ TCP 连接成功")
    else:
        print(f"✗ TCP 连接失败: {result}")
    sock.close()
except Exception as e:
    print(f"✗ 连接异常: {e}")

# 使用 paho-mqtt 测试
try:
    from paho.mqtt import client as mqtt
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✓ MQTT 连接成功！")
        else:
            print(f"✗ MQTT 连接失败，错误码: {rc}")
            errors = {
                1: "协议版本错误",
                2: "客户端标识符无效", 
                3: "服务器不可用",
                4: "用户名或密码错误",
                5: "未授权"
            }
            print(f"  错误说明: {errors.get(rc, '未知错误')}")
    
    print("\n使用 paho-mqtt 测试 MQTT 连接...")
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.username_pw_set(device_id, password)
    
    try:
        client.connect(host, port, keepalive=60)
        client.loop_start()
        time.sleep(3)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"✗ 连接异常: {e}")
        
except ImportError:
    print("未安装 paho-mqtt，跳过此测试")
EOF

python3 test_mqtt_connection.py

echo ""
echo "4. 可能的问题和解决方案"
echo "======================"
echo "如果认证失败，请检查："
echo "1. 设备是否已在华为云 IoT 平台注册"
echo "2. 设备ID是否完全匹配: $DEVICE_ID"
echo "3. 设备密钥是否正确: $SECRET"
echo "4. 系统时间是否准确（误差不超过1小时）"
echo "5. 设备是否已被禁用或删除"
echo ""
echo "如需重新注册设备："
echo "- 登录华为云 IoT 控制台"
echo "- 进入产品 > 设备管理"
echo "- 确认或创建设备 '$DEVICE_ID'"
echo "- 设置密钥为 '$SECRET'"

# 清理
rm -f test_mqtt_connection.py
