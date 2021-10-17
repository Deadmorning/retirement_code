# -*- coding:utf-8 -*-
import schedule
import time
from chinese_calendar import is_workday,is_holiday
from datetime import date
import datetime
import os

'''
def job():
	print('sss')

#schedule.every().day.at('16:00').do(job)

schedule.every().seconds.do(job)
while True:
	schedule.run_pending()
	time.sleep(1)

# 交易日时间定义方式1：使用chinese_calendar 模块，先判定是否是周末，再判断是否是工作日；
# 因为只有非周末的工作日才交易，假日调休也不交易；
dt= datetime.date.today()+datetime.timedelta(-3)
dt_num = datetime.date.isoweekday(dt)
dt_isworkday = is_workday(dt)
if dt_num <6 and dt_isworkday:
	print(dt)
else:
	print(dt_num)
'''


def job():
	dt = datetime.date.today()+datetime.timedelta(-3)
	dt_num = datetime.date.isoweekday(dt)
	dt_isworkday = is_workday(dt)
	if dt_num <6 and dt_isworkday:
		os.system('python D:\\GitHub\\retirement\\SSE_Stocks_traded_Byday_analysis_V1.py')
		print(dt)
		print('OK')
	else:
		next
#schedule.every(5).seconds.do(job)
schedule.every().day.at('16:00').do(job)

while True:
	schedule.run_pending()
	time.sleep(1)

