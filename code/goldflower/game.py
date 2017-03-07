#coding: utf-8
import gevent
from gevent import monkey;monkey.patch_all()
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
from proto import struct_pb2 as pb2
from db.connect import *

from db.user_goldflower import *
from db.goldflower import *
from db.goldflower_gambler import *
from db.account_book import *

from util.commonutil import *

from gameconf import *
from eventsender import *

from task.dailytask import *
from task.achievementtask import *

from helper import dbhelper
from config import broadcast
            
class Chip:
    def __init__(self,uid,gold):
        self.uid = uid
        self.gold = gold

    def get_proto_struct(self,pb_chip = None):
        if pb_chip == None:
            pb_chip = pb2.Chip()
        pb_chip.uid = self.uid
        pb_chip.gold = self.gold
        return pb_chip    

class Poker:
    def __init__(self,flower,value):
        self.flower = flower
        self.value = value   

    def __eq__(self,other):
        return self.flower == other.flower and self.value == other.value         

    def __repr__(self):
        return "%d-%d" % (self.flower,self.value,)

    def get_proto_struct(self,pb_poker = None):
        if pb_poker == None:
            pb_poker = pb2.Poker()
        pb_poker.flower = self.flower
        pb_poker.value = self.value
        return pb_poker

class PlayerPokers:
    @staticmethod
    def from_pokers_str(uid,pokers_str):
        poker_strs = pokers_str.split(",")
        pokers = []
        for poker_str in poker_strs:
            fv = poker_str.split("-")
            flower = int(fv[0])
            value = int(fv[1])
            pokers.append(Poker(flower,value))

        return PlayerPokers(uid,*pokers)


    def __init__(self,uid,poker1,poker2,poker3):
        self.uid = uid
        self.pokers = []
        self.pokers.append(poker1)
        self.pokers.append(poker2)
        self.pokers.append(poker3)
        self.pokers.sort(cmp = lambda x,y: cmp(x.value,y.value),reverse=True)

        if self.is_baozi():
            self.poker_type = P_BAOZI
        elif self.is_tonghuashun():
            self.poker_type = P_TONGHUASHUN
        elif self.is_tonghua():
            self.poker_type = P_TONGHUA
        elif self.is_shun():
            self.poker_type = P_SHUN
        elif self.is_dui():
            self.poker_type = P_DUI
        elif self.is_352():
            self.poker_type = P_352    
        else:
            self.poker_type = P_DAN

        self.poker_value = self.V()

    def to_pokers_str(self):
        pokers = self.pokers
        return "%d-%d,%d-%d,%d-%d" % (pokers[0].flower,pokers[0].value,pokers[1].flower,pokers[1].value,pokers[2].flower,pokers[2].value)

    def get_dui_value(self):
        if self.poker_type == P_DUI:
            if self.pokers[0].value == self.pokers[1].value:
                return self.pokers[0].value
            elif self.pokers[0].value == self.pokers[2].value:
                return self.pokers[0].value
            else:
                return self.pokers[1].value
        return -1

    def get_dan_value(self):
        values = (self.pokers[0].value,self.pokers[1].value,self.pokers[2].value,)
        if values == (13,12,1):
            return 14

        if self.poker_type == P_TONGHUASHUN \
                or self.poker_type == P_SHUN \
                    or self.poker_type == P_TONGHUA \
                        or self.poker_type == P_DAN:
            return self.pokers[0].value
        return -1

    def __repr__(self):
        return "(%s,%s,%s)" % (str(self.pokers[0]),str(self.pokers[1]),str(self.pokers[2]),)

    def V(self):
        values = []
        for p in self.pokers:
            if p.value == 1:
                values.append(14)
            else:
                values.append(p.value)

        values.sort(reverse=True)
        values = tuple(values)

        if values == (14,3,2):
            return "030201"

        if not self.is_baozi() and self.is_dui():
            if values[0] != values[1]:
               values = (values[2],values[1],values[0],)
        return "%02d%02d%02d" % values

    def is_baozi(self):
        return self.pokers[0].value == self.pokers[1].value and self.pokers[1].value == self.pokers[2].value

    def is_tonghua(self):
        return self.pokers[0].flower == self.pokers[1].flower and self.pokers[1].flower == self.pokers[2].flower
        
    def is_shun(self):
        values = (self.pokers[0].value,self.pokers[1].value,self.pokers[2].value,)
        if values == (13,12,1):
            return True
        if values[2] - values[1] == -1 and values[1] - values[0] == -1:
            return True
        return False

    def is_tonghuashun(self):
        return self.is_tonghua() and self.is_shun()

    def is_dui(self):
        return self.pokers[0].value == self.pokers[1].value  \
                or self.pokers[1].value == self.pokers[2].value
 
    def is_dan(self):
        return self.pokers[0].value != self.pokers[1].value \
                and self.pokers[1].value != self.pokers[2].value 

    def is_352(self):
        values = (self.pokers[0].value,self.pokers[1].value,self.pokers[2].value,)
        return values == (5,3,2,)

    def compare(self,other):
        if self.poker_type == other.poker_type and self.poker_value == other.poker_value:
            return -1

        if self.poker_type == P_352 and other.poker_type == P_BAOZI:
            return 1

        if self.poker_type == P_BAOZI and other.poker_type == P_352:
            return -1   

        if self.poker_type == other.poker_type:
            return cmp(self.poker_value, other.poker_value)
        return cmp(self.poker_type, other.poker_type)

    def get_proto_struct(self,pb_pokers = None):
        if pb_pokers == None:
            pb_pokers = pb2.PlayerPokers()

        pb_pokers.uid = self.uid
        for poker in self.pokers:
            poker.get_proto_struct(pb_pokers.pokers.add())
        return pb_pokers

