import paho.mqtt.client as mqtt
import time
import random
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 连接到MQTT代理
broker_address = "127.0.0.1"
port = 1883
TOPIC = "python/mqtt"
CLIENT_ID = f"python-mqtt-{random.randint(0, 1000)}"

# 设置客户端唯一id
client = mqtt.Client(client_id=CLIENT_ID)


# 连接成功回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
    else:
        print(f"❌ Failed to connect, return code {rc}")


# 绑定回调函数
client.on_connect = on_connect

# 带认证的连接（如果Broker需要）
client.username_pw_set(os.getenv("username"), os.getenv("password"))

# 启动网络循环
# 这会在一个后台线程中处理网络连接和回调，非常关键！
client.loop_start()

# 连接MQTT代理
client.connect(broker_address, port)

# 发布消息
msg_count = 0
try:
    while True:
        if msg_count > 10:
            break
        time.sleep(2)
        msg = f"messages: {msg_count}"
        # publish() 返回一个 MQTTMessageInfo 对象
        result = client.publish(TOPIC, msg, qos=1)

        # 检查 result.rc (return code) 来判断是否成功
        # rc == 0 (mqtt.MQTT_ERR_SUCCESS) 表示消息已成功交给网络层
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Send `{msg}` to topic `{TOPIC}`")
        else:
            print(f"Failed to send message to topic {TOPIC}, error code: {result.rc}")
        msg_count += 1
finally:
    # 程序退出前，停止网络循环并断开连接，确保资源被正确释放
    client.loop_stop()
    client.disconnect()
    print("MQTT client disconnected.")