#coding:utf-8

import gevent
from gevent import monkey;monkey.patch_all()

from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue
import httplib,urllib
import signal 
import json
import string
import logging
import traceback
import time
import os,sys
import random
from datetime import date
from systemconfig import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists,or_
from proto.access_pb2 import *
from message.base import *
from message.resultdef import *
from config.var import *
import redis

from db.connect import *
from db.account import *
from db.user import *
from util.asyncsocket import *
from helper.smshelper import SMS
# from config.broadcast import *
# from hall.hallobject import *
from helper import encryhelper


pool = Pool(50)

def random_session():
    return random.randint(10000000,20000000)
    

CLIENT_TIMEOUT = 60
BUFFER_SIZE = 1024


class VersionManager:
    def __init__(self):
        with open("web/static/upgrade/version.txt") as f:
            self.version = int(f.readline())
        self.upgrade_info = {}
        gevent.spawn(self.load_version)
        
    def load_version(self):
        while True:
            with open("web/static/upgrade/version.txt") as f:
                self.version = int(f.readline())
            gevent.sleep(60)
        
    def get_upgrade_info(self,old_version):
        if self.version <= old_version:
            return None
        key = self.version
        json = self.upgrade_info.get(key,None)
        if json == None:
            version_file = "../version/verinfo_" + str(self.version) + ".json"
            with open(version_file) as f:
                json = f.read()
      
            self.upgrade_info[key] = json
        return json

class AccountValidate:
    def check_state(self,state):
        if state == 1:
            return False
        return True

    def check_mobile_password(self,mobile,password):
        if len(mobile) > 11 or len(mobile) == 0:
            return False
        if len(password) < 6 and len(password) > 15:
            return False
        return True

    def check_device_id(self,device_id):
        if device_id == None:
            return False
        device_id = device_id.strip()
        if len(device_id) == 0 or len(device_id) > 20:
            return False
        return True

