from machine import Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import UILib as ui
import utime
import re
import _thread
import gc
import ubinascii
import uzlib

WIDTH  = 128 # SSD1306 horizontal resolution
HEIGHT = 64   # SSD1306 vertical resolution

i2c = I2C(1,scl=Pin(3),sda=Pin(2),freq=200000)  # start I2C on I2C1 (GPIO 26/27)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c) # oled controller

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

rtc = machine.RTC()
rtc.datetime((2022, 5, 27, 5, 13, 31, 59, 0))

ui.initUI(oled, WIDTH, HEIGHT)

lock = _thread.allocate_lock()

def FormatDate(year, month, day):
    monthText = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    output = "{} {} {}".format(day ,monthText.get(month), year)
    return output

oled.fill(0)

# MODES
# -1: WAIT FOR CONNECT
# 0: HOME
# 1: TEXT
mode = -1

def ReadCommand(cmd):
    global oled, mode
    cmdArgs = cmd.split(" ")
    OPCODE = cmdArgs[0]
    if OPCODE == "CLEAR":
        oled.fill(0)
        mode = 1
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
    elif OPCODE == "MODE":
        mode = int(cmdArgs[1])
    elif OPCODE == "SET":
        if cmdArgs[1] == "time":
            year = int(cmdArgs[2])
            month = int(cmdArgs[3])
            day = int(cmdArgs[4])
            date = int(cmdArgs[5])
            hour = int(cmdArgs[6])
            minute = int(cmdArgs[7])
            try: # There is a bug here. So I added this to prevent the bug appears :v
                second = int(cmdArgs[8])
            except:
                second = 0
            rtc.datetime((year, month, day, date, hour, minute, second, 0))
    elif OPCODE == "IMAGE":
        b64 = cmdArgs[1]
        width = int(cmdArgs[2])
        height = int(cmdArgs[3])
        pos_x = int(cmdArgs[4])
        pos_y = int(cmdArgs[5])
        
        zlib = ubinascii.a2b_base64(b64)
        imageData = uzlib.decompress(zlib)
        print(imageData)
        ui.printGraphic(imageData, width, height, pos_x, pos_y)
        oled.show()
            
cmdList = []

def Print():
    global mode
    while True:
        if mode == -1:
            oled.fill(0)
            ui.writeTextWrap("Waiting for connection...")
        elif mode == 0:
            oled.fill(0)
            ui.writeText("Welcome to MP-HUD")
            ui.printGraphic(buffer, 32, 32, pos_x=0)

            time = rtc.datetime()
            ui.writeText( "{:02d}:{:02d}".format(time[4],time[5]), 20, 40,16)
            ui.writeText( ":{:02d}".format(time[6]), 8, 91,22)
            ui.writeText(FormatDate(time[0], time[1], time[2]), 5, 38, 38)
            
        if len(cmdList) > 0:
            ReadCommand(cmdList[0])
            cmdList.pop(0)
            
        oled.show()
            
        utime.sleep(0.05)
        gc.collect()
        print(gc.mem_free())
                
            
thread1 = _thread.start_new_thread(Print,())

bt = UART(0,9600)
command = ''
while True:
    if bt.any():
        char = ''.join(map(chr, bt.readline()))
        
        if char != '\n':
            command += char
        else:
           print(command)
           cmdList.append(command)
           command = ''