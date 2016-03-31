from pin_manager import PinMode

# SIM CARD Pin (required only if not deactivated)
SIM_PIN = None

# Serial Port on which GSM modem is attached to
#   For WINDOWS host port names begin with 'COM'
#   For LINUX host port names begin with '/dev/ttyUSB'
# SERIAL_PORT = '/dev/ttyUSB2'
SERIAL_PORT = 'COM5'

# MODEM BAUD-RATE VALUES
#           110
#           150
#           300
#           1200
#           2400
#           4800
#           9600
#           19200
#           38400
#           19200
#           57600
#           115200
#           230400
#           460800
#           921600
MODEM_BAUDRATE = 9600

# Pin number according to Broadcom enumeration
SWITCH_PIN = 14

# if switch is activated with VCC PIN_MODE should be HIGH,
# vice versa if switch reacts to GND this value should be LOW
PIN_MODE = PinMode.ACTIVE_HIGH

# Activation Time in seconds (the period during which switch is active)
ACTIVATION_TIME = 1
