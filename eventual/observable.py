import threading


class Observable:
    def __init__(self):
        self.__handlers = []

    def addObserver(self, method):
        self.__handlers.append(method)

    def removeObserver(self, handlerMethod):
        self.__handlers.remove(handlerMethod)

    def notifyObeservers(self, sender, args):
        for handler in self.__handlers:
            handler(sender, args)

    def notifyObeserversAsync(self, sender, args):
        for handler in self.__handlers:
            thr = threading.Thread(target=handler, args=(sender, args))
            thr.start()
