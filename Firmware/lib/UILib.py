from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from oled import Write
from oled.fonts import ubuntu_mono_12, ubuntu_mono_15, ubuntu_mono_20
import framebuf,sys

WIDTH, HEIGHT = 128, 64
oled = None

def initUI(_oled, width, height):
    global oled, WIDTH, HEIGHT
    
    oled = _oled
    WIDTH = width
    HEIGHT = height

def writeText(string, size = 12, pos_x = 0, pos_y = 0):
    global oled
    if size <= 12:
        writeF = Write(oled, ubuntu_mono_12)
    elif size <= 15:
        writeF = Write(oled, ubuntu_mono_15)
    else:
        writeF = Write(oled, ubuntu_mono_20)
    writeF.text(string, pos_x, pos_y)

def writeTextWrap(string, size = 12, pos_x = 0, pos_y = 0, width = WIDTH, height = 100):
    if size <= 12: size = 12
    elif size <= 15: size = 15
    else: size = 20
        
    strings = string.split(' ')
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

def printGraphic(buffer_byte, width, height, pos_x = None, pos_y = None):
    global WIDTH, HEIGHT
    fb = framebuf.FrameBuffer(buffer_byte, width, height, framebuf.MONO_HLSB)
    if pos_x == None:
        pos_x = int((WIDTH - width)/2)
    if pos_y == None:
        pos_y = int((HEIGHT - height)/2)
    oled.blit(fb, pos_x, pos_y)