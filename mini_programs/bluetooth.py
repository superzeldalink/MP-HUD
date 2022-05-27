from machine import Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import UILib as ui
import utime
import re

WIDTH  = 128 # SSD1306 horizontal resolution
HEIGHT = 64   # SSD1306 vertical resolution

i2c = I2C(1,scl=Pin(3),sda=Pin(2),freq=200000)  # start I2C on I2C1 (GPIO 26/27)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c) # oled controller

bt = UART(0,9600)

ui.initUI(oled, WIDTH, HEIGHT)

oled.fill(0)
def ReadCommand(cmd):
    global oled
    OPCODE = (re.search(r'^(\S*)', cmd)).group(1)
    if OPCODE == "CLEAR":
        oled.fill(0)
        oled.show()
    elif OPCODE == "WRITE":
        pattern = '^(\S*) \"(.*)\" ([0-9]*) ([0-9]*) ([0-9]*)$'
        instruction = re.search(pattern, cmd)
        strToPrint = instruction.group(2)
        size = int(instruction.group(3))
        pos_x = int(instruction.group(4))
        pos_y = int(instruction.group(5))
        ui.writeTextWrap(strToPrint, size, pos_x, pos_y)
        oled.show()
        
command = ''
while True:
    if bt.any():
        char = ''.join(map(chr, bt.readline()))
        
        if char!= '\n':
            command += char
        else:        
            ReadCommand(command)
            command = ''