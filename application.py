from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep,time
from threading import Thread, Event
import csv
import base64
import pandas as pd  
#from promptpay import qrcode
from datetime import datetime
import json
import os
import io
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import urllib.request

__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, logger=True, engineio_logger=True)
thread = Thread()
thread_stop_event = Event()

cred = credentials.Certificate('/home/phawit/Documents/x1/store2020-bca76-firebase-adminsdk-ilrdw-d7644136e0.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

finish = False
status = ''

def clear_all(path):
    f = open(path, "w")
    f.truncate()
    f.close()

def create_table_history2(customer_id):
    ref = db.collection(u'customers').document(f'{customer_id}')
    c = ref.get().to_dict()
    items = [x.split('|') for x in c['history'].split('||')][:-1]
    if len(items)>10:
        items = items[-10:]
    return items


def create_table_history(customer_id):
  docs = db.collection(u'History').stream()
  data = []
  for doc in docs:
      data.append(doc.to_dict())

  h = []
  for d in data:
      for k in d.keys():
          for kk in d[k].keys():
              if customer_id == d[k][kk]['customer']:
  #                 print(k+kk,k,kk,d[k][kk]['customer'],d[k][kk]['total'])
                  h.append([k+kk,d[k][kk]['customer'],d[k][kk]['total'],d[k][kk]['balance']])
  #             print('---------')
              
  df_history = pd.DataFrame(h,columns=['date', 'name','total','balance'])
  df_history = df_history.sort_values(by=['date'])

  items = []
  for index, row in df_history.iterrows():
    # print(row['date'],row['total'],row['balance'])
    d = row['date']
    d = f'{d[6:8]}/{d[4:6]}/{d[:4]}-{d[8:10]}:{d[10:12]}'
    items.append([d,row['total'],row['balance']])
  return items

def getBarcodeFromCsv(filename):
    file = open(filename)
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row[0])
    file.close()
    return rows

def customer_detail(customer_id):
    ref = db.collection(u'customers').document(f'{customer_id}')
    return ref.get().to_dict()

def internet_connection():
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except:
        return False

def find_product_data(df,barcode):
    for i,b in enumerate(df['barcode']):
        if str(b) == str(barcode):
            return df['name'][i],df['price'][i]
    else:
        return None,None

def cut_same_barcode(a):
    x = []
    for i in a:
        if i not in x:
            x.append(i)
    return x

def save_history2(Historys,time_now,date_now):
    # time_now = datetime.now().strftime("%H%M%S%f")
    # date_now = datetime.now().strftime("%Y%m%d")

    print('Historys',Historys)

    if internet_connection():
        try:
            doc_ref = db.collection(u'History').document(u'sell')
            doc_ref.update({f'{str(date_now)}.{str(time_now)}': Historys})
            return 'complete'
        except:
            return 'notconnectfb'
            
    else:
        return 'nointernet'

def update_balace(customer_id,money,time_now,date_now):
    ref = db.collection(u'customers').document(f'{customer_id}')
    c = ref.get().to_dict()
    c['balance'] = int(c['balance']) + money

    h = f"{date_now[6:]}/{date_now[4:6]}/{date_now[:4]}-{time_now[:2]}:{time_now[2:4]}:{time_now[4:6]}|{money}|{c['balance']}||"
    if 'history' in c.keys():
        c['history'] = c['history'] + h
    else:
        c['history'] = h
    
    ref.set(c)

    return c['balance']

def update_df_customers():
    data = []
    docs = db.collection(u'customers').stream()
    for doc in docs:
        print(f"{doc.id} => {doc.to_dict()['name']}")
        data.append([doc.id,doc.to_dict()['name']])
    df_customers = pd.DataFrame((data),columns=['id', 'name'])
    return df_customers

def update_df_products():
    data = []
    docs = db.collection(u'products').stream()
    for doc in docs:
        print(f"{doc.id} => {doc.to_dict()['name']}")
        data.append([doc.id,doc.to_dict()['name'],doc.to_dict()['price']])
    df_customers = pd.DataFrame((data),columns=['barcode','name','price'])
    return df_customers




if internet_connection():
    df_customers = update_df_customers()
    df_products = update_df_products()
    df_customers.to_csv('/home/phawit/Documents/x1/static/customers.csv',index=False)
    df_products.to_csv('/home/phawit/Documents/x1/static/products.csv',index=False)

df_customers = pd.read_csv('/home/phawit/Documents/x1/static/customers.csv')
df_products = pd.read_csv('/home/phawit/Documents/x1/static/products.csv')
df_customers['id'] = [str(x) for x in list(df_customers['id'])]
df_products['barcode'] = [str(x) for x in list(df_products['barcode'])]

clear_all('/home/phawit/Documents/x1/static/current_barcode.csv')
Barcodes = getBarcodeFromCsv('/home/phawit/Documents/x1/static/current_barcode.csv')
start = time()

