import threading

class EnhancedThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    @property 
    def stopped(self):
        return self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()

    def reset(self):
        self._stop_event.clear()