class LoginServer:
    def __init__(self,conf):
        self.conf = conf
        self.accounts = {}
        self.redis = redis.Redis(*conf.get_redis_config("login_redis"))
        
        self.message_handlers = {
            RegisterReq.DEF.Value("ID"):self.handle_register,
            LoginReq.DEF.Value("ID"): self.handle_login,
            ResetReq.DEF.Value("ID"): self.handle_reset,
            LogoutReq.DEF.Value("ID"): self.handle_logout,
            FastLoginReq.DEF.Value("ID"): self.handle_fast_login,
            GetVerifyCodeReq.DEF.Value("ID"): self.handle_get_verify_code,
            CheckUpgradeReq.DEF.Value("ID"):self.handle_check_upgrade,
            GameResUpgradeReq.DEF.Value("ID"):self.handle_game_res_upgrade,
        }
        self.version_manager = VersionManager()
        self.av = AccountValidate()
    
    def init(self):
        logging.info("Check account table ...")
        session = UserSession()
        try:
            session.begin()
            row = session.execute("show table status where name = 'account'").fetchone()
            auto_increment = row["Auto_increment"]
            if auto_increment < 10000:
                session.execute("alter table account auto_increment = 10000")
            session.commit()
        except:
            traceback.print_exc()
            session.rollback()
        finally:
            session.close()
            session = None
    
    def handle_client_socket(self,sock,address):
        #logging.info("------------>" + str(sock) + "------->" + str(address))
        logging.info("=====》 new client is comming ...")
        sock.settimeout(CLIENT_TIMEOUT)
        sock = async_send_socket(sock)
        buffer = ""
        while True:
            try :
                request_data = get_message(buffer,len(buffer),0)
                if request_data == None:
                    data = sock.recv(BUFFER_SIZE)
                    if data == None or len(data) == 0:
                        logging.info("disconnected now ---> no data")
                        break
                    buffer += data
                    continue
                msg,start = request_data
                buffer = buffer[start:]
                handler = self.message_handlers.get(msg.header.command)
                if handler == None:
                    logging.info("receive invalid message" + str(msg.header.command))
                    break
                logging.info("receive a client message:" + str(msg.body))
                resp = create_response(msg)
                connect = handler(msg,resp)
                if connect == True and handler == self.handle_logout:
                    logging.info('logout a client '+str(msg.header.command))
                    sock.async_close()

                logging.info("send a message back to client: %d,%d " + str(resp.body),resp.header.result,resp.header.user)
                sock.async_send(resp.encode())
                #if connect == True:
                #     continue
                break
            except:
                traceback.print_exc()
                break
        sock.async_close()

    def handle_check_upgrade(self,message,resp):
        # old_version = message.body.version
        # version_info = self.version_manager.get_upgrade_info(old_version)
        # resp.body.version = self.version_manager.version
        # if version_info != None:
        #     resp.body.upgrade_info = version_info
        # resp.header.result = 0
        # return True

        resp.body.is_upgrade = False
        print '------------->',message.body.ver,float(message.body.ver,2)
        if message.body.ver < self.version_manager.upgrade_info:
            resp.body.is_upgrade = True
            resp.body.upgrade_url = UPGRADE_URL

        print message.body.ver,self.version_manager.res_ver
        resp.header.result = 0

        return True

    def handle_register(self,message,resp):
        session = UserSession()
        try :
            if self.av.check_mobile_password(message.body.mobile,message.body.password) == False:
                resp.header.result = RESULT_FAILED_ACCOUNT_OR_PASSWORD_INVALID
                return
            if self.av.check_device_id(message.body.device_id) == False:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return
            if int(message.body.verify_code) != 0000:
                if self.redis.get('sms_'+message.body.mobile) == None:
                    resp.header.result = RESULT_FAILED_SMS_NOT_EQUALS
                    return
                if int(message.body.verify_code) != int(self.redis.get('sms_'+message.body.mobile)):
                    resp.header.result = RESULT_FAILED_SMS_NOT_EQUALS
                    return

            session.begin()
            account = session.query(TAccount).filter(TAccount.device_id == message.body.device_id).first()
            if account != None:
                if self.av.check_state(account.state) == False:
                    resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                    return
                # 曾经快速登录过，现在注册手机号
                account.mobile = message.body.mobile
                account.password = message.body.password
                # account.password = encryhelper.md5_encry(message.body.password+PASS_ENCRY_STR)
                account.imei = message.body.imei
                account.imsi = message.body.imsi
                account.state = STATE_ENABLE # 0=通过验证，-1=未通过验证
                user_info = session.query(TUser).filter(TUser.id == account.id).first()
            else:
                account = self.add_account(message)
                session.add(account)
                user_info = self.add_user(account.id)
                session.add(user_info)
            session.commit()

            random_key = random_session()
            resp.body.uid = account.id
            resp.body.session = random_key
            
            id,ip,port = self.get_idle_server()
            
            resp.body.server.id = id
            resp.body.server.ip = ip
            resp.body.server.port = port
                
            resp.header.result = 0
            resp.header.user = account.id
            self.redis.hset("sessions",account.id,random_key)
        except:
            traceback.print_exc()
            session.rollback()          
        finally :
            if session != None:
                session.close()
        return True
        
    # 快速登录 api_3
    def handle_fast_login(self,message,resp):
        session = UserSession()
        try :
            accounts = session.query(TAccount).with_lockmode("update").filter(TAccount.imei == message.body.imei).all()
            print 'accounts',accounts
            if len(accounts) > 1:
                # imei相同，验证安卓id
                devices = session.query(TAccount).with_lockmode("update").filter(and_(TAccount.imei == message.body.imei, TAccount.device_id == message.body.device_id)).all()

                if len(devices) > 1:
                    # 多条安卓id，返回错误
                    resp.header.result = resp.header.result = 1
                    return
                elif len(devices) == 1:
                    # 单条安卓id，通过
                    if self.av.check_state(accounts[0].state) == False:
                        resp.header.result = 2
                        return
                    account = devices[0]
                else:
                    # imei相同，没有安卓id，就新建
                    session.begin()
                    # if self.av.check_device_id(message.body.device_id) == False:
                    #     resp.header.result = 3
                    #     return
                    account = self.add_account(message)
                    session.add(account)
                    session.flush()
                    user_info = self.add_user(account.id)
                    session.add(user_info)
                    session.commit()
            elif len(accounts) == 1:
                # 安卓id相同，同一台手机
                account = accounts[0]
                if account.device_id == message.body.device_id:
                    if self.av.check_state(account.state) == False:
                        resp.header.result = 4
                        return
                else:
                    # 同一个imei，不同安卓id就新建账号
                    session.begin()
                    if self.av.check_device_id(message.body.device_id) == False:
                        resp.header.result = 5
                        return
                    account = self.add_account(message)
                    session.add(account)
                    session.flush()
                    user_info = self.add_user(account.id)
                    session.add(user_info)
                    session.commit()
            else:
                session.begin()
                if self.av.check_device_id(message.body.device_id) == False:
                    resp.header.result = 6
                    return
                account = self.add_account(message)
                session.add(account)
                session.flush()
                user_info = self.add_user(account.id)
                session.add(user_info)
                session.commit()

            print '------------------------------>hahahahah'
            # account = session.query(TAccount).with_lockmode("update").filter(TAccount.device_id == message.body.device_id).first()
            # if account == None:
            #     session.begin()
            #     if self.av.check_device_id(message.body.device_id) == False:
            #         resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
            #         return
            #     account = self.add_account(message)
            #     session.add(account)
            #     session.flush()
            #     user_info = self.add_user(account.id)
            #     session.add(user_info)
            #     session.commit()
            # else:
            #     if self.av.check_state(account.state) == False:
            #         resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
            #         return


            # 用户数据返回
            random_key = random_session()
            resp.body.uid = account.id
            resp.body.session = random_key

            id,ip,port = self.get_idle_server()

            resp.body.server.id = id
            resp.body.server.ip = ip
            resp.body.server.port = port

            resp.header.result = 0
            resp.header.user = account.id
            self.redis.hset("sessions",account.id,random_key)
        except:
            traceback.print_exc()
            session.rollback()
        finally :
            if session != None:
                session.close()
        return True

    # 验证码验证 api_7
    def handle_get_verify_code(self,message,resp):
        #resp.header.result = RESULT_FAILED_SMS_EMPTY
        #return False

        if message.body.mobile == None or message.body.mobile == '':
            resp.header.result = RESULT_FAILED_SMS_EMPTY
            return False

        if self.redis.get('sms_'+message.body.mobile) != None:
            resp.header.result = RESULT_FAILED_SMS_EXITS
            return False

        result,json,code = SMS().send_code(message.body.mobile)
        if result == False:
            resp.header.result = RESULT_FAILED_SMS_SEND_FAILED
            return False
        # {"taskId":"161128183055423368","overage":32482,"mobileCount":1,"status":0,"desc":"发送成功"}

        if json['status'] == 0:
            self.redis.set('sms_'+message.body.mobile, code, SMS_CONF['exp'])
            resp.header.result = 0
        else:
            resp.header.result = RESULT_FAILED_SMS_SEND_FAILED
            return False
        return

    # 重置密码
    def handle_reset(self,message,resp):
        if self.av.check_mobile_password(message.body.mobile,message.body.password) == False:
            resp.header.result = RESULT_FAILED_ACCOUNT_OR_PASSWORD_INVALID
            return
        if int(message.body.verify_code) != 0:
                if self.redis.get('sms_'+message.body.mobile) == None:
                    resp.header.result = RESULT_FAILED_SMS_NOT_EQUALS
                    return
                if int(message.body.verify_code) != int(self.redis.get('sms_'+message.body.mobile)):
                    resp.header.result = RESULT_FAILED_SMS_NOT_EQUALS
                    return
        session = UserSession()
        try:
            session.begin()
            session.query(TAccount).filter(TAccount.mobile == message.body.mobile).update({
                TAccount.password: message.body.password.strip()
            })
            session.commit()
        except:
            traceback.print_exc()
            session.rollback()
        finally :
            if session != None:
                session.close()

        resp.header.result = 0


    # 登录 api_1
    def handle_login(self,message,resp):
        if self.av.check_mobile_password(message.body.mobile,message.body.password) == False:
            resp.header.result = RESULT_FAILED_ACCOUNT_OR_PASSWORD_INVALID
            return
        # if self.av.check_device_id(message.body.device_id) == False:
        #     resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
        #     return

        session = UserSession()
        try :
            session.begin()
            account = session.query(TAccount).filter(TAccount.mobile == message.body.mobile).first()

            if account == None :
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return

            if self.av.check_state(account.state) == False:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return
            if account.password != message.body.password:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return

            random_key = random_session()
            self.accounts[account.id] = random_key
            resp.body.uid = account.id
            resp.body.session = random_key
            
            id,ip,port = self.get_idle_server()
            
            resp.body.server.id = id
            resp.body.server.ip = ip
            resp.body.server.port = port
                
            resp.header.result = 0
            session.commit()
            resp.header.user = account.id
            self.redis.hset("sessions",account.id,random_key)
        except:
            traceback.print_exc()
            session.rollback()          
        finally :
            if session != None:
                session.close()

    # 退出 api_5
    def handle_logout(self,message,resp):
        try :
            resp.header.result = 0
            if message.header.user:
                self.redis.hdel("sessions",message.header.user)
                resp.header.result = 0
            else:
                resp.header.result = -1
        finally :
            return

    # 创建账号
    def add_account(self,message):
        account = TAccount()
        account.device_id = message.body.device_id
        account.state = STATE_DISABLED # 0=通过验证，-1=未通过验证
        account.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        account.channel = message.body.channel
        account.imei = message.body.imei
        account.imsi = message.body.imsi
        return account

    # 更新
    def handle_game_res_upgrade(self,message,resp):
        if message.body.ver < self.version_manager.version:
            resp.body.is_upgrade = True
            resp.body.upgrade_url = UPGRADE_URL
        else:
            resp.body.is_upgrade = False
        resp.header.result = 0
        return True

    # 创建用户
    def add_user(self,uid):
        user = TUser()
        user.id = uid
        user.nick = random.choice(DEFAULT_USER['nick'])+DEFAULT_USER['nick_num'][0] % random.randint(*DEFAULT_USER['nick_num'][1])
        user.avatar = random.choice(DEFAULT_USER['avatar'])
        user.gold = DEFAULT_USER['gold']
        user.diamond = DEFAULT_USER['diamond']
        user.vip = DEFAULT_USER['vip']
        user.vip_exp = DEFAULT_USER['vip_exp']
        user.money = DEFAULT_USER['money']
        user.charm = DEFAULT_USER['charm']
        user.birthday = DEFAULT_USER['birthday']
        user.sign = DEFAULT_USER['sign']
        user.sex = DEFAULT_USER['sex']
        user.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        user.is_charge = DEFAULT_USER['is_charge']
        return user

    def get_idle_server(self):
        keys = self.redis.keys("server*")

        id = 0
        ip = ''
        port = 0
        users = 1000000

        for k in keys:
            s_id,s_ip,s_port = self.redis.hmget(k,"id","ip","port")
            s_users = self.redis.hlen(k) - 3
            if s_users <= users:
                id,ip,port,users = s_id,s_ip,s_port,s_users
        return int(id),ip,int(port)

    def handle_check_account(self,message,resp):
        session = UserSession()
        try :
            account = session.query(TAccount).with_lockmode("update").filter(TAccount.name == message.body.account).first()
            if account != None:
                resp.header.result = RESULT_FAILED_NAME_EXISTED
                return
            account = message.body.account.strip()

            if account.startswith("_robot_") or len(account) < 6 or len(account) > 11:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return

            if len(message.body.account.strip()) == 0 :
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return

            resp.header.result = 0
        except:
            traceback.print_exc()
        finally :
            if session != None:
                session.close()

        return True

if __name__ == "__main__":
    
    MessageMapping.init()
    
    conf = SystemConfig("system.ini",None)   
    DATABASE.setup_user_session(*conf.get_database_config("userdb"))
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = conf.system_config.getint("system","login_port")
        
    logging.basicConfig(level=logging.DEBUG,                        
                        format='%(threadName)s:%(asctime)s %(levelname)s %(message)s',
                        stream=sys.stdout,
                        filemode='a')
    
    threads = []
    login_server = LoginServer(conf)    
    login_server.init()
    threads.append(gevent.spawn(StreamServer(('0.0.0.0', port), login_server.handle_client_socket).serve_forever))
    logging.info("Login Server System Started on port=%d",port)
    
    _queue = Queue()    
    
    def quit():
        _queue.put_nowait(None)
    
    gevent.signal(signal.SIGINT,quit)
    
    _queue.get()
    logging.info("====> Login Server Quit <====")