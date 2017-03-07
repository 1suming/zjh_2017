# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import redis

from proto.constant_pb2 import *
from util.singleton import *


@singleton
class BroadCast:
    conf = {
        'host':'121.201.29.89',
        'host':'121.201.29.89',
        'host':'121.201.29.89',
        'host':'121.201.29.89',
    }
    def __init__(self):
        pass

    def push_message(self):

    @staticmethod
    def push_message(service,users,p1,p2,notifi_type = N_BROADCAST):
        pass


if __name__ == '__main__':
    b1 = BroadCast()
    b2 = BroadCast()

    b2.x = 3
    print b1.x
    print b2.x

    print id(b1)
    print id(b2)

    print b1 == b2

    b1.x = 99
    print b2.x
