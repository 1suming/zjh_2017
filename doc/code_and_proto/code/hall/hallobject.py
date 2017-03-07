# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from config.var import *
from db.bag_item import *
from db.mail import *
from datetime import date,datetime
from helper import cachehelper
import time


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
    def __init__(self,dataaccess,session):
        self.da = dataaccess
        self.session = session

    def send_mail(self, contents, **kwargs):
        print '222222222222222222222222222222222'
        print contents,'========',kwargs
        for i in contents:
            kwargs['content'] += MAIL_TEMPLATE[i]

        print kwargs

        self.save_mail(kwargs)
        cachehelper.add_notification_queue(self.da.redis,[kwargs.get('to')],0, {},N_MAIL)


    def save_mail(self, **kwargs):
        mail = TMail()
        mail.from_user = kwargs.get('from_user')
        mail.to_user = kwargs.get('to')
        mail.send_time = int(time.time())
        mail.title = kwargs.get('title')
        mail.content = kwargs.get('content')
        mail.type = kwargs.get('type')
        mail.diamond = kwargs.get('diamond',0)
        mail.gold = kwargs.get('gold',0)
        mail.items = kwargs.get('items')
        mail.gifts = kwargs.get('gifts')
        mail.received_time = kwargs.get('received_time')
        mail.state = 0
        self.session.save(mail)