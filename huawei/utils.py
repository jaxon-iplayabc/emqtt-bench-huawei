import time
import hmac
from hashlib import sha256
def get_client_id(device_id=None, psw_sig_type=0):
    """
    一机一密的设备clientId由4个部分组成：设备ID、设备身份标识类型、密码签名类型、时间戳。通过下划线“_”分隔。
    :param deviceId: 注册时的设备ID，可在配置文件设置，即config.py中的deviceId
    :param device_id_type: 设备身份标识类型固定值为0
    :param Psw_sig_type:  密码签名类型：长度1字节，当前支持2种类型：
                          “0”代表HMACSHA256不校验时间戳。
                          “1”代表HMACSHA256校验时间戳。
    :param time_stamp: 时间戳
    """
    if not isinstance(device_id, str):
        raise ValueError('device_id should be a string type')

    return device_id + '_0_' + str(psw_sig_type) + '_' + get_timeStamp()

def get_timeStamp():
    """
    :return:时间戳：为设备连接平台时的UTC时间，格式为YYYYMMDDHH，如UTC 时间2020/04/26 19:56:20 则应表示为2020032619。
    """
    return time.strftime('%Y%m%d%H', time.localtime(time.time()))



def get_password(secret):
    """
    对 secret 进行加密
    :param secret: 返回的password的值为使用“HMACSHA256”算法以时间戳为秘钥，对secret进行加密后的值。secret为注册设备时平台返回的secret。
    """
    secret_key = get_timeStamp().encode('utf-8')  # 秘钥
    secret = secret.encode('utf-8')  # 加密数据
    password = hmac.new(secret_key, secret, digestmod=sha256).hexdigest()
    return password