class Gambler:
    def __init__(self,game,player):
        self.game = game
        self.player = player
        self.seat = self.player.seat
        self.uid = player.uid
        self.is_fail = False
        self.is_seen = False
        self.is_given_up = False
        self.is_dealer = False
        self.is_show_hand = False
        self.bet_gold = 0
        self.action_gold = 0
        self.pokers = None

    def turn_timeout(self,turn_count):
        self.game.table.lock.acquire()
        try :
            if self.game.start_time > 0 and self.game.round.current_gambler.uid == self.uid \
                    and self.game.round.count == turn_count:
                print "==== Timeout GIVE UP =>",self.uid,self.game.round.count
                self.game.bet(self.player.uid,GIVE_UP,0,0)
        finally:
            self.game.table.lock.release()

    def is_advanced(self,other):
        seats = range(self.game.dealer.seat,MAX_TABLE_PLAYER)
        seats.extend(0,self.game.dealer.seat)
        for i in seats:
            if i == self.player.seat:
                return True
        return False        

    def stake(self,gold):
        if not self.player.has_gold(gold):
            return RESULT_FAILED_NO_ENOUGH_GOLD
        self.action_gold = gold
        self.bet_gold += gold
        chip = Chip(self.uid, gold)
        self.game.chips.append(chip)
        self.game.total_gold += gold
        session = get_context("session",None)
        self.player.modify_gold(session,-gold)
        
        DailyTaskManager(self.game.table.redis).bet_gold(self.uid,gold)
        
        return 0

    def has_gold(self,gold):
        return self.player.has_gold(gold)    

    def get_gold(self):
        return self.player.get_gold()

    def compare_pokers(self,other):
        p_result = self.pokers.compare(other.pokers)
        if p_result == 0:
            return -1 if self.is_advanced(other) else 1
        else:
            return p_result

    def __repr__(self):
        return " Gam:(" + str(self.player.uid) +  ":" + str(self.pokers) + ":"  +  str(self.bet_gold) \
                 + ":" + str(self.player.get_gold()) + ")"
 
    def get_proto_struct(self,pb_gambler):
        if pb_gambler == None:
            pb_gambler = pb2.Gambler()

        pb_gambler.uid = self.player.uid
        
        pb_gambler.seat = self.seat
        pb_gambler.gold = self.player.get_gold()

        pb_gambler.bet_gold = self.bet_gold
        pb_gambler.is_dealer = self.is_dealer
        pb_gambler.is_seen = self.is_seen
        pb_gambler.is_given_up = self.is_given_up
        pb_gambler.is_show_hand = self.is_show_hand
        pb_gambler.is_fail = self.is_fail

        return pb_gambler

