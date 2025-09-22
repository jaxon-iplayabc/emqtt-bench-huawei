#!/bin/bash
# 调试华为云认证信息生成

echo "=== 华为云认证信息调试 ==="
echo ""

DEVICE_ID="Speaker-000000001"
SECRET="12345678"

echo "1. Python 生成的认证信息："
echo "=========================="
python3 -c "
from huawei.utils import get_client_id, get_password
device_id = '$DEVICE_ID'
secret = '$SECRET'
client_id = get_client_id(device_id)
password = get_password(secret)
print(f'ClientID: {client_id}')
print(f'Username: {device_id}')
print(f'Password: {password}')
"

echo ""
echo "2. Erlang 生成的认证信息："
echo "=========================="
# 创建一个简单的 Erlang 脚本来测试
cat > test_erlang_auth.erl << 'EOF'
#!/usr/bin/env escript
%%! -pa _build/default/lib/*/ebin

main([]) ->
    DeviceId = <<"Speaker-000000001">>,
    Secret = <<"12345678">>,
    
    ClientId = huawei_auth:get_client_id(DeviceId),
    Password = huawei_auth:get_password(Secret),
    
    io:format("ClientID: ~s~n", [ClientId]),
    io:format("Username: ~s~n", [DeviceId]),
    io:format("Password: ~s~n", [Password]).
EOF

chmod +x test_erlang_auth.erl
escript test_erlang_auth.erl

echo ""
echo "3. 使用调试模式运行 emqtt_bench："
echo "=================================="
echo "命令："
echo "./emqtt_bench pub \\"
echo "    -h 016bc9ac7b.st1.iotda-device.cn-north-4.myhuaweicloud.com \\"
echo "    -p 1883 \\"
echo "    -c 1 \\"
echo "    -t '\$oc/devices/%d/sys/properties/report' \\"
echo "    --device-id '$DEVICE_ID' \\"
echo "    -P 'huawei:$SECRET' \\"
echo "    --huawei-auth \\"
echo "    -s 100 \\"
echo "    --limit 1 \\"
echo "    --log_to console"
echo ""

# 清理
rm -f test_erlang_auth.erl
