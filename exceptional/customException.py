from commonLog.rollingFileLog import RollingFileLog as Logging


class CustomException(Exception):
    def __init__(self, code, message=None, exception=None):
        self.code = code                        # @code         exception code
        self.message = message                  # @message      error message
        self.originalException = exception      # @exception    inner exception

        if self.message is None and self.originalException is not None:
            self.message = self.originalException.args[0]

        logger = Logging.getLogger('CustomException')   # Get Logger instance (with attached handlers)
        logger.error(self)                              # Make sure this exception is properly logged

    def __str__(self):
        return '(%s - %s) Exception: %s - %s' % \
               (self.code, self.message, type(self.originalException), self.originalException)
