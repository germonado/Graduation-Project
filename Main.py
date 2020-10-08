from flask import Flask
from flask import render_template
from flask import request as flask_request
from flask import session
from flask import send_file
from flask import send_from_directory
from flask_socketio import SocketIO
from flask_socketio import emit
from socket import *
import numpy as np
import wave
import io
import base64
import os
import threading
import time
import socket
import random
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as current_app
 
from app.module.DB import dbModule
import zigbee
import bluetooth

import DBload as DB

HOST_ADDRESS = '127.0.0.1'

HOST_PORT = 8085

# 생각해보면 사용자가 저장여부 판단하지 않을 것으로 예상하는데, db 저장은 백엔드에서 다 구현하고 알아서 필터링 해야하지 않을까
# 1. 파일 로드
# 2. 필터링 및 로그 파일 생성해서 사용자에게 보여주거나 다운가능하도록
# 3. 필터링 한 데이터는 DB로 바로 저장(로그 파일도 따로 만들고)
# 4. DB 테이블을 프로토콜 별로 만들까? 뭘 기준으로 나눠서 해야할까
# 5. 졸프 ppt 분석할 필요 있음
# 6. 남의 PC에서 local DB 쓰면 어케되는거지? MySQL 사용하면?

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
test= Blueprint('test', __name__, url_prefix='/test')

@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')

@app.route("/log_lists")
def log_lists():
    path = "./log_data/"

    return render_template('log_list.html', protocol='')


@app.route("/log_lists/ble")
def ble_log():
    path = "./log_data/ble/"
    log_file = os.listdir(path)
    
    return render_template('log_list.html', protocol='ble', bleList=log_file)
    

@app.route("/log_lists/zbee")
def zbee_log():
    path = "./log_data/zigbee"
    log_file = os.listdir(path)

    return render_template('log_list.html', protocol='zbee', zbeeList=log_file)


@app.route("/bluetooth_report")
def bluetooth_report():
   # ble = ble_json_read.BluetoothCheck()
    #ble.write_command_extract(ble.get_file())
    #ble_file_list = DB.ble_file_load()
    ble_file_list = ble.get_file()
    #print(file_list)
    
    for f in ble_file_list:
        ble.write_command_extract(f)
        ble_list, ble_statistics, t = ble.write_command_succeed_check()
        break
    
    #ble_list, ble_statistics = DB.ble_lists_from_DB(ble_file_list[0])
    return render_template('bluetooth_report.html', bleList=ble_list, staList=ble_statistics, fileList=ble_file_list)


@app.route("/zigbee_report")
def zigbee_report():
    zb = zigbee.ZigbeeCheck()
    hub, trans, packets, ng = zb.exportLogList('20200930.json', '20200930.json')
    zb.debugging()
    #ble.write_command_extract(ble.get_file())
    #ble.get_file(ble, 'onoffctonoff_error4.json')
    #ble_list, cmd_statistics = ble.write_command_succeed_check()

def zibgee_report():
    zbee_file_list = DB.zbee_file_load()

    zbee_ng_list, zbee_list = DB.zbee_lists_from_DB(zbee_file_list[0])
    return render_template('zigbee_report.html', fileList=zbee_list, staList=cmd_statistics, ngList=zbee_ng_list)


@app.route("/tables")
def tables():
    return render_template('tables.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/calendar")
def calendar():
    return render_template('calendar.html')   

@app.route("/login")
def login():
    return render_template('login.html')   

@app.route("/register")
def registration():
    return render_template('register.html')       

@app.route('/log_file_download')
def log_file_download():
    path = "./log_data/"
    protocol = flask_request.args.get('protocol', None)
    file_name = flask_request.args.get('file_name', None)
    return send_file(path + '/' + protocol + '/' + file_name, attachment_filename=file_name, as_attachment=True)

# INSERT 함수 예제
@test.route('/insert', methods=['GET'])
def insert():
    db_class= dbModule.Database()
 
    sql     = "INSERT INTO testDB.testTable(test) \
                VALUES('%s')"% ('testData')
    db_class.execute(sql)
    db_class.commit()
 
    return render_template('/test/test.html',
                           result='insert is done!',
                           resultData=None,
                           resultUPDATE=None)
 
 
 
# SELECT 함수 예제
@test.route('/select', methods=['GET'])
def select():
    db_class= dbModule.Database()
 
    sql     = "SELECT idx, test \
                FROM testDB.testTable"
    row     = db_class.executeAll(sql)
 
    print(row)
 
    return render_template('/test/test.html',
                            result=None,
                            resultData=row[0],
                            resultUPDATE=None)
 
 
# UPDATE 함수 예제
@test.route('/update', methods=['GET'])
def update():
    db_class= dbModule.Database()
 
    sql     = "UPDATE testDB.testTable \
                SET test='%s' \
                WHERE test='testData'"% ('update_Data')
    db_class.execute(sql)   
    db_class.commit()
 
    sql     = "SELECT idx, test \
                FROM testDB.testTable"
    row     = db_class.executeAll(sql)
 
    return render_template('/test/test.html',
                            result=None,
                            resultData=None,
                            resultUPDATE=row[0])

# default host address 127.0.0.1
# host port numer 8085
if __name__ == "__main__":
    HOST_ADDRESS = socket.gethostbyname(socket.getfqdn())

    # 앞쪽에 만들어 둔 모듈 전부 불러쓰기 (DB에 로깅하는 모듈들)
    
    print('Start Main')
    try:
        app.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True)

    except Exception as e:
        print('Error :', e)

