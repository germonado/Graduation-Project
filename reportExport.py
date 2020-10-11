import os,sys
import pymysql
import shutil

p_file = './exported_json/zigbee'
h_file = './exported_json/hub'
b_file = './exported_json/ble'

db_dir = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/'
dest_ble = './log_data/ble/'
dest_zbee = './log_data/zigbee/'


def get_file(dirpath):
    fileList = [s for s in os.listdir(dirpath) 

    if os.path.isfile(os.path.join(dirpath, s))]
    fileList.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
	
    return fileList


def csvExport(bleFiles, zbeeFiles):
    
    bleCSV = []
    zbeeCSV = []
    
    try:
        
        #1. 블루투스 export
        conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='ble', charset='utf8')
        curs = conn.cursor()
        
            
        for file in bleFiles:
            sql = 'select file_number from file_ble where file_name = (%s)'
            curs.execute(sql, (file))
            file_idx = curs.fetchone()

            if file_idx != None:
                # 해당 file_idx인 것 트랜잭션 패킷에서 select해오기
                sql = '''SELECT 'file_number', 'transaction_number', 'command', 'phone_address', 'device_address',
                        'NG', 'request time', 'response time', 'error code' UNION '''
                sql += 'select * from transaction_ble where file_number = (%s)\n'
                sql += '''INTO OUTFILE %s\n'''
                sql += '''FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' '''
                
                newName = file + '_log.csv'
                curs.execute(sql, (file_idx[0], db_dir + newName))
                bleCSV.append(newName)

                # 해당 file_idx인 것 에러 패킷에서 select해오기
                sql = '''SELECT 'file_number', 'transaction_number', 'location'  UNION '''
                sql += 'select * from ng_ble where file_number = (%s)\n'
                sql += '''INTO OUTFILE %s\n'''
                sql += '''FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' '''

                newName = file + '_ng_log.csv'
                curs.execute(sql, (file_idx[0], db_dir + newName))
                bleCSV.append(newName)



        #2. 지그비 export
        conn = pymysql.connect(host='localhost', user='root', password='wlalsl4fkd.',
                       db='zigbee', charset='utf8')
        curs = conn.cursor()


        for file in zbeeFiles:
            sql = 'select file_number from file_zigbee where file_name = (%s)'
            curs.execute(sql, (file))
            file_idx = curs.fetchone()

            if file_idx != None:
                
                # 해당 file_idx인 것 트랜잭션 패킷에서 select해오기

                sql = '''SELECT 'file number', 'transaction number', 'command', 'command value', 'NG' UNION '''
                sql += 'select * from transaction_zigbee where file_number = (%s)\n'
                sql += '''INTO OUTFILE %s\n'''
                sql += '''FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' '''

                newName = file + '_log.csv'
                curs.execute(sql, (file_idx[0], db_dir + newName))
                zbeeCSV.append(newName)

                # 해당 file_idx인 것 에러 패킷에서 select해오기
                sql = '''SELECT 'file number', 'transaction number', 'location' UNION '''
                sql += 'select * from ng_zigbee where file_number = (%s)\n'
                sql += '''INTO OUTFILE %s\n'''
                sql += '''FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' '''

                newName = file + '_ng_log.csv'
                curs.execute(sql, (file_idx[0], db_dir + newName))
                zbeeCSV.append(newName)

                # 해당 file_idx인 것 패킷에서 select해오기
                sql = '''SELECT 'file number', 'transaction number', 'packet number', 'command', 'command value', 'NG', 'dest',
                        'src', 'time', 'location' UNION '''
                sql += 'select * from packet_zigbee where file_number = (%s)\n'
                sql += '''INTO OUTFILE %s\n'''
                sql += '''FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' '''

                newName = file + '_packet_log.csv'
                curs.execute(sql, (file_idx[0], db_dir + newName))
                zbeeCSV.append(newName)

    finally:
        
        conn.commit()
        conn.close()

        return bleCSV, zbeeCSV
    

def fileMove(bleList, zbeeList):
    for b in bleList:
        src = db_dir
        des = dest_ble
        shutil.move(src + b, des + b)

    for z in zbeeList:
        src = db_dir
        des = dest_zbee
        shutil.move(src + z, des + z)
        

# 모듈 사용 --------------------------------------------------

bleFiles = get_file(b_file)
zbeeFiles = get_file(p_file)

bleFiles, zbeeFiles = csvExport(bleFiles, zbeeFiles)
fileMove(bleFiles, zbeeFiles)
