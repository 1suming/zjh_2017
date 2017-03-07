# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import hashlib


# 32位md5加密
def md5_encry(md5_str):
    m2 = hashlib.md5()
    m2.update(md5_str)
    print m2.hexdigest()