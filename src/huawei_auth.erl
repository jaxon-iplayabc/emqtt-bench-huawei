%%--------------------------------------------------------------------
%% Copyright (c) 2024 EMQ Technologies Co., Ltd. All Rights Reserved.
%%
%% Licensed under the Apache License, Version 2.0 (the "License");
%% you may not use this file except in compliance with the License.
%% You may obtain a copy of the License at
%%
%%     http://www.apache.org/licenses/LICENSE-2.0
%%
%% Unless required by applicable law or agreed to in writing, software
%% distributed under the License is distributed on an "AS IS" BASIS,
%% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%% See the License for the specific language governing permissions and
%% limitations under the License.
%%--------------------------------------------------------------------

-module(huawei_auth).

-export([get_password/1, get_password/2]).
-export([get_client_id/1, get_client_id/2]).
-export([get_timestamp/0]).

%% @doc 生成华为云设备密码
%% 使用 HMAC-SHA256 算法，以时间戳为密钥对 secret 进行加密
-spec get_password(binary() | string()) -> binary().
get_password(Secret) when is_list(Secret) ->
    get_password(list_to_binary(Secret));
get_password(Secret) when is_binary(Secret) ->
    Timestamp = get_timestamp(),
    get_password(Secret, Timestamp).

-spec get_password(binary() | string(), binary() | string()) -> binary().
get_password(Secret, Timestamp) when is_list(Secret) ->
    get_password(list_to_binary(Secret), Timestamp);
get_password(Secret, Timestamp) when is_list(Timestamp) ->
    get_password(Secret, list_to_binary(Timestamp));
get_password(Secret, Timestamp) when is_binary(Secret), is_binary(Timestamp) ->
    %% 使用时间戳作为密钥，对 secret 进行 HMAC-SHA256 加密
    Mac = crypto:mac(hmac, sha256, Timestamp, Secret),
    %% 转换为十六进制字符串
    bin_to_hex(Mac).

%% @doc 生成华为云设备 ClientID
%% 格式：设备ID_0_密码签名类型_时间戳
-spec get_client_id(binary() | string()) -> binary().
get_client_id(DeviceId) ->
    get_client_id(DeviceId, 0).

-spec get_client_id(binary() | string(), integer()) -> binary().
get_client_id(DeviceId, PswSigType) when is_list(DeviceId) ->
    get_client_id(list_to_binary(DeviceId), PswSigType);
get_client_id(DeviceId, PswSigType) when is_binary(DeviceId), is_integer(PswSigType) ->
    Timestamp = get_timestamp(),
    %% 格式：设备ID_0_密码签名类型_时间戳
    iolist_to_binary([DeviceId, "_0_", integer_to_binary(PswSigType), "_", Timestamp]).

%% @doc 获取华为云格式的时间戳
%% 格式：YYYYMMDDHH（本地时间）
-spec get_timestamp() -> binary().
get_timestamp() ->
    {{Year, Month, Day}, {Hour, _, _}} = calendar:local_time(),
    iolist_to_binary(
        io_lib:format("~4..0B~2..0B~2..0B~2..0B", [Year, Month, Day, Hour])
    ).

%% @doc 将二进制数据转换为十六进制字符串
-spec bin_to_hex(binary()) -> binary().
bin_to_hex(Bin) ->
    list_to_binary([io_lib:format("~2.16.0b", [B]) || <<B>> <= Bin]).


%%--------------------------------------------------------------------
%% Tests
%%--------------------------------------------------------------------

-ifdef(TEST).
-include_lib("eunit/include/eunit.hrl").

get_timestamp_test() ->
    %% 时间戳应该是10位数字
    Timestamp = get_timestamp(),
    ?assertEqual(10, byte_size(Timestamp)),
    %% 应该都是数字
    ?assert(is_valid_timestamp(Timestamp)).

is_valid_timestamp(<<Y:4/binary, M:2/binary, D:2/binary, H:2/binary>>) ->
    lists:all(fun(B) -> B >= $0 andalso B =< $9 end, 
              binary_to_list(<<Y/binary, M/binary, D/binary, H/binary>>)).

get_password_test() ->
    %% 测试密码生成
    Secret = <<"12345678">>,
    Password = get_password(Secret),
    %% 密码应该是64个字符（32字节的十六进制表示）
    ?assertEqual(64, byte_size(Password)),
    %% 应该都是十六进制字符
    ?assert(is_hex_string(Password)).

get_password_with_timestamp_test() ->
    Secret = <<"12345678">>,
    Timestamp = <<"2024111812">>,
    %% 使用固定时间戳，结果应该是确定的
    Password = get_password(Secret, Timestamp),
    %% 验证生成的密码长度
    ?assertEqual(64, byte_size(Password)).

get_client_id_test() ->
    DeviceId = <<"Speaker-000000001">>,
    ClientId = get_client_id(DeviceId),
    %% ClientID 格式应该包含 _0_0_ 或 _0_1_
    ?assertMatch(<<_:18/binary, "_0_", _/binary>>, ClientId).

is_hex_string(Bin) ->
    lists:all(fun(C) -> 
        (C >= $0 andalso C =< $9) orelse 
        (C >= $a andalso C =< $f) orelse 
        (C >= $A andalso C =< $F)
    end, binary_to_list(Bin)).

-endif.
