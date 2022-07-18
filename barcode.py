from evdev import InputDevice, ecodes, list_devices, categorize
import signal, sys
import csv
import pandas as pd
import time
import RPi.GPIO as GPIO
import time

but_pin = 15
but_pin2 = 16  

def button_pressed(channel):
    if not GPIO.input(channel):
        print("button 1 pressed.....")
        clear_all('/home/phawit/Documents/x1/static/current_barcode.csv')

def button_pressed2(channel):
    if not GPIO.input(channel):
        print("button 2 pressed.....")
        delete_last_line('/home/phawit/Documents/x1/static/current_barcode.csv')

def append_line(path,barcode):
    f = open(path, "r+")
    lines = f.readlines()
    lines.append(barcode)   #------
    lines = [x.strip('\n') for x in lines]
    lines = [x+'\n' for x in lines]
    if lines:
        lines[-1] = lines[-1].strip('\n')
    f = open(path, "w+")
    f.writelines(lines)
    f.close()

def delete_last_line(path):
    f = open(path, "r+")
    lines = f.readlines()
    lines.pop()   #------
    lines = [x.strip('\n') for x in lines]
    lines = [x+'\n' for x in lines]
    if lines:
        lines[-1] = lines[-1].strip('\n')
    f = open(path, "w+")
    f.writelines(lines)
    f.close()
    
def clear_all(path):
    f = open(path, "w")
    f.truncate()
    f.close()

def ok_barcode():
    Barcodes = getBarcodeFromCsv('/home/phawit/Documents/x1/static/current_barcode.csv')
    df_products = pd.read_csv('/home/phawit/Documents/x1/static/products.csv')
    df_customers = pd.read_csv('/home/phawit/Documents/x1/static/customers.csv')
    ok_barcode = list(df_products['barcode']) + list(df_customers['id'])
    ok_barcode = [str(x) for x in ok_barcode]
    # print(len(ok_barcode))
    # print(ok_barcode)

    return ok_barcode

def getBarcodeFromCsv(filename):
    file = open(filename)
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row[0])
    file.close()
    return rows

def signal_handler(signal, frame):
    print('Stopping')
    dev.ungrab()
    sys.exit(0)

# def write_csv(filename,barcode):
#     f = open(filename, "a")
#     f.write(str(barcode))
#     f.close()
def write_csv(file_name, text_to_append):
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)

devices = map(InputDevice, list_devices())
barcode_devices = ['Symbol Technologies, Inc, 2008 Symbol Bar Code Scanner','TMS HIDKeyBoard']

#time.sleep(10)
#append_line('/home/phawit/Documents/x1/static/current_barcode.csv','start')
# dev = False

dev = None
while not dev:
    for device in devices:
        print(device.name)
        if device.name in barcode_devices:
            print(device.name)
            dev = InputDevice(device.path)
        time.sleep(2)

signal.signal(signal.SIGINT, signal_handler)
barcode = ""
keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

GPIO.setmode(GPIO.BOARD)  #number onboard  
GPIO.setup(but_pin, GPIO.IN) 
GPIO.setup(but_pin2, GPIO.IN)  
GPIO.add_event_detect(but_pin, GPIO.FALLING, callback=button_pressed, bouncetime=100)
GPIO.add_event_detect(but_pin2, GPIO.FALLING, callback=button_pressed2, bouncetime=100)
print("Starting demo now! Press CTRL+C to exit")

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        data = categorize(event)
        if data.keystate == 1 and data.scancode != 42: # Catch only keydown, and not Enter
            if data.scancode == 28:
                barcode = barcode.replace('X','')
                if barcode in ok_barcode():
                    print('okkkkk',barcode)
                    append_line('/home/phawit/Documents/x1/static/current_barcode.csv',barcode)
                    # write_csv('static/current_barcode.csv',barcode)
                elif barcode in ['8851013793296']:
                    delete_last_line('/home/phawit/Documents/x1/static/current_barcode.csv')
                elif barcode in ['8991001502926']:
                    clear_all('/home/phawit/Documents/x1/static/current_barcode.csv')

                barcode = ""
        else:
            barcode += keys[data.scancode]

print('xxxxx')










# keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
# scancodes = {
#     # Scancode: ASCIICode
#     0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
#     10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
#     20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
#     30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
#     40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
#     50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
# }
# barCodeDeviceString = "TMS HIDKeyBoard"
#
# devices = map(InputDevice, list_devices())
# print('xxxx')
# for device in devices:
# 	print(device.name)
    # if device.name == barCodeDeviceString:
    # 	print(device.name)
        # dev = InputDevice(device.path)

#
# def signal_handler(signal, frame):
#     print('Stopping')
#     dev.ungrab()
#     sys.exit(0)
#
# signal.signal(signal.SIGINT, signal_handler)
#
# dev.grab()
#
# barcode = ""
# for event in dev.read_loop():
#     if event.type == ecodes.EV_KEY:
#         data = categorize(event)
#         if data.keystate == 1 and data.scancode != 42: # Catch only keydown, and not Enter
# 			if data.scancode == 28:
# 				print('bbb',type(barcode),barcode)
# 				write_csv('data/current_barcode.csv',barcode)
# 				#file_object = open('current_barcode.csv','a')
# 				#file_object.write(barcode)
# 				#file_object.close()
#
# 				barcode = ""
#         else:
#             barcode += keys[data.scancode]
