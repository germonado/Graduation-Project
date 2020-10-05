# ble_json_read와 zigbee_json_read에서 만들어진 list들을 db에 로깅하는 모듈
import os,sys
import pymysql
import zigbee
import bluetooth as ble

p_file = './exported_json/zigbee'
h_file = './exported_json/hub'
b_file = './exported_json/ble'


def get_file(dirpath):
    fileList = [s for s in os.listdir(dirpath) 

    if os.path.isfile(os.path.join(dirpath, s))]
    fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	
    return fileList


def csvExport(bleFiles, zbeeFiles):
    # TODO: 트랜잭션 정보 csv, 에러 패킷 csv, 트랜잭션 내 전체(패킷 + 에러) csv
    # 블루투스, 직비 나눠서 저장
    # files 리스트에는 해당 파일 이름이 적혀 있음 -> DB로 가서 해당 파일 이름 찾고, 그 파일의 idx를 알아오기
    # 알아온 파일 idx에 해당하는 트랜잭션 패킷들 -> csv로 빼기
    # idx 가지고 에러 패킷 select -> csv로 빼기
    # idx 가지고 패킷 select + 에러 패킷 select
    # 가져온 select된 것들 사이에 에러 패킷을 중간에 끼워 넣어야 함
    # select한 패킷들 순차적으로 기록하다가 에러 패킷이랑 트랜잭션 번호 같은 곳 있으면 거기서 null로 기록된 csv로 저장

    conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='ble', charset='utf8')
    curs = conn.cursor()

    try:
        #1. 블루투스 export
        for file in bleFiles:
            sql = 'select file_number from file_ble where file_name = \'' + file + '\''
            curs.execute(sql)
            file_idx = curs.fetchone()

            if file_idx != None:
                # 해당 file_idx인 것 트랜잭션 패킷에서 select해오기
                sql = '''SELECT 'file_number', 'transaction_number', 'command', 'phone_address', 'device_address',
                        'NG', 'request time', 'response time' UNION '''
                sql += 'select * from transaction_ble where file_number = ' + str(file_idx[0]) + '\n'
                sql += 'INTO OUTFILE \'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/' + file + '.csv\'\n'
                sql += 'FIELDS TERMINATED BY \',\' LINES TERMINATED BY \'\n\''
                curs.execute(sql)
                packets = curs.fetchall()

    finally:
        conn.commit()
        conn.close()
    

def bleToDB(packetFiles):


    curs = conn.cursor()
    file_idx = 0
    
    for packet in packetFiles:

        b = ble.BluetoothCheck()
        b.write_command_extract(packet)
        transactions, cmd_statistics, NG_packets = b.write_command_succeed_check()

        sql = 'insert ignore into file_ble values (%s, %s)'
        curs.execute(sql, (file_idx, packet))

        for t in transactions:
            sql = 'insert ignore into transaction_ble values (%s, %s, %s, %s, %s, %s, %s, %s)'
            t.insert(0, file_idx)
            t = tuple(t)
            curs.execute(sql, t)

        for ng in NG_packets:
            sql = 'insert ignore into ng_ble values (%s, %s, %s)'
            ng.insert(0, file_idx)
            ng = tuple(ng)
            curs.execute(sql, ng)
        
        file_idx += 1

    


bleFiles = get_file(b_file)
zbeeFiles = get_file(p_file)
csvExport(bleFiles, zbeeFiles)
