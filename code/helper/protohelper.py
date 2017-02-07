#coding:utf-8

from proto.constant_pb2 import *
from util.protoutil import *
from datetime import *
import time
import json

def set_player(pb,user,user_gf,gifts = None):

    copy_simple_field(pb,user,not_fields = ["birthday","best"])
    copy_simple_field(pb,user_gf)
    if user.birthday != None:
        pb.birthday = user.birthday.strftime('%Y-%m-%d')
    pb.uid = user.id

    if user_gf.best != None and user_gf.best.strip() != "":
        pks = user_gf.best.split(",")
        for pk in pks:
            pb_poker = pb.best.add()
            f,v = pk.split("-")
            pb_poker.flower = int(f)
            pb_poker.value = int(v)

    if gifts != None:
        for gift in gifts:
            pb_gift = pb.gifts.add()
            copy_simple_field(pb_gift,gift)

def set_announcement(pb,announcement):
    copy_simple_field(pb,announcement)

def set_reward(pb,reward,reward_logs):
    copy_simple_field(pb,reward, not_fields = ["is_daily","params"])
    pb.state = -1
    for item in reward_logs:
        if reward.id == item.task_id:
            pb.state = item.state
            break

def set_signs(pb, sign):
    copy_simple_field(pb,sign)

def set_shop_item(pb, shopitem, items):
    copy_simple_field(pb,shopitem,not_fields =["item_type"])
    pb.item_type = SHOP_ITEM if shopitem.type == SHOP_ITEM else SHOP_GOLD
    if items != None:
        for im in items:
            if shopitem.item_id == im.id:
                pb.item.id = im.id
                pb.item.icon = im.icon
                pb.item.name = im.name
                pb.item.count = 1
                pb.item.description = im.description
                break;

def set_trades(pb,trade,seller):
    copy_simple_field(pb,trade, not_fields = ["sell_time","buyer","buy_time"])
    pb.type = SHOP_GOLD
    pb.seller_name = seller.nick

def set_bag_item(pb,user_item, items):
    for item in items:
        if user_item.item_id == item.id:
            pb.id = item.id
            pb.name = item.name
            pb.icon = item.icon
            pb.description = item.description
            pb.count = user_item.countof
            break;

def set_bag_gift(pb,user_gift, gifts):
    for gift in gifts:
        if user_gift.gift_id == gift.id:
            pb.id = gift.id
            pb.name = gift.name
            pb.icon = gift.icon
            pb.count = user_gift.countof
            break;

def set_mail(pb,mail):
    copy_simple_field(pb,mail)

def set_gifts_str(redis,pb,gifts):
    if gifts != None:
        for gift in gifts.split(','):
            conf = redis.hget('conf_gift', gift[0])
            pb_gift = pb.gifts.add()
            if conf == None:
                continue
            conf = json.loads(conf)
            pb_gift.id = conf['id']
            pb_gift.name = conf['name']
            pb_gift.icon = conf['icon']
            pb_gift.count = int(gift[2])

def set_friend_apply(pb, friend_apply, gifts = None):
    pb.id = friend_apply.id
    pb.apply_from = friend_apply.uid1
    pb.apply_from_nick = friend_apply.uid1_nick
    pb.to = friend_apply.uid2
    pb.time = int(time.mktime(time.strptime(friend_apply.apply_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')))
    pb.message = friend_apply.message
    pb.apply_from_avatar = friend_apply.avatar
    if gifts != None:
        for gift in gifts:
            pb_gift = pb.gifts.add()
            copy_simple_field(pb_gift,gift)

def set_room_table(pb,uid,redis):
    rooms = redis.keys('room_users_*')
    for room in rooms:
        table_id = redis.hget(room,uid)
        if table_id != None:
            pb.table_id = int(table_id)
            pb.room_id = int(room[11:])
            return