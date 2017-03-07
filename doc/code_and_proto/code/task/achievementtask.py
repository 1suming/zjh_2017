#coding:utf8

import json
from db.system_achievement import *
from db.game_achievement import *

AT_FIRST_LOGIN 		= 1
AT_BAOZI			= 1000
AT_235_WIN_BAOZI	= 1001

AT_EXP_CONFIG = {
	# id : exp
	36 : 40000,
	37 : 50000,
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
	56 : 10,
	57 : 50,
	58 : 200,
	59 : 1000,
	60 : 3000,
	61 : 6000,
	62 : 10000,
	63 : 20000,
	64 : 35000,
	65 : 60000,	
}

AT_WIN_GOLD_CONFIG = {
	# id : gold
}


AT_VIP_CONFIG = {
	# id : vip_level
}


ACHIEVEMENT_FINISHED = 0
ACHIEVEMENT_RECEIVED = 1
ACHIEVEMENT_NOT_FINISHED = 2

class BaseAchievement:
	def __init__(self,session,uid,table):
		self.session = session
		self.uid = uid
		self.table = table
		self.data = session.query(table).filter(table.uid == uid).first()
		if self.data == None:
			self.archievements = json.loads(data.achievements)
			self.values = json.loads(data.values)
		else:
			self.archievements = {}
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
			self.data = table()
			self.data.uid = self.uid
			self.data.archievements = json.dumps(self.achievements)
			self.data.values = json.dumps(self.values)			
			self.session.add(self.data)
		else:
			self.data.archievements = json.dumps(self.achievements)
			self.data.values = json.dumps(self.values)
		

	def is_achievement_finished(self,achievement_id):
		achievement_id = str(achievement_id)
		return achievement_id in self.archievements and self.archievements[achievement_id] in (ACHIEVEMENT_FINISHED,ACHIEVEMENT_RECEIVED)
		
	def is_achievement_received(self,achievement_id):
		achievement_id = str(achievement_id)
		return achievement_id in self.archievements and self.archievements[achievement_id] == ACHIEVEMENT_FINISHED
		
	def set_achievement_finished(self,achievement_id):
		achievement_id = str(achievement_id)
		self.archievements[achievement_id] = ACHIEVEMENT_FINISHED
		
	def set_achievement_received(self,achievement_id):
		achievement_id = str(achievement_id)
		self.archievements[achievement_id] = ACHIEVEMENT_RECEIVED


class SystemAchievement(BaseAchievement):
	def __init__(self,session,uid):
		super(SystemAchievement,self).__init__(session,uid,TSystemArchievement)
		
	def finish_first_login(self):
		if not self.is_archievement_finished(AT_FIRST_LOGIN):
			self.set_archievement_finished(AT_FIRST_LOGIN)
			self.save()
		
	def finish_upgrade_vip(self,vip):
		if vip == 0:
			return
		for at_id,vip_level in AT_VIP_CONFIG.items():
			if vip >= vip_level and not self.is_archievement_finished(at_id):
				self.set_archievement_finished(at_id)
		self.save()	

class GameAchievement:
	def __init__(self,session,uid):
		super(SystemAchievement,self).__init__(session,uid,TGameArchievement)

	def finish_baozi_pokers(self):
		if not self.is_archievement_finished(AT_BAOZI):
			self.set_archievement_finished(AT_BAOZI)
			self.save()
	

	def finish_235_win_baozi(self):
		if not self.is_archievement_finished(AT_235_WIN_BAOZI):
			self.set_archievement_finished(AT_235_WIN_BAOZI)
			self.save()
		
	
	def finish_play_game(self,user_gf,win_gold):
		need_update = False
		
		total_exp = user_gf.exp
		for at_id,exp in AT_EXP_CONFIG.items():
			if total_exp >= exp and not self.is_archievement_finished(at_id):
				self.set_archievement_finished(at_id)
				need_update = True
		
		total_games = user_gf.total_games
		for at_id,games in AT_PLAY_CONFIG.items():
			if total_games >= games and not self.is_archievement_finished(at_id):
				self.set_archievement_finished(at_id)
				need_update = True
		
		if win_gold > 0:
			win_games = user_gf.win_games
			for at_id,games in AT_WIN_CONFIG.items():
				if win_games >= games and not self.is_archievement_finished(at_id):
					self.set_archievement_finished(at_id)
					need_update = True
			
			total_gold = self.inc_value("gold",win_gold)
			need_update = True

			for at_id,gold in AT_WIN_GOLD_CONFIG.items():
				if total_gold >= gold and not self.is_archievement_finished(at_id):
					self.set_archievement_finished(at_id)
					need_update = True

			
		if need_update:
			self.save()
		
		
if __name__ == "__main__":
	VipAchievement(session,uid).finish_upgrade_vip(vip)
	
	SystemArchievement(session,uid).finish_first_login()
	
	
	