from machine import Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import UILib as ui
import utime
import _thread
import gc
import uzlib

WIDTH = 128  # SSD1306 horizontal resolution
HEIGHT = 64   # SSD1306 vertical resolution

# start I2C on I2C1 (GPIO 26/27)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)  # oled controller

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

rtc = machine.RTC()

ui.initUI(oled, WIDTH, HEIGHT)

lock = _thread.allocate_lock()

executing = False


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
    output = "{} {} {}".format(day, monthText.get(month), year)
    return output


oled.fill(0)

# MODES
# -1: WAIT FOR CONNECT
# 0: HOME
# 1: TEXT
mode = -1


def ReadCommand(bytes):
    global oled, mode
    executing = True
    opcode = int.from_bytes(bytes[:1], "big")
    if opcode == 0:
        mode = 1
        oled.fill(0)
        oled.show()
    elif opcode == 1:
        year = int.from_bytes(bytes[1:2], "big")
        month = int.from_bytes(bytes[2:3], "big")
        day = int.from_bytes(bytes[3:4], "big")
        date = int.from_bytes(bytes[4:5], "big")
        hour = int.from_bytes(bytes[5:6], "big")
        minute = int.from_bytes(bytes[6:7], "big")
        rtc.datetime((year, month, day, date, hour, minute, second, 0))
    elif opcode == 2:
        mode = 0
    elif opcode == 3:
        width = int.from_bytes(bytes[1:2], "big")
        height = int.from_bytes(bytes[2:3], "big")
        pos_x = int.from_bytes(bytes[3:4], "big")
        pos_y = int.from_bytes(bytes[4:5], "big")
        
        zlib = bytes[5:]
        imageData = uzlib.decompress(zlib)
        ui.printGraphic(imageData, width, height, pos_x, pos_y)
        oled.show()
    elif opcode == 4:
        oled.fill(0)
        size = int.from_bytes(bytes[1:2], "big")
        pos_x = int.from_bytes(bytes[2:3], "big")
        pos_y = int.from_bytes(bytes[3:4], "big")
        
        strToPrint = bytes[4:].decode("utf-8")

        ui.writeTextWrap(strToPrint, size, pos_x, pos_y)
        oled.show()
        
    utime.sleep(0.01)

def Print():
    global mode
    while True:
        try:
            if mode == -1:
                oled.fill(0)
                ui.writeTextWrap("Waiting for connection...")
                oled.show()
            elif mode == 0:
                oled.fill(0)
                ui.writeText("Welcome to MP-HUD")
                ui.printGraphic(buffer, 32, 32, pos_x=0)

                time = rtc.datetime()
                ui.writeText("{:02d}:{:02d}".format(time[4], time[5]), 20, 40, 16)
                ui.writeText(":{:02d}".format(time[6]), 8, 91, 22)
                ui.writeText(FormatDate(time[0], time[1], time[2]), 5, 38, 38)
                
                oled.show()
        
        except Exception as e:
            bt.write("E\r\n")
        utime.sleep(0.1)
        gc.collect()
        # print(gc.mem_free())


thread1 = _thread.start_new_thread(Print,())

bt = UART(0,9600,timeout=5, parity=None)
while True:
    if bt.any():
        received = bt.read()
        opcode = received[:1]
        
        try:
            ReadCommand(received)
        except Exception as e:
            bt.write("E\r\n")
    utime.sleep(0.01)
