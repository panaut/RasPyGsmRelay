from eventual.observable import Observable
import time
import threading


class Timer(Observable):
    def __init__(self, period, isAsync=True):
        # @period           period between firing events
        # @isAsync          flag indicating whether notifications are async

        super().__init__()

        self._started = False
        self.period = period
        self.isAsync = isAsync

    def start(self):
        self._started = True

        thr = threading.Thread(target=self.__run, args=())
        thr.start()

    def stop(self):
        self._started = False

    def __run(self):
        while self._started:
            time.sleep(self.period)
            if self._started:
                if self.isAsync:
                    self.notifyObeserversAsync(self, None)
                else:
                    self.notifyObeservers(self, None)
