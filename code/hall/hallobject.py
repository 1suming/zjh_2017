# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from config.var import *
from config.rank import *
from config.vip import *
from config.item import *
from config.reward import *
from config.sign import *
from config.broadcast import *
from config.mail import *
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
from db.rank_gold_top import *
from db.rank_charge_top import *
from db.rank_make_money_top import *
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
from helper import protohelper
from helper import datehelper
from datetime import date,datetime
from helper import cachehelper
import time,json,sys

from proto import struct_pb2 as pb2
from proto.constant_pb2 import *
from proto.friend_pb2 import *

from sqlalchemy import desc,and_




class HallObject:
    def __init__(self, service):
        self.service = service
        self.has_reward_count = 0
        self.has_announcement_count = 0
        self.is_charge = False # 没有首冲过
        self.announcements = None
        self.is_sign = False # 今日没签到
        self.has_friend_count = 0
        self.has_mail = 0

    def user_is_none(self, user):
        return user is None

    def load_user_hall(self, session, user_info, user_gf, max_announcement_id, max_mail_id):
        self.has_reward_count = session.query(TRewardUserLog).filter(and_(TRewardUserLog.state == 1, TRewardUserLog.uid == user_info.id)).count()
        self.has_announcement_count = session.query(TAnnouncement)\
            .filter(and_(TAnnouncement.id > max_announcement_id, TAnnouncement.start_time <= datehelper.get_today_str(), datehelper.get_today_str() <= TAnnouncement.end_time)).count()
        self.is_charge = True if user_info.is_charge > 0 else False
        self.announcements = session.query(TAnnouncement).filter(and_(TAnnouncement.start_time <= datehelper.get_today_str(), \
                                                              TAnnouncement.end_time>=datehelper.get_today_str(), \
                                                              TAnnouncement.popup == STATE_NEED_POPUP)).order_by(TAnnouncement.sort).all()
        sign_log = self.service.sign.get_sign_log(session, user_info.id)
        if sign_log is not None:
            self.is_sign = self.service.sign.today_is_sign(sign_log)
        friend_count = self.service.redis.hlen('message_'+str(user_info.id))
        self.has_friend_count = friend_count if friend_count > 0 else 0
        self.has_mail = session.query(TMail).filter(and_(TMail.to_user == user_info.id, TMail.id > max_mail_id)).order_by(desc(TMail.id)).count()

class UserObject:
    def __init__(self, service):
        self.service = service

    def update_user(self, session, user_info):
        self.service.da.save_user(session, user_info)

    # 提醒，新用户注册
    def new_user_broadcast(self, user_info):
        content = BORADCAST_CONF['reg'] % user_info.nick
        MessageObject.push_message(self,self.redis.hkeys('online'),5,{'message':content})

class UserGoldFlower:
    def __init__(self, service):
        self.service = service
        self.user_gf = None

    def get_user_gf(self, session, user):
        return session.query(TUserGoldFlower).filter(TUserGoldFlower.id == user).first()

    def add_user_gf(self, session, uid, channel):
        user_gf = TUserGoldFlower()
        user_gf.id = uid
        user_gf.channel = channel
        user_gf.exp = DEFAULT_USER_GLODFLOWER['exp']
        user_gf.win_games = DEFAULT_USER_GLODFLOWER['win_games']
        user_gf.total_games = DEFAULT_USER_GLODFLOWER['total_games']
        user_gf.best = DEFAULT_USER_GLODFLOWER['best']
        user_gf.create_time = datehelper.get_today_str()
        user_gf.max_bank = DEFAULT_USER_GLODFLOWER['max_bank']
        user_gf.max_items = DEFAULT_USER_GLODFLOWER['max_items']
        user_gf.max_gifts = DEFAULT_USER_GLODFLOWER['max_gifts']
        user_gf.signin_days = DEFAULT_USER_GLODFLOWER['signin_days']
        user_gf.last_signin_day = DEFAULT_USER_GLODFLOWER['last_signin_day']
        user_gf.change_nick = DEFAULT_USER_GLODFLOWER['change_nick']
        user_gf.wealth_rank = DEFAULT_USER_GLODFLOWER['wealth_rank']
        user_gf.win_rank = DEFAULT_USER_GLODFLOWER['win_rank']
        user_gf.charm_rank = DEFAULT_USER_GLODFLOWER['charm_rank']
        user_gf.charge_rank = DEFAULT_USER_GLODFLOWER['charge_rank']
        session.add(user_gf)
        session.flush()
        self.user_gf = user_gf

