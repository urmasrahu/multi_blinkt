try:
    import psutil
except ImportError:
    exit("This script requires the psutil module\nInstall with: sudo pip install psutil")

import datetime
from multi_blinkt import blinky
import time
import sys

MAX_BRIGHTNESS = 10 # adjust LED brightness with this, max value is 255

POLLING_INTERVAL_SECONDS = 5
LED_INDEX = 6

def GetColorForCpuLoad(loadPercentage):
    red = int(loadPercentage * MAX_BRIGHTNESS / 100)
    green = int(MAX_BRIGHTNESS - red)
    blue = 0
    
    return (red, green, blue)


### =============== MAIN PROGRAM STARTS HERE ===============

verbose = "-v" in sys.argv
led = blinky.Blinkt()

try:
    while True:
        load = psutil.cpu_percent()
        if verbose:
            timeString = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print (f"{timeString} {load}%")
        color = GetColorForCpuLoad(load)
        led.On(LED_INDEX, color)
        time.sleep(POLLING_INTERVAL_SECONDS)
except KeyboardInterrupt:
    led.Off(LED_INDEX)
