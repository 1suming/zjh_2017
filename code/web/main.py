# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import time,json,hashlib
import random
from datetime import datetime,date
from flask import Flask,request
from config import config
from ..config import var
from ..db.connect import *
from ..db.order import *

app = Flask(__name__)
app.config.from_object(config.DevConfig)
session = Session()
@app.route('/')
def home():
    return '<h1>hello world!</h1>'

@app.route('/pay_result', methods=['POST'])
def pay_result():
    data = json.dumps(request.form['data'])
    sign = request.form['sign']

    if get_sign(request.form['data']) != sign:
        return json.dumps({
            'status':'FAIL'
        })

    order = session.query(TOrder).filter(TOrder.order_sn == data['cp_order_sn']).first()
    if order == None:
        return json.dumps({
            'status':'FAIL'
        })
    if order.money != int((float(data['money']) * 100)):
        return json.dumps({
            'status':'FAIL'
        })


    return json.dumps({
        'status':'SUCCESS'
    })

def get_sign(data):
    callback = var.PAY_RESULT_URL
    cp_key = var.CP_KEY
    return hashlib.md5(callback+data+cp_key).hexdigest()


if __name__ == '__main__':
    # Entry the application
    app.run()