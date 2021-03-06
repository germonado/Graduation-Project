import os

from flask import Flask, render_template, request, send_file, Blueprint
from app.module.DB import DBlogging, DBload as DB
from app.module.Zigbee import zigbee
from app.module.BLE import bluetooth
from app.module.Report import reportExport

HOST_ADDRESS = '127.0.0.1'

HOST_PORT = 8085

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
test= Blueprint('test', __name__, url_prefix='/test')

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


@app.route("/")
@app.route("/index.html")
@app.route("/bluetooth_report", methods=['POST', 'GET'])
def bluetooth_report():
    db = DB.DB_LOAD()
    ble_file_list = db.ble_file_load()
       
    if request.method =="POST":
        result = request.form.get('FileName')
        ble_list, ble_statistics = db.ble_lists_from_DB(result)
        return render_template('bluetooth_report.html', bleList=ble_list, staList=ble_statistics, fileList=ble_file_list, selectedpkt=result)

    ble_list, ble_statistics = db.ble_lists_from_DB(ble_file_list[0])
    return render_template('bluetooth_report.html', bleList=ble_list, staList=ble_statistics, fileList=ble_file_list, selectedpkt=ble_file_list[0])


@app.route("/zigbee_report", methods=['POST', 'GET'])
def zigbee_report():
    db = DB.DB_LOAD()
    zbee_file_list = db.zbee_file_load()

    if request.method =="POST":
        result = request.form.get('FileName')
        zbee_ng_list, zbee_list, zbee_statistics = db.zbee_lists_from_DB(result)
        return render_template('zigbee_report.html', fileList=zbee_file_list, zbeeList=zbee_list, staList=zbee_statistics, selectedpkt=result)

    zbee_ng_list, zbee_list, zbee_statistics = db.zbee_lists_from_DB(zbee_file_list[0])
    return render_template('zigbee_report.html', fileList=zbee_file_list, zbeeList=zbee_list, staList=zbee_statistics, selectedpkt=zbee_file_list[0])
     

@app.route('/log_file_download')
def log_file_download():
    path = "./log_data/"
    protocol = request.args.get('protocol', None)
    file_name = request.args.get('file_name', None)
    return send_file(path + '/' + protocol + '/' + file_name, attachment_filename=file_name, as_attachment=True)


@app.route("/profile")
def profile():
    return render_template('profile.html')


# default host address 127.0.0.1
# host port numer 8085
if __name__ == "__main__":

    print('Start Main')
    
    try:
        app.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True)

    except Exception as e:
        print('Error :', e)

