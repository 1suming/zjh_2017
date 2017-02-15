# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from config.var import *
from config.rank import *
from config.vip import *
from config.item import *
from message.resultdef import *
from db.bag_item import *
from db.bag_gift import *
from db.mail import *
from db.user import *
from db.item import *
from db.rank_gold_top import *
from db.rank_charge_top import *
from db.rank_make_money_top import *
from helper import protohelper
from helper import datehelper
from datetime import date,datetime
from helper import cachehelper
import time

from proto import struct_pb2 as pb2
from proto import constant_pb2

from sqlalchemy import desc,and_

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
    def __init__(self,session):
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

    def use_user_item(self, user, item_id, countof = 1):
        return self.del_countof({'table_name':'bag_item','stuff_id':item_id,'uid':user,'countof':countof,'stuff_field':'item_id'})

    def del_countof(self,fields):
        delete_stmt = "UPDATE "+fields['table_name']+" SET countof = countof - :col_1 WHERE uid = :col_2 AND item_id = :col_3 AND countof > 0"
        return self.session.execute(delete_stmt,{
            'col_1':fields['countof'],
            'col_2':fields['uid'],
            'col_3':fields['stuff_id']
        }).rowcount

    def get_user_item(self, user, item_id):
        return self.session.query(TBagItem).filter(and_(TBagItem.item_id == item_id, TBagItem.uid == user)).first()

    def use_item(self, service,user, item_name, **args):
        return getattr(self, ITEM_MAP[item_name][1])(service, user, args)
    def use_kick(self, service, uid):
        # 调用踢人函数
        pass

    def use_horn(self, service, uid, args):
        # 调用广播函数
        cachehelper.add_notification_queue(service.redis,service.redis.hkeys('online'), 5,{'message':args['message'],"message_color":'red'})

    def use_exp_1(self, service, user,args):
        if type(user) == int:
            user = service.da.get_user(user)
        user.exp = user.exp + 1
        vip = VIPObject.get_vip(user.exp)
        if user.vip < vip:
            user.vip = vip
        return service.da.save_user(self.session, user)

    def use_exp_10(self, service, user,args):
        if type(user) == int:
            user = service.da.get_user(user)
        user.exp = user.exp + 10
        vip = VIPObject.get_vip(user.exp)
        if user.vip < vip:
            user.vip = vip
        return service.da.save_user(self.session, user)

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


class RankObject:

    # 日充值榜单，调用函数
    # RankObject.add_charge_top(session, 10026,'nick','avatar',100)
    # 周赚金榜单，调用函数
    # RankObject.add_make_money_top(session, 10026,'nick','avatar',100)

    def __init__(self, session):
        self.session = session
        self.rank_type_map = {
            1: self.wealth_top,
            2: self.charge_top,
            4: self.make_money_top,
        }

    def get_lists(self, rank_type, rank_time = None):
        func = self.rank_type_map[rank_type]
        return func(rank_time)

    def wealth_top(self, rank_time):
        return self.session.query(TRankGoldTop).order_by(desc(TRankGoldTop.gold)).limit(RANK_WEALTH_TOP).all()

    def charge_top(self,rank_time):
        query = self.session.query(TRankChargeTop)
        if constant_pb2.RANK_YESTERDAY == rank_time:
            query = query.filter(TRankChargeTop.add_date == datehelper.get_yesterday())
        else:
            query = query.filter(TRankChargeTop.add_date == datehelper.get_datetime().strftime('%Y-%m-%d'))
        items = query.order_by(desc(TRankChargeTop.gold)).limit(RANK_CHARGE_TOP).all()
        self.merage_fake(items)
        return items

    def make_money_top(self,rank_time):
        query = self.session.query(TRankMakeMoneyTop)
        print constant_pb2.RANK_LAST_WEEK,rank_time
        if constant_pb2.RANK_LAST_WEEK == rank_time:
            query = query.filter(and_(TRankMakeMoneyTop.add_year == datehelper.get_last_week().strftime('%Y'),TRankMakeMoneyTop.week_of_year == datehelper.get_last_week().strftime('%W')) )
        else:
            query = query.filter(and_(TRankMakeMoneyTop.add_year == datehelper.get_datetime().strftime('%Y'),TRankMakeMoneyTop.week_of_year == datehelper.get_datetime().strftime('%W')) )
        items = query.order_by(desc(TRankMakeMoneyTop.gold)).limit(RANK_CHARGE_TOP).all()
        self.merage_fake(items)
        return items


    def set_pb(self, resp, items):

        for index in range(len(items)):
            protohelper.set_top(resp.body.players.add(), items[index], index)


    def merage_fake(self, data):
        if len(data) <= 0:
            data = RANK_FAKE
        else:
            for fake in RANK_FAKE:
                if len(data) >= RANK_CHARGE_TOP:
                    break;
                data.append(fake)
    @staticmethod
    def add_charge_top(session,uid,nick,avatar,gold,vip):
        result = session.execute("INSERT INTO rank_charge_top(uid,nick,avatar,gold,add_date) VALUES (:uid,:nick,:avatar,:gold,:add_date)"
                        " ON DUPLICATE KEY UPDATE nick = :nick, avatar = :avatar, gold = gold + :gold", {
            'uid':uid,
            'nick':nick,
            'avatar':avatar,
            'gold':gold,
            'add_date':time.strftime('%Y-%m-%d'),
            'vip':vip,
        }).rowcount

    @staticmethod
    def add_make_money_top(session, uid, nick, avatar, gold, vip):
        result = session.execute("INSERT INTO rank_make_money_top(uid,nick,avatar,gold,add_year,week_of_year) VALUES (:uid,:nick,:avatar,:gold,:add_year,:week_of_year)"
                        " ON DUPLICATE KEY UPDATE nick = :nick, avatar = :avatar, gold = gold + :gold", {
            'uid':uid,
            'nick':nick,
            'avatar':avatar,
            'gold':gold,
            'add_year':time.strftime('%Y'),
            'week_of_year':time.strftime('%W'),
            'vip':vip,
        }).rowcount

