from flask import Flask
from flask import render_template
from flask import request 
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

import DBlogging
import reportExport
import DBload as DB

HOST_ADDRESS = '127.0.0.1'

HOST_PORT = 8085

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


@app.route("/bluetooth_report", methods=['POST', 'GET'])
def bluetooth_report():
    #db = DB.DB_LOAD()
    #ble_file_list = db.ble_file_load()
       
    if request.method =="POST":
        result = request.form.get('FileName')
        print(result)
        ble = bluetooth.BluetoothCheck()
        ble_file_list = ble.get_file()
        ble.write_command_extract(result)
        #ble_list, ble_statistics = db.ble_lists_from_DB(ble_file_list[0])
        ble_list, ble_statistics, t = ble.write_command_succeed_check()
        return render_template('bluetooth_report.html', bleList=ble_list, staList=ble_statistics, fileList=ble_file_list, selectedpkt=result)

    #ble_list, ble_statistics = db.ble_lists_from_DB(ble_file_list[0])
    ble = bluetooth.BluetoothCheck()
    ble_file_list = ble.get_file()
    print(ble_file_list)
    for i in ble_file_list:
        ble.write_command_extract(i)
        ble_list, ble_statistics, t = ble.write_command_succeed_check()
        break
    return render_template('bluetooth_report.html', bleList=ble_list, staList=ble_statistics, fileList=ble_file_list, selectedpkt=ble_file_list[0])


@app.route("/zigbee_report")
def zigbee_report():
    db = DB.DB_LOAD()
    zbee_file_list = db.zbee_file_load()

    if request.method =="POST":
        result = request.form.get('FileName')
        print(result)
        db.zbee_lists_from_DB(result)
        zbee_ng_list, zbee_list, zbee_statistics = db.zbee_lists_from_DB(zbee_file_list[0])
        return render_template('zigbee_report.html', fileList=zbee_file_list, zbeeList=zbee_list, staList=zbee_statistics, selectedpkt=result)

    zbee_ng_list, zbee_list, zbee_statistics = db.zbee_lists_from_DB(zbee_file_list[0])
    '''
    for i in zbee_list:
        flag = 0
        for j in zbee_ng_list:
            if i[8] == zbee_ng_list[2] and i[0] == zbee_ng_list[0] and i[1] == zbee_ng_list[1]:
                i.append("Error")
                flag = 1
        if flag == 0:
            i.append("Success")
    '''
    print(zbee_statistics)

    return render_template('zigbee_report.html', fileList=zbee_file_list, zbeeList=zbee_list, staList=zbee_statistics, selectedpkt=zbee_file_list[0])


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
    protocol = request.args.get('protocol', None)
    file_name = request.args.get('file_name', None)
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
    #HOST_ADDRESS = socket.gethostbyname(socket.getfqdn())

    print('Start Main')
    
    try:
        app.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True)

    except Exception as e:
        print('Error :', e)

