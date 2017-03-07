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
from datetime import datetime,timedelta
from datetime import date as dt_date
from datetime import time as dt_time

from proto.access_pb2 import *
from proto.constant_pb2 import *
from proto.game_pb2 import *
from proto.chat_pb2 import *
from proto import struct_pb2 as pb2

from goldflower.game import *
from goldflower.gameconf import *

from message.base import *
from message.resultdef import *

from util.commonutil import *

from db.connect import *
from db.user import *
from db.account_book import *
from db.robot import *

from helper import dbhelper

from strategy import *

from dal.core import *

ROBOT_JIJIN = 1
ROBOT_PINGHENG = 2
ROBOT_BAOSHOU = 3

CHAT_WAIT_TOO_LONG = 1

EMOTION_WAIT_TOO_LONG = {
    2:17,
    3:5,
    4:2,
    5:5,
    6:6,
    7:7,
}

RESPONSE_CHAT = {
    1:1,
    2:5,
    3:8,
    4:16,
    5:16,
}

LOST_5_GAMES = {
    90:(-1,0),
    5:(1,22),
    5:(2,10),  # 今天可真是够背的
}

WIN_3_GAMES = {
    80:(-1,0),
    10:(1,4),
    10:(2,11), # 今天可赚大发了，哈哈”
}

LOST_GAME =  {
    90:(-1,0),
    5:(1,4),
    5:(1,8),
}

WIN_GAME = {
    94:(-1,0),
    2:(1,14),
    2:(1,15),
    2:(1,16),
}

CHAT_SHOW_HAND = {
    40:(-1,0),
    20:(1,12),
    20:(1,20),
    20:(1,21),
}

CHIPS = [500,1000,2000,3000,5000,10000,20000,30000,50000,100000,150000,250000,500000]


