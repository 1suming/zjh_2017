# -*- coding: utf-8 -*-
__author__ = 'Administrator'


BORADCAST_CONF = {
    'reg':u'欢迎新人玩家%s加入天天炸翻天，开启快乐的游戏之旅，预祝早日成为人生赢家！ ',
    'vip_up':u'玩家%s一掷千金，成功升级为%s，成为人生赢家！',
    'win_game':u'玩家xxx（昵称）在xx场（游戏场地）赢得xx万金币，恭喜发财！小赌养家糊口，大赌发家至富！',
    'sys':u'【系统提醒】：本游戏不提供任何形式的游戏外充值，请勿上当受骗！',
    'sys2':u'【系统提醒】：为了感谢您对游戏的支持和热爱，从即日起到3月31日，特进行首充大礼包超值放送，数量有限，先到先得！',
    'trade_sell':u'玩家%s在金币交易所挂售%d金币，仅需要%d钻石，快去看看吧！',
    'gold_top_online':u'财富榜排名第%d位的玩家%s上线了!',
    'luck_money_game':u'恭喜玩家%s在%s场拿到%s，通杀全场！', # （场次）（顺金或者豹子牌型）
    'make_money_top':u'恭喜玩家%s获赠赢取%d金币，跃升周赚金榜榜第%d名。',
    'charge_top':u'恭喜玩家%s充值%d元，跃升今日充值榜第%d名。',
}


def broadcast_register(uid,name):
    message = BORADCAST_CONF["reg"] % (name)

def broadcast_upgrade_vip(uid,name,vip):
    pass

def broadcast_win_game():
    pass

def broadcast_good_pokers(uid,name,poker_type):
    pass