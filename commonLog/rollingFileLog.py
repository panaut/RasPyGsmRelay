import logging
from logging.handlers import TimedRotatingFileHandler


class RollingFileLog:
    entryFormat = '%(asctime)s %(levelname)s %(name)s - %(message)s'
    dateTimeFormat = '%d/%m/%Y %H:%M:%S'
    __handlers = []

    @staticmethod
    def addHandler(fileName, loggingLevel, enableConsoleOutput = True):
        if enableConsoleOutput:
            # Following Configuration will be applied to Console Tracing
            logging.basicConfig(
                format=RollingFileLog.entryFormat,
                datefmt=RollingFileLog.dateTimeFormat,
                level=logging.DEBUG
            )

        # Get new instance of Time Rotating File Handler
        handler = RollingFileLog.__getTimeRotatingHandler(fileName, loggingLevel)

        # append handler to static collection
        RollingFileLog.__handlers.append(handler)

    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)    # name should follow convention: name of the class using the logger
        logger.setLevel(logging.DEBUG)      # default logging level (does not affect handler settings)

        # in case that all handlers in static collection aren't attached to this logger
        # attach those that haven't been attached yet
        for handler in RollingFileLog.__handlers:
            if handler not in logger.handlers:
                logger.addHandler(handler)

        return logger

    @staticmethod
    def __getTimeRotatingHandler(path, loggingLevel):
        handler = TimedRotatingFileHandler(
                                        path,
                                        when='midnight',
                                        interval=1,
                                        backupCount=5)

        formatter = logging.Formatter(
            RollingFileLog.entryFormat,
            RollingFileLog.dateTimeFormat)
        handler.setFormatter(formatter)
        handler.suffix = '%Y-%m-%d %H-%M-%S.log'    # '%Y-%m-%d %H-%M-%S.log'
        handler.setLevel(loggingLevel)
        return handler
