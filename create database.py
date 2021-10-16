# -*- coding:utf-8 -*-
import pymysql


###create database :stock_deal_detail_daily
conn = pymysql.connect(host='localhost',user='root',passwd='cucumber',charset='utf8')
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS stock_deal_detail_daily")
conn.close()