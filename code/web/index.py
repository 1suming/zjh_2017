# coding: utf-8
import os
import json
import sys
import redis
import zipfile
import hashlib
import decimal
import time
sys.path.append(os.path.dirname(__file__) + os.sep + '..' + os.sep)
from db.connect import *
from db.user import *
from db.reward_user_log import *
from db.order import *
from db.charge_item import *


from bottle import route, run, static_file, error, get, post, request
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists


STATIC_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'static' + os.sep)
AVATAR_PATH = STATIC_PATH + 'avatar'
UPGRADE_PATH = STATIC_PATH + 'upgrade'

AVATAR = '/avatar'
UPGRADE = '/upgrade'
STATIC_P = '/static'

allow_ext = ('.png', '.jpg', '.jpeg', '.zip')


session = Session()
r = redis.Redis(host='121.201.29.89', port=26379,db=0, password='Wgc@123456')


def avatar_save_path(filename):
    return AVATAR_PATH + os.sep + filename


def avatar_url_path(filename):
    return http_url(STATIC_P + AVATAR + '/' + filename)


def app_save_apth(filename):
    return UPGRADE_PATH + os.sep + filename


def app_url_apth(filename):
    return http_url(STATIC_P + UPGRADE + '/' + filename)


def http_url(url=None):
    if url is not None:
        return 'http://' + request.environ.get('HTTP_HOST') + url
    return 'http://' + request.environ.get('HTTP_HOST') + '/'

def get_md5(s):
    return hashlib.md5(s).hexdigest()

def get_sign(data):
    return hashlib.md5(CALLBACK+data+CP_KEY).hexdigest()

def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root=STATIC_PATH)


@error(404)
def error_page(error):
    return u'没有你要访问的界面'


@route('/')
def index():
    return request.url


@route("/avatar_upload", method='POST')
@route("/avatar_upload", method='GET')
def avatar_upload():

    if request.method == 'POST':
        file = request.files.get('file')
        uid = request.forms.get('uid')
        device_id = request.forms.get('device_id')

        if file == None or uid == None or device_id == None:
            return {'result': 0, 'message': 'error,file or uid or device_id is empty!'}

        name, ext = os.path.splitext(file.filename)

        if ext not in allow_ext:
            return {'result': 0, 'message': 'error,file ext need png or zip'}

        filename = uid + '_' + device_id + '_' + file.filename
        file.save(avatar_save_path(filename), True)

        url_path = avatar_url_path(filename)

        result = session.query(TUser).filter(TUser.id == uid).filter(TUser.id == int(uid)).update({
            TUser.avatar: url_path
        })

        if result > 0:
             # 修改头像换缓存
            if r.exists('u' + str(uid)):
                r.hset('u' + str(uid), 'avatar', url_path)

            # 记录完成头像任务
            task_log = session.query(TRewardUserLog).filter(
                and_(TRewardUserLog.uid == uid, TRewardUserLog.task_id == 10)).first()
            if task_log is None:
                task_log = TRewardUserLog()
                task_log.uid = uid
                task_log.task_id = 10  # 修改任务头像id
                task_log.state = 1  # 1=已完成，未领取 。 0 = 已完成，已领取。 其他 = 未完成
                task_log.create_time = datehelper.get_today_str()
                session.add(task_log)

            return {'result': 0, message: 'success,message:' + url_path}
        return {'result': -1, message: 'error:upload return false'}

    pathDir = os.listdir(AVATAR_PATH)
    html = ''
    for allDir in pathDir:
        # child = os.path.join('%s%s' % (REAL_PATH, allDir))
        html += '<li><a href="http://' + request.environ.get('HTTP_HOST') + STATIC_P + AVATAR + '/' + allDir + \
            '">http://' + \
                request.environ.get('HTTP_HOST') + STATIC_P + \
            AVATAR + '/' + allDir + '</a></li>'
    return '''
    <!doctype html>
    <title>Upload new avatar</title>
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


@route('/upgrade_game', method='POST')
@route('/upgrade_game', method='GET')
def upgrade_game():

    if request.method == 'POST':
        file = request.files.get('file')
        if file == None:
            return {'result': 0, 'message': 'error,file error!'}

        name, ext = os.path.splitext(file.filename)

        if ext not in allow_ext:
            return {'result': 0, 'message': 'error,file ext need png or zip'}

        filename = file.filename
        url_path = app_save_apth('backup'+os.sep+filename)
        
        file.save(url_path, True)
   
        unzip_file(url_path, app_save_apth(os.sep+name))

    pathDir = os.listdir(UPGRADE_PATH)
    html = ''
    for allDir in pathDir:
        html += '<li><a href="http://' + request.environ.get('HTTP_HOST') + STATIC_P + UPGRADE + '/' + allDir + \
                '">http://' + \
            request.environ.get('HTTP_HOST') + STATIC_P + \
                UPGRADE + '/' + allDir + '</a></li>'
    return '''
    <!doctype html>
    <title>Upload new app</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <ol>
    %s
    </ol>
    ''' % html


@post('/pay_result')
def pay_result():
    data = json.loads(request.forms.get('data'))
    sign = request.forms.get('sign')

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
    # 1 horn    大喇叭 可以公开喊话  2017-02-14 15:33:01
    # 2 kick    踢人卡 奖玩家踢出房间 2017-02-14 15:35:02
    # 3 exp_1   经验卡1点   使用后获得1点VIP经验    2017-02-15 10:43:51
    # 4 exp_10  经验卡10点  使用后获得10点VIP经验   2017-02-15 11:15:49
    # 5 tgold   金币名称    金币介绍    2017-02-15 16:57:49
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

if __name__ == '__main__':
    # 默认端口  run(host='localhost', port=8080)
    run(host='0.0.0.0', debug=True, reloader=True)