def randomNumberGenerator():
    global finish,df_customers,df_products,status,Barcodes,start

    while not thread_stop_event.isSet():

        # df_customers = pd.read_csv('/home/phawit/Documents/x1/static/customers.csv')
        # df_products = pd.read_csv('/home/phawit/Documents/x1/static/products.csv')
        # df_customers['id'] = [str(x) for x in list(df_customers['id'])]
        # df_products['barcode'] = [str(x) for x in list(df_products['barcode'])]
        
        if status == 'no internet':
            sleep(5)
            clear_all('/home/phawit/Documents/x1/static/current_barcode.csv')




        if finish:
            
            f = open('/home/phawit/Documents/x1/static/current_barcode.csv', "w")
            f.truncate()
            f.close()

            #df_customers = update_df_customers()
            #df_products = update_df_products()
            #df_customers.to_csv('/home/phawit/Documents/x1/static/customers.csv',index=False)
            #df_products.to_csv('/home/phawit/Documents/x1/static/products.csv',index=False)

            finish = False
            sleep(5)

        
        if Barcodes != getBarcodeFromCsv('/home/phawit/Documents/x1/static/current_barcode.csv'):
            start = time()
        else:
            if time()-start > 30:
                if Barcodes:
                    clear_all('/home/phawit/Documents/x1/static/current_barcode.csv')
                start = time()


        Barcodes = getBarcodeFromCsv('/home/phawit/Documents/x1/static/current_barcode.csv')


        products_barcode = []
        rcustomer_barcode = []
        for i in Barcodes:
            if i in list(df_products['barcode']):
                products_barcode.append(i)
            if i in list(df_customers['id']):
                rcustomer_barcode.append(i)
            

        customer_barcode = ''
        if products_barcode and Barcodes[-1] in list(df_customers['id']):
            customer_barcode = Barcodes[-1]

        if not products_barcode and not rcustomer_barcode:
            Total = 'Welcome!'
            items = []
            status = 'scan your products'
            customer = 'Signalschool'
            with open("/home/phawit/Documents/x1/static/start.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

            print('Barcodes----------------------------------------------------',Barcodes)

            print('*-*-'*100,list(df_customers['id']))

        # if len(Barcodes) == 1:
        if not products_barcode and Barcodes and status != 'show history data':
            if Barcodes[-1] in list(df_customers['id']) and internet_connection():
                custom = customer_detail(Barcodes[-1])
                customer = custom['name'] + ' : ' + str(custom['balance'])
                status = 'show history data'

                items = create_table_history2(Barcodes[-1])
                Total = 'Balance : '+str(custom['balance'])
            else:
                status = 'no internet'


        if products_barcode:
            items = []
            total = 0
            status = 'Scan for payment'
            df = pd.read_csv('/home/phawit/Documents/x1/static/products.csv')

            with open("/home/phawit/Documents/x1/static/scanforpay.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

            Historys = {}
            for i,barcode in enumerate(cut_same_barcode(products_barcode)):
                # print(barcode)
                product_name,price = find_product_data(df,barcode)
                # print(product_name,price)
                amount = Barcodes.count(barcode)
                # print(barcode,amount,product_name,price)
                # print(price,type(price))
                items.append([product_name,str(amount),str(price*amount)])
                total += int(price*amount)
                
                Historys[str(i)] = {
                    
                    'barcode' : barcode,
                    'name' : product_name,
                    'price' : int(price),
                    'amount' : int(amount),
                    'total' : int(price*amount)

                } 
            Historys['total'] = int(total)*-1
            Historys['customer'] = customer_barcode

            Total = f'Total {total}'

            if customer_barcode:
                if internet_connection():
                    custom = customer_detail(customer_barcode)
                    customer = custom['name'] + ' : ' + str(custom['balance'])
                    # customer = custom['name'] + ' : ' + str(custom['balance'])
                    #print('ccc'*1000)
                    if int(custom['balance']) > total:
                        time_now = datetime.now().strftime("%H%M%S%f")
                        date_now = datetime.now().strftime("%Y%m%d")
                        balance = update_balace(customer_barcode,total*-1,time_now,date_now)
                        Historys['balance'] = balance
                        sta = save_history2(Historys,time_now,date_now)
                        if sta == 'complete':
                            with open("/home/phawit/Documents/x1/static/finish.png", "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())
                            # balance = update_balace(customer_barcode,total*-1)
                            Total = f'Finish balace : {balance} $'
                            finish = True
                        else:
                            status = 'no internet'

                    else:
                        status = 'not enought money'

                else:
                    #print('ddd'*1000)
                    status = 'no internet'



            

        

        
        customer_barcode = list(df_customers['id'])[0]

        socketio.emit('newnumber', {'total': Total,'items': items,'qr':encoded_string.decode("utf-8"),'status':status,'customer':customer}, namespace='/test')
        socketio.sleep(1)



@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
