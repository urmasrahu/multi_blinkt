import datetime
from multi_blinkt import blinky
import os
import time

POLLING_INTERVAL_SECONDS = 60
LED_INDEX = 5

# LED colors
COLOR_WHILE_CHECKING = (0, 0, 255)
COLOR_OK = (0, 8, 0)
COLOR_ERROR = (255, 0, 0)

# colors for terminal output
COLOR_TERM_ALERT = '\033[91m'
COLOR_TERM_OK = '\033[92m'
COLOR_TERM_END = '\033[0m'


IP_ADDRESS = "192.168.10.1" # will ping this address to check for connection, e.g. use your home router address

def IsNetworkAlive():
    ret = os.system(F"ping -c 3 {IP_ADDRESS}")
    return ret == 0


### =============== MAIN PROGRAM STARTS HERE ===============

led = blinky.Blinkt()
try:
    while True:
        led.On(LED_INDEX, COLOR_WHILE_CHECKING)
        alive = IsNetworkAlive()
        timeString = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print (f"{COLOR_TERM_OK if alive else COLOR_TERM_ALERT}{timeString} Ping: {'OK' if alive else 'FAILED'}{COLOR_TERM_END}")
        led.On(LED_INDEX, COLOR_OK if alive else COLOR_ERROR)
        time.sleep(POLLING_INTERVAL_SECONDS)
except KeyboardInterrupt:
    led.Off(LED_INDEX)
