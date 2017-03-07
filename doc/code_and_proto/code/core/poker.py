#coding:utf8

from proto import struct_pb2 as pb2

F_WANG          = 0
F_HEI_TAO       = 1
F_HONG_TAO      = 2
F_MEI_HUA       = 3
F_FANG_PIAN     = 4

class Poker:
    def __init__(self,flower,value):
        self.flower = flower
        self.value = value
        self.meta = {}

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

class BasePokers:
    def __init__(self,pokers):
        self.pokers = pokers

    def get_proto_struct(self,pb_pokers = None):
        if pb_pokers == None:
            pb_pokers = pb2.PlayerPokers()

        for poker in self.pokers :
            pb_poker = pb_pokers.add()
            poker.get_proto_struct(pb_poker)

        return pb_pokers

    def to_pokers_str(self):
        s = ""
        for poker in self.pokers:
            s += "%d-%d,%d-%d,%d-%d" % (poker.flower,poker.value)
        return s

    @staticmethod
    def from_pokers_str(pokers_str):
        poker_strs = pokers_str.split(",")
        pokers = []
        for poker_str in poker_strs:
            fv = poker_str.split("-")
            flower = int(fv[0])
            value = int(fv[1])
            pokers.append(Poker(flower,value))

        return BasePokers(*pokers)