class FriendObject:
    def __init__(self, service):
        self.service = service
        self.friend_message = None

    def get_friends(self, session, user):
        return session.query(TFriend).filter(TFriend.apply_uid == user).all()

    def get_friends_count(self, session, user):
        return session.query(TFriend).filter(TFriend.apply_uid == user).count()

    def make_friend(self, session, user_info, friend_info, message):
        # 0 = 同意，2=拒绝，1=申请
        apply_record = session.query(TFriendApply).filter(and_(TFriendApply.apply_uid == user_info.id, TFriendApply.to_uid == friend_info.id)).first()
        if apply_record is not None:
            if apply_record.state == 0:
                # 同意或申请的状态下，不可再重复申请
                return  RESULT_FAILED_HAS_FRIEND

            if apply_record.state == 1:
                return RESULT_FAILED_MAKE_APPLY
            else:
                # 重新申请好友
                session.query(TFriendApply).with_lockmode("update").filter(and_(TFriendApply.id == apply_record.id)).update({
                    TFriendApply.state : 1,
                    TFriendApply.finish_time : datetime.now()
                })
        else:
            # 建立申请记录
            apply_record = TFriendApply()
            apply_record.apply_uid = user_info.id
            apply_record.to_uid = friend_info.id
            apply_record.message = message
            apply_record.apply_time = datetime.now()
            apply_record.state = 1 # 1=申请
            session.add(apply_record)
            session.flush()


        # 发送申请事件给相关用户
        if self.service.manager.offline(friend_info.id) != 0:
            # 在线就推送数据
            event = create_client_event(FriendApplyEvent)
            event.body.apply.id = apply_record.id
            event.body.apply.apply_from = user_info.id
            event.body.apply.apply_from_nick = user_info.nick
            event.body.apply.apply_from_avatar = user_info.avatar
            event.body.apply.to = friend_info.id
            event.body.apply.time = int(time.mktime(apply_record.apply_time.timetuple()))
            event.body.apply.message = message
            self.service.sender.send_event([friend_info.id], event)
        else:
            # 不在线，就发离线数据
            self.service.redis.hincrby('friend_queue', friend_info.id)

        return 0

    def make_friend_apply(self, session, apply_id, accept, user_info, friend_info):
        # 0 = 同意，2=拒绝，1=申请, accept = true同意，false拒绝
        state = 0 if accept else 2
        session.query(TFriendApply).with_lockmode("update").filter(and_(TFriendApply.id == apply_id, TFriendApply.state == 1)).update({
            TFriendApply.state : state,
            TFriendApply.finish_time : datetime.now()
        })

        # 发送是否同意邮件给双方
        self.send_mail_make_friend(session, user_info, friend_info, accept)
        if accept == False:
            # 拒绝好友申请
            return

        # 同意申请，建立数据库朋友关系
        friend_apply = TFriend()
        friend_apply.apply_uid = user_info.id  # apply_id
        friend_apply.to_uid = friend_info.id  # to_uid
        friend_apply.type = 0
        friend_apply.create_time = datetime.now()
        session.add(friend_apply)
        friend_other = TFriend()
        friend_other.apply_uid = friend_info.id # to_uid
        friend_other.to_uid = user_info.id # apply_id
        friend_other.type = 0
        friend_other.create_time = datetime.now()
        session.add(friend_other)

    def get_friend_apply(self, session, apply_id):
        return session.query(TFriendApply).filter(and_(TFriendApply.id == apply_id)).first()

    def load_friend_message(self, user):
        self.friend_message = self.service.redis.hgetall('message_'+str(user))

    def send_friend_message(self, user):
        if self.friend_message is not None:
            for index in self.friend_message:
                event = create_client_event(FriendMessageEvent)
                event.body.ParseFromString(self.friend_message[index])
                self.service.sender.send_event([user], event)

    def send_mail_make_friend(self, session, user_info_source, user_info_target, accept):
        # 玩家xxx同意/拒绝了你的好友申请！
        # 你同意/拒绝了玩家xxx的好友申请！
        if accept:
            print 'yes , friend apply'
            content = MAIL_CONF['friend_make_apply_source'] % (user_info_source.nick)
            MessageObject.send_mail(session, user_info_source, 0 ,title=u'好友申请提醒',content =content,type=0)
            content = MAIL_CONF['friend_make_apply_target'] % (user_info_target.nick)
            MessageObject.send_mail(session, user_info_target, 0 ,title=u'好友申请提醒',content =content,type=0)
        else:
            print 'no, firend no'
            content = MAIL_CONF['friend_make_no_apply_source'] % (user_info_source.nick)
            MessageObject.send_mail(session, user_info_source, 0 ,title=u'好友申请提醒',content =content,type=0)
            content = MAIL_CONF['friend_make_no_apply_target'] % (user_info_target.nick)
            MessageObject.send_mail(session, user_info_target, 0 ,title=u'好友申请提醒',content =content,type=0)

    def send_mail_remove_friend(self, session, user_info_source, user_info_target):
        # 你删除了与玩家xxx的好友关系！
        content = MAIL_CONF['friend_remove_source'] % (user_info_target.nick)
        MessageObject.send_mail(session, user_info_source, 0 ,title=u'好友删除提醒',content =content,type=0)
        # 玩家xxx删除了与你的好友关系
        content = MAIL_CONF['friend_remove_target'] % (user_info_source.nick)
        MessageObject.send_mail(session, user_info_target, 0 ,title=u'好友删除提醒',content =content,type=0)

