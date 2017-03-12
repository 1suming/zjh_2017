#coding: utf-8

import json
import logging
import traceback

import sys
import binascii
import decimal
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
from db.friend import *
from db.friend_apply import *
from db.feedback import *
from db.order import *
from db.charge_item import *
from db.charge_record import *
from db.customer_service_log import *
from db.system_achievement import *
from db.game_achievement import *

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
from proto.friend_pb2 import *
from proto.rank_pb2 import *
from util.handlerutil import *

from config.var import *
from config.reward import *
from config.item import *
from config.sign import *
from config.mail import *
from config.broadcast import *
from helper import protohelper
from helper import cachehelper
from helper import datehelper

from dal.core import *
from hall.hallobject import *
from hall.eventsender import *
from task.achievementtask import *
from task.dailytask import *

reload(sys)
sys.setdefaultencoding('utf8')

class HallService(GameService):

    def init(self):
        self.redis = self.server.redis
        self.da = DataAccess(self.redis)
        self.manager = Manager(self)
        self.sender = EventSender(self.manager)
        gevent.spawn(self.queue_notification)
        gevent.spawn(self.say_hello)
        gevent.spawn_later(10, self.say_hello_2)
        # gevent.spawn(self.queue_charge)

        self.bag = BagObject(self)
        self.hall = HallObject(self)
        self.user_gf = UserGoldFlower(self)
        self.sign = SignObject(self)
        self.friend = FriendObject(self)
        self.rank = RankObject(self)
        self.shop = ShopObject(self)
        self.item = ItemObject(self)
        self.reward = RewardObject(self)
        self.userobj = UserObject(self)
        self.vip = VIPObject(self)
        self.broke = BrokeObject(self)
        self.trade = TradeObject(self)
        self.profile = Profile(self)

        self.daliy_task = DailyTaskManager(self.redis)


    # 系统自定义广播，定时发送
    def say_hello(self):
        while True:
            MessageObject.push_message(self, self.redis.hkeys('online'), PUSH_TYPE['sys_broadcast'],{'message':BORADCAST_CONF['sys']} )
            gevent.sleep(NOTI_TIME)

    def say_hello_2(self):
        while True:
            MessageObject.push_message(self, self.redis.hkeys('online'), PUSH_TYPE['sys_broadcast'],{'message':BORADCAST_CONF['sys2']} )
            gevent.sleep(NOTI_TIME_2)

    def queue_charge(self):
        while True:
            _,charge = self.redis.brpop("queue_charge")
            order = session.query(TOrder).filter(TOrder.order_sn == charge['order_sn']).first()
            if order == None or order != 0:
                continue

            # 告知客户端已经充值成功
            # event = create_client_event(NotificationEvent)
            # event.body.type = NotificationType.N_CHARGE
            # self.sender.send_event([order.uid],event)

            # "type":10,
            # "money":33.99,
            # "diamond":6,
            # "gold":0,

            # 充值成功，给客户端发送消息
            event = create_client_event(NotificationEvent)
            event.body.type = NotificationType.N_MAIL
            event.body.param1 = 10
            event.body.param2 = json.dumps({'money':order.charge,'gold':charge['gold'],'diamond':charge['diamond']})
            if self.manager.offline(order.uid) != 0:
                MessageObject.push_message(self, [order.uid], PUSH_TYPE['charge_success'], {'money':str(order.charge),'diamond':0,'gold':''})


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

        # 破产补助
        self.registe_command(QueryBankcruptRewardReq,QueryBankcruptRewardResp,self.handle_query_bankcrupt)
        self.registe_command(ReceiveBankcruptRewardReq,ReceiveBankcruptRewardResp,self.handle_receive_bankcrupt)

        # 排行
        self.registe_command(QueryRankReq, QueryRankResp, self.handle_rank)

        # 牌桌奖励
        self.registe_command(ResetPlayRewardReq, ResetPlayRewardResp, self.handle_reset_play_reward)
        self.registe_command(ReceivePlayRewardReq, ReceivePlayRewardResp, self.handle_receive_play_reward)
        self.registe_command(RecordPlayRewardReq, RecordPlayRewardResp, self.handle_record_play_reward)

        # 商城、交易
        self.registe_command(QueryShopReq,QueryShopResp,self.handle_shop)
        self.registe_command(BuyItemReq,BuyItemResp,self.handle_shop_buy)
        self.registe_command(QueryTradeReq,QueryTradeResp,self.handle_trade)
        self.registe_command(BuyTradeReq,BuyTradeResp,self.handle_trade_buy)
        self.registe_command(SellGoldReq,SellGoldResp,self.handle_sell_gold)
        self.registe_command(OutGoldReq,OutGoldResp,self.handle_out_gold)

        # 背包
        self.registe_command(QueryBagReq,QueryBagResp,self.handle_bag)

        # 使用道具
        self.registe_command(UseItemReq,UseItemResp,self.handle_use_bag)

        # 银行
        self.registe_command(QueryBankReq,QueryBankResp,self.handle_bank)
        self.registe_command(SaveMoneyReq,SaveMoneyResp,self.handle_bank_save)

        # 信箱
        self.registe_command(SendMailReq,SendMailResp,self.handle_send_mail)
        self.registe_command(FetchMailReq,FetchMailResp,self.handle_fetch_mail)
        self.registe_command(ReceiveAttachmentReq,ReceiveAttachmentResp,self.handle_receive_mail)

        # 好友
        self.registe_command(GetFriendsReq,GetFriendsResp,self.handle_get_friends)
        self.registe_command(GetFriendAppliesReq,GetFriendAppliesResp,self.handle_get_friends_applies)
        self.registe_command(SendFriendMessageReq,SendFriendMessagetResp,self.handle_send_friends_message)
        self.registe_command(MakeFriendReq,MakeFriendResp,self.handle_make_friends)
        self.registe_command(HandleFriendApplyReq,HandleFriendApplyResp,self.handle_friends_apply)
        self.registe_command(ReceiveFriendMessageReq,ReceiveFriendMessageResp,self.handle_receive_friends_message)
        self.registe_command(RemoveFriendMessageReq,RemoveFriendMessageResp,self.handle_remove_friends)

        # 意见反馈
        self.registe_command(FeedBackReq,FeedBackResp,self.handle_feedback)

        # 生成订单
        self.registe_command(CreateOrderReq,CreateOrderResp,self.handle_create_order)

        # 充值
        self.registe_command(QueryChargeReq,QueryChargeResp,self.handle_charge)

        # 快速补币
        self.registe_command(QueryQuickBuyGoldReq,QueryQuickBuyGoldResp,self.handle_quick_charge)

        # 首冲
        self.registe_command(QueryFirstTimeChargeReq,QueryFirstTimeChargeResp,self.handle_first_charge)

        # 注册、修改手机
        self.registe_command(BindMobileReq,BindMobileResp,self.handle_bind_mobile)

    # 破产补助查询
    @USE_TRANSACTION
    def handle_query_bankcrupt(self, session, req, resp, event):
        user_info = self.da.get_user(req.header.user)
        resp.body.total,resp.body.remain,resp.body.gold = BrokeObject.query_broke(req.header.user,self.redis, VIP_CONF[self.vip.to_level(user_info.vip_exp)] )
        resp.header.result = 0

    # 破产补助领取
    @USE_TRANSACTION
    def handle_receive_bankcrupt(self, session, req, resp, event):
        user_info = self.da.get_user(req.header.user)

        resp.header.result,resp.body.gold = BrokeObject.receive_broke(self,session,user_info, VIP_CONF[self.vip.to_level(user_info.vip_exp)])

    # 排名查询
    @USE_TRANSACTION
    def handle_rank(self, session, req, resp, event):

        # // 排行榜类型
        # enum RankType {
        # 	RANK_WEALTH = 1;
        # 	RANK_CHARGE = 2;
        # 	RANK_CHARM = 3;
        # 	RANK_MAKE_MONEY = 4;
        # }
        #
        # // 排行榜参数
        # enum RankTime{
        # 	RANK_ALL_TIME = 0;
        # 	RANK_YESTERDAY = 1;
        # 	RANK_TODAY = 2;
        # 	RANK_LAST_MONTH = 3;
        # 	RANK_THIS_MONTH = 4;
        # 	RANK_LAST_WEEK = 5;
        # 	RANK_THIS_WEEK = 6;
        # }
        items = []
        if req.body.rank_type == RANK_WEALTH:
            # 总财富榜
            items = self.rank.wealth_top(session, 0)
        elif req.body.rank_type == RANK_CHARGE:
            # 日充值榜
            items = self.rank.charge_top(session, req.body.rank_time)
        elif req.body.rank_type == RANK_MAKE_MONEY:
            # 周赚金榜
            items = self.rank.make_money_top(session, req.body.rank_time)

        for index in range(len(items)):

            protohelper.set_top(resp.body.players.add(), items[index], index)
        resp.header.result = 0


        resp.header.result = 0


    @USE_TRANSACTION
    def handle_get_friends(self,session,req,resp,event):
        page = req.body.page
        page_size = req.body.page_size
        friends = session.query(TFriend).filter(TFriend.apply_uid == req.header.user).offset((int(page) - 1) * page_size).limit(page_size)

        orderby_friends = []
        for friend in friends:
            friend_user = self.da.get_user(friend.to_uid)
            if friend_user == None:
                continue
            print '========>',friend_user.id,friend_user.nick
            if self.redis.hexists('online', friend_user.id):
                orderby_friends.insert(0, friend_user)
            else:
                orderby_friends.append(friend_user)

        for orderby_friend in orderby_friends:
            print '=========>orderBy',orderby_friend.id,orderby_friend.nick
            pb = resp.body.friends.add()
            pb.avatar = orderby_friend.avatar
            pb.gold = orderby_friend.gold
            pb.uid = orderby_friend.id
            pb.nick = orderby_friend.nick
            pb.type = orderby_friend.type

            pb.is_online = False if self.redis.hexists('online',orderby_friend.id) == False else True
            protohelper.set_room_table(pb,orderby_friend.id,self.redis)

        #countof_applies = session.query(TFriendApply).filter(and_(TFriendApply.to_uid == req.header.user, TFriendApply.state == 1)).count()
        # resp.body.countof_applies = countof_applies
        resp.body.countof_applies = len(orderby_friends)
        resp.header.result = 0
    @USE_TRANSACTION
    def handle_get_friends_applies(self,session,req,resp,event):
        page = req.body.page
        page_size = req.body.page_size

        apply_friends = session.query(TFriendApply).filter(and_(TFriendApply.to_uid == req.header.user, TFriendApply.state == 1))\
            .order_by(TFriendApply.id)\
            .offset((int(page) - 1) * page_size).limit(page_size)

        for item in apply_friends:
            temp_user = self.da.get_user(item.apply_uid)
            protohelper.set_friend_applies(resp.body.applies.add(), item, nick = temp_user.nick,avatar = temp_user.avatar)

        resp.header.result = 0
    @USE_TRANSACTION
    def handle_send_friends_message(self,session,req,resp,event):
        from_user = self.da.get_user(req.header.user)

        if req.body.friend_id == 10000:
            log = TCustomerServiceLog()
            log.from_user = from_user.id
            log.to_user = 10000
            log.content = req.body.message
            log.send_time = int(time.time())
            log.user_say = 1
            session.add(log)
            resp.header.result = 0
            return
        event = create_client_event(FriendMessageEvent)
        event.body.message.message_id = self.redis.incr('message_id')
        event.body.message.from_user = req.header.user
        event.body.message.to = req.body.friend_id
        event.body.message.time = int(time.time())
        event.body.message.message = req.body.message
        event.body.message.from_user_nick = from_user.nick
        event.body.message.from_user_avatar = from_user.avatar
        self.sender.send_friend_message(event, req.body.friend_id)
        self.redis.hset('message_'+str(req.body.friend_id),event.body.message.message_id,event.body.SerializeToString())

        resp.header.result = 0

    # 申请好友
    @USE_TRANSACTION
    def handle_make_friends(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        friend_info = self.da.get_user(req.body.target)

        # 自己+自己，直接返回
        if user_info.id == friend_info.id:
            resp.header.result = RESULT_FAILED_INVALID_FRIEND
            return

        # 不能+客服
        if req.body.target == 10000:
            resp.header.result = RESULT_FAILED_INVALID_FRIEND
            return

        # vip验证好友数限制
        my_firend_count = self.friend.get_friends_count(session, user_info.id)
        print '------>',my_firend_count
        if self.vip.over_friend_max( self.vip.to_level(user_info.vip_exp), my_firend_count + 1 ):
            resp.header.result = RESULT_FAILED_FRIEND_MAX
            return

        target_firend_count = self.friend.get_friends_count(session, friend_info.id)
        print '=======>',target_firend_count
        if self.vip.over_friend_max( self.vip.to_level(friend_info.vip_exp), target_firend_count + 1 ):
            resp.header.result = RESULT_FAILED_FRIEND_TARGET_MAX
            return


        resp.header.result = self.friend.make_friend(session, user_info, friend_info, req.body.message)

    # 同意/拒绝好友申请
    @USE_TRANSACTION
    def handle_friends_apply(self,session,req,resp,event):
        friend_info = self.da.get_user(req.header.user)
        apply_record = self.friend.get_friend_apply(session, req.body.apply_id)

        if apply_record.state == 0:
            resp.header.result = RESULT_FAILED_HAS_FRIEND
            return

        user_info = self.da.get_user(apply_record.apply_uid)

        self.friend.make_friend_apply(session, req.body.apply_id, req.body.accept, user_info, friend_info)

        resp.header.result = 0

    @USE_TRANSACTION
    def handle_receive_friends_message(self,session,req,resp,event):
        self.redis.hdel('message_'+str(req.header.user),req.body.message_id)

        resp.header.result = 0

    # 删除好友
    @USE_TRANSACTION
    def handle_remove_friends(self,session,req,resp,event):
        # 不能删除客服
        if req.body.friend_id == 10000:
            resp.header.result = RESULT_FAILED_INVALID_FRIEND
            return

        # 自己删除好友
        session.query(TFriend).filter(and_(TFriend.apply_uid == req.header.user,TFriend.to_uid == req.body.friend_id)).delete()
        # 从好友中删除自己
        session.query(TFriend).filter(and_(TFriend.apply_uid == req.body.friend_id,TFriend.to_uid == req.header.user)).delete()

        # 删除自己申请该好友的记录或者该好友申请自己好友的记录
        session.query(TFriendApply).filter(and_(TFriendApply.apply_uid == req.header.user,TFriendApply.to_uid == req.body.friend_id)).delete()
        session.query(TFriendApply).filter(and_(TFriendApply.apply_uid == req.body.friend_id,TFriendApply.to_uid == req.header.user)).delete()

        user_info_source = self.da.get_user(req.header.user)
        user_info_target = self.da.get_user(req.body.friend_id)
        self.friend.send_mail_remove_friend(session, user_info_source, user_info_target)
        resp.header.result = 0


    # 给指定用户发送邮件
    @USE_TRANSACTION
    def handle_send_mail(self,session,req,resp,event):

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

    # 查询邮件信息
    @USE_TRANSACTION
    def handle_fetch_mail(self,session,req,resp,event):
        mails = session.query(TMail).filter(and_(TMail.to_user == req.header.user, TMail.id > req.body.max_mail_id)).order_by(desc(TMail.sent_time)).limit(100)

        item_ids = []

        for mail in mails:
            if mail.type == 1 and mail.items != None and mail.items != '':
                for s in mail.items.split(','):
                    item_ids.append(s[0])
            else:
                protohelper.set_mail(resp.body.mails.add(), mail)

        if len(item_ids) > 0:
            item_datas = ItemObject.get_items(session, item_ids)

        for mail in mails:
            if mail.type == 1 and mail.items != None and mail.items != '':
                pb_mail = resp.body.mails.add()
                protohelper.set_mail(pb_mail, mail)
                for item in mail.items.split(','):
                    for item_data in item_datas:
                        if int(item[0]) == int(item_data.id):
                            pb_item = pb_mail.items.add()
                            pb_item.id = item_data.id
                            pb_item.icon = item_data.icon
                            pb_item.name = item_data.name
                            pb_item.description = item_data.description
                            pb_item.count = int(item[2])
                            break

        resp.header.user = 0

    # 确认接收邮件
    @USE_TRANSACTION
    def handle_receive_mail(self,session,req,resp,event):
        mail = session.query(TMail).filter(TMail.id == req.body.mail_id).first()
        if mail == None or mail.state == 1:
            resp.header.result = RESULT_FAILED_MAIL
            return

        user_info = self.da.get_user(req.header.user)
        user_info.gold = user_info.gold + mail.gold
        user_info.diamond = user_info.diamond + mail.diamond
        self.da.save_user(session,user_info)

        bag_obj = BagObject(session)
        if mail.items != None and mail.items != '' and len(mail.items) > 0:
            for item_str in mail.items.split(','): # 1-1,2-1,3-1
                bag_obj.save_user_item(session, req.header.user, item_str[0],item_str[2])
                item = ItemObject.get_item(session, item_str[0])
                print '====================>'
                item_add = resp.body.result.items_added.add()
                item_add.id = item.id
                item_add.name = item.name
                item_add.icon = item.icon
                item_add.count = int(item_str[2])
                item_add.description = item.description
                print '=================>',item_add


        session.query(TMail).with_lockmode("update").filter(TMail.id == req.body.mail_id).update({
            TMail.state:1,
            TMail.received_time:int(time.time())
        })

        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond
        resp.body.result.incr_gold = mail.gold
        resp.body.result.incr_diamond = mail.diamond
        resp.header.result = 0

    # 查询签到
    @USE_TRANSACTION
    def handle_query_signin(self,session,req,resp,event):
        signs = session.query(TRewardSignin).all()
        for item in signs:
            protohelper.set_signs(resp.body.rewards.add(), item)

        sign_log = session.query(TRewardSigninMonth).filter(TRewardSigninMonth.id == req.header.user).first()
        if sign_log.signin_days == -1 or sign_log.total_days == -1:
            resp.header.result = RESULT_FAILED_INVALID_REWARD
            return

        resp.body.signin_days = sign_log.signin_days
        resp.body.month_sigin_days = sign_log.total_days
        resp.header.result = 0


    # 确认接收签到
    @USE_TRANSACTION
    def handle_signin(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        sign_log = self.sign.get_sign_log(session, user_info.id)

        # 今日是否签到
        if self.sign.today_is_sign(sign_log):
            resp.header.result = RESULT_FAILED_TODAY_SIGNED
            return

        # 签到
        total_days,signin_days, sign_luck_max = self.sign.sign_now(session, sign_log, user_info)
        if total_days < 0  or signin_days < 0:
            resp.header.result = RESULT_FAILED_TODAY_SIGNED
            return
        print 'vip======>',self.vip.to_level(user_info.vip_exp),user_info.vip_exp
        print '---------------->11111|',total_days,signin_days, sign_luck_max
        # 签到奖励，需要判断vip等级
        incr_gold = 0
        incr_gold = self.sign.sign_reward(session, user_info, sign_luck_max)
        print '---------------->222222|',incr_gold
        print incr_gold
        add_item = {}
        # if self.vip.to_level(user_info.vip_exp) >= 1:
        incr_gold += self.sign.sign_reward_vip(session, user_info, sign_luck_max, incr_gold)
        add_item = self.sign.sign_reward_vip_item(session,user_info,sign_luck_max)

        if add_item is not None and len(add_item) >0:
            horn_item = self.item.get_item_by_id(session, add_item['horn_card'][0])
            horn_card = add_item['horn_card'].split('-')
            if int(horn_card[1]) > 0:
                protohelper.set_item_add(resp.body.result.items_added.add() ,{
                    'id':horn_item.id,
                    'icon':horn_item.icon,
                    'name':horn_item.name,
                    'description':horn_item.description,
                }, horn_card[1])
            kick_item = self.item.get_item_by_id(session, add_item['kick_card'][0])
            print '---------->,send item 2',kick_item
            kick_card = add_item['kick_card'].split('-')
            if int(kick_card[1]) > 0:
                protohelper.set_item_add(resp.body.result.items_added.add() ,{
                   'id':kick_item.id,
                    'icon':kick_item.icon,
                    'name':kick_item.name,
                    'description':kick_item.description,
                },kick_card[1])
        print '---------------->333333|',incr_gold
        # 累计签到，幸运日发送奖品
        item,count = self.sign.sign_luck_day(session, total_days, sign_log.id)
        if item is not None and count > 0:
            protohelper.set_item_add(resp.body.result.items_added.add() ,item, count)


        protohelper.set_result(resp.body.result, gold=user_info.gold, diamond=user_info.diamond, incr_gold=incr_gold)


        resp.header.result = 0


    # 查询大厅
    @USE_TRANSACTION
    def handle_query_hall(self,session,req,resp,event):

        user_info = self.da.get_user(req.header.user)
        if self.hall.user_is_none(user_info):
            resp.header.result = RESULT_FAILED_ACCOUNT_EMPTY
            return

        user_gf = self.user_gf.get_user_gf(session, user_info.id)
        if user_gf == None:
            # 需要创建该条记录,说明该用户为首次使用该游戏
            # 初始化 user_goldflowe表和bag_item表记录
            self.user_gf.add_user_gf(session, user_info.id, user_info.channel)
            self.bag.user_init(session, req.header.user)
            self.sign.sign_init(session, req.header.user)
            # self.reward.task_first_login(session, req.header.user)
            SystemAchievement(session, req.header.user).finish_first_login()
            self.userobj.new_user_broadcast(user_info)

        protohelper.set_brief_hall(resp.body.brief, user_info)

        # 获取用户大厅信息
        self.hall.load_user_hall(session, user_info, user_gf, req.body.max_announcement_id, req.body.max_mail_id)

        # 设置大厅protobuf
        protohelper.set_hall(resp.body, self.hall)

        # 有好友信息就推送出去
        if self.hall.has_friend_count > 0:
            self.friend.load_friend_message(user_info.id)
            self.friend.send_friend_message(user_info.id)
        resp.header.result = 0


    # 查询用户
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

        account = session.query(TAccount).filter(TAccount.id == req.body.uid).first()
        if account is not  None and account.mobile is not None:
            resp.body.player.mobile = account.mobile

        is_friend = session.query(TFriend).filter(and_(TFriend.apply_uid == req.header.user, TFriend.to_uid == req.body.uid)).count()
        if is_friend > 0:
            resp.body.player.is_friend = True
        else:
            resp.body.player.is_friend = False

        protohelper.set_player(resp.body.player,user_info,user_gf)
        resp.body.update_avatar_url = UPDATE_AVATAR_URL
        resp.header.result = 0
    # 更新用户
    @USE_TRANSACTION
    def handle_update_user(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        if len(req.body.nick) > 0:
            # 任务-成就任务：修改昵称
            # self.reward.task_change_nick(session, user_info, req.body.nick)
            if req.body.nick is not user_info.nick:
                SystemAchievement(session, user_info.id).finish_change_nick()
            user_info.nick = req.body.nick
        if len(req.body.birthday) > 0:
            user_info.birthday = req.body.birthday
        if len(req.body.sign)  > 0:
            user_info.sign = req.body.sign
        if len(req.body.sex) > 0:
            user_info.sex = req.body.sex

        self.da.save_user(session, user_info)

        # 返回result标准格式
        # protohelper.set_result(resp.body.result, gold = user_info.gold,
        #                    diamond = user_info.diamond,
        #                    incr_gold = self.reward.result['incr_gold'])
        # for item in self.reward.result['items_add']:
        #     protohelper.set_item_add(resp.body.result.items_added.add(), item, item['count'])

        resp.header.result = 0

    # 查询公告
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
    # 查询奖励
    @USE_TRANSACTION
    def handle_rewards(self,session,req,resp,event):
        rewards = session.query(TRewardTask).order_by(desc(TRewardTask.is_daily)).all()
        reward_logs = session.query(TRewardUserLog).filter(TRewardUserLog.uid == req.header.user).all()

        items = self.item.get_itme_by_all(session)
        if len(rewards) <= 0:
            resp.header.result = -1
            return

        daily_task = self.daliy_task.get_daily_task(req.header.user)
        achievement_taks = SystemAchievement(session, req.header.user)
        for reward in rewards:
            pb_reward = resp.body.rewards.add()
            protohelper.set_reward(pb_reward, reward)
            if reward.is_daily == 1:
                pb_reward.state = daily_task.get_task_state(reward.id)
                if reward.id == 9:
                    print daily_task
            else:
                pb_reward.state = achievement_taks.get_task_state(reward.id)
                if reward.id == 9:
                    print achievement_taks.get_task_state(reward.id)


            if reward.items is None or reward.items == '':
                continue
            for split_item in reward.items.split(','):
                for item in items:
                    if item.id == int(split_item[0]):
                        protohelper.set_item_add(pb_reward.items.add(), {
                            'id':item.id,
                            'name':item.name,
                            'icon':item.icon,
                            'description':item.description,
                        }, split_item[2])


        resp.header.result = 0
    # 接收奖励
    @USE_TRANSACTION
    def handle_rewards_receive(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        print '=====>before',user_info.gold,user_info.diamond
        # 给用户奖励
        result = self.reward.give_user_reward(session, user_info, req.body.reward_id)
        if result is None or len(result) <= 0:
            resp.header.result = RESULT_FAILED_INVALID_REWARD
            return

        print '=====>after',user_info.gold,user_info.diamond
        print '====>result',result
        # 返回result标准格式
        protohelper.set_result(resp.body.result, gold = user_info.gold,
                           diamond = user_info.diamond,
                           incr_gold = result.get('incr_gold',0),
                           incr_diamond = result.get('incr_diamond', 0))
        for item in result['items_add']:
            protohelper.set_item_add(resp.body.result.items_added.add(), item, item['count'])

        resp.header.result = 0

    # 发送聊天（牌桌内|牌桌外）
    @USE_TRANSACTION
    def handle_send_chat(self,session,req,resp,event):
         user_info = self.da.get_user(req.header.user)
         if user_info == None:
             return
         if req.body.table_id <= 0:
             print '=======>1'
             # 完成喊话任务
             DailyTaskManager(self.redis).use_horn(req.header.user)
             print '=======>2'


             # 世界聊天，需要具有聊天道具卡
             if self.bag.has_item(session, req.header.user, ITEM_MAP['horn'][0]) == False:
                 resp.header.result = RESULT_FAILED_INVALID_BAG
                 return

             if self.bag.use_horn_item(session,req.header.user, 1) > 0:
                 self.bag.send_horn_item(self.redis.hkeys('online'), user_info,  req.body.message)



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
    # 奖励卷代码
    @USE_TRANSACTION
    def handle_code_reward(self,session,req,resp,event):
        reward_code = session.query(TRewardCode).filter(TRewardCode.code == req.body.code).first()

        if reward_code == None:
            resp.header.result = RESULT_FAILED_CODE
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
            resp.header.result = RESULT_FAILED_CODE_USED
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

            user_info = self.da.get_user(req.header.user)
            user_info.gold = user_info.gold +reward_code.gold
            user_info.diamond = user_info.diamond +reward_code.diamond
            self.da.save_user(session, user_info)
        except Exception as e:
            print e.message
            resp.header.result = RESULT_FAILED_CODE
            return

        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond
        resp.body.result.incr_gold = reward_code.gold
        resp.body.result.incr_diamond = reward_code.diamond
        resp.header.user = 0
    # 查询商品
    @USE_TRANSACTION
    def handle_shop(self,session,req,resp,event):
        shopitem = session.query(TShopItem).all()
        items = session.query(TItem).all()
        for spi in shopitem:
            protohelper.set_shop_item(resp.body.items.add(), spi, items)
        resp.header.result = 0

    # 购买商品
    @USE_TRANSACTION
    def handle_shop_buy(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        if self.shop.buy_item(session, user_info, req.body.shop_item_id, req.body.count) == False:
            resp.header.result = RESULT_FAILED_SHOP
            return

        # 每日任务
        DailyTaskManager(self.redis).buy_diamond(req.header.user)

        # type,1=金币，2=道具
        protohelper.set_result(resp.body.result, gold = user_info.gold, diamond = user_info.diamond,
                           incr_gold =self.shop.shop_item.gold, incr_diamond = -(self.shop.shop_item.total))

        protohelper.set_item_add(resp.body.result.items_added.add(),
                             self.shop.get_item_by_shop(session, req.body.shop_item_id),req.body.count)
        # 发送购买记录邮件
        self.shop.send_mail(session, user_info, req.body.shop_item_id)
        resp.header.result = 0


    # 查询交易记录
    @USE_TRANSACTION
    def handle_trade(self,session,req,resp,event):
        page = req.body.page
        page_size = req.body.page_size
        can_buy = req.body.can_buy
        user_info = self.da.get_user(req.header.user)


        data_count, items = self.shop.get_lists(session, req.body.page, req.body.page_size,user_info, req.body.can_buy, req.body.my_sell)



        # other data
        for item in items:
            protohelper.set_trades(resp.body.trades.add(), item,self.da.get_user(item.seller))
        resp.body.total = data_count
        resp.header.user = 0

    # 购买交易
    @USE_TRANSACTION
    def handle_trade_buy(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        # 权限验证，vip1及以上等级可在金币交易中购买金币交易
        if self.vip.denied_buy_gold( self.vip.to_level(user_info.vip_exp) ):
            resp.header.result = RESULT_FAILED_INVALID_AUTH
            return

        # 出售商品验证
        trade = session.query(TTrade).filter(TTrade.id == req.body.trade_id).first()
        if user_info.diamond < trade.diamond:
            resp.header.result = RESULT_FAILED_SHOP_DIAMOND
            return

        try:
            # 修改交易记录
            result = session.query(TTrade).with_lockmode("update").filter(and_(TTrade.id == req.body.trade_id, \
                                                                               TTrade.status != 1, TTrade.diamond <= user_info.diamond)).update({
                TTrade.buyer : user_info.id,
                TTrade.buy_time : datetime.now(),
                TTrade.status : 1,
            })
            if result != 1:
                resp.header.result = RESULT_FAILED_SHOP
                return
            # 修改出售者数据，通过邮件领取的方式
            # seller_info = self.da.get_user(trade.seller)
            # seller_info.diamond= seller_info.diamond + trade.diamond
            # self.da.save_user(session, seller_info)

            # 修改购买者数据
            user_info.gold = user_info.gold + trade.gold
            user_info.diamond = user_info.diamond - trade.diamond
            self.da.save_user(session,user_info)
        except Exception as e:
            print e.message
            resp.header.result = RESULT_FAILED_SHOP
            return

        # 发送当前用户的消费记录
        t = time.time()
        content = MAIL_CONF['trade_buy_gold'] % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t)),trade.diamond ,trade.gold)
        MessageObject.send_mail(session, user_info, 0, \
                                title=u'消费记录',
                                content=content,
                                type=0, ) # 不带附件

        # 给挂售的用户发领取邮件
        content = MAIL_CONF['trade_sell_success'] % (trade.gold,trade.diamond)
        MessageObject.send_mail(session, trade.seller, 0,\
                                title=u'领取钻石',
                                content=content,
                                type=1, # 带附件
                                diamond=trade.diamond)

        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond
        resp.body.result.incr_gold = trade.gold
        resp.body.result.incr_diamond = -trade.diamond
        resp.header.result = 0
    # 出售金币
    @USE_TRANSACTION
    def handle_sell_gold(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)


        # 权限验证，vip2及以上等级可在金币交易中出售金币
        if self.vip.denied_sell_gold(self.vip.to_level(user_info.vip_exp)):
            resp.header.result = RESULT_FAILED_INVALID_AUTH
            return

        # 扣税
        if user_info.gold <= (TAX_NUM * req.body.gold) + req.body.gold:
            resp.header.result = RESULT_FAILED_INVALID_GOLD
            return


        trade = TTrade()
        trade.seller = req.header.user
        trade.gold = req.body.gold
        trade.diamond = req.body.diamond
        trade.sell_time = datetime.now()
        trade.rate = float(req.body.diamond) / float(req.body.gold) * float(SELL_RATE)

        trade.status = 0
        session.add(trade)

        tax_gold = int((TAX_NUM * req.body.gold) + req.body.gold)
        user_info.gold = user_info.gold - tax_gold
        self.da.save_user(session,user_info)

        # 广播，当前用户挂售金币成功
        self.shop.sell_gold_brodacast(user_info, req.body.gold, req.body.diamond)

        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond
        resp.body.result.incr_gold = -tax_gold
        resp.header.result = 0
    # 下架金币
    @USE_TRANSACTION
    def handle_out_gold(self,session,req,resp,event):
        # -1 下架，0=交易中，1=被买走
        user_info = self.da.get_user(req.header.user)
        if self.shop.sell_out(session, user_info, req.body.trade_id) == False:
            resp.header.result = RESULT_FAILED_SHOP

        trade = self.shop.get_trade(session, req.body.trade_id)
        protohelper.set_result(resp.body.result, gold = user_info.gold, diamond = user_info.diamond,
                               incr_gold = trade.gold, incr_diamond = 0)
        resp.header.result = 0




    # 查询背包
    @USE_TRANSACTION
    def handle_bag(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)
        if user_info == None:
            resp.header.result = -1
            return

        items = session.query(TItem).all()
        # gifts = session.query(TGift).all()

        # load item
        user_items = session.query(TBagItem).filter(TBagItem.uid == req.header.user).all()
        for user_item in user_items:
            protohelper.set_bag_item(resp.body.items.add(), user_item, items)

        # load bag
        # user_gifts = session.query(TBagGift).filter(TBagGift.uid == req.header.user).all()
        # for user_gift in user_gifts:
        #     protohelper.set_bag_gift(resp.body.gifts.add(), user_gift, gifts)

        resp.header.result = 0

    # 使用背包内的道具
    @USE_TRANSACTION
    def handle_use_bag(self,session,req,resp,event):

        # 暂时只有vip经验卡能使用到该方法
        if self.bag.has_item(session, req.header.user, req.body.item_id, req.body.count) == False:
            resp.header.result = RESULT_FAILED_INVALID_BAG
            return

        # 使用道具
        result = self.bag.use_user_item(session, req.header.user, req.body.item_id, countof=req.body.count)
        if result <= 0:
            resp.header.result = RESULT_FAILED_INVALID_BAG
            return

        # 加vip经验
        user_info = self.da.get_user(req.header.user)
        user_info.vip_exp = 0 if user_info.vip_exp <= 0 else user_info.vip_exp
        old_vip_level = self.vip.to_level(user_info.vip_exp)
        for times in range(req.body.count):
            user_info.vip_exp = user_info.vip_exp + ItemObject.get_item_conf(req.body.item_id)[0]
        self.da.save_user(session, user_info)

        new_vip_level = self.vip.to_level(user_info.vip_exp)
        # vip升级广播
        if old_vip_level < new_vip_level:
            self.vip.level_up_broadcast(user_info.nick, user_info.vip_exp)
            # 完成vip任务
            SystemAchievement(session, user_info.id).finish_upgrade_vip(new_vip_level)


        # 返回数据
        resp.body.result.vip_exp = user_info.vip_exp
        item = ItemObject.get_item(session, req.body.item_id)
        pb = resp.body.result.items_removed.add()
        pb.id = item.id
        pb.name = item.name
        pb.icon = item.icon
        pb.description = item.description
        pb.count = req.body.count
        resp.header.result = 0

    # 查询银行
    @USE_TRANSACTION
    def handle_bank(self,session,req,resp,event):

        bank_account = session.query(TBankAccount).filter(TBankAccount.uid == req.header.user).first()

        user_info = self.da.get_user(req.header.user)

        resp.body.gold = bank_account.gold if bank_account != None else 0
        resp.body.limit = VIP_CONF[self.vip.to_level(user_info.vip_exp)]['bank_max']
        resp.body.next_vip_limit = VIP_CONF[-1]['bank_max'] if (self.vip.to_level(user_info.vip_exp) + 1) >= len(VIP_CONF) else VIP_CONF[self.vip.to_level(user_info.vip_exp) + 1]['bank_max']
        resp.header.user = 0
    # 存钱到银行
    @USE_TRANSACTION
    def handle_bank_save(self,session,req,resp,event):
        user_info = self.da.get_user(req.header.user)

        print '---->1'
        # vip 银行存款限制
        if self.vip.over_bank_max(self.vip.to_level(user_info.vip_exp), req.body.gold):
            resp.header.result = RESULT_FAILED_BANK_MAX
            return
        print '---->2'
        if req.body.gold > 0 and user_info.gold < req.body.gold:
            resp.header.result = RESULT_FAILED_INVALID_GOLD
            return
        print '---->3'
        if VIP_CONF[self.vip.to_level(user_info.vip_exp)]['bank_max'] > 0:
            bank_account = session.query(TBankAccount).filter(TBankAccount.uid == req.header.user).first()
            if bank_account == None:
                bank_account = TBankAccount()
                bank_account.uid = req.header.user
                bank_account.gold = int(req.body.gold)
                bank_account.diamond = 0
                bank_account.update_time = datehelper.get_today_str()
                bank_account.create_time = datehelper.get_today_str()
                session.add(bank_account)
        # if bank_account == None or VIP_CONF[user_info.vip]['bank_max'] <= 0:
        print '----->4'
        if req.body.gold < 0:
            if bank_account.gold < abs(req.body.gold):
                resp.header.result = RESULT_FAILED_INVALID_GOLD
                return
        else:
            if (bank_account.gold + req.body.gold) > VIP_CONF[self.vip.to_level(user_info.vip_exp)]['bank_max']:
                resp.header.result = RESULT_FAILED_INVALID_GOLD
                return

        session.query(TBankAccount).filter(TBankAccount.uid == req.header.user).update({
            TBankAccount.gold: TBankAccount.gold + req.body.gold
        })
        print '----->5',user_info.gold,type(user_info.gold),req.body.gold,type(req.body.gold)
        if req.body.gold > 0:
            user_info.gold = user_info.gold - int(req.body.gold)
        elif req.body.gold < 0:
            user_info.gold = user_info.gold + int(abs(req.body.gold))
        print '----->6',user_info.gold,type(user_info.gold),req.body.gold,type(req.body.gold)
        self.da.save_user(session, user_info)
        resp.body.result.gold = user_info.gold
        resp.body.result.diamond = user_info.diamond
        resp.header.result = 0
    # 重置牌桌奖励记数
    @USE_TRANSACTION
    def handle_reset_play_reward(self,session,req,resp,event):
        try:
            key = 'round_reward:'+str(req.header.user)
            self.redis.hmset(key, {'total':REWARD_PLAY_ROUND[0][0],'current':0})
            self.redis.expireat(key, int(datehelper.next_midnight_unix(delay_sec = 5)) )
        except Exception as e:
            print e.message
            resp.header.result -1
            return
        resp.header.result = 0

    # 领取牌桌奖励
    @USE_TRANSACTION
    def handle_receive_play_reward(self,session,req,resp,event):
        key = 'round_reward:'+str(req.header.user)
        if self.redis.exists(key) == False:
            resp.header.result = RESULT_FAILED_RECEIVE_REWARD
            return

        record = self.redis.hgetall(key)
        if int(record['total']) != int(record['current']):
            resp.header.result = RESULT_FAILED_RECEIVE_REWARD
            return

        round_reward_conf = RewardObject.get_conf(int(record['total']))

        if round_reward_conf == None:
            resp.header.result = RESULT_FAILED_RECEIVE_REWARD
            return
        next_round_reward_conf = RewardObject.get_next_round(int(record['total']))

        self.redis.hmset(key,{'total':next_round_reward_conf[0],'current':0})
        user_info = self.da.get_user(req.header.user)
        user_info.gold = user_info.gold + random.randint(round_reward_conf[1],round_reward_conf[2])
        self.da.save_user(session, user_info)

        resp.body.next_round = next_round_reward_conf[0]
        resp.body.result.gold = user_info.gold
        resp.header.result = 0

    # 生成订单
    @USE_TRANSACTION
    def handle_create_order(self,session,req,resp,event):
        # shop_id = 0 首充，负数代表快充场次，正数代表商品id
        if req.body.shop_id == 0:
            is_first_charge = session.query(TUser.is_charge).filter(TUser.id == req.header.user).first()
            if is_first_charge[0] == 1:
                resp.header.result = RESULT_FAILED_FIRST_CHARGE
                return

        order_sn = self.get_order_sn(req.header.user)
        order =  session.query(TOrder).filter(TOrder.order_sn == order_sn).first()
        if order != None:
            order_sn = self.get_order_sn(req.header.user)
            order =  session.query(TOrder).filter(TOrder.order_sn == order_sn).first()
            if order != None:
                resp.header.result = -1
                return

        if req.body.shop_id > 0:
            charge_item = session.query(TChargeItem).filter(TChargeItem.id == req.body.shop_id).first()
            if charge_item == None:
                resp.header.result = -1
                return
            item = ItemObject.get_item(session, req.body.shop_id)
            money = charge_item.money
            real_money = charge_item.real_money
            name = item.name
        elif req.body.shop_id == 0 :
            user_info = self.da.get_user(req.header.user)
            if user_info.is_charge:
                resp.header.result = -1
                return
            money = decimal.Decimal((FRIST_CHARGE['money'])) / 100
            real_money = decimal.Decimal((FRIST_CHARGE['real_money'])) / 100
            name = FRIST_CHARGE['title']
        else:
            money,gold_w,name,real_money = QUICK_CHARGE[abs(req.body.shop_id)-1]
            real_money = decimal.Decimal(real_money) / 100

        print '---->',money,real_money,name

        order = TOrder()
        order.order_sn = order_sn
        order.uid = req.header.user
        order.money = money
        order.shop_id = req.body.shop_id
        order.status = -1
        order.comment = req.body.comment
        order.create_time = datehelper.get_today_str()
        session.add(order)

        resp.body.name = name
        resp.body.money = int(real_money * decimal.Decimal(100))
        resp.body.order_sn = str(order_sn)
        resp.body.callback = PAY_RESULT_URL
        resp.header.result=0

    @USE_TRANSACTION
    def handle_quick_charge(self,session,req,resp,event):
        money,gold,name,real_money = QUICK_CHARGE[abs(req.body.table_type)-1]
        print '===================>'
        print money,gold,name
        resp.body.money = money
        resp.body.gold = gold
        resp.header.result = 0

    # 记录牌桌次数
    @USE_TRANSACTION
    def handle_record_play_reward(self,session,req,resp,event):
        key = 'round_reward:'+str(req.header.user)
        if self.redis.exists(key) == False:
            self.redis.hmset(key, {'total':REWARD_PLAY_ROUND[0][0],'current':0})
            self.redis.expireat(key, int(datehelper.next_midnight_unix(delay_sec = 5)) )

        total = int(self.redis.hget(key,'total'))
        current = int(self.redis.hget(key,'current'))
        if total > current:
            current = int(self.redis.hincrby(key, 'current'))
        resp.body.total = total
        resp.body.current = current
        resp.header.result = 0

    # 意见反馈
    @USE_TRANSACTION
    def handle_feedback(self,session,req,resp,event):
        feedback = TFeedBack()
        feedback.message = req.body.message
        feedback.contact = req.body.contact
        feedback.create_time = datehelper.get_today_str()
        feedback.status = -1
        session.add(feedback)
        resp.header.result = 0


    # 充值
    @USE_TRANSACTION
    def handle_charge(self,session,req,resp,event):
        items = session.query(TChargeItem).all()
        for item in items:
            protohelper.set_charge(resp.body.items.add(), item)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_bind_mobile(self,session,req,resp,event):
        # todo ... 上线需修改
        code = 0
        if int(req.body.verify_code) != 0:
            code = self.redis.get('sms_'+req.body.mobile)
            verify_code = req.body.verify_code
        else:
            verify_code = 0

        # 验证不正确
        if code is None or code is not verify_code:
            resp.header.result = RESULT_FAILED_VERIFY_ERROR
            return

        # 绑定类型：1：新用户绑定（password必传）设置密码,  2：绑定新手机号（password不传）, 3：解绑旧手机资格校验（password不传）
        if req.body.bind_type == 1:
            if req.body.password is None:
                resp.header.result = RESULT_FAILED_PASSWORD_EMPTY
                return
            self.profile.bind_mobile(session, req.body.uid, req.body.mobile, req.body.password)
        elif req.body.bind_type == 2:
            self.profile.bind_mobile(session, req.body.uid, req.body.mobile)
        elif req.body.bind_type == 3:
            pass

        resp.header.result = 0

    @USE_TRANSACTION
    def handle_first_charge(self,session,req,resp,event):

        resp.body.money = FRIST_CHARGE['money']
        resp.body.diamond = FRIST_CHARGE['diamond']
        resp.body.hore = FRIST_CHARGE['hore']
        resp.body.gold = FRIST_CHARGE['gold']
        resp.body.kicking_card = FRIST_CHARGE['kicking_card']
        resp.body.vip_card = FRIST_CHARGE['vip_card']
        resp.header.result = 0

    # 获取通用result结果
    def get_result(self,user,resp):
        resp.body.result.gold = user.gold
        resp.body.result.diamond = user.diamond
    # 通用推送广播消息
    def queue_notification(self):
        while True:
            _,data = self.redis.brpop("notification_queue")
            json_object = json.loads(data)

            users = json_object['users']
            event = create_client_event(NotificationEvent)
            event.body.type = json_object['notifi_type']
            event.body.param1 = json_object['param1']
            event.body.param2 = json.dumps(json_object['param2'])

            self.sender.send_event(users,event)


    def get_order_sn(self, uid):
        return time.strftime('%Y%m%d')+str(random.randint(10000,99999))+str(uid)


if __name__ == "__main__":
    pass

