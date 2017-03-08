# -*- coding: utf-8 -*-
__author__ = 'Administrator'


VIP_CONF = [
    {'id':0,'level':0,'friend_max':5, 'charge':0,'sign_reward':0,'kick_card':'2-0','horn_card':'1-1','relief_time':2,'relief_good':10000, 'bank_max':0,'nick_color':'white','auth':[]},
    {'id':76,'level':1,'friend_max':10, 'charge':20,'sign_reward':0.5,'kick_card':'2-0','horn_card':'1-2','relief_time':3,'relief_good':10000, 'bank_max':500000,'nick_color':'green','auth':['handle_trade_buy']},
    {'id':77,'level':2,'friend_max':20, 'charge':60,'sign_reward':1,'kick_card':'2-0','horn_card':'1-3','relief_time':4,'relief_good':10000, 'bank_max':2000000,'nick_color':'green','auth':['handle_trade_buy','handle_sell_gold']},
    {'id':78,'level':3,'friend_max':30, 'charge':100,'sign_reward':2,'kick_card':'2-3','horn_card':'1-5','relief_time':4,'relief_good':10000, 'bank_max':5000000,'nick_color':'blue','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
    {'id':79,'level':4,'friend_max':40, 'charge':200,'sign_reward':3,'kick_card':'2-4','horn_card':'1-10','relief_time':5,'relief_good':10000, 'bank_max':20000000,'nick_color':'blue','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
    {'id':80,'level':5,'friend_max':50, 'charge':500,'sign_reward':4,'kick_card':'2-5','horn_card':'1-15','relief_time':5,'relief_good':10000, 'bank_max':50000000,'nick_color':'yellow','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold']},
    {'id':81,'level':6,'friend_max':60, 'charge':1000,'sign_reward':5,'kick_card':'2-6','horn_card':'1-20','relief_time':6,'relief_good':10000, 'bank_max':100000000,'nick_color':'yellow','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
    {'id':82,'level':7,'friend_max':70, 'charge':2000,'sign_reward':6,'kick_card':'2-7','horn_card':'1-25','relief_time':6,'relief_good':10000, 'bank_max':200000000,'nick_color':'red','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
    {'id':83,'level':8,'friend_max':80, 'charge':5000,'sign_reward':7,'kick_card':'2-8','horn_card':'1-30','relief_time':8,'relief_good':10000, 'bank_max':500000000,'nick_color':'red','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
    {'id':84,'level':9,'friend_max':90, 'charge':10000,'sign_reward':8,'kick_card':'2-9','horn_card':'1-35','relief_time':8,'relief_good':10000, 'bank_max':1000000000,'nick_color':'purple','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
    {'id':85,'level':10,'friend_max':100, 'charge':20000,'sign_reward':9,'kick_card':'2-10','horn_card':'1-40','relief_time':10,'relief_good':10000, 'bank_max':2000000000,'nick_color':'purple','auth':['handle_kick_other','handle_trade_buy','handle_sell_gold''handle_trade_buy','handle_sell_gold','no_kick']},
]

VIP_CHARGE_MAP = [(0,0),(20,1),(60,2),(100,3),(200,4),(500,5),(1000,6),(2000,7),(5000,8),(10000,9),(20000,10)]
