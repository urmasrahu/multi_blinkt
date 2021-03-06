#!/usr/bin/env python3

import json
import socket
import sys
import time

try:
    import blinkt
except ModuleNotFoundError:
    pass  # blinkt is only required in server mode

LOCALHOST = "127.0.0.1" # server always binds to localhost

# defaults, these can be overriden in blinky_options.py
SERVER_USE_LOCALHOST = True  # if True, run server on localhost, otherwise try to use the host's prper IP address
CLIENT_USE_LOCALHOST = True  # if True, connect client to localhost, otherwise connect to SERVER_ADDRESS
SERVER_ADDRESS = "x.x.x.x"  # replace with server's IP address if one is running on another computer
PORT = 65434        # (non-privileged ports are > 1023)
COMMS_TIMEOUT = 1.0
LED_BRIGHTNESS_PERCENT = 5 # Blinkt LEDs are really bright, 5% is a good default

VERBOSE_MODE = False

try: # override above constants if needed
    import blinky_options
    SERVER_USE_LOCALHOST, CLIENT_USE_LOCALHOST, SERVER_ADDRESS, PORT, COMMS_TIMEOUT, LED_BRIGHTNESS_PERCENT = blinky_options.GetOptions()
except ImportError:
    pass

def PrintUsageAndExit():
    print("Usage: blinky command <parameters>")
    print("Commands:")
    print("  Run the Blinkt server: blinky.py server")
    print("  Turn LED on: blinky.py on index red green blue")
    print("  Turn LED off: blinky.py off")
    print("  Flash LED: blinky.py flash index red green blue milliseconds")
    sys.exit(1)


class IpcServer:
    def Run(self):
        self.ipAddress = self.GetIpAddress()
        self.OnStartup()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ipAddress, PORT))
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                except KeyboardInterrupt:
                    self.OnExit()
                    return
                
                with conn:
                    if VERBOSE_MODE:
                        print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        if VERBOSE_MODE:
                            print(f"Received {repr(data)}")
                        # conn.sendall(data) # use this if you want to echo data back
                        result = self.HandleRequest(data)
                        conn.sendall(result.encode("UTF-8"))
                        
    def GetIpAddress(self):
        if SERVER_USE_LOCALHOST:
            return LOCALHOST
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            result = s.getsockname()[0]
        except Exception:
            print("Error: cannot determine host IP address, falling back to loopback address")
            result = LOCALHOST
        finally:
            s.close()
        return result
    
    def OnStartup(self):
        print(f"Running server on {self.ipAddress} port {PORT}, brightness={LED_BRIGHTNESS_PERCENT}%, press CTRL-C to exit")
        blinkt.set_all(255, 255, 255)
        blinkt.show()
        time.sleep(1)
        blinkt.set_all(0, 0, 0)
        blinkt.show()
        
    def OnExit(self):
        print("Exiting")
        blinkt.set_all(255, 0, 0)
        blinkt.show()
        time.sleep(1)
        blinkt.set_all(0, 0, 0)
        blinkt.show()
                        
    def HandleRequest(self, data):
        try:
            request = json.loads(data)
        except json.decoder.JSONDecodeError:
            return "Error: json"
        
        try:
            command = request["cmd"]
        except KeyError:
            return "Error: cmd"

        led = self.GetParam(request, "led", 0)
        color = self.GetParam(request, "color", (255,255,255))
        time_ms = self.GetParam(request, "time", 0)
        
        if command in ("on"):
            if not self.ValidateLedAndColor(led, color):
                return "Error: params"
        
        if command in ("off"):
            if not self.ValidateLed(led):
                return "Error: params"
            
        if command == "flash":
            if not self.ValidateLedAndColorAndTime(led, color, time_ms):
                return "Error: params"

        if command == "on":
            self.HandleOn(led, color)
        elif command == "off":
            self.HandleOff(led)
        elif command == "flash":
            self.HandleFlash(led, color, time_ms)
        
        return "OK"
    
    def GetParam(self, request, name, default):
        return request[name] if name in request else default
    
    def HandleOn(self, led, color):
        blinkt.set_pixel(led, color[0], color[1], color[2])
        blinkt.show()
        
    def HandleOff(self, led):
        self.HandleOn(led, (0, 0, 0))
        
    def HandleFlash(self, led, color, time_ms):
        previous = blinkt.get_pixel(led)
        self.HandleOn(led, color)
        time.sleep(time_ms / 1000)
        self.HandleOn(led, previous[:3]) # first 3 items are the color values
        
    def ValidateLed(self, led):
        if not isinstance(led, int):
            return False
        if led < 0 or led > 7:
            return False
        return True        
        
    def ValidateLedAndColor(self, led, color):
        if not self.ValidateLed(led):
            return False
        if not isinstance(color, list):
            return False
        if len(color) != 3:
            return False
        for c in color:
            if not isinstance(c, int):
                return False
            if c < 0 or c > 255:
                return False
        return True
    
    def ValidateLedAndColorAndTime(self, led, color, time_ms):
        if not self.ValidateLedAndColor(led, color):
            return False
        if not isinstance(time_ms, int):
            return False
        if time_ms < 0 or time_ms > 1000:
            return False
        return True
   

