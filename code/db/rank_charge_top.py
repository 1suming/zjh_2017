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

tab_rank_charge_top = Table("rank_charge_top", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("uid", Integer),
                 Column("nick",String(40)),
                 Column("avatar", String(255)),
                 Column("gold",BigInteger),
                 Column("rank_reward",  String(255)),
                 Column("money_maked",Integer),
                 Column("add_date",Date),
                 )
                 

                 
class TRankChargeTop(TableObject):
    def __init__(self):
        TableObject.__init__(self)
        
mapper_rank_charge_top = Mapper(TRankChargeTop,tab_rank_charge_top)

if __name__=="__main__":
    pass