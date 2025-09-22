#!/usr/bin/env escript
%%! -pa _build/default/lib/*/ebin

main([]) ->
    %% 测试不同序号
    test_device_id(1, "Speaker"),
    test_device_id(10, "Speaker"),
    test_device_id(100, "Speaker"),
    test_device_id(1, undefined).

test_device_id(N, Prefix) ->
    DeviceId = case Prefix of
        undefined ->
            iolist_to_binary(io_lib:format("device-~9..0B", [N]));
        P ->
            iolist_to_binary(io_lib:format("~s-~9..0B", [P, N]))
    end,
    io:format("N=~p, Prefix=~p -> DeviceId=~s~n", [N, Prefix, DeviceId]).
