"""
将订阅者放入子线程，不影响其他线程和主进程的操作
"""
import paho.mqtt.client as mqtt
import threading
import time
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def mqtt_thread_func():
    client = mqtt.Client(client_id="python_mqtt_client_thread")

    def on_connect(client, userdata, flags, rc):
        print(f"[MQTT线程] 连接成功，结果码: {rc}")
        client.subscribe("python/mqtt", qos=1)

    client.on_connect = on_connect
    client.on_message = lambda c, u, m: print(f"[MQTT线程] 收到消息: {m.payload.decode()}")

    client.username_pw_set(os.getenv("username"), os.getenv("password"))
    client.connect("127.0.0.1", 1883)

    # 这里会阻塞当前这个子线程，但不会阻塞主线程
    print("[MQTT线程] 准备进入 loop_forever...")
    client.loop_forever()
    print("[MQTT线程] loop_forever 结束了")  # 只有断开连接才会打印



if __name__ == "__main__":
    # --- 主程序逻辑 ---
    print("[主线程] 1. 启动 MQTT 子线程...")
    t = threading.Thread(target=mqtt_thread_func)
    t.start()

    print("[主线程] 2. MQTT 线程已启动，主线程继续执行其他任务...")
    for i in range(5):
        time.sleep(1)
        print(f"[主线程] ... 正在处理其他业务，计数: {i}")

    print("[主线程] 3. 主线程任务完成，但程序不会退出，因为 MQTT 子线程还在运行。")
    # 注意：为了让演示效果明显，这里没有调用 t.join()，否则主线程会等待子线程