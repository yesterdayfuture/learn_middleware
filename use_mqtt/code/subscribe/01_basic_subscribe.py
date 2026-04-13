import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 设置客户端唯一id
client = mqtt.Client(client_id="python_mqtt_client")

# 连接到MQTT代理
broker_address = "127.0.0.1"  # 公共Broker地址
port = 1883  # 默认端口
TOPIC = "python/mqtt"


# 连接成功回调
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC, qos=1)


# 接收消息回调
def on_message(client, userdata, msg):
    print(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")


# 绑定回调函数
client.on_connect = on_connect
client.on_message = on_message


# 带认证的连接（如果Broker需要）
client.username_pw_set(os.getenv("username"), os.getenv("password"))
# 连接MQTT代理
client.connect(broker_address, port)


# 启动循环处理网络流量
client.loop_forever()  # 阻塞式，持续运行
# 或
# client.loop_start()  # 非阻塞式，适合需要同时执行其他任务的场景


