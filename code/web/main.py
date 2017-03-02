# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import json,sys,redis,time,os
import hashlib

from flask import Flask,request,render_template,redirect, url_for,jsonify
from werkzeug import secure_filename
# from os.path import join, dirname, realpath


from conf import DevConfig
# from config.var import *
from db.connect import *
from db.order import *
from db.mail import *
from db.bag_item import *
from db.charge_item import *
from db.mail import *
from db.reward_user_log import *
from db.customer_service_log import *
from db.user import *
# from hall.hallobject import *
from helper import datehelper
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

UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
REAL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        file = request.files['file']
        uid = request.form['uid']
        device_id = request.form['device_id']

        if file == None or uid == None or device_id == None:
            return jsonify(result=0,message='error,file or uid or device_id is empty!')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(REAL_PATH, uid+'_'+device_id+'_'+filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            full_filename ='/'+uid+'_'+device_id+'_'+filename
            path_url = request.url_root+app.config['UPLOAD_FOLDER']+full_filename


            result = session.query(TUser).filter(TUser.id == uid).filter(TUser.id == int(uid)).update({
                TUser.avatar:path_url
            })



            if result > 0:
                # 修改头像换缓存
                if r.exists('u'+str(uid)):
                    r.hset('u'+str(uid), 'avatar', path_url)

                # 记录完成头像任务
                task_log = session.query(TRewardUserLog).filter(and_(TRewardUserLog.uid == uid,TRewardUserLog.task_id == 10)).first()
                if task_log is None:
                    task_log = TRewardUserLog()
                    task_log.uid = uid
                    task_log.task_id = 10 # 修改任务头像id
                    task_log.state = 1 # 1=已完成，未领取 。 0 = 已完成，已领取。 其他 = 未完成
                    task_log.create_time = datehelper.get_today_str()
                    session.add(task_log)

                return jsonify(result=0,message='success,message:'+full_filename+',path:'+path_url,url=path_url)
            return jsonify(result=-1,message='error:upload return false')
            # if execute(conn, "UPDATE `user` SET `avatar` = '%s' WHERE `id`=%d" % (path_url, int(uid))):
            #     return jsonify(result=0,message='success,message:'+full_filename+',path:'+path_url,url=path_url)
            # return jsonify(result=-1,message='error:upload return false')
            #return jsonify(rr=0,mm='success,message:'+full_filename+',path:'+path_url,uu=path_url)

    pathDir =  os.listdir(REAL_PATH)
    html = ''
    for allDir in pathDir:
        # child = os.path.join('%s%s' % (REAL_PATH, allDir))
        html +='<li><a href="'+request.url_root+UPLOAD_FOLDER+'/'+allDir+'">'+request.url_root+UPLOAD_FOLDER+'/'+allDir+'</a></li>'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <input type=text name=uid placeholder=uid>
      <input type=text name=device_id placeholder=device_id>
         <input type=submit value=Upload>
    </form>
    <ol>
    %s
    </ol>
    ''' % html
# ''' % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))










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



    if r.exists('u'+str(order.uid)):
        r.delete('u'+str(order.uid))

    user_info = session.query(TUser).filter(TUser.id == order.uid, TUser.is_charge == 0).first()
    if user_info.is_charge == 0:
        session.query(TUser).with_lockmode("update").filter(TUser.id == order.uid, TUser.is_charge == 0).update({
            TUser.is_charge:1,
            TUser.gold:TUser.gold+300000,
            TUser.gold:TUser.diamond+10
        })
    # 1	horn	大喇叭	可以公开喊话	2017-02-14 15:33:01
    # 2	kick	踢人卡	奖玩家踢出房间	2017-02-14 15:35:02
    # 3	exp_1	经验卡1点	使用后获得1点VIP经验	2017-02-15 10:43:51
    # 4	exp_10	经验卡10点	使用后获得10点VIP经验	2017-02-15 11:15:49
    # 5	tgold	金币名称	金币介绍	2017-02-15 16:57:49
    # 大喇叭 10
        save_countof(session, {
            'uid':order.uid,
            'stuff_id':1,
            'countof':10,
        })
        # 踢人卡 10
        save_countof(session, {
            'uid':order.uid,
            'stuff_id':2,
            'countof':10,
        })
        # 经验卡10点
        save_countof(session, {
            'uid':order.uid,
            'stuff_id':4,
            'countof':1,
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


def save_countof(session, fields):
    insert_stmt = "INSERT INTO bag_item(uid,item_id,countof) VALUES (:col_1,:col_2,:col_3) ON DUPLICATE KEY UPDATE countof = countof + :col_3;"
    session.execute(insert_stmt, {
        'col_1':fields['uid'],
        'col_2':fields['stuff_id'],
        'col_3':fields['countof']
    })
    session.flush()

if __name__ == '__main__':
    # Entry the application
    app.run()