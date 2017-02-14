# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import datetime

def get_datetime():
    return datetime.datetime.now()

def get_yesterday():
	today=datetime.date.today()
	oneday=datetime.timedelta(days=1)
	yesterday=today-oneday
	return yesterday

def get_last_week():
    d = datetime.datetime.now()
    dayscount = datetime.timedelta(days=d.isoweekday())
    dayto = d - dayscount
    sixdays = datetime.timedelta(days=6)
    dayfrom = dayto - sixdays
    return datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)

    #date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    # print date_from.strftime('%Y-%m-%d %H:%M:%S'),date_from.strftime('%W')
    # # print '---'.join([str(date_from), str(date_to)])
    # # return time.strftime('%W', str(date_from))
