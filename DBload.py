import json
import sys
import datetime
import os
import pymysql
import zigbee
import bluetooth

BLE_PATH = './exported_json/ble'
ZBEE_PATH = './exported_json/zigbee'

class DB_LOAD:
	

	def __init__(self):
		
		self.ble_filelist = []
		self.zbee_filelist = []


	def ble_file_load(self):

		dirpath = BLE_PATH
		ble_file_list = [s for s in os.listdir(dirpath)
			if os.path.isfile(os.path.join(dirpath, s))]
		ble_file_list.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
		
		return ble_file_list

	def zbee_file_load(self):

		dirpath = ZBEE_PATH
		zbee_file_list = [s for s in os.listdir(dirpath)
			if os.path.isfile(os.path.join(dirpath, s))]
		zbee_file_list.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
		
		return zbee_file_list

	def ble_lists_from_DB(self, file):
		conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='ble', charset='utf8')

    	curs = conn.cursor()
    	file_idx = 0

    	try:

    		sql = 'select file_number from file_ble where file_name=(%s)'
    		file_number = curs.execute(sql, (file))

    		sql = 'select * from ng_ble where file_number=(%d)'
    		ble_ng_list = curs.execute(sql, (file_number))

    		sql = 'select * from ng_ble where file_number=(%d)'
    		ble_transaction_list = curs.execute(sql, (file_number))

    	finally:
    		conn.close()

    	print(ble_ng_list, ble_transaction_list)

    	return ble_ng_list, ble_transaction_list