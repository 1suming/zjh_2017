# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import json,sys,redis,time,os,os.path,decimal
import hashlib
import zipfile

from flask import Flask,request,render_template,redirect, url_for,jsonify
from werkzeug import secure_filename

from conf import DevConfig


from db.connect import *
from db.order import *
from db.mail import *
from db.bag_item import *
from db.charge_item import *
from db.mail import *
from db.reward_user_log import *
from db.customer_service_log import *
from db.user import *
from config.var import *
from config.rank import *

from helper import datehelper
from sqlalchemy import and_
from sqlalchemy.sql import desc

# from web.upload import *
# from web.avatar import *

# from config.var import *
# from config.vip import *
from hall.hallobject import *
from task.achievementtask import *
from rank.chargetop import *

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__, static_path='',static_folder='')
app.config.from_object(DevConfig)

session = Session()
r = redis.Redis(host='121.201.29.89',port=26379,db=0,password='Wgc@123456')
STATIC_PATH = 'web/static/'
# uploader = Uploader(STATIC_PATH)
vip = VIPObject(None)




# CPID：jjcq20170223_141_312
# CPKEY：d5ff856beccf4c472831c3f16c376e28
# CP_KEY = 'd5ff856beccf4c472831c3f16c376e28'

# VIP_UP=u'玩家%s一掷千金，成功升级为%s，成为人生赢家！(VIP1+)'
UPLOAD_FOLDER = 'web/static/avatar'
UPGRADE_FOLDER = 'web/static/upgrade'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])
REAL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web/static/avatar')
UPGRADE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web/static/upgrade')
BACK_UP = os.sep+'backup'+os.sep
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    return CALLBACK


@app.route('/avatar', methods=['GET', 'POST'])
def upload_avatar():

    if request.method == 'POST':

        file = request.files['file']
        uid = request.form['uid']
        device_id = request.form['device_id']

        if file == None or uid == None or device_id == None:
            return jsonify(result=0,message='error,file or uid or device_id is empty!')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            savefolder = time.strftime('%Y-%m-%d')
            savepath = REAL_PATH+os.sep+time.strftime('%Y-%m-%d')
            if not os.path.isdir(savepath):
                os.mkdir(savepath)
            file.save(os.path.join(savepath, uid+'_'+device_id+'_'+filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            full_filename ='/'+uid+'_'+device_id+'_'+filename
            path_url = request.url_root+UPLOAD_FOLDER+'/'+savefolder+full_filename

            result = session.query(TUser).filter(TUser.id == uid).filter(TUser.id == int(uid)).update({
                TUser.avatar:path_url
            })


            if result > 0:
                # 修改头像换缓存
                if r.exists('u'+str(uid)):
                    r.hset('u'+str(uid), 'avatar', path_url)

                SystemAchievement(session,uid).finish_upload_avatar()

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
    <h1>Upload new <span style='color:green;'>avatar</span></h1>
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


@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade():


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
    <h1>Upload new <span style='color:red;'>App</span></h1>
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
    print 'init---->'
    print request.form
    print 'init_end---->'
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
        mail.content = u'首冲成功 %.2f 元，获得%d万金币，%d个张喇叭卡，%d张踢人卡，%d张vip经验卡' %\
                       (decimal.Decimal(FRIST_CHARGE['money']) / 100,FRIST_CHARGE['gold'],FRIST_CHARGE['hore'],FRIST_CHARGE['kicking_card'],FRIST_CHARGE['vip_card'])
        item_price = FRIST_CHARGE['money']
    else:
        quick_charge = QUICK_CHARGE[abs(order.shop_id)-1]
        item_price = quick_charge[3]
        mail.content = u'快充成功 %.2f 元，获得%d万金币' % (decimal.Decimal(quick_charge[1]) * 100,quick_charge[1] )


    print 'shop_id--->',order.shop_id
    session.add(mail)
    session.flush()
    print 'mail_id--->',mail.id
    user_info = session.query(TUser).filter(TUser.id == order.uid, TUser.is_charge == 0).first()



    # 加vip经验
    user_info.vip_exp = 0 if user_info.vip_exp <= 0 else user_info.vip_exp
    old_vip_level = vip.to_level(user_info.vip_exp)
    user_info.vip_exp = user_info.vip_exp + item_price
    session.query(TUser).filter(TUser.id == user_info.id).update({
        TUser.vip_exp:user_info.vip_exp
    })
    new_vip_level = vip.to_level(user_info.vip_exp)
    # vip升级送金币、道具、发广播
    if old_vip_level < new_vip_level:
        diff_level = new_vip_level - old_vip_level
        if diff_level > 0:
            push_message(r,r.keys('online'),2,{'nick':user_info.nick,'vip_exp':user_info.vip_exp})
            SystemAchievement(session,user_info.id).finish_upgrade_vip(vip.to_level(user_info.vip_exp))

    # 通知用户充值成功
    push_message(r,[user_info.id],0,'',N_CHARGE)

    if r.exists('u'+str(order.uid)):
        r.delete('u'+str(order.uid))



    user_info = session.query(TUser).filter(TUser.id == order.uid, TUser.is_charge == 0).first()
    if order.shop_id == 0 and user_info.is_charge == 0:
        session.query(TUser).with_lockmode("update").filter(TUser.id == order.uid, TUser.is_charge == 0).update({
            TUser.is_charge:1,
            TUser.gold:TUser.gold+(FRIST_CHARGE['gold'] * 10000),
            TUser.diamond:TUser.diamond+FRIST_CHARGE['diamond']
        })

        for item in FRIST_CHARGE['items'].split(','):
            arr_item = item.split('-')
            save_countof(session, {
                'uid':order.uid,
                'stuff_id':arr_item[0],
                'countof':arr_item[1],
            })
    elif order.shop_id < 0:
        session.query(TUser).with_lockmode("update").filter(TUser.id == order.uid).update({
            TUser.gold:TUser.gold+quick_charge[1] * 10000,
        })
    else:
        session.query(TUser).with_lockmode("update").filter(TUser.id == order.uid).update({
            TUser.gold:TUser.gold+shop_item.gold,
            TUser.diamond:TUser.diamond+shop_item.diamond,
        })

    ChargeTop.save_rank(session, user_info.id, 0, charge_money)

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



def push_message(r,users,p1,p2,notifi_type = 1):
    item = {'users':users,'notifi_type':notifi_type}
    if p1 is not None:
        item['param1'] = p1
    if p2 is not None:
        item['param2'] = p2

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