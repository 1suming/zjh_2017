#coding: utf-8
import time
import random
from datetime import time as dt_time
from datetime import date as dt_date
from proto.constant_pb2 import *



DEBUG                       = True
UNIT_TEST                   = False


#http://api.chanzor.com/send?account=wanggouchao&password=153457&mobile=13480879974&content=%E6%B5%8B%E8%AF%95%E9%AA%8C%E8%AF%81%E7%A0%81%EF%BC%9A4321%E3%80%90%E7%BD%91%E8%B4%AD%E6%BD%AE%E3%80%91
SMS_CONF={
    'zc_sms':{
        'account':'wanggouchao',
        'password':'153457',
    },
    'url':"http://api.chanzor.com/send",
    'sign':u'【网购潮科技】',
    'tpl':u'您的短信验证码是@如非本人操作，请忽略此短信。本短信免费。',
    'exp':120,
}

MAIL_TEMPLATE = {
	1:u'魅力值增加，+%d',
	2:u'魅力值减少，-%d',
	3:u'同意您的好友申请，并添加您为好友',
	4:u'已拒绝您的好友申请',
	5:u'出售金币成功',
	6:u'恭喜到达活动要求',
	7:u'获得%d个喇叭，赶快去吼一嗓子吧',
	8:u'获得%d个钻石，赶快去背包里看看吧',
    9:u'点击领取使用',
}

BANK_LELVEL_LIMIT = {
    1:100000,
    2:200000,
    3:300000,
    4:400000,
    5:500000,
}

REGISTER_NICK_COLOR = 'FF0066'
BORADCAST_CHANGE_NAME = 1
BORADCAST_SEND_CHAT = 7

DEFAULT_USER={
    'avatar':[''],
    'sign':u'小赌怡情，大赌致富。',
    'nick':[u'游客',u'来宾',u'赌客',u'guest'],
    'nick_num':["%03d",(0, 999)],
    'gold':0,
    'diamond':0,
    'vip':0,
    'money':0,
    'charm':0,
    'birthday':dt_date(2000,1,1),
    'sex':0,
}

DEFAULT_USER_GLODFLOWER ={
    'exp':0,
    'win_games':0,
    'total_games':0,
    'best':'0',
    'wealth_rank':0,
    'win_rank':0,
    'charm_rank':0,
    'charge_rank':0,
    'max_bank':0,
    'max_items':0,
    'max_gifts':0,
    'signin_days':0,
    'last_signin_day':dt_date(2000,1,1),
    'oneline_time':0,
    'login_times':0,
    'change_nick':-1,
}

PRM_SIGN_LUCK_DAYS = [7,14,21,28]
PRM_CHANGE_NAME_MINUS_DIAMOND = 100
PRM_MAX_DEVICE_ID = 15
PRM_MAX_PASSWORD_LEN = 15
PRM_MIN_PASSWORD_LEN = 6

SYS_MAX_SIGN_DAY = 7

STATE_IS_SHOW = 0
STATE_NO_ACCEPT_REWARD = 1
STATE_ACCEPT_REWARD = 0
STATE_NEED_POPUP = 0
STATE_DISABLED = -1
STATE_ENABLE = 0