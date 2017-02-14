    #coding: utf-8
'''
Created on 2012-2-20

@author: Administrator
'''

from gevent import monkey;monkey.patch_all()

import importlib
import time,traceback
import threading
import sys,logging

from db.connect import *
from message.base import *
import socket

from proto.access_pb2 import *
from proto.constant_pb2 import *
from proto.game_pb2 import *
from proto.hall_pb2 import *
from proto.chat_pb2 import *
from proto.reward_pb2 import *
from proto.trade_pb2 import *
from proto.bag_pb2 import *
from proto.bank_pb2 import *
from proto.mail_pb2 import *
from proto.friend_pb2 import *
from proto.struct_pb2 import *
from proto.rank_pb2 import *
from testbasecard import *



def fast_login_game(client,device_id,imei,imsi,token):
    try:
        MessageMapping.init()
        resp = client.fast_test_enter_server(device_id,imei,imsi,token)

        req = create_client_message(ConnectGameServerReq)
        req.header.user = resp.header.user
        req.body.session = resp.body.session

        client.socket.send(req.encode())

        resp2 = client.get_message()
        print '1111111111111111111111111111111111111111111'

        req2 = create_client_message(GetServerTimeReq)
        req2.header.user = resp.header.user
        client.socket.send(req2.encode())
        # client.get_message()
        # req2 = create_client_message(QueryUserReq)
        # req2.header.user = resp2.header.user
        # req2.body.uid = resp2.header.user
        # client.socket.send(req2.encode())
        # client.get_message()
    except:
        traceback.print_exc()
    finally:
        pass

def register_game(client,mobile,password,verify_code,imei,imsi,device_id,channel):
    try:
        MessageMapping.init()
        resp = client.register_test_enter_server(mobile,password,verify_code,imei,imsi,device_id,channel)
        # RESULT_FAILED_NAME_EXISTED
        if resp.header.result == 5:
            print 'RESULT_FAILED_NAME_EXISTED'
            return

        if resp.header.result == 8:
            print 'RESULT_FAILED_ACCOUNT_DISABLED'
            return


        req = create_client_message(ConnectGameServerReq)
        req.header.user = resp.header.user
        req.body.session = resp.body.session

        client.socket.send(req.encode())
    except:
        traceback.print_exc()
    finally:
        pass

