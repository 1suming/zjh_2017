# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import json
from config.var import *

def add_notification_queue(redis, users,p1, p2, notifi_type = N_BROADCAST):
    item = {'users':users,'param1':p1,'param2':p2,'notifi_type':notifi_type}
    redis.lpush('notification_queue', json.dumps(item))

def add_friend_queue(redis,to_user):
    redis.hincrby('friend_queue', to_user)

def del_friend_queue(redis,to_user):
    redis.hincrby('friend_queue',to_user, -1)