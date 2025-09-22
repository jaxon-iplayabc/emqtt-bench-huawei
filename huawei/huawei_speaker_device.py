# coding=utf-8

from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
from paho.mqtt import client as mqtt
import ssl
import socket
from datetime import datetime
from time import time, sleep
from urllib import parse
from base64 import b64encode, b64decode
from hmac import HMAC
from hashlib import sha256

from utils import get_client_id, get_password

# ssl._create_default_https_context = ssl._create_unverified_context
mqtt_server = '<MQTT-SERVER>'





device_id = '<DEVICE-PREFIX>-000000001'


def on_connect(client, userdata, flags, rc):
    print("Device connected with result code: " + str(rc))


def on_disconnect(client, userdata, rc):
    print("Device disconnected with result code: " + str(rc))


def on_publish(client, userdata, mid):
    print("Device sent message")

client_id = get_client_id(device_id)
client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
pwd = get_password('12345678')
client.username_pw_set(device_id, pwd)

# client.tls_set(ca_certs=path_to_root_cert, certfile=None, keyfile=None,
#                cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# ca_certs = "./huawei_root_ca.pem"
# client.tls_set(ca_certs=ca_certs,
#                cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)




# ssl_context = SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
# ssl_context.load_cert_chain(cert_file, key_file)
# ssl_context.verify_mode = CERT_REQUIRED
# ssl_context.check_hostname = False
# ssl_context.load_verify_locations(cafile=ca_certs)
# client.tls_set_context(context=ssl_context)

# client.tls_insecure_set(False)

# for res in socket.getaddrinfo(mqtt_server, None, 0, socket.SOCK_STREAM):
#     af, socktype, proto, canonname, sa = res
#     print(sa)
#     print(af)
#     print(socktype)
#     print(proto)
#     print(canonname)
#     print(sa)
#     print(sa[0])
#     print(sa[1])
client.connect(mqtt_server, port=1883)

# client.publish("devices/" + device_id + "/messages/events/", '{"id":123}', qos=1)
client.loop_forever()