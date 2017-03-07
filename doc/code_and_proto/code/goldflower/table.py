#coding: utf-8
import gevent
from gevent import monkey;monkey.patch_all()
from gevent import lock

import json
import logging
import traceback
from sqlalchemy.sql import select, update, delete, insert, and_,or_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time

from collections import Counter
from datetime import datetime
from datetime import date as dt_date
from datetime import time as dt_time

from proto.constant_pb2 import *

from message.base import *
from message.resultdef import *

from game import *
from gameconf import *
from eventsender import *

from proto import struct_pb2 as pb2
from db.connect import *

from dal.core import *

class Player:
    def __init__(self,table,uid,user,access_service,seat):
        self.table = table
        self.uid = uid
        self.user = user
        self.access_service = access_service
        self.seat = seat
        self.gold = 10000
        self.disconnected = False
        self.nick = user.nick
        self.avatar = user.avatar

    def has_gold(self,gold):
        return self.user.gold >= gold

    def get_gold(self):
        return self.user.get_gold()

    def modify_gold(self,session,gold):
        gold = self.user.modify_gold(session,gold)
        return gold 

    def leave_table(self):
        if self.disconnected:
            self.table.remove_player(self.uid)  

    def __repr__(self):
        return "Player[%d/%d]" % (self.uid,self.seat)
         
    def get_brief_proto_struct(self,pb_brief = None):
        if pb_brief == None:
            pb_brief = pb2.PlayerBrief()

        pb_brief.uid = self.uid
        pb_brief.avatar = self.user.avatar
        pb_brief.gold = self.user.gold
        pb_brief.seat = self.seat
        pb_brief.nick = self.user.nick
        pb_brief.vip = self.user.vip
        return pb_brief


class Table:
    def __init__(self,manager,table_id,type):
        self.id = table_id
        self.game = None
        self.table_type = type
        self.manager = manager
        self.players = {}
        self.restart_game()
        self.redis = manager.redis
        self.table_key = "table_" + str(manager.service.serviceId) + "_" + str(table_id)

        self.sender = TableEventSender(self)
        self.lock = lock.DummySemaphore()

    def update_player(self,uid,user,access_service):
        player = self.get_player(uid)
        player.user = user
        player.access_service = access_service
        player.disconnected = False

        self.redis.hset(self.table_key,uid,access_service)
        self.redis.hset(self.manager.room_key,uid,self.id)
        self.sender.send_player_connect(player,True)

    def player_disconnected(self,uid):
        player = self.get_player(uid)
        player.disconnected = True

        gevent.spawn_later(20,self.remove_player,uid)
        self.sender.send_player_connect(player,False)

    def add_player(self,uid,user,access_service):
        if self.is_full() or self.has_player(uid):
            return None

        used = [x.seat for x in self.players.values()]
        not_used = [x for x in xrange(MAX_TABLE_PLAYER) if x not in used]
        seat = random.choice(not_used)
        player = Player(self,uid,user,access_service,seat)
        self.players[uid] = player

        self.redis.hset(self.table_key,uid,access_service)
        self.redis.hset(self.manager.room_key,uid,self.id)
        self.sender.send_player_join(player)
        return player


    def remove_player(self,uid, is_kicked = False):
        player = self.get_player(uid)
        if player == None:
            return False

        self.players.pop(uid,None)

        if self.game != None:
            self.game.leave_game(uid)

        self.redis.hdel(self.table_key,uid)
        self.redis.hdel(self.manager.room_key,uid)
        if not is_kicked:
            self.sender.send_player_leave(player)
        return len(self.players) == 0 

    def kick_player(self,kicker,uid):
        if kicker < 0:
            kicker_player = self.get_player(kicker)
        else:
            kicker_player = None
        player = self.get_player(uid)

        self.remove_player(uid,is_kicked = True)
        self.sender.send_player_kicked(kicker_player,player)

    def has_player(self,uid):
        return uid in self.players

    def get_player(self,uid):
        return self.players.get(uid,None)

    def countof_players(self):
        return len(self.players)
    
    def is_empty(self):
        return len(self.players) == 0

    def is_full(self):
        return len(self.players) == MAX_TABLE_PLAYER
        
    
    def restart_game(self):
        #self.game = None
        config = TABLE_GAME_CONFIG[self.table_type]

        for player in self.players.values():
            gold = player.get_gold()
            if config[0] >= 0 and gold < config[0]:
                self.kick_player(-1,player.uid)
                continue
            if config[1] >= 0 and gold > config[1]:
                self.kick_player(-1,player.uid)
                continue
        self.game = GoldFlower(self,config[2],config[3],config[4],config[5],config[6])

    def notify_event(self,event):
        event_type = event.header.command
        event_data = event.encode()
        service = self.manager.service
        for player in self.players.values():
            service.send_client_event(player.access_service,player.uid,event_type,event_data)

    def notify_event_player(self,event,player):
        event_type = event.header.command
        event_data = event.encode()
        service = self.manager.service
        service.send_client_event(player.access_service,player.uid,event_type,event_data)
    
    def __repr__(self):
        s = "Table["
        for player in self.players.values():
            s += str(player) + "|"
        s += "]\n"
        s += str(self.game)
        return s

    def get_proto_struct(self,pb_table = None):
        if pb_table == None:
            pb_table = pb2.Table()

        pb_table.table_type = self.table_type

        for player in self.players.values():
            player.get_brief_proto_struct(pb_table.players.add())

        if self.game != None:
            self.game.get_proto_struct(pb_table)
        return pb_table    

