#coding:utf-8

"""
\u6570\u636E\u5E93\u8FDE\u63A5\u7BA1\u7406
"""

__author__ = "liangxiaokai@21cn.com"
__version__ = "1.0"
__date__ = "2011/04/14"
__copyright__ = "Copyright (c) 2011"
__license__ = "Python"

from connect import *

from sqlalchemy import Table,Column,func
from sqlalchemy.types import  *
from sqlalchemy.orm import Mapper

tab_mail = Table("Mail", metadata,
                 Column("id",Integer, primary_key=True),
                 Column("from_user",Integer,nullable =False),
                 Column("to_user",Integer,nullable =False),
                 Column("sent_time", Integer,nullable =False),
                 Column("title", String(100)),
                 Column("content", String(2000)),
             	 Column("type", SmallInteger,nullable =False),
             	 Column("diamond", BigInteger,default=0,nullable =False),
             	 Column("gold", BigInteger,default=0,nullable =False),
             	 Column("items", String(200)),
                 Column("gifts", String(200)),
             	 Column("received_time", Integer),
             	 Column("state", SmallInteger,default=0,nullable =False), # 0 未收取
                 )
                 

                 
class TMail(TableObject):
    def __init__(self):
        TableObject.__init__(self)
    
mapper_mail = Mapper(TMail,tab_mail)       

if __name__=="__main__":
    pass