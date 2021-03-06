# -*- coding: utf-8 -*-
import json
from proto.constant_pb2 import *
import var

BORADCAST_CONF = {
    'reg':u'欢迎新人玩家%s加入全民炸翻天，开启快乐的游戏之旅，预祝早日成为人生赢家！ ',
    'good_pokers':u'恭喜玩家%s在%s拿到%s，通杀全场！', # （场次）（顺金或者豹子牌型）
    'win_game':u'玩家%s 在%s 赢得%d万金币，恭喜发财！小赌养家糊口，大赌发家至富！',

    #------------ 未实现 -----------

    'vip_up':u'玩家%s一掷千金，成功升级为%s，成为人生赢家！',
    'sys':u'【系统提醒】：本游戏不提供任何形式的游戏外充值，请勿上当受骗！',
    'sys2':u'【系统提醒】：首充大礼包超值放送，数量有限，先到先得！',
    'trade_sell':u'玩家%s在金币交易所挂售%d金币，仅需要%d钻石，快去看看吧！',
    'gold_top_online':u'财富榜排名第%d位的玩家%s上线了!',

    'make_money_top':u'恭喜玩家%s获赠赢取%d金币，跃升周赚金榜榜第%d名。',
    'charge_top':u'恭喜玩家%s充值%d元，跃升今日充值榜第%d名。',
}

PLACES = {
    TABLE_L : u"初级场",
    TABLE_M : u"中级场",
    TABLE_H : u"高级场",
    TABLE_H2 : u"大师场",
}


def send_register(uid,name):
    message = BORADCAST_CONF["reg"] % (name)
    send_broadcast(message)

def send_win_game(redis, uid,name,table_type,gold,vip_exp):
    if gold < 1:#1000000:
        return

    # place = PLACES[table_type]
    #gold = gold / 10000
    # message = BORADCAST_CONF["win_game"] % (name,place,gold)
    send_broadcast(redis, var.PUSH_TYPE['table_winner'],{'winner_nick':name,'table_type':table_type,'winner_gold':gold,'vip_exp':vip_exp})

def send_good_pokers(redis, uid,name,table_type,pokers, vip_exp):
    pokers_index = None
    if pokers.is_baozi():
        pokers_index = 2 # u"豹子"
    if pokers.is_tonghuashun():
        pokers_index = 1 # u"顺金"
    if pokers_index == None:
        return

    # place = PLACES[table_type]
    # message = BORADCAST_CONF["good_pokers"] % (name,place,pokers_str)

    send_broadcast(redis,var.PUSH_TYPE['luck_poker'], {
        'nick':name,'vip_exp':vip_exp,'table_type':table_type,'luck_type':pokers_index
    })


def send_broadcast(redis,push_type, message):
    # TBD
    users = redis.hkeys('online')
    p1 = push_type
    p2 = message

    print '------------------>broadcast',message

    item = {'users':users,'param1':p1,'param2':p2,'notifi_type':N_BROADCAST}
    redis.lpush('notification_queue', json.dumps(item))