class SignObject:

    def __init__(self, service):
        self.service = service
        self.diff_day = 0
        self.sign_day = 1
        self.total_sign_day = 0
        self.luck_day_item = None


    def sign_init(self, session, user):
        sign = TRewardSigninMonth()
        sign.id = user
        sign.signin_days = -1
        sign.total_days = -1
        sign.last_signin_day = '2000-01-01'
        session.add(sign)

    def sign_now(self,session, sign_log, user_info):
        diff_day = self.get_diff_day(sign_log.last_signin_day)

        total_days = -1         # 当月累计签到
        signin_days = -1        # 连续签到
        sign_luck_max = 0      # 最大金币奖励日
        # 断签时间过长
        if diff_day > 1:
            if sign_log.signin_days == -1 and sign_log.total_days == -1:
                # 有可能是第一次登陆，赠送道具（大喇叭）
                self.first_sign_send_item(session, user_info.id)
            total_days = 1
            signin_days = 1
            sign_luck_max = 1
        elif diff_day == 1:
            # 昨天签到，今天没签到，马上签到
            if time.strftime('%Y-%m') == sign_log.last_signin_day.strftime('%Y-%m'):
                # 当月处理
                total_days = sign_log.total_days + 1
                signin_days = sign_log.signin_days + 1
                sign_luck_max = signin_days
            else:
                # 跨月处理
                signin_days = sign_log.signin_days + 1
                total_days = 1 # 月累计归0
                sign_luck_max = 1

            # 累计签到天数超过最大签到数，按最大签到数算
            if signin_days >= SYS_MAX_SIGN_DAY:
                sign_luck_max = SYS_MAX_SIGN_DAY - 1

        elif diff_day <= 0:
            # 异常情况
            return -1,-1,-1

        # 记录签到日志
        self.go_sign(session, user_info.id, signin_days, total_days)
        return total_days,signin_days,sign_luck_max


    def get_sign_log(self, session, user):
        return session.query(TRewardSigninMonth).filter(TRewardSigninMonth.id == user).first()

    def get_diff_day(self, last_signin_day):
        return (date.today() - last_signin_day).days

    # 今日是否签到
    def today_is_sign(self, sign_log):
        diff_day = self.get_diff_day(sign_log.last_signin_day)
        print '------------->',diff_day
        if diff_day >= 1:
            return False # 今日没有签到
        return True # 今日已签到

    # 签到
    def go_sign(self, session, user, signin_days, total_days):
        session.query(TRewardSigninMonth).with_lockmode("update").filter(TRewardSigninMonth.id == user).update({
            TRewardSigninMonth.signin_days: signin_days,
            TRewardSigninMonth.total_days: total_days,
            TRewardSigninMonth.last_signin_day : datehelper.get_date_str()
        })


    # 第一次签到送东西
    def first_sign_send_item(self,session, user):
        print '------------->first_sign_send_item'
        self.service.bag.save_user_item(session, user, DEFAULT_USER['default_item'][0], DEFAULT_USER['default_item'][1])

    # 签到奖励
    def sign_reward(self, session, user_info, index):
        if index == 0:
            return
        incr_gold = SIGN_CONF[index]['gold']
        user_info.gold = user_info.gold + incr_gold
        self.service.da.save_user(session, user_info)
        return incr_gold

    # vip签到奖励
    def sign_reward_vip(self, session, user_info, index):
        if index == 0:
            return
        incr_gold = 0
        # 普通签到加钱
        incr_gold = self.sign_reward(session, user_info, index)
        # vip额外加钱
        incr_gold = incr_gold + VIP_CONF[self.service.vip.to_level(user_info.vip_exp)]['sign_reward'] * user_info.gold
        user_info.gold = user_info.gold +incr_gold
        self.service.da.save_user(session,user_info)
        return incr_gold


    # 签到log，便于后期计算
    def sign_log(self, session, user_gf):
        # 当月累计总签到数
        self.total_sign_day = 0
        if datetime.now().strftime('%m') == user_gf.last_signin_day.strftime('%m'):
            self.total_sign_day = TRewardSigninMonth.signin_days + 1
        else:
            self.total_sign_day = 1

        session.query(TRewardSigninMonth).with_lockmode("update").filter(TRewardSigninMonth.uid == user_gf.id).update({
            TRewardSigninMonth.signin_days: self.total_sign_day,
            TRewardSigninMonth.last_signin_day : date.today()
        })

    # 月累计签到，幸运日发送奖品
    def sign_luck_day(self,session, total_days, user):
        if  total_days in SIGN_MONTH_LUCK:
            luck_day_item = SIGN_MONTH_LUCK.get(total_days)
            self.service.bag.save_user_item(session, user, luck_day_item[1], luck_day_item[0])
            return ItemObject.get_item(session, luck_day_item[1]),luck_day_item[0]
        return [],0
    # 第一次登陆送东西
    @staticmethod
    def first_login_send_item(user, bag):
        bag.save_user_item(user, DEFAULT_USER['default_item'][0], DEFAULT_USER['default_item'][1])

    # 记录最后一天
    @staticmethod
    def last_sign(session,day):
        session.query(TUserGoldFlower).with_lockmode("update").filter(TUserGoldFlower.id == user_gf.id).update({
            TUserGoldFlower.signin_days: day,
            TUserGoldFlower.last_signin_day : date.today()
        })

