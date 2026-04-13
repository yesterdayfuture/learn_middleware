"""
t.join() 的核心作用非常明确：让当前线程（通常是主线程）停下来等待，直到 t 这个线程执行完毕，当前线程才继续往下执行。

下面示例：
    如果不加t.join()，会先打印 主线程：我先走了，不等了！ ，然后等待子线程执行结束后，项目结束
    如果加t.join()，会执行完 子线程， 然后打印 主线程：我先走了，不等了！ ，项目结束
"""
import threading
import time

def task():
    time.sleep(3)
    print("子线程：任务做完了！")

t = threading.Thread(target=task)
t.start()
t.join()
print("主线程：我先走了，不等了！")
# 结果：这句话会立刻打印，哪怕子线程还没干完活