class IpcClient:
    def __init__(self):
        self.ipAddress = LOCALHOST if CLIENT_USE_LOCALHOST else SERVER_ADDRESS
        print(f"Blinky IPC client: will connect to {self.ipAddress} port {PORT}")
    
    def SendMessage(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(COMMS_TIMEOUT)
            
            try:
                s.connect((self.ipAddress, PORT))
            except ConnectionRefusedError:
                return (None, "Unable to connect to server")
            
            try:
                s.sendall(message)
            except socket.timeout:
                return (None, "Send timeout")
            
            try:
                data = s.recv(1024)
            except socket.timeout:
                return (None, "Receive response timeout")
                
            s.close()
            return (data, None)
        
        
class Blinkt:
    def __init__(self):
        self.client = IpcClient()
    
    def On(self, led, color):
        data = {}
        data["cmd"] = "on"
        data["led"] = led
        data["color"] = color
        return self.SendMessageToServer(data)
    
    def Off(self, led):
        data = {}
        data["cmd"] = "off"
        data["led"] = led
        return self.SendMessageToServer(data)
    
    def Flash(self, led, color, time):
        data = {}
        data["cmd"] = "flash"
        data["led"] = led
        data["color"] = color
        data["time"] = time
        return self.SendMessageToServer(data)
        
    def SendMessageToServer(self, data):
        return self.client.SendMessage(json.dumps(data).encode("UTF-8"))
        

def RunServerAndExit():
    server = IpcServer()
    server.Run()
    sys.exit(0)

def DecodeCommandLineParameters(command, parameters):
    result = {}
    n = len(parameters)
    if command in ("on", "off", "flash"):
        result["led"] = int(parameters[0]) if n > 0 else 0
        result["r"] = int(parameters[1]) if n > 1 else 255
        result["g"] = int(parameters[2]) if n > 2 else 255
        result["b"] = int(parameters[3]) if n > 3 else 255
        result["time"] = int(parameters[4]) if n > 4 else 100
    return result

def SendCommandToServerAndExit(command, parameters):
    blinkt = Blinkt()
    p = DecodeCommandLineParameters(command, parameters)
    
    if command == "on":
        response, error = blinkt.On(p["led"], (p["r"],p["g"],p["b"]))
    elif command == "off":
        response, error = blinkt.Off(p["led"])
    elif command == "flash":
        response, error = blinkt.Flash(p["led"], (p["r"],p["g"],p["b"]), p["time"])
    
    if response != None:
        print(f"Received: {repr(response)}")
    else:
        print(f"Error: {error}")
    
    sys.exit(0 if error != None else 1)
    
    
### =============== MAIN PROGRAM STARTS HERE ===============

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            VERBOSE_MODE = True
        
        if sys.argv[1] == "server":
            RunServerAndExit()
        if sys.argv[1] in ("on", "off", "flash"):
            SendCommandToServerAndExit(sys.argv[1], sys.argv[2:])

    PrintUsageAndExit()