class TableManager:
    def __init__(self,service):
        self.service = service
        if service != None:
            self.redis = service.server.redis
        else:
            self.redis = None

        self.tables = {}
        self.table_id = 0
        self.room_id = service.serviceId

        self.session = Session()
        self.dal = DataAccess(self.redis)

        if self.redis != None:
            self.room_key = "room_users_" + str(self.room_id)
            self.redis.delete(self.room_key)
            self.redis.hset(self.room_key,"info","")

            keys = self.redis.keys("table_" + str(service.serviceId) + "*")
            for k in keys:
                self.redis.delete(k)
        self.lock = lock.DummySemaphore()


    def get_table(self,table_id):
        return self.tables.get(table_id)

    def new_table(self,table_type):
        table_id = self.redis.incr("table_id")
        table = Table(self, table_id, table_type)
        self.tables[table_id] = table
        return table

    def get_player_table(self,uid):
        for table in self.tables.values():
            if table.has_player(uid):
                return table    
        return None

    def get_players_by_access_services(self,access_services):
        players = []
        for table in self.tables.values():
            for player in table.players.values():
                if player.access_service in access_services:
                    players.append(player)
        return players

    def check_table_type(table_type,gold):
        config = TABLE_GAME_CONFIG[table_type]
        if config[0] >= 0 and gold < config[0]:
            return RESULT_FAILED_LESS_GOLD
        if config[1] >= 0 and gold > config[1]:
            return RESULT_FAILED_MORE_GOLD
        return 0    
           
    def find_suitable_table_type(gold):
        for k,v in TABLE_GAME_CONFIG.items():
            if v[0] >=0 and user.gold < v[0]:
                continue
            if v[1] >=0 and user.gold > v[1]:
                continue
            return k
        return -1

    def sit_table(self,target_table_id,uid,access_service,not_table_ids,table_type):
        user = self.dal.get_user(uid)
        if user == None:
            return RESULT_FAILED_INVALID_USER,None

        if table_type < 0:
            table_type = self.find_suitable_table_type(user.gold)
            if table_type < 0:
                return RESULT_FAILED_LESS_GOLD,None

        old_table = self.get_player_table(uid)
        change_table = old_table != None and old_table.id != target_table_id
        # clean old table info if change table, otherwise it means re-join table
        if old_table != None:
            if not change_table:
                old_table.lock.acquire()
                try:
                    old_table.update_player(uid,user,access_service)
                finally:
                    old_table.lock.release()
                return 0, old_table
            else:
                if len(old_table.players) == 1 and table == None:
                    table = old_table
                    return 0,table
                old_table.lock.acquire()
                try :
                    old_table.remove_player(uid)
                finally:
                    old_table.lock.release()
        
        # if player want to sit specific table,then check table info,such as countof players,table_type and so on
        if target_table_id >= 0:
            table = self.get_table(target_table_id)
            if table == None or table.is_full():
                return RESULT_FAILED_INVALID_TABLE,None
        else:
            table = None
            for t in self.tables.values():
                if old_table != None and old_table.id == t.id :
                    continue
                if t.id in not_table_ids or t.table_type != table_type:
                    continue
                if t.is_full():
                    continue
                table = t
                break

            if table == None:
                table = self.new_table(table_type)

        table.lock.acquire()
        try :
            check_result = self.check_table_type(table.table_type,gold)
            if check_result < 0:
                return check_result,None
                
            player = table.add_player(uid,user, access_service)
            if player == None:
                return RESULT_FAILED_TABLE_IS_FULL,None
        finally:
            table.lock.release()
        return 0,table
    

if __name__ == '__main__':
    
    manager = TableManager(None)

    manager.sit_table(1, 1, [], TABLE_L)
    manager.sit_table(2, 1, [], TABLE_L)
    table = manager.sit_table(3, 1, [], TABLE_L)

    print table

    table.game.set_ready(1)
    table.game.set_ready(2)
    table.game.set_ready(3)

    gevent.sleep(1)

