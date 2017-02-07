# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from db.user import *
from message.resultdef import *
from config.var import *

def get_level_max(user):
    level = get_level(user)
    return BANK_LELVEL_LIMIT[level]

def get_level(user):
    # todo ...用户的等级
    user = 1
    return user

#
#
#
# def change_name(session, user, req, resp, redis):
#     # 验证条件
#     if len(req.body.nick) > 0:
#         if user.diamond < PRM_CHANGE_NAME_MINUS_DIAMOND:
#             resp.body.result.gold = user.gold
#             resp.body.result.diamond = user.diamond
#             resp.body.result.vip = user.vip
#             resp.header.result = -1
#             return False
#
#     try:
#         data = {}
#         if len(req.body.nick) > 0:
#
#             if user_ext.change_nick != -1:
#                 resp.header.result = -1
#                 return False
#             data[TUser.nick] =  req.body.nick
#             data[TUser.diamond] =  TUser.diamond - PRM_CHANGE_NAME_MINUS_DIAMOND
#             session.query(TUser).with_lockmode("update").filter(TUser.id == user.id).update(data)
#             session.query(TUserExtra).with_lockmode("update").filter(TUserExtra.uid == user.id).update({
#                 TUserExtra.change_nick : 0
#             })
#             return True
#         if len(req.body.birthday) > 0:
#             data[TUser.birthday] = req.body.birthday
#         if len(req.body.sign)  > 0:
#             data[TUser.sign] = req.body.sign
#         if len(req.body.avatar) > 0:
#             data[TUser.avatar] = req.body.avatar
#         if len(req.body.sex) > 0:
#             data[TUser.sex] = req.body.sex
#
#         session.query(TUser).with_lockmode("update").filter(TUser.id == user.id).update(data)
#
#         result = session.query(TRewardUserLog).filter(TRewardUserLog.uid == user.id).first()
#
#         if result == None:
#             # 完成任务，加入奖励记录，记录状态用户待接收
#             reward_log = TRewardUserLog()
#             reward_log.uid = user.id
#             reward_log.task_id = 1
#             reward_log.state = STATE_NO_ACCEPT_REWARD
#             reward_log.finish_date = time.strftime('%Y-%m-%d')
#             reward_log.create_time = time.strftime('%Y-%m-%d %H:%M:%S')
#             session.add(reward_log)
#
#     except Exception as e:
#         print e.message
#         resp.header.result = -1
#         return False
#     return True