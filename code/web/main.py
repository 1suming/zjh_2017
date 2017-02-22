# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import json,sys,redis
import hashlib

from flask import Flask,request
from conf import DevConfig


#from config.var import *
from db.connect import *
from db.order import *


app = Flask(__name__)
app.config.from_object(DevConfig)
session = Session()
@app.route('/')
def home():
    return '<h1>hello world!</h1>'

@app.route('/pay_result', methods=['POST'])
def pay_result():
    data = json.loads(request.form['data'])
    sign = request.form['sign']
    print '===============>0'
    print data
    print '==============>1',get_sign(request.form['data']),sign
    if get_sign(request.form['data']) != sign:
        return json.dumps({
            'status':'FAIL'
        })
    print '==============>2'
    # order = session.query(TOrder).filter(TOrder.order_sn == data['cp_order_sn']).first()
    order = session.query(TOrder).filter(TOrder.order_sn == data['private']).first()
    if order == None:
        return json.dumps({
            'status':'FAIL'
        })

    print '==============>3'
    charge_money = float(data['money'])
    # 充值金额相等时
    status = 0
    if int(order.money * 100) != int(charge_money * 100):
        # 充值金额不相等时
        status = 1
    print '======================>4',order.money,charge_money,int(order.money * 100) != int(charge_money * 100)
    session.query(TOrder).filter(TOrder.order_sn == data['private']).update({
        TOrder.sdk_order_sn:data['order_sn'],
        TOrder.charge:charge_money,
        TOrder.status:status
    })

    data['uid'] = order.uid
    print '======================>5',data
    r = redis.Redis(host='121.201.29.89',port=26379,db=0,password='Wgc@123456')
    r.lpush('queue_charge', json.dumps(data))


    print 'status, success'
    return json.dumps({
        'status':'SUCCESS'
    })

def get_sign(data):
    # callback = PAY_RESULT_URL
    # cp_key = CP_KEY
    callback = 'http://121.201.29.89:18000/pay_result'
    cp_key = 'bde25760c1556899efc0dff13bf41b4e'
    return hashlib.md5(callback+data+cp_key).hexdigest()


if __name__ == '__main__':
    # Entry the application
    app.run()