class BetStrategy:
    def __init__(self,robot):
        self.robot = robot

    def get_pokers_level(self,pokers):
        if pokers.poker_type == P_BAOZI:
            return 0
        elif pokers.poker_type == P_TONGHUASHUN and pokers.get_dan_value() >= 10:
            return 1
        elif pokers.poker_type == P_TONGHUASHUN and pokers.get_dan_value() < 10:
            return 2
        elif pokers.poker_type == P_TONGHUA and pokers.get_dan_value() >= 10:
            return 3
        elif pokers.poker_type == P_TONGHUA and pokers.get_dan_value() < 10:
            return 4
        elif pokers.poker_type == P_SHUN and pokers.get_dan_value() >= 10:
            return 5
        elif pokers.poker_type == P_SHUN and pokers.get_dan_value() < 10:
            return 6
        elif pokers.poker_type == P_DUI and pokers.get_dui_value() >= 10:
            return 7
        elif pokers.poker_type == P_DUI and pokers.get_dui_value() < 10:
            return 8
        elif pokers.poker_type == P_DAN and pokers.get_dui_value() >= 11:
            return 9
        else:
            return 10

    def get_see_bet_strategy(self):
        robot = self.robot
        level = self.get_pokers_level(robot.my_pokers)

        if robot.type == ROBOT_BAOSHOU:
            strategy = STRATEGY_BAOSHOU[MAP_BAOSHOU[level]]
        elif robot.type == ROBOT_PINGHENG:
            strategy = STRATEGY_PINGHENG[MAP_PINGHENG[level]]
        elif robot.type == ROBOT_JIJIN:
            strategy = STRATEGY_JIJIN[MAP_JIJIN[level]]

        rate_accept_show_hand = strategy[5](robot,robot.round)
        rate_show_hand = strategy[4](robot,robot.round)
        rate_giveup = strategy[3](robot,robot.round)
        rate_compare = strategy[2](robot,robot.round)
        rate_add = strategy[1](robot,robot.round)
        rate_follow = strategy[0](robot,robot.round)

        return rate_accept_show_hand,rate_show_hand,rate_giveup,rate_compare,rate_add,rate_follow


    def do_bet_action(self):
        robot = self.robot

        rate_accept_show_hand = 0
        rate_show_hand = 0
        rate_giveup = 0
        rate_compare = 0
        rate_add = 0

        if robot.is_see:
            if robot.type == ROBOT_BAOSHOU:
                rate_accept_show_hand   = 70 + 30 * robot.x + 30 * robot.b * ( 1 - robot.x)
                rate_show_hand          = 1 * (robot.x + robot.b) + robot.round - 1
                rate_compare            = 7 * (robot.round - robot.b)+ 10 * (robot.k - 0.5 * robot.x) * robot.round
                rate_add                = 12 - robot.k * 9
                rate_follow             = 90 - 7 *(robot.round - robot.b) - 10 * (robot.k - 0.5 * robot.x) * robot.round + 9 * robot.k

            elif robot.type == ROBOT_PINGHENG:
                rate_accept_show_hand   = 75 + 25 * robot.x + 25 * robot.b * ( 1 - robot.x)
                rate_show_hand          = 3 * (robot.x + robot.b) + robot.round - 1
                rate_compare            = 5 * (robot.round - robot.b)+ 6 * (robot.k - 0.7 * robot.x) * robot.round
                rate_add                = 20 - robot.k * 7
                rate_follow             = 85 - 5 *(robot.round - robot.b) - 6 * (robot.k - 0.7 * robot.x) * robot.round + 7 * robot.k
            elif robot.type == ROBOT_JIJIN:
                rate_accept_show_hand   = 80 + 20 * robot.x + 20 * robot.b * ( 1 - robot.x)
                rate_show_hand          = 5 * (robot.x + robot.b) + robot.round
                rate_compare            = 3 * (robot.round - robot.b)+ 3 * (robot.k - 1 * robot.x) * robot.round
                rate_add                = 35 - robot.k * 5
                rate_follow             = 70 - 3 *(robot.round - robot.b) - 3 * (robot.k - 1 * robot.x) * robot.round + 5 * robot.k
        else:
            rate_accept_show_hand,rate_show_hand,rate_giveup,rate_compare,rate_add,rate_follow = self.get_see_bet_strategy()

        rate_accept_show_hand = int(rate_accept_show_hand)
        rate_show_hand = int(rate_show_hand)
        rate_giveup = int(rate_giveup)
        rate_compare = int(rate_compare)
        rate_add = int(rate_add)

        robot.info("选择策略 看牌=%s,接受=%d,全压=%d,放弃=%d,比=%d,加=%d,跟=%d",robot.is_see,rate_accept_show_hand,rate_show_hand, \
                                    rate_giveup,rate_compare,rate_add,rate_follow)
        if robot.is_see and random.randint(1,100) < rate_giveup:
            self.bet(GIVE_UP,0,0)
            return

        if robot.is_show_hand:
            if random.randint(1,100) < rate_accept_show_hand:
                self.bet(SHOW_HAND)
            else:
                self.bet(GIVE_UP)
        else:
            not_fails = [player for player in robot.players.values() if not player.is_fail and player.uid != robot.robot_id]
            see_players = [player for player in robot.players.values() if not player.is_fail and player.is_see and player.uid != robot.robot_id]

            if robot.is_see:
                need_gold = TABLE_GAME_CONFIG[robot.table_type][3] * 3 * 2
            else:
                need_gold = TABLE_GAME_CONFIG[robot.table_type][3] * 3

            if robot.round >= 3 and robot.gold < need_gold:
                if len(see_players) != 0:
                    self.bet(COMPARE,0,random.choice(see_players).uid)
                else:
                    self.bet(COMPARE,0,random.choice(not_fails).uid)
                return

            if len(not_fails) == 1 and random.randint(1,100) < rate_show_hand:
                self.bet(SHOW_HAND)
            else:
                if robot.round >= 3 and random.randint(1,100) < rate_compare:
                    if len(see_players) != 0:
                        self.bet(COMPARE,0,random.choice(see_players).uid)
                    else:
                        self.bet(COMPARE,0,random.choice(not_fails).uid)
                else:
                    if random.randint(1,100) > rate_add:
                        self.bet(FOLLOW)
                    else:
                        current_chip = CHIPS.index(robot.round_min_bet)
                        gold = 0
                        ch = robot.decide(40,30,20,10)
                        add = 0
                        if ch == 0:
                            add = 1
                        elif ch == 1:
                            add = 2
                        elif ch == 2:
                            add = 3
                        else:
                            add = 1

                        next_chip = current_chip + add
                        if next_chip >= len(CHIPS) or CHIPS[next_chip] > TABLE_GAME_CONFIG[robot.table_type][3]:
                            gold = TABLE_GAME_CONFIG[robot.table_type][3]
                        else:
                            gold = CHIPS[next_chip]

                        if robot.is_see:
                            self.bet(ADD,gold * 2)
                        else:
                            self.bet(ADD,gold)

    def bet(self,action,gold = 0,other = -1):
        self.robot.info("%s,金币=%d,比牌对手=%d",BetAction.Name(action),gold,other)

        req = create_client_event(BetActionReq,self.robot.robot_id)
        req.body.action = action
        req.body.table_id = self.robot.table_id
        req.body.gold = gold
        req.body.other = other
        gevent.spawn_later(self.robot.get_delay(),self.robot.service.forward_message,req.header,req.encode())


