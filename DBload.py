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
                        curs.execute(sql, (file))
                        file_number = curs.fetchone()[0]

                        sql = 'select * from ng_ble where file_number=(%s)'
                        curs.execute(sql, (file_number))
                        ble_ng_list = curs.fetchall()

                        sql = 'select * from transaction_ble where file_number=(%s)'
                        curs.execute(sql, (file_number))
                        ble_transaction_list = curs.fetchall()

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number, "OnOff"))
                        onoff_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number,"Dim Level"))
                        dim_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number,"Color Temp"))
                        ctmp_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"OnOff", "Success"))
                        suc_onoff = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"Dim Level", "Success"))
                        suc_dim = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"Color Temp", "Success"))
                        suc_ctmp = curs.fetchone()[0]

                        
                finally:
                        conn.close()

                ng_onoff = onoff_cmd - suc_onoff
                ng_ctmp = ctmp_cmd - suc_ctmp
                ng_dim = dim_cmd - suc_dim
                ng_total = ng_onoff+ng_ctmp+ng_dim
                suc_total = suc_ctmp+suc_dim+suc_onoff

                ble_statistics = [[onoff_cmd,suc_onoff,ng_onoff], [ctmp_cmd,suc_ctmp,ng_ctmp], [dim_cmd,suc_dim,ng_dim],
                                                ng_total, suc_total, len(ble_transaction_list)
                                                ]
                
                return ble_transaction_list, ble_statistics


        def zbee_lists_from_DB(self, file):
                
                conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='zigbee', charset='utf8')

                curs = conn.cursor()
                file_idx = 0

                try:

                        sql = 'select file_number from file_zigbee where file_name=(%s)'
                        curs.execute(sql, (file))
                        file_number = curs.fetchone()[0]

                        sql = 'select * from packet_zigbee where file_number=(%s)'
                        curs.execute(sql, (file_number))
                        zbee_packet_list = curs.fetchall()

                        sql = 'select * from ng_zigbee where file_number=(%s)'
                        curs.execute(sql, (file_number))
                        zbee_ng_list = curs.fetchall()

                        sql = 'select * from transaction_zigbee where file_number=(%s)'
                        curs.execute(sql, (file_number))
                        zbee_transaction_list = curs.fetchall()

                        sql = 'select count(*) from transaction_zbee where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number, "On/Off"))
                        onoff_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number,"level"))
                        dim_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s)'
                        curs.execute(sql, (file_number,"color"))
                        ctmp_cmd = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"OnOff", "NG"))
                        ng_onoff = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"Dim Level", "NG"))
                        ng_dim = curs.fetchone()[0]

                        sql = 'select count(*) from transaction_ble where file_number=(%s) and command=(%s) and ng=(%s)'
                        curs.execute(sql, (file_number,"Color Temp", "NG"))
                        ng_ctmp = curs.fetchone()[0]

                        suc_onoff = onoff_cmd - ng_onoff
                        suc_ctmp = ctmp_cmd - ng_ctmp
                        suc_dim = dim_cmd - ng_dim
                        ng_total = ng_onoff+ng_ctmp+ng_dim
                        suc_total = suc_ctmp+suc_dim+suc_onoff

                        zbee_statistics = [[onoff_cmd,suc_onoff,ng_onoff], [ctmp_cmd,suc_ctmp,ng_ctmp], [dim_cmd,suc_dim,ng_dim],
                                                        ng_total, suc_total, len(zbee_transaction_list)
                                                        ]

                        for i in zbee_packet_list:
                            flag = 0
                            for j in zbee_transaction_list:
                                if i[0] == j[0] && i[1] == j[1]:
                                    i.append(j[4])


                finally:
                        conn.close()
                
                        return zbee_ng_list, zbee_packet_list, zbee_statistics

db = DB_LOAD()
ble_file_list = db.ble_file_load()
db.ble_lists_from_DB(ble_file_list[0])
zbee_file_list = db.zbee_file_load()
db.zbee_lists_from_DB(zbee_file_list[0])
