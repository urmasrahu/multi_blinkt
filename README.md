# multi_blinkt

Use Pimoroni Blinkt! (Raspberry Pi add-on) from multiple independent programs.


## What is it

[Pimoroni Blinkt!](https://shop.pimoroni.com/products/blinkt) is a Raspberry Pi add on of eight RGB LEDs. There is a [Python library](https://github.com/pimoroni/blinkt) for controlling it. Unfortunately using this library directly in your programs does not allow you to use the LEDs from multiple programs simultaneously. You may want to use some of the LEDs from one program and others from another, and this is not possible because the library maintains the state of all eight LEDs internally, and the show() call will then affect all LEDs. This **multi_blinkt** thing here allows you to overcome this limitation.

## How it works

**multi_blinkt** works by having a simple server (using the "socket" networking interface) listening to incoming requests to change the lights. One or more clients will then connect to the server to make the requests. There are two Python scripts here: **blinky.py** contains code for both the server and clients, and **blinky_options.py** can be used to change some parameters.

## Dependencies

**multi_blinkt** naturally requires the Blinkt! device and its Python library (link above). It works with Python 3 only.

## Installation

I haven't bothered to make a proper pip-installable package for this, you will install it manually, but this is quite straightforward. Download the package from GitHub here, then copy both Python files to your **/usr/local/lib/python3.7/dist-packages/multi_blinkt** directory. There is also a **deploy** Bash script included here that shows how this is done:

```
sudo mkdir /usr/local/lib/python3.7/dist-packages/multi_blinkt
sudo cp -v blinky.py /usr/local/lib/python3.7/dist-packages/multi_blinkt
sudo cp -v blinky_options.py /usr/local/lib/python3.7/dist-packages/multi_blinkt
```
 
If you have your Python packages located in some other directory then change the paths above accordingly. You can also copy them to your Python site-packages directory under your home directory, but in this case other user accounts won't be able to use this. This will matter if you need to run some of your programs using this as "superuser" (sudo).

Actually, you will not need to install the files to the above noted location in case you want to control the leds from the terminal or a Bash script, as in this case you can have the files in any directory. The above noted installation is needed in case you want to use the library from your Python code. More of this below.

## Running the server

To start the server, start blinky.py with the *server* command line parameter:

```
python3 /usr/local/lib/python3.7/dist-packages/multi_blinkt/blinky.py server
```
 
Optionally, you can add the *-v* parameter to run in verbose mode, printing out all incoming requests.

Now that the server is running, you can interact with it to turn the LEDs on and off. There are two options for this, see below.

## Using the LEDs from the terminal or a Bash script (option 1)

You can run blinky.py from the terminal or a Bash script in "client" mode by controlling the LEDs according to command line parameters. In the examples below, I have omitted the long path to the blinky.py script; you can either have an alias or just another copy of the script in some directory, it does not really need to be located in the Python dist-packages directory.

### Turning a LED on
To turn a LED on, use the **on** command:

```
on <index> <red> <green> <blue>
```
  
where *index* is the LED index (from 0 to 7), and the follwing paramters are the red, green and blue color values respectively (in the range 0-255). For example, this will set the first (index 0) LED to red:

```
python3 blinky.py on 0 255 0 0
```
  
### Turning a LED off
To turn a LED off, you can actually use the above "on" command with zero values for all colors, but for convenience, you can use the **off** command:

```
off <index>
```
  
For example, this will turn off the first LED:

```
python3 blinky.py off 0
```
  
### Flashing a LED

To "flash" a LED, i.e. turn it on, wait for a short period, and return LED to its previous state, use the **flash** command:

```
flash <index> <red> <green> <blue> <milliseconds>
```  
  
For example, this will flash the 2nd LED (index 1) as green for 0.1 seconds:

```
python3 blinky.py flash 1 0 255 0 100
```
  
Note: as flashing a LED will block the server for the specified amount of time, flash times longer than 1000 ms (one second) are not permitted.
  
## Using the LEDs from your Python program (option 2)

To use the LEDs from your Python program, first import the library:

```
from multi_blinkt import blinky
```  
  
Then create an instance of the **Blinkt** class, like this:

```
led = blinky.Blinkt()
```

Then use the **Blinkt** class methods for controlling the LEDs as follows.

### Turning a LED on

Use the **On(led, color)** method, where *led* is the LED index (from 0 to 7), and *color* is a three-member tuple of the (red, green, blue) color values (again, ranging from 0 to 255). For example, this will set the first (index 0) LED to red:

```
led.On(0, (255, 0, 0))
```
  
### Turning a LED off

Use the **Off(led)** method. For example, this will turn off the first LED:

```
led.Off(0)
```
  
### Flashing a LED

To "flash" a LED, i.e. turn it on, wait for a short period, and return LED to its previous state, use the **Flash(led, color, milliseconds)** method. For example, this will flash the 2nd LED (index 1) as green for 0.1 seconds:

```
led.Flash(1, (0, 255, 0), 100)
```

## Examples

The **applications** directory contains some examples that use the **Blinkt** class:

* **cpuload.py**: Show CPU load on one LED (green with low load, red with high)
* **cputemp.py**: Chow CPU temperature on one LED (green with low temperature, red with high)
* **network_check.py**: Check for network connectivity, show green when connection available, red when not

## Advanced use: control LEDs from another computer over network

In **blinky_options.py**, the following constants are being set:

```
SERVER_USE_LOCALHOST = True  # if True, run server on localhost, otherwise try to use the host's proper IP address
CLIENT_USE_LOCALHOST = True  # if True, connect client to localhost, otherwise connect to SERVER_ADDRESS
SERVER_ADDRESS = "x.x.x.x"  # replace with server's IP address if one is running on another computer
PORT = 65434        # (non-privileged ports are > 1023)
```

As the comments above indicate, with these defaults, the server will run on the computer's "localhost" address, 127.0.0.1, and one or more clients will also connect to this address. This allows only programs running on the same computer (the Raspberry Pi) to use the LEDs, as other computers won't be able to connect to the server. This is probably good for most use scenarios.

However, if you want to give access to the Blinkt LEDs from another computer, you can change these values. In this case, set both SERVER_USE_LOCALHOST and CLIENT_USE_LOCALHOST to False, and set SERVER_ADDRESS to the IP address of the computer that runs the multi_blinkt server. That way, both clients running in the same computer and other computers can connect to the server and use the LEDs (the server will print out the IP address it is using at startup). The other computers will not need to have the Blinkt! Python library installed, and they don't need to be Raspbarry Pi computers, you can use Windows or whatever.
