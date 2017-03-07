#coding: utf-8

import json
import logging
import traceback

import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time
from datetime import datetime
from datetime import date


from services import GameService
from message.base import *
from message.resultdef import *

from db.connect import *
from db.account import *
from db.user_goldflower import *
from db.announcement import *
from db.reward_code import *
from db.reward_code_record import *
from db.reward_task import *
from db.reward_user_log import *
from db.reward_signin import *
from db.reward_sigin_month import *
from db.shop_item import *
from db.trade import *
from db.item import *
from db.gift import *
from db.bag_gift import *
from db.bag_item import *
from db.bank_account import *
from db.user import *
from db.mail import *

from proto.hall_pb2 import *
from proto.access_pb2 import *
from proto.constant_pb2 import *
from proto.struct_pb2 import *
from proto.chat_pb2 import *
from proto.reward_pb2 import *
from proto.trade_pb2 import *
from proto.bag_pb2 import *
from proto.bank_pb2 import *
from proto.mail_pb2 import *
from util.handlerutil import *

from config.var import *
from helper import protohelper
from helper import levelhelper
from helper import cachehelper

from dal.core import *
from hall.hallobject import *
class HallService(GameService):

    def setup_route(self):
        self.registe_command(QueryHallReq,QueryHallResp,self.handle_query_hall)
        self.registe_command(QueryUserReq,QueryUserResp,self.handle_query_user)
        self.registe_command(UpdateUserReq,UpdateUserResp,self.handle_update_user)
        self.registe_command(QueryAnnouncementsReq,QueryAnnouncementsResp,self.handle_annoucement)
        self.registe_command(QueryRewardsReq,QueryRewardsResp,self.handle_rewards)
        self.registe_command(ReceiveRewardReq,ReceiveRewardResp,self.handle_rewards_receive)

        self.registe_command(SendChatReq,SendChatResp,self.handle_send_chat)
        self.registe_command(ReceiveCodeRewardReq,ReceiveCodeRewardResp,self.handle_code_reward)
        self.registe_command(QuerySigninRewardReq,QuerySigninRewardResp,self.handle_query_signin)
        self.registe_command(SigninReq,SigninResp,self.handle_signin)

        # 商城、交易
        self.registe_command(QueryShopReq,QueryShopResp,self.handle_shop)
        self.registe_command(BuyItemReq,BuyItemResp,self.handle_shop_buy)
        self.registe_command(QueryTradeReq,QueryTradeResp,self.handle_trade)
        self.registe_command(BuyTradeReq,BuyTradeResp,self.handle_trade_buy)
        self.registe_command(SellGoldReq,SellGoldResp,self.handle_sell_gold)

        # 背包
        self.registe_command(QueryBagReq,QueryBagResp,self.handle_bag)
        # 银行
        self.registe_command(QueryBankReq,QueryBankResp,self.handle_bank)
        self.registe_command(SaveMoneyReq,SaveMoneyResp,self.handle_bank_save)

        # 信箱
        self.registe_command(SendMailReq,SendMailResp,self.handle_send_mail)
        self.registe_command(FetchMailReq,FetchMailResp,self.handle_fetch_mail)
        self.registe_command(ReceiveAttachmentReq,ReceiveAttachmentResp,self.handle_receive_mail)


    def init(self):
        self.redis = self.server.redis
        self.da = DataAccess(self.redis)

        gevent.spawn(self.handle_notification_queue)

    def handle_notification_queue(self):
        while True:
            _,data = self.redis.brpop("notification_queue")
            json_object = json.loads(data)

            users = json_object['users']
            event = create_client_event(NotificationEvent)
            event.body.type = json_object['notifi_type']
            event.body.param1 = json_object['param1']
            event.body.param2 = json.dumps(json_object['param2'])
            event_data = event.encode()

            for user in users:
                access_service = self.redis.hget("online",user)
                if access_service == None:
                    continue
                access_service = int(access_service)
                user = int(user)
                self.send_client_event(access_service,user,event.header.command,event_data)

    @USE_TRANSACTION
    def handle_send_mail(self,session,req,resp,event):

        print '11111111111111111111111111111111111111'
        print req.body

        try:
            MessageObject(self.da,session).send_mail((1),{
                'to':req.body.to,
                'title':req.body.title,
                'content':req.body.content,
                'from_user':req.header.user,
                'type':0,
            })
        except Exception as e:
            print e.message
            print 'error...............................'
            resp.header.result = -1
            return
        resp.header.result = 0



    @USE_TRANSACTION
    def handle_fetch_mail(self,session,req,resp,event):
        mails = session.query(TMail).filter(and_(TMail.to_user == req.header.user, TMail.id > req.body.max_mail_id)).all()

        for item in mails:
            protohelper.set_mail(resp.body.mails.add(), item)

        resp.header.user = 0

    @USE_TRANSACTION
    def handle_receive_mail(self,session,req,resp,event):
        mail = session.query(TMail).filter(and_(TMail.to_user == req.header.user,TMail.type == 1,TMail.state == 1)).first()
        user_info = self.da.get_user(req.header.user)

        if mail == None or user_info == None:
            resp.header.result = -1
            return

        user_info.gold = user_info.gold + mail.gold
        user_info.diamond = user_info.diamond + mail.gold

        self.da.save_user(session,user_info)
        session.query(TMail).with_lockmode("update").filter(and_(TMail.to_user == req.header.user,TMail.type == 1,TMail.state == 1)).update({
            TMail.state:0
        })

        self.get_result(user_info,resp)
        resp.header.result = 0


    @USE_TRANSACTION
    def handle_query_signin(self,session,req,resp,event):
        user = session.query(TUser).filter(TUser.id == req.header.user).first()
        signs = session.query(TRewardSignin).all()
        for item in signs:
            protohelper.set_signs(resp.body.rewards.add(), item)

        user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == req.header.user).first()
        resp.body.signin_days = user_gf.signin_days

        signin_month = session.query(TRewardSigninMonth).filter(and_(TRewardSigninMonth.uid == req.header.user, \
                                                                     func.month(TRewardSigninMonth.last_signin_day) == time.strftime('%m'), \
                                                                     func.year(TRewardSigninMonth.last_signin_day) == time.strftime('%Y'))).first()
        if signin_month != None:
            resp.body.month_sigin_days = signin_month.signin_days
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_signin(self,session,req,resp,event):
        user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == req.header.user).first()
        if user_gf == None:
            resp.header.result = RESULT_FAILED_ACCOUNT_EMPTY
            return
        user = self.da.get_user(req.header.user)
        # 1.判断今日是否已经签到
        signs = session.query(TRewardSignin).all()
        if user_gf.last_signin_day != None:
            diff_day = (date.today() - user_gf.last_signin_day).days
        else:
            diff_day = 1

        index = user_gf.signin_days
        if diff_day == 0:
            resp.header.result = RESULT_FAILED_TODAY_SIGNED
            return
        elif diff_day > 1:
            index = 0
            # 3.修改用户扩展表的最后签到时间和签到天数（签到天数必须判断是否是连续签到）
            session.query(TUserGoldFlower).with_lockmode("update").filter(TUserGoldFlower.id == user_gf.id).update({
                TUserGoldFlower.signin_days: 1,
                TUserGoldFlower.last_signin_day : time.strftime('%Y-%m-%d')
            })
        elif diff_day == 1:
            # 3.修改用户扩展表的最后签到时间和签到天数（签到天数必须判断是否是连续签到）
            session.query(TUserGoldFlower).with_lockmode("update").filter(TUserGoldFlower.id == user_gf.id).update({
                TUserGoldFlower.signin_days: TUserGoldFlower.signin_days + 1,
                TUserGoldFlower.last_signin_day : time.strftime('%Y-%m-%d')
            })
            if user_gf.signin_days >= SYS_MAX_SIGN_DAY:
                index = SYS_MAX_SIGN_DAY - 1

        user.gold = user.gold + signs[index].gold
        user.diamond = user.diamond + signs[index].diamond
        self.da.save_user(session,user)

        # 2.插入签到累计数据表或者修改数据表（签到天数）
        signin_month = session.query(TRewardSigninMonth).filter(TRewardSigninMonth.uid == user_gf.id).first()
        if signin_month == None:
            # 需要创建该条记录,说明该用户为首次使用该游戏
            signin_month = TRewardSigninMonth()
            signin_month.uid = user_gf.id
            signin_month.signin_days = 1
            signin_month.last_signin_day = time.strftime('%Y-%m-%d')
            session.add(signin_month)
        else:
            total_signin_day = TRewardSigninMonth.signin_days + 1
            session.query(TRewardSigninMonth).with_lockmode("update").filter(TRewardSigninMonth.uid == user_gf.id).update({
                        TRewardSigninMonth.signin_days: total_signin_day,
                        TRewardSigninMonth.last_signin_day : time.strftime('%Y-%m-%d')
            })
            # 月累计签到，奖励日，todo...待道具模块完成
            if total_signin_day in PRM_SIGN_LUCK_DAYS:
                pass

        resp.body.result.gold = signs[index].gold
        resp.body.result.diamond = signs[index].diamond
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_query_hall(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        if user_info == None:
            resp.header.result = RESULT_FAILED_ACCOUNT_EMPTY
            return

        user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == req.header.user).first()
        #user_gf = self.da.get_user_gf(req.header.user)
        if user_gf == None:
            # 需要创建该条记录,说明该用户为首次使用该游戏
            user_gf = TUserGoldFlower()
            user_gf.id = req.header.user
            user_gf.channel = user_info.channel
            user_gf.exp = DEFAULT_USER_GLODFLOWER['exp']
            user_gf.win_games = DEFAULT_USER_GLODFLOWER['win_games']
            user_gf.total_games = DEFAULT_USER_GLODFLOWER['total_games']
            user_gf.best = DEFAULT_USER_GLODFLOWER['best']
            user_gf.create_time = now
            user_gf.max_bank = DEFAULT_USER_GLODFLOWER['max_bank']
            user_gf.max_items = DEFAULT_USER_GLODFLOWER['max_items']
            user_gf.max_gifts = DEFAULT_USER_GLODFLOWER['max_gifts']
            user_gf.signin_days = DEFAULT_USER_GLODFLOWER['signin_days']
            user_gf.last_signin_day = DEFAULT_USER_GLODFLOWER['last_signin_day']
            user_gf.change_nick = DEFAULT_USER_GLODFLOWER['change_nick']
            session.add(user_gf)

        resp.body.brief.nick = user_info.nick
        resp.body.brief.uid = user_info.id
        resp.body.brief.avatar = user_info.avatar
        resp.body.brief.gold = user_info.gold
        resp.body.brief.seat = -1
        resp.body.brief.vip = user_info.vip
        resp.body.brief.diamond = user_info.diamond

        # 获取通知信息 todo...mail功能暂时没有做
        has_reward_count = session.query(TRewardUserLog).filter(and_(TRewardUserLog.state == STATE_NO_ACCEPT_REWARD, TRewardUserLog.uid == user_info.id)).count()
        has_announcement_count = session.query(TAnnouncement).filter(and_(TAnnouncement.id > req.body.max_announcement_id, TAnnouncement.start_time <= now, now <= TAnnouncement.end_time)).count()

        resp.body.notification.has_announcement = has_announcement_count if has_announcement_count > 0 else 0
        resp.body.notification.has_reward = has_reward_count if has_reward_count > 0 else 0
        # 获取公告信息
        announcements = session.query(TAnnouncement).filter(and_(TAnnouncement.start_time <= now, \
                                                              TAnnouncement.end_time>=now, \
                                                              TAnnouncement.popup == STATE_NEED_POPUP)).order_by(TAnnouncement.sort).all()
        for item in announcements:
            protohelper.set_announcement(resp.body.announcements.add(), item)

        # 签到验证
        resp.body.is_signin = True
        if user_gf.last_signin_day != None:
            diff_day = (date.today() - user_gf.last_signin_day).days
        else:
            diff_day = 1

        if diff_day > 1:
            session.query(TUserGoldFlower).with_lockmode("update").filter(TUserGoldFlower.id == user_info.id).update({
                        TUserGoldFlower.signin_days: 0
            })
            resp.body.is_signin = False
        elif diff_day == 1 :
            resp.body.is_signin = False
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_query_user(self,session,req,resp,event):
        if req.body.uid <= 0 or req.body.uid == None:
            resp.header.result = -1
            return
        user_info = session.query(TUser).filter(TUser.id == req.body.uid).first()
        if user_info == None:
            resp.header.result = RESULT_FAILED_ACCOUNT_EMPTY
            return

        user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == req.body.uid).first()
        if user_gf == None:
            resp.header.result = -1
            return

        protohelper.set_player(resp.body.player,user_info,user_gf)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_update_user(self,session,req,resp,event):
        # user = session.query(TUser).filter(TUser.id == req.header.user).first()
        user_info = self.da.get_user(req.header.user)
        user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == req.header.user).first()
        if len(req.body.nick) >= 0:
            if user_gf.change_nick == 0:
                resp.header.result = -1
                resp.body.result.gold = 0
                resp.body.result.diamond = 0
                return

            if user_info.diamond < PRM_CHANGE_NAME_MINUS_DIAMOND:
                resp.header.result = -2
                resp.body.result.gold = 0
                resp.body.result.diamond = 0
                return

            user_info.nick =  req.body.nick
            user_info.diamond =  user_info.diamond - PRM_CHANGE_NAME_MINUS_DIAMOND
            self.da.save_user(session,user_info)
            session.query(TUserGoldFlower).with_lockmode("update").filter(TUserGoldFlower.id == req.header.user).update({
                TUserGoldFlower.change_nick : 0
            })
        else:
            data = {}
            if len(req.body.birthday) > 0:
                user_info.birthday = req.body.birthday
            if len(req.body.sign)  > 0:
                user_info.sign = req.body.sign
            if len(req.body.avatar) > 0:
                user_info.avatar = req.body.avatar
            if len(req.body.sex) > 0:
                user_info.sex = req.body.sex
            session.query(TUser).with_lockmode("update").filter(TUser.id == req.header.user).update(data)

            result = session.query(TRewardUserLog).filter(TRewardUserLog.uid == user.id).first()

            if result == None:
                # 完成任务，加入奖励记录，记录状态用户待接收
                reward_log = TRewardUserLog()
                reward_log.uid = user.id
                reward_log.task_id = 1
                reward_log.state = STATE_NO_ACCEPT_REWARD
                reward_log.finish_date = time.strftime('%Y-%m-%d')
                reward_log.create_time = time.strftime('%Y-%m-%d %H:%M:%S')
                session.add(reward_log)

        # 发送用户修改成功广播
        # self.add_notification_queue(self.redis.hkeys('online'), BORADCAST_CHANGE_NAME,{'nick':req.body.nick,"nick_color":REGISTER_NICK_COLOR})
        cachehelper.add_notification_queue(self.redis,self.redis.hkeys('online'), BORADCAST_CHANGE_NAME,{'nick':req.body.nick,"nick_color":REGISTER_NICK_COLOR})
        resp.body.result.gold = 0
        resp.body.result.diamond = -PRM_CHANGE_NAME_MINUS_DIAMOND
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_annoucement(self,session,req,resp,event):
        today = time.strftime("%Y-%m-%d %H:%M:%S")
        annoucements = session.query(TAnnouncement).filter(and_(TAnnouncement.start_time<= today, \
                                                         TAnnouncement.end_time >=today)).order_by(TAnnouncement.sort).all()
        if len(annoucements) <= 0:
            return

        for item in annoucements:
            protohelper.set_announcement(resp.body.announcements.add(), item)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_rewards(self,session,req,resp,event):
        rewards = session.query(TRewardTask).all()
        reward_logs = session.query(TRewardUserLog).filter(TRewardUserLog.uid == req.header.user).all()
        if len(rewards) <= 0:
            resp.header.result = -1
            return

        for item in rewards:
            protohelper.set_reward(resp.body.rewards.add(), item, reward_logs)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_rewards_receive(self,session,req,resp,event):
        try:
            task = session.query(TRewardTask).filter(TRewardTask.id == req.body.reward_id).first()
            if task == None:
                resp.header.result = -1
                return

            task_log = session.query(TRewardUserLog).filter(and_(TRewardUserLog.uid == req.header.user,TRewardUserLog.task_id == req.body.reward_id)).first()
            if task_log == None or task_log.state == 0:
                resp.header.result = -1
                return

            session.query(TUser).with_lockmode("update").filter(TUser.id == req.header.user).update({
                        TUser.gold: TUser.gold + task.gold,
                        TUser.diamond: TUser.diamond + task.diamond
            })
            session.query(TRewardUserLog).with_lockmode("update").filter(and_(TRewardUserLog.uid == req.header.user, TRewardUserLog.task_id == req.body.reward_id,TRewardUserLog.state == 1)).update({
                TRewardUserLog.state: 0
            })

        except Exception as e:
            print e.message
            resp.header.result = -1
            return

        resp.body.result.gold = task.gold
        resp.body.result.diamond = task.diamond
        user_info = session.query(TUser).filter(TUser.id == req.header.user).first()
        cachehelper.add_notification_queue(self.redis,self.redis.hkeys('online'), BORADCAST_CHANGE_NAME,{'nick':user_info.nick,"nick_color":REGISTER_NICK_COLOR})
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_send_chat(self,session,req,resp,event):
         user_info = self.da.get_user(req.header.user)
         if user_info == None:
             return
         if req.body.table_id <= 0:
            cachehelper.add_notification_queue(self.redis,self.redis.hkeys('online'), BORADCAST_SEND_CHAT,{'message':req.body.message,'nick_id':user_info.id,'nick':user_info.nick,"nick_color":REGISTER_NICK_COLOR})
         elif req.body.table_id > 0:
             keys = self.redis.keys("table_*_" + str(req.body.table_id))
             if len(keys) != 1:
                 resp.header.result = -1
                 return
             table = self.redis.hgetall(keys[0])
             if table != None:
                event = create_client_event(ChatEvent)
                event.body.sender = req.header.user
                event.body.table_id = req.body.table_id
                event.body.message = req.body.message
                event_data = event.encode()
                users = table.keys()
                print users
                for user in users:
                    access_service = self.redis.hget("online",user)
                    if access_service == None:
                        continue
                    access_service = int(access_service)
                    user = int(user)
                    self.send_client_event(access_service,user,event.header.command,event_data)
         else:
             resp.header.result -2
             return
         resp.header.result = 0

    @USE_TRANSACTION
    def handle_code_reward(self,session,req,resp,event):
        reward_code = session.query(TRewardCode).filter(TRewardCode.code == req.body.code).first()

        if reward_code == None:
            resp.header.result = -1
            return

        if time.mktime(reward_code.expired_at.timetuple()) <= time.time():
            resp.header.result = RESULT_FAILED_CODE_EXPIRED
            return

        if reward_code.total <= reward_code.used:
            resp.header.result = RESULT_FAILED_CODE_FILL
            return

        reward_code_log = session.query(TRewardCodeRecord).filter(and_(TRewardCodeRecord.code_id == reward_code.id, \
                                                                       TRewardCodeRecord.uid == req.header.user)).first()
        if reward_code_log != None:
            resp.header.result = -2
            return
        try:
            code_record = TRewardCodeRecord()
            code_record.code_id = reward_code.id
            code_record.uid = req.header.user
            code_record.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
            session.add(code_record)

            session.query(TRewardCode).with_lockmode("update").filter(and_(TRewardCode.code == req.body.code, TRewardCode.total>TRewardCode.used)).update({
                        TRewardCode.used: TRewardCode.used + 1,
            })

            session.query(TUser).with_lockmode("update").filter(TUser.id == req.header.user).update({
                        TUser.gold: TUser.gold + reward_code.gold,
                        TUser.diamond: TUser.diamond + reward_code.diamond
            })

        except Exception as e:
            print e.message
            resp.header.result = -3
            return

        resp.body.result.gold = reward_code.gold
        resp.body.result.diamond = reward_code.diamond

        resp.header.user = 0

    @USE_TRANSACTION
    def handle_shop(self,session,req,resp,event):
        shopitem = session.query(TShopItem).all()
        items = session.query(TItem).all()
        for spi in shopitem:
            protohelper.set_shop_item(resp.body.items.add(), spi, items)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_shop_buy(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        shopitem = session.query(TShopItem).filter(TShopItem.id == req.body.shop_item_id).first()

        if ShopObject(self.da,session).buy(user_info, shopitem, req) == False:
            resp.header.result = RESULT_FAILED_SHOP
            return

        item = session.query(TItem).filter(TItem.id == shopitem.item_id).first()
        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond

        item_add = resp.body.result.items_added.add()
        item_add.id = item.id
        item_add.name = item.name
        item_add.icon = item.icon
        item_add.count = req.body.count
        item_add.description = item.description
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_trade(self,session,req,resp,event):
        page = req.body.page
        page_size = req.body.page_size
        can_buy = req.body.can_buy

        if can_buy:
            user_info = self.da.get_user(req.header.user)
            trades_count = session.query(TTrade).filter(and_(TTrade.diamond <= user_info.diamond,TTrade.buyer == None)).count()
            trades = session.query(TTrade).filter(and_(TTrade.diamond <= user_info.diamond,TTrade.buyer == None)).order_by(TTrade.id).offset((int(page) - 1) * page_size).limit(page_size)
        else:
            trades_count = session.query(TTrade).filter(TTrade.buyer == None).count()
            trades = session.query(TTrade).filter(TTrade.buyer == None).order_by(TTrade.id).offset((int(page) - 1) * page_size).limit(page_size)

        for item in trades:
            protohelper.set_trades(resp.body.trades.add(), item,self.da.get_user(item.seller))
        resp.body.total = trades_count
        resp.header.user = 0

    @USE_TRANSACTION
    def handle_trade_buy(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        try:

            result = session.query(TTrade).with_lockmode("update").filter(and_(TTrade.id == req.body.trade_id, \
                                                                               TTrade.buyer == None)).update({
                TTrade.buyer : user_info.id,
                TTrade.buy_time : datetime.now(),
            })
            if result != 1:
                resp.header.result = -1
                return
        except Exception as e:
            print e.message
            resp.header.result = -1
            return

        self.get_result(user_info, resp)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_sell_gold(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        if user_info.gold < req.body.gold:
            resp.header.result = -1
            return

        trade = TTrade()
        trade.seller = req.header.user
        trade.gold = req.body.gold
        trade.diamond = req.body.diamond
        trade.sell_time = datetime.now()
        session.add(trade)

        self.get_result(user_info, resp)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_bag(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        if user_info == None:
            resp.header.result = -1
            return

        items = session.query(TItem).all()
        gifts = session.query(TGift).all()

        # load item
        user_items = session.query(TBagItem).filter(TBagItem.uid == req.header.user).all()
        for user_item in user_items:
            protohelper.set_bag_item(resp.body.items.add(), user_item, items)

        # load bag
        user_gifts = session.query(TBagGift).filter(TBagGift.uid == req.header.user).all()
        for user_gift in user_gifts:
            protohelper.set_bag_gift(resp.body.gifts.add(), user_gift, gifts)

        resp.header.result = 0

    @USE_TRANSACTION
    def handle_bank(self,session,req,resp,event):
        bank_account = session.query(TBankAccount).filter(TBankAccount.uid == req.header.user).first()
        if bank_account == None:
            resp.header.user = -1
            return
        user_info = self.da.get_user(req.header.user)
        resp.body.gold = bank_account.gold
        resp.body.limit = levelhelper.get_level_max(user_info)
        resp.body.next_vip_limit = BANK_LELVEL_LIMIT[levelhelper.get_level(user_info) + 1]
        resp.header.user = 0

    @USE_TRANSACTION
    def handle_bank_save(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        if req.body.type == BANK_ACT_SAVE :
            if user_info.gold < req.body.gold:
                resp.header.result = -1
                return
            user_info.gold = user_info.gold - req.body.gold
            print req.body.gold,type(req.body.gold),int(req.body.gold)
            BankObject(self.da,session).bank_save(user_info, req.body.gold)

        elif req.body.type == BANK_ACT_GET :
            bank_account = session.query(TBankAccount).filter(TBankAccount.uid == req.header.user).first()
            if bank_account == None or bank_account.gold < req.body.gold:
                resp.header.result = -1
                return
            bank_account.gold = bank_account.gold - req.body.gold
            user_info.gold = user_info.gold + req.body.gold
            print '----------------------------->get',bank_account.gold,user_info.gold
            # self.da.save_user(user_info)
            # user_info.modify_gold(session,user_info.gold + req.body.gold)
        else:
            resp.header.result = -1
            return
        resp.header.result = 0

    def get_result(self,user,resp):
        resp.body.result.gold = user.gold
        resp.body.result.diamond = user.diamond

if __name__ == "__main__":
    pass

