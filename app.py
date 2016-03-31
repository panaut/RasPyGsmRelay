import logging
import time

from commonLog.rollingFileLog import RollingFileLog as Log
from exceptional.customException import CustomException
from gsmModem.exceptions import InterruptedException
from modem_manager import ModemManager


class ConsoleApp:
    def __init__(self):

        # Initialize Logger
        Log.addHandler('DEBUG.log', logging.DEBUG)
        self.logger = Log.getLogger('ConsoleApp')

    def run(self):
        try:
            self.logger.info('GSM Relay Console App started')

            # Initialize GSM modem
            self.logger.info('Initializing modem...')
            print('Initializing modem...')
            mManager = ModemManager(self.incommingCallHandler)
            if mManager.connect(autoDetectPort=True):
                self.logger.info('Modem connected!')
                print('Modem connected!')
            else:
                self.logger.info('Connecting modem failed')
                print('Connecting modem failed')
                raise CustomException(
                            code=500,
                            message='Failed to initialize modem')

            print('Waiting for incoming calls...')

            while True:
                # mManager.rxThread.join(60)
                mManager.wait(60)


            # pManager = PinManager(
            #     switchPin=config.SWITCH_PIN,
            #     pinMode=config.PIN_MODE,
            #     activationTime=config.ACTIVATION_TIME)
            #
            # pManager.activateSwitch()
            # pManager.cleanup()
        except Exception as ex:
            if not isinstance(ex, CustomException):     # just make sure exception is being properly logged
                CustomException(
                    code=102,
                    message='Unexpected error',
                    exception=ex)

        self.logger.info('Terminating GSM Relay Console App')

    def incommingCallHandler(self, call):
        if call.ringCount == 1:
            print('Incoming call from:', call.number)
        elif call.ringCount >= 2:
            if call.dtmfSupport:
                print('Answering call and playing some DTMF tones...')
                call.answer()
                # Wait for a bit - some older modems struggle to send DTMF tone immediately after answering a call
                time.sleep(2.0)
                try:
                    call.sendDtmfTone('9515999955951')
                except InterruptedException as e:
                    # Call was ended during playback
                    print('DTMF playback interrupted: {0} ({1} Error {2})'.format(e, e.cause.type, e.cause.code))
                finally:
                    if call.answered:
                        print('Hanging up call.')
                        call.hangup()
            else:
                print('Modem has no DTMF support - hanging up call.')
                call.hangup()
        else:
            print(' Call from {0} is still ringing...'.format(call.number))

app = ConsoleApp()

try:
    app.run()
except RuntimeError:
    print('Oh oh... An error...')
finally:
    print('Exiting loop')
