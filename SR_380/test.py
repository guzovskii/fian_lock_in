import time
import threading
import numpy as np

def func_1():
    lock.acquire()
    for i in range(10):
        print("func_1: ", i)
        time.sleep(1)
    lock.release()
    print("thread_1 finished")

def func_2():
    lock.acquire()
    for i in range(5):
        print("---waiting---")
        time.sleep(2)
    lock.release()
    print("thread_2 finished")

#thread_1 = threading.Thread(target=func_1)
#thread_2 = threading.Thread(target=func_2)

lock = threading.Lock()

m = np.matrix([[1, 2], [3, 4]])

print(type(m))

#thread_1.start()
#thread_2.start()