def normal_login_game_server_time(client,mobile,password,device_id):
    try:
        MessageMapping.init()
        print mobile,password,device_id
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        req = create_client_message(GetServerTimeReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def normal_logout(client,mobile,password,token):
    try:
        MessageMapping.init()
        resp = client.normal_logout_server('13412341234','123456','d_9333')

        print '#####################'
        print resp.header.user,'=',resp.header.result
    except:
        traceback.print_exc()
    finally:
        pass

def update_user(client,mobile,password,device_id):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        time.sleep(1)
        print '33333333333333333333333333333333333'
        req = create_client_message(UpdateUserReq)
        req.header.user = result.header.user
        req.body.sign = '222222签名喔~~~'
        # req.body.nick = '1111111张学友'
        req.body.birthday = '1911-01-11'
        req.body.avatar = 'http://p2.gexing.com/touxiang/2012/3/17/201237180763704.jpg'
        print req.header.user,'=',req.header.result
        client.socket.send(req.encode())

    except:
        traceback.print_exc()
    finally:
        pass

def get_annoucments(client,mobile,password,token):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server('13412311111','123456','device_id_333')

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body


        req = create_client_message(QueryAnnouncementsReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def send_chat_world(client,mobile = '13412341235',password= '123456',token='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,token)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body


        req = create_client_message(QueryHallReq)
        req.header.user = result.header.user
        req.body.max_mail_id =  0
        req.body.max_announcement_id =  0
        client.socket.send(req.encode())
        time.sleep(2)
        req2 = create_client_message(SendChatReq)
        req2.header.user = result.header.user
        req2.body.table_id = 0
        req2.body.message = u'在Python中使用protocol buffers参考指南！！#￥%……&*（'
        client.socket.send(req2.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def send_chat_room(client,mobile = '13412341235',password= '123456',token='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,token)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body


        req = create_client_message(QueryHallReq)
        req.header.user = result.header.user
        req.body.max_mail_id =  0
        req.body.max_announcement_id =  0
        client.socket.send(req.encode())
        time.sleep(2)
        req2 = create_client_message(SendChatReq)
        req2.header.user = result.header.user
        req2.body.table_id = 0
        req2.body.message = u'在Python中使用protocol buffers参考指南！！#￥%……&*（'
        client.socket.send(req2.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_rewards(client,mobile,password,device_id):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        req = create_client_message(QueryRewardsReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

        # req2 = create_client_message(QueryRewardsResp)
        # req2.header.user = result.header.user
        # client.socket.send(req2.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def revice_rewards(client,mobile,password,device_id):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body


        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

        req2 = create_client_message(ReceiveRewardReq)
        req2.header.user = result.header.user
        req2.body.reward_id = 2
        client.socket.send(req2.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass


def get_hall_query(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryHallReq)
        req.header.user = result.header.user
        req.body.max_mail_id = 0
        req.body.max_announcement_id = 0
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def query_player(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        # print '3333333333333333333333333333333333'
        # req = create_client_message(QueryHallReq)
        # req.header.user = result.header.user
        # req.body.max_mail_id = 0
        # req.body.max_announcement_id = 0
        # client.socket.send(req.encode())

        req = create_client_message(QueryUserReq)
        req.header.user = result.header.user
        req.body.uid = result.header.user
        client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def use_code(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        # print '3333333333333333333333333333333333'
        # req = create_client_message(QueryHallReq)
        # req.header.user = result.header.user
        # req.body.max_mail_id = 0
        # req.body.max_announcement_id = 0
        # client.socket.send(req.encode())

        req = create_client_message(ReceiveCodeRewardReq)
        req.header.user = result.header.user
        req.body.code = '0755'
        client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_signs(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryHallReq)
        req.header.user = result.header.user
        req.body.max_mail_id = 0
        req.body.max_announcement_id = 0
        client.socket.send(req.encode())

        time.sleep(1)
        req = create_client_message(QuerySigninRewardReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def today_sign(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryHallReq)
        req.header.user = result.header.user
        req.body.max_mail_id = 0
        req.body.max_announcement_id = 0
        client.socket.send(req.encode())
        print '444444444444444444444444444444444444444444'
        time.sleep(1)
        req = create_client_message(QuerySigninRewardReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())
        time.sleep(1)
        print '5555555555555555555555555555555555555555555'
        req = create_client_message(SigninReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())
      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_register_code(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()

        req = create_client_message(GetVerifyCodeReq)
        req.header.user = -99
        req.body.mobile = '17727853917'
        req.body.token = '123123'
        print '111111111111111111111111111111111'
        client.login_socket.send(req.encode())

        resp = client.get_message(client.login_socket)
        print resp.body
        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_shop_item(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryShopReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def buy_shop_item(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(BuyItemReq)
        req.header.user = result.header.user
        req.body.shop_item_id = 1
        req.body.count = 1
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def trade_page_list(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryTradeReq)
        req.header.user = result.header.user
        req.body.page = 1
        req.body.page_size = 3
        req.body.can_buy = True
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass
def trade_buy(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(BuyTradeReq)
        req.header.user = result.header.user
        req.body.trade_id = 1
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def trade_sell(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(SellGoldReq)
        req.header.user = result.header.user
        req.body.gold = 1000
        req.body.diamond = 10
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def query_user_bag(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryBagReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def query_bank(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryBankReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def active_bank_gold(client,mobile = '13412341777',password= '123456',device_id='d_9444',act = ''):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(SaveMoneyReq)
        req.header.user = result.header.user
        req.body.gold = 10
        req.body.type = act
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_mails(client,mobile = '13412341777',password= '123456',device_id='d_9444',act = ''):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(FetchMailReq)
        req.header.user = result.header.user
        req.body.max_mail_id = 0
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def receive_mails(client,mobile = '13412341777',password= '123456',device_id='d_9444',act = ''):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(ReceiveAttachmentReq)
        req.header.user = result.header.user
        req.body.mail_id = 2
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def send_mail(client,mobile = '13412341777',password= '123456',device_id='d_9444',act = ''):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(SendMailReq)
        req.header.user = result.header.user
        req.body.to = 10018
        req.body.title = '测试标题'
        req.body.content = '测试正文内容'
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_friends(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(GetFriendsReq)
        req.header.user = result.header.user
        req.body.page = 1
        req.body.page_size = 10
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_friends_apply(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(GetFriendAppliesReq)
        req.header.user = result.header.user
        req.body.page = 1
        req.body.page_size = 10
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def make_friends_apply(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(MakeFriendReq)
        req.header.user = result.header.user
        req.body.target = 10020
        req.body.message = '88 flowers for you'
        gift = req.body.gifts.add()
        gift.id = 66
        gift.name = '88 flowers'
        gift.icon = '88flower'
        gift.count = 2
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def remove_friends_apply(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(RemoveFriendMessageReq)
        req.header.user = result.header.user
        req.body.friend_id = 10158

        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def send_friends_message(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(SendFriendMessageReq)
        req.header.user = result.header.user
        req.body.friend_id = 10020
        req.body.message = '77 flowers for you'

        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_rank(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryRankReq)
        req.header.user = result.header.user
        req.body.rank_type = 4
        req.body.rank_time = 2
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def receive_broke(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(ReceiveBankcruptRewardReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def get_broke(client,mobile = '13412341777',password= '123456',device_id='d_9444'):
    try:
        MessageMapping.init()
        resp = client.normal_test_enter_server(mobile,password,device_id)

        print '1111111111111111111'
        print resp.header.user,'=',resp.header.result
        print resp.body

        client.setup_socket()
        result = client.connect_game_server(resp.header.user, resp.body.session, 1)
        print '2222222222222222222'
        print result.header.user,'=',result.header.result
        print result.body

        print '3333333333333333333333333333333333'
        req = create_client_message(QueryBankcruptRewardReq)
        req.header.user = result.header.user
        client.socket.send(req.encode())

        # req = create_client_message(QueryUserReq)
        # req.header.user = result.header.user
        # req.body.uid = result.header.user
        # client.socket.send(req.encode())

      # client.socket.send(req.encode())

    except Exception as e:
        traceback.print_exc()
    finally:
        pass

def test_card(imei,imsi,token,need_idle,*args):
    resp = None
    try:
        MessageMapping.init()
        client = TestClient(str(999999),str(999998), 'token_123')
        # get_broke(client, '13412311111','123456', 'device_id_333')
        # receive_broke(client, '13412311111','123456', 'device_id_333')
        # upgrade_check(client, '13412311111','123456', 'device_id_333')
        get_rank(client, '13488889999','123456', '865372020475361')

        # send_friends_message(client, '13412311111','123456', 'device_id_333')
        # make_friends_apply(client, '13412311111','123456', 'device_id_333')
        # remove_friends_apply(client, '13412311111','123456', 'device_id_333')
        # receive_mails(client, '13412311111','123456', 'device_id_333')

        # get_friends_apply(client, '13412311111','123456', 'device_id_333')
        # get_friends(client, '13412311111','123456', 'device_id_333')
        # query_bank(client, '13412311111','123456', 'device_id_333')

       #  active_bank_gold(client, '13412311111','123456', 'device_id_333', BANK_ACT_SAVE)

        # buy_shop_item(client, '13412311111','123456', 'device_id_333')
        # normal_login_game_server_time(client, '13412341777','123456', '88899111121')
        # trade_page_list(client, '13412311111','123456', 'device_id_333')
        # trade_buy(client, '13412311111','123456', 'device_id_333')
        # trade_sell(client, '13412311111','123456', 'device_id_333')
        # query_user_bag(client, '13412311111','123456', 'device_id_333')

        # query_player(client, '13412311111','123456', 'device_id_333')
       #  fast_login_game(client,'device_id_333','imei_1010','imsi_2020', 'token_2020')
        # register_game(client, '13412311111','123456','1234','imei_1111','imsi_2222','device_id_333','LT333')
        # get_hall_query(client,'13412345678','123456','000000000000000')

        # normal_logout(client, str(999999),str(999998), 'token_123')
        # update_user(client, '13412311111','123456', 'device_id_333')

        # get_annoucments(client, str(999999),str(999998), 'token_123')

       #  use_code(client, '13412311111', '123456', 'device_id_333')

        # get_signs(client, 'wxy', '123456', '865647020556892')
        # today_sign(client, '13412311111', '123456', 'device_id_333')
        # send_chat_world(client,'13488889999', '123456', '865372020475361')
        # send_chat_room(client,'13412311111', '123456', 'device_id_333')
        # get_rewards(client, '13412311111','123456', 'device_id_333')
        # revice_rewards(client, '13412311111','123456', 'device_id_333')
        # get_shop_item(client, '13412311111','123456', 'device_id_333')
        # get_register_code(client,'13412311111', '123456', 'device_id_333')

        get_mails(client, '13488889999','123456', '865372020475361')

        # send_mail(client, '13412311111','123456', 'device_id_333')

        if need_idle:
            client.idle()
        else:    
            resp = client.get_message()  
            print "== result ==>",resp.header.result
          
    except:
        traceback.print_exc()
    finally:
        pass
    return resp

if __name__ == "__main__":
    if sys.argv[1] != "-w":
        test_card(sys.argv[1],"123456",'',True,*sys.argv[2:])
    else:
        test_card(sys.argv[2],"123456",'',True,*sys.argv[3:])
    print "Done"