class ShopObject:
    def __init__(self, service):
        self.service = service
        self.shop_item = None

    def buy_item(self, session, user_info, shop_item_id, count):
        self.shop_item = self.get_shop_item(session, shop_item_id)
        if self.shop_item is None:
            return False

        if user_info.diamond < ( int(self.shop_item.diamond) * int(count) ):
            return False
        self.shop_item.total = int(self.shop_item.diamond) * int(count)
        user_info.diamond = user_info.diamond - ( int(self.shop_item.diamond) * int(count) )
        # 1 = 金币，2 = 道具
        if self.shop_item.type == 1:
            user_info.gold = user_info.gold + self.shop_item.shop_gold
        elif self.shop_item.type == 2:
            self.service.bag.save_user_item(session, user_info.id, self.shop_item.item_id, count)

        self.service.da.save_user(session,user_info)
        return True

    def send_mail(self, session, user_info, shop_item_id):
        # shop_item = self.get_shop_item(session, shop_item_id)
        item = self.service.item.get_item_by_id(session, self.shop_item.item_id)

        if self.shop_item is None:
            return
        if self.shop_item.type == 1:
            content = MAIL_CONF['trade_buy_gold'] % (datehelper.get_today_str(),self.shop_item.diamond, self.shop_item.shop_gold)
            MessageObject.send_mail(session, user_info, 0, title=u'购买金币', content=content, type=0)
        elif self.shop_item.type ==2:
            content = MAIL_CONF['trade_buy_item'] % (datehelper.get_today_str(),self.shop_item.diamond, item.name)
            MessageObject.send_mail(session, user_info, 0, title=u'购买道具', content=content, type=0)



    def get_shop_item(self, session ,shop_item_id):
        return session.query(TShopItem).filter(TShopItem.id == shop_item_id).first()

    def get_item_by_shop(self, session, shop_item_id):
        shop_item = self.get_shop_item(session, shop_item_id)
        if shop_item is None:
            return
        return self.service.item.get_item_by_id(session, shop_item.item_id)
    # 下架
    def sell_out(self, session, user_info, trade_id):

        trade = session.query(TTrade).filter(and_(TTrade.id == trade_id, TTrade.status == 0)).first()

        if trade == None:
            return False
        session.query(TTrade).with_lockmode('update').filter(and_(TTrade.id == trade_id, TTrade.status == 0)).update({
            TTrade.status : -1
        })
        user_info.gold = user_info.gold + trade.gold
        # user_info.diamond = user_info.diamond + trade.diamond
        self.service.da.save_user(session, user_info)
        return True

    def get_trade(self, session, trade_id):
        return session.query(TTrade).filter(and_(TTrade.id == trade_id)).first()

