# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from config.var import *

import urllib
import urllib2
import hashlib
import json
import md5

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class SMS:
    def __init__(self):
        self.load_config()

    def load_config(self):
        self.conf = SMS_CONF
        self.conf['zc_sms']['password'] = self.password_md5()

    def get_random_code(self):
        return ''.join([str(i) for i in random.sample(range(0, 9), 4)])

    def password_md5(self):
        m1 = md5.new()
        m1.update(self.conf['zc_sms']['password'])
        return m1.hexdigest()

    def send_code(self, mobile):
        if mobile == None or mobile == '':
            return (False,'')
        code = self.get_random_code()
        self.conf['zc_sms']['mobile'] = mobile
        self.conf['zc_sms']['content'] = self.conf['tpl'].replace('@',code)+self.conf['sign']

        data = urllib.urlencode(self.conf['zc_sms'])

        request = urllib2.Request(self.conf['url'] + "?"+data)
        response = urllib2.urlopen(request)
        result = response.read()

        return (True,json.loads(result), code)
