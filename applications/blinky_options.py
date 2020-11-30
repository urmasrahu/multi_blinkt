#!/usr/bin/env python3

SERVER_USE_LOCALHOST = True  # if True, run server on localhost, otherwise try to use the host's prper IP address
CLIENT_USE_LOCALHOST = True  # if True, connect client to localhost, otherwise connect to SERVER_ADDRESS
SERVER_ADDRESS = "x.x.x.x"  # replace with server's IP address if one is running on another computer
PORT = 65434        # (non-privileged ports are > 1023)
COMMS_TIMEOUT = 1.0
LED_BRIGHTNESS_PERCENT = 5 # Blinkt LEDs are really bright, 5% is a good default

def GetOptions():
    return (SERVER_USE_LOCALHOST, CLIENT_USE_LOCALHOST, SERVER_ADDRESS, PORT, COMMS_TIMEOUT, LED_BRIGHTNESS_PERCENT)

