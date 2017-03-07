# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import json,sys,redis,time,os,os.path,decimal
import hashlib
import zipfile

from flask import Flask,request,render_template,redirect, url_for,jsonify
from werkzeug import secure_filename

from conf import DevConfig


from helper import datehelper
from sqlalchemy import and_
from sqlalchemy.sql import desc


# reload(sys)
# sys.setdefaultencoding('utf-8')

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
QUICK_CHARGE = [
    # 分，万，商品名称
    (500, 15, u'新手场', 1),
    (3000, 90, u'普通场', 1),
    (15000, 450, u'高级场', 1),
    (60000, 1800, u'大师场', 1),
]

# 首冲
FRIST_CHARGE = {
    'title':u'首充',
    'money' : 6100,
    'real_money':1,
    'diamond' : 10,
    'gold' : 30, # 单位w
    'hore' : 10,
    'kicking_card':10,
    'vip_card' :1,
}
VIP_CONF = [
        {'id':0,'level':0,'friend_max':5, 'charge':0,'sign_reward':0,'kick_card':0,'horn_card':1,'relief_time':2,'relief_good':10000, 'bank_max':0,'nick_color':'white','auth':[]},
        {'id':76,'level':1,'friend_max':10, 'charge':20,'sign_reward':0.5,'kick_card':0,'horn_card':2,'relief_time':3,'relief_good':10000, 'bank_max':500000,'nick_color':'green','auth':['handle_trade_buy']},
        {'id':77,'level':2,'friend_max':20, 'charge':60,'sign_reward':1,'kick_card':0,'horn_card':3,'relief_time':4,'relief_good':10000, 'bank_max':2000000,'nick_color':'green','auth':['handle_trade_buy','handle_sell_gold']},
        {'id':78,'level':3,'friend_max':30, 'charge':100,'sign_reward':2,'kick_card':3,'horn_card':5,'relief_time':4,'relief_good':10000, 'bank_max':5000000,'nick_color':'blue','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
        {'id':79,'level':4,'friend_max':40, 'charge':200,'sign_reward':3,'kick_card':4,'horn_card':10,'relief_time':5,'relief_good':10000, 'bank_max':20000000,'nick_color':'blue','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
        {'id':80,'level':5,'friend_max':50, 'charge':500,'sign_reward':4,'kick_card':5,'horn_card':15,'relief_time':5,'relief_good':10000, 'bank_max':50000000,'nick_color':'yellow','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
        {'id':81,'level':6,'friend_max':60, 'charge':1000,'sign_reward':5,'kick_card':6,'horn_card':20,'relief_time':6,'relief_good':10000, 'bank_max':100000000,'nick_color':'yellow','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
        {'id':82,'level':7,'friend_max':70, 'charge':2000,'sign_reward':6,'kick_card':7,'horn_card':25,'relief_time':6,'relief_good':10000, 'bank_max':200000000,'nick_color':'red','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
        {'id':83,'level':8,'friend_max':80, 'charge':5000,'sign_reward':7,'kick_card':8,'horn_card':30,'relief_time':8,'relief_good':10000, 'bank_max':500000000,'nick_color':'red','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
        {'id':84,'level':9,'friend_max':90, 'charge':10000,'sign_reward':8,'kick_card':9,'horn_card':35,'relief_time':8,'relief_good':10000, 'bank_max':1000000000,'nick_color':'purple','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
        {'id':85,'level':10,'friend_max':100, 'charge':20000,'sign_reward':9,'kick_card':10,'horn_card':40,'relief_time':10,'relief_good':10000, 'bank_max':2000000000,'nick_color':'purple','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
    ]
VIP_UP=u'玩家%s一掷千金，成功升级为%s，成为人生赢家！(VIP1+)'
UPLOAD_FOLDER = 'static/upload'
UPGRADE_FOLDER = 'static/upgrade'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])
REAL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload')
UPGRADE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upgrade')
BACK_UP = os.sep+'back_up'+os.sep
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    from hall.hallobject import *
    print sys.path
    # print '--------------------------->',TAX_NUM

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


@app.route('/upgrade_game', methods=['GET', 'POST'])
def upgrade_game():


    if request.method == 'POST':

        file = request.files['file']
        if file == None:
            return jsonify(result=0,message='error,file or uid or device_id is empty!')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPGRADE_PATH+BACK_UP, filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            print UPGRADE_PATH+BACK_UP+filename
            unzip_file(UPGRADE_PATH+BACK_UP+filename, UPGRADE_PATH)
            #     return jsonify(result=0,message='success,message:'+full_filename+',path:'+path_url,url=path_url)
            # return jsonify(result=-1,message='error:upload return false')
            # if execute(conn, "UPDATE `user` SET `avatar` = '%s' WHERE `id`=%d" % (path_url, int(uid))):
            #     return jsonify(result=0,message='success,message:'+full_filename+',path:'+path_url,url=path_url)
            # return jsonify(result=-1,message='error:upload return false')
            #return jsonify(rr=0,mm='success,message:'+full_filename+',path:'+path_url,uu=path_url)

    pathDir =  os.listdir(UPGRADE_PATH)
    html = ''
    for allDir in pathDir:
        # child = os.path.join('%s%s' % (REAL_PATH, allDir))
        html +='<li><a href="'+request.url_root+UPGRADE_FOLDER+'/'+allDir+'">'+request.url_root+UPGRADE_FOLDER+'/'+allDir+'</a></li>'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <ol>
    %s
    </ol>
    ''' % html





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
    charge_money = decimal.Decimal( (data['money']) )
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
    mail = TMail()
    mail.from_user = 10000
    mail.to_user = order.uid
    mail.sent_time = time.time()
    mail.title = u'充值'

    mail.type = 0
    mail.diamond = 0
    mail.gold = 0
    mail.state = 1
    item_price = 0
    if order.shop_id > 0:
        shop_item = session.query(TChargeItem).filter(TChargeItem.id == order.shop_id).first()
        item_price = int(shop_item.money)
        mail.content = u'成功充值 %.2f 元' % (charge_money)
        if shop_item.type is not None and shop_item.type == 'gold':
            mail.content += u'，购买 %d 金币' % (shop_item.gold)
        if shop_item.type is not None and shop_item.type == 'diamond':
            mail.content += u'，购买 %d 个钻石' % (shop_item.diamond)
    elif order.shop_id == 0:
        mail.content = u'首冲成功 %.2f 元，获得30万金币，10个张喇叭卡，10张踢人卡，1张vip经验卡' % (decimal.Decimal(FRIST_CHARGE['money']) * 100)
        item_price = FRIST_CHARGE['money']
    else:
        mail.content = u'快充成功 %.2f 元，获得万金币' % (decimal.Decimal(QUICK_CHARGE[abs(order.shop_id)-1][0]) * 100)
        item_price = QUICK_CHARGE[abs(order.shop_id)-1][3]

    print 'shop_id--->',order.shop_id
    session.add(mail)
    session.flush()
    print 'mail_id--->',mail.id
    user_info = session.query(TUser).filter(TUser.id == order.uid, TUser.is_charge == 0).first()


    # vip = VIPObject('tets')
    # reward = RewardObject('test')
    # 加vip经验
    user_info.vip_exp = 0 if user_info.vip_exp <= 0 else user_info.vip_exp
    old_vip_level = to_level(user_info.vip_exp)['level']
    user_info.vip_exp = user_info.vip_exp + item_price
    session.query(TUser).filter(TUser.id == user_info.id).update({
        TUser.vip_exp:user_info.vip_exp
    })
    new_vip_level = to_level(user_info.vip_exp)['level']
    # vip升级送金币、道具、发广播
    if old_vip_level < new_vip_level:
        diff_level = new_vip_level - old_vip_level
        if diff_level > 0:
            up_level_conf = VIP_CONF[old_vip_level:new_vip_level+1]
            for conf in up_level_conf:
                # 发广播
                # vip.level_up_broadcast(user_info.nick, 'VIP'+str(conf['level']))
                push_message(r,[],5,{'message':VIP_UP % (user_info.nick, to_level(user_info.vip_exp)['level'])})
                # 记录任务完成
                # reward.reward_log(session, user_info.id, conf['id'])
                task_log = TRewardUserLog()
                task_log.uid = user_info.id
                task_log.task_id = conf['id']
                task_log.state = 1 # 1=已完成，未领取 。 0 = 已完成，已领取。 其他 = 未完成
                task_log.create_time = datehelper.get_today_str()
                session.merge(task_log)
                session.flush()

    # 充值榜记录
    save_charge_top(session, {
        'uid':order.uid,
        'charge_money':charge_money
    })

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

def save_charge_top(session, fields):
    insert_stmt = "INSERT INTO rank_charge_top(add_date,uid,charge_money) VALUES (:col_1,:col_2,:col_3) ON DUPLICATE KEY UPDATE charge_money = charge_money + :col_3;"
    session.execute(insert_stmt, {
        'col_1':time.strftime('%Y-%m-%d'),
        'col_2':fields['uid'],
        'col_3':fields['charge_money']
    })
    session.flush()


def to_level(charge):

    lst_len = len(VIP_CONF)
    for index in range(lst_len):
        if index + 1 == lst_len:
            if charge >= VIP_CONF[index].get('charge'):
                return VIP_CONF[index]
            else:
                return VIP_CONF[index - 1]

        if charge >= VIP_CONF[index].get('charge') and charge < VIP_CONF[index + 1].get('charge'):
            return VIP_CONF[index]

def push_message(r,users,p1,p2,notifi_type = 1):
    users = r.keys('online')
    item = {'users':users,'param1':p1,'param2':p2,'notifi_type':notifi_type}
    r.lpush('notification_queue', json.dumps(item))

def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\','/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir) : os.mkdir(ext_dir,0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

if __name__ == '__main__':
    # Entry the application
    app.run()