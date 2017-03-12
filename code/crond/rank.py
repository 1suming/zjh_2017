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
from hall.hallobject import *

RANK_REWARD = {
    # 金币，钻石，vip经验，[(道具1,数量),(道具2,数量),]
    'rank_charge_top':(10000,1000,1000,[(1,12),(2,24)],),
    'rank_gold_top':(10000,1000,1000,[(1,12),(2,24)],),
    'rank_make_money_top':(10000,1000,1000,[(1,12),(2,24)],),
}
REDIS_CONF = {
    'host':'121.201.29.89','port':26379,'db':0,'password':'Wgc@123456',
}

DAILY_KEY = 'DailyTasks'
session = Session()
class CrondServer:

    def __init__(self):
        self.redis = redis.Redis(**REDIS_CONF)

        # self.da = DataAccess(self.redis)

    def load_data(self, rank_type):
        return getattr(self, 'load_'+rank_type)()

    def save_data(self, rank_type, top_one, top_index):
        return getattr(self, 'save_'+rank_type)(rank_type, top_one, top_index)

    def load_rank_charge_top(self):
        return session.query(TRankChargeTop).filter(TRankChargeTop.add_date == datehelper.get_yesterday().strftime('%Y-%m-%d')).order_by(desc(TRankChargeTop.charge_money)).limit(RANK_CHARGE_REWARD)
    def load_rank_gold_top(self):
        return session.query(TUser).order_by(desc(TUser.gold)).limit(RANK_WEALTH_REWARD)
    def load_rank_make_money_top(self):
        last_week = int(time.strftime('%W')) -1
        if last_week == 0:
            last_week = 1
        return session.query(TRankMakeMoneyTop).filter(and_(TRankMakeMoneyTop.add_year == time.strftime('%Y'), TRankMakeMoneyTop.week_of_year == last_week)).order_by(desc(TRankMakeMoneyTop.gold)).limit(RANK_MAKE_MONEY_REWARD)


    def save_rank_charge_top(self, rank_type, top_one, top_index):
        if top_index >= RANK_CHARGE_REWARD:
            return

        user = top_one['uid'] if hasattr(top_one,'uid') else top_one['id']
        if top_one.charge_money is None:
            return

        reward_diamond = int(top_one.charge_money) / RANK_CHARGE_RATE

        MessageObject.send_mail(session, user,0,
            title = u'充值榜奖励',
            content = RANK_CHARGE_MAIL % (top_index+1,reward_diamond),
            type = 1,
            diamond = reward_diamond,
            gold = 0,
            items = '')


    def save_rank_gold_top(self, rank_type, args):
        self.save_rank_charge_top(rank_type,args)

    def save_rank_make_money_top(self, rank_type, top_one, top_index):
        if top_index >= RANK_MAKE_MONEY_REWARD:
            return

        user = top_one['uid'] if hasattr(top_one,'uid') else top_one['id']

        MessageObject.send_mail(session,user,0,
            title = u'赚金榜奖励',
            content = RANK_MAKE_MONEY_MAIL % (top_index+1,RANK_MAKE_MONEY_REWARD_CONF[top_index+1]),
            type = 1,
            diamond = RANK_MAKE_MONEY_REWARD_CONF[top_index+1],
            gold = 0,
            items = '')



    def run(self, func_name):
        items = self.load_data(func_name)
        for index,item in enumerate(items):
            self.save_data(func_name, item, index)
        session.flush()

    def remove_daily_task(self):
        self.redis.delete(DAILY_KEY)
if __name__ == '__main__':
    crond = CrondServer()
    if len(sys.argv) > 3:
        func_name = sys.argv[1]
        param_name = sys.argv[2]
        getattr(crond, func_name)(param_name)
    else:
        func_name = sys.argv[1]
        getattr(crond, func_name)()


    # python -m crond.rank run rank_charge_top
    # python -m crond.rank run rank_make_money_top
    #  python -m crond.rank remove_daily_task