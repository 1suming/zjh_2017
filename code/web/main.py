# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import json,sys,redis,time
import hashlib

from flask import Flask,request,render_template,redirect
from conf import DevConfig


#from config.var import *
from db.connect import *
from db.order import *
from db.mail import *
from db.charge_item import *
from db.mail import *
from db.customer_service_log import *
from db.user import *
from sqlalchemy import and_
from sqlalchemy.sql import desc

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config.from_object(DevConfig)
session = Session()
r = redis.Redis(host='121.201.29.89',port=26379,db=0,password='Wgc@123456')

# CPID：jjcq20170223_141_312
# CPKEY：d5ff856beccf4c472831c3f16c376e28
CALLBACK = 'http://121.201.29.89:18000/pay_result'
# CP_KEY = 'd5ff856beccf4c472831c3f16c376e28'
CHARGE_KEY = 'cqkj2017'
CP_KEY = 'bde25760c1556899efc0dff13bf41b4e'

@app.route('/')
def home():
    return '<h1>hello world!</h1>'

@app.route('/customer')
def customer():
    items = session.query(TCustomerServiceLog).order_by(desc(TCustomerServiceLog.send_time)).limit(20)
    for item in items:
        key = 'u'+str(item.from_user)
        user_info = r.hgetall(key)
        print '============>'
        print user_info
        item.from_user_nick = user_info.get('nick')
        item.from_user_avatar = user_info.get('avatar')
    return render_template('customer.html',items = items)



@app.route('/pay_result', methods=['POST'])
def pay_result():
    data = json.loads(request.form['data'])
    sign = request.form['sign']

    data['private'] = json.loads(data['private'])
    print '===============>0'
    print data

    print '===============>0.5'
    print data['private']['privateInfo'],get_md5(data['private']['order']+CHARGE_KEY+data['private']['other'])
    # 校验
    if data['private']['privateInfo'] != get_md5(data['private']['order']+CHARGE_KEY+data['private']['other']):
        return json.dumps({
            'status':'FAIL'
        })


    print '==============>1',get_sign(request.form['data']),sign
    if get_sign(request.form['data']) != sign:
        return json.dumps({
            'status':'FAIL'
        })
    print '==============>2'

    order = session.query(TOrder).filter(and_(TOrder.order_sn == data['private']['order'], TOrder.uid == data['private']['other'])).first()
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
    session.query(TOrder).filter(TOrder.order_sn == data['private']['order']).update({
        TOrder.sdk_order_sn:data['order_sn'],
        TOrder.charge:charge_money,
        TOrder.status:status
    })

    data['uid'] = order.uid
    print '======================>5',data

    shop_item = session.query(TChargeItem).filter(TChargeItem.id == order.shop_id).first()

    mail = TMail()
    mail.from_user = 10000
    mail.to_user = order.uid
    mail.sent_time = time.time()
    mail.title = u'充值'
    mail.content = u'成功充值 %.2f 元' % (charge_money)
    if shop_item.type == 'gold':
        mail.content += u'，购买 %d 金币' % (shop_item.gold)
    if shop_item.type == 'diamond':
        mail.content += u'，购买 %d 个钻石' % (shop_item.diamond)
    mail.type = 0
    mail.diamond = 0
    mail.gold = 0
    mail.state = 1
    session.add(mail)
    session.flush()

    session.query(TUser).with_lockmode("update").filter(TUser.id == order.uid).update({
        TUser.is_charge:1
    })

    # r = redis.Redis(host='121.201.29.89',port=26379,db=0,password='Wgc@123456')
    # r.lpush('queue_charge', {'order_sn':data['private']['order'],'gold':shop_item.gold,'diamond':shop_item.diamond})


    print 'status, success'
    return json.dumps({
        'status':'SUCCESS'
    })

def get_sign(data):
    return hashlib.md5(CALLBACK+data+CP_KEY).hexdigest()

def get_md5(s):
    return hashlib.md5(s).hexdigest()

if __name__ == '__main__':
    # Entry the application
    app.run()