#coding: utf-8

from proto.constant_pb2 import *

MAX_TABLE_PLAYER = 5
MAX_GAME_ROUND = 15
MIN_GAME_COMPARE_ROUND = 3

DELAY_FOR_COMPARE = 4
TURN_TIMEOUT = 20
WAIT_SECONDS = 3

#min_gold,max_gold,min_chip,max_chip,required_round,max_round,fee_rate

TABLE_GAME_CONFIG = {
    TABLE_L : (1000     ,500000,	500        ,3000     ,2,19,0),
    TABLE_M : (200000   ,5000000,	3000       ,20000    ,2,19,0.02),
    TABLE_H : (1000000  ,10000000,	20000      ,100000   ,4,29,0.05),
    TABLE_H2: (6000000	,-1		,   100000	   ,500000	 ,4,87,0.05)
}