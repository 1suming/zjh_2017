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


REGISTER_NICK_COLOR = 'FF0066'
BORADCAST_CHANGE_NAME = 1
BORADCAST_SEND_CHAT = 7

DEFAULT_USER={
    'avatar':[''],
    'sign':u'小赌怡情，大赌致富。',
    'nick':[u'游客',u'来宾',u'赌客',u'guest'],
    'nick_num':["%03d",(0, 999)],
    'gold':50000,
    'diamond':1000,
    'vip':0,
    'money':0,
    'charm':0,
    'birthday':dt_date(2000,1,1),
    'sex':0,
    'is_charge':0,
    'vip_exp':0,
    'default_item':(1,1),
}

DEFAULT_USER_GLODFLOWER ={
    'exp':0,
    'win_games':0,
    'total_games':0,
    'best':'',
    'wealth_rank':0,
    'win_rank':0,
    'charm_rank':0,
    'charge_rank':0,
    'max_bank':0,
    'max_items':0,
    'max_gifts':0,
    'signin_days':-1,
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


PAY_RESULT_URL = 'http://121.201.29.89:18000/pay_result'
CP_KEY = 'bde25760c1556899efc0dff13bf41b4e' # bde25760c1556899efc0dff13bf41b4e

TAX_NUM = 0.05 # 金币交易，税率


QUICK_CHARGE = [
    # 分，万，商品名称
    (500, 15, u'新手场',1),
    (3000, 90, u'普通场',1),
    (15000, 450, u'高级场',1),
    (60000, 1800, u'大师场',1),
]
NO_KICK_LEVEL = 6   # 被踢的人在vip6及以上等级有免踢权限
BUY_GOLD_LEVEL = 1  # vip1及以上才可以购买金币
SELL_GOLD_LEVEL = 3 # vip3及以上等级可在金币交易中出售金币

# 系统提醒时间
NOTI_TIME = 300
NOTI_TIME_2 = 180
	# optional int32 id = 1;
	# required int32 money = 2;
	# required int32 diamond = 3;
	# required int32 gold = 4;
	# required int32 hore = 5;
	# required int32 kicking_card = 6;
	# required int32 vip_card = 7;
PASS_ENCRY_STR = 'cqkj2017'

# 首冲
FRIST_CHARGE = {
    'title':u'首充',
    'money' : 1000,
    'real_money':1,
    'diamond' : 10,
    'gold' : 30, # 单位w
    'hore' : 10,
    'kicking_card':10,
    'vip_card' :1,
    'items':'1-10,2-10,4-1'
}

# 系统推送消息类型
PUSH_TYPE ={
    'new_user_register':1,
    'vip_upgrade':2,
    'table_winner':3,
    'send_gift':4,
    'sys_broadcast':5,
    'gold_trade':6,
    'world_horn':7,
    'luck_poker':8,
    'rank_top':9,
    'charge_success':10,
}

# 出售金币时，兑换的钻石 / 金币 = 比率（乘以位数）
SELL_RATE = 10000

# 每日全场任务完成，赠送钻石脚本区间
DT_ALL_DIAMOND = (1,100)

# ******************************* web *****************************************
# 第三方支付的回调
CALLBACK = 'http://121.201.29.89:18000/pay_result'
# 与客户端的秘钥
CHARGE_KEY = 'cqkj2017'
# 给第三方支付的秘钥
CP_KEY = 'bde25760c1556899efc0dff13bf41b4e'
# avatar头像上传地址
UPDATE_AVATAR_URL = 'http://121.201.29.89:18000/avatar'
# 更新文件上传地址
UPGRADE_URL = 'http://121.201.29.89:18000/web/static/upgrade/'
