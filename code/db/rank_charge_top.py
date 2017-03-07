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
                 Column("uid", Integer, primary_key=True),
                 Column("nick",String(40)),
                 Column("avatar", String(255)),
                 Column("gold",BigInteger),
                 Column("add_date",Date, primary_key=True),
                 Column("vip",SMALLINT),
                 Column("charge_money", DECIMAL(11,2))
                 )
                 

                 
class TRankChargeTop(TableObject):
    def __init__(self):
        TableObject.__init__(self)
        
mapper_rank_charge_top = Mapper(TRankChargeTop,tab_rank_charge_top)

if __name__=="__main__":
    pass