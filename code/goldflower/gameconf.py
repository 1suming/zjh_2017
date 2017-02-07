#coding: utf-8

from proto.constant_pb2 import *

MAX_TABLE_PLAYER = 5
MAX_GAME_ROUND = 15
MIN_GAME_COMPARE_ROUND = 3

DELAY_FOR_COMPARE = 4
TURN_TIMEOUT = 20
WAIT_SECONDS = 5

TABLE_GAME_CONFIG = {
    TABLE_L : (1000      ,-1,	200        ,3000     ,2,14,0.05),
    TABLE_M : (200000    ,-1,	5000       ,40000    ,2,14,0.05),
    TABLE_H : (5000000  ,-1,	50000      ,250000   ,2,14,0.05),
}