class GameRound:
    def __init__(self,table,game):
        self.table = table
        self.game = game
        self.count = 0
        self.turn_uids = []
        self.current_gambler = None
        self.turn_start_time = 0
        self.min_gold = self.game.required_gold
        self.is_show_hand = False


    def start_game(self):
        self.current_gambler = self.next_notlose_gambler(self.game.dealer.uid)

        for gambler in self.game.gamblers.values():
            if not gambler.is_fail:
                gambler.stake(self.game.required_gold)
        self.game.sender.send_game_started()
        # 发牌动作
        gevent.sleep(3)
        self.turn_start_time = int(time.time())
        self.game.sender.send_current_turn(self.count,self.current_gambler)
        gevent.spawn_later(TURN_TIMEOUT,self.current_gambler.turn_timeout,self.count)

    def finish_turn(self,uid):
        self.turn_uids.append(self.current_gambler.uid)
        gambler = self.next_notlose_gambler(self.current_gambler.uid)
        if gambler != None  and gambler.uid in self.turn_uids:
            self.finish_round()

        if self.game.check_result():
            return

        self.current_gambler = self.next_notlose_gambler(self.current_gambler.uid)
        self.turn_start_time = int(time.time())
        self.game.sender.send_current_turn(self.count,self.current_gambler)
        gevent.spawn_later(TURN_TIMEOUT,self.current_gambler.turn_timeout,self.count)

    def finish_round(self):
        self.count += 1
        self.turn_uids = []

    def current_turn_no(self):
        return len(self.turn_uids)    

    def next_notlose_gambler(self,uid):
        next_gambler = None
        tmp_uid = uid
        while next_gambler == None:
            g = self.next_gambler(tmp_uid)
            if g.uid == uid :
                break
            if not g.is_fail:
                return g
            tmp_uid = g.uid
        return next_gambler

    def next_gambler(self,uid):
        gambler = self.game.gamblers[uid]

        first_gambler = min(self.game.gamblers.values(),key = lambda x:x.seat)
        next_gamblers = filter(lambda x: x.seat > gambler.seat,self.game.gamblers.values())
        if len(next_gamblers) == 0:
            return first_gambler
        else:
            return min(next_gamblers,key = lambda x:x.seat)

    def get_proto_struct(self,pb_round = None):
        if pb_round == None:
            pb_round = pb2.GameRound()

        pb_round.round = self.count
        if self.current_gambler != None:
            pb_round.current_gambler = self.current_gambler.uid
        else:
            pb_round.current_gambler = -1
        pb_round.turn_start_time = self.turn_start_time

        return pb_round    


