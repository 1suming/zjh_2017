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

tab_announcement = Table("announcement", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("category", String(255),nullable =False),
                 Column("title",String(255),nullable =False),
                 Column("content", String(255),nullable =False),
                 Column("sort",Integer,nullable =False),
                 Column("popup",SmallInteger,default=1,nullable =False), # 1 弹出
                 Column("has_action",SmallInteger,default=0,nullable =False), # 0 没有动作
                 Column("action",String(100),default="",nullable =False),
                 Column("start_time",DateTime,nullable =False),
                 Column("end_time",DateTime,nullable =False),
                 Column("create_time",DateTime,nullable =False),
                 )
                 


class TAnnouncement(TableObject):
    def __init__(self):
        TableObject.__init__(self)

    # def __repr__(self):
    #     return "brithday=%s,id=%d,mobile=%s,nick=%s,state=%d,imei=%s,imsi=%s,password=%s,create_time=%d,nick=%s,sign=%s,address=%s, sex=%d,channel=%d" % \
    #             (self.brithday,self.id,self.mobile,self.nick,self.state,self.imei,self.imsi,self.password,self.create_time,self.nick,self.sign,self.address, self.sex,self.channel)

mapper_announcement = Mapper(TAnnouncement,tab_announcement)

if __name__=="__main__":
    pass