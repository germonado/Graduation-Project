from flask import Flask
from flask import render_template
from flask import request as flask_request
from flask import session
from flask import send_file
from flask import send_from_directory
from flask_socketio import SocketIO
from flask_socketio import emit
from socket import *
import matplotlib.pyplot as plt
import numpy as np
import wave
import io
import base64
import os
import threading
import time
import socket
import random



HOST_ADDRESS = socket.gethostbyname(socket.getfqdn())

HOST_PORT = 8085

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(app)

@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')

@app.route("/log_lists")
def log_lists():
    path = "./log_data/"

    log_file_list = os.listdir(path)

    return render_template('log_list.html', fileList=log_file_list)

@app.route('/log_file_download')
def log_file_download():
    path = "./log_data/"

    file_name = flask_request.args.get('file_name', None)
    return send_file(path + file_name, attachment_filename=file_name, as_attachment=True)


if __name__ == "__main__":
    print('Start Main')
    #while True:
    try:
        socket_io.run(app, host=HOST_ADDRESS, port=HOST_PORT, debug=True)
    except Exception as e:
        print('Error :', e)
    # app.run(host=HOST_ADDRESS, port=HOST_PORT)

