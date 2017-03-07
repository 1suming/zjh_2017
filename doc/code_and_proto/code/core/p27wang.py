#coding:utf-8

from poker import *

class PlayerPokers(BasePlayerPokers):
    def __init__(self,pokers,key_flower):
        super(PlayerPokers,self).__init__(pokers)
        self.key_flower = key_flower
        self.set_pokers_meta()
        self.sort_pokers()

    def set_pokers_meta(self):
        for poker in self.pokers:
            if poker.flower == 0:
                self.meta["level"] = 0
            elif poker.value == 7:
                self.meta["level"] = 1
            elif poker.value == 2:
                self.meta["level"] = 2
            elif poker.flower == self.key_flower:
                self.meta["level"] = 3
            else:
                self.meta["level"] = 4

    def cmp_poker(self,x,y):
        if x.meta["level"] == y.meta["level"]:
            if x.flower == y.flower:
                if x.value == 1:
                    return -1
                elif y.value == 1:
                    return 1
                else:
                    return cmp(x.value,y.value)
            else:
                return -cmp(x.flower,y.flower)
        return cmp(x.meta["level"],y.meta["level"])

    def sort_pokers(self):
        self.pokers.sort(key=self.cmp_poker,reversed = True)

    def can_deal(self,pokers):
        pass
