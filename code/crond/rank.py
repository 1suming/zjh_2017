# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import sys
import time
import redis
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists,desc

from config.rank import *
from db.connect import *
from db.rank_charge_top import *
from db.user import *
from db.rank_make_money_top import *
from helper import datehelper
from dal.core import *
from hall.hallobject import *

RANK_REWARD = {
    # 金币，钻石，vip经验，[(道具1,数量),(道具2,数量),]
    'rank_charge_top':(10000,1000,1000,[(1,12),(2,24)],),
    'rank_gold_top':(10000,1000,1000,[(1,12),(2,24)],),
    'rank_make_money_top':(10000,1000,1000,[(1,12),(2,24)],),
}
redis_conf = {
    # 'host':'192.168.2.75','port':6379,'db':0,'password':'Wgc@123456',
    'host':'127.0.0.1','port':6379,'db':0,'password':'Wgc@123456',
}

session = Session()
class CrondServer:

    def __init__(self):
        self.redis = redis.Redis(**redis_conf)

        # self.da = DataAccess(self.redis)

    def load_data(self, rank_type):
        return getattr(self, 'load_'+rank_type)()

    def save_data(self, rank_type, top_one):
        return getattr(self, 'save_'+rank_type)(rank_type, top_one)

    def load_rank_charge_top(self):
        return session.query(TRankChargeTop).filter(TRankChargeTop.add_date == datehelper.get_yesterday().strftime('%Y-%m-%d')).order_by(desc(TRankChargeTop.gold)).limit(RANK_CHARGE_REWARD)
    def load_rank_gold_top(self):
        return session.query(TUser).order_by(desc(TUser.gold)).limit(RANK_WEALTH_REWARD)
    def load_rank_make_money_top(self):
        return session.query(TRankMakeMoneyTop).filter(and_(TRankMakeMoneyTop.add_year == time.strftime('%Y'), TRankMakeMoneyTop.week_of_year == time.strftime('%W'))).order_by(desc(TRankMakeMoneyTop.gold)).limit(RANK_MAKE_MONEY_REWARD)


    def save_rank_charge_top(self, rank_type, top_one):
        user = top_one['uid'] if hasattr(top_one,'uid') else top_one['id']
        key = 'u'+str(user)

        user_info = self.redis.hgetall(key)
        print '===>before,',top_one.id,top_one.gold,top_one.diamond
        if len(user_info) > 0:
            user_info['gold'] = int(user_info['gold']) + RANK_REWARD[rank_type][0]
            user_info['diamond'] = int(user_info['diamond']) + RANK_REWARD[rank_type][1]
            self.redis.hmset(key, user_info)
        result = session.query(TUser).filter(TUser.id == user).update({
            TUser.gold : TUser.gold + RANK_REWARD[rank_type][0],
            TUser.diamond : TUser.diamond + RANK_REWARD[rank_type][1],
        })
        print '===>after,',top_one.id,top_one.gold,top_one.diamond
        bag = BagObject(self)
        for item in RANK_REWARD[rank_type][3]:
            bag.save_user_item(session, user,item[0],item[1])
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