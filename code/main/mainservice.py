#coding: utf-8

import json
import logging
import traceback
import gevent

import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time
from datetime import datetime

from services import GameService
from message.base import *
from message.resultdef import *

from db.connect import *

from proto.game_pb2 import *
from proto.access_pb2 import *
from proto.constant_pb2 import *
from proto.struct_pb2 import *

from util.handlerutil import *

from config.var import *
from hall.hallobject import *
from dal.core import DataAccess


class MainService(GameService):
    def setup_route(self):
        self.registe_command(ConnectGameServerReq,ConnectGameServerResp,self.handle_connect_game_server)
        self.registe_command(QuitGameServerReq,QuitGameServerResp,self.handle_quit_game_server)
        self.registe_command(GetServerTimeReq,GetServerTimeResp,self.handle_get_server_time)
    
    def init(self):
        self.redis = self.server.redis
        self.redis.delete("online") 
    
    def notify_offline(self,session,userid):
        req = create_client_message(OfflineReq)
        req.header.user = userid
        req.body.uid = userid
        gevent.spawn_later(0.1,self.broadcast_message,req.header,req.encode())
    
    @USE_TRANSACTION
    def handle_connect_game_server(self,session,req,resp,event):
        now = int(time.time())
        self.redis.hset("online",req.header.user,event.srcId)
        resp.header.result = 0
        logging.info("====> User Connect Now: %d", req.header.user)

        da = DataAccess(self.redis)
        da.get_user(req.header.user,must_update=True)

        # 财富榜人物上线了，广播
        RankObject.gold_top_online_broadcast(self, session, req.header.user)

        return False
    
    @USE_TRANSACTION
    def handle_get_server_time(self,session,req,resp,event):        
        resp.body.server_time = int(time.time() * 1000)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_quit_game_server(self,session,req,resp,event):
        logging.info("----> User Quit Now: %d", req.header.user)
        self.redis.hdel("online",req.header.user)

        self.notify_offline(session,req.header.user)
        return False    
    
    
if __name__ == "__main__":
    pass

