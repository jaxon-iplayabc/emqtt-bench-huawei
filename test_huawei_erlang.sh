#!/bin/bash
# 测试华为云 Erlang 认证功能

echo "=== 测试华为云 Erlang 认证功能 ==="
echo ""

# 生成密码（使用固定 secret）
SECRET="12345678"
DEVICE_ID="Speaker-000000001"

# 使用 emqtt_bench 的华为认证功能
echo "1. 测试密码生成（使用 --password huawei:$SECRET）："
./emqtt_bench pub \
    -h localhost \
    -p 1883 \
    -c 1 \
    -I 1000 \
    -t '$oc/devices/Speaker-%i/sys/properties/report' \
    -u "$DEVICE_ID" \
    -P "huawei:$SECRET" \
    --huawei-auth \
    -s 100 \
    --limit 1 \
    --log_to null &

PID=$!
sleep 2
kill $PID 2>/dev/null

echo ""
echo "2. 使用 escript 直接测试模块："
cat > test_auth.erl << 'EOF'
#!/usr/bin/env escript
%%! -pa _build/default/lib/*/ebin

main([]) ->
    try
        io:format("测试华为认证模块...~n"),
        
        %% 测试时间戳
        Timestamp = huawei_auth:get_timestamp(),
        io:format("时间戳: ~s~n", [Timestamp]),
        
        %% 测试密码生成
        Secret = <<"12345678">>,
        Password = huawei_auth:get_password(Secret),
        io:format("生成的密码: ~s~n", [Password]),
        
        %% 测试 ClientID
        DeviceId = <<"Speaker-000000001">>,
        ClientId = huawei_auth:get_client_id(DeviceId),
        io:format("生成的 ClientID: ~s~n", [ClientId]),
        
        io:format("~n测试成功！~n")
    catch
        Error:Reason ->
            io:format("错误: ~p:~p~n", [Error, Reason]),
            io:format("栈跟踪: ~p~n", [erlang:get_stacktrace()])
    end.
EOF

escript test_auth.erl

# 清理
rm -f test_auth.erl

echo ""
echo "3. 显示生成的认证信息示例："
echo "   设备ID: $DEVICE_ID"
echo "   密钥: $SECRET"
echo "   密码格式: --password \"huawei:$SECRET\""
echo "   启用华为认证: --huawei-auth"