class BrokeObject:

    @staticmethod
    def query_broke(uid, r, vip_conf):
        # 根据用户vip体系，查询得到用户可领取的次数总数
        total = vip_conf['relief_time']
        # conf文件读取每次领取金额数
        good = vip_conf['relief_good']
        key = 'broke:'+str(uid)
        if r.exists(key):
            remain = int(r.get(key))
        else:
            remain = total

        return total,remain,good

    @staticmethod
    def receive_broke(service, session,user, vip_conf):
        # 根据用户vip体系，查询得到用户可领取的次数总数
        total = vip_conf['relief_time']
        # conf文件读取每次领取金额数
        good = vip_conf['relief_good']
        key  = 'broke:'+str(user.id)
        if service.redis.exists(key):
            remain = int(service.redis.get(key))
            if remain == 0:
                return RESULT_FAILED_BROKE_FULL,0
            else:
                # 给用户加金币操作
                user.modify_gold(session, good)
                remain = service.redis.decr(key)
                return 0,good
        else:
            # 给用户加金币操作
            user.modify_gold(session, good)
            service.redis.set(key, total)
            t = time.time()
            service.redis.expire(key, int(( t - ( t % 86400 ) + time.timezone ) + 86400 - t) )
            remain = int(service.redis.decr(key))
            print 'first plus gold'
            return 0,good


class VIPObject:

    @staticmethod
    def get_vip(exp):
       if charge > VIP_CHARGE_MAP[0][0] and charge < VIP_CHARGE_MAP[1][0]:
           return 0
       elif charge >= VIP_CHARGE_MAP[1][0] and charge < VIP_CHARGE_MAP[2][0]:
           return 1
       elif charge >= VIP_CHARGE_MAP[2][0] and charge < VIP_CHARGE_MAP[3][0]:
           return 2
       elif charge >= VIP_CHARGE_MAP[3][0] and charge < VIP_CHARGE_MAP[4][0]:
           return 3
       elif charge >= VIP_CHARGE_MAP[4][0] and charge < VIP_CHARGE_MAP[5][0]:
           return 4
       elif charge >= VIP_CHARGE_MAP[5][0] and charge < VIP_CHARGE_MAP[6][0]:
           return 5
       elif charge >= VIP_CHARGE_MAP[6][0] and charge < VIP_CHARGE_MAP[7][0]:
           return 6
       elif charge >= VIP_CHARGE_MAP[7][0] and charge < VIP_CHARGE_MAP[8][0]:
           return 7
       elif charge >= VIP_CHARGE_MAP[8][0] and charge < VIP_CHARGE_MAP[9][0]:
           return 8
       elif charge >= VIP_CHARGE_MAP[9][0] and charge < VIP_CHARGE_MAP[10][0]:
           return 9
       elif charge >= VIP_CHARGE_MAP[10][0] and charge < VIP_CHARGE_MAP[11][0]:
           return 10
       elif charge >= VIP_CHARGE_MAP[11][0]:
           return 10
       else:
           return 0

    @staticmethod
    def set_vip(session, service, user, exp):
        if vip >= len(VIP_CONF):
            return

        vip = VIPObject.get_vip(exp)

        if user.vip == vip:
            return

        user.vip = vip
        user.exp = exp
        service.da.save_user(session, user)

        # 送物品
        bag = BagObject(session)
        if VIP_CONF[vip]['horn_card'] > 0:
            bag.save_user_item(user.id, ITEM_MAP['horn'][0], VIP_CONF[vip]['horn_card'])
        if VIP_CONF[vip]['kick_card'] > 0:
            bag.save_user_item(user.id, ITEM_MAP['kick'][0], VIP_CONF[vip]['kick_card'])


    @staticmethod
    def check_vip_auth(vip, auth):
        conf = VIP_CONF[vip]
        if auth in conf:
            return True
        return False


class ItemObject:

    @staticmethod
    def get_items(session, item_ids):
        return session.execute('SELECT * FROM item WHERE id IN ('+ ','.join(item_ids) +')').fetchall()

    @staticmethod
    def get_user_item(self, user, item_id):
        return self.session.query(TItem).filter(TItem.id == item_id).first()