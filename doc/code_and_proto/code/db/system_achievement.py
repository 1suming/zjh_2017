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

tab_system_achievement = Table("system_achievement", metadata,
                    Column("uid", Integer, primary_key=True),
                    Column("achievements",String(2000)),
                    Column("values",String(500)),
                    
                 )
                 


class TSystemAchievement(TableObject):
    def __init__(self):
        TableObject.__init__(self)
    
mapper_system_achievement = Mapper(TSystemAchievement,tab_system_achievement)

if __name__=="__main__":
    pass