class OtherPlayer:
    def __init__(self,uid):
        self.uid = uid
        self.is_see = False
        self.is_fail = False
        self.pokers = None


class Robot:
    def __init__(self,manager,robot_id,start_time,duration):
        self.start_time = datetime.combine(datetime.today(),start_time)
        self.end_time = self.start_time + timedelta(seconds = duration)
        self.cant_play = False
        self.should_stop = False

        self.robot_id = robot_id

        self.manager = manager
        self.service = manager.service

        session = Session()
        try :
            self.row_robot_user = session.query(TUser).filter(TUser.id == robot_id).first()
            self.row_robot = session.query(TRobot).filter(TRobot.uid == robot_id).first()
        finally:
            session.close()
            session = None

        self.table_ids = []
        self.game_results = []
        self.type = self.row_robot.type

        self.bet_strategy = BetStrategy(self)

        self.reset_table()


        gevent.spawn(self.check_quit_condition)

    def reset_table(self):
        self.room_id = -1
        self.table_id = -1
        self.table_type = -1
        self.seat = -1
        self.table_players = []
        self.table = None

        self.same_table_games = 0
        self.leave_table_rate = 30

        self.reset_game()

    def reset_game(self):
        self.game = None
        self.is_game_ready = False
        self.is_game_start = False
        self.is_player_ready = False

        self.players = {}
        self.in_game = False
        self.my_pokers = None
        self.current = -1
        self.can_see = False

        self.x = 0
        self.b = 0
        self.k = 0

        self.is_see = False
        self.is_other_see = False
        self.is_show_hand = False
        self.is_fail = False
        self.round = 0
        self.round_min_bet = 0

        session = Session()
        try :
            row_user = session.query(TUser).filter(TUser.id == self.robot_id).first()
            self.gold = row_user.gold
        finally:
            session.close()
            session = None

    def should_quit(self):
        return self.end_time < datetime.now() or self.cant_play or self.should_stop

    def info(self,format,*args,**kwargs):
        if kwargs == None or len(kwargs) == 0:
            logging.info("[%d/%d]" + format,self.robot_id,self.table_id,*args)
        else:
            color = kwargs["color"]
            logging.info(color("[%d/%d]" + format),self.robot_id,self.table_id,*args)


    def get_delay(self):
        if self.row_robot.type == ROBOT_JIJIN:
            return random.randint(1,4)
        elif self.row_robot.type == ROBOT_PINGHENG:
            return random.randint(2,5)
        else:
            return random.randint(2,7)

    def set_player_ready(self):
        req = create_client_event(SetPlayerReadyReq,self.robot_id)
        req.header.route = self.room_id
        req.body.table_id = self.table_id
        req.body.is_ready = True
        self.service.forward_message(req.header,req.encode())
        self.info("开始准备游戏")

    def start(self):
        self.info("启动")
        req = create_client_event(ConnectGameServerReq)
        req.header.user = self.robot_id
        req.body.session = 12121231
        self.service.forward_message(req.header,req.encode())
        gevent.spawn_later(random.randint(1,3),self.sit_table)

    def sit_table(self):
        if self.should_quit():
            self.info("准备离开，不再进桌子")
            return
        self.reset_table()
        self.info("试图坐下")

        req = create_client_event(SitTableReq)
        req.header.user = self.robot_id
        req.body.table_id = -1
        req.body.table_type = self.get_table_type()
        self.service.forward_message(req.header,req.encode())

    def handle_sit_table_resp(self,req):
        if req.header.result < 0:
            self.info("无法坐下，原因：%d",req.header.result,color=color.red)
            self.cant_play = True
            return
        if req.body.table.id == self.table_id:
            self.info("继续坐在原桌",color=color.yellow)
            if self.table.goldflower.start_time < 0:
                if not self.should_quit() and not self.is_player_ready:
                    gevent.spawn_later(self.get_delay(),self.set_player_ready)
            else:
                gevent.spawn_later(random.randint(7,10),self.wait_game_finished,20)
            return

        self.reset_table()
        self.room_id = req.body.room_id
        self.table = req.body.table
        self.table_id = self.table.id
        self.table_type = req.body.table.table_type

        self.table_ids.append(self.table_id)

        player_ids = [player_brief.uid for player_brief in req.body.table.players]

        self.info("坐下...，当前桌子的状态=%d，玩家=%s",req.body.table.goldflower.start_time,player_ids,color=color.strong)

        for brief in self.table.players:
            if brief.uid == self.robot_id:
                self.seat = brief.seat
                break

        if len(player_ids) == 5:
            self.info("坐下...，当前桌子的用户超过5人，准备退出",color=color.red)
            gevent.spawn_later(random.randint(1,6),self.change_table)
            return

        if self.table.goldflower.start_time < 0:
            if not self.should_quit():
                gevent.spawn_later(self.get_delay(),self.set_player_ready)
        else:
            gevent.spawn_later(random.randint(7,10),self.wait_game_finished,20)

    def wait_game_finished(self,rate):
        if not self.is_game_ready:
            if random.randint(0,100) < rate:
                self.info("游戏没有结束，机器人不耐烦，换桌",color=color.strong)
                self.change_table()
            else:
                gevent.spawn_later(random.randint(2,4),self.wait_game_finished,rate + 20)


    def handle_sit_player_ready_resp(self,req):
        if req.header.result in [-1,RESULT_FAILED_NO_ENOUGH_GOLD]:
            self.info("无法准备游戏，钱不足，准备充值，%d",req.header.result,color=color.red)
            gold = self.manager.recharge(self.robot_id,50000)
            if gold > 0:
                self.gold = gold
            gevent.spawn_later(random.randint(1,6),self.change_table)
            #self.cant_play = True
            #self.info("无法准备游戏，机器人准备退出，%d",req.header.result,color=color.red)
        elif req.header.result < 0:
            if req.header.result == RESULT_FAILED_ALREADY_READY:
                self.info("准备游戏失败，准备换桌，错误码%d",req.header.result,color=color.red_bg)
            else:
                self.info("准备游戏失败，准备换桌，错误码%d",req.header.result,color=color.yellow_bg)
            self.change_table()

    def handle_chat_event(self,req):
        if req.body.sender == self.robot_id:
            return
        ch = self.decide(60,8,8,8,8,8)
        if ch == 0:
            return
        if RESPONSE_CHAT.get(ch) != None:
            gevent.spawn_later(random.randint(1,3),self.send_emotion,RESPONSE_CHAT[ch])

    def handle_player_ready_event(self,req):
        if req.body.player == self.robot_id:
            self.is_player_ready = True
            gevent.spawn_later(12,self.wait_ready_too_long_1)
            self.info("自己准备好了")

    def wait_ready_too_long_1(self):
        if not self.is_game_ready:
            ch = self.decide(50,5,4,3,2,2,1,1)
            if ch == 0:
                self.info("没有开始游戏，机器人不耐烦，换桌",color=color.strong)
                self.change_table()
            elif ch >=1 and ch <= 6:
                if ch == 1:
                    self.send_chat(CHAT_WAIT_TOO_LONG)
                else:
                    self.send_emotion(EMOTION_WAIT_TOO_LONG[ch])
                gevent.spawn_later(3,self.wait_ready_too_long_2)
            else:
                gevent.spawn_later(random.randint(3,6),self.wait_ready_too_long_2)

    def wait_ready_too_long_2(self):
        if not self.is_game_ready:
            self.info("没有开始游戏，机器人实在不耐烦，换桌",color=color.strong)
            self.change_table()

    def handle_game_ready_event(self,req):
        self.is_game_ready = True

    def handle_game_cancel_event(self,req):
        self.is_game_ready = False

    def handle_game_start_event(self,event):
        self.round_min_bet = TABLE_GAME_CONFIG[self.table_type][2]

        for player_gold in event.body.player_golds:
            player = OtherPlayer(player_gold.uid)
            self.players[player.uid] = player

        pokers_str = self.manager.redis.hget("pokers" , self.table_id)
        self.info("游戏开始了,%s",str(self.players.keys()))
        pokers = json.loads(pokers_str)

        for poker_data in pokers:
            uid = poker_data["uid"]
            p1 = poker_data["p1"].split("-")
            poker1 = Poker(int(p1[0]),int(p1[1]))
            p2 = poker_data["p2"].split("-")
            poker2 = Poker(int(p2[0]),int(p2[1]))
            p3 = poker_data["p3"].split("-")
            poker3 = Poker(int(p3[0]),int(p3[1]))

            player_pokers = PlayerPokers(uid,poker1,poker2,poker3)
            if uid in self.players:
                self.players[uid].pokers = player_pokers

            if uid == self.robot_id:
                self.my_pokers = player_pokers

        self.is_game_start = True
        self.same_table_games += 1
        if self.same_table_games >= 5:
            self.leave_table_rate += 10

        self.in_game = False
        for player_gold in event.body.player_golds:
            if player_gold.uid == self.robot_id:
                self.in_game = True
                break

        if self.in_game:
            self.x = 1
            for k,player in self.players.items():
                if k == self.robot_id:
                    continue

                if player.pokers.compare(self.my_pokers) > 0:
                    self.x = 0
                    break


    def get_players_state(self):
        s = ""
        for uid,p in self.players.items():
            s += "[%d-%s-%s]" % (uid,"看" if p.is_see else "未看","败" if p.is_fail else "")
        return s

    def handle_game_over_event(self,req):
        self.info("游戏结束了")
        if self.in_game:
            if req.body.winner == self.robot_id:
                self.game_results.append(1)
            else:
                self.game_results.append(0)

            if len(self.game_results) >= 5 and sum(self.game_results[-5:]) == 0:
                self.talk_random(LOST_5_GAMES)
            elif sum(self.game_results[-3:]) == 3:
                self.talk_random(WIN_3_GAMES)
            elif self.game_results[-1] == 0:
                self.talk_random(LOST_GAME)
            elif self.game_results[-1] == 1:
                self.talk_random(WIN_GAME)

            win_gold = req.body.gold if req.body.winner == self.robot_id else 0
            for player_gold in req.body.player_golds:
                if player_gold.uid == self.robot_id:
                    win_gold -= player_gold.bet_gold
                    self.gold = player_gold.gold

            session = Session()
            session.begin()
            try :
                self.row_robot = session.query(TRobot).filter(TRobot.uid == self.robot_id).first()
                self.row_robot.win_gold += win_gold
                session.commit()
            except:
                traceback.print_exc()
                session.rollback()
            finally:
                session.close()
                session = None


        self.reset_game()
        if self.same_table_games >= 6 and sum(self.game_results[-6:]) == 0:
            self.info("连续输了6把，换桌",color=color.strong)
            self.change_table()
        elif self.same_table_games >= 5 and random.randint(1,100) < self.leave_table_rate:
            self.info("连续在一个桌上了玩了5把，换桌",color=color.strong)
            self.change_table()
        else:
            if not self.should_quit():
                gevent.spawn_later(random.randint(10,13),self.set_player_ready)

    def handle_bet_action_resp(self,resp):
        if resp.header.result == RESULT_FAILED_NO_ENOUGH_GOLD and self.current == self.robot_id:
            self.info(" 没有足够的钱，放弃",color=color.red)
            req = create_client_event(BetActionReq,self.robot_id)
            req.body.action = GIVE_UP
            req.body.table_id = self.table_id
            gevent.spawn_later(1,self.service.forward_message,req.header,req.encode())

    def handle_bet_action_event(self,event):
        if not self.in_game:
            return

        if event.body.player == self.robot_id:
            self.info(" 下注信息，用户:%d,动作：%s,金币：%d,对手：%d,赢家:%d,%s",event.body.player,BetAction.Name(event.body.action),
                  event.body.action_gold,event.body.other,event.body.compare_winner,self.get_players_state(),color=color.green)
            self.gold = event.body.gold

        player = self.players.get(event.body.player,None)
        if player == None:
            self.info("something wrong %s",self.players,color=color.red)

        if event.body.action == GIVE_UP:
            if event.body.player in self.players:
                self.players[event.body.player].is_fail = True
            if event.body.player == self.robot_id:
                self.is_fail = True
        elif event.body.action == COMPARE:
            if event.body.player == self.robot_id or event.body.other == self.robot_id:
                self.b = 0
            two = [event.body.player,event.body.other]
            two.remove(event.body.compare_winner)
            loser = two[0]

            if loser in self.players:
                self.players[loser].is_fail = True
            if loser == self.robot_id:
                self.is_fail = True

        elif event.body.action == SHOW_HAND:
            self.is_show_hand = True
            if event.body.player == self.robot_id:
                self.talk_random(CHAT_SHOW_HAND)

        elif event.body.action == SEE_POKER:
            self.players[event.body.player].is_see = True

            if event.body.player != self.robot_id:
                self.is_other_see = True
                self.k = 1
            else:
                self.is_see = True

            if event.body.player == self.robot_id and self.current == self.robot_id:
                # 看完牌后进行操作
                self.bet_strategy.do_bet_action()

        elif event.body.action == FOLLOW or event.body.action == ADD:
            if self.players[event.body.player].is_see:
                self.round_min_bet = event.body.action_gold / 2
            else:
                self.round_min_bet = event.body.action_gold


    def handle_game_turn_event(self,event):
        self.current = event.body.current
        if event.body.current != self.robot_id:
            # 首次回合后可以看牌
            self.can_see = True
            return
        self.round = event.body.round
        gevent.spawn_later(1,self.think)

    def think(self):
        if self.is_see:
            self.bet_strategy.do_bet_action()
        else:
            if not self.decide_see_poker():
                self.bet_strategy.do_bet_action()

        self.can_see = True

    def decide_see_poker(self):
        if self.is_see or not self.can_see:
            return False
        if self.type == ROBOT_BAOSHOU:
            if self.is_other_see:
                rate = 30 + (self.round + 1 - self.x) * 8 + 20 * self.b
            elif self.round_min_bet >= TABLE_GAME_CONFIG[self.table_type][3]:
                rate = 40 + (self.round + 1 - self.x) * 9 + 20 * self.b
            else:
                rate = 50 + (self.round + 1 - self.x) * 10 + 20 * self.b
        elif self.type == ROBOT_PINGHENG:
            if self.is_other_see:
                rate = 15 + (self.round + 1 - self.x) * 7 + 15 * self.b
            elif self.round_min_bet >= TABLE_GAME_CONFIG[self.table_type][3]:
                rate = 25 + (self.round + 1 - self.x) * 8 + 15 * self.b
            else:
                rate = 35 + (self.round + 1 - self.x) * 9 + 15 * self.b
        elif self.type == ROBOT_JIJIN:
            if self.is_other_see:
                rate = 10 * self.b + (self.round + 1 - self.x) * 3
            elif self.round_min_bet >= TABLE_GAME_CONFIG[self.table_type][3]:
                rate = 10 + (self.round + 1 - self.x) * 7 + 10 * self.b
            else:
                rate = 20 + (self.round + 1 - self.x) * 9 + 10 * self.b

        if rate >= 100 or random.randint(1,100) <= rate:
            self.info("选择看牌")
            req = create_client_event(BetActionReq,self.robot_id)
            req.body.action = SEE_POKER
            req.body.table_id = self.table_id
            self.service.forward_message(req.header,req.encode())
            return True
        return False

    def shutdown(self):
        req = create_client_event(QuitGameServerReq)
        req.header.user = self.robot_id
        self.service.forward_message(req.header,req.encode())

        self.manager.robots.pop(self.robot_id,None)
        self.manager.prepare_robots.pop(self.robot_id,None)

    def check_quit_condition(self):
        while True:
            if not self.is_game_start and self.should_quit():
                req = create_client_event(QuitGameServerReq)
                req.header.user = self.robot_id
                self.service.forward_message(req.header,req.encode())
                self.info("机器人退出 !!!",color=color.red)

                if self.cant_play:
                    session = Session()
                    try :
                        session.begin()
                        row_robot = session.query(TRobot).filter(TRobot.uid == self.robot_id).first()
                        row_robot.state = 2
                        session.commit()
                    except:
                        traceback.print_exc()
                        session.rollback()
                    finally:
                        session.close()
                        session = None
                break

            gevent.sleep(10)

        self.manager.robots.pop(self.robot_id,None)
        if self.cant_play or self.should_stop:
            self.manager.prepare_robots.pop(self.robot_id,None)

    def send_chat(self,message):
        data = {}
        data["type"] = 2
        data["uid"] = self.robot_id
        data["nick"] = self.row_robot_user.nick
        data["vip"] = self.row_robot_user.vip
        data["seat"] = self.seat
        data["content"] = str(message)

        req = create_client_event(SendChatReq,self.robot_id)
        req.body.table_id = self.table_id
        req.body.message = json.dumps(data)
        self.service.forward_message(req.header,req.encode())

    def send_emotion(self,emotion):
        data = {}
        data["type"] = 1
        data["uid"] = self.robot_id
        data["nick"] = self.row_robot_user.nick
        data["vip"] = self.row_robot_user.vip
        data["seat"] = self.seat
        data["content"] = str(emotion)

        req = create_client_event(SendChatReq,self.robot_id)
        req.body.table_id = self.table_id
        req.body.message = json.dumps(data)
        self.service.forward_message(req.header,req.encode())

    def talk_random(self,talks):
        ch = self.decide(*talks.keys())
        if ch >= len(talks):
            return
        talk = talks.values()[ch]
        if talk[0] < 0:
            return
        if talk[0] == 1:
            self.send_emotion(talk[1])
        elif talk[0] == 2:
            self.send_chat(talk[1])

    def get_table_type(self):
        if self.gold < 1000:
            gold = self.manager.recharge(self.robot_id,50000)
            if gold > 0:
                self.gold = gold

        if self.gold <= 200000:
            return TABLE_L
        else:
            return TABLE_M

    def change_table(self):
        self.info("换桌，原桌=%d",self.table_id,color=color.strong)

        req = create_client_event(SitTableReq,self.robot_id)
        req.body.table_id = self.table_id
        req.body.table_type = self.get_table_type()
        last_tables = self.table_ids[-3:]
        req.body.not_tables.extend(last_tables)
        self.service.forward_message(req.header,req.encode())


    def handle_table_event(self,req):
        if req.body.event_type == PLAYER_JOIN:
            if req.body.player in self.table_players:
                return
            self.table_players.append(req.body.player)
        elif req.body.event_type == PLAYER_LEAVE:
            if not req.body.player in self.table_players:
                return
            self.table_players.remove(req.body.player)

        if req.body.event_type == PLAYER_KICKED and req.body.player == self.robot_id:
            self.info("被踢出",color=color.red)
            self.reset_table()
            self.sit_table()


    def decide(self,*args):
        r = random.randint(1,100)
        total = 0
        for k,p in enumerate(args):
            total += p
            if r <= p:
                return k
        return len(args)


