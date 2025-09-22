#!/bin/bash
# 比较 Python 和 Erlang 的时间戳生成

echo "=== 时间戳生成对比 ==="
echo ""

echo "1. Python 时间戳："
python3 -c "
import sys
sys.path.append('./huawei')
from utils import get_timeStamp
print(f'Python 时间戳: {get_timeStamp()}')
"

echo ""
echo "2. Erlang 时间戳："
cat > test_erlang_timestamp.erl << 'EOF'
#!/usr/bin/env escript

main([]) ->
    % 模拟 huawei_auth:get_timestamp/0 的实现
    LocalTime = calendar:universal_time_to_local_time(calendar:universal_time()),
    Timestamp = format_timestamp(LocalTime),
    io:format("Erlang 时间戳: ~s~n", [Timestamp]).

format_timestamp({{Year, Month, Day}, {Hour, _Min, _Sec}}) ->
    lists:flatten(io_lib:format("~4..0B~2..0B~2..0B~2..0B", [Year, Month, Day, Hour])).
EOF

chmod +x test_erlang_timestamp.erl
escript test_erlang_timestamp.erl

echo ""
echo "3. 系统时间信息："
echo "本地时间: $(date '+%Y%m%d%H')"
echo "UTC 时间: $(date -u '+%Y%m%d%H')"

# 清理
rm -f test_erlang_timestamp.erl
