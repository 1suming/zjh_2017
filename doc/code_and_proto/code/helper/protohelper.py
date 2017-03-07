#coding:utf-8

from proto.constant_pb2 import *
from util.protoutil import *
from datetime import *

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