class GoldFlower:
    def __init__(self,table,required_gold,max_gold,required_round,max_round,fee_rate):
        self.required_gold = required_gold
        self.max_gold = max_gold
        self.required_round = required_round
        self.max_round = max_round
        
        self.fee_rate = fee_rate

        self.table = table

        self.gamblers = {}
        self.chips = []
        self.round = GameRound(self.table, self)
        self.total_gold = 0
        self.winner = None
        self.game_id = -1
        self.dealer = None
        self.start_time = -1

        self.sender = GameEventSender(table, self)
        self.process_started = False

    def is_started(self):
        return self.start_time > 0

    def set_ready(self,uid):
        if self.start_time > 0:
            return RESULT_FAILED_ALREADY_START

        if uid in self.gamblers:
            return RESULT_FAILED_ALREADY_READY

        player = self.table.get_player(uid)
        if player == None:
            raise Exception("player is not exist")

        if not player.has_gold(self.required_gold):
            return RESULT_FAILED_NO_ENOUGH_GOLD

        gambler = Gambler(self,player)

        self.gamblers[uid] = gambler
        self.sender.send_player_ready(uid) 

        if len(self.gamblers) >= 2 and not self.process_started:
            self.process_started = True
            gevent.spawn(self.start_game)  
        return 0

    def leave_game(self,uid):
        if self.start_time < 0:
            self.gamblers.pop(uid,None)
            return True
        else:
            gambler = self.gamblers.get(uid)
            if gambler == None:
                return
            if not gambler.is_fail:
                self.bet(uid,GIVE_UP,0,0)
        return True

    def check_result(self):
        if self.winner != None:
            return True

        if self.round.count < MAX_GAME_ROUND:
            not_fails = [x  for x in self.gamblers.values() if x.is_fail == False]
            if len(not_fails) == 1:
                self.decide_winner(not_fails[0])
            elif len(not_fails) == 2 and not_fails[0].is_show_hand and not_fails[1].is_show_hand:
                self.decide_winner()
            else:
                return False
        else:
            self.decide_winner()
       
        return True

    def decide_winner(self,winner = None):
        if winner == None:
            not_fails = [x for x in self.gamblers.values() if x.is_fail == False]
            for gambler in not_fails:
                if winner == None:
                    winner = gambler
                else:
                    if gambler.compare_pokers(winner) > 0:
                        winner = gambler

        self.winner = winner

        fee_gold = int(self.total_gold * self.fee_rate)
        win_gold = self.total_gold - fee_gold

        session = get_context("session")
        if session == None:
            session = Session()
            try :
                session.begin()
                self.save_result(session,winner,win_gold,fee_gold)
                session.commit()
            except:
                traceback.print_exc()
                session.rollback()
            finally:
                session.close()
                session = None
        else:
            self.save_result(session,winner,win_gold,fee_gold)

        self.sender.send_game_over_event(winner.uid,win_gold,fee_gold)
        self.start_time = -1
        self.gamblers = {}

        # 删除牌的信息
        self.table.redis.hdel("pokers",self.table.id)

        self.table.restart_game()

    def save_result(self,session,winner,win_gold,fee_gold):
    	# the winner will be next game dealer
    	self.table.dealer = winner.uid

        row_game = TGoldFlower()
        row_game.type = self.table.table_type
        row_game.winner = winner.uid
        row_game.countof_gamblers = len(self.gamblers)
        row_game.gold = win_gold
        row_game.fee = fee_gold
        row_game.create_time = datetime.now()

        session.add(row_game)
        session.flush()

        for gambler in self.gamblers.values():
            row_gambler = TGoldFlowerGambler()
            row_gambler.game_id = row_game.id
            row_gambler.uid = gambler.uid
            row_gambler.type = self.table.table_type
            row_gambler.bet_gold = gambler.bet_gold

            row_gambler.is_winner = 1 if row_gambler.uid == winner.uid else 0
            row_gambler.win_gold = (win_gold - gambler.bet_gold) if gambler.uid == winner.uid else -gambler.bet_gold
            row_gambler.fee_gold = fee_gold if row_gambler.is_winner == 1 else 0

            row_gambler.create_time = datetime.now()
            row_gambler.pokers = str(gambler.pokers)
            session.add(row_gambler)

            user_gf = session.query(TUserGoldFlower).filter(TUserGoldFlower.id == row_gambler.uid).first()

            if user_gf.best == None or user_gf.best.strip() == "":
                user_gf.best = gambler.pokers.to_pokers_str()
            else:
                best_pokers = PlayerPokers.from_pokers_str(user_gf,user_gf.best)
                if gambler.pokers.compare(best_pokers) > 0:
                    user_gf.best = gambler.pokers.to_pokers_str()

            user_gf.total_games += 1
            if user_gf.id == winner.uid :
                user_gf.win_games += 1
                
            if self.table.table_type == TABLE_L:
                user_gf.exp += 2 if user_gf.uid == winner.uid else 1
            elif self.table.table_type == TABLE_M:
                user_gf.exp += 4 if user_gf.uid == winner.uid else 2
            elif self.table.table_type == TABLE_H:
                user_gf.exp += 8 if user_gf.uid == winner.uid else 4
            else:
                user_gf.exp += 16 if user_gf.uid == winner.uid else 8
            
            achievement = GameAchievement(session,user_gf.id)
            achievement.finish_game(user_gf,row_gambler.win_gold)   
            if gambler.pokers.is_baozi():
                achievement.finish_baozi_pokers()
            if gambler.pokers.is_352() and gambler.uid == winner.uid:
                achievement.finish_235_win_baozi()

        dbhelper.recycle_gold(session,game_id=row_game.id,gold=fee_gold)
        winner.player.modify_gold(session,win_gold)

        DailyTaskManager(self.table.redis).finish_game(winner,[gambler.uid for gambler in self.gamblers.values()])
        broadcast.send_win_game(winner.uid,winner.nick,win_gold - winner.bet_gold)
        broadcast.send_good_pokers(winner.uid,winner.nick,winner.pokers)

    def bet(self,uid,action,gold,other):
        if action == GIVE_UP:
            result = self.bet_giveup(uid)
            if self.round.current_gambler.uid == uid:
                self.round.finish_turn(uid)
            else:  
                self.check_result()

            return result
            
        if self.round.current_gambler.uid != uid or self.round.current_gambler.is_fail:
            return RESULT_FAILED_INVALID_TURN

        result = False
        if action == FOLLOW:
            result = self.bet_follow(uid)
        elif action == ADD:
            result = self.bet_add(uid,gold)
        elif action == SHOW_HAND:
            result = self.bet_show_hand(uid)
        elif action == COMPARE:
            result = self.bet_compare(uid,other)
        
        if result < 0:
            return result
        if action == COMPARE or action == SHOW_HAND:
            gevent.spawn_later(DELAY_FOR_COMPARE,self.round.finish_turn,uid)
        else:
            self.round.finish_turn(uid)
        return result

    def bet_follow(self,uid):
        if self.round.is_show_hand:
            return RESULT_FAILED_SHOW_HAND
        need_gold = 2 * self.round.min_gold if self.round.current_gambler.is_seen else self.round.min_gold
        current_gambler = self.round.current_gambler
        result = current_gambler.stake(need_gold)
        if result < 0:
            return result

        self.sender.send_bet_follow(current_gambler,uid,need_gold)
        return 0

    def bet_add(self,uid,gold):
        if self.round.is_show_hand:
            return RESULT_FAILED_SHOW_HAND
        need_gold = 2 * self.round.min_gold if self.round.current_gambler.is_seen else self.round.min_gold
        max_gold = 2 * self.max_gold if self.round.current_gambler.is_seen else self.max_gold

        if gold < need_gold or gold > max_gold:
            return RESULT_FAILED_INVALID_GOLD
        current_gambler = self.round.current_gambler
        result = current_gambler.stake(gold)
        if result < 0:
            return result
        self.round.min_gold = gold / 2 if self.round.current_gambler.is_seen else gold
        self.sender.send_bet_add(current_gambler,uid,gold)
        return 0

    def bet_compare(self,uid,other):
        if self.round.count < MIN_GAME_COMPARE_ROUND:
            return RESULT_FAILED_INVALID_ROUND

        if self.round.is_show_hand:
            return RESULT_FAILED_SHOW_HAND

        other_gambler = self.gamblers.get(other)
        if other_gambler.is_fail:
            return RESULT_FAILED_INVALID_GAMBLER

        current_gambler = self.round.current_gambler
        need_gold = 4 * self.round.min_gold if current_gambler.is_seen else 2 * self.round.min_gold

        result = current_gambler.stake(need_gold)
        if result < 0:
            return result

        winner = -1
        if current_gambler.compare_pokers(other_gambler) > 0:
            other_gambler.is_fail = True
            winner = current_gambler.uid
        else:
            current_gambler.is_fail = True
            winner = other_gambler.uid

        self.sender.send_bet_compare(current_gambler,uid,other,need_gold,winner)
        return 0

    def bet_giveup(self,uid):
        gambler = self.gamblers.get(uid)
        if gambler == None:
            raise Exception("it should not happen")

        if gambler.is_fail:
            return RESULT_FAILED_INVALID_GAMBLER

        not_fails = [x  for x in self.gamblers.values() if not x.is_fail]
        if len(not_fails) == 1:
            return RESULT_FAILED_MORE_GAMBLERS
	
        gambler.is_fail = True
        gambler.is_given_up = True
        self.sender.send_bet_give_up(uid)
        return 0

    def bet_show_hand(self,uid):
        not_fails = [x  for x in self.gamblers.values() if not x.is_fail and x.uid != self.round.current_gambler.uid]
        if len(not_fails) != 1:
            return RESULT_FAILED_MORE_GAMBLERS

        if self.round.count == MAX_GAME_ROUND - 1 and self.round.current_turn_no() != 0:
            return RESULT_FAILED_INVALID_ROUND

        current_gambler = self.round.current_gambler
        if not self.round.is_show_hand:
            other = not_fails[0]

            my_gold = current_gambler.get_gold()
            other_gold = other.get_gold() 

            if current_gambler.is_seen == other.is_seen:
                if my_gold > other_gold:
                    my_gold = other_gold
            elif self.round.current_gambler.is_seen:
                if my_gold > 2 * other_gold:
                    my_gold = 2 * other_gold
            else:
                if my_gold > other_gold / 2:
                    my_gold = other_gold / 2

            self.round.min_gold = my_gold / 2 if current_gambler.is_seen else my_gold
        else:
            my_gold = 2 * self.round.min_gold if current_gambler.is_seen else self.round.min_gold


        result = current_gambler.stake(my_gold)
        if result < 0:
            return result

        current_gambler.is_show_hand = True
        self.round.is_show_hand = True
        
        DailyTaskManager(self.table.redis).bet_show_hand(uid)
        
        self.sender.send_show_hand(current_gambler,uid,my_gold)
        return 0

    def see_poker(self,uid):
        gambler = self.gamblers.get(uid)
        if self.round.count == 0 and uid == self.round.next_notlose_gambler(self.dealer.uid).uid \
                and uid == self.round.current_gambler:
            return None

        gambler.is_seen = True 
        self.sender.send_see_poker(uid)   
        return gambler.pokers

    def deal(self):
        pokers = []
        for flower in xrange(1,5):
            for value in xrange(1,14):
                pokers.append(Poker(flower,value))

        self.player_pokers = {}
        data = []

        for uid in self.gamblers.keys():
            d = {}
            poker1 = random.choice(pokers)
            pokers.remove(poker1)
            poker2 = random.choice(pokers)
            pokers.remove(poker2)
            poker3 = random.choice(pokers)
            pokers.remove(poker3)
            self.gamblers[uid].pokers = PlayerPokers(uid,poker1, poker2, poker3)
            d["uid"] = uid
            d["p1"] = str(poker1)
            d["p2"] = str(poker2)
            d["p3"] = str(poker3)
            data.append(d)

        json_data = json.dumps(data)
        self.table.redis.hdel("pokers",self.table.id)
        self.table.redis.hset("pokers",self.table.id,json_data)

    def start_game(self):
        self.sender.send_game_ready(WAIT_SECONDS)
        
        for i in xrange(WAIT_SECONDS):
            self.table.lock.acquire()
            try :
                if len(self.gamblers) >= 3:
                    break
            finally:
                self.table.lock.release()
            gevent.sleep(1)
        
        self.table.lock.acquire()
        try :
            if len(self.gamblers) < 2:
                self.sender.send_game_cancel()
                self.process_started = False
                return
            self.start_time = int(time.time())
            if self.table.dealer > 0 and self.table.dealer in self.gamblers:
            	self.dealer = self.gamblers[self.table.dealer]
            else:
            	self.dealer = random.choice(self.gamblers.values())
            		
            self.dealer.is_dealer = True
            self.deal()
            self.round.start_game()
        finally:
            self.table.lock.release()


    def __repr__(self):
        s = "GoldFlower[" + str(self.total_gold) + ":"
        for gambler in self.gamblers.values():
            s += str(gambler) + "|"
        s += "]\n"
        return s


    def get_proto_struct(self,pb_table = None):
        if pb_table == None:
            pb_table = pb2.Table()

        pb_table.id = self.table.id

        pb_game = pb_table.goldflower
        pb_game.start_time = self.start_time
        self.round.get_proto_struct(pb_game.round)
        for gambler in self.gamblers.values():
            gambler.get_proto_struct(pb_game.gamblers.add())
        for chip in self.chips:
            chip.get_proto_struct(pb_game.chips.add())    
        pb_game.required_gold = self.required_gold
        pb_game.max_gold = self.max_gold
        pb_game.required_round = self.required_round
        pb_game.max_round = self.max_round
        return pb_table
if __name__ == '__main__':
    pass
