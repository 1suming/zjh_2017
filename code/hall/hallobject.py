# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from config.var import *
from db.bag_item import *
from db.bag_gift import *
from db.mail import *
from datetime import date,datetime
from helper import cachehelper
import time

from proto import struct_pb2 as pb2




class ShopObject:
    def __init__(self,dataaccess,session):
        self.da = dataaccess
        self.session = session

    def buy(self, user, shopitem, req):
        if shopitem.type == SHOP_GOLD:
            if int(user.diamond) < int(shopitem.diamond):
                return False
            self.buy_gold(user,shopitem,req)
        elif shopitem.type == SHOP_ITEM:
            if int(user.diamond) < ( int(req.body.count) * int(shopitem.diamond) ):
                return False
            self.buy_item(user,shopitem,req)
        return True

    def buy_gold(self, user, shopitem, req):
        user.diamond = user.diamond - shopitem.diamond
        user.gold = user.gold + shopitem.shop_gold + shopitem.extra_gold
        self.da.save_user(self.session,user)

    def buy_item(self, user, shopitem,req):

        user.diamond = user.diamond - ( int(shopitem.diamond) * int(req.body.count) )
        bag = TBagItem()
        bag.uid = user.id
        bag.item_id = shopitem.item_id
        bag.countof = req.body.count
        insert_stmt = "INSERT INTO bag_item (uid, item_id, countof) VALUES (:column_1_bind, :columnn_2_bind, :columnn_3_bind) " \
                      "ON DUPLICATE KEY UPDATE countof=countof+:columnn_3_bind;"
        self.session.execute(insert_stmt, {'column_1_bind':bag.uid,'columnn_2_bind':bag.item_id,'columnn_3_bind':bag.countof})
        self.session.flush()
        self.da.save_user(self.session,user)

class BankObject:
    def __init__(self,dataaccess,session):
        self.da = dataaccess
        self.session = session

    def bank_save(self, user, gold):
        insert_stmt = "INSERT INTO bank_account (uid, gold, diamond,update_time,create_time) VALUES (:column_1_bind, :columnn_2_bind, :columnn_3_bind, :columnn_4_bind, :columnn_5_bind) " \
                      "ON DUPLICATE KEY UPDATE gold=gold+:columnn_2_bind,update_time=:columnn_4_bind;"
        self.session.execute(insert_stmt, {
            'column_1_bind':user.id,
            'columnn_2_bind':gold,
            'columnn_3_bind':0,
            'columnn_4_bind':datetime.now(),
            'columnn_5_bind':datetime.now(),
        })
        self.session.flush()

class MessageObject:
    def __init__(self,dataaccess):
        self.da = dataaccess
    def get_friend_message(self,event,user):
        message = event.body.ParseFromString(self.da.redis.hget('message_queue',user))
        if message != None:
            self.da.redis.hdel('message_queue',user)
        return message

    # def send_mail(self, contents, **kwargs):
    #     print '222222222222222222222222222222222'
    #     print contents,'========',kwargs
    #     for i in contents:
    #         kwargs['content'] += MAIL_TEMPLATE[i]
    #
    #     print kwargs
    #
    #     self.save_mail(kwargs)
    #     cachehelper.add_notification_queue(self.da.redis,[kwargs.get('to')],0, {},N_MAIL)
    # def save_mail(self, **kwargs):
    #     mail = TMail()
    #     mail.from_user = kwargs.get('from_user')
    #     mail.to_user = kwargs.get('to')
    #     mail.send_time = int(time.time())
    #     mail.title = kwargs.get('title')
    #     mail.content = kwargs.get('content')
    #     mail.type = kwargs.get('type')
    #     mail.diamond = kwargs.get('diamond',0)
    #     mail.gold = kwargs.get('gold',0)
    #     mail.items = kwargs.get('items')
    #     mail.gifts = kwargs.get('gifts')
    #     mail.received_time = kwargs.get('received_time')
    #     mail.state = 0
    #     self.session.save(mail)

class BagObject:
    def __init__(self,dataaccess,session):
        self.da = dataaccess
        self.session = session

    def save_user_gift(self, user,gift_id,countof):
        self.save_countof({'table_name':'bag_gift','stuff_id':gift_id,'uid':user,'countof':countof,'stuff_field':'gift_id'})

    def save_user_item(self, user,item_id,countof):
        self.save_countof({'table_name':'bag_item','stuff_id':item_id,'uid':user,'countof':countof,'stuff_field':'item_id'})

    def save_countof(self,fields):
        insert_stmt = "INSERT INTO "+fields['table_name']+"(uid,"+fields['stuff_field']+",countof) VALUES (:col_1,:col_2,:col_3) ON DUPLICATE KEY UPDATE countof = countof + :col_3;"
        self.session.execute(insert_stmt, {
            'col_1':fields['uid'],
            'col_2':fields['stuff_id'],
            'col_3':fields['countof']
        })
        self.session.flush()

class ResultObject:
    def __init__(self,pb,gold = 0,diamond = 0):
        self.gold = gold
        self.diamond = diamond
        self.pb = pb

    def set_gift(self,gift):
        self.set_stuff(self.pb.gifts_added.add(), gift)

    def set_item(self,item):
        stuff = self.set_stuff(self.pb.items_added.add(), item)
        stuff.description = item['description']


    def set_stuff(self,item,stuff):
        item.id = int(stuff['id'])
        item.icon = stuff['icon']
        item.name = stuff['name']
        item.count = stuff['count']
        return item

    def del_item(self,items):
        pass


    def gen(self):
        self.pb.gold = self.gold
        self.pb.diamond = self.diamond

class FriendObject:
    def __init__(self,pb_friend = None):
        self.pb = pb_friend

    def get_proto_struct(self, friend):
        self.pb.avatar = friend.avatar
        self.pb.gold = friend.gold
        self.pb.uid = friend.id
        self.pb.nick = friend.nick

class FriendApplyObject:
    def __init__(self,pb_friend_apply = None):
        self.pb = pb_friend_apply
    def get_proto_struct(self,friend_apply):
        self.pb.id = friend_apply.id
        self.pb.apply_from = friend_apply.uid1
        self.pb.to = friend_apply.uid2
        self.pb.time = int(time.mktime(time.strptime(friend_apply.apply_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')))
        self.pb.message = friend_apply.message


class Manager:
    def __init__(self,service):
        self.service = service

    def offline(self, user):
        access_service = self.redis.hget("online", user)
        if access_service != None:
            return int(access_service)
        return 0

    def notify_one(self,event,user):
        access_id = self.offline(user)
        if access_id == 0:
            return False
        self.service.send_client_event(access_id,user,event.header.command,event.encode())
        return True
