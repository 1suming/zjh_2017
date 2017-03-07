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

tab_reward_signin_month = Table("reward_sigin_month", metadata,
                    Column("id", Integer, primary_key=True),
                    Column("uid", Integer),
                    Column("signin_days",Integer),
                    Column("last_signin_day",Date),
                 )

class TRewardSigninMonth(TableObject):
    def __init__(self):
        TableObject.__init__(self)
    def __repr__(self):
        return 'id=%d,uid=%d,signin_days=%d,last_signin_day=%s' % \
               (self.id,self.uid,self.signin_days,self.uid,self.sign_days)

mapper_reward_signin_month = Mapper(TRewardSigninMonth,tab_reward_signin_month)

if __name__=="__main__":
    pass