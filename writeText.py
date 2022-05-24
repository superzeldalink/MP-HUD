from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_12, ubuntu_mono_15, ubuntu_mono_20
import utime
 
WIDTH =128
HEIGHT= 64
i2c=I2C(0,scl=Pin(1),sda=Pin(0),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

def writeText(string, size, x, y):
    global oled
    if size <= 12:
        writeF = Write(oled, ubuntu_mono_12)
    elif size <= 15:
        writeF = Write(oled, ubuntu_mono_15)
    elif size <= 20:
        writeF = Write(oled, ubuntu_mono_20)
    writeF.text(string, x, y)

writeText("Hello", 12, 0, 0)

oled.show()