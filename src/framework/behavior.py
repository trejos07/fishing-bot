import time
from framework import AppBase
from framework import EnhancedThread

class Behavior():
    def __init__(self, run_new_thread=False):
        self.thread = EnhancedThread(target=self.run_on_thread) if run_new_thread else None
        self.awake()

    def awake(self):
        pass

    def start (self):
        if self.thread:
            self.thread.start()
        else:
            AppBase.to_update.append(self.update)

    def run_on_thread(self):
        while self.thread and not self.thread.stopped:
            self.update()
            time.sleep(0.01)

    def update(self):
        pass

    def stop(self):
        if self.thread:
            self.thread.stop()
        else:
            AppBase.to_update.remove(self.update)
    
    def dispose(self):
        pass