class RankObject:

    # 财富榜人物上线，广播
    @staticmethod
    def gold_top_online_broadcast(service, session, user):
        user_info = session.query(TUser).filter(TUser.id == user).first()
        gold_top = session.query(TRankGoldTop).filter(TRankGoldTop.uid == user).first()
        if gold_top is None:
            return
        items = session.query(TRankGoldTop,TUser).filter(TRankGoldTop.uid == TUser.id).order_by(desc(TUser.gold))\
            .limit(RANK_CHARGE_TOP).all()
        rank = 0
        for index in range(len(items)):
            if items[index][1].id == user_info.id:
                rank = index
                break
        if rank == 0:
            return
        content = BORADCAST_CONF['gold_top_online'] % (rank, user_info.nick)
        MessageObject.push_message(service, service.redis.hkeys('online'),5,{'message':content})


    # 日充值榜单，调用函数
    # RankObject.add_charge_top(session, 10026,'nick','avatar',100)
    # 周赚金榜单，调用函数
    # RankObject.add_make_money_top(session, 10026,'nick','avatar',100)

    def __init__(self, service):
        self.service = service
        self.rank_type_map = {
            1: self.wealth_top,
            2: self.charge_top,
            4: self.make_money_top,
        }

    def get_lists(self, session, rank_type, rank_time = None):
        func = self.rank_type_map[rank_type]
        return func(session, rank_time)

    def wealth_top(self, session, rank_time):
        top = []
        items = session.query(TRankGoldTop,TUser).filter(TRankGoldTop.uid == TUser.id).order_by(desc(TUser.gold))\
            .limit(RANK_CHARGE_TOP).all()
        for item in items:
            gold_top, user = item
            top.append(self.pack_top(uid=user.id,nick=user.nick,avatar=user.avatar,gold=user.gold, vip=user.vip))
        return top

    def pack_top(self, **kwargs):
        return {
            'uid':kwargs['uid'],
            'nick':kwargs['nick'],
            'avatar':kwargs['avatar'],
            'gold':kwargs['gold'],
            'vip':kwargs['vip'],
            'rank_reward':kwargs.get('rank_reward', ''),
            'money_maked':kwargs.get('money_maked',0),
            'charm':0,
        }

    def charge_top(self,session, rank_time):
        query = session.query(TRankChargeTop, TUser).filter(TRankChargeTop.uid == TUser.id)
        if rank_time == RANK_YESTERDAY:
            query = query.filter(TRankChargeTop.add_date == datehelper.get_yesterday())
        elif rank_time == RANK_TODAY:
            query = query.filter(TRankChargeTop.add_date == datehelper.get_datetime().strftime('%Y-%m-%d'))
        items = query.order_by(desc(TUser.gold)).limit(RANK_CHARGE_TOP).all()

        top = []
        for item in items:
            charge_top, user = item
            top.append(self.pack_top(uid=user.id,nick=user.nick,avatar=user.avatar,gold=user.gold, vip=user.vip))
        if RANK_FAKE_CHARGE_ENABLE:
            self.merage_fake(top, RANK_FAKE_CHARGE)
        return top

    def make_money_top(self,session, rank_time):
        query = session.query(TRankMakeMoneyTop, TUser).filter(TRankChargeTop.uid == TUser.id)
        if rank_time == RANK_LAST_WEEK:
            query = query.filter(and_(TRankMakeMoneyTop.add_year == datehelper.get_last_week().strftime('%Y'),TRankMakeMoneyTop.week_of_year == datehelper.get_last_week().strftime('%W')) )
        elif rank_time == RANK_THIS_WEEK:
            query = query.filter(and_(TRankMakeMoneyTop.add_year == datehelper.get_datetime().strftime('%Y'),TRankMakeMoneyTop.week_of_year == datehelper.get_datetime().strftime('%W')) )
        items = query.order_by(desc(TUser.gold)).limit(RANK_MAKE_MONEY_TOP).all()

        top = []
        for item in items:
            make_money, user = item
            top.append(self.pack_top(uid=user.id,nick=user.nick,avatar=user.avatar,gold=user.gold, vip=user.vip))
        if RANK_FAKE_MAKE_MONEYD_ENABLE:
            self.merage_fake(items, RANK_FAKE_MAKE_MONEYD)
        return top


    def set_pb(self, resp, items):

        for index in range(len(items)):
            protohelper.set_top(resp.body.players.add(), items[index], index)


    def merage_fake(self, data, fake_data):
        if len(data) <= 0:
            data = fake_data
        else:
            for fake in fake_data:
                if len(data) >= RANK_FAKE_LEN:
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

