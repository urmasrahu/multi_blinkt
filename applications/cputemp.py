from gpiozero import CPUTemperature
from multi_blinkt import blinky
import datetime
import time
import sys

FULL_GREEN_LEVEL = 50
FULL_RED_LEVEL = 80
MAX_BRIGHTNESS = 10 # adjust LED brightness with this, max value is 255

POLLING_INTERVAL_SECONDS = 60
LED_INDEX = 7

def GetColorForCpuTemp(temperature):
    level = temperature
    if level < FULL_GREEN_LEVEL:
        level = FULL_GREEN_LEVEL
    elif level > FULL_RED_LEVEL:
        level = FULL_RED_LEVEL
        
    # map temperature to the range 0 - MAX_BRIGHTNESS
    level = (level - FULL_GREEN_LEVEL) * (MAX_BRIGHTNESS / (FULL_RED_LEVEL - FULL_GREEN_LEVEL))
    
    red = int(level)
    green = int(MAX_BRIGHTNESS - level)
    blue = 0
    
    return (red, green, blue)

### =============== MAIN PROGRAM STARTS HERE ===============

verbose = "-v" in sys.argv
led = blinky.Blinkt()

try:
    while True:
        temperature = CPUTemperature().temperature
        if verbose:
            timeString = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print (f"{timeString} {temperature}°C")
        color = GetColorForCpuTemp(temperature)
        led.On(LED_INDEX, color)
        time.sleep(POLLING_INTERVAL_SECONDS)
except KeyboardInterrupt:
    led.Off(LED_INDEX)
