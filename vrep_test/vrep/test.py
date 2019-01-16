import threading
import time

class Thread(self):
    def job():
      for i in range(5):
        print("Child thread:", i)
        time.sleep(1)

    t = threading.Thread(target = job)
    t.start()
    for i in range(3):
      print("Main thread:", i)
      time.sleep(1)

    t.join()
    print("Done.")