class RewardObject:

    def __init__(self, service):
        self.service = service
        self.conf = REWARD_CONF
        self.result = {
            'incr_gold':0,
            'incr_diamond':0,
            'items_add':[]
        }

    def get_reward_id(self, reward):
        return self.conf.get(reward)['id']

    def get_reward_conf_by_id(self, task_id):
        for conf in self.conf.values():
            if int(conf['id']) == task_id:
                return conf

    # 修改昵称
    def task_change_nick(self, session, user_info, new_nick):
        task_id = self.get_reward_id('update_nick')

        if user_info.nick == new_nick:
            return

        if self.reward_log(session, user_info.id, task_id):
            return

    # 首次登陆
    def task_first_login(self, session, user):
        task_id = self.get_reward_id('first_login')
        if self.reward_log(session, user, task_id):
            return


    def reward_log(self, session, user, task_id):
        task_log = session.query(TRewardUserLog).filter(and_(TRewardUserLog.uid == user,TRewardUserLog.task_id == task_id)).first()

        if task_log is None:
            task_log = TRewardUserLog()
            task_log.uid = user
            task_log.task_id = task_id
            task_log.state = 1 # 1=已完成，未领取 。 0 = 已完成，已领取。 其他 = 未完成
            task_log.create_time = datehelper.get_today_str()
            session.add(task_log)


        if task_log.state == 0:
            return True
        return False


    def is_undone(self,session,user, task_id):
        task_log = session.query(TRewardUserLog).filter(and_(TRewardUserLog.uid ==user,TRewardUserLog.task_id == task_id)).first()

        if task_log is None:
            return True
        if task_log.state == 0:
            return True
        return False

    def edit_reward_state(self, session, user, task_id):
        session.query(TRewardUserLog).with_lockmode("update").filter(and_(TRewardUserLog.uid == user, TRewardUserLog.task_id == task_id,TRewardUserLog.state == 1)).update({
            TRewardUserLog.state: 0,
            TRewardUserLog.finish_date: datehelper.get_date_str()
        })



    # 领取奖励
    def give_user_reward(self, session, user_info, task_id):
        task = self.get_reward_conf_by_id(task_id)
        if task is None:
            return False

        if task.get('gold', 0) > 0:
            user_info.gold = user_info.gold + task.get('gold')
            self.result['incr_gold'] = task.get('gold')
        if task.get('diamond', 0) > 0:
            user_info.diamond = user_info.diamond + task.get('diamond')
            self.result['incr_diamond'] = task.get('diamond')
        if task.get('items') is not None and task.get('items') != '':
            self.result['items_add'] = []
            for item in task.get('items').split(','):
                self.service.bag.save_user_item(session, user_info.id, item[0], item[2])
                self.result['items_add'].append(self.service.item.format_item(session, item[0], item[2]) )
        self.service.da.save_user(session, user_info)
        return True

    @staticmethod
    def task_edit_avatar(service, session, user_info, avatar):

        # 验证是否完成任务
        if user_info.avatar == avatar:
            return

        # 9 = 上传头像, 已经加过钱了，就直接返回
        if RewardObject.check_reward_log(session, user_info.id, 9 ):
            return

        # 给用户加钱或道具
        RewardObject.reward_done(session, user_info, 9, BagObject())

        # 发送邮件
        MessageObject.send_mail(session, user_info, 9, REWARD_CONF.get(9) )

        # 广播
        # MessageObject.push_message(service,[user_info.id],5,'', NotificationType.N_BROADCAST )


    @staticmethod
    def check_reward_log(session, uid, task_id):
        task_log = session.query(TRewardUserLog).filter(and_(TRewardUserLog.uid == uid,TrewardUserLog.task_id == task_id)).first()

        if task_log is None:
            task_log = TRewardUserLog()
            task_log.uid = uid
            task_log.task_id = task_id
            task_log.state == 1 # 1=已完成，未领取
            task_log.create_time = datehelper.get_today_str()
            session.add(task_log)

        # 0 = 已完成，已领取
        if task_log.state == 0:
            return True
        return False

    @staticmethod
    def reward_done(session,user_info,task_id, bag = None):
        task = REWARD_CONF.get(9)
        if task is not None:
            if task.get('gold') > 0:
                user_info.gold = user_info.gold + task.get('gold')
            if task.get('diamond') > 0:
                user_info.diamond = user_info.diamond + task.get('diamond')
            if task.get('items') is not None and task.get('items') != '':
                for item in task.get('items').split(','):
                    bag.save_user_item(user_info.id, item[0], item[2])
            return True
        return False

    @staticmethod
    def is_done(round):
        if round == REWARD_PLAY_ROUND[-1][0]:
            return True

    @staticmethod
    def get_next_round(total):
        if total > REWARD_PLAY_ROUND[-1][0]:
            return REWARD_PLAY_ROUND[0]
        if total == 0:
        	return REWARD_PLAY_ROUND[0]
     	if total == 1:
     		return REWARD_PLAY_ROUND[1]
        if total == REWARD_PLAY_ROUND[-1][0]:
            return REWARD_PLAY_ROUND[-1]

        for index in range(len(REWARD_PLAY_ROUND)):
            if REWARD_PLAY_ROUND[index][0] <= total and total < REWARD_PLAY_ROUND[index+1][0]:
                return REWARD_PLAY_ROUND[index+1]

    @staticmethod
    def get_conf(total):
        for index in range(len(REWARD_PLAY_ROUND)):
            if REWARD_PLAY_ROUND[index][0] == total:
                return REWARD_PLAY_ROUND[index]
        return None




