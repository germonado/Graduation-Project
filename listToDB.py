# ble_json_read와 zigbee_json_read에서 만들어진 list들을 db에 로깅하는 모듈
import os,sys
import pymysql
import zigbee_json_read as zb
import ble_json_read as ble

p_file = './exported_json/zigbee'
h_file = './exported_json/hub'
b_file = './exported_json/ble'


def get_file(dirpath):
    fileList = [s for s in os.listdir(dirpath) 

    if os.path.isfile(os.path.join(dirpath, s))]
    fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	
    return fileList


def bleToDB(packetFiles):
    conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='ble', charset='utf8')

    curs = conn.cursor()
    file_idx = 0

    try:
        for packet in packetFiles:

            b = ble.BluetoothCheck()
            b.write_command_extract(packet)
            ble_list, cmd_statistics, ng_list = b.write_command_succeed_check()

            #TODO: DB 모델 바꾸거나 transactions, packets, NG_packets로 수정

            sql = 'insert ignore into file_ble values (%s, %s)'
            curs.execute(sql, (file_idx, packet))

            for t in ble_list:
                sql = 'insert ignore into packet_ble values (%s, %s, %s, %s, %s)'
                t.insert(0, file_idx)
                t = tuple(t)
                curs.execute(sql, t)
                    

            for p in packets:
                sql = 'insert ignore into packet_zigbee values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                p.insert(0, file_idx)
                p = tuple(p)
                curs.execute(sql, p)


            for ng in NG_packets:
                sql = 'insert ignore into ng_zigbee values (%s, %s, %s)'
                ng.insert(0, file_idx)
                ng = tuple(ng)
                curs.execute(sql, ng)

            
            conn.commit()
            file_idx += 1


    finally:
        conn.close()



def zbeeToDB(packetFiles, hubFiles):
    conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='zigbee', charset='utf8')

    curs = conn.cursor()
    print(packetFiles, hubFiles)

    try:
        for file_idx in range(len(packetFiles)):
            packet = packetFiles[file_idx]
            hub = hubFiles[file_idx]
            
            print(packet, hub)

            hub_db = []
            transactions = []
            packets = []
            NG_packets = []
            
            hub_db, transactions, packets, NG_packets = zb.exportLogList(packet, hub)

            sql = 'insert ignore into file_zigbee values (%s, %s)'
            curs.execute(sql, (file_idx, packet))

            for t in transactions:
                sql = 'insert ignore into transaction_zigbee values (%s, %s, %s, %s, %s)'
                t.insert(0, file_idx)
                print(t)

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
                sql = 'insert ignore into packet_zigbee values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                p.insert(0, file_idx)

                if '0x' in p[4]:
                    p[4] = int(p[4], 16)

                else:
                    p[4] = int(p[4])
                        
                p = tuple(p)
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


    

# 모듈 사용 --------------------------------------------------------------

#bleToDB(get_file(b_file))
zbeeToDB(get_file(p_file), get_file(h_file))
