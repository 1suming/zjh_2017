#coding:utf-8

"""
���ݿ����ӹ���
"""

__author__ = "liangxiaokai@21cn.com"
__version__ = "1.0"
__date__ = "2011/04/14"
__copyright__ = "Copyright (c) 2011"
__license__ = "Python"

from connect import *

from sqlalchemy import Table,Column,func
from sqlalchemy.types import  *
from sqlalchemy.ext.declarative import declarative_base

TCB_GAME_RECYCLE    = 0
TCB_CHARGE          = 1
TCB_ITEM            = 2
TCB_SHOP_GOLD       = 3
TCB_SHOP_DIAMOND    = 4
TCB_GIFT            = 5
TCB_BANKRUPT        = 6
TCB_DAILY_TASK_GIVE = 7
TCB_SIGN            = 8
TCB_GAME_GIVE       = 9
TCB_OTHER_TASK_GIVE = 10
TCB_ROBOT_LOSE      = 11
TCB_ROBOT_WIN       = 12
TCB_CODE            = 13
TCB_ROBOT_RECHARGE  = 14

tab_account_book = Table("account_book", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("type",SmallInteger,default = 0,nullable =False), # 0:付出 1:回收
                 Column("gold",BigInteger,default=0,nullable =False),
                 Column("diamond",Integer,default=0,nullable =False),
                 Column("uid",Integer,default=-1,nullable =False),
                 Column("game_id",Integer,default=-1,nullable =False),
                 Column("mode", SmallInteger,default=0,nullable =False), # 0: 游戏抽水, 1:充值, 2: 道具回收 3:商城付出金币 4: 商城回收钻石
                                                     # 5: 礼物赠送回收  6: 破产赠送 7: 日常任务赠送 8: 签到赠送 9: 游戏奖励赠送
                                                     # 10: 其它任务赠送 11: 机器人付出, 12:机器人回收, 13 : 兑换码 14:机器人补钱
                 Column("param1",Integer,default=-1),
                 Column("param2",String(40),default=""), # 附加信息
                 Column("create_time",DateTime,nullable =False),
                 )
                 


class TAccountBook(TableObject):
    def __init__(self):
        TableObject.__init__(self)

mapper_account_book = Mapper(TAccountBook,tab_account_book)

if __name__=="__main__":
    pass