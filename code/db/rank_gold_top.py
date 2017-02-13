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

tab_rank_gold_top = Table("rank_gold_top", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("uid", Integer),
                 Column("nick",String(40)),
                 Column("avatar", String(255)),
                 Column("gold",BigInteger),
                 Column("rank_reward",  String(255)),
                 Column("money_maked",Integer),
                 Column("create_time",DateTime),
                 )
                 

                 
class TRankGoldTop(TableObject):
    def __init__(self):
        TableObject.__init__(self)
        
mapper_rank_gold_top = Mapper(TRankGoldTop,tab_rank_gold_top)

if __name__=="__main__":
    pass