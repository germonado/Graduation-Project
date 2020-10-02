# ble_json_read와 zigbee_json_read에서 만들어진 list들을 db에 로깅하는 모듈
import os,sys
import pymysql
import zigbee_json_read as zb
import ble_json_read as ble

p_file = './exported_json/zigbee'
h_file = './exported_json/hub'
b_file = './exported_json/ble'

conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='zigbee', charset='utf8')

curs = conn.cursor()


def get_file(dirpath):
    fileList = [s for s in os.listdir(dirpath) 

    if os.path.isfile(os.path.join(dirpath, s))]
    fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	
    return fileList



#def bleToDB(packetFiles):
    


def zbeeToDB(packetFiles, hubFiles):
    file_idx = 0
    print(packetFiles, hubFiles)

    try:
        for packet, hub in zip(packetFiles, hubFiles):

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

                if t[2] == 'On/Off':
                    t[3] = int(t[3], 16)

                else:
                    t[3] = int(t[3])

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

            
            conn.commit()
            file_idx += 1


    finally:
        conn.close()


    

# main 함수 --------------------------------------------------------------

#bleToDB(get_file(b_file))
zbeeToDB(get_file(p_file), get_file(h_file))
