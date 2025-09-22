#!/bin/bash
# 调试认证信息生成

echo "=== 调试华为云认证信息 ==="
echo ""

DEVICE_ID="Speaker-000000001"
SECRET="12345678"

echo "1. Python 生成的认证信息（作为参考）："
echo "====================================="
python3 -c "
import sys
sys.path.append('./huawei')
from utils import get_client_id, get_password, get_timeStamp
device_id = '$DEVICE_ID'
secret = '$SECRET'
timestamp = get_timeStamp()
client_id = get_client_id(device_id)
password = get_password(secret)
print(f'时间戳: {timestamp}')
print(f'ClientID: {client_id}')
print(f'Username: {device_id}')
print(f'Password: {password}')
"

echo ""
echo "2. 使用 emqtt_bench 调试模式："
echo "=============================="
echo "运行命令："
echo "./emqtt_bench pub \\"
echo "    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \\"
echo "    -p 1883 \\"
echo "    -c 1 \\"
echo "    -t '\$oc/devices/%d/sys/properties/report' \\"
echo "    --device-id '$DEVICE_ID' \\"
echo "    -P 'huawei:$SECRET' \\"
echo "    --huawei-auth \\"
echo "    --limit 1"

echo ""
echo "3. 测试设备是否已注册："
echo "======================="
echo "请确认设备 '$DEVICE_ID' 已在华为云平台注册"
echo "设备密钥是否为 '$SECRET'"

echo ""
echo "4. 使用原始密码测试（不使用 --huawei-auth）："
echo "=========================================="
# 先获取 Python 生成的密码
PASSWORD=$(python3 -c "
import sys
sys.path.append('./huawei')
from utils import get_password
print(get_password('$SECRET'))
")
CLIENT_ID=$(python3 -c "
import sys
sys.path.append('./huawei')
from utils import get_client_id
print(get_client_id('$DEVICE_ID'))
")

echo "生成的密码: $PASSWORD"
echo "生成的ClientID: $CLIENT_ID"
echo ""
echo "测试命令："
echo "./emqtt_bench pub \\"
echo "    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \\"
echo "    -p 1883 \\"
echo "    -c 1 \\"
echo "    -t '\$oc/devices/$DEVICE_ID/sys/properties/report' \\"
echo "    -u '$DEVICE_ID' \\"
echo "    -P '$PASSWORD' \\"
echo "    -C '$CLIENT_ID' \\"
echo "    --limit 1"
