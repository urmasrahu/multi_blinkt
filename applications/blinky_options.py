#!/usr/bin/env python3

HOST = "127.0.0.1"  # localhost
PORT = 65434        # (non-privileged ports are > 1023)
COMMS_TIMEOUT = 1.0
LED_BRIGHTNESS_PERCENT = 5 # Blinkt LEDs are really bright, 5% is a good default

def GetOptions():
    return (HOST, PORT, COMMS_TIMEOUT, LED_BRIGHTNESS_PERCENT)

