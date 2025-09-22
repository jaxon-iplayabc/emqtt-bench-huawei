#!/usr/bin/env escript
%%! -pa _build/default/lib/*/ebin

-mode(compile).

main([]) ->
    io:format("=== 华为云认证测试 ===~n~n"),
    
    %% 测试时间戳生成
    Timestamp = huawei_auth:get_timestamp(),
    io:format("当前时间戳: ~s~n", [Timestamp]),
    
    %% 测试密码生成
    Secret = <<"12345678">>,
    Password = huawei_auth:get_password(Secret),
    io:format("生成的密码: ~s~n", [Password]),
    
    %% 使用固定时间戳测试（方便验证）
    TestTimestamp = <<"2024111812">>,
    TestPassword = huawei_auth:get_password(Secret, TestTimestamp),
    io:format("固定时间戳密码: ~s~n", [TestPassword]),
    
    %% 测试 ClientID 生成
    DeviceId = <<"Speaker-000000001">>,
    ClientId = huawei_auth:get_client_id(DeviceId),
    io:format("生成的 ClientID: ~s~n", [ClientId]),
    
    %% 测试带密码签名类型的 ClientID
    ClientId1 = huawei_auth:get_client_id(DeviceId, 1),
    io:format("签名类型1的 ClientID: ~s~n", [ClientId1]),
    
    io:format("~n测试完成！~n").
