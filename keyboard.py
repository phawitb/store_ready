from pynput import keyboard
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
# from datetime import datetime
from datetime import datetime, timezone, timedelta

cred = credentials.Certificate('/home/phawit/Documents/x1/store2020-bca76-firebase-adminsdk-ilrdw-d7644136e0.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

ref = db.collection(u'setup').document(f'shortcut')
Shortcut = ref.get().to_dict()

key_release = []
press_time = []

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

def on_press(key):
    global key_release,press_time,Shortcut
    if press_time:
        if time.time()-press_time[-1] > 3:
            key_release = []
            press_time = []

    try:
        key = key.char
    except:
        pass

    if str(key) == 'Key.enter':
        short_cut = ''
        if len(key_release) == 2:
            if press_time[-1]-press_time[-2] < 3:
                # print('okkk',key_release[-2],key_release[-1])
                short_cut = key_release[-2]+key_release[-1]
        elif len(key_release) == 1:
            # print('okkk',key_release[-1])
            short_cut = key_release[-1]

        if short_cut:
            # Shortcut = {'1': '1286451229164', '2': '1628418596595', '3': '1839931803770'}
            print('short_cut',short_cut,type(short_cut))
            if short_cut in Shortcut.keys():
                barcode = Shortcut[short_cut]
                append_line('/home/phawit/Documents/x1/static/current_barcode.csv',barcode)



        key_release = []
        press_time = []

def on_release(key):
    global key_release,press_time

    try:
        key = str(key).split("'")[1]
        if key.isdigit():
            key_release.append(key)
            press_time.append(time.time())

        elif key == '-':
            delete_last_line('/home/phawit/Documents/x1/static/current_barcode.csv')
            print('------')
            
    except:
        if str(key) == '<65437>':
            key_release.append('5')
            press_time.append(time.time())
    
# Collect events until released
with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()


