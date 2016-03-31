from exceptional.customException import CustomException
from commonLog.rollingFileLog import RollingFileLog as Log


class PinMode:
    ACTIVE_LOW = 0
    ACTIVE_HIGH = 1


class PinManager:
    class __PinManager:
        class __PinState:
            INACTIVE = 0
            ACTIVE = 1

        class __PinLevel:
            LOW = 0
            HIGH = 1

        def __init__(self, switchPin, pinMode, activationTime):
            # @switchPin            definition of PIN to which relay is attached to
            # @pinMode              definition of PIN mode (Active is HIGH or LOW)
            # @activationTime       duration of relay activation

            self.logger = Log.getLogger('__PinManager')

            self.__switchPin = switchPin
            self.__pinMode = pinMode
            self.__activationTime = activationTime

            # ToDo: Setup PIN as output
            self.__setPin(self.__PinState.INACTIVE)

        def __setPin(self, pinState):
            targetLevel = 0

            if self.__pinMode == PinMode.ACTIVE_HIGH and pinState == self.__PinState.INACTIVE:
                targetLevel = self.__PinLevel.LOW
            elif self.__pinMode == PinMode.ACTIVE_HIGH and pinState == self.__PinState.ACTIVE:
                targetLevel = self.__PinLevel.HIGH
            elif self.__pinMode == PinMode.ACTIVE_LOW and pinState == self.__PinState.INACTIVE:
                targetLevel = self.__PinLevel.HIGH
            elif self.__pinMode == PinMode.ACTIVE_LOW and pinState == self.__PinState.ACTIVE:
                targetLevel = self.__PinLevel.LOW

            # do something with targetLevel...

            try:
                # ToDo: Set value of output PIN
                raise NotImplementedError("Don't forget to set pin voltage to targetLevel!")
            except CustomException as ex:
                raise ex    # Propagate error upwards
            except Exception as ex:
                raise CustomException(
                                    code=902,
                                    message='Unable to set output pin voltage to %s level' % pinState,
                                    exception=ex)

        def activateSwitch(self):
            self.logger.debug("Called 'activatePin' method")

            try:
                self.__setPin(self.__PinState.ACTIVE)

                # ToDo: Implement Timing Mechanism
                raise NotImplementedError("Don't forget your timer mechanism!")
            except CustomException as ex:
                raise ex    # Propagate error upwards
            except Exception as ex:
                raise CustomException(
                                    code=903,
                                    message='Unable to activate switch',
                                    exception=ex)

        def cleanup(self):
            self.logger.debug("Called 'cleanup' method")

            # ToDo: Reset PIN (opposite of setting up PIN as output)
            raise NotImplementedError("Don't forget to reset PIN statuses!")

    __instance = None

    def __init__(self, switchPin, pinMode=PinMode.ACTIVE_HIGH, activationTime=1):
        # @switchPin                definition of PIN to which relay is attached to
        # @pinMode                  definition of PIN mode (Active is HIGH or LOW)
        # @activationTime           duration of relay activation

        # ToDo: these lines should probably be removed
        # if switchPin is None:
        #     raise CustomException(code=901, message='Relay switch is not defined')

        if PinManager.__instance is None:
            PinManager.__instance = PinManager.__PinManager(
                                                    switchPin=switchPin,
                                                    pinMode=pinMode,
                                                    activationTime=activationTime)

    def __getattr__(self, attrName):
        if hasattr(PinManager.__instance, attrName):
            return getattr(PinManager.__instance, attrName)
        else:
            raise AttributeError(attrName)


