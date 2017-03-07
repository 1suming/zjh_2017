#coding:utf8

import json,time

from db.system_achievement import *
from db.game_achievement import *
from db.reward_user_log import *

AT_FIRST_LOGIN 		= 8
AT_BAOZI			= 18
AT_235_WIN_BAOZI	= 19

AT_EXP_CONFIG = {
	# id : exp
	36:10000,
    37:20000,
    38:40000,
    39:80000,
    40:160000,
    41:320000,
    42:640000,
    43:1280000,
    44:2560000,
    45:5120000,
}

AT_PLAY_CONFIG = {
	# id : play_games
	46 : 10,
	47 : 50,
	48 : 200,
	49 : 1000,
	50 : 3000,
	51 : 6000,
	52 : 10000,
	53 : 20000,
	54 : 35000,
	55 : 60000,									
}

AT_WIN_CONFIG = {
	# id : win_games
	56 : 5,
	57 : 25,
	58 : 100,
	59 : 500,
	60 : 1500,
	61 : 3000,
	62 : 5000,
	63 : 10000,
	64 : 17500,
    65 : 30000,
}

AT_WIN_GOLD_CONFIG = {
	# id : gold
    66 : 100000,
	67 : 500000,
	68 : 2000000,
	69 : 10000000,
	70 : 30000000,
	71 : 60000000,
	72 : 100000000,
	73 : 200000000,
	74 : 350000000,
    75 : 600000000,
}


AT_VIP_CONFIG = {
	# id : vip_level
    76 : 1,
	77 : 2,
	78 : 3,
	79 : 4,
	80 : 5,
	81 : 6,
	82 : 7,
	83 : 8,
	84 : 9,
    85 : 10,

}



ACHIEVEMENT_FINISHED = 0
ACHIEVEMENT_RECEIVED = 1
ACHIEVEMENT_NOT_FINISHED = 2

class BaseAchievement(object):
	def __init__(self,session,uid,table):
		self.session = session
		self.uid = uid
		self.table = table
		self.data = session.query(table).filter(table.uid == uid).first()
		
		if self.data is not None:
			self.achievements = json.loads(self.data.achievements)
			self.values = json.loads(self.data.values)
		else:
			self.achievements = {}
			self.values = {}
			
	def inc_value(self,name,added = 1):
		value = self.values.get(name,0)
		self.values[name] = value + added
		return value + added
		
	def get_value(self,name,default):
		value = self.values.get(name,None)
		return default if value == None else value
		
	def set_value(self,name,value):
		self.values[name] = value 
		return value		
			
	def save(self):
		if self.data == None:
			self.data = self.table()
			self.data.uid = self.uid
			self.data.achievements = json.dumps(self.achievements)
			self.data.values = json.dumps(self.values)
			self.session.add(self.data)
		else:
			self.data = self.table()
			self.data.uid = self.uid
			self.data.achievements = json.dumps(self.achievements)
			self.data.values = json.dumps(self.values)
			self.session.merge(self.data)

		# 修改记录为已完成，待领取
		for task_id,status in self.achievements.items():
			print '-------->',task_id,status
			if status == ACHIEVEMENT_FINISHED:
				log = TRewardUserLog()
				log.uid = self.uid
				log.task_id = int(task_id)
				log.state = 1 # 1= 已完成，待领取
				log.finish_date = time.strftime('%Y-%m-%d')
				self.session.merge(log)
		self.session.flush()

		# if self.data == None:
		# 	self.data = self.table()
		# 	self.data.uid = self.uid
		# 	self.data.achievements = json.dumps(self.achievements)
		# 	self.data.values = json.dumps(self.values)
		# 	self.session.add(self.data)
		# 	self.session.flush()
		# else:
		# 	self.data.achievements = json.dumps(self.achievements)
		# 	self.data.values = json.dumps(self.values)

		

	def is_achievement_finished(self,achievement_id):
		achievement_id = str(achievement_id)
		return achievement_id in self.achievements and self.achievements[achievement_id] in (ACHIEVEMENT_FINISHED,ACHIEVEMENT_RECEIVED)
		
	def is_achievement_received(self,achievement_id):
		achievement_id = str(achievement_id)
		return achievement_id in self.achievements and self.achievements[achievement_id] == ACHIEVEMENT_FINISHED
		
	def set_achievement_finished(self,achievement_id):
		achievement_id = str(achievement_id)
		self.achievements[achievement_id] = ACHIEVEMENT_FINISHED
		
	def set_achievement_received(self,achievement_id):
		achievement_id = str(achievement_id)
		self.achievements[achievement_id] = ACHIEVEMENT_RECEIVED


class SystemAchievement(BaseAchievement):
	def __init__(self,session,uid):
		super(SystemAchievement,self).__init__(session,uid,TSystemAchievement)
		
	def finish_first_login(self):
		if self.is_achievement_finished(AT_FIRST_LOGIN) is False:
			self.set_achievement_finished(AT_FIRST_LOGIN)
			self.save()
		
	def finish_upgrade_vip(self,vip):
		if vip == 0:
			return
		for at_id,vip_level in AT_VIP_CONFIG.items():
			if vip >= vip_level and not self.is_achievement_finished(at_id):
				self.set_achievement_finished(at_id)
		self.save()


class GameAchievement(SystemAchievement):
	def __init__(self,session,uid):
		super(GameAchievement,self).__init__(session,uid,TGameAchievement)

	def finish_baozi_pokers(self):
		if not self.is_achievement_finished(AT_BAOZI):
			self.set_achievement_finished(AT_BAOZI)
			self.save()
	

	def finish_235_win_baozi(self):
		if not self.is_achievement_finished(AT_235_WIN_BAOZI):
			self.set_achievement_finished(AT_235_WIN_BAOZI)
			self.save()
		
	
	def finish_play_game(self,user_gf,win_gold):
		need_update = False
		
		total_exp = user_gf.exp
		for at_id,exp in AT_EXP_CONFIG.items():
			if total_exp >= exp and not self.is_achievement_finished(at_id):
				self.set_achievement_finished(at_id)
				need_update = True
		
		total_games = user_gf.total_games
		for at_id,games in AT_PLAY_CONFIG.items():
			if total_games >= games and not self.is_achievement_finished(at_id):
				self.set_achievement_finished(at_id)
				need_update = True
		
		if win_gold > 0:
			win_games = user_gf.win_games
			for at_id,games in AT_WIN_CONFIG.items():
				if win_games >= games and not self.is_achievement_finished(at_id):
					self.set_achievement_finished(at_id)
					need_update = True
			
			total_gold = self.inc_value("gold",win_gold)
			need_update = True

			for at_id,gold in AT_WIN_GOLD_CONFIG.items():
				if total_gold >= gold and not self.is_achievement_finished(at_id):
					self.set_achievement_finished(at_id)
					need_update = True

			
		if need_update:
			self.save()

		
if __name__ == "__main__":
    import sys,os
    sys.path.append(os.path.dirname(__file__) + os.sep + '..//')


    from db.connect import *
    from db.system_achievement import *
    from db.game_achievement import *
    from db.reward_user_log import *

    session = Session()
    uid = 10020
    vip = 1
    SystemAchievement(session, uid).finish_first_login()
    SystemAchievement(session,uid).finish_upgrade_vip(vip)
	
	
	
	