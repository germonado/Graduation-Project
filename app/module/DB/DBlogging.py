# ble_json_read와 zigbee_json_read에서 만들어진 list들을 db에 로깅하는 모듈
import os,sys,json
import pymysql
from app.module.Zigbee import zigbee
from app.module.BLE import bluetooth as ble


p_file = './exported_json/zigbee'
h_file = './exported_json/hub'
b_file = './exported_json/ble'
DBINFO_JSON = './app/module/DB/dbinfo.json'

json_file = open(DBINFO_JSON, encoding="utf8")
json_read = json.load(json_file)
dbhost = json_read['host']
dbuser = json_read['user']
dbpassword = json_read['password']


def get_file(dirpath):
    fileList = [s for s in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, s))]
    fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
    print(fileList)
    return fileList


def bleToDB(packetFiles):
    conn = pymysql.connect(host=dbhost, user=dbuser, password=dbpassword,
                       db='ble', charset='utf8')

    curs = conn.cursor()
    file_idx = 0

    try:
        for packet in packetFiles:

            b = ble.BluetoothCheck()
            b.write_command_extract(packet)
            transactions, cmd_statistics, NG_packets = b.write_command_succeed_check()

            sql = 'insert ignore into file_ble values (%s, %s)'
            curs.execute(sql, (file_idx, packet))

            for t in transactions:
                sql = 'insert ignore into transaction_ble values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                t.insert(0, file_idx)
                t = tuple(t)
                curs.execute(sql, t)

            for ng in NG_packets:
                sql = 'insert ignore into ng_ble values (%s, %s, %s)'
                ng.insert(0, file_idx)
                ng = tuple(ng)
                curs.execute(sql, ng)
            
            file_idx += 1


    finally:
        conn.commit()
        conn.close()
    


def zbeeToDB(packetFiles, hubFiles):
    conn = pymysql.connect(host=dbhost, user=dbuser, password=dbpassword,
                       db='zigbee', charset='utf8')

    curs = conn.cursor()

    try:
        for file_idx in range(len(packetFiles)):
            packet = packetFiles[file_idx]
            hub = hubFiles[file_idx]

            hub_db = []
            transactions = []
            packets = []
            NG_packets = []

            zb = zigbee.ZigbeeCheck()
            hub_db, transactions, packets, NG_packets = zb.exportLogList(packet, hub)
            
            sql = 'insert ignore into file_zigbee values (%s, %s)'
            curs.execute(sql, (file_idx, packet))

            for t in transactions:
                sql = 'insert ignore into transaction_zigbee values (%s, %s, %s, %s, %s)'
                t.insert(0, file_idx)
                

                if '0x' in t[3]:
                    t[3] = int(t[3], 16)

                elif 'on' in t[3]:
                    t[3] = 1
                    
                elif 'off' in t[3]:
                    t[3] = 0

                t = tuple(t)
                curs.execute(sql, t)
                    

            for h in hub_db:
                sql = 'insert ignore into hub_zigbee values (%s, %s, %s, %s, %s, %s)'
                h.insert(0, file_idx)

                if h[4] == 'on':
                    h[4] = 1

                elif h[4] == 'off':
                    h[4] = 0
                        
                h = tuple(h)
                curs.execute(sql, h)
                    

            for p in packets:
                
                p.insert(0, file_idx)

                sql = 'select NG from transaction_zigbee where file_number = (%s) and transaction_number = (%s)'
                curs.execute(sql, (file_idx, p[1]))
                ngStr = curs.fetchone()[0]
                
                p.insert(5, ngStr)

                if '0x' in p[4]:
                    p[4] = int(p[4], 16)

                elif 'on' in p[4]:
                    p[4] = 1

                elif 'off' in p[4]:
                    p[4] = 0
                    
                else:
                    p[4] = int(p[4])
                    
                p = tuple(p)
                sql = 'insert ignore into packet_zigbee values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                curs.execute(sql, p)


            for ng in NG_packets:
                sql = 'insert ignore into ng_zigbee values (%s, %s, %s)'
                ng.insert(0, file_idx)
                    
                ng = tuple(ng)
                curs.execute(sql, ng)
            
            file_idx += 1


    finally:
        conn.commit()
        conn.close()

#bleToDB(get_file(b_file))
#zbeeToDB(get_file(p_file), get_file(h_file))
