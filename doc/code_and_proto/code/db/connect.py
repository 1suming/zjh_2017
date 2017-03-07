#coding:utf-8

"""
数据库连接管理
"""

__author__ = "liangxiaokai@21cn.com"
__version__ = "1.0"
__date__ = "2011/04/14"
__copyright__ = "Copyright (c) 2011"
__license__ = "Python"

from gevent import monkey;monkey.patch_all()
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,create_session
from sqlalchemy import MetaData

from sqlalchemy import Table,Column,func
from sqlalchemy.types import  Integer, String,TIMESTAMP
from sqlalchemy.orm import Mapper
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#engine = create_engine('mysql://game:game@localhost/game?charset=utf-8', echo=False,pool_recycle=3600)
#engine = create_engine('mysql+mysqlconnector://root:123456@localhost/game?charset=utf8', echo=False,pool_recycle=3600)
#user_engine = create_engine('mysql+mysqlconnector://root:123456@localhost/logindb?charset=utf8', echo=False,pool_recycle=3600)
# autocommit必须是True，这样可以自行控制事务
# 另外，在使用mysql时，需要表的类型是innoDB类型，而不是MyISAM类型
#Session = sessionmaker(bind=engine,autoflush=False,autocommit=True,expire_on_commit = False)
#UserSession = sessionmaker(bind=user_engine,autoflush=False,autocommit=True,expire_on_commit = False)

metadata = MetaData(None)

class Database:
    def __init__(self):
        self.session_maker = None
        self.user_session_maker = None
    
    def get_session(self):
        if self.session_maker == None:
             self.setup_session("root","123456","game")
        return self.session_maker()
        
    def get_user_session(self):
        if self.user_session_maker == None:
              self.setup_user_session("root","123456","userdb")
        return self.user_session_maker()    
        
    def setup_session(self,user,password,database,host = "127.0.0.1",port = None,pool_size = 15):
        url_pattern = "mysql+mysqlconnector://%s:%s@%s:%d/%s?charset=utf8"
        url_pattern_no_port = "mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8"
        if port != None:
            url = url_pattern % (user,password,host,database,port)
        else:
            url = url_pattern_no_port % (user,password,host,database)
        
        engine = create_engine(url, echo=False,pool_recycle=3600,pool_size = pool_size)
        self.session_maker = sessionmaker(bind=engine,autoflush=False,autocommit=True,expire_on_commit = False)

    def setup_user_session(self,user,password,database,host = "127.0.0.1",port = None,pool_size = 5):
        url_pattern = "mysql+mysqlconnector://%s:%s@%s:%d/%s?charset=utf8"
        url_pattern_no_port = "mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8"
        if port != None:
            url = url_pattern % (user,password,host,database,port)
        else:
            url = url_pattern_no_port % (user,password,host,database)
        engine = create_engine(url, echo=False,pool_recycle=3600,pool_size = pool_size)
        self.user_session_maker = sessionmaker(bind=engine,autoflush=False,autocommit=True,expire_on_commit = False)
    
DATABASE  = Database()

class TableObject(object):

    def __setitem__(self,key,item):
        setattr(self,key,item)
        self._internal_props[key] = item
        
    def __getitem__(self,key):
        return getattr(self,key)
        
    def __init__(self):
        self._internal_props = {}

def Session():
    return DATABASE.get_session()
    
def UserSession():
    return DATABASE.get_user_session()

def create_tables(drop = False):
    import os
    import importlib

    session = Session()
    engine = session.connection().engine

    all = os.listdir(os.getcwd() + "/db")

    for name in all:
        if not name.endswith(".py"):
            continue

        name = name[:-3]
        if name in ("connect","__init__"):
            continue
        m = importlib.import_module("db." + name)
        try :
            print "====> create table ",name
            tab = getattr(m,"tab_" + name)
            if drop :
                tab.drop(engine)
        except:
            traceback.print_exc()
        tab.create(engine)
        #print dir(m)


if __name__=="__main__":
    """
    
    
    import sys
    if sys.argv[1] == "-drop":
        drop = True
    else:
        drop = False

    create_tables(drop)
    """
    
    DATABASE.setup_user_session("root","123456","smallapp")
    session = UserSession()
    count = 0
    
    from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey,DateTime,Integer
    
    small_apps = Table('small_apps', metadata,
         Column('id', Integer, primary_key=True),
         Column('name', String),
         Column('category', String),
         Column('description', String),
         Column('icon', String),
         Column('search_word', String),
         Column('create_time', DateTime),
         Column('good', Integer),
         Column('normal', Integer),
         Column('bad', Integer),
         )
         
    categorys = []
    
    with open("/Users/liangxiaokai/smallapps.txt") as f:
        lines = f.readlines()
        category = ""
        for line in lines:
            line = line.strip()
            dot_idx = line.find(".") 
            if dot_idx >= 0 and line[dot_idx:].startswith(". ["):
                category = line[dot_idx + 3:-1]
                categorys.append(category)
                continue
            
            if line == "":
                continue
            app = line
            count += 1
            
            ins = small_apps.insert().values(category=category,name=app,search_word=app)
            #print ins
            #session.execute(ins)
            print count,"--->",category,app
    
    for c in categorys:        
    	print c 
                
    session.close()


    