def timestr_to_seconds(timestr):
    hm_str = timestr.split(":")
    hour = int(hm_str[0])
    min = int(hm_str[1])
    return hour * 3600 + min * 60

def random_time(segs_str):
    segs = segs_str.split("-")
    begin = timestr_to_seconds(segs[0])
    end = timestr_to_seconds(segs[1])

    seconds = random.randint(begin,end)
    h = seconds / 3600
    m = (seconds % 3600) / 60
    s = seconds - h * 3600 - m * 60
    return dt_time(h,m,s)

def random_duraiont(segs_str):
    segs = segs_str.split("-")
    return random.randint(int(segs[0]),int(segs[1]))

def seconds_between_times(time1,time2, offset = 0):
    seconds1 = time1.hour * 3600 +time1.minute * 60 + time1.second
    seconds2 = time2.hour * 3600 +time2.minute * 60 + time2.second

    return abs(seconds1 - seconds2 - offset)

class RobotManager:
    def __init__(self,service):
        self.service = service
        if service != None:
            self.redis = service.server.redis
        else:
            self.redis = None

        self.robots = {}
        self.prepare_robots = {}
        self.redis.delete("online_robots")

        gevent.spawn(self.manage_robots_console) # 提供在线接口，可以在线进行robot的加载或者停止
        gevent.spawn(self.startup_ready_robots) # 启动符合条件的robot，每隔30秒检查一次
        gevent.spawn_later(1,self.redis.lpush,"robot_cmd","loadall") # 启动时加载所有robot

        gevent.spawn_later(10,self.reload_all_robots_everyday) # 每天3点开始重新加载更新所有robot配置
        #gevent.spawn(self.check_table)

    # just for testing
    def check_table(self):
        while True:
            user_table_map = self.redis.hgetall("room_users_210")

            keys = self.redis.keys("table_*")
            for k in keys:
                if k == "table_id":
                    continue
                users = self.redis.hgetall(k).keys()
                table_id = k[10:]

                for u in users:
                    if user_table_map.get(u) == table_id:
                        continue
                    logging.info(color.red("user[%s]/table[%s] is not correct,map=%s"),u,table_id,user_table_map.get(u))

            gevent.sleep(1)


    def reload_all_robots_everyday(self):
        loaded_date = datetime.now().date()

        while True:
            now = datetime.now()
            if now.date() != loaded_date and now.time().hour >= 3:
                loaded_date = now.date()
                gevent.spawn_later(1,self.redis.lpush,"robot_cmd","loadall")
            gevent.sleep(60)

    def manage_robots_console(self):
        while True:
            _,cmd = self.redis.brpop("robot_cmd")
            logging.info(color.strong("Command:%s"),cmd)
            if cmd == "loadall":
                self.prepare_robots = {}
                row_robots = None
                session = Session()
                try :
                    row_robots = session.query(TRobot).filter(TRobot.state == 1).all()
                except:
                    traceback.print_exc()
                finally :
                    session.close()
                    session = None

                self.prepare_robots = {}

                for row_robot in row_robots:
                    self.load_prepare_robot(row_robot)

                logging.info(color.red("=======> all robots prepared: %s"),self.prepare_robots)
            elif cmd.startswith("load"):
                robot_id = int(cmd[len("load"):])
                session = Session()
                row_robot = None
                try :
                    row_robot = session.query(TRobot).filter(TRobot.uid == robot_id).first()
                finally :
                    session.close()
                    session = None
                if row_robot == None or row_robot.state != 1:
                    logging.info(color.red("robot is not exist or wrong state"))
                    continue
                self.load_prepare_robot(row_robot)
                logging.info(color.red("done"))
            elif cmd == "stopall":
                self.prepare_robots = {}
                for _,robot in self.robots.items():
                    robot.should_stop = True
                logging.info(color.red("=======> all robots[%d] quit now"),len(self.robots))
            elif cmd.startswith("stop"):
                robot_id = int(cmd[len("stop"):])
                robot = self.robots.get(robot_id)
                if robot == None:
                    logging.info(color.red("robot is not exist"))
                    continue

                robot.should_stop = True
                logging.info(color.red("done"))
            elif cmd == "shutdownall":
                self.prepare_robots = {}
                count = len(self.robots)
                for _,robot in self.robots.items():
                    robot.shutdown()
                logging.info(color.red("=======> all robots[%d] shutdown now"),count)

            elif cmd.startswith("shutdown"):
                robot_id = int(cmd[len("shutdown"):])
                robot = self.robots.get(robot_id)
                if robot == None:
                    logging.info(color.red("robot is not exist"))
                    continue

                robot.shutdown()
                logging.info(color.red("done"))

    # 启动缓存中机器人
    def startup_ready_robots(self):
        loop_seconds = 30
        while True:
            now = datetime.now().time()
            for robot_id,start_times in self.prepare_robots.items():
                if robot_id in self.robots:
                    continue
                ready = False
                for t in start_times:
                    if t[0] <= now and seconds_between_times(t[0],now) < t[1]:
                        ready = True
                        break
                    if t[0] >= now and seconds_between_times(t[0],now , 24 * 3600) < t[1]:
                        ready = True
                        break
                if not ready:
                    continue
                robot = Robot(self,robot_id,t[0],t[1])
                robot.start()
                self.robots[robot_id] = robot
            logging.info(color.red("There are %d robots online"),len(self.robots))

            gevent.sleep(loop_seconds)

    def get_robot(self,robot_id):
        return self.robots.get(robot_id,None)

    def load_prepare_robot(self,row_robot):
        segs = row_robot.online_times.split(",")
        start_times = []
        for seg in segs:
            s = seg.split("|")
            robot_start_time = random_time(s[0])
            robot_duration = random_duraiont(s[1])
            start_times.append((robot_start_time,robot_duration,))

        start_times.sort(cmp=lambda x,y:cmp(x[0],y[0]))
        self.prepare_robots[row_robot.uid] = start_times

    def recharge(self,robot_id,gold):
        session = Session()
        try :
            session.begin()
            row_user = session.query(TUser).filter(TUser.id == robot_id).first()
            row_user.gold += gold

            dbhelper.provide_gold(session,type=0,gold=gold,uid=robot_id,mode=TCB_ROBOT_RECHARGE)

            session.commit()
            self.gold = row_user.gold
            DataAccess(self.redis).reload_user(session,robot_id)
            return row_user.gold
        except:
            traceback.print_exc()
            session.rollback()
        finally:
            session.close()
            session = None
        return -1

        
if __name__ == '__main__':
    
    pass