# =============================>
class ShopObject2:
    def __init__(self,dataaccess,session):
        self.da = dataaccess
        self.session = session

    # 购买商品
    def buy(self, user, shop_item, count):
        if shop_item.type == SHOP_GOLD and int(user.diamond) >= int(shop_item.diamond):
            self.buy_gold(user,shop_item,count)
            return True
        elif shop_item.type == SHOP_ITEM and int(user.diamond) >= ( int(count) * int(shop_item.diamond) ):
            self.buy_item(user,shop_item,count)
            return True
        return False

    # 拿钻石换金币，购买金币
    def buy_gold(self, user, shop_item, count):
        user.diamond = user.diamond - shop_item.diamond
        user.gold = user.gold + shop_item.shop_gold + shop_item.extra_gold
        self.da.save_user(self.session,user)

    # 拿钻石换道具，购买道具
    def buy_item(self,service,session, user, shop_item,count):
        user.diamond = user.diamond - ( int(shop_item.diamond) * int(count) )
        service.bag.save_user_item(session, user.id, shop_item.item_id, count)
        service.da.save_user(self.session,user)

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

    @staticmethod
    def send_mail(session, user_info, task_id, **kwargs):

        # 加入邮件日志，待用户下次启动拉取
        mail = TMail()
        mail.from_user = 10000
        mail.to_user = user_info if type(user_info) == int else user_info.id
        mail.sent_time = int(time.time())
        mail.title = kwargs.get('title')
        mail.content = kwargs.get('content')
        mail.type = kwargs.get('type')
        mail.diamond = kwargs.get('diamond',0)
        mail.gold = kwargs.get('gold',0)
        mail.items = kwargs.get('items')
        mail.gifts = kwargs.get('gifts')
        mail.received_time = kwargs.get('received_time')
        mail.state = 0 # 0 = 未收取
        session.add(mail)

    @staticmethod
    def push_message(service,users,p1,p2,notifi_type = N_BROADCAST):
        item = {'users':users,'param1':p1,'param2':p2,'notifi_type':notifi_type}
        service.redis.lpush('notification_queue', json.dumps(item))
        print '--------------------------------------------------------------------------->'


class BagObject:
    def __init__(self, service):
        self.service = service

    def user_init(self,session, uid):
        str = ''
        for item in ITEM_MAP.values():
            str += '(%d,%d,%d),' % (uid, item[0],0)
        session.execute('INSERT IGNORE INTO bag_item VALUES'+(str[:-1]))

    def has_item(self,session, user, item_id, countof = 1):
        item = session.query(TBagItem).filter(and_(TBagItem.uid == user, TBagItem.item_id == item_id)).first()
        if item == None or item.countof < countof:
            return False
        return True

    def use_horn_item(self, session, user,count):
        result = self.use_user_item(session, user,ITEM_MAP['horn'][0])

        if result > 0:
            return True
        return False

    def send_horn_item(self, users,user_info, content):
        MessageObject.push_message(self.service, users, 7, {'message':content,'nick_id':user_info.id,'nick':user_info.nick,'vip':self.service.vip.to_level(user_info.vip_exp)})

    def save_user_gift(self, user,gift_id,countof):
        self.save_countof({'table_name':'bag_gift','stuff_id':gift_id,'uid':user,'countof':countof,'stuff_field':'gift_id'})

    def save_user_item(self, session, user,item_id,countof):
        self.save_countof(session, {'table_name':'bag_item','stuff_id':item_id,'uid':user,'countof':countof,'stuff_field':'item_id'})

    def save_countof(self,session, fields):
        insert_stmt = "INSERT INTO "+fields['table_name']+"(uid,"+fields['stuff_field']+",countof) VALUES (:col_1,:col_2,:col_3) ON DUPLICATE KEY UPDATE countof = countof + :col_3;"
        session.execute(insert_stmt, {
            'col_1':fields['uid'],
            'col_2':fields['stuff_id'],
            'col_3':fields['countof']
        })
        session.flush()

    def use_user_item(self, session, user, item_id, countof = 1):
        return self.del_countof(session, {'table_name':'bag_item','stuff_id':item_id,'uid':user,'countof':countof,'stuff_field':'item_id'})

    def del_countof(self,session, fields):
        delete_stmt = "UPDATE "+fields['table_name']+" SET countof = countof - :col_1 WHERE uid = :col_2 AND item_id = :col_3 AND countof > 0"
        return session.execute(delete_stmt,{
            'col_1':fields['countof'],
            'col_2':fields['uid'],
            'col_3':fields['stuff_id']
        }).rowcount

    def get_user_item(self,session, user, item_id):
        return session.query(TBagItem).filter(and_(TBagItem.item_id == item_id, TBagItem.uid == user)).first()

    def use_item(self, service,user, item_name, **args):
        return getattr(self, ITEM_MAP[item_name][1])(service, user, args)

    def use_kick(self, service, uid,args):
        return True

    def use_tgold(self, service, uid, args):
        return True

    def use_horn(self, service, uid, args):
        cachehelper.add_notification_queue(service.redis,service.redis.hkeys('online'), 7,{'message':args['message'],"nick_id":args['nick_id'],"nick":args['nick'],"vip":args['vip']})

    def use_exp_1(self, service, user,args):
            if type(user) == int:
                user = service.da.get_user(user)
            user.vip_exp = user.vip_exp + 1
            vip = VIPObject.get_vip(user.vip_exp)
            if user.vip < vip:
                user.vip = vip
            return service.da.save_user(self.session, user)

    def use_exp_10(self, service, user,args):
        if type(user) == int:
            user = service.da.get_user(user)
        user.vip_exp = user.vip_exp + 10
        vip = VIPObject.get_vip(user.vip_exp)
        if user.vip < vip:
            user.vip = vip
        return service.da.save_user(self.session, user)

