import config
import RPi.GPIO as gpio
import time
import threading

from exceptional.customException import CustomException
from commonLog.rollingFileLog import RollingFileLog as Log
from threading import Thread


class PinMode:
    ACTIVE_LOW = 0
    ACTIVE_HIGH = 1

class AppStatus:
    INITIALIZING = 0
    ACTIVE = 1
    INACTIVE = 2


class PinManager:
    class __PinManager:
        class __PinState:
            INACTIVE = 0
            ACTIVE = 1

        def __init__(self, switchPin, switchPinMode, statusLedPin, relayStatusLedPin, errorLedPin, activationTime):
            # @switchPin                definition of PIN to which relay is attached to
            # @switchPinMode            definition of PIN mode (Active is HIGH or LOW)
            # @statusLedPin             definition of PIN to which STATUS LED is attached to
            # @relayStatusLedPin        definition of PIN to which relay status LED is attached to
            # @errorLedPin              definition of PIN to which error LED is attached to
            # @activationTime           duration of relay activation

            self.logger = Log.getLogger('__PinManager')

            self.__blinkers = {}

            # set up GPIO using BCM numbering
            gpio.setmode(gpio.BCM)
            self.logger.debug('GPIO mode set to Broadcom')

            self.__switchPin = switchPin
            gpio.setup(switchPin, gpio.OUT)
            self.logger.debug('SWITCH pin set to %s' % switchPin)

            self.__statusLedPin = statusLedPin
            if statusLedPin:
                gpio.setup(statusLedPin, gpio.OUT)
                self.logger.debug('STATUS_LED pin set to %s' % statusLedPin)

            self.__relayStatusPin = relayStatusLedPin
            if relayStatusLedPin:
                gpio.setup(relayStatusLedPin, gpio.OUT)
                self.logger.debug('RELAY_STATUS_LED pin set to %s' % relayStatusLedPin)

            self.__errorLedPin = errorLedPin
            if errorLedPin:
                gpio.setup(errorLedPin, gpio.OUT)
                self.logger.debug('ERROR_LED pin set to %s' % errorLedPin)

            self.__switchPinMode = switchPinMode
            self.__activationTime = activationTime

            # Set relay to inactive state
            self.__setPin(self.__switchPin, self.__PinState.INACTIVE)

        def __setPin(self, pin, pinState):
            targetLevel = gpio.LOW

            if pin == self.__switchPin:
                if self.__switchPinMode == PinMode.ACTIVE_HIGH and pinState == self.__PinState.INACTIVE:
                    targetLevel = gpio.LOW
                elif self.__switchPinMode == PinMode.ACTIVE_HIGH and pinState == self.__PinState.ACTIVE:
                    targetLevel = gpio.HIGH
                elif self.__switchPinMode == PinMode.ACTIVE_LOW and pinState == self.__PinState.INACTIVE:
                    targetLevel = gpio.HIGH
                elif self.__switchPinMode == PinMode.ACTIVE_LOW and pinState == self.__PinState.ACTIVE:
                    targetLevel = gpio.LOW
            else:
                if pinState == self.__PinState.INACTIVE:
                    targetLevel = gpio.LOW
                else:
                    targetLevel = gpio.HIGH

            try:
                gpio.output(pin, targetLevel)
                self.logger.debug('Pin %s voltage level set to %s' % (pin, pinState))

                if pin == self.__switchPin and self.__relayStatusPin:
                    # set relay status LED ON or OFF
                    self.__setPin(self.__relayStatusPin, pinState)
            except CustomException as ex:
                raise ex    # Propagate error upwards
            except Exception as ex:
                raise CustomException(
                                    code=902,
                                    message="Unable to set output pin %s's voltage to %s level" % (pin, pinState),
                                    exception=ex)

        def __doActivateSwitch(self):
            try:
                # Set switch to ACTIVE state
                self.__setPin(self.__switchPin, self.__PinState.ACTIVE)

                # wait defined period pf time
                time.sleep(self.__activationTime)

                # Restore switch back to INACTIVE state
                self.__setPin(self.__switchPin, self.__PinState.INACTIVE)
            except CustomException as ex:
                raise ex  # Propagate error upwards
            except Exception as ex:
                raise CustomException(
                    code=903,
                    message='Unable to activate switch',
                    exception=ex)

        def __doBlink(self, pin, timeOn, timeOff, stopEvent):
            self.logger.debug('Pin %s started blinking' % pin)
            while stopEvent.isSet():
                self.__setPin(pin, self.__PinState.ACTIVE)
                time.sleep(timeOn)

                self.__setPin(pin, self.__PinState.INACTIVE)
                time.sleep(timeOff)

            self.logger.debug('Pin %s stopped blinking' % pin)

        def __blink(self, pin, timeOn, timeOff):
            threadStopEvent = threading.Event()
            threadStopEvent.set()

            blinkerThread = threading.Thread(
                                target=self.__doBlink,
                                kwargs={'pin': pin, 'timeOn': timeOn, 'timeOff': timeOff, 'stopEvent': threadStopEvent})
            # blinkerThread.daemon = True

            self.__blinkers[pin] = threadStopEvent

            blinkerThread.start()

            return threadStopEvent

        def activateSwitch(self):
            self.logger.info("Activating switch")

            activatorThread = Thread(target=self.__doActivateSwitch)
            activatorThread.start()

        def setStatus(self, status):
            # do we have active blinker on this pin?
            blinker = self.__blinkers.pop(self.__statusLedPin, None)

            if self.__statusLedPin:
                if status == AppStatus.INITIALIZING:
                    # start blinking
                    if not blinker:
                        blinker = self.__blink(
                                            self.__statusLedPin,
                                            config.BLINK_TIME_ON,
                                            config.BLINK_TIME_OFF)
                    self.__blinkers[self.__statusLedPin] = blinker

                elif status == AppStatus.ACTIVE:
                    if blinker:
                        # stop blinking
                        blinker.clear()
                    # turn LED ON
                    self.__setPin(self.__statusLedPin, self.__PinState.ACTIVE)
                else:
                    if blinker:
                        # stop blinking
                        blinker.clear()
                    # turn LED ON
                    self.__setPin(self.__statusLedPin, self.__PinState.INACTIVE)

            self.logger.info("Status set to %s" % status)

        def cleanup(self):
            # stop blinkers
            for blinker in self.__blinkers:
                blinker.clear()

            gpio.cleanup()
            self.logger.info("GPIO 'cleanup' performed")

    __instance = None

    def __init__(self,
                 switchPin,
                 switchPinMode = PinMode.ACTIVE_HIGH,
                 statusLedPin=None,
                 relayStatusLedPin=None,
                 errorLedPin=None,
                 activationTime=1):
        # @switchPin                definition of PIN to which relay is attached to
        # @switchPinMode            definition of PIN mode (Active is HIGH or LOW)
        # @statusLedPin             definition of PIN to which STATUS LED is attached to
        # @relayStatusLedPin        definition of PIN to which relay status LED is attached to
        # @errorLedPin              definition of PIN to which error LED is attached to
        # @activationTime           duration of relay activation

        if PinManager.__instance is None:
            PinManager.__instance = PinManager.__PinManager(
                                                    switchPin=switchPin,
                                                    switchPinMode=switchPinMode,
                                                    statusLedPin=statusLedPin,
                                                    relayStatusLedPin=relayStatusLedPin,
                                                    errorLedPin=errorLedPin,
                                                    activationTime=activationTime)

    def __getattr__(self, attrName):
        if hasattr(PinManager.__instance, attrName):
            return getattr(PinManager.__instance, attrName)
        else:
            raise AttributeError(attrName)


