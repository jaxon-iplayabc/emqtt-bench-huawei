#!/usr/bin/env escript
%%! -pa _build/default/lib/*/ebin

main([]) ->
    %% 测试时间戳生成
    LocalTime = calendar:local_time(),
    {{Year, Month, Day}, {Hour, _Min, _Sec}} = LocalTime,
    Timestamp = iolist_to_binary(
        io_lib:format("~4..0B~2..0B~2..0B~2..0B", [Year, Month, Day, Hour])
    ),
    
    io:format("本地时间: ~p~n", [LocalTime]),
    io:format("时间戳: ~s~n", [Timestamp]),
    
    %% 测试认证信息生成
    DeviceId = <<"Speaker-000000001">>,
    Secret = <<"12345678">>,
    
    ClientId = huawei_auth:get_client_id(DeviceId),
    Password = huawei_auth:get_password(Secret),
    
    io:format("~n设备ID: ~s~n", [DeviceId]),
    io:format("ClientID: ~s~n", [ClientId]),
    io:format("Password: ~s~n", [Password]).
