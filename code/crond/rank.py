# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import sys
import time
import redis
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists,desc

from db.connect import *
from db.rank_charge_top import *
from db.rank_gold_top import *
from db.rank_make_money_top import *
from db.user import *
from helper import datehelper
from rankconf import *
from dal.core import *
from hall.hallobject import *

session = Session()
class CrondServer:

    def __init__(self):
        self.redis = redis.Redis(host='192.168.2.75',port=6379,db=0,password='Wgc@123456')
        self.da = DataAccess(self.redis)

    def load_data(self, rank_type):
        return getattr(self, 'load_'+rank_type)()
    def save_data(self, rank_type, top_one):
        return getattr(self, 'save_'+rank_type)(rank_type, top_one)

    def load_rank_charge_top(self):
        return session.query(TRankChargeTop).filter(TRankChargeTop.add_date == datehelper.get_yesterday().strftime('%Y-%m-%d')).order_by(desc(TRankChargeTop.gold)).limit(10)
    def load_rank_gold_top(self):
        return session.query(TRankGoldTop).order_by(desc(TRankGoldTop.gold)).limit(10)
    def load_rank_make_money_top(self):
        return session.query(TRankMakeMoneyTop).filter(and_(TRankMakeMoneyTop.add_year == time.strftime('%Y'), TRankMakeMoneyTop.week_of_year == time.strftime('%W'))).order_by(desc(TRankMakeMoneyTop.gold)).limit(10)


    def save_rank_charge_top(self, rank_type, top_one):
        user_info = self.da.get_user(int(top_one['uid']))
        user_info.gold = user_info.gold + RANK_REWARD[rank_type][0]
        user_info.diamond = user_info.diamond + RANK_REWARD[rank_type][1]

        bag = BagObject()
        for item in RANK_REWARD[rank_type][3]:
            bag.save_user_item(top_one['uid'],item[0],item[1])
    def save_rank_gold_top(self, rank_type, args):
        self.save_rank_charge_top(rank_type,args)
    def save_rank_make_money_top(self, rank_type, args):
        self.save_rank_charge_top(rank_type,args)



    def run(self, func_name):
        items = self.load_data(func_name)
        for item in items:
            self.save_data(func_name, item)


if __name__ == '__main__':
    crond = CrondServer()
    # crond.run('rank_charge_top')
    crond.run('rank_gold_top')
    # crond.run('rank_make_money_top')