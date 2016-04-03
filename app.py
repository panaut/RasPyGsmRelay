import config
import logging

from commonLog.rollingFileLog import RollingFileLog as Log
from exceptional.customException import CustomException
from gsmModem.exceptions import InterruptedException
from modem_manager import ModemManager
from pin_manager import PinManager
from pin_manager import AppStatus


class ConsoleApp:
    def __init__(self):
        # Initialize Logger
        Log.addHandler('DEBUG.log', logging.DEBUG)
        self.logger = Log.getLogger('ConsoleApp')

        self.pManager = None

    def run(self):
        try:
            self.logger.info('GSM Relay Console App started')

            # Initialize GPIO
            print('Initializing GPIO...')
            self.pManager = PinManager(
                switchPin=config.SWITCH_PIN,
                switchPinMode=config.PIN_MODE,
                statusLedPin=config.STATUS_LED_PIN,
                relayStatusLedPin=config.RELAY_LED_PIN,
                activationTime=config.ACTIVATION_TIME)
            print('GPIO initialized!')
            self.logger.info('GPIO initialized!')

            self.pManager.setStatus(AppStatus.INITIALIZING)

            # Initialize GSM modem
            self.logger.info('Initializing modem...')
            print('Initializing modem...')
            mManager = ModemManager(self.incommingCallHandler)
            if mManager.connect(autoDetectPort=True):
                self.logger.info('Modem connected!')
                print('Modem connected!')
            else:
                print('Connecting modem failed')
                raise CustomException(
                            code=500,
                            message='Failed to initialize modem')

            print('Waiting for incoming calls...')

            self.pManager.setStatus(AppStatus.ACTIVE)

            while True:
                mManager.wait(3600)

        except Exception as ex:
            self.pManager.setStatus(AppStatus.INACTIVE)
            if not isinstance(ex, CustomException):     # just make sure exception is being properly logged
                CustomException(
                    code=102,
                    message='Unexpected error',
                    exception=ex)

    def stop(self):
        self.pManager.cleanup()
        self.logger.info('GSM Relay Console App stopped.')

    def incommingCallHandler(self, call):
        if call.active:
            print('Incoming call from: %s' % call.number)
            self.pManager.activateSwitch()

            call.hangup()
            self.logger.debug('Call terminated')

        # if call.ringCount == 1:
        #     print('Incoming call from: %s' % call.number)
        # elif call.ringCount >= 2:
        #     if call.dtmfSupport:
        #         print('Answering call and playing some DTMF tones...')
        #         call.answer()
        #         # Wait for a bit - some older modems struggle to send DTMF tone immediately after answering a call
        #         time.sleep(2.0)
        #         try:
        #             call.sendDtmfTone('9515999955951')
        #         except InterruptedException as e:
        #             # Call was ended during playback
        #             print('DTMF playback interrupted: {0} ({1} Error {2})'.format(e, e.cause.type, e.cause.code))
        #         finally:
        #             if call.answered:
        #                 print('Hanging up call.')
        #                 call.hangup()
        #     else:
        #         print('Modem has no DTMF support - hanging up call.')
        #         call.hangup()
        # else:
        #     print(' Call from {0} is still ringing...'.format(call.number))

app = ConsoleApp()

try:
    app.run()
except:
    app.stop()
finally:
    app.logger.info('GSM Relay Console App terminated')
