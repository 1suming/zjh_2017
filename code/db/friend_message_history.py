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

tab_friend_message_history = Table("friend_message_history", metadata,
                 Column("id",Integer, primary_key=True),
                 Column("from_user",Integer),
                 Column("from_user_nick",String(40)),
                 Column("from_user_avatar",String(255)),
                 Column("to_user", Integer),
                 Column("to_user_nick",String(40)),
                 Column("to_user_avatar",String(255)),
                 Column("sent_time",Integer),
                 Column("content",String(2000)),
                 Column("status",SMALLINT),
                 Column("create_time",DateTime)
                 )
                 

                 
class TFriendMessageHistory(TableObject):
    def __init__(self):
        TableObject.__init__(self)
    
mapper_friend_message_history = Mapper(TFriendMessageHistory,tab_friend_message_history)

if __name__=="__main__":
    pass