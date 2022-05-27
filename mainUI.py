from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import UILib as ui
import utime

WIDTH  = 128 # SSD1306 horizontal resolution
HEIGHT = 64   # SSD1306 vertical resolution

i2c = I2C(1,scl=Pin(3),sda=Pin(2),freq=200000)  # start I2C on I2C1 (GPIO 26/27)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c) # oled controller

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

rtc = machine.RTC()
rtc.datetime((2022, 5, 27, 5, 11, 04, 59, 0))

ui.initUI(oled, WIDTH, HEIGHT)

def FormatDate(datetime):
    day = str(datetime[2])
    year = str(datetime[0])
    date = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday"
    }
    
    
    month = {
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
       
    output = "{} {} {}".format(day ,month.get(datetime[1]), year)

    return output


while True:
    oled.fill(0)
    ui.writeText("Welcome to MP-HUD")
    ui.printGraphic(buffer, 32, 32, pos_x=0)

    time = rtc.datetime()
    ui.writeText( "{:02d}:{:02d}".format(time[4],time[5]), 20, 40,16)
    ui.writeText( ":{:02d}".format(time[6]), 8, 91,22)
    ui.writeText(FormatDate(time), 5, 38,38)

    # Send the FrameBuffer content to the LCD
    oled.show()