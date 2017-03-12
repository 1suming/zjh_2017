# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import time

from sqlalchemy import and_

from db.rank_charge_top import *

class ChargeTop:

    @staticmethod
    def save_rank(session, user, gold, charge_money):
        user_info = session.query(TRankChargeTop).filter(and_(TRankChargeTop.uid == user
                                                                      ,TRankChargeTop.add_date == time.strftime('%Y-%m-%d'))).first()
        if user_info is None:
            top = TRankChargeTop()
            top.uid = user
            top.gold = gold,
            top.add_date = time.strftime('%Y-%m-%d')
            top.charge_money = charge_money
            session.add(top)
        else:
            session.query(TRankChargeTop).filter(and_(TRankChargeTop.uid == user
                                                                      ,TRankChargeTop.add_date == time.strftime('%Y-%m-%d'))).update({
                TRankChargeTop.gold: TRankChargeTop.gold + gold,
                TRankChargeTop.diamond: TRankChargeTop.diamond + diamond,
            })