class ResultObject:

    @staticmethod
    def get_result(user_info, ):
        pass
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
        access_service = self.service.redis.hget("online", user)
        if access_service != None:
            return int(access_service)
        return 0


    def notify_one(self,event,user):
        access_id = self.offline(user)
        if access_id == 0:
            return False
        self.service.send_client_event(access_id,user,event.header.command,event.encode())
        return True




class BrokeObject:

    def __init__(self, service):
        self.service = service



    @staticmethod
    def query_broke(uid, r, vip_conf):
        # 可领取的次数总数
        total = vip_conf['relief_time']
        # 每次领取金额数
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
            service.redis.expireat(key, datehelper.next_midnight_unix(delay_sec = 5) )
            remain = int(service.redis.decr(key))
            return 0,good


class VIPObject:

    def __init__(self, service):
        self.service = service
        self.vip = VIP_CONF

    def denied_buy_gold(self, vip):

        if vip < BUY_GOLD_LEVEL:
            return True
        return False

    def denied_sell_gold(self, vip):

        if vip < SELL_GOLD_LEVEL:
            return True
        return False

    def over_friend_max(self, vip, num):
        return self.over_max('friend_max', vip,num)

    def over_bank_max(self, vip, money):
        return self.over_max('bank_max', vip, money)

    def over_broke_max(self, vip, relief_time ):
        return self.over_max('relief_time', vip, relief_time)

    def over_max(self, name, vip, max):
        vip_max = self.vip[vip][name]
        if vip_max < max:
            return True
        return False

    def to_level(self, charge):
        return self.get_vip_conf(charge)['level']

    def get_vip_conf(self, charge):
        lst_len = len(self.vip)
        for index in range(lst_len):
            if index + 1 == lst_len:
                if charge >= self.vip[index].get('charge'):
                    return self.vip[index]
                else:
                    return self.vip[index - 1]

            if charge >= self.vip[index].get('charge') and charge < self.vip[index + 1].get('charge'):
                return self.vip[index]


    @staticmethod
    def get_vip(charge):
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
    def check_vip_auth(vip, auth):
        conf = VIP_CONF[vip]
        if auth in conf['auth']:
            return True
        return False


class ItemObject:

    def __init__(self, service):
        self.service = service

    def get_item_by_id(self, session, item_id):
        return session.query(TItem).filter(TItem.id == item_id).first()

    def format_item(self, session, item_id, count):
        item = self.get_item_by_id(session, item_id)
        return {
            'id':item.id,
            'name':item.name,
            'icon':item.icon,
            'count':count,
            'description':item.description,
        }

    @staticmethod
    def get_items(session, item_ids):
        return session.execute('SELECT * FROM item WHERE id IN ('+ ','.join(item_ids) +')').fetchall()

    @staticmethod
    def get_item(session, item_id):
        return session.query(TItem).filter(and_(TItem.id == item_id)).first()

    @staticmethod
    def get_item_conf(item_id):
        return ITEM_CONF.get(item_id)

