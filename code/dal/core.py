#coding:utf8

import gevent
from gevent import monkey;monkey.patch_all()
import json
import logging
import traceback
from sqlalchemy.sql import select, update, delete, insert, and_,or_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

from db.connect import *
from db.user import *



from user import DalUser
from user import DalUserGoldFlower

class DataAccess:
    def __init__(self,redis):
        self.redis = redis

    def get_user(self,uid):
        dal_user = DalUser(self,uid)
        if dal_user.load():
            return dal_user
        return None

    def save_user(self,session,dal_user):
        dal_user.save(session)

    def get_user_gf(self,uid):
        dal_user_gf = DalUserGoldFlower(self, uid)
        if dal_user_gf.load():
            return dal_user_gf
        return None

if __name__ == "__main__":
    import redis
    redis = redis.Redis()
    da = DataAccess(redis)
    da.get_user(10019)