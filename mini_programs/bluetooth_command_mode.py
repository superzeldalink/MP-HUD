# Press and hold -- button when power on for two seconds to enter command mode!

import uos
import machine
import utime

uart0 = machine.UART(0, baudrate=38400)

def sendCMD_waitResp(cmd, uart=uart0, timeout=5000):
    print("CMD: " + cmd)
    uart.write(cmd)
    waitResp(uart, timeout)
    print()
    
def waitResp(uart=uart0, timeout=5000):
    prvMills = utime.ticks_ms()
    resp = b""
    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])
    print("resp:")
    try:
        print(resp.decode())
    except UnicodeError:
        print(resp)
        
# send CMD to uart,
# wait and show response without return
def sendCMD_waitAndShow(cmd, uart=uart0):
    print("CMD: " + cmd)
    uart.write(cmd)
    while True:
        print(uart.readline())
        
sendCMD_waitResp('AT\r\n')

while True:
    print('Enter something:')
    msg = input()
    #sendCMD_waitResp('AT+CIPSTART="TCP","192.168.12.147",9999\r\n')
    sendCMD_waitResp(msg+'\r\n')