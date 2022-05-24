from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf,sys

from oled.fonts import ubuntu_mono_12, ubuntu_mono_15, ubuntu_mono_20


WIDTH  = 128 # SSD1306 horizontal resolution
HEIGHT = 64   # SSD1306 vertical resolution

i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=200000)  # start I2C on I2C1 (GPIO 26/27)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c) # oled controller

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

def writeGraphic(buffer_byte, width, height, pos_x = None, pos_y = None):
    global WIDTH, HEIGHT
    fb = framebuf.FrameBuffer(buffer_byte, width, height, framebuf.MONO_HLSB)
    oled.fill(0)
    if pos_x == None:
        pos_x = int((WIDTH - width)/2)
    if pos_y == None:
        pos_y = int((HEIGHT - height)/2)
    oled.blit(fb, pos_x, pos_y)
    
# Finally update the oled display so the image & text is displayed
oled.show()
