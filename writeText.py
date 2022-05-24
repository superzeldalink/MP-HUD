from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_12, ubuntu_mono_15, ubuntu_mono_20
 
WIDTH =128
HEIGHT= 64
i2c=I2C(0,scl=Pin(1),sda=Pin(0),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

def writeText(str, size, pos_x, pos_y):
    global oled
    if size <= 12:
        writeF = Write(oled, ubuntu_mono_12)
    elif size <= 15:
        writeF = Write(oled, ubuntu_mono_15)
    else:
        writeF = Write(oled, ubuntu_mono_20)
    writeF.text(str, pos_x, pos_y)

def writeTextWrap(str, size, pos_x, pos_y, width = WIDTH, height = 100):
    if size <= 12: size = 12
    elif size <= 15: size = 15
    else: size = 20
        
    strings = str.split(' ')
    strToPrint = ""
    line = 0
    for i in range(len(strings)):
        if pos_x + len(strToPrint + strings[i])*size/2 <= width:
            strToPrint += strings[i] + " "
            if i < len(strings) - 1:
                continue
        
        writeText(strToPrint, size, pos_x, pos_y + line*size)
        strToPrint = strings[i] + " "
        line += 1
        if i < len(strings):
            writeText(strToPrint, size, pos_x, pos_y + line*size)
        if line*size > height:
            break

writeTextWrap("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.", 12, 0, 0)

oled.show()