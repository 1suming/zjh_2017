#coding: utf-8

import json
import logging
import traceback
import socket
import gevent
import binascii
from ctypes import *

import random,time
from datetime import datetime
from datetime import date as dt_date
from datetime import time as dt_time


from services import GameService
from message.base import *
from message.resultdef import *

from proto.constant_pb2 import *
from proto.access_pb2 import *
from proto.game_pb2 import *

from db.connect import *

from util.handlerutil import *
from util.commonutil import *

from table import *
from game import *
from dal.core import *


class GoldFlowerService(GameService):
    def setup_route(self):
        self.registe_command(LeaveTableReq,LeaveTableResp,self.handle_leave_table)

        self.registe_command(SetPlayerReadyReq,SetPlayerReadyResp,self.handle_set_player_ready)
        self.registe_command(BetActionReq,BetActionResp,self.handle_bet_action)
    
    def init(self):
        self.registe_handler(SitTableReq,SitTableResp,self.handle_sit_table)
        self.registe_handler(LeaveTableInternalReq,LeaveTableInternalResp,self.handle_leave_table_internal)

        self.room_id = self.serviceId
        self.table_manager = TableManager(self)
        self.redis = self.server.redis

        keys = self.redis.keys("u1*")
        for k in keys:
            self.redis.delete(k)


    def get_table(self,user):
        return self.table_manager.get_player_table(user)


    @USE_TRANSACTION
    def handle_sit_table(self,session,req,resp,event):
        table = None
        self.table_manager.lock.acquire()
        try :
            result,table = self.table_manager.sit_table(req.body.table_id > 0, \
                    req.header.user,event.srcId, req.body.not_tables, req.body.table_type)
            if result < 0:
                resp.header.result = result
                return
            table.get_proto_struct(resp.body.table)
            resp.body.room_id = self.room_id
            resp.header.result = 0
        finally :
            self.table_manager.lock.release()


    @USE_TRANSACTION
    def handle_leave_table(self,session,req,resp,event):
        table = self.get_table(req.header.user)
        if table == None:
            resp.header.result = RESULT_FAILED_INVALID_TABLE
            return

        table.lock.acquire()
        try:
            table.remove_player(req.header.user)
            resp.header.result = 0
        finally:
            table.lock.release()



    @USE_TRANSACTION
    def handle_leave_table_internal(self,session,req,resp,event):
        table = self.get_table(req.header.user)
        if table == None:
            resp.header.result = RESULT_FAILED_INVALID_TABLE
            return False

        table.lock.acquire()
        try:
            table.remove_player(req.header.user)
        finally:
            table.lock.release()
        return False

    @USE_TRANSACTION
    def handle_set_player_ready(self,session,req,resp,event):
        table = self.get_table(req.header.user)
        if table == None:
            resp.header.result = RESULT_FAILED_INVALID_TABLE
            return False

        table.lock.acquire()
        try :
            result = table.game.set_ready(req.header.user)
            resp.header.result = result
        finally:
            table.lock.release()

    @USE_TRANSACTION
    def handle_bet_action(self,session,req,resp,event):
        table = self.get_table(req.header.user)
        if table == None:
            resp.header.result = RESULT_FAILED_INVALID_TABLE
            return False

        table.lock.acquire()
        try :
            game = table.game
            uid = req.header.user
            if game.start_time <= 0:
                resp.header.result = RESULT_FAILED_NOT_START
                return

            if req.body.action == SEE_POKER:
                pokers = game.see_poker(uid)
                if pokers == None:
                    resp.header.result = -1
                    return
                pokers.get_proto_struct(resp.body.pokers)
                resp.header.result = 0
            else:
                result= game.bet(req.header.user,req.body.action,req.body.gold,req.body.other)
                resp.header.result = result
        finally:
            table.lock.release()
    