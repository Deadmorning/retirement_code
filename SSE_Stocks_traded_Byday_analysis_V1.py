# -*- coding:utf-8 -*-
import datetime
from datetime import date
from chinese_calendar import is_workday,is_holiday
import akshare as ak
import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine


company_code = {'sz000063','sz000651'}

def get_ddd(company_code):
	DDD = ak.stock_zh_a_tick_tx_js(code=company_code)
	rowdata = DDD.apply(pd.to_numeric,errors= 'ignore')
	rowdata['成交时间']=pd.to_datetime(rowdata['成交时间'])
#	print(company_code)
	return rowdata


def handle_ddd(rowdata):
#	rowdata = get_ddd(company_code)
#	rowdata['成交时间']=pd.to_datetime(rowdata['成交时间'])
	rowdata.set_index('成交时间',inplace=True)
	open_price = rowdata.iat[0,0]
	closed_price = rowdata.iat[len(rowdata.index)-1,0]
	today_change_precent = round((closed_price-open_price)/open_price,4)
	today_high = rowdata['成交价'].max()
	today_low = rowdata['成交价'].min()
	day_range = round((today_high-today_low)/today_low,4)
	today_turnover = rowdata['成交额'].sum()
	today_volume = rowdata['成交量'].sum()
	turnover_500K = rowdata.loc[rowdata['成交额']>500000]
	turnover_500K_sum =turnover_500K['成交额'].sum()
	turnover_500K_ration = round(turnover_500K_sum/today_turnover,4)
	buyorder = rowdata.loc[(rowdata['性质']=='B')]
	sellorder= rowdata.loc[(rowdata['性质']=='S')]
	buyorder_turnover = buyorder['成交额'].sum()
	sellorder_sellorder = sellorder['成交额'].sum()
	net_inflows = buyorder_turnover-sellorder_sellorder

	# By 成交金额By成交金额(区分B/S)
	#	>1000
	#	>500
	#	>200
	#	>100
	#	>50
	#10.	>10Million

	buyorder_turnover_10M = buyorder.loc[buyorder['成交额']>10000000]
	buyorder_turnover_10M_sum = buyorder_turnover_10M['成交额'].sum()
	sellorder_turnover_10M = sellorder.loc[sellorder['成交额']>10000000]
	sellorder_turnover_10M_sum = sellorder_turnover_10M['成交额'].sum()
	net_inflows_10Million = buyorder_turnover_10M_sum-sellorder_turnover_10M_sum

	#	10Millin<>5Million
	buyorder_turnover_5M = buyorder.loc[(buyorder['成交额']>5000000)&(buyorder['成交额']<10000000)]
	buyorder_turnover_5M_sum = buyorder_turnover_5M['成交额'].sum()
	sellorder_turnover_5M = sellorder.loc[(sellorder['成交额']>5000000)&(sellorder['成交额']<10000000)]
	sellorder_turnover_5M_sum = sellorder_turnover_5M['成交额'].sum()
	net_inflows_5Million = buyorder_turnover_5M_sum-sellorder_turnover_5M_sum

	#	5Millin<>2Million
	buyorder_turnover_2M = buyorder.loc[(buyorder['成交额']>2000000)&(buyorder['成交额']<5000000)]
	buyorder_turnover_2M_sum = buyorder_turnover_2M['成交额'].sum()
	sellorder_turnover_2M = sellorder.loc[(sellorder['成交额']>2000000)&(sellorder['成交额']<5000000)]
	sellorder_turnover_2M_sum = sellorder_turnover_2M['成交额'].sum()
	net_inflows_2Million = buyorder_turnover_2M_sum-sellorder_turnover_2M_sum

	#	2Millin<>1Million
	buyorder_turnover_1M = buyorder.loc[(buyorder['成交额']>1000000)&(buyorder['成交额']<2000000)]
	buyorder_turnover_1M_sum = buyorder_turnover_1M['成交额'].sum()
	sellorder_turnover_1M = sellorder.loc[(sellorder['成交额']>1000000)&(sellorder['成交额']<2000000)]
	sellorder_turnover_1M_sum = sellorder_turnover_1M['成交额'].sum()
	net_inflows_1Million = buyorder_turnover_1M_sum-sellorder_turnover_1M_sum

	#	1Millin<>500K

	buyorder_turnover_500K = buyorder.loc[(buyorder['成交额']>500000)&(buyorder['成交额']<1000000)]
	buyorder_turnover_500K_sum = buyorder_turnover_500K['成交额'].sum()
	sellorder_turnover_500K = sellorder.loc[(sellorder['成交额']>500000)&(sellorder['成交额']<1000000)]
	sellorder_turnover_500K_sum = sellorder_turnover_500K['成交额'].sum()
	net_inflows_500K = buyorder_turnover_500K_sum-sellorder_turnover_500K_sum

	#	<500K
	buyorder_turnover_500000 = buyorder.loc[buyorder['成交额']<500000]
	buyorder_turnover_500000_sum = buyorder_turnover_500000['成交额'].sum()
	sellorder_turnover_500000 = sellorder.loc[sellorder['成交额']<500000]
	sellorder_turnover_500000_sum = sellorder_turnover_500000['成交额'].sum()
	net_inflows_1Million = buyorder_turnover_500000_sum-sellorder_turnover_500000_sum


	# By成交时间段(区分B/S)
	#	9:25~9:45
	#	9:45~10:00
	#	10:00~10:30
	#	10:30~11:30
	#	13:00~14:30
	#	14:30~15:00

	#	9:25~9:45
	buyorder_time_index_0945 = buyorder.index.indexer_between_time('09:25:00','9:44:59')
	buyorder_time_0945 = buyorder.iloc[buyorder_time_index_0945]['成交额'].sum()
	sellorder_time_index_0945 = sellorder.index.indexer_between_time('09:25:00','9:44:59')
	sellorder_time_0945 = sellorder.iloc[sellorder_time_index_0945]['成交额'].sum()

	#	9:46~10:00
	buyorder_time_index_1000 = buyorder.index.indexer_between_time('09:45:00','09:59:59')
	buyorder_time_1000 = buyorder.iloc[buyorder_time_index_1000]['成交额'].sum()
	sellorder_time_index_1000 = sellorder.index.indexer_between_time('09:45:00','09:59:59')
	sellorder_time_1000 = sellorder.iloc[sellorder_time_index_1000]['成交额'].sum()

	#	10:00~10:30
	buyorder_time_index_1030 = buyorder.index.indexer_between_time('10:00:00','10:29:59')
	buyorder_time_1030 = buyorder.iloc[buyorder_time_index_1030]['成交额'].sum()
	sellorder_time_index_1030 = sellorder.index.indexer_between_time('10:00:00','10:29:59')
	sellorder_time_1030= sellorder.iloc[sellorder_time_index_1030]['成交额'].sum()

	#	10:30~11:30
	buyorder_time_index_1130 = buyorder.index.indexer_between_time('10:30:00','11:30:59')
	buyorder_time_1130 = buyorder.iloc[buyorder_time_index_1130]['成交额'].sum()
	sellorder_time_index_1130 = sellorder.index.indexer_between_time('10:30:00','11:30:59')
	sellorder_time_1130 = sellorder.iloc[sellorder_time_index_1130]['成交额'].sum()

	#	13:00~14:30
	buyorder_time_index_1430 = buyorder.index.indexer_between_time('13:00:00','14:29:59')
	buyorder_time_1430 = buyorder.iloc[buyorder_time_index_1430]['成交额'].sum()
	sellorder_time_index_1430 = sellorder.index.indexer_between_time('13:00:00','14:29:59')
	sellorder_time_1430 = sellorder.iloc[sellorder_time_index_1430]['成交额'].sum()

	#	14:30~15:00
	buyorder_time_index_1500 = buyorder.index.indexer_between_time('14:30:00','15:00:59')
	buyorder_time_1500 = buyorder.iloc[buyorder_time_index_1500]['成交额'].sum()
	sellorder_time_index_1500 = sellorder.index.indexer_between_time('14:30:00','15:00:59')
	sellorder_time_1500 = sellorder.iloc[sellorder_time_index_1500]['成交额'].sum()


	datatime=datetime.date.today()+datetime.timedelta(days=-1)
	reviewdata_list=[datatime,open_price,closed_price,today_change_precent,today_turnover,today_volume,turnover_500K_ration,buyorder_turnover,sellorder_sellorder,net_inflows,
	buyorder_turnover_10M_sum,sellorder_turnover_10M_sum,buyorder_turnover_5M_sum,sellorder_turnover_5M_sum,buyorder_turnover_2M_sum,sellorder_turnover_2M_sum,buyorder_turnover_1M_sum,sellorder_turnover_1M_sum,buyorder_turnover_500K_sum,sellorder_turnover_500K_sum,buyorder_turnover_500000_sum,sellorder_turnover_500000_sum,
	buyorder_time_0945,sellorder_time_0945,buyorder_time_1000,sellorder_time_1000,buyorder_time_1030,sellorder_time_1030,buyorder_time_1000,sellorder_time_1000,buyorder_time_1130,sellorder_time_1130,buyorder_time_1430,sellorder_time_1430,buyorder_time_1500,sellorder_time_1500,]


	reviewdata_dic={
	'datatime':datatime,
	'open_price':open_price,
	'closed_price':closed_price,
	'today_change_precent':today_change_precent,
	'today_volume':today_volume,
	'turnover_500K_ration':turnover_500K_ration,
	'buyorder_turnover':buyorder_turnover,
	'sellorder_sellorder':sellorder_sellorder,
	'net_inflows':net_inflows,

	'buyorder_turnover_10M_sum':buyorder_turnover_10M_sum,
	'sellorder_turnover_10M_sum':sellorder_turnover_10M_sum,
	'buyorder_turnover_5M_sum':buyorder_turnover_5M_sum,
	'sellorder_turnover_5M_sum':sellorder_turnover_5M_sum,
	'buyorder_turnover_2M_sum':buyorder_turnover_2M_sum,
	'sellorder_turnover_2M_sum':sellorder_turnover_2M_sum,
	'sellorder_turnover_1M_sum':sellorder_turnover_1M_sum,
	'buyorder_turnover_500K_sum':buyorder_turnover_500K_sum,
	'sellorder_turnover_500K_sum':sellorder_turnover_500K_sum,
	'buyorder_turnover_500000_sum':buyorder_turnover_500000_sum,
	'sellorder_turnover_500000_sum':sellorder_turnover_500000_sum,

	'buyorder_time_0945':buyorder_time_0945,
	'sellorder_time_0945':sellorder_time_0945,
	'buyorder_time_1000':buyorder_time_1000,
	'sellorder_time_1000':sellorder_time_1000,
	'buyorder_time_1030':buyorder_time_1030,
	'sellorder_time_1030':sellorder_time_1030,
	'buyorder_time_1000':buyorder_time_1000,
	'sellorder_time_1000':sellorder_time_1000,
	'buyorder_time_1130':buyorder_time_1130,
	'sellorder_time_1130':sellorder_time_1130,
	'buyorder_time_1430':buyorder_time_1430,
	'sellorder_time_1430':sellorder_time_1430,
	'buyorder_time_1500':buyorder_time_1500,
	'sellorder_time_1500':sellorder_time_1500,


	}
	reviewdata=pd.DataFrame(reviewdata_dic,index=[0])

#	rowdata_datetime = DDD.apply(pd.to_numeric,errors= 'ignore')

#	rowdata_datetime['成交时间']=pd.to_datetime(rowdata_datetime['成交时间'])
#	tablename_ddd_rowdata = company_code+'_ddd_rowdata'
#	tablename_ddd_reviewdata = company_code+'_ddd_reviewdata'
	return reviewdata


'''
def save_handle_ddd(rowdata,reviewdata):

	conn = create_engine('mysql+pymysql://root:cucumber@localhost/stock_deal_detail_daily',encoding='utf-8')
	rowdata.to_sql(name=tablename_ddd_rowdata, con=conn, if_exists='append', index=False)
	reviewdata.to_sql(name=tablename_ddd_reviewdata, con=conn, if_exists='append', index=False)
'''


for x in company_code:
	tablename_ddd_reviewdata = x +'_ddd_reviewdata'
	tablename_ddd_rowdata = x+'_ddd_rowdata'
	conn = create_engine('mysql+pymysql://root:cucumber@localhost/stock_deal_detail_daily',encoding='utf-8')
	print(tablename_ddd_reviewdata)
	rowdata = get_ddd(x)
	rowdata.to_sql(name=tablename_ddd_rowdata, con=conn, if_exists='append', index=False)
	print(rowdata)
	reviewdata=handle_ddd(rowdata)
	reviewdata.to_sql(name=tablename_ddd_reviewdata, con=conn, if_exists='append', index=False)
	print(reviewdata)
 







