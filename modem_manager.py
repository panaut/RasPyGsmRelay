import config

from commonLog.rollingFileLog import RollingFileLog as Log
from exceptional.customException import CustomException
from gsmModem.exceptions import CommandError
from gsmModem.exceptions import TimeoutException
from gsmModem.modem import GsmModem
from serial.serialutil import SerialException


class ModemManager:
    class __ModemManager:

        def __init__(self, incomingCallCallbackFunc):
            try:
                self.logger = Log.getLogger('__ModemManager')
                self.__gsmModem = GsmModem(
                                    config.SERIAL_PORT,
                                    config.MODEM_BAUDRATE,
                                    incomingCallCallbackFunc=incomingCallCallbackFunc)

                self.logger.info('GSM Modem initialized.')
            except CommandError as err:
                raise CustomException(
                            code=501,
                            message='Error executing GSM Command on Modem initialization',
                            exception=err)
            except Exception as ex:
                raise CustomException(
                            code=502,
                            message='Unexpected error',
                            exception=ex)

        def wait(self, timeout):
            self.__gsmModem.rxThread.join(timeout=timeout)

        def connect(self, autoDetectPort=True, portsToAttempt=10):
            if self.__connect():
                return True

            # failed to open port defined in config file
            if autoDetectPort:
                self.logger.debug('Attempt to connect failed, but Port auto detection is ON, attempting to detect port')

                # get port name prefix (for windows it is 'COM', for linux is is '/dev/ttyUSB')
                prefix = config.SERIAL_PORT

                for i in range(1, len(prefix)):
                    if not prefix[-i:].isdigit():
                        prefix = prefix[0:len(prefix)-i+1]
                        break

                # acquired port prefix
                self.logger.debug('Serial port prefix is %s' % prefix)

                for i in range(0, 21):
                    self.__gsmModem.port = prefix + str(i)
                    self.logger.info('Attempting to open port %s' % self.__gsmModem.port)
                    if self.__connect():
                        return True
                return False

        def __connect(self):
            try:
                self.__gsmModem.connect(config.SIM_PIN)
                return True
            except SerialException as err:
                CustomException(
                            code=505,
                            message='Serial port not found',
                            exception=err)
                return False
            except TimeoutException as tex:
                CustomException(
                            code=506,
                            message='Serial port not responding',
                            exception=tex)
                return False
            except Exception as ex:
                raise CustomException(
                            code=504,
                            message='Unexpected error on Modem connecting',
                            exception=ex)

    __instance = None

    def __init__(self, incomingCallCallbackFunc):
        if not ModemManager.__instance:
            ModemManager.__instance = ModemManager.__ModemManager(incomingCallCallbackFunc)

    def __getattr__(self, attrName):
        if hasattr(ModemManager.__instance, attrName):
            return getattr(ModemManager.__instance, attrName)
        else:
            